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
			t.Errorf("Not equal: %v = %v", expected[i], intervals[i])
		}
	}
}
