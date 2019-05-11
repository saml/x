package main

import (
	"strings"
)

// SplitSeg splits path into first segment and the rest.
func SplitSeg(resPath string) (string, string) {
	seg := strings.Trim(resPath, "/")
	idx := strings.IndexByte(seg, '/')
	var rest string
	if idx >= 0 {
		seg = seg[:idx]
		rest = resPath[idx+1:]
	}
	return seg, rest
}

// Split splits path into dir and file.
func Split(resPath string) (string, string) {
	dir := strings.Trim(resPath, "/")
	idx := strings.LastIndexByte(dir, '/')
	var file string
	if idx >= 0 {
		file = dir[idx+1:]
		dir = dir[:idx]
	}
	return dir, file
}

// EnsureDirs creates given directory and all parent directories.
func EnsureDirs(res Resource, dirPath string) (Resource, error) {
	seg, rest := SplitSeg(dirPath)
	if seg == "" {
		return res, nil
	}

	child, err := res.Add(seg, nil)
	if child != nil {
		return EnsureDirs(child, rest)
	}
	return nil, err
}

// Add adds a new resource.
func Add(res Resource, resPath string, data Data) (Resource, error) {
	dirPath, name := Split(resPath)
	dir, err := EnsureDirs(res, dirPath)
	if err != nil {
		return nil, err
	}
	return dir.Add(name, data)
}
