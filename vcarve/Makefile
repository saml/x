.PHONY: clean test all

all: bin/vcarve

bin/%: cmd/%/*.go
	go build -o $@ ./cmd/$(@F)

test:
	go fmt ./...
	go vet ./...
	go test -v ./...

clean:
	rm -rf bin


