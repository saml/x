package http

import (
	"io"
	"net/http"
	"os"
	"path/filepath"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve"
	"github.com/saml/x/vcarve/cachefs"
	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/http/jsonresp"
)

// App is an HTTP app
type App struct {
	FFmpeg     ffmpeg.Runner
	Originals  *cachefs.CacheFS
	Renditions *cachefs.CacheFS
	Addr       string
}

// CarveApp returns carve application from animated thumbnail request.
func (app *App) CarveApp(param *AnimRequest) *vcarve.App {
	fileDir := filepath.Dir(app.Renditions.Hash(param.Video))
	return &vcarve.App{
		FFmpeg: app.FFmpeg,
		Input:  app.Originals.Hash(param.Video),
		Output: filepath.Join(fileDir, param.Base()),
		Script: filepath.Join(fileDir, param.Script()),
	}
}

func (app *App) animatedThumbnail(carveApp *vcarve.App, param *AnimRequest) error {
	exists, err := cachefs.Exists(carveApp.Output)
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	_, err = Download(app.Originals, param.Video)
	if err != nil {
		return err
	}

	err = cachefs.EnsureDir(carveApp.Output)
	if err != nil {
		return err
	}

	return carveApp.CarveSceneChange(param.MinDuration, param.Probability)
}

// HandleAnimThumb generates animated thumbnail on the fly.
func (app *App) HandleAnimThumb(w http.ResponseWriter, r *http.Request) {

	param, err := ParseAnimRequest(r)
	if err != nil {
		log.Print(err)
		jsonresp.New(http.StatusBadRequest).Err(err).Write(w)
		return
	}

	carveApp := app.CarveApp(param)

	log.Printf("Querying cache with key: %v", param.Video)
	err = app.animatedThumbnail(carveApp, param)
	if err != nil {
		log.Print(err)
		jsonresp.New(http.StatusInternalServerError).Err(err).Write(w)
		return
	}

	f, err := os.Open(carveApp.Output)
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
