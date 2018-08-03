package main

import (
	"encoding/xml"
	"flag"
	"fmt"
	"log"
	"net/http"
	"time"
)

// SitemapIndex is <sitemapindex>
type SitemapIndex struct {
	XMLName xml.Name  `xml:"sitemapindex"`
	Sitemap []Sitemap `xml:"sitemap"`
}

// Sitemap is <sitemap>
type Sitemap struct {
	Loc string `xml:"loc"`
}

// URLSet is <urlset>
type URLSet struct {
	XMLName xml.Name `xml:"urlset"`
	URL     []URL    `xml:"url"`
}

// URL is <url>
type URL struct {
	Loc string `xml:"loc"`
}

// App is main application
type App struct {
	httpClient *http.Client
}

func (app *App) fetchSitemapURLs(indexURL string) (*SitemapIndex, error) {
	log.Printf("GET %s", indexURL)
	resp, err := app.httpClient.Get(indexURL)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var index SitemapIndex
	d := xml.NewDecoder(resp.Body)
	err = d.Decode(&index)
	if err != nil {
		return nil, err
	}
	return &index, nil
}

func (app *App) fetchURLs(urlsetURL string) (*URLSet, error) {
	log.Printf("GET %s", urlsetURL)
	resp, err := app.httpClient.Get(urlsetURL)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	var urlset URLSet
	d := xml.NewDecoder(resp.Body)
	err = d.Decode(&urlset)
	if err != nil {
		return nil, err
	}
	return &urlset, nil
}

func main() {
	indexURL := flag.String("url", "", "sitemapindex url")
	flag.Parse()

	c := http.Client{
		Timeout: 10 * time.Second,
	}
	app := App{
		httpClient: &c,
	}

	index, err := app.fetchSitemapURLs(*indexURL)
	if err != nil {
		log.Fatal(err)
	}

	for _, sitemap := range index.Sitemap {
		urlset, err := app.fetchURLs(sitemap.Loc)
		if err != nil {
			log.Fatal(err)
		}
		for _, url := range urlset.URL {
			fmt.Println(url.Loc)
		}
	}
}
