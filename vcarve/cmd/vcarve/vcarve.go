package main

import (
	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/silencedetect"
)

func main() {
	app := &ffmpeg.App{
		FFmpeg:  "ffmpeg",
		FFprobe: "ffprobe",
	}

	silencedetect.Exec(app, "/tmp/a.mkv")
}
