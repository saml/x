package streams

import (
	"bufio"
	"io/ioutil"

	"github.com/rs/zerolog/log"
)

// ReadString reads as string.
func ReadString(reader *bufio.Reader) string {
	out, err := ioutil.ReadAll(reader)
	if err != nil {
		log.Print(err)
		return ""
	}
	return string(out)
}
