.PHONY: clean test all

all: bin/vcarve bin/vcarvesilence bin/vcarvescenechange bin/scenedetect bin/vcarveserver

bin/%: cmd/%/*.go *.go ./**/*.go
	go build -o $@ ./cmd/$(@F)

test:
	go fmt ./...
	go vet ./...
	go test ./...

clean:
	rm -rf bin


