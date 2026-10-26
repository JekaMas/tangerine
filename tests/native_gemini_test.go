package app

// I23: actual native owners with either an explicitly admitted Gemini Free
// transport or labelled controlled error packets. No provider substitution.
import (
	"bytes"
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
	"tangerine.local/api/internal/provider"
)

func g23JSON(v any) []byte { b, _ := json.MarshalIndent(v, "", "  "); return b }
func g23Require(t *testing.T, e error) {
	t.Helper()
	if e != nil {
		t.Fatal(e)
	}
}

type g23Trip func(*http.Request) (*http.Response, error)

func (f g23Trip) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }
func g23Write(t *testing.T, name string, v any) {
	t.Helper()
	g23Require(t, os.WriteFile(filepath.Join(os.Getenv("TANGERINE_GEMINI_EVIDENCE"), name), g23JSON(v), 0600))
}

func g23Setup(t *testing.T) (*Server, CanonicalPreparationRequest) {
	t.Helper()
	ctx := context.Background()
	s, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	g23Require(t, e)
	t.Cleanup(s.DB.Close)
	c, rev, e := s.Configuration(ctx)
	g23Require(t, e)
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	for k, v := range map[string]any{"id": "gemini-i23-free", "provider": "gemini_interactions", "model": "gemini-3.1-flash-lite", "endpoint": provider.GeminiEndpoint, "auth_method": "api_key", "billing_mode": "free_tier", "credential_ref": "GEMINI_API_KEY", "adapter_version": "gemini-interactions-v1", "context_budget_tokens": 1000000, "max_output_tokens": 12000, "temperature": 0.2, "reasoning_effort": nil, "stream": false, "structured_output": false} {
		p[k] = v
	}
	c["llm_profiles"] = []any{p}
	c["llm_profile"] = p["id"]
	for role := range c["stage_profiles"].(map[string]any) {
		c["stage_profiles"].(map[string]any)[role] = nil
	}
	c["speech_profile"] = "kokoro-local-en-v1"
	c["speech_profiles"] = []any{}
	c["mapping_audit_enabled"] = false
	c["llm_lab_capture_content"], c["llm_lab_trace_enabled"] = true, true
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	saved, _, e := s.PutConfiguration(ctx, g23JSON(c), uuid.NewString(), rev)
	g23Require(t, e)
	request := map[string]any{"exercise_request": map[string]any{"topic": "Planning a community garden", "speaker_count": 2, "text_length_words": 90, "english_level": "B1", "category_families": []any{"grammar"}, "mutation_count": 1, "audio_backend": "local"}}
	b, e := s.WriteBlueprint(ctx, g23JSON(request), uuid.NewString())
	g23Require(t, e)
	server := NewServer(s, "http://localhost:3000", os.Getenv("TANGERINE_SPEECH_TEST_URL"))
	return server, CanonicalPreparationRequest{BlueprintID: b["id"].(string), ConfigurationSHA: saved["configuration_sha256"].(string), Sources: []string{}, Attempt: 1}
}

// Collect native documents/assets even after a provider stop. This is an evidence
// export only, never another model call or a stored-data admission gate.
func g23Dump(t *testing.T, s *Server, prefix string) {
	t.Helper()
	ctx := context.Background()
	rows, e := s.Store.DB.Query(ctx, "SELECT id FROM document WHERE kind IN ('provider-receipt','llm-context-snapshot','effective-binding') ORDER BY created_at,id")
	g23Require(t, e)
	ids := []string{}
	for rows.Next() {
		var id string
		g23Require(t, rows.Scan(&id))
		ids = append(ids, id)
	}
	rows.Close()
	docs := []any{}
	assets := map[string]bool{}
	for _, id := range ids {
		d, e := s.Store.ReadDocument(ctx, id)
		g23Require(t, e)
		var v map[string]any
		g23Require(t, json.Unmarshal(d.Payload, &v))
		docs = append(docs, v)
		for k, x := range v {
			if strings.HasSuffix(k, "asset_id") {
				if id, ok := x.(string); ok {
					assets[id] = true
				}
			}
		}
	}
	g23Write(t, prefix+"documents.json", docs)
	dir := filepath.Join(os.Getenv("TANGERINE_GEMINI_EVIDENCE"), "assets")
	g23Require(t, os.MkdirAll(dir, 0700))
	for id := range assets {
		b, e := s.Store.ReadAsset(ctx, id)
		if e == nil {
			g23Require(t, os.WriteFile(filepath.Join(dir, id+".json"), b, 0600))
		}
	}
}

