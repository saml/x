package main

import (
	"path"
	"strings"
)

// Split splits path into first segment and the rest.
func Split(resPath string) (string, string) {
	seg := strings.Trim(resPath, "/")
	idx := strings.IndexByte(seg, '/')
	var rest string
	if idx >= 0 {
		seg = seg[:idx]
		rest = resPath[idx+1:]
	}
	return seg, rest
}

// EnsureDirs creates given directory and all parent directories.
func EnsureDirs(res Resource, dirPath string) (Resource, error) {
	seg, rest := Split(dirPath)
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
	dirPath, name := path.Split(resPath)
	dir, err := EnsureDirs(res, dirPath)
	if err != nil {
		return nil, err
	}
	return dir.Add(name, data)
}
