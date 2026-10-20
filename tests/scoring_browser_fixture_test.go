package app

import (
	"context"
	"encoding/json"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestNativeScoringBrowserFixture(t *testing.T) {
	f := scoringFixture(t, false)
	dir := os.Getenv("TANGERINE_INTERPRETATION_EVIDENCE")
	if dir == "" {
		t.Fatal("evidence required")
	}
	f.modePath = filepath.Join(dir, "mode")
	f.s.token = "listening-owned-token"
	listener, e := net.Listen("tcp", ":8080")
	requireListening(t, e)
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/test-model-counts" {
			_ = json.NewEncoder(w).Encode(map[string]any{"extractions": f.extracts.Load(), "mappings": f.maps.Load(), "feedback": f.feedbackCalls.Load()})
			return
		}
		f.s.Handler().ServeHTTP(w, r)
	})
	server := &http.Server{Handler: handler, ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = server.Shutdown(ctx)
	}()
	var schema string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT current_schema()").Scan(&schema))
	requireListening(t, os.WriteFile(filepath.Join(dir, "fixture.json"), mustJSON(map[string]any{"case_id": f.id, "case_sha256": f.sha, "schema": schema}), 0600))
	deadline := time.After(300 * time.Second)
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-deadline:
			t.Fatal("browser timeout")
		case <-ticker.C:
			if _, e = os.Stat(filepath.Join(dir, "done")); e == nil {
				return
			}
		}
	}
}
