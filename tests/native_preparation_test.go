package app

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"testing"
	"time"
)

// Real PostgreSQL/MinIO and production preparation/provider owners. The HTTP
// model endpoint is a controlled constructed fixture, never hosted AI evidence.
func preparationNative(t *testing.T) *Storage {
	t.Helper()
	s, e := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(s.DB.Close)
	return s
}

type preparationTrip func(*http.Request) (*http.Response, error)

func (f preparationTrip) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }
func prepareNativeFixture(t *testing.T, response string, status int) (*Server, CanonicalPreparationRequest, *http.Client, *int) {
	return prepareNativeFixtureRequest(t, response, status, nil)
}
func prepareNativeFixtureRequest(t *testing.T, response string, status int, configure func(map[string]any)) (*Server, CanonicalPreparationRequest, *http.Client, *int) {

	t.Helper()
	store := preparationNative(t)
	ctx := context.Background()
	c, rev, e := store.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	p["provider"] = "openai"
	p["model"] = "constructed-clean-text"
	p["endpoint"] = "https://api.openai.com/v1/responses"
	p["auth_method"] = "api_key"
	p["billing_mode"] = "free_tier"
	p["credential_ref"] = "OPENAI_API_KEY"
	p["stream"] = false
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	raw, _ := json.Marshal(c)
	saved, _, e := store.PutConfiguration(ctx, raw, uuid.NewString(), rev)
	if e != nil {
		t.Fatal(e)
	}
	request := map[string]any{"exercise_request": map[string]any{"topic": "Café opening", "speaker_count": 1, "text_length_words": 50}}
	if configure != nil {
		configure(request)
	}
	requestBytes, _ := json.Marshal(request)
	b, e := store.WriteBlueprint(ctx, requestBytes, uuid.NewString())
	if e != nil {
		t.Fatal(e)
	}
	failFirst := response == "fail-once"
	if failFirst {
		response = ""
	}
	candidate := map[string]any{"schema_version": "1.0.0", "blueprint_id": b["id"], "status": "candidate", "failure_reason": nil, "utterances": []any{map[string]any{"id": "u1", "speaker_id": "s1", "canonical_text": "The café opens tomorrow.", "surface_text": "The café opens tomorrow."}}, "planned_units": []any{}, "acoustic_edits": []any{}}
	raw, _ = json.Marshal(candidate)
	if response == "" {
		encoded, _ := json.Marshal(string(raw))
		response = `{"object":"response","id":"fixture-response","status":"completed","model":"constructed-clean-text","output":[{"type":"message","content":[{"type":"output_text","text":` + string(encoded) + `}]}]}`
	}
	n := 0
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		n++
		wire, _ := io.ReadAll(r.Body)
		if !strings.Contains(string(wire), "Café opening") || !strings.Contains(string(wire), "canonical_text") {
			t.Error("incomplete context", string(wire))
		}
		w.Header().Set("Content-Type", "application/json")
		if failFirst && n == 1 {
			w.WriteHeader(429)
			_, _ = io.WriteString(w, `{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}`)
			return
		}
		w.WriteHeader(status)
		_, _ = io.WriteString(w, response)
	}))
	t.Cleanup(target.Close)
	endpoint, _ := url.Parse(target.URL)
	client := &http.Client{Transport: preparationTrip(func(req *http.Request) (*http.Response, error) {
		clone := req.Clone(req.Context())
		u := *req.URL
		u.Scheme = endpoint.Scheme
		u.Host = endpoint.Host
		clone.URL = &u
		return http.DefaultTransport.RoundTrip(clone)
	})}
	t.Setenv("OPENAI_API_KEY", "CONSTRUCTED_NATIVE_CREDENTIAL")
	s := NewServer(store, "http://localhost:3000", "")
	return s, CanonicalPreparationRequest{BlueprintID: b["id"].(string), ConfigurationSHA: saved["configuration_sha256"].(string), Sources: []string{}, Attempt: 1}, client, &n
}
func saveNativePreparationEvidence(t *testing.T, s *Server, p map[string]any) {
	t.Helper()
	root := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	if root == "" {
		return
	}
	dir := filepath.Join(root, t.Name())
	if e := os.MkdirAll(dir, 0700); e != nil {
		t.Fatal(e)
	}
	write := func(name string, raw []byte) {
		t.Helper()
		if e := os.WriteFile(filepath.Join(dir, name), raw, 0600); e != nil {
			t.Fatal(e)
		}
	}
	raw, _ := json.MarshalIndent(map[string]any{"origin": "constructed_remote_protocol_with_native_preparation_storage", "preparation": p}, "", "  ")
	write("state.json", raw)
	assets := map[string]bool{}
	var collect func(any)
	collect = func(v any) {
		switch x := v.(type) {
		case map[string]any:
			for k, v := range x {
				if strings.HasSuffix(k, "asset_id") {
					if id, ok := v.(string); ok {
						assets[id] = true
					}
				}
				collect(v)
			}
		case []any:
			for _, v := range x {
				collect(v)
			}
		}
	}
	collect(p)
	documents := []SavedDocument{}
	for _, parent := range p["operation_ids"].([]any) {
		var child string
		if e := s.Store.DB.QueryRow(context.Background(), "SELECT child.id FROM operation parent JOIN operation child ON child.idempotency_key=parent.idempotency_key AND child.operation_name='canonical_text' WHERE parent.id=$1", parent).Scan(&child); e != nil {
			continue
		}
		rows, e := s.Store.DB.Query(context.Background(), "SELECT id FROM document WHERE (kind IN ('provider-receipt','llm-context-snapshot') AND payload->>'operation_id'=$1) OR id=(SELECT input_document_id FROM operation WHERE id=$1)", child)
		if e != nil {
			t.Fatal(e)
		}
		ids := []string{}
		for rows.Next() {
			var id string
			if e = rows.Scan(&id); e != nil {
				t.Fatal(e)
			}
			ids = append(ids, id)
		}
		rows.Close()
		for _, id := range ids {
			d, e := s.Store.ReadDocument(context.Background(), id)
			if e != nil {
				t.Fatal(e)
			}
			documents = append(documents, d)
			var v any
			_ = json.Unmarshal(d.Payload, &v)
			collect(v)
		}
	}
	raw, _ = json.MarshalIndent(documents, "", "  ")
	write("native-documents.json", raw)
	// Settings reference their exact shipped registries. Context snapshots reference
	// each actual model-visible part. Retain both recursively before fixture teardown.
	visited := map[string]bool{}
	for len(assets) > 0 {
		batch := assets
		assets = map[string]bool{}
		for id := range batch {
			if visited[id] {
				continue
			}
			visited[id] = true
			b, e := s.Store.ReadAsset(context.Background(), id)
			if e != nil {
				t.Fatal(e)
			}
			write(id+".bytes", b)
			var v any
			if json.Unmarshal(b, &v) == nil {
				collect(v)
			}
		}
	}
}

