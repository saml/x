package vcarve_test

import (
	"bufio"
	"strings"
	"testing"

	"github.com/saml/x/vcarve"
	tt "github.com/saml/x/vcarve/testing"
)

func TestParseFloats(t *testing.T) {
	stdout := bufio.NewReader(strings.NewReader(`
	0
	1
	1.1
	2.0
	`))
	expected := []float64{
		0.0,
		1.0,
		1.1,
		2.0,
	}

	result, err := vcarve.ParseFloats(stdout)

	if err != nil {
		t.Error(err)
	}
	if len(expected) != len(result) {
		t.Errorf("Not same length: %v = %v", expected, result)
	}
	for i := range result {
		if !tt.FloatSimilar(expected[i], result[i]) {
			t.Errorf("Not same interval: %v = %v", expected[i], result[i])
		}
	}
}

func TestParseFloatsNoValid(t *testing.T) {
	stdout := bufio.NewReader(strings.NewReader(`
	a
	b
	c
	
	`))

	result, err := vcarve.ParseFloats(stdout)

	if err != nil {
		t.Error(err)
	}
	if len(result) > 0 {
		t.Errorf("Expected []. Got: %v", result)
	}
}
