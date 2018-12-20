package interval_test

import (
	"strings"
	"testing"

	"github.com/saml/x/vcarve/interval"
	tt "github.com/saml/x/vcarve/testing"
)

func TestIntervalGuarentee(t *testing.T) {
	result := interval.New(0, -1)

	if result.End < result.Start {
		t.Errorf("End is before Start: %v <= %v", result.Start, result.End)
	}
}

func TestReadIntervalsEmpty(t *testing.T) {
	input := strings.NewReader("")

	result, err := interval.ReadIntervals(input)

	if err != nil {
		t.Error(err)
	}
	if len(result) > 0 {
		t.Errorf("Expected []. Got: %v", result)
	}
}

func TestReadIntervalsMultiple(t *testing.T) {
	input := strings.NewReader(`0 1.0
	2
	3.0
	
	4.0 5 6
	7
	`)
	expected := []*interval.Interval{
		interval.New(0, 1),
		interval.New(2, 3),
		interval.New(4, 5),
		interval.New(6, 7),
	}

	result, err := interval.ReadIntervals(input)

	if err != nil {
		t.Error(err)
	}
	if len(expected) != len(result) {
		t.Errorf("Not same length: %v = %v", expected, result)
	}
	for i := range result {
		if !tt.IntervalSimilar(expected[i], result[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], result[i])
		}
	}
}
