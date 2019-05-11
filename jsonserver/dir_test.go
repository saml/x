package main

import (
	"reflect"
	"testing"
)

func TestSplitSegEmpty(t *testing.T) {
	seg, rest := SplitSeg("")
	if seg != "" {
		t.Errorf("Expected seg to be empty")
	}
	if rest != "" {
		t.Errorf("Expected rest to be empty")
	}
}

func TestSplitSegSlash(t *testing.T) {
	seg, rest := SplitSeg("/")
	if seg != "" {
		t.Errorf("Expected seg to be empty")
	}
	if rest != "" {
		t.Errorf("Expected rest to be empty")
	}
}

func TestSplitSegOneSeg(t *testing.T) {
	seg, rest := SplitSeg("/a")
	if seg != "a" {
		t.Errorf("Seg is wrong.")
	}
	if rest != "" {
		t.Errorf("Expected rest to be empty")
	}
}

func TestSplitSegOneSegNoSlash(t *testing.T) {
	seg, rest := SplitSeg("a")
	if seg != "a" {
		t.Errorf("Seg is wrong.")
	}
	if rest != "" {
		t.Errorf("Expected rest to be empty")
	}
}

func TestSplit(t *testing.T) {
	dir, file := Split("/a/b/c")

	if dir != "a/b" {
		t.Errorf("Dir is wrong: %v", dir)
	}
	if file != "c" {
		t.Errorf("File is wrong: %v", file)
	}
}
func TestSplitSegHasRest(t *testing.T) {
	seg, rest := SplitSeg("/a/b/")
	if seg != "a" {
		t.Errorf("Seg is wrong.")
	}
	if rest != "/b/" {
		t.Errorf("Rest is wrong: rest=%v", rest)
	}
}

func TestAddNew(t *testing.T) {
	res := NewRoot()

	child, err := Add(res, "/a", nil)

	if err != nil {
		t.Errorf("Expecting no error. But got: %v", err)
	}
	if len(child.Read()) != 0 {
		t.Errorf("Expecting empty child data.")
	}
}

func TestAddCreatesParents(t *testing.T) {
	root := NewRoot()
	resPath := "/a/b/c"

	res, err := Add(root, resPath, nil)

	if err != nil {
		t.Errorf("Expecting no error. But got: %v", err)
	}
	if len(res.Read()) != 0 {
		t.Errorf("Expecting empty res data.")
	}
	AssertAllExist(t, root, resPath)
}

func TestEnsureDirDoesNotCreateExisting(t *testing.T) {
	root := NewRoot()
	resPath := "/a"
	data := make(Data)
	data["foo"] = "bar"
	a, err := Add(root, resPath, data)
	if err != nil {
		t.Errorf("Expecting no error. But got: %v", err)
	}

	b, err := Add(root, "/a/b", nil)

	if err != nil {
		t.Errorf("Expecting no error. But got: %v", err)
	}
	if len(b.Read()) != 0 {
		t.Errorf("Expecting empty res data.")
	}
	if !reflect.DeepEqual(data, a.Read()) {
		t.Errorf("Expecting existing resource to not be altered")
	}

}

func AssertAllExist(t *testing.T, res Resource, resPath string) {
	head, tail := SplitSeg(resPath)
	if head != "" {
		child, err := res.Child(head)
		if err != nil {
			t.Errorf("Expecting a resource to exist: %v", head)
			return
		}
		AssertAllExist(t, child, tail)
	}
}

func NewRoot() Resource {
	return NewResource(nil)
}
