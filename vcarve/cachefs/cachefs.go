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
