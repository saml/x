package vcarve

import (
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/interval"
	"github.com/saml/x/vcarve/scenedetect"
	"github.com/saml/x/vcarve/silencedetect"
	"github.com/saml/x/vcarve/streams"
)

// Carver can carve a video
type Carver interface {
	// Intervals writes intervals that should be included in the result.
	Intervals(vid string, output io.Writer) error
}

// WriteConcat writes concat statements (that concat filter uses).
func WriteConcat(vid string, intervals []*interval.Interval, output string) error {
	log.Printf("Writing concat file to: %v", output)
	file, err := os.OpenFile(output, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		return err
	}
	for _, pair := range intervals {
		_, err := fmt.Fprintf(file, "file %s\n", vid)
		if err != nil {
			return err
		}
		_, err = fmt.Fprintf(file, "inpoint %f\n", pair.Start)
		if err != nil {
			return err
		}
		_, err = fmt.Fprintf(file, "outpoint %f\n", pair.End)
		if err != nil {
			return err
		}
	}
	return nil
}

// WriteTrim writes filter graph for carving out video so that only intervals are included.
func WriteTrim(intervals []*interval.Interval, output string) error {
	log.Printf("Writing filter graph to: %v", output)
	file, err := os.OpenFile(output, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		return err
	}

	var inputs strings.Builder
	for i, pair := range intervals {
		_, err := fmt.Fprintf(file, "[0]trim=start=%f:end=%f,setpts=PTS-STARTPTS[v%d];\n", pair.Start, pair.End, i)
		if err != nil {
			return err
		}
		_, err = fmt.Fprintf(file, "[0]atrim=start=%f:end=%f,asetpts=PTS-STARTPTS[a%d];\n", pair.Start, pair.End, i)
		if err != nil {
			return err
		}
		_, err = fmt.Fprintf(&inputs, "[v%d][a%d]", i, i)
		if err != nil {
			return err
		}
	}
	_, err = fmt.Fprintf(file, "%s concat=n=%d:v=1:a=1[v][a]\n", inputs.String(), len(intervals))
	return err
}

// CarveSilence carves silence from video.
func (app *App) CarveSilence() error {
	silences, err := silencedetect.Exec(app.FFmpeg, app.Input)
	if err != nil {
		return err
	}

	duration, err := ffmpeg.Duration(app.FFmpeg, app.Input)
	if err != nil {
		return err
	}

	intervals := silencedetect.Invert(silences, duration)
	return app.Carve(intervals)
}

// WriteSelect writes filtergraph using select filter instead of trim.
func WriteSelect(intervals []*interval.Interval, output string) error {
	log.Printf("Writing select filter graph to: %v", output)
	file, err := os.OpenFile(output, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0644)
	if err != nil {
		return err
	}

	var selects []string
	for _, pair := range intervals {
		selects = append(selects, fmt.Sprintf("between(t,%f,%f)", pair.Start, pair.End))
	}
	_, err = fmt.Fprintf(file, "[0:v]select='%s',setpts=N/(FRAME_RATE*TB)[v];\n", strings.Join(selects, "+"))
	if err != nil {
		return err
	}
	_, err = fmt.Fprintf(file, "[0:a]aselect='%s',asetpts=N/(FRAME_RATE*TB)[a]\n", strings.Join(selects, "+"))
	return err
}

// Carve carves given intervals out of video.
func (app *App) Carve(intervals []*interval.Interval) error {
	err := WriteSelect(intervals, app.Script)
	if err != nil {
		return err
	}

	log.Printf("Writing output video: %v", app.Output)
	stderr, err := app.FFmpeg.ExecFFmpeg("-i", app.Input,
		"-filter_complex_script", app.Script,
		"-map", "[v]", "-map", "[a]", app.Output)
	if err != nil {
		log.Print(streams.ReadString(stderr))
		return err
	}
	return nil
}

// CarveSeconds carves pairs of seconds out of video.
// There are even number of seconds.
func (app *App) CarveSeconds(seconds io.Reader) error {
	intervals, err := interval.ReadIntervals(seconds)
	if err != nil {
		return err
	}

	return app.Carve(intervals)
}

// CarveSceneChange extracts scence changes from video.
func (app *App) CarveSceneChange(minDuration float64, probability float64) error {

	duration, err := ffmpeg.Duration(app.FFmpeg, app.Input)
	if err != nil {
		return err
	}

	intervals, err := scenedetect.SceneIntervals(app.FFmpeg, app.Input, probability, minDuration, duration)
	if err != nil {
		return err
	}

	return app.Carve(intervals)
}
