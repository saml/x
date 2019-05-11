package main

import (
	"errors"
	"reflect"
)

// Resource supports CRUD
type Resource interface {
	// Add adds a child of given name.
	Add(name string, data Data) (Resource, error)

	// Write overwrites the child of given name.
	Write(name string, data Data) (Resource, error)

	// Update updates part of the child.
	Update(name string, patch Data) (Resource, error)

	// Read reads data of this Resource
	Read() Data

	// Child gives the child of the given name.
	Child(name string) (Resource, error)

	// Del deletes the child.
	Del(name string) (Resource, error)
}

// Data is JSON serializable.
type Data map[string]interface{}

// Children is child's name to data mapping.
type Children map[string]*InMemoryTree

// InMemoryTree has JSON data and maybe children.
type InMemoryTree struct {
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

// NewResource creates new resource without children.
func NewResource(data Data) *InMemoryTree {
	if data == nil {
		data = make(map[string]interface{})
	}
	return &InMemoryTree{
		Data:     data,
		Children: make(map[string]*InMemoryTree),
	}
}

// Read reads data.
func (res *InMemoryTree) Read() Data {
	return res.Data
}

// Child gives child resource.
func (res *InMemoryTree) Child(name string) (Resource, error) {
	child, ok := res.Children[name]
	if !ok {
		return nil, ErrNotFound
	}
	return child, nil
}

// Add adds a child.
func (res *InMemoryTree) Add(name string, data Data) (Resource, error) {
	child, ok := res.Children[name]
	if ok {
		return child, ErrExists
	}

	res.Children[name] = NewResource(data)

	return res.Child(name)
}

// Del deletes a child.
func (res *InMemoryTree) Del(name string) (Resource, error) {
	child, ok := res.Children[name]
	if !ok {
		return nil, ErrNotFound
	}
	delete(res.Children, name)
	return child, nil
}

// Write overwrites child.
func (res *InMemoryTree) Write(name string, data Data) (Resource, error) {
	child, ok := res.Children[name]
	if !ok {
		return nil, ErrNotFound
	}
	if reflect.DeepEqual(child.Data, data) {
		return child, ErrNoChange
	}
	child.Data = data
	return child, nil
}

// Update updates child.
func (res *InMemoryTree) Update(name string, patch Data) (Resource, error) {
	child, ok := res.Children[name]
	if !ok {
		return nil, ErrNotFound
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
