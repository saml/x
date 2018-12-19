package interval_test

import (
	"testing"

	"github.com/saml/x/vcarve/interval"
)

func TestIntervalGuarentee(t *testing.T) {
	result := interval.New(0, -1)

	if result.End < result.Start {
		t.Errorf("End is before Start: %v <= %v", result.Start, result.End)
	}
}
