package http

import (
	"io"
	"net/http"
	"os"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/cachefs"
	"github.com/saml/x/vcarve/http/jsonresp"
)

// App is an HTTP app
type App struct {
	Originals  *cachefs.CacheFS
	Renditions *cachefs.CacheFS
	Addr       string
}

// HandleAnimThumb generates animated thumbnail on the fly.
func (app *App) HandleAnimThumb(w http.ResponseWriter, r *http.Request) {

	param, err := ParseAnimRequest(r)
	if err != nil {
		log.Print(err)
		jsonresp.New(http.StatusBadRequest).Err(err).Write(w)
		return
	}

	log.Printf("Querying cache with key: %v", param.Video)
	original, err := Download(app.Originals, param.Video)
	f, err := os.Open(original)
	if err != nil {
		log.Print(err)
		jsonresp.New(http.StatusInternalServerError).Err(err).Write(w)
		return
	}
	_, err = io.Copy(w, f)
	if err != nil {
		log.Print(err)
		jsonresp.New(http.StatusInternalServerError).Err(err).Write(w)
		return
	}
}
