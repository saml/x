package vcarve

import (
	"bufio"
	"strconv"
	"strings"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/streams"
)

// ExecKeyFrames runs FFprobe to find key frame locations (in seconds).
func ExecKeyFrames(app ffmpeg.Runner, vid string) ([]float64, error) {
	stdout, err := app.ExecFFprobe("-loglevel", "error",
		"-skip_frame", "nokey",
		"-select_streams", "v:0",
		"-show_entries", "frame=pkt_pts_time",
		"-of", "csv=print_section=0",
		vid,
	)
	if err != nil {
		log.Print(streams.ReadString(stdout))
		return nil, err
	}

	return ParseFloats(stdout)
}

// ParseFloats parses new line separated floats. Ignores invalid floats.
func ParseFloats(stdout *bufio.Reader) ([]float64, error) {
	scanner := bufio.NewScanner(stdout)
	var floats []float64
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		val, err := strconv.ParseFloat(line, 64)
		if err != nil {
			// ignore parse error.
			log.Print(err)
		} else {
			// only append parsed floats.
			floats = append(floats, val)
		}
	}
	return floats, nil
}
