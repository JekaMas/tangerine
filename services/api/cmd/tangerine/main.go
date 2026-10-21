package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"tangerine.local/api/internal/app"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/localctl"
)

func run() error {
	mode := "serve"
	if len(os.Args) > 1 {
		mode = os.Args[1]
	}
	if mode == "lab-portcheck" || mode == "lab-healthcheck" {
		if len(os.Args) != 3 {
			return fmt.Errorf("LAB_PORT_INVALID")
		}
		return app.CheckLabPublic(context.Background(), os.Args[2], mode == "lab-portcheck")
	}
	if mode == "local-maintenance" {
		ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
		defer stop()
		return localctl.Command(ctx, os.Getenv("TANGERINE_ROOT"), os.Getenv("COMPOSE_PROJECT_NAME"), os.Getenv("TANGERINE_RUNTIME_FILE"), os.Args[2:], os.Stdout)
	}
	if mode == "lab-json" {
		return lab.Command(os.Stdin, os.Stdout)
	}
	if mode == "configure" {
		return app.ConfigureLocal(os.Getenv("TANGERINE_OPERATOR_FILE"), os.Getenv("TANGERINE_RUNTIME_DIR"))
	}
	if mode == "redact" {
		return app.Redact(os.Stdin, os.Stdout)
	}
	if mode == "public-healthcheck" {
		return app.CheckPublicReady(context.Background(), "http://127.0.0.1:3000/health/ready", os.Getenv("API_INTERNAL_TOKEN"))
	}
	if mode == "healthcheck" {
		client := http.Client{Timeout: 6 * time.Second}
		req, err := http.NewRequest(http.MethodGet, "http://127.0.0.1:8080/health/ready", nil)
		if err != nil {
			return err
		}
		req.Header.Set("Authorization", "Bearer "+os.Getenv("API_INTERNAL_TOKEN"))
		res, err := client.Do(req)
		if err != nil {
			return fmt.Errorf("API is unavailable")
		}
		defer res.Body.Close()
		if res.StatusCode != 200 {
			return fmt.Errorf("API is not ready")
		}
		return nil
	}
	ctx, cancel := context.WithTimeout(context.Background(), 270*time.Second)
	defer cancel()
	store, err := app.OpenStorage(ctx, os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	if err != nil {
		return fmt.Errorf("local storage configuration is unavailable")
	}
	defer store.DB.Close()
	switch mode {
	case "maintenance-lab-purged":
		return store.RecordLabPurge(ctx)
	case "snapshot-create":
		snapshotCtx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
		defer stop()
		return store.Snapshot(snapshotCtx, os.Stdout)
	case "snapshot-restore":
		snapshotCtx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
		defer stop()
		return store.RestoreSnapshot(snapshotCtx, os.Stdin, os.Stdout)
	case "quality":
		batchCtx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
		defer stop()
		return app.NewServer(store, os.Getenv("APP_ORIGIN"), os.Getenv("SPEECH_URL")).QualityCommand(batchCtx, os.Stdin, os.Stdout)
	case "prepare":
		return app.NewServer(store, os.Getenv("APP_ORIGIN"), os.Getenv("SPEECH_URL")).PreparationCommand(ctx, os.Stdin, os.Stdout)
	case "provider":
		return app.NewServer(store, os.Getenv("APP_ORIGIN"), os.Getenv("SPEECH_URL")).ProviderCommand(ctx, os.Stdin, os.Stdout)
	case "lab":
		return store.LabCommand(ctx, os.Stdin, os.Stdout)
	case "storage":
		return store.StorageCommand(ctx, os.Stdin, os.Stdout)
	case "migrate":
		return store.Migrate(ctx)
	case "media-init":
		return store.InitMedia(ctx)
	case "initialize":
		if err := store.Migrate(ctx); err != nil {
			return fmt.Errorf("MIGRATION_FAILED: inspect initialization logs and database availability")
		}
		if err := store.InitMedia(ctx); err != nil {
			return fmt.Errorf("MEDIA_INIT_FAILED: verify private bucket and storage readiness")
		}
		return nil
	case "serve":
	default:
		return fmt.Errorf("unknown command")
	}
	origin := os.Getenv("APP_ORIGIN")
	if err = app.ValidateOrigin(origin); err != nil {
		return err
	}
	server := &http.Server{Addr: ":8080", Handler: app.NewServer(store, origin, os.Getenv("SPEECH_URL")).Handler(), ReadHeaderTimeout: 5 * time.Second, ReadTimeout: app.OverallDeadline, WriteTimeout: app.OverallDeadline, IdleTimeout: 60 * time.Second, MaxHeaderBytes: 16 * 1024}
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

func modeErrorIsUnsafe(message string) bool {
	for _, prefix := range []string{"BACKUP_", "RESTORE_", "WORKSPACE_", "LOCAL_MAINTENANCE_", "MAINTENANCE_USAGE"} {
		if strings.HasPrefix(message, prefix) {
			return false
		}
	}
	return true
}

func main() {
	if err := run(); err != nil {
		message := err.Error()
		if !strings.Contains(message, "CONFIG_") && !strings.Contains(message, "MIGRATION_FAILED") && !strings.Contains(message, "MEDIA_INIT_FAILED") && modeErrorIsUnsafe(message) {
			message = "OPERATION_FAILED: check local prerequisites and configuration"
		}
		fmt.Fprintln(os.Stderr, message)
		os.Exit(1)
	}
}
