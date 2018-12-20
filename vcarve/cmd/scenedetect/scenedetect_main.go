package main

import (
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/scenedetect"
)

func main() {
	input := flag.String("i", "", "input video file")
	outputPath := flag.String("o", "-", "output file. - means stdout")
	minDuration := flag.Float64("interval", 1.0, "seconds of each scene to include.")
	probability := flag.Float64("prob", 0.5, "probability of scene change. 0 ~ 1.0")
	ffmpegPath := flag.String("ffmpeg", "ffmpeg", "path to ffmpeg")
	ffprobePath := flag.String("ffprobe", "ffprobe", "path to ffprobe")
	flag.Parse()
	if *input == "" {
		flag.Usage()
		os.Exit(1)
	}

	var output io.Writer
	var err error
	if *outputPath == "-" {
		output = os.Stdout
	} else {
		output, err = os.Open(*outputPath)
		if err != nil {
			log.Fatal().Err(err)
		}
	}

	app := &ffmpeg.App{
		FFmpeg:  *ffmpegPath,
		FFprobe: *ffprobePath,
	}
	duration, err := ffmpeg.Duration(app, *input)
	if err != nil {
		log.Fatal().Err(err)
	}

	intervals, err := scenedetect.SceneIntervals(app, *input, *probability, *minDuration, duration)
	if err != nil {
		log.Fatal().Err(err)
	}

	for _, pair := range intervals {
		fmt.Fprintf(output, "%f %f\n", pair.Start, pair.End)
	}
}
