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

// Browser fixture owns only its disposable schema, records and fault switches.
// All import/status/progress/row responses come from the actual HTTP/storage owners.
func TestSourceCompletionBrowserFixture(t *testing.T) {
	dir := os.Getenv("TANGERINE_SOURCE_EVIDENCE")
	if dir == "" {
		t.Fatal("evidence directory required")
	}
	f := sourceFixture(t)
	f.bea(t)
	first := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), first.Report.ID))
	older := f.release
	second := &sourceNative{s: f.s}
	second.upload(t, "new/train.m2", "S We made a decision .\n\n")
	second.register(t, "FCE-2.1", "partial_export")
	last := second.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), last.Report.ID))
	var schema string
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT current_schema()").Scan(&schema))
	sourceRequire(t, os.WriteFile(filepath.Join(dir, "fixture.json"), sourceBytes(map[string]any{
		"schema": schema, "older_release": older, "newer_release": second.release,
		"older_import": first.Report, "newer_import": last.Report,
		"origin": "constructed records through real API/PostgreSQL/MinIO; no corpus or model qualification",
	}), 0600))
	listener, e := net.Listen("tcp", ":8080")
	sourceRequire(t, e)
	server := &http.Server{Handler: f.s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer server.Close()
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	deadline := time.After(45 * time.Minute)
	for {
		select {
		case <-deadline:
			t.Fatal("test-owned browser fixture deadline")
		case <-ticker.C:
			if _, e := os.Stat(filepath.Join(dir, "done")); e != nil {
				continue
			}
			var calls int
			sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='provider-receipt'").Scan(&calls))
			sourceAssert(t, 0, calls)
			sourceRequire(t, os.WriteFile(filepath.Join(dir, "native-final.json"), sourceBytes(map[string]any{"provider_receipts": calls, "source_ids": 11}), 0600))
			return
		}
	}
}
