package ffmpeg

import (
	"bufio"
	"bytes"
	"os/exec"
	"strconv"
	"strings"

	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/streams"
)

// App is an application that uses FFmpeg cli.
type App struct {
	FFmpeg  string
	FFprobe string
}

// Runner can run FFmpeg cli.
type Runner interface {
	ExecFFmpeg(args ...string) (*bufio.Reader, error)
	ExecFFprobe(args ...string) (*bufio.Reader, error)
}

// ExecFFmpeg runs FFmpeg and return stderr.
func (app *App) ExecFFmpeg(args ...string) (*bufio.Reader, error) {
	cmd := exec.Command(app.FFmpeg, args...)
	log.Print("cmd=", cmd)
	var out bytes.Buffer
	cmd.Stderr = &out
	err := cmd.Run()
	return bufio.NewReader(&out), err
}

// ExecFFprobe runs FFprobe and return stdout.
func (app *App) ExecFFprobe(args ...string) (*bufio.Reader, error) {
	cmd := exec.Command(app.FFprobe, args...)
	log.Print("cmd=", cmd)
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	return bufio.NewReader(&out), err
}

// Duration reads duration of video.
func Duration(ff Runner, vid string) (float64, error) {
	stdout, err := ff.ExecFFprobe("-loglevel", "error", "-show_entries", "format=duration", "-of", "csv=print_section=0", "-i", vid)
	if err != nil {
		return 0, err
	}

	line := strings.TrimSpace(streams.ReadString(stdout))
	result, err := strconv.ParseFloat(line, 64)
	if err != nil {
		return 0, err
	}
	return result, nil

}
