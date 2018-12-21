package http

import (
	"io"
	"net/http"
	"net/url"
	"os"
	"time"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/cachefs"
)

// Client is default http client.
var Client = &http.Client{
	Timeout: 10 * time.Minute,
}

// Download downloads video if it does not exist in cache.
func Download(cache *cachefs.CacheFS, u *url.URL) (string, error) {
	filePath := cache.Hash(u)
	exists, err := cachefs.Exists(filePath)
	if err != nil {
		return "", err
	}
	if !exists {
		log.Printf("Downloading: %v => %v", u, filePath)
		res, err := Client.Get(u.String())
		if err != nil {
			return "", err
		}
		defer res.Body.Close()
		err = cachefs.EnsureDir(filePath)
		if err != nil {
			return "", err
		}
		f, err := os.Create(filePath)
		if err != nil {
			return "", err
		}
		defer f.Close()
		n, err := io.Copy(f, res.Body)
		if err != nil {
			return "", err
		}
		log.Printf("Downloaded file: %v (%v)", filePath, n)
	}
	return filePath, nil
}
