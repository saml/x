package vcarve

import (
	"bufio"
	"io/ioutil"

	"github.com/rs/zerolog/log"
)

// ReadString reads as string.
func ReadString(stderr *bufio.Reader) string {
	out, err := ioutil.ReadAll(stderr)
	if err != nil {
		log.Print(err)
		return ""
	}
	return string(out)
}