func TestNativePreparationCheckpointPositive(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	if *n != 1 || p["phase_states"].(map[string]any)["canonical_text"] != "complete" || p["phase_states"].(map[string]any)["mutation"] != "not_started" || p["audio_asset_id"] != nil || p["active_operation_id"] != nil {
		t.Fatal(p, *n)
	}
	raw, e := s.Store.ReadAsset(context.Background(), p["canonical_asset_id"].(string))
	if e != nil || !strings.Contains(string(raw), "The café opens tomorrow.") {
		t.Fatal(e, string(raw))
	}
	var count int
	e = s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM exercise_catalog").Scan(&count)
	if e != nil || count != 0 {
		t.Fatal("canonical entered playable library", count, e)
	}
	var countWords int
	if e = s.Store.DB.QueryRow(context.Background(), "SELECT (event_payload->>'canonical_word_count')::int FROM audit_event WHERE action='preparation.canonical.completed' AND event_payload->>'preparation_id'=$1", p["id"]).Scan(&countWords); e != nil || countWords != 4 {
		t.Fatal("missing exact generated count", e, countWords)
	}

	saveNativePreparationEvidence(t, s, p)
}
func TestNativePreparationRestartPositive(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	other := preparationNative(t)
	got, e := other.Preparation(context.Background(), p["id"].(string))
	if e != nil || got["canonical_sha256"] != p["canonical_sha256"] || *n != 1 {
		t.Fatal(got, e, *n)
	}
	rows, e := other.Preparations(context.Background(), 100, "")
	if e != nil || len(rows["items"].([]map[string]any)) == 0 {
		t.Fatal(e)
	}
	saveNativePreparationEvidence(t, s, got)
}
func TestNativePreparationQuotaNegative(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, `{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}`, 429)
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c)
	if e == nil || *n != 1 || p["canonical_asset_id"] != nil {
		t.Fatal(e, p, *n)
	}
	saved, e := s.Store.Preparation(context.Background(), p["id"].(string))
	if e != nil || saved["phase_states"].(map[string]any)["canonical_text"] != "failed" || saved["settings_asset_id"] == nil {
		t.Fatal(e, saved)
	}
	var receipt bool
	if e = s.Store.DB.QueryRow(context.Background(), "SELECT state='failed' AND error_document_id IS NOT NULL AND result_document_id IS NOT NULL FROM operation WHERE id=$1", saved["original_operation_id"]).Scan(&receipt); e != nil || !receipt {
		t.Fatal("failure/head transaction incomplete", e)
	}
	saveNativePreparationEvidence(t, s, saved)
}
func TestNativePreparationFreezeFailureNegative(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	s.Store.Bucket = "missing"
	_, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c)
	if e == nil || *n != 0 {
		t.Fatal(e, *n)
	}
}

