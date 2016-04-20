package slackbot

import (
	"log"
)

type message struct {
	Type      string `json:"type"`
	UserID    string `json:"user"`
	ChannelID string `json:"channel"`
	Text      string `json:"text"`
}

func (c *Client) processMessages(done chan struct{}) {
	defer close(done)

	var msg message
	for {
		err := c.conn.ReadJSON(&msg)
		if err != nil {
			log.Fatal(err)
		}

		log.Printf("> %s [%s] @%s: %s", msg.Type, c.channelName(msg.ChannelID), c.userName(msg.UserID), msg.Text)
	}
}

func (c *Client) userName(userID string) string {
	name, ok := c.userNames[userID]
	if !ok {
		return userID
	}
	return name
}

func (c *Client) channelName(channelID string) string {
	name, ok := c.channelNames[channelID]
	if !ok {
		return channelID
	}
	return name
}
