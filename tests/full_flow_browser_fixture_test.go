package app

// I29 serves actual native owners before any generation. CUA drives the real UI.
// Only the database/media and constructed developer answer belong to this test;
// Gemini Free and installed local Kokoro replies are never substituted.
import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"testing"
	"time"
)

func i29Observe(t *testing.T) func() {
	old := http.DefaultTransport
	var mu sync.Mutex
	dispatches := []any{}
	if raw, err := os.ReadFile(filepath.Join(os.Getenv("TANGERINE_GEMINI_EVIDENCE"), "dispatches.json")); err == nil {
		g23Require(t, json.Unmarshal(raw, &dispatches))
	}
	http.DefaultTransport = g23Trip(func(req *http.Request) (*http.Response, error) {
		local := req.URL.Hostname() == "ollama" && req.URL.Path == "/v1/responses"
		model := req.URL.Hostname() == "generativelanguage.googleapis.com" || local
		speech := req.URL.Hostname() == "speech" && req.Method == http.MethodPost
		if !model && !speech {
			return old.RoundTrip(req)
		}
		raw, e := io.ReadAll(req.Body)
		if e != nil {
			return nil, e
		}
		req.Body = io.NopCloser(bytes.NewReader(raw))
		mu.Lock()
		index := len(dispatches)
		row := map[string]any{"index": index, "url": req.URL.String(), "request": json.RawMessage(raw), "started_at": time.Now().UTC().Format(time.RFC3339Nano), "credential_header_present": req.Header.Get("x-goog-api-key") != "", "speech_internal_header_present": speech && req.Header.Get("Authorization") != "", "kind": "speech_worker"}
		row["http_host"] = req.Host
		if model {
			row["kind"] = "gemini_free"
			if local {
				row["kind"] = "local_responses"
			}
		}
		dispatches = append(dispatches, row)
		g23Write(t, "dispatches.json", dispatches)
		mu.Unlock()
		response, e := old.RoundTrip(req)
		mu.Lock()
		defer mu.Unlock()
		row["finished_at"] = time.Now().UTC().Format(time.RFC3339Nano)
		if e != nil {
			row["transport_error"] = e.Error()
		} else {
			body, readErr := io.ReadAll(response.Body)
			_ = response.Body.Close()
			response.Body = io.NopCloser(bytes.NewReader(body))
			row["http_status"] = response.StatusCode
			if json.Valid(body) {
				row["response"] = json.RawMessage(body)
			} else {
				row["response_text"] = string(body)
			}
			if readErr != nil {
				row["read_error"] = readErr.Error()
			}
		}
		g23Write(t, "dispatches.json", dispatches)
		return response, e
	})
	return func() { http.DefaultTransport = old }
}

func i29IDs(t *testing.T, s *Storage, kind string) []string {
	t.Helper()
	rows, e := s.DB.Query(context.Background(), "SELECT id FROM entity_head WHERE kind=$1 ORDER BY id", kind)
	g23Require(t, e)
	defer rows.Close()
	ids := []string{}
	for rows.Next() {
		var id string
		g23Require(t, rows.Scan(&id))
		ids = append(ids, id)
	}
	g23Require(t, rows.Err())
	return ids
}

