package ffmpeg

import (
	"bufio"
	"bytes"
	"os/exec"

	"github.com/rs/zerolog/log"
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
