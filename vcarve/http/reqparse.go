package http

import (
	"fmt"
	"net/http"
	"net/url"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// TimestampRequest is request to only include given timestamps
type TimestampRequest struct {
	Video      *url.URL
	Timestamps []time.Duration // must be even number of elements
}

// ParseTimestampRequest parses TimestampRequest out of request.
func ParseTimestampRequest(r *http.Request) (*TimestampRequest, error) {
	q := r.URL.Query()
	key, err := url.ParseRequestURI(q.Get("v"))
	if err != nil {
		return nil, parseErr("v", err)
	}

	var timestamps []time.Duration
	for _, timestamp := range strings.Split(q.Get("t"), ",") {
		t, err := time.ParseDuration(timestamp)
		if err != nil {
			return nil, parseErr("t", err)
		}
		timestamps = append(timestamps, t)
	}
	return &TimestampRequest{
		Video:      key,
		Timestamps: timestamps,
	}, nil
}

// Base is file name of timestamp request.
func (a *TimestampRequest) Base() string {
	base := filepath.Base(a.Video.Path)
	var timestamps []string
	for _, t := range a.Timestamps {
		timestamps = append(timestamps, strconv.FormatFloat(t.Seconds(), 'f', -1, 64))
	}
	return fmt.Sprintf("%s_%s_%s", base, strings.Join(timestamps, "."), filepath.Ext(base))
}

// Script returns filter script name (not full path).
func (a *TimestampRequest) Script() string {
	return a.Base() + ".filter.txt"
}

// AnimRequest is animated thumbnail generation requeste parameter.
type AnimRequest struct {
	Video       *url.URL
	Probability float64
	MinDuration float64
}

// ParseError represents request parsing error.
type ParseError struct {
	Param string
	Err   error
}

func (p *ParseError) Error() string {
	return p.Param + ": " + p.Err.Error()
}

func parseErr(param string, err error) *ParseError {
	return &ParseError{
		Param: param,
		Err:   err,
	}
}

// ParseAnimRequest extracts animated thumbnail request parameters.
func ParseAnimRequest(r *http.Request) (*AnimRequest, error) {
	q := r.URL.Query()
	key, err := url.ParseRequestURI(q.Get("v"))
	if err != nil {
		return nil, parseErr("v", err)
	}
	probability, err := strconv.ParseFloat(q.Get("prob"), 64)
	if err != nil {
		probability = 0.6
	}
	duration, err := strconv.ParseFloat(q.Get("len"), 64)
	if err != nil {
		duration = 1.0
	}
	return &AnimRequest{
		Video:       key,
		Probability: probability,
		MinDuration: duration,
	}, nil
}

// Base is file name of animated thumbnail request.
func (a *AnimRequest) Base() string {
	base := filepath.Base(a.Video.Path)
	return fmt.Sprintf("%s_p%.6f_d%.6f_%s", base, a.Probability, a.MinDuration, filepath.Ext(base))
}

// Script returns filter script name (not full path).
func (a *AnimRequest) Script() string {
	return a.Base() + ".filter.txt"
}
