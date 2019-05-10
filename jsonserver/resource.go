package main

import (
	"errors"
	"reflect"
)

// Data is JSON serializable.
type Data map[string]interface{}

// Children is child's name to data mapping.
type Children map[string]*Resource

// Resource has JSON data and maybe children.
type Resource struct {
	Data     Data
	Children Children
}

var (
	// ErrExists is when child already exists.
	ErrExists = errors.New("ERR_EXISTS")

	// ErrNotFound is when child isn't found.
	ErrNotFound = errors.New("ERR_NOTFOUND")

	// ErrNoChange is when update results in no change.
	ErrNoChange = errors.New("ERR_NOCHANGE")
)

func (res *Resource) Has(name string) bool {
	_, ok := res.Children[name]
	return ok
}

// Add adds a child.
func (res *Resource) Add(name string, data Data) error {
	_, ok := res.Children[name]
	if ok {
		return ErrExists
	}
	res.Children[name] = &Resource{
		Data: data,
	}
	return nil
}

// Del deletes a child.
func (res *Resource) Del(name string) error {
	_, ok := res.Children[name]
	if !ok {
		return ErrNotFound
	}
	delete(res.Children, name)
	return nil
}

// Write overwrites child.
func (res *Resource) Write(name string, data Data) error {
	child, ok := res.Children[name]
	if !ok {
		return ErrNotFound
	}
	if reflect.DeepEqual(child.Data, data) {
		return ErrNoChange
	}
	child.Data = data
	return nil
}

// Update updates child.
func (res *Resource) Update(name string, patch Data) error {
	child, ok := res.Children[name]
	if !ok {
		return ErrNotFound
	}
	var newData Data
	for k, v := range child.Data {
		newData[k] = v
	}
	for k, v := range patch {
		newData[k] = v
	}
	return res.Write(name, newData)
}