func TestNativePreparationReplayPositive(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	key := uuid.NewString()
	p, e := s.PrepareCanonical(context.Background(), r, key, c)
	if e != nil {
		t.Fatal(e)
	}
	again, e := s.PrepareCanonical(context.Background(), r, key, c)
	if e != nil || *n != 1 || again["canonical_asset_id"] != p["canonical_asset_id"] {
		t.Fatal(e, *n)
	}
	saveNativePreparationEvidence(t, s, again)
}
func TestNativePreparationSavedSettingsPositive(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	config, rev, e := s.Store.Configuration(context.Background())
	if e != nil {
		t.Fatal(e)
	}
	config["llm_profiles"].([]any)[0].(map[string]any)["model"] = "different-current-model"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(config, k)
	}
	raw, _ := json.Marshal(config)
	if _, _, e = s.Store.PutConfiguration(context.Background(), raw, uuid.NewString(), rev); e != nil {
		t.Fatal(e)
	}
	id := p["id"].(string)
	r.PreparationID = &id
	r.Attempt = 2
	again, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c)
	if e != nil || *n != 1 || again["settings_sha256"] != p["settings_sha256"] {
		t.Fatal(e, *n)
	}
	saveNativePreparationEvidence(t, s, again)
}
func TestNativePreparationRequestConflictNegative(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	key := uuid.NewString()
	if _, e := s.PrepareCanonical(context.Background(), r, key, c); e != nil {
		t.Fatal(e)
	}
	r.Attempt = 2
	if _, e := s.PrepareCanonical(context.Background(), r, key, c); !errors.Is(e, ErrConflict) || *n != 1 {
		t.Fatal(e, *n)
	}
}
func TestNativePreparationResumeSettingsNegative(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	id := p["id"].(string)
	r.PreparationID = &id
	r.ConfigurationSHA = strings.Repeat("a", 64)
	if _, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c); !errors.Is(e, ErrConflict) || *n != 1 {
		t.Fatal(e, *n)
	}
}

