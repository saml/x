.PHONY: clean test all

all: bin/slackbot bin/github_release

bin/%: pkg/**/*.go cmd/%/*.go
	wgo build -o $@ ./cmd/$(@F)

test:
	go fmt ./pkg/... ./cmd/...
	go vet ./pkg/... ./cmd/...
	golint ./pkg/...
	golint ./cmd/...
	go test ./pkg/... ./cmd/...

clean:
	rm -rf bin


