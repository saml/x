package main

import (
	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/silencedetect"
)

func main() {
	app := &ffmpeg.App{
		Cmd: "ffmpeg",
	}

	silencedetect.Exec(app, "/tmp/a.mkv")
}
