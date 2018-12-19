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
// keyFrames must have length >= 2. keyFrames[0] = 0.0; keyFrames[-1] = video duration.
func Include(silences []*interval.Interval, keyFrames []float64) []*interval.Interval {
	var intervals []*interval.Interval

	// silences index.
	var curr int
	next := 1

	// keyFrames index.
	var i int
	var start int

	// add sentinels
	silences = append([]*interval.Interval{interval.New(0, 0)}, silences...)
	silences = append(silences, interval.New(keyFrames[len(keyFrames)-1], -1))

	for next < len(silences) {
		for i < len(keyFrames) && silences[curr].End > keyFrames[i] {
			i++
		}
		// keyFrames[i] is possible start of interval to include.
		start = i

		for i < len(keyFrames) && silences[next].Start >= keyFrames[i] {
			i++
		}
		// keyFrames[i-1] is possible end of interval to include.
		if i-1 > start {
			intervals = append(intervals, interval.New(keyFrames[start], keyFrames[i-1]))
		}
		curr++
		next++
	}
	return intervals
}
