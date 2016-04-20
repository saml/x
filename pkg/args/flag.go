package args

import (
	"flag"
	"os"
)

// String reads string argument from environment variable or flag.
func String(key, envVar, defaultVal, usage string) *string {
	v := os.Getenv(envVar)
	if v == "" {
		v = defaultVal
	}

	return flag.String(key, v, usage+" "+envVar)
}
