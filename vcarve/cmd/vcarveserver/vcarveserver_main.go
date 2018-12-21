package main

import (
	"flag"
	"net/http"
	"os"
	"path/filepath"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/cachefs"
	"github.com/saml/x/vcarve/ffmpeg"
	httpapp "github.com/saml/x/vcarve/http"
)

func main() {
	addr := flag.String("addr", ":8080", "address to bind to")
	cacheDir := flag.String("cache", "data", "directory to store cache objects")
	ffmpegPath := flag.String("ffmpeg", "ffmpeg", "path to ffmpeg")
	ffprobePath := flag.String("ffprobe", "ffprobe", "path to ffprobe")
	flag.Parse()

	originals := &cachefs.CacheFS{
		Dir: filepath.Join(*cacheDir, "originals"),
	}
	renditions := &cachefs.CacheFS{
		Dir: filepath.Join(*cacheDir, "renditions"),
	}
	log.Printf("Creating originals dir: %v", originals.Dir)
	err := os.MkdirAll(originals.Dir, 0755)
	if err != nil {
		log.Fatal().Err(err)
	}
	log.Printf("Creating renditions dir: %v", renditions.Dir)
	err = os.MkdirAll(renditions.Dir, 0755)
	if err != nil {
		log.Fatal().Err(err)
	}

	app := &httpapp.App{
		FFmpeg: &ffmpeg.App{
			FFmpeg:  *ffmpegPath,
			FFprobe: *ffprobePath,
		},
		Originals:  originals,
		Renditions: renditions,
		Addr:       *addr,
	}

	s := &http.Server{
		Addr:    app.Addr,
		Handler: http.HandlerFunc(app.HandleAnimThumb),
	}
	log.Printf("Listening to %v", s.Addr)
	err = s.ListenAndServe()
	if err != nil {
		log.Fatal().Err(err)
	}
}
