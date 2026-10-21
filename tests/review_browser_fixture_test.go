package app

import (
	"context"
	"github.com/google/uuid"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestNativeReviewBrowserFixture(t *testing.T) {
	f := reviewFixture(t, "supported")
	root := f.attempt
	second := f.start(t)
	f.attempt = second
	_, _, err := f.s.Store.WriteAnswer(context.Background(), second, uuid.NewString(), 0, answerPacket("Use opens.", "en"), true)
	requireListening(t, err)
	_, err = f.interpret(t, uuid.NewString())
	requireListening(t, err)
	f.attempt = root
	dir := os.Getenv("TANGERINE_INTERPRETATION_EVIDENCE")
	if dir == "" {
		t.Fatal("evidence required")
	}
	f.reviewPath = filepath.Join(dir, "review-mode")
	f.s.token = "listening-owned-token"
	listener, e := net.Listen("tcp", ":8080")
	requireListening(t, e)
	server := &http.Server{Handler: f.s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = server.Shutdown(ctx)
	}()
	var schema string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT current_schema()").Scan(&schema))
	requireListening(t, os.WriteFile(filepath.Join(dir, "fixture.json"), mustJSON(map[string]any{"case_id": f.id, "case_sha256": f.sha, "attempt_id": f.attempt, "second_attempt_id": second, "schema": schema}), 0600))
	deadline := time.After(600 * time.Second)
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-deadline:
			t.Fatal("browser deadline")
		case <-ticker.C:
			if _, e = os.Stat(filepath.Join(dir, "done")); e == nil {
				return
			}
		}
	}
}
