package vcarve

import (
	"github.com/saml/x/vcarve/ffmpeg"
)

// App is a vcarve app.
type App struct {
	FFmpeg ffmpeg.Runner
	Input  string
	Output string
	Script string
}
