package scenedetect_test

import (
	"strings"
	"testing"

	"github.com/saml/x/vcarve/interval"
	"github.com/saml/x/vcarve/scenedetect"
	tt "github.com/saml/x/vcarve/testing"
)

func TestParseScenes(t *testing.T) {
	input := strings.NewReader(`
	foo
	[Parsed_showinfo_1 @ 0x55be8c520640] n:   5 pts:  48549 pts_time:48.549  pos: 14427569 fmt:rgb24 sar:1/1 s:1920x1080 i:P iskey:0 type:I checksum:15EF2A26 plane_checksum:[15EF2A26] mean:[94] stdev:[70.0]
	[Parsed_showinfo_1 @ 0x55be8c520640] n:   6 pts:  52219 pts_time:52.219  pos: 15109412 fmt:rgb24 sar:1/1 s:1920x1080 i:P iskey:1 type:I checksum:EF704922 plane_checksum:[EF704922] mean:[100] stdev:[71.6]

	[Parsed_showinfo_1 @ 0x55be8c520640] n:   7 pts:  55155 pts_time:55.155  pos: 16295408 fmt:rgb24 sar:1/1 s:1920x1080 i:P iskey:1 type:I checksum:167365F9 plane_checksum:[167365F9] mean:[121] stdev:[71.0]
	[Parsed_showinfo_1 @ 0x55be8c520640] n:   8 pts:  56957 pts_time:56.957  pos: 16757353 fmt:rgb24 sar:1/1 s:1920x1080 i:P iskey:1 type:I checksum:247103D5 plane_checksum:[247103D5] mean:[105] stdev:[76.7]
	`)
	expected := []float64{
		48.549,
		52.219,
		55.155,
		56.957,
	}

	result, err := scenedetect.ParseScenes(input)

	if err != nil {
		t.Error(err)
	}
	if len(expected) != len(result) {
		t.Errorf("Not same length: %v = %v", expected, result)
	}
	for i := range result {
		if !tt.FloatSimilar(expected[i], result[i]) {
			t.Errorf("Not same: %v = %v", expected[i], result[i])
		}
	}
}

func TestIntervalsZero(t *testing.T) {
	seconds := []float64{
		2,
	}
	minDuration := 1.0
	duration := 0.0

	result := scenedetect.Intervals(seconds, minDuration, duration)

	if len(result) > 0 {
		t.Errorf("Expected []. Got: %v", result)
	}
}

func TestIntervalsMinGreater(t *testing.T) {
	seconds := []float64{
		1,
		2,
	}
	minDuration := 2.0
	duration := 4.0
	expected := []*interval.Interval{
		interval.New(0, 2),
		interval.New(2, 4),
	}

	result := scenedetect.Intervals(seconds, minDuration, duration)

	if len(expected) != len(result) {
		t.Errorf("Not same length: %v = %v", expected, result)
	}
	for i := range result {
		if !tt.IntervalSimilar(expected[i], result[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], result[i])
		}
	}
}

func TestIntervalsMinSmaller(t *testing.T) {
	seconds := []float64{
		1,
		3,
		5,
	}
	minDuration := 1.0
	duration := 8.0
	expected := []*interval.Interval{
		interval.New(0, 1),
		interval.New(1, 2),
		interval.New(3, 4),
		interval.New(5, 6),
	}

	result := scenedetect.Intervals(seconds, minDuration, duration)

	if len(expected) != len(result) {
		t.Errorf("Not same length: %v = %v", expected, result)
	}
	for i := range result {
		if !tt.IntervalSimilar(expected[i], result[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], result[i])
		}
	}
}
