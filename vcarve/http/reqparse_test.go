package http_test

import (
	"fmt"
	"net/url"
	"testing"

	httpapp "github.com/saml/x/vcarve/http"
)

const videoURL = "http://host/path/a.mp4"

var animBaseTests = []struct {
	probability float64
	duration    float64
	basename    string
}{
	{0.1, 1.2, "a.mp4_p0.100000_d1.200000_.mp4"},
	{1, 0, "a.mp4_p1.000000_d0.000000_.mp4"},
	{1.0, 0.0, "a.mp4_p1.000000_d0.000000_.mp4"},
}

func TestBasename(t *testing.T) {
	video, err := url.ParseRequestURI(videoURL)
	if err != nil {
		t.Errorf("Invalid url: %v", videoURL)
	}

	for _, testcase := range animBaseTests {
		title := fmt.Sprintf("p=%f,d=%f", testcase.probability, testcase.duration)
		t.Run(title, func(t *testing.T) {
			param := &httpapp.AnimRequest{
				Video:       video,
				Probability: testcase.probability,
				MinDuration: testcase.duration,
			}

			basename := param.Base()

			if basename != testcase.basename {
				t.Errorf("Expected: %v != %v", testcase.basename, basename)
			}
		})
	}
}
