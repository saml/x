.PHONY: clean test all

all: bin/vcarve bin/vcarvesilence bin/vcarvescenechange bin/scenedetect

bin/%: cmd/%/*.go
	go build -o $@ ./cmd/$(@F)

test:
	go fmt ./...
	go vet ./...
	go test ./...

clean:
	rm -rf bin


