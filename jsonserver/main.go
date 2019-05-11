package main

// App is fake Media API implementation.
type App struct {
	Root Resource
}

func main() {
	root := &InMemoryTree{}
	root.Add("v1", nil)

}
