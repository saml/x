package slackbot

import (
	"encoding/json"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"time"

	"github.com/gorilla/websocket"
)

var (
	// StartURL is default endpoint for slack connection.
	StartURL = "https://slack.com/api/rtm.start"

	httpClient = http.Client{
		Timeout: time.Duration(10 * time.Second),
	}
)

// SlackUser is a user.
type slackUser struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type slackChannel struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type slackPrivateMessage struct {
	ID     string `json:"id"`
	UserID string `json:"user"`
}

// Client is slack bot client.
type Client struct {
	WebSocketURL string                `json:"url"`
	Users        []slackUser           `json:"users"`
	Bots         []slackUser           `json:"bots"`
	Channels     []slackChannel        `json:"channels"`
	PMs          []slackPrivateMessage `json:"ims"`
	conn         *websocket.Conn
	userNames    map[string]string
	channelNames map[string]string
}

// New creates new bot.
func New(token string) (*Client, error) {
	start, err := url.Parse(StartURL)
	if err != nil {
		return nil, err
	}
	q := start.Query()
	q.Set("token", token)
	start.RawQuery = q.Encode()

	res, err := httpClient.Get(start.String())
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	d := json.NewDecoder(res.Body)
	var client Client
	err = d.Decode(&client)
	if err != nil {
		return nil, err
	}

	client.userNames = make(map[string]string)
	for _, user := range client.Users {
		client.userNames[user.ID] = user.Name
	}
	for _, user := range client.Bots {
		client.userNames[user.ID] = user.Name
	}

	client.channelNames = make(map[string]string)
	for _, channel := range client.Channels {
		client.channelNames[channel.ID] = channel.Name
	}
	for _, channel := range client.PMs {
		client.channelNames[channel.ID] = client.userName(channel.UserID) // client.userName() only works after initializing userNames
	}

	return &client, nil
}

// Start connects to chat and starts bot.
func (c *Client) Start() {
	conn, _, err := websocket.DefaultDialer.Dial(c.WebSocketURL, nil)
	if err != nil {
		log.Fatal(err)
	}

	defer conn.Close()
	c.conn = conn

	done := make(chan struct{})
	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, os.Interrupt)

	go c.processMessages(done)
	for {
		select {
		case <-interrupt:
			err = conn.WriteMessage(websocket.CloseMessage, websocket.FormatCloseMessage(websocket.CloseNormalClosure, ""))
			if err != nil {
				log.Fatal(err)
			}
			select {
			case <-done:
			case <-time.After(time.Second):
			}
			return
		}
	}
}
