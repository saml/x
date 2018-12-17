package ffmpeg

import (
	"bufio"
	"bytes"
	"os/exec"

	"github.com/rs/zerolog/log"
)

// App is an application that uses FFmpeg cli.
type App struct {
	Cmd string
}

// Runner can run FFmpeg cli.
type Runner interface {
	Exec(args ...string) (*bufio.Reader, error)
}

// Exec runs FFmpeg and return stderr.
func (app *App) Exec(args ...string) (*bufio.Reader, error) {
	cmd := exec.Command(app.Cmd, args...)
	log.Print("cmd=", cmd)
	var out bytes.Buffer
	cmd.Stderr = &out
	err := cmd.Run()
	return bufio.NewReader(&out), err

}
