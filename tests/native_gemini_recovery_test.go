package app

import (
	"context"
	"encoding/json"
	"io"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
)

// A literal replay of the previously saved text/key response. It is a controlled
// HTTP dependency, never another hosted model qualification or linguistic gold.
func g23RecordedResponse(t *testing.T, index int, blueprint string) []byte {
	t.Helper()
	raw, e := os.ReadFile("/reference/dispatches.json")
	g23Require(t, e)
	var all []struct{ Response map[string]any }
	g23Require(t, json.Unmarshal(raw, &all))
	body := all[index].Response
	for _, step := range body["steps"].([]any) {
		s := step.(map[string]any)
		if s["type"] != "model_output" {
			continue
		}
		for _, part := range s["content"].([]any) {
			p := part.(map[string]any)
			if p["type"] != "text" {
				continue
			}
			var output map[string]any
			g23Require(t, json.Unmarshal([]byte(p["text"].(string)), &output))
			output["blueprint_id"] = blueprint
			p["text"] = string(g23JSON(output))
		}
	}
	return g23JSON(body)
}

func TestNativeGeminiBrowserRecovery(t *testing.T) {
	t.Setenv("GEMINI_API_KEY", "controlled-gemini-key")
	s, r := g23Setup(t)
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_GEMINI_EVIDENCE")
	old := http.DefaultTransport
	var mu sync.Mutex
	dispatches := []any{}
	http.DefaultTransport = g23Trip(func(req *http.Request) (*http.Response, error) {
		if req.URL.Hostname() != "generativelanguage.googleapis.com" {
			return old.RoundTrip(req)
		}
		raw, e := io.ReadAll(req.Body)
		if e != nil {
			return nil, e
		}
		mode, e := os.ReadFile(filepath.Join(dir, "provider-state"))
		if e != nil {
			return nil, e
		}
		var wire struct{ Input string }
		g23Require(t, json.Unmarshal(raw, &wire))
		phase := "mutation"
		index := 2
		var messages []struct{ Content string }
		g23Require(t, json.Unmarshal([]byte(wire.Input), &messages))
		for _, message := range messages {
			if !strings.HasPrefix(message.Content, "Complete stage input: ") {
				continue
			}
			var input struct{ Phase string }
			g23Require(t, json.Unmarshal([]byte(strings.TrimPrefix(message.Content, "Complete stage input: ")), &input))
			if input.Phase == "canonical_text" {
				phase, index = "canonical", 0
			}
		}
		status, body := 200, g23RecordedResponse(t, index, r.BlueprintID)
		if phase == "mutation" && strings.TrimSpace(string(mode)) != "recovered" {
			status, body = 403, []byte(`{"error":{"code":"permission_denied","message":"private provider diagnostic must not reach UI"}}`)
		}
		mu.Lock()
		dispatches = append(dispatches, map[string]any{"phase": phase, "status": status, "request": json.RawMessage(raw), "response": json.RawMessage(body), "origin": "controlled transport; no hosted dispatch"})
		g23Write(t, "dispatches.json", dispatches)
		mu.Unlock()
		return &http.Response{StatusCode: status, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(string(body)))}, nil
	})
	defer func() { http.DefaultTransport = old }()
	p, e := s.PrepareCanonical(ctx, r, uuid.NewString(), nil)
	g23Require(t, e)
	id := p["id"].(string)
	r.PreparationID = &id
	r.Attempt = 2
	failed, e := s.PrepareMutation(ctx, r, uuid.NewString(), nil)
	if e == nil {
		t.Fatal("expected controlled denial")
	}
	g23Write(t, "before.json", failed)
	g23Write(t, "fixture.json", map[string]any{"preparation_id": id, "origin": "controlled native failure/recovery; actual saved checkpoints and local speech"})
	listener, e := net.Listen("tcp", "0.0.0.0:8080")
	g23Require(t, e)
	api := &http.Server{Handler: s.Handler()}
	go func() { _ = api.Serve(listener) }()
	defer api.Close()
	g23Write(t, "ready.json", map[string]any{"preparation_id": id})
	deadline := time.Now().Add(60 * time.Minute)
	for {
		if _, e := os.Stat(filepath.Join(dir, "done")); e == nil {
			break
		}
		if time.Now().After(deadline) {
			t.Fatal("owned browser timeout")
		}
		time.Sleep(100 * time.Millisecond)
	}
	after, e := s.Store.Preparation(ctx, id)
	g23Require(t, e)
	if after["canonical_asset_id"] != p["canonical_asset_id"] || after["settings_asset_id"] != p["settings_asset_id"] || after["audio_asset_id"] == nil {
		t.Fatal("resume lost checkpoint or did not complete", after)
	}
	g23Write(t, "after.json", after)
	g23Dump(t, s, "")
}
