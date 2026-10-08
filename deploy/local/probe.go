package main

import (
	"net/http"
	"os"
	"time"
)

func main() {
	if len(os.Args) != 2 {
		os.Exit(1)
	}
	client := &http.Client{Timeout: 5 * time.Second}
	res, err := client.Get(os.Args[1])
	if err != nil {
		os.Exit(1)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		os.Exit(1)
	}
}
