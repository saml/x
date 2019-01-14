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
	"github.com/saml/x/vcarve/interval"
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

// CarveAppFromTimestamps returns carve application from timestamp thumbnail request.
func (app *App) CarveAppFromTimestamps(param *TimestampRequest) *vcarve.App {
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

func (app *App) thumbnailFromTimestamps(carveApp *vcarve.App, param *TimestampRequest) error {
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

	var intervals []*interval.Interval
	for i, j := 0, 1; j < len(param.Timestamps); i, j = i+2, j+2 {
		intervals = append(intervals, interval.New(param.Timestamps[i].Seconds(), param.Timestamps[j].Seconds()))
	}
	return carveApp.Carve(intervals)
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

// HandleTimestampThumb generates animated thumbnail on the fly using specified timestamps
func (app *App) HandleTimestampThumb(w http.ResponseWriter, r *http.Request) {

	param, err := ParseTimestampRequest(r)
	if err != nil {
		log.Print(err)
		jsonresp.New(http.StatusBadRequest).Err(err).Write(w)
		return
	}

	carveApp := app.CarveAppFromTimestamps(param)

	log.Printf("Querying cache with key: %v", param.Video)
	err = app.thumbnailFromTimestamps(carveApp, param)
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
