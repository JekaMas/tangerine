package app

import (
	"context"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestNativeQualityBrowserFixture(t *testing.T) {
	s, _ := qualityGenerationServer(t, false)
	dir := os.Getenv("TANGERINE_QUALITY_EVIDENCE")
	if dir == "" {
		t.Fatal("evidence required")
	}
	listener, e := net.Listen("tcp", ":8080")
	requireListening(t, e)
	server := &http.Server{Handler: s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer server.Close()
	var schema string
	requireListening(t, s.Store.DB.QueryRow(context.Background(), "SELECT current_schema()").Scan(&schema))
	submission := qualitySimpleSubmission(t, s, "generation_pipeline", qualityGenerationRequest())
	requireListening(t, os.WriteFile(filepath.Join(dir, "fixture.json"), mustJSON(map[string]any{"schema": schema, "experiment": submission}), 0600))
	deadline := time.After(600 * time.Second)
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-deadline:
			t.Fatal("browser did not finish")
		case <-ticker.C:
			if _, e := os.Stat(filepath.Join(dir, "done")); e == nil {
				return
			}
		}
	}
}