func g23Observe(t *testing.T) func() {
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
		req.Body = io.NopCloser(bytes.NewReader(raw))
		mu.Lock()
		index := len(dispatches)
		dispatches = append(dispatches, map[string]any{"index": index, "url": req.URL.String(), "request": json.RawMessage(raw), "credential_header_present": req.Header.Get("x-goog-api-key") != "", "authorization_header_present": req.Header.Get("Authorization") != ""})
		mu.Unlock()
		response, e := old.RoundTrip(req)
		mu.Lock()
		defer mu.Unlock()
		record := dispatches[index].(map[string]any)
		if e != nil {
			record["transport_error"] = e.Error()
		} else {
			body, readErr := io.ReadAll(response.Body)
			_ = response.Body.Close()
			response.Body = io.NopCloser(bytes.NewReader(body))
			record["http_status"] = response.StatusCode
			record["response"] = json.RawMessage(body)
			if readErr != nil {
				record["read_error"] = readErr.Error()
			}
		}
		g23Write(t, "dispatches.json", dispatches)
		return response, e
	})
	return func() { http.DefaultTransport = old }
}

func TestNativeGeminiFreeFlow(t *testing.T) {
	if os.Getenv("TANGERINE_GEMINI_LIVE") != "1" {
		t.Skip("explicit admitted Free project required")
	}
	s, r := g23Setup(t)
	defer g23Dump(t, s, "")
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_GEMINI_EVIDENCE")
	defer g23Observe(t)()
	// The unchanged ordinary coordinator uses the same production wire owner.
	p, e := s.GenerateExercise(ctx, r, uuid.NewString())
	g23Write(t, "preparation.json", p)
	if e != nil {
		code, detail := provider.SafeError(e)
		g23Write(t, "failure.json", map[string]any{"code": code, "provider_code": detail, "stage": "generation"})
		t.Fatal(e)
	}
	keyDoc, e := s.Store.ReadDocument(ctx, p["key_id"].(string))
	g23Require(t, e)
	var key map[string]any
	g23Require(t, json.Unmarshal(keyDoc.Payload, &key))
	g23Write(t, "key.json", key)
	if len(key["units"].([]any)) != 1 {
		t.Fatal("requested one mutation", key)
	}
	audio, e := s.Store.ReadAsset(ctx, p["audio_asset_id"].(string))
	g23Require(t, e)
	g23Require(t, os.WriteFile(filepath.Join(dir, "exercise.wav"), audio, 0600))
	var caseID, sha string
	g23Require(t, s.Store.DB.QueryRow(ctx, "SELECT case_version_id,case_sha256 FROM listening_case WHERE source_key_id=$1", p["key_id"]).Scan(&caseID, &sha))
	started, e := s.Store.StartAttempt(ctx, g23JSON(map[string]any{"case_version_id": caseID, "case_sha256": sha, "requested_language": "en"}), uuid.NewString())
	g23Require(t, e)
	attempt := started["attempt_id"].(string)
	g23Write(t, "fixture.json", map[string]any{"preparation_id": p["id"], "case_id": caseID, "key_id": p["key_id"], "audio_asset_id": p["audio_asset_id"], "attempt_id": attempt, "request": r, "text_provider": "gemini_interactions", "model": "gemini-3.1-flash-lite", "speech": "local_kokoro", "constructed_answer": true})
	g23Wait(t, s, attempt)
}

func g23Wait(t *testing.T, s *Server, attempt string) {
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_GEMINI_EVIDENCE")
	listener, e := net.Listen("tcp", ":8080")
	g23Require(t, e)
	api := &http.Server{Handler: s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = api.Serve(listener) }()
	defer api.Close()
	g23Write(t, "ready.json", map[string]any{"attempt_id": attempt, "port": 8080})
	deadline := time.Now().Add(90 * time.Minute)
	for {
		if _, e := os.Stat(filepath.Join(dir, "done")); e == nil {
			break
		}
		if time.Now().After(deadline) {
			t.Fatal("owned browser observation timeout")
		}
		time.Sleep(100 * time.Millisecond)
	}
	state, e := s.Store.interpretationState(ctx, attempt)
	g23Require(t, e)
	record, e := s.Store.Attempt(ctx, attempt)
	g23Require(t, e)
	result, e := s.Store.interpretationEnvelope(ctx, record, state)
	g23Require(t, e)
	g23Write(t, "attempt.json", record)
	g23Write(t, "result.json", result)
	if result["feedback_status"] != "complete" {
		t.Fatal("feedback incomplete", result)
	}
}

