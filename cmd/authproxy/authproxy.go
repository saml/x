// http basic auth proxy

package main

import (
	"encoding/base64"
	"flag"
	"io"
	"log"
	"net/http"
	"time"
)

type App struct {
	upstream   string
	authHeader string
	client     *http.Client
}

func (a *App) onRedirect(req *http.Request, via []*http.Request) error {
	req.Header.Add("Authorization", a.authHeader)
	return nil
}

func (a *App) onRequest(w http.ResponseWriter, req *http.Request) {
	req, err := http.NewRequest("GET", a.upstream+req.URL.Path, nil)
	log.Printf("GET %s%s", a.upstream, req.URL.Path)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	req.Header.Add("Authorization", a.authHeader)
	res, err := a.client.Do(req)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	defer res.Body.Close()
	_, err = io.Copy(w, res.Body)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
}

func main() {
	upstream := flag.String("url", "http://localhost", "url to proxy")
	addr := flag.String("addr", ":8080", "local address to listen to")
	auth := flag.String("auth", "", "username:password for basic auth")
	timeout := flag.Int("timeout", 30, "request timeout in seconds")

	flag.Parse()

	authHeader := "Basic " + base64.StdEncoding.EncodeToString([]byte(*auth))
	app := &App{
		upstream:   *upstream,
		authHeader: authHeader,
	}

	client := &http.Client{
		Timeout:       time.Duration(*timeout) * time.Second,
		CheckRedirect: app.onRedirect,
	}
	app.client = client

	mux := http.NewServeMux()
	mux.HandleFunc("/", app.onRequest)
	log.Printf("Listening to %s", *addr)
	log.Printf("Proxying %s", *upstream)
	log.Fatal(http.ListenAndServe(*addr, mux))
}
