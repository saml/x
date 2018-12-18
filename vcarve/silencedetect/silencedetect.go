package silencedetect

import (
	"bufio"
	"io/ioutil"
	"regexp"
	"strconv"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/interval"
)

var intervalRe = regexp.MustCompile(` silence_end: ([\d.]+) | silence_duration: ([\d.]+)`)

func readAll(stderr *bufio.Reader) string {
	out, err := ioutil.ReadAll(stderr)
	if err != nil {
		log.Print(err)
		return ""
	}
	return string(out)
}

// Exec runs ffmpeg to detect silence intervals.
func Exec(ff ffmpeg.Runner, vid string) ([]*interval.Interval, error) {
	args := []string{"-hide_banner", "-i", vid, "-af", "silencedetect=duration=1:noise=0.1", "-f", "null", "-"}
	stderr, err := ff.Exec(args...)
	if err != nil {
		log.Print(readAll(stderr))
		return nil, err
	}
	return ParseSilence(stderr)
}

// ParseSilence parses silence intervals out of stderr.
func ParseSilence(stderr *bufio.Reader) ([]*interval.Interval, error) {
	scanner := bufio.NewScanner(stderr)
	var intervals []*interval.Interval
	for scanner.Scan() {
		line := scanner.Text()
		match := intervalRe.FindAllStringSubmatch(line, -1)

		if len(match) == 2 {
			end, err := strconv.ParseFloat(match[0][1], 64)
			if err != nil {
				return nil, err
			}
			duration, err := strconv.ParseFloat(match[1][2], 64)
			if err != nil {
				return nil, err
			}
			intervals = append(intervals, interval.New(end-duration, end))
		}

	}
	return intervals, nil
}

// Include calculates sections of video to include, carving out silences.
// Sections are synced to keyFrames.
// keyFrames have length >= 2. keyFrames[0] = 0.0; keyFrames[-1] = video duration.
func Include(silences []*interval.Interval, keyFrames []float64) []*interval.Interval {
	var intervals []*interval.Interval
	var start int
	var end int
	var i int // silences index.
	if len(silences) == 0 {
		return []*interval.Interval{
			interval.New(keyFrames[start], keyFrames[len(keyFrames)-1]),
		}
	}

	// // first section is free of silence.
	// for end < len(keyFrames) && silences[i].Start <= keyFrames[end] {
	// 	end++
	// }
	// // end is past Start.
	// if end-1 > start {
	// 	intervals = append(intervals, interval.New(keyFrames[start], keyFrames[end-1]))
	// }

	for end < len(keyFrames) && i < len(silences) {
		// move start past End
		for start < len(keyFrames) && silences[i].End > keyFrames[start] {
			start++
		}

		// next silence
		for i < len(silences) && silences[i].End <= keyFrames[start] {
			i++
		}
		if i == len(silences) {
			break
		}

		// find end before Start
		end = start
		for end < len(keyFrames) && silences[i].Start >= keyFrames[end] {
			end++
		}

		// end includes Start.
		// there is at least one interval free of silence.
		if end-1 > start {
			intervals = append(intervals, interval.New(keyFrames[start], keyFrames[end-1]))
		}
	}

	// last section is free of silence.
	if start < len(keyFrames)-1 && silences[len(silences)-1].End <= keyFrames[start] {
		intervals = append(intervals, interval.New(keyFrames[start], keyFrames[len(keyFrames)-1]))
	}
	return intervals
}
