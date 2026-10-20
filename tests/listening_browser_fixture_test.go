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

func TestNativeListeningBrowserFixture(t *testing.T) {
	f := listeningCase(t)
	dir := os.Getenv("TANGERINE_LISTENING_EVIDENCE")
	if dir == "" {
		t.Fatal("private evidence path required")
	}
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
	raw, _ := json.Marshal(map[string]any{"case_id": f.id, "case_sha256": f.sha, "audio_sha256": f.audioSHA})
	requireListening(t, os.WriteFile(filepath.Join(dir, "fixture.json"), raw, 0600))
	deadline := time.After(300 * time.Second)
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-deadline:
			t.Fatal("browser did not finish")
		case <-ticker.C:
			if _, e = os.Stat(filepath.Join(dir, "done")); e == nil {
				return
			}
		}
	}
}
