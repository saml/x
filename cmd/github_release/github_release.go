package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"strings"

	"github.com/google/go-github/github"
	"golang.org/x/oauth2"

	"github.com/saml/x/pkg/args"
)

func main() {
	token := args.String("token", "GITHUB_TOKEN", "", "github api token")
	flag.Parse()

	ts := oauth2.StaticTokenSource(&oauth2.Token{
		AccessToken: *token,
	})
	tc := oauth2.NewClient(oauth2.NoContext, ts)

	client := github.NewClient(tc)
	repos, _, err := client.Repositories.List("", nil)
	if err != nil {
		log.Fatal(err)
	}
	for _, repo := range repos {
		fmt.Println(*repo.Name)

	}

	reader := bufio.NewReader(os.Stdin)

	for {
		fmt.Print("> ")
		line, err := reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				fmt.Println("")
				break
			}
			log.Fatal(err)
		}
		line = strings.TrimSpace(line)

		fmt.Println(line)
	}

}
