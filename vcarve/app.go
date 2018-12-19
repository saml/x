package vcarve

import (
	"github.com/saml/x/vcarve/ffmpeg"
)

// App is vcarve application
type App struct {
	FFmpegCli ffmpeg.Runner
}
