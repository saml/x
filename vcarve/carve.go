package vcarve

import (
	"fmt"
	"io"
	"os"
	"strings"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/interval"
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

// WriteFilterGraph writes filter graph for carving out video so that only intervals are included.
func WriteFilterGraph(intervals []*interval.Interval, output string) error {
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
func CarveSilence(ff ffmpeg.Runner, vid string, script string, output string) error {
	silences, err := silencedetect.Exec(ff, vid)
	if err != nil {
		return err
	}

	keyFrames, err := ExecKeyFrames(ff, vid)
	if err != nil {
		return err
	}

	intervals := silencedetect.Include(silences, keyFrames)

	err = WriteFilterGraph(intervals, script)
	if err != nil {
		return err
	}

	log.Printf("Writing output video: %v", output)
	stderr, err := ff.ExecFFmpeg("-i", vid, "-filter_complex_script", script, "-map", "[v]", "-map", "[a]", output)
	if err != nil {
		log.Print(streams.ReadString(stderr))
		return err
	}
	return nil
}