func g23Clean(blueprint string) []byte {
	v := map[string]any{"schema_version": "1.0.0", "blueprint_id": blueprint, "status": "candidate", "failure_reason": nil, "utterances": []any{map[string]any{"id": "u1", "speaker_id": "s1", "canonical_text": "The garden opens tomorrow.", "surface_text": "The garden opens tomorrow."}, map[string]any{"id": "u2", "speaker_id": "s2", "canonical_text": "I will bring seeds.", "surface_text": "I will bring seeds."}}, "planned_units": []any{}, "acoustic_edits": []any{}}
	return g23JSON(map[string]any{"id": "constructed-gemini-canonical", "status": "completed", "model": "gemini-3.1-flash-lite", "steps": []any{map[string]any{"type": "model_output", "content": []any{map[string]any{"type": "text", "text": string(g23JSON(v))}}}}, "usage": map[string]any{"total_input_tokens": 17, "total_output_tokens": 13}})
}

func TestNativeGeminiErrors(t *testing.T) {
	t.Setenv("GEMINI_API_KEY", "controlled-gemini-key")
	for _, tc := range []struct {
		name       string
		status     int
		body, code string
		calls      int
	}{{"quota", 429, `{"error":{"status":"RESOURCE_EXHAUSTED","message":"private quota diagnostic"}}`, "LOCAL_BUDGET_EXCEEDED", 1}, {"denied", 403, `{"error":{"status":"PERMISSION_DENIED","message":"private denial diagnostic"}}`, "PROVIDER_FAILURE", 1}, {"credentials", 401, `{"error":{"status":"UNAUTHENTICATED"}}`, "MISSING_CREDENTIALS", 1}, {"unavailable", 503, `{"error":{"status":"UNAVAILABLE","message":"private outage diagnostic"}}`, "PROVIDER_FAILURE", 2}} {
		t.Run(tc.name, func(t *testing.T) {
			s, r := g23Setup(t)
			calls := 0
			phase := "canonical"
			client := &http.Client{Transport: g23Trip(func(req *http.Request) (*http.Response, error) {
				if req.URL.String() != provider.GeminiEndpoint || req.Header.Get("x-goog-api-key") != "controlled-gemini-key" {
					t.Fatal("substitution or credential transport changed")
				}
				status, body := 200, string(g23Clean(r.BlueprintID))
				if phase == "mutation" {
					calls++
					status, body = tc.status, tc.body
				}
				return &http.Response{StatusCode: status, Header: http.Header{"Content-Type": []string{"application/json"}}, Body: io.NopCloser(strings.NewReader(body))}, nil
			})}
			p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), client)
			g23Require(t, e)
			id := p["id"].(string)
			canonical := p["canonical_asset_id"]
			if canonical == nil {
				t.Fatal("missing actual canonical checkpoint", p)
			}
			r.PreparationID = &id
			r.Attempt = 2
			phase = "mutation"
			failed, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
			code, _ := provider.SafeError(e)
			if code != tc.code || calls != tc.calls {
				t.Fatalf("wrong error/retry: %s calls=%d, %v", code, calls, e)
			}
			if failed["canonical_asset_id"] != canonical || failed["settings_asset_id"] != p["settings_asset_id"] || failed["audio_asset_id"] != nil || failed["phase_states"].(map[string]any)["canonical_text"] != "complete" {
				t.Fatal("saved checkpoint lost or falsely completed", failed)
			}
			g23Write(t, "error-"+tc.name+".json", map[string]any{"code": code, "calls": calls, "before": p, "after": failed, "origin": "controlled-error-transport"})
			g23Dump(t, s, "error-"+tc.name+"-")
		})
	}
}

func TestNativeGeminiUnavailableRecovery(t *testing.T) {
	t.Setenv("GEMINI_API_KEY", "controlled-gemini-key")
	s, r := g23Setup(t)
	calls := 0
	client := &http.Client{Transport: g23Trip(func(req *http.Request) (*http.Response, error) {
		calls++
		status, body := 503, `{"error":{"status":"UNAVAILABLE"}}`
		if calls == 2 {
			status, body = 200, string(g23Clean(r.BlueprintID))
		}
		return &http.Response{StatusCode: status, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(body))}, nil
	})}
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), client)
	g23Require(t, e)
	if calls != 2 || p["phase_states"].(map[string]any)["canonical_text"] != "complete" {
		t.Fatal("transient retry did not recover", calls, p)
	}
	g23Write(t, "recovery.json", map[string]any{"calls": calls, "preparation": p, "origin": "controlled-transient-transport"})
	g23Dump(t, s, "recovery-")
}

