package interval

import (
	"bufio"
	"io"
	"math"
	"strconv"
)

// Interval is in seconds into video.
type Interval struct {
	Start float64
	End   float64
}

// New creates a new Interval.
func New(start float64, end float64) *Interval {
	// guarantee interval to be end >= start
	if end < start {
		end = start
	}
	return &Interval{
		Start: start,
		End:   end,
	}
}

// ReadIntervals reads a line separated series of intervals.
func ReadIntervals(r io.Reader) ([]*Interval, error) {
	start := math.NaN()
	var result []*Interval
	scanner := bufio.NewScanner(r)
	scanner.Split(bufio.ScanWords)
	for scanner.Scan() {
		word := scanner.Text()
		f, err := strconv.ParseFloat(word, 64)
		if err != nil {
			return nil, err
		}
		if !math.IsNaN(start) {
			result = append(result, New(start, f))
			start = math.NaN()
		} else {
			start = f
		}
	}
	return result, nil
}
