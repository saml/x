.PHONY: clean

bin/slackbot: cmd/slackbot/*.go pkg/**/*.go
	wgo build -o $@ ./cmd/slackbot

clean:
	rm -rf bin
