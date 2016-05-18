package main

import (
	"bufio"
	"encoding/json"
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

func tokenize(s string) []string {
	var tokens []string
	for _, tok := range strings.Split(s, " ") {
		tok = strings.TrimSpace(tok)
		if tok != "" {
			tokens = append(tokens, tok)
		}
	}
	return tokens
}

func fetchRepos(c *github.Client, orgName string) (map[string]github.Repository, error) {
	allRepos := make(map[string]github.Repository)
	repoOpt := &github.RepositoryListByOrgOptions{
		ListOptions: github.ListOptions{
			PerPage: 100,
		},
	}
	for {
		repos, resp, err := c.Repositories.ListByOrg(orgName, repoOpt)
		if err != nil {
			return nil, err
		}
		for _, repo := range repos {
			allRepos[*repo.Name] = repo
		}
		if resp.NextPage == 0 {
			break
		}
	}
	return allRepos, nil
}

func loadOrFetchRepos(c *github.Client, orgName string, filePath string) (map[string]github.Repository, error) {
	var allRepos map[string]github.Repository
	f, err := os.Open(filePath)
	if err != nil {
		log.Print(err)
		return fetchRepos(c, orgName)
	}

	defer f.Close()

	d := json.NewDecoder(f)
	err = d.Decode(&allRepos)
	return allRepos, err
}

func saveRepos(allRepos map[string]github.Repository, filePath string) error {
	f, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, os.ModePerm)
	if err != nil {
		return err
	}
	defer f.Close()
	e := json.NewEncoder(f)
	return e.Encode(allRepos)
}

func main() {
	token := args.String("token", "GITHUB_TOKEN", "", "github api token")
	orgName := args.String("org", "GITHUB_ORGANIZATION", "", "github organization name")
	reposFile := args.String("repos", "GITHUB_REPOS_FILE", "./repos.json", "github repositories")
	flag.Parse()

	ts := oauth2.StaticTokenSource(&oauth2.Token{
		AccessToken: *token,
	})
	tc := oauth2.NewClient(oauth2.NoContext, ts)

	client := github.NewClient(tc)

	var allRepos map[string]github.Repository
	var err error
	allRepos, err = loadOrFetchRepos(client, *orgName, *reposFile)
	if err != nil {
		log.Fatal(err)
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
		tokens := tokenize(line)
		if len(tokens) < 1 {
			fmt.Println(".COMMAND ARG1 ARG2 ...")
			continue
		}

		command := tokens[0]
		arguments := tokens[1:]
		switch command {
		case ".quit":
			break
		case ".save":
			err := saveRepos(allRepos, *reposFile)
			if err != nil {
				fmt.Println(err.Error())
			} else {
				fmt.Printf("Saved %s\n", *reposFile)
			}
		case ".repos":
			for repoName, repo := range allRepos {
				fmt.Printf("%s %s\n", repoName, *repo.URL)
			}
		case ".release":
			if len(arguments) < 1 {
				fmt.Println(".release REPO")
			} else {
				repoName := arguments[0]
				repo, ok := allRepos[repoName]
				if !ok {
					fmt.Println("Repo not found")
				} else {
					release, _, err := client.Repositories.GetLatestRelease(*repo.Owner.Login, *repo.Name)
					if err != nil {
						fmt.Printf("ERROR %s\n", err.Error())
					} else {
						fmt.Println(*release.TagName)
					}
				}
			}
		}
	}

}