// Explicit development snapshot only. It reads accepted native data and does
// not invoke a model, recalculate a score or requalify a stored record.
func i29Snapshot(t *testing.T, s *Server, checkpoint string) {
	t.Helper()
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_GEMINI_EVIDENCE")
	for _, name := range []string{"preparations", "keys", "attempts", "assets", "snapshots"} {
		g23Require(t, os.MkdirAll(filepath.Join(dir, name), 0700))
	}
	preparations := i29IDs(t, s.Store, "preparation-state")
	attempts := i29IDs(t, s.Store, "attempt")
	for _, id := range preparations {
		p, e := s.Store.Preparation(ctx, id)
		g23Require(t, e)
		g23Write(t, "preparations/"+id+".json", p)
		for _, field := range []string{"settings_asset_id", "canonical_asset_id", "candidate_asset_id", "mutated_asset_id", "mutation_manifest_asset_id", "render_plan_asset_id", "render_progress_asset_id", "audio_asset_id"} {
			asset, ok := p[field].(string)
			if !ok || asset == "" {
				continue
			}
			body, e := s.Store.ReadAsset(ctx, asset)
			g23Require(t, e)
			ext := ".json"
			if field == "audio_asset_id" {
				ext = ".wav"
			}
			g23Require(t, os.WriteFile(filepath.Join(dir, "assets", asset+ext), body, 0600))
		}
		if key, ok := p["key_id"].(string); ok && key != "" {
			doc, e := s.Store.ReadDocument(ctx, key)
			g23Require(t, e)
			g23Require(t, os.WriteFile(filepath.Join(dir, "keys", id+".json"), doc.Payload, 0600))
		}
	}
	for _, id := range attempts {
		record, e := s.Store.Attempt(ctx, id)
		g23Require(t, e)
		g23Write(t, "attempts/"+id+".json", record)
		state, e := s.Store.interpretationState(ctx, id)
		if e == nil {
			value, e := s.Store.interpretationEnvelope(ctx, record, state)
			g23Require(t, e)
			g23Write(t, "attempts/"+id+"-result.json", value)
		}
	}
	rows, e := s.Store.DB.Query(ctx, "SELECT case_version_id,source_key_id,case_sha256 FROM listening_case ORDER BY case_version_id")
	g23Require(t, e)
	relations := []any{}
	for rows.Next() {
		var id, key, digest string
		g23Require(t, rows.Scan(&id, &key, &digest))
		relations = append(relations, map[string]any{"case_version_id": id, "source_key_id": key, "case_sha256": digest})
	}
	g23Require(t, rows.Err())
	rows.Close()
	g23Write(t, "native-relationships.json", relations)
	g23Dump(t, s, "")
	snapshot := map[string]any{"checkpoint": checkpoint, "preparation_ids": preparations, "attempt_ids": attempts, "recorded_at": time.Now().UTC().Format(time.RFC3339Nano)}
	g23Write(t, "snapshot.json", snapshot)
	g23Write(t, "snapshots/"+time.Now().UTC().Format("20060102T150405.000000000")+".json", snapshot)
}

func TestNativeFullFlowBrowserFixture(t *testing.T) {
	if os.Getenv("TANGERINE_GEMINI_LIVE") != "1" {
		t.Fatal("The actual selected Free project must be explicitly available")
	}
	var s *Server
	if os.Getenv("TANGERINE_I29_RESUME") == "1" {
		store, err := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
		g23Require(t, err)
		t.Cleanup(store.DB.Close)
		s = NewServer(store, "http://localhost:3000", os.Getenv("TANGERINE_SPEECH_TEST_URL"))
	} else {
		s, _ = g23Setup(t)
	}
	defer i29Observe(t)()
	listener, e := net.Listen("tcp", ":8080")
	g23Require(t, e)
	server := &http.Server{Handler: s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer server.Close()
	dir := os.Getenv("TANGERINE_GEMINI_EVIDENCE")
	g23Write(t, "ready.json", map[string]any{"model": "gemini-3.1-flash-lite", "billing": "Free; project billing unlinked", "speech": "installed local Kokoro", "generated_exercises": len(i29IDs(t, s.Store, "preparation-state")), "resumed": os.Getenv("TANGERINE_I29_RESUME") == "1", "recorded_at": time.Now().UTC().Format(time.RFC3339Nano), "origin": "actual native workspace; CUA drives all user actions"})
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	deadline := time.After(3 * time.Hour)
	checkpoint := ""
	for {
		select {
		case <-deadline:
			t.Fatal("owned UI observation deadline")
		case <-ticker.C:
			if raw, e := os.ReadFile(filepath.Join(dir, "capture-request")); e == nil && string(raw) != checkpoint {
				checkpoint = string(raw)
				i29Snapshot(t, s, checkpoint)
			}
			if _, e := os.Stat(filepath.Join(dir, "done")); e == nil {
				i29Snapshot(t, s, "final")
				return
			}
		}
	}
}
