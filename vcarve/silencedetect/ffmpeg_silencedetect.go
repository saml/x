package silencedetect

import (
	"bufio"
	"io/ioutil"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve"
	"github.com/saml/x/vcarve/ffmpeg"
)

func readAll(stderr *bufio.Reader) string {
	out, err := ioutil.ReadAll(stderr)
	if err != nil {
		log.Print(err)
		return ""
	}
	return string(out)
}

// Exec runs ffmpeg to detect silence intervals.
func Exec(ff ffmpeg.Runner, vid string) ([]vcarve.Interval, error) {
	args := []string{"-hide_banner", "-i", vid, "-af", "silencedetect=duration=1:noise=0.1", "-f", "null", "-"}
	stderr, err := ff.Exec(args...)
	if err != nil {
		log.Print(readAll(stderr))
		return nil, err
	}
	return parse(stderr)
}

func parse(stderr *bufio.Reader) ([]vcarve.Interval, error) {
	scanner := bufio.NewScanner(stderr)
	for scanner.Scan() {
		log.Print(scanner.Text())
	}
	log.Print("hello")
	// log.Print(readAll(stderr))
	return []vcarve.Interval{}, nil
}
