package silencedetect_test

import (
	"bufio"
	"strings"
	"testing"

	"github.com/saml/x/vcarve/interval"
	"github.com/saml/x/vcarve/silencedetect"
	tt "github.com/saml/x/vcarve/testing"
)

func TestParseSilence(t *testing.T) {
	stderr := bufio.NewReader(strings.NewReader(`
	encoder         : Lavc58.18.100 pcm_s16le
	[silencedetect @ 0x55a13db38480] silence_start: 0
	[silencedetect @ 0x55a13db38480] silence_end: 9.79599 | silence_duration: 9.79599
	[silencedetect @ 0x55a13db38480] silence_start: 10.2968
	[silencedetect @ 0x55a13db38480] silence_end: 11.5384 | silence_duration: 1.24154
	[silencedetect @ 0x55a13db38480] silence_start: 14.9884
	[silencedetect @ 0x55a13db38480] silence_end: 16.6142 | silence_duration: 1.6258
	[silencedetect @ 0x55a13db38480] silence_start: 22.4913itrate=N/A speed=17.6x    
	[silencedetect @ 0x55a13db38480] silence_end: 24.5777 | silence_duration: 2.08639
	[silencedetect @ 0x55a13db38480] silence_start: 26.4904itrate=N/A speed=17.8x    
	[silencedetect @ 0x55a13db38480] silence_end: 27.7528 | silence_duration: 1.26245
	frame= 1800 fps=1072 q=-0.0 Lsize=N/A time=00:00:30.00 bitrate=N/A speed=17.9x
	`))
	// I expect (silence_start, silence_end) pairs.
	expected := []*interval.Interval{
		interval.New(0.0, 9.79599),
		interval.New(10.2968, 11.5384),
		interval.New(14.9884, 16.6142),
		interval.New(22.4913, 24.5777),
		interval.New(26.4904, 27.7528),
	}

	intervals, err := silencedetect.ParseSilence(stderr)

	if err != nil {
		t.Error(err)
	}
	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}

func TestInclude(t *testing.T) {
	keyFrames := []float64{
		0.0,
		1.0,
		2.0,
		3.0,
		4.0,
	}
	silences := []*interval.Interval{
		interval.New(0.0, 0.5),
		interval.New(0.6, 0.7),
		interval.New(0.9, 2.8),
	}
	expected := []*interval.Interval{
		interval.New(3.0, 4.0),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}

func TestIncludeNoSilence(t *testing.T) {
	keyFrames := []float64{
		0.0,
		1.0,
		2.0,
		3.0,
		4.0,
	}
	var silences []*interval.Interval
	expected := []*interval.Interval{
		interval.New(0.0, 4.0),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}

func TestIncludeMultiple(t *testing.T) {
	keyFrames := []float64{
		0.0,
		2.0,
		4.0,
		8.0,
		9.0,
		10.0,
		12.0,
		13.0,
		14.0,
	}
	silences := []*interval.Interval{
		interval.New(0.0, 1.0),
		interval.New(3.0, 5.0),
		interval.New(6.0, 7.0),
		interval.New(11.0, 12.0),
	}
	expected := []*interval.Interval{
		interval.New(8.0, 10.0),
		interval.New(12.0, 14.0),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}

func TestIncludeMostlySilence(t *testing.T) {
	keyFrames := []float64{
		0.0,
		2.0,
		4.0,
	}
	silences := []*interval.Interval{
		interval.New(0.0, 2.1),
		interval.New(3.0, 4.0),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(intervals) > 0 {
		t.Errorf("Expecting []. Got non empty array: %v", intervals)
	}
}

func TestIncludeAllSilence(t *testing.T) {
	keyFrames := []float64{
		0.0,
		2.0,
		4.0,
	}
	silences := []*interval.Interval{
		interval.New(0.0, 4),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(intervals) > 0 {
		t.Errorf("Expecting []. Got non empty array: %v", intervals)
	}
}

func TestIncludeBeginning(t *testing.T) {
	// no silence in the beginning. So, include the beginning.
	keyFrames := []float64{
		0,
		1,
		2,
		3,
	}
	silences := []*interval.Interval{
		interval.New(2.0, 2.1),
	}
	expected := []*interval.Interval{
		interval.New(0, 2),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}

func TestIncludeEnd(t *testing.T) {
	// no silence at the end. So, include the end.
	keyFrames := []float64{
		0,
		1,
		2,
		3,
	}
	silences := []*interval.Interval{
		interval.New(0, 2),
	}
	expected := []*interval.Interval{
		interval.New(2, 3),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}

func TestIncludeMiddle(t *testing.T) {
	// no silence in the middle. So, include the middle
	keyFrames := []float64{
		0,
		1,
		2,
		3,
	}
	silences := []*interval.Interval{
		interval.New(0, 1),
		interval.New(2, 3),
	}
	expected := []*interval.Interval{
		interval.New(1, 2),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}

func TestIncludeComplement(t *testing.T) {
	keyFrames := []float64{
		0,
		1,
		2,
		3,
		4,
		5,
	}
	silences := []*interval.Interval{
		interval.New(1, 2),
		interval.New(3, 4),
	}
	expected := []*interval.Interval{
		interval.New(0, 1),
		interval.New(2, 3),
		interval.New(4, 5),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}

func TestIncludeComplementNotExact(t *testing.T) {
	keyFrames := []float64{
		0,
		1,
		2,
		3,
		4,
		5,
	}
	silences := []*interval.Interval{
		interval.New(1.5, 1.6),
		interval.New(1.7, 1.8),
		interval.New(3.2, 3.5),
		interval.New(3.8, 3.9),
	}
	expected := []*interval.Interval{
		interval.New(0, 1),
		interval.New(2, 3),
		interval.New(4, 5),
	}

	intervals := silencedetect.Include(silences, keyFrames)

	if len(expected) != len(intervals) {
		t.Errorf("Not same length: %v = %v", expected, intervals)
	}
	for i := range intervals {
		if !tt.IntervalSimilar(expected[i], intervals[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], intervals[i])
		}
	}
}
