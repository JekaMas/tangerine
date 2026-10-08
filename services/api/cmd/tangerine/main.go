package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"tangerine.local/api/internal/app"
)

func run() error {
	mode := "serve"
	if len(os.Args) > 1 {
		mode = os.Args[1]
	}
	if mode == "healthcheck" {
		client := http.Client{Timeout: 6 * time.Second}
		res, err := client.Get("http://127.0.0.1:8080/health/ready")
		if err != nil {
			return fmt.Errorf("API is unavailable")
		}
		defer res.Body.Close()
		if res.StatusCode != 200 {
			return fmt.Errorf("API is not ready")
		}
		return nil
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	store, err := app.OpenStorage(ctx, os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	if err != nil {
		return fmt.Errorf("local storage configuration is unavailable")
	}
	defer store.DB.Close()
	switch mode {
	case "migrate":
		return store.Migrate(ctx)
	case "media-init":
		return store.InitMedia(ctx)
	case "initialize":
		return store.InitializeAccount(ctx, os.Getenv("INITIAL_EMAIL"), os.Getenv("INITIAL_PASSWORD"))
	case "serve":
	default:
		return fmt.Errorf("unknown command")
	}
	origin := os.Getenv("APP_ORIGIN")
	if err = app.ValidateOrigin(origin); err != nil {
		return err
	}
	server := &http.Server{Addr: ":8080", Handler: app.NewServer(store, origin, os.Getenv("SPEECH_URL")).Handler(), ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 10 * time.Second, WriteTimeout: app.OverallDeadline, IdleTimeout: 60 * time.Second, MaxHeaderBytes: 16 * 1024}
	shutdownCtx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	finished := make(chan error, 1)
	go func() { finished <- server.ListenAndServe() }()
	select {
	case err = <-finished:
		if err != http.ErrServerClosed {
			return fmt.Errorf("HTTP listener failed")
		}
	case <-shutdownCtx.Done():
		deadline, done := context.WithTimeout(context.Background(), 10*time.Second)
		defer done()
		return server.Shutdown(deadline)
	}
	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "Tangerine operation failed; check local prerequisites and configuration.")
		os.Exit(1)
	}
}
