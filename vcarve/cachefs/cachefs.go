package cachefs

import (
	"net/url"
	"os"
	"path"
)

// CacheFS is filesystem based cache.
type CacheFS struct {
	Dir string
}

// Hash returns filesystem cache path for the url.
func (c *CacheFS) Hash(key *url.URL) string {
	return path.Join(c.Dir, key.Scheme, key.Host, key.Path)
}

// Open opens file for key.
func (c *CacheFS) Open(key *url.URL) (*os.File, error) {
	return os.Open(c.Hash(key))
}

// Exists tests if file path exists in cache.
func Exists(filePath string) (bool, error) {
	_, err := os.Stat(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

// EnsureDir creates directory the file will be in.
func EnsureDir(filePath string) error {
	return os.MkdirAll(path.Dir(filePath), 0755)
}
