package main

// App is fake Media API implementation.
type App struct {
	Root *Resource
}

// func AddRoute(res *Resource, path string, data Data) error {
// 	name, rest := segment(path)
// 	child, ok := res.Children[name]
// 	if ok {
// 		if rest != "" {
// 			return AddRoute(child, rest, data)
// 		}
// 	} else {
// 		child = &Resource{}
// 	}
// 	if name != "" {

// 	}
// }

func (app *App) Add(path string, data Data) error {
	return nil
}

func main() {
	root := &Resource{}
	root.Add("v1", nil)

}
