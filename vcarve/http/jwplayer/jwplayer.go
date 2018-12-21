package jwplayer

import (
	"encoding/json"
	"net/http"

	"github.com/rs/zerolog/log"
)

// Feed is a media feed
type Feed struct {
	Playlist []*Media `json:"playlist"`
}

// Media is a video
type Media struct {
	Thumbnail  string       `json:"image"`
	Renditions []*Rendition `json:"sources"`
}

// Rendition is a particular encoding of a video.
type Rendition struct {
	Width  *int   `json:"width"`
	Height *int   `json:"height"`
	Type   string `json:"type"`
	URL    string `json:"file"`
}

// Width finds a rendition of specified width.
func (m *Media) Width(width int) *Rendition {
	for _, rendition := range m.Renditions {
		if rendition.Width != nil && *rendition.Width == width {
			return rendition
		}
	}
	return nil
}

// FetchFeed fetches jwplayer json feed.
func FetchFeed(feedID string) (*Feed, error) {
	feedURL := "http://cdn.jwplayer.com/v2/playlists/" + feedID
	log.Printf("Fetching feed: %v", feedURL)
	resp, err := http.Get(feedURL)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var feed Feed
	err = json.NewDecoder(resp.Body).Decode(&feed)
	if err != nil {
		return nil, err
	}
	return &feed, nil
}
