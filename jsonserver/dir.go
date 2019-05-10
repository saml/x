package main

import "strings"

// Split splits path into first segment and the rest.
func Split(path string) (string, string) {
	seg := strings.Trim(path, "/")
	idx := strings.IndexByte(seg, '/')
	var rest string
	if idx >= 0 {
		seg = seg[:idx]
		rest = path[idx+1:]
	}
	return seg, rest
}
