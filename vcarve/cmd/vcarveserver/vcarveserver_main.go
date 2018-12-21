package main

import (
	"flag"
	"html/template"
	"net/http"
	"os"
	"path/filepath"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/cachefs"
	"github.com/saml/x/vcarve/ffmpeg"
	httpapp "github.com/saml/x/vcarve/http"
	"github.com/saml/x/vcarve/http/jwplayer"
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

	log.Print("Loading templates ...")
	tmpl := template.Must(template.ParseFiles("index.html"))

	static := http.FileServer(http.Dir("static"))
	http.Handle("/static", static)
	http.HandleFunc("/vcarve", app.HandleAnimThumb)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		q := r.URL.Query()
		feed, err := jwplayer.FetchFeed(q.Get("feed"))
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}

		err = tmpl.ExecuteTemplate(w, "index.html", feed)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})

	log.Printf("Listening to %v", app.Addr)
	err = http.ListenAndServe(app.Addr, nil)
	if err != nil {
		log.Fatal().Err(err)
	}
}
