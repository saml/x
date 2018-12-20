package main

import (
	"flag"
	"os"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve"
	"github.com/saml/x/vcarve/ffmpeg"
)

func main() {
	input := flag.String("i", "", "input video file")
	output := flag.String("o", "", "output video file")
	script := flag.String("script", "filter.txt", "temporary filter graph script file")
	minDuration := flag.Float64("interval", 1.0, "seconds of each scene to include.")
	probability := flag.Float64("prob", 0.6, "probability of scene change. 0 ~ 1.0")
	ffmpegPath := flag.String("ffmpeg", "ffmpeg", "path to ffmpeg")
	ffprobePath := flag.String("ffprobe", "ffprobe", "path to ffprobe")
	flag.Parse()
	if *input == "" {
		flag.Usage()
		os.Exit(1)
	}

	app := &vcarve.App{
		FFmpeg: &ffmpeg.App{
			FFmpeg:  *ffmpegPath,
			FFprobe: *ffprobePath,
		},
		Input:  *input,
		Output: *output,
		Script: *script,
	}

	err := app.CarveSceneChange(*minDuration, *probability)
	if err != nil {
		log.Fatal().Err(err)
	}
}
