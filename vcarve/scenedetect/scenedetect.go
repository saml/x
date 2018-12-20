package scenedetect

import (
	"bufio"
	"fmt"
	"io"
	"math"
	"regexp"
	"strconv"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/interval"
	"github.com/saml/x/vcarve/streams"
)

var (
	sceneRE = regexp.MustCompile(`showinfo.+ pts_time:([.\d]+)`)
)

// Scenes outputs scene changes in seconds.
func Scenes(ff ffmpeg.Runner, vid string, probabilty float64) ([]float64, error) {
	stderr, err := ff.ExecFFmpeg("-i", vid,
		"-vf", fmt.Sprintf("select='gt(scene,%f)',showinfo", probabilty),
		"-f", "null", "-")
	if err != nil {
		log.Print(streams.ReadString(stderr))
		return nil, err
	}
	return ParseScenes(stderr)
}

// ParseScenes reads scene change timestamps (seconds).
func ParseScenes(r io.Reader) ([]float64, error) {
	scanner := bufio.NewScanner(r)
	var result []float64
	for scanner.Scan() {
		line := scanner.Text()
		match := sceneRE.FindStringSubmatch(line)

		if len(match) == 2 {
			f, err := strconv.ParseFloat(match[1], 64)
			if err != nil {
				return nil, err
			}
			result = append(result, f)
		}

	}
	return result, nil
}

// SceneIntervals detects scene change includes minDuration for each scene.
func SceneIntervals(ff ffmpeg.Runner, vid string, probabilty float64, minDuration float64, duration float64) ([]*interval.Interval, error) {
	seconds, err := Scenes(ff, vid, probabilty)
	if err != nil {
		return nil, err
	}
	return Intervals(seconds, minDuration, duration), nil
}

// Intervals includes minDuration for each segment.
func Intervals(seconds []float64, minDuration float64, duration float64) []*interval.Interval {
	var result []*interval.Interval
	prev := 0.0
	for _, sec := range seconds {
		if sec > duration {
			// end of video.
			break
		}
		if sec-prev >= minDuration {
			result = append(result, interval.New(prev, prev+minDuration))
			prev = sec
		}
	}
	if prev < duration {
		result = append(result, interval.New(prev, math.Min(duration, prev+minDuration)))
	}
	return result
}
