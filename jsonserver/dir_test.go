package main

import (
	"testing"
)

func TestSplitEmpty(t *testing.T) {
	seg, rest := Split("")
	if seg != "" {
		t.Errorf("Expected seg to be empty")
	}
	if rest != "" {
		t.Errorf("Expected rest to be empty")
	}
}

func TestSplitSlash(t *testing.T) {
	seg, rest := Split("/")
	if seg != "" {
		t.Errorf("Expected seg to be empty")
	}
	if rest != "" {
		t.Errorf("Expected rest to be empty")
	}
}

func TestSplitOneSeg(t *testing.T) {
	seg, rest := Split("/a")
	if seg != "a" {
		t.Errorf("Seg is wrong.")
	}
	if rest != "" {
		t.Errorf("Expected rest to be empty")
	}
}

func TestSplitOneSegNoSlash(t *testing.T) {
	seg, rest := Split("a")
	if seg != "a" {
		t.Errorf("Seg is wrong.")
	}
	if rest != "" {
		t.Errorf("Expected rest to be empty")
	}
}

func TestSplitHasRest(t *testing.T) {
	seg, rest := Split("/a/b/")
	if seg != "a" {
		t.Errorf("Seg is wrong.")
	}
	if rest != "/b/" {
		t.Errorf("Rest is wrong: rest=%v", rest)
	}
}
