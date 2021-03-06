package main

import (
	"flag"
	"os"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve"
	"github.com/saml/x/vcarve/ffmpeg"
)

func main() {
	input := flag.String("i", "", "input video")
	script := flag.String("script", "filter.txt", "temporary filter graph script file")
	ffmpegPath := flag.String("ffmpeg", "ffmpeg", "path to ffmpeg")
	ffprobePath := flag.String("ffprobe", "ffprobe", "path to ffprobe")
	flag.Parse()

	if flag.NArg() < 1 || *input == "" {
		flag.Usage()
		os.Exit(1)
	}
	output := flag.Arg(0)

	app := &vcarve.App{
		FFmpeg: &ffmpeg.App{
			FFmpeg:  *ffmpegPath,
			FFprobe: *ffprobePath,
		},
		Input:  *input,
		Output: output,
		Script: *script,
	}

	err := app.CarveSilence()
	if err != nil {
		log.Fatal().Err(err)
	}
}
