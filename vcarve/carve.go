package vcarve

import (
	"github.com/rs/zerolog/log"

	"github.com/saml/x/vcarve/ffmpeg"
	"github.com/saml/x/vcarve/silencedetect"
)

// CarveSilence carves silence from video.
func CarveSilence(ff ffmpeg.Runner, vid string) error {
	silences, err := silencedetect.Exec(ff, vid)
	if err != nil {
		return err
	}

	keyFrames, err := ExecKeyFrames(ff, vid)
	if err != nil {
		return err
	}

	intervals := silencedetect.Include(silences, keyFrames)
	for _, pair := range intervals {
		log.Print(pair)
	}
	return nil
}