func runningNativePreparation(t *testing.T) (*Server, map[string]any, Operation) {
	t.Helper()
	s, r, _, _ := prepareNativeFixture(t, "", 200)
	ctx := context.Background()
	b, e := s.Store.Blueprint(ctx, r.BlueprintID)
	if e != nil {
		t.Fatal(e)
	}
	config, _, e := s.Store.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	op, e := s.Store.ReserveOperation(ctx, OperationRequest{Name: "canonical_prepare", Key: uuid.NewString(), Path: "/prepare", Body: json.RawMessage(`{}`)})
	if e != nil {
		t.Fatal(e)
	}
	if _, e = s.Store.DB.Exec(ctx, "UPDATE operation SET state='running' WHERE id=$1", op.ID); e != nil {
		t.Fatal(e)
	}
	p, e := s.freezePreparation(ctx, b, config, lab.Shipped(), op)
	if e != nil {
		t.Fatal(e)
	}
	return s, p, op
}
func TestNativePreparationTakeoverPositive(t *testing.T) {
	s, p, op := runningNativePreparation(t)
	ctx := context.Background()
	_, e := s.Store.DB.Exec(ctx, "UPDATE operation SET started_at=clock_timestamp()-interval '271 seconds' WHERE id=$1", op.ID)
	if e != nil {
		t.Fatal(e)
	}
	fresh, e := s.Store.ReserveOperation(ctx, OperationRequest{Name: "canonical_prepare", Key: uuid.NewString(), Path: "/prepare", Body: json.RawMessage(`{}`)})
	if e != nil {
		t.Fatal(e)
	}
	_, e = s.Store.DB.Exec(ctx, "UPDATE operation SET state='running' WHERE id=$1", fresh.ID)
	if e != nil {
		t.Fatal(e)
	}
	if e = s.Store.takePreparation(ctx, p, fresh.ID); e != nil {
		t.Fatal(e)
	}
	got, e := s.Store.Preparation(ctx, p["id"].(string))
	if e != nil || got["revision"] != float64(1) || got["active_operation_id"] != fresh.ID || len(got["operation_ids"].([]any)) != 2 {
		t.Fatal(got, e)
	}
	saveNativePreparationEvidence(t, s, got)
}
func TestNativePreparationReadOnlyPositive(t *testing.T) {
	s, p, _ := runningNativePreparation(t)
	before := p["revision"]
	got, e := s.Store.Preparation(context.Background(), p["id"].(string))
	if e != nil || got["revision"] != before {
		t.Fatal(e)
	}
	b, e := s.Store.ReadAsset(context.Background(), got["settings_asset_id"].(string))
	if e != nil || !strings.Contains(string(b), "constructed-clean-text") || strings.Contains(string(b), "CONSTRUCTED_NATIVE_CREDENTIAL") {
		t.Fatal(e, "frozen settings missing or credential retained")
	}
	saveNativePreparationEvidence(t, s, got)

	time.Sleep(time.Millisecond)
}
func TestNativePreparationLateCheckpointNegative(t *testing.T) {
	s, p, op := runningNativePreparation(t)
	_, e := s.Store.DB.Exec(context.Background(), "UPDATE operation SET started_at=clock_timestamp()-interval '271 seconds' WHERE id=$1", op.ID)
	if e != nil {
		t.Fatal(e)
	}
	revision := int64(0)
	p["revision"] = float64(1)
	if e = s.Store.checkpoint(context.Background(), p, &revision, op.ID, false); e == nil {
		t.Fatal("expired operation wrote checkpoint")
	}
	got, e := s.Store.Preparation(context.Background(), p["id"].(string))
	if e != nil || got["revision"] != float64(0) {
		t.Fatal(got, e)
	}
}
func TestNativePreparationActiveLeaseNegative(t *testing.T) {
	s, p, _ := runningNativePreparation(t)
	fresh, e := s.Store.ReserveOperation(context.Background(), OperationRequest{Name: "canonical_prepare", Key: uuid.NewString(), Path: "/prepare", Body: json.RawMessage(`{}`)})
	if e != nil {
		t.Fatal(e)
	}
	if _, e = s.Store.DB.Exec(context.Background(), "UPDATE operation SET state='running' WHERE id=$1", fresh.ID); e != nil {
		t.Fatal(e)
	}
	if e = s.Store.takePreparation(context.Background(), p, fresh.ID); e == nil {
		t.Fatal("active operation superseded")
	}
}

