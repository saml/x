package interval

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
