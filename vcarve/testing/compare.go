package testing

import (
	"math"

	"github.com/saml/x/vcarve/interval"
)

// FloatEpsilon is allowed error when comparing floats.
const FloatEpsilon = 0.0001

// FloatSimilar tests if two floats are similar.
func FloatSimilar(a float64, b float64, args ...float64) bool {
	var epsilon float64
	if len(args) < 1 {
		epsilon = FloatEpsilon
	} else {
		epsilon = args[0]
	}
	return math.Abs(a-b) <= epsilon
}

// IntervalSimilar tests if two Intervals are same.
func IntervalSimilar(a *interval.Interval, b *interval.Interval) bool {
	return FloatSimilar(a.Start, b.Start) && FloatSimilar(a.End, b.End)
}
