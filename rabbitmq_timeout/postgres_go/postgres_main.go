package main

import (
	"bufio"
	"context"
	"database/sql"
	"log"
	"os"
	"time"

	_ "github.com/lib/pq"
)

func main() {
	db, err := sql.Open("postgres", "dbname=postgres user=postgres password=postgres host=localhost port=5434 client_encoding=utf8 sslmode=disable")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	ctx, stop := context.WithCancel(context.Background())
	defer stop()
	ctx, cancel := context.WithTimeout(ctx, 200*time.Second)
	defer cancel()
	tx, err := db.BeginTx(ctx, nil)
	if err != nil {
		log.Fatal(err)
	}

	result, err := tx.ExecContext(ctx, "insert into foo(id) values (1)")
	if err != nil {
		log.Fatal(err)
	}

	reader := bufio.NewReader(os.Stdin)
	log.Printf("Got result: %v Press Enter to continue.", result)
	_, err = reader.ReadString('\n')
	if err != nil {
		log.Fatal(err)
	}

	err = tx.Commit()
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("Committed.")
}