func TestNativePreparationFailedResumePositive(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "fail-once", 200)
	ctx := context.Background()
	p, e := s.PrepareCanonical(ctx, r, uuid.NewString(), c)
	if e == nil || *n != 1 {
		t.Fatal("missing native first failure", e, *n)
	}
	id := p["id"].(string)
	r.PreparationID = &id
	r.Attempt = 2
	got, e := s.PrepareCanonical(ctx, r, uuid.NewString(), c)
	if e != nil || *n != 2 || got["settings_sha256"] != p["settings_sha256"] || got["phase_states"].(map[string]any)["canonical_text"] != "complete" || len(got["operation_ids"].([]any)) != 2 || got["last_failure"] != nil {
		t.Fatal(e, *n, got)
	}
	saveNativePreparationEvidence(t, s, got)
}
func TestNativePreparationLostCheckpointPositive(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	ctx := context.Background()
	key := uuid.NewString()
	p, e := s.PrepareCanonical(ctx, r, key, c)
	if e != nil {
		t.Fatal(e)
	}
	// Test-owned interrupted parent head with its already committed child bytes.
	// The immutable completed head/document and child receipts remain retained.
	p["revision"] = float64(2)
	p["canonical_asset_id"] = nil
	p["canonical_sha256"] = nil
	p["active_operation_id"] = p["original_operation_id"]
	p["phase_states"].(map[string]any)["canonical_text"] = "running"
	raw, _ := lab.Canonical(p)
	expected := int64(1)
	id := p["settings_asset_id"].(string)
	if _, e = s.Store.WriteDocuments(ctx, []DocumentWrite{{ID: uuid.NewString(), Kind: "preparation-state", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: p["id"].(string), Expected: &expected, State: "running"}, References: []Reference{{Pointer: "/settings_asset_id", ID: id, Scope: id, Kind: "asset-bytes", SHA: p["settings_sha256"].(string), Relation: "settings_asset_id"}}}}); e != nil {
		t.Fatal(e)
	}
	prepID := p["id"].(string)
	r.PreparationID = &prepID
	r.Attempt = 2
	got, e := s.PrepareCanonical(ctx, r, uuid.NewString(), c)
	if e != nil || *n != 1 || got["canonical_asset_id"] == nil || got["phase_states"].(map[string]any)["canonical_text"] != "complete" {
		t.Fatal(e, *n, got)
	}
	saveNativePreparationEvidence(t, s, got)
}
func TestNativePreparationAttemptCounterNegative(t *testing.T) {
	s, p, _ := runningNativePreparation(t)
	raw, e := s.Store.ReadAsset(context.Background(), p["settings_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var settings map[string]any
	_ = json.Unmarshal(raw, &settings)
	id := p["id"].(string)
	r := CanonicalPreparationRequest{BlueprintID: settings["blueprint"].(map[string]any)["id"].(string), ConfigurationSHA: settings["configuration"].(map[string]any)["configuration_sha256"].(string), Sources: []string{}, Attempt: 99, PreparationID: &id}
	if _, e = s.PrepareCanonical(context.Background(), r, uuid.NewString(), nil); !errors.Is(e, ErrConflict) {
		t.Fatal(e)
	}
	got, e := s.Store.Preparation(context.Background(), id)
	if e != nil || got["revision"] != float64(0) {
		t.Fatal(e, got)
	}
}
func TestNativePreparationRevisionConflictNegative(t *testing.T) {
	s, p, op := runningNativePreparation(t)
	wrong := int64(9)
	p["revision"] = float64(10)
	if e := s.Store.checkpoint(context.Background(), p, &wrong, op.ID, false); !errors.Is(e, ErrRevision) {
		t.Fatal(e)
	}
}

func preparationHTTP(t *testing.T, s *Server, method, path, body, key string) *httptest.ResponseRecorder {
	t.Helper()
	s.token = "NATIVE_HTTP_CREDENTIAL"
	r := httptest.NewRequest(method, path, strings.NewReader(body))
	r.Header.Set("Authorization", "Bearer NATIVE_HTTP_CREDENTIAL")
	r.Header.Set("Origin", "http://localhost:3000")
	r.Header.Set("Content-Type", "application/json")
	r.Header.Set("Idempotency-Key", key)
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	return w
}
func TestNativePreparationHTTPBlueprintPositive(t *testing.T) {
	s := NewServer(preparationNative(t), "http://localhost:3000", "")
	key := uuid.NewString()
	body := `{"exercise_request":{"topic":"Library discussion","speaker_count":2,"text_length_words":80}}`
	w := preparationHTTP(t, s, "POST", "/api/v1/blueprints", body, key)
	if w.Code != 201 {
		t.Fatal(w.Code, w.Body.String())
	}
	var b map[string]any
	_ = json.Unmarshal(w.Body.Bytes(), &b)
	read := preparationHTTP(t, s, "GET", "/api/v1/blueprints/"+b["id"].(string), "", "")
	if read.Code != 200 || read.Body.String() != w.Body.String() {
		t.Fatal(read.Code, read.Body.String())
	}
	again := preparationHTTP(t, s, "POST", "/api/v1/blueprints", body, key)
	if again.Code != 201 || again.Body.String() != w.Body.String() {
		t.Fatal("blueprint idempotency lost")
	}
}
func TestNativePreparationKeysetPositive(t *testing.T) {
	s, _, _ := runningNativePreparation(t)
	ctx := context.Background()
	seen := map[string]bool{}
	cursor := ""
	for {
		page, e := s.Store.Preparations(ctx, 1, cursor)
		if e != nil {
			t.Fatal(e)
		}
		for _, p := range page["items"].([]map[string]any) {
			id := p["id"].(string)
			if seen[id] {
				t.Fatal("duplicate keyset item")
			}
			seen[id] = true
		}
		if page["next_cursor"] == nil {
			break
		}
		cursor = page["next_cursor"].(string)
	}
	if len(seen) == 0 {
		t.Fatal("missing saved preparation")
	}
	w := preparationHTTP(t, s, "GET", "/api/v1/preparations?limit=1", "", "")
	if w.Code != 200 || !strings.Contains(w.Body.String(), `"items"`) {
		t.Fatal(w.Code, w.Body.String())
	}
}
func TestNativePreparationCursorNegative(t *testing.T) {
	s := NewServer(preparationNative(t), "http://localhost:3000", "")
	w := preparationHTTP(t, s, "GET", "/api/v1/preparations?cursor=malformed", "", "")
	if w.Code != 400 {
		t.Fatal(w.Code)
	}
	if _, _, e := contracts.Validate("error-response", "2.0.0", w.Body.Bytes()); e != nil {
		t.Fatal(e)
	}
}
func TestNativePreparationDuplicateJSONNegative(t *testing.T) {
	s := NewServer(preparationNative(t), "http://localhost:3000", "")
	w := preparationHTTP(t, s, "POST", "/api/v1/blueprints", `{"exercise_request":{"topic":"First","topic":"Second","speaker_count":1,"text_length_words":10}}`, uuid.NewString())
	if w.Code != 400 {
		t.Fatal(w.Code, w.Body.String())
	}
	if _, _, e := contracts.Validate("error-response", "2.0.0", w.Body.Bytes()); e != nil {
		t.Fatal(e)
	}
}

// Once admitted, persisted values are trusted. Constructed test-owned records
// make any unwanted second schema/hash/data audit observable.
func TestNativePreparationTrustedDocumentPositive(t *testing.T) {
	s := preparationNative(t)
	id := uuid.NewString()
	ctx := context.Background()
	_, e := s.DB.Exec(ctx, "INSERT INTO document(id,workspace_id,kind,schema_version,schema_sha256,payload_sha256,payload) SELECT $1,'local','error-response',version,sha256,$2,'{}'::jsonb FROM schema_registry WHERE kind='error-response'", id, strings.Repeat("a", 64))
	if e != nil {
		t.Fatal(e)
	}
	d, e := s.ReadDocument(ctx, id)
	if e != nil || string(d.Payload) != "{}" {
		t.Fatal("stored record was revalidated", e, string(d.Payload))
	}
}
func TestNativePreparationTrustedAssetPositive(t *testing.T) {
	s := preparationNative(t)
	ctx := context.Background()
	a, e := s.saveProviderBytes(ctx, []byte("accepted"), "provider_input")
	if e != nil {
		t.Fatal(e)
	}
	_, e = s.Media.PutObject(ctx, s.Bucket, a.Key, strings.NewReader("stored value"), int64(len("stored value")), minio.PutObjectOptions{})
	if e != nil {
		t.Fatal(e)
	}
	body, e := s.ReadAsset(ctx, a.ID)
	if e != nil || string(body) != "stored value" {
		t.Fatal("stored blob was revalidated", e, string(body))
	}
}
func TestNativePreparationNoReadbackNegative(t *testing.T) {
	s := preparationNative(t)
	ctx := context.Background()
	body := []byte("admitted")
	a, e := s.ReserveAsset(ctx, AssetRequest{Operation: OperationRequest{Name: "trust_once", Key: uuid.NewString(), Path: "/test/trust", Body: json.RawMessage(`{}`)}, SHA: contracts.Digest(body), Size: int64(len(body)), Purpose: "provider_input", MIME: "application/json"})
	if e != nil {
		t.Fatal(e)
	}
	a, e = s.UploadAsset(ctx, a.ID, body)
	if e != nil {
		t.Fatal(e)
	}
	if e = s.Media.RemoveObject(ctx, s.Bucket, a.Key, minio.RemoveObjectOptions{}); e != nil {
		t.Fatal(e)
	}
	if _, e = s.VerifyAsset(ctx, a.ID); e != nil {
		t.Fatal("accepted bytes were reread", e)
	}
	if _, e = s.LinkAsset(ctx, a.ID, nil); e != nil {
		t.Fatal("link repeated content admission", e)
	}
}
func TestNativePreparationMissingRecordNegative(t *testing.T) {
	s := preparationNative(t)
	if _, e := s.ReadDocument(context.Background(), uuid.NewString()); e == nil {
		t.Fatal("missing record invented")
	}
	if _, e := s.ReadAsset(context.Background(), uuid.NewString()); e == nil {
		t.Fatal("missing blob invented")
	}
}

func TestNativePreparationFailedActionReplayPositive(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "fail-once", 200)
	ctx := context.Background()
	key := uuid.NewString()
	failed, err := s.PrepareCanonical(ctx, r, key, c)
	if err == nil || *n != 1 {
		t.Fatal("missing first failure", err, *n)
	}
	original := r
	id := failed["id"].(string)
	r.PreparationID = &id
	r.Attempt = 2
	completed, err := s.PrepareCanonical(ctx, r, uuid.NewString(), c)
	if err != nil || completed["last_failure"] != nil || *n != 2 {
		t.Fatal("resume failed", err, completed, *n)
	}
	replay, err := s.PrepareCanonical(ctx, original, key, c)
	if err == nil || replay["phase_states"].(map[string]any)["canonical_text"] != "failed" || replay["revision"] != failed["revision"] || replay["last_failure"].(map[string]any)["code"] != failed["last_failure"].(map[string]any)["code"] || *n != 2 {
		t.Fatal("failed action changed after resume", err, replay, *n)
	}
	current, err := s.Store.Preparation(ctx, id)
	if err != nil || current["phase_states"].(map[string]any)["canonical_text"] != "complete" {
		t.Fatal("replay replaced current head", err, current)
	}
}

func TestNativePreparationCompletedActionReplayPositive(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	ctx := context.Background()
	key := uuid.NewString()
	saved, err := s.PrepareCanonical(ctx, r, key, c)
	if err != nil {
		t.Fatal(err)
	}
	// A newer selected head is a separate version; the original action owns its
	// already committed immutable response. This models later phase advancement.
	newer := make(map[string]any)
	for k, v := range saved {
		newer[k] = v
	}
	newer["revision"] = float64(2)
	raw, _ := json.Marshal(newer)
	expected := int64(1)
	if _, err = s.Store.WriteDocuments(ctx, []DocumentWrite{{ID: uuid.NewString(), Kind: "preparation-state", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: saved["id"].(string), Expected: &expected, State: "complete"}, References: []Reference{{Pointer: "/settings_asset_id", ID: saved["settings_asset_id"].(string), Scope: saved["settings_asset_id"].(string), Kind: "asset-bytes", SHA: saved["settings_sha256"].(string), Relation: "settings_asset_id"}, {Pointer: "/canonical_asset_id", ID: saved["canonical_asset_id"].(string), Scope: saved["canonical_asset_id"].(string), Kind: "asset-bytes", SHA: saved["canonical_sha256"].(string), Relation: "canonical_asset_id"}}}}); err != nil {
		t.Fatal(err)
	}
	replay, err := s.PrepareCanonical(ctx, r, key, c)
	if err != nil || replay["revision"] != saved["revision"] || *n != 1 {
		t.Fatal("completed action read a newer head", err, replay, *n)
	}
}

func TestNativePreparationFailedReplayConflictNegative(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "fail-once", 200)
	key := uuid.NewString()
	if _, err := s.PrepareCanonical(context.Background(), r, key, c); err == nil {
		t.Fatal("missing first failure")
	}
	r.Attempt = 2
	if _, err := s.PrepareCanonical(context.Background(), r, key, c); !errors.Is(err, ErrConflict) || *n != 1 {
		t.Fatal("changed failed action accepted", err, *n)
	}
}

func TestNativePreparationMissingActionResultNegative(t *testing.T) {
	s, r, c, n := prepareNativeFixture(t, "", 200)
	ctx := context.Background()
	key := uuid.NewString()
	if _, err := s.PrepareCanonical(ctx, r, key, c); err != nil {
		t.Fatal(err)
	}
	if _, err := s.Store.DB.Exec(ctx, "UPDATE operation SET result_document_id=NULL WHERE operation_name='canonical_prepare' AND idempotency_key=$1", key); err != nil {
		t.Fatal(err)
	}
	if _, err := s.PrepareCanonical(ctx, r, key, c); err == nil || *n != 1 {
		t.Fatal("missing result replaced by latest head or redispatch", err, *n)
	}
}
