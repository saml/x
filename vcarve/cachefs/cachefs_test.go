package cachefs_test

import (
	"net/url"
	"testing"

	"github.com/saml/x/vcarve/cachefs"
)

var urlHashTests = []struct {
	url    string
	fsPath string
}{
	{"https://a", "/cachefs/https/a"},
	{"http://a:80/b", "/cachefs/http/a:80/b"},
	{"http://a/b?q=c", "/cachefs/http/a/b"},
}

func TestHash(t *testing.T) {
	cache := cachefs.CacheFS{
		Dir: "/cachefs",
	}
	for _, testcase := range urlHashTests {
		t.Run(testcase.url, func(t *testing.T) {
			u, err := url.Parse(testcase.url)
			if err != nil {
				t.Errorf("Invalid url: %v", err)
			} else {
				fsPath := cache.Hash(u)
				if fsPath != testcase.fsPath {
					t.Errorf("Expected: %v != %v", testcase.fsPath, fsPath)
				}
			}
		})
	}
}
