package app

import (
	"context"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestNativeSourceBrowserFixture(t *testing.T) {
	f := sourceFixture(t)
	remote := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Query().Get("cursor") == "second" {
			_, _ = io.WriteString(w, `{"items":[{"id":"b"}],"next":null,"done":true,"total":2}`)
		} else {
			_, _ = io.WriteString(w, `{"items":[{"id":"a"}],"next":"second","done":false,"total":2}`)
		}
	}))
	defer remote.Close()
	f.s.client = remote.Client()
	dir := os.Getenv("TANGERINE_SOURCE_EVIDENCE")
	if dir == "" {
		t.Fatal("evidence required")
	}
	listener, e := net.Listen("tcp", ":8080")
	sourceRequire(t, e)
	server := &http.Server{Handler: f.s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = server.Shutdown(ctx)
	}()
	var schema string
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT current_schema()").Scan(&schema))
	sourceRequire(t, os.WriteFile(filepath.Join(dir, "fixture.json"), sourceBytes(map[string]any{"schema": schema, "remote_endpoint": remote.URL}), 0600))
	deadline := time.After(600 * time.Second)
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-deadline:
			t.Fatal("browser deadline")
		case <-ticker.C:
			if _, e = os.Stat(filepath.Join(dir, "done")); e == nil {
				var calls int
				sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='provider-receipt'").Scan(&calls))
				sourceAssert(t, 0, calls)
				return
			}
		}
	}
}
