package main

import (
	"flag"
	"io"
	"os"
	"path/filepath"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve"
	"github.com/saml/x/vcarve/ffmpeg"
)

func main() {
	output := flag.String("o", "", "output video file")
	timePath := flag.String("t", "-", "file that contains pair of timestamps to include. - means stdin")
	script := flag.String("script", "filter.txt", "temporary filter graph script file")
	ffmpegPath := flag.String("ffmpeg", "ffmpeg", "path to ffmpeg")
	ffprobePath := flag.String("ffprobe", "ffprobe", "path to ffprobe")
	flag.Parse()
	if flag.NArg() < 1 {
		flag.Usage()
		os.Exit(1)
	}
	input := flag.Arg(0)

	if *output == "" {
		*output = input + ".vcarve" + filepath.Ext(input)
	}

	var timestamps io.Reader
	var err error
	if *timePath == "-" {
		timestamps = os.Stdin
	} else {
		timestamps, err = os.Open(*timePath)
		if err != nil {
			log.Fatal().Err(err)
		}
	}

	app := &vcarve.App{
		FFmpeg: &ffmpeg.App{
			FFmpeg:  *ffmpegPath,
			FFprobe: *ffprobePath,
		},
		Input:  input,
		Output: *output,
		Script: *script,
	}

	err = app.CarveSeconds(timestamps)
	if err != nil {
		log.Fatal().Err(err)
	}
}