func TestNativeGeminiRepairContext(t *testing.T) {
	t.Setenv("GEMINI_API_KEY", "controlled-gemini-key")
	s, r := g23Setup(t)
	calls := 0
	client := &http.Client{Transport: g23Trip(func(req *http.Request) (*http.Response, error) {
		calls++
		status, body := 200, string(g23Clean(r.BlueprintID))
		if calls == 1 {
			body = `{"status":"completed","steps":[{"type":"model_output","content":[{"type":"text","text":"broken"}]}]}`
		}
		if calls == 2 {
			status, body = 503, `{"error":{"status":"UNAVAILABLE"}}`
		}
		return &http.Response{StatusCode: status, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(body))}, nil
	})}
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), client)
	g23Require(t, e)
	if calls != 3 || p["phase_states"].(map[string]any)["canonical_text"] != "complete" {
		t.Fatal("native repair/retry failed", calls, p)
	}
	rows, e := s.Store.DB.Query(context.Background(), "SELECT payload FROM document WHERE kind='llm-context-snapshot' ORDER BY created_at DESC LIMIT 2")
	g23Require(t, e)
	defer rows.Close()
	observations := []any{}
	for rows.Next() {
		var raw []byte
		g23Require(t, rows.Scan(&raw))
		var snapshot map[string]any
		g23Require(t, json.Unmarshal(raw, &snapshot))
		found := false
		for _, c := range snapshot["components"].([]any) {
			part := c.(map[string]any)
			if part["kind"] == "candidate" {
				data, e := s.Store.ReadAsset(context.Background(), part["asset_id"].(string))
				g23Require(t, e)
				var content map[string]any
				g23Require(t, json.Unmarshal(data, &content))
				if content["raw_visible_output"] != "broken" || content["repair_instruction"] == nil {
					t.Fatal("repair context was not the actual message", content)
				}
				found = true
			}
		}
		if !found {
			t.Fatal("repair or its transport retry lost the native context", snapshot)
		}
		observations = append(observations, snapshot)
	}
	if len(observations) != 2 {
		t.Fatal("missing native repair snapshots")
	}
	g23Write(t, "repair-context.json", map[string]any{"calls": calls, "snapshots": observations, "origin": "controlled-repair-and-retry"})
	g23Dump(t, s, "repair-context-")
}

// A new attempt freezes the repaired shipped prompt. The saved generation,
// mutation key and audio are reused; existing attempt history is not rewritten.
func TestNativeGeminiAnswerRepair(t *testing.T) {
	if os.Getenv("TANGERINE_GEMINI_LIVE") != "1" {
		t.Skip("explicit admitted Free project required")
	}
	ctx := context.Background()
	store, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	g23Require(t, e)
	defer store.DB.Close()
	s := NewServer(store, "http://localhost:3000", os.Getenv("TANGERINE_SPEECH_TEST_URL"))
	defer g23Dump(t, s, "")
	defer g23Observe(t)()
	raw, e := os.ReadFile("/prior/fixture.json")
	g23Require(t, e)
	var fixture map[string]any
	g23Require(t, json.Unmarshal(raw, &fixture))
	var sha string
	g23Require(t, store.DB.QueryRow(ctx, "SELECT case_sha256 FROM listening_case WHERE case_version_id=$1", fixture["case_id"]).Scan(&sha))
	started, e := store.StartAttempt(ctx, g23JSON(map[string]any{"case_version_id": fixture["case_id"], "case_sha256": sha, "requested_language": "en"}), uuid.NewString())
	g23Require(t, e)
	fixture["superseded_attempt_id"], fixture["attempt_id"] = fixture["attempt_id"], started["attempt_id"]
	fixture["reuse_reason"] = "Repaired extraction instruction; same generated case/key/audio and fixed developer answer. Original uncertain result remains saved."
	g23Write(t, "fixture.json", fixture)
	g23Wait(t, s, fixture["attempt_id"].(string))
}

func TestNativeGeminiResume(t *testing.T) {
	if os.Getenv("TANGERINE_GEMINI_LIVE") != "1" {
		t.Skip("explicit admitted Free project required")
	}
	ctx := context.Background()
	store, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	g23Require(t, e)
	defer store.DB.Close()
	s := NewServer(store, "http://localhost:3000", os.Getenv("TANGERINE_SPEECH_TEST_URL"))
	defer g23Dump(t, s, "")
	defer g23Observe(t)()
	raw, e := os.ReadFile("/prior/fixture.json")
	g23Require(t, e)
	var fixture map[string]any
	g23Require(t, json.Unmarshal(raw, &fixture))
	fixture["resume_reason"] = "Provider-neutral repair context recorder fixed; resume the interrupted attempt using its frozen prompt/profile and unchanged answer."
	g23Write(t, "fixture.json", fixture)
	g23Wait(t, s, fixture["attempt_id"].(string))
}
