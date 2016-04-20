package main

import (
	"flag"
	"log"

	"github.com/saml/x/pkg/args"
	"github.com/saml/x/pkg/slackbot"
)

func main() {
	token := args.String("token", "SLACK_API_TOKEN", "", "Slack API token.")
	flag.Parse()

	bot, err := slackbot.New(*token)
	if err != nil {
		log.Fatal(err)
	}
	bot.Start()
}
