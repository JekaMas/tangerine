package app

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func nativeMutationFixture(t *testing.T, mode string) (*Server, CanonicalPreparationRequest, *http.Client, *int, map[string]any) {
	t.Helper()
	s, r, cleanClient, cleanCalls := prepareNativeFixture(t, "", 200)
	// This constructed model has no tokenizer. Its explicit byte-conservative
	// budget must hold the complete selected records; no category is truncated.
	config, rev, err := s.Store.Configuration(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	config["llm_profiles"].([]any)[0].(map[string]any)["context_budget_tokens"] = float64(1000000)
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(config, k)
	}
	body, _ := json.Marshal(config)
	saved, _, err := s.Store.PutConfiguration(context.Background(), body, uuid.NewString(), rev)
	if err != nil {
		t.Fatal(err)
	}
	r.ConfigurationSHA = saved["configuration_sha256"].(string)
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), cleanClient)
	if e != nil || *cleanCalls != 1 {
		t.Fatal(p, e)
	}
	r.PreparationID = new(string)
	*r.PreparationID = p["id"].(string)
	r.Attempt = 2
	_, _, candidate, _ := mutationFixture()
	candidate["blueprint_id"] = r.BlueprintID
	calls := 0
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		calls++
		raw, _ := io.ReadAll(req.Body)
		if !containsMutationInput(raw) {
			t.Error("mutation input omitted original text/recipe/phase")
		}
		w.Header().Set("Content-Type", "application/json")
		if mode == "fail-once" && calls == 1 || mode == "limit" {
			w.WriteHeader(429)
			_, _ = io.WriteString(w, `{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}`)
			return
		}
		out := candidate
		if mode == "unattributed" {
			out["utterances"].([]any)[0].(map[string]any)["surface_text"] = "The café open tomorrows."
		}
		if mode == "invalid" {
			if calls == 2 && (!strings.Contains(string(raw), "validation_detail") || !strings.Contains(string(raw), "canonical_turn_identity")) {
				t.Error("semantic repair omitted the owning admission reason")
			}
			raw, _ := json.Marshal(candidate)
			_ = json.Unmarshal(raw, &out)
			out["utterances"].([]any)[0].(map[string]any)["canonical_text"] = "Replaced baseline."
		}
		raw, _ = json.Marshal(out)
		encoded, _ := json.Marshal(string(raw))
		_, _ = io.WriteString(w, `{"object":"response","id":"mutation-fixture","status":"completed","model":"constructed-clean-text","output":[{"type":"message","content":[{"type":"output_text","text":`+string(encoded)+`}]}]}`)
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
	return s, r, client, &calls, p
}
func containsMutationInput(raw []byte) bool {
	var wire map[string]any
	if json.Unmarshal(raw, &wire) != nil {
		return false
	}
	text := string(raw)
	return strings.Contains(text, "The café opens tomorrow.") && strings.Contains(text, "subject_verb_agreement") && strings.Contains(text, "canonical_script") && strings.Contains(text, "mutation")
}
func TestNativeMutationCheckpointPositive(t *testing.T) {
	s, r, client, n, clean := nativeMutationFixture(t, "")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil || *n != 1 || p["phase_states"].(map[string]any)["mutation"] != "complete" || p["canonical_asset_id"] != clean["canonical_asset_id"] || p["audio_asset_id"] != nil {
		t.Fatal(p, e, *n)
	}
	raw, e := s.Store.ReadAsset(context.Background(), p["mutation_manifest_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var m map[string]any
	_ = json.Unmarshal(raw, &m)
	if m["surface_word_count"] != float64(4) || len(m["planned_units"].([]any)) != 1 || m["edits"].([]any)[0].(map[string]any)["original_text"] != "s" {
		t.Fatal(m)
	}
	saveNativeMutationEvidence(t, s, p)
}
func TestNativeMutationEvidencePositive(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil || *n != 1 {
		t.Fatal(p, e)
	}
	doc, e := s.Store.ReadDocument(context.Background(), p["candidate_id"].(string))
	if e != nil || doc.Kind != "candidate-envelope" {
		t.Fatal(doc, e)
	}
	var receipts, contexts, audits int
	_ = s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document d WHERE kind='provider-receipt' AND payload->>'operation_id' IN (SELECT child.id::text FROM operation parent JOIN operation child ON child.idempotency_key=parent.idempotency_key AND child.operation_name IN ('canonical_text','mutation') WHERE parent.subject_id=$1)", p["id"]).Scan(&receipts)
	_ = s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document d WHERE kind='llm-context-snapshot' AND payload->>'operation_id' IN (SELECT child.id::text FROM operation parent JOIN operation child ON child.idempotency_key=parent.idempotency_key AND child.operation_name IN ('canonical_text','mutation') WHERE parent.subject_id=$1)", p["id"]).Scan(&contexts)
	_ = s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM audit_event WHERE action='preparation.mutation.completed' AND event_payload->>'preparation_id'=$1", p["id"]).Scan(&audits)
	if receipts != 2 || contexts != 2 || audits != 1 {
		t.Fatal(receipts, contexts, audits)
	}
	saveNativeMutationEvidence(t, s, p)
}
func TestNativeMutationMissingCanonicalNegative(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	r.PreparationID = nil
	if _, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client); e == nil || *n != 0 {
		t.Fatal(e, *n)
	}
}
func TestNativeMutationChangedConfigurationNegative(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	r.ConfigurationSHA = strings.Repeat("f", 64)
	if _, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client); !errors.Is(e, ErrConflict) || *n != 0 {
		t.Fatal(e, *n)
	}
}
func TestNativeMutationReplayPositive(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	key := uuid.NewString()
	a, e := s.PrepareMutation(context.Background(), r, key, client)
	if e != nil {
		t.Fatal(e)
	}
	b, e := s.PrepareMutation(context.Background(), r, key, client)
	if e != nil || *n != 1 || a["mutation_manifest_asset_id"] != b["mutation_manifest_asset_id"] {
		t.Fatal(a, b, e, *n)
	}
}
func TestNativeMutationTrustedReplayPositive(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	key := uuid.NewString()
	a, e := s.PrepareMutation(context.Background(), r, key, client)
	if e != nil {
		t.Fatal(e)
	} // accepted manifest is deliberately changed at the storage boundary: read/replay must not audit it.
	_, e = s.Store.DB.Exec(context.Background(), "UPDATE asset_location SET storage_key='test-owned-absent' WHERE asset_id=$1", a["mutation_manifest_asset_id"])
	if e != nil {
		t.Fatal(e)
	}
	b, e := s.PrepareMutation(context.Background(), r, key, client)
	if e != nil || *n != 1 || b["mutation_manifest_asset_id"] != a["mutation_manifest_asset_id"] {
		t.Fatal(b, e, *n)
	}
}
func TestNativeMutationKeyConflictNegative(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	key := uuid.NewString()
	if _, e := s.PrepareMutation(context.Background(), r, key, client); e != nil {
		t.Fatal(e)
	}
	r.Attempt = 3
	if _, e := s.PrepareMutation(context.Background(), r, key, client); !errors.Is(e, ErrConflict) || *n != 1 {
		t.Fatal(e, *n)
	}
}
func TestNativeMutationAttemptNegative(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	r.Attempt = 9
	if _, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client); !errors.Is(e, ErrConflict) || *n != 0 {
		t.Fatal(e, *n)
	}
}
func TestNativeMutationFailureResumePositive(t *testing.T) {
	s, r, client, n, clean := nativeMutationFixture(t, "fail-once")
	key := uuid.NewString()
	failed, e := s.PrepareMutation(context.Background(), r, key, client)
	if e == nil || *n != 1 || failed["phase_states"].(map[string]any)["canonical_text"] != "complete" || failed["mutated_asset_id"] != nil {
		t.Fatal(failed, e, *n)
	}
	r.Attempt = 3
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil || *n != 2 || p["settings_asset_id"] != clean["settings_asset_id"] || p["last_failure"] != nil {
		t.Fatal(p, e, *n)
	}
	r.Attempt = 2
	replay, e := s.PrepareMutation(context.Background(), r, key, client)
	if e == nil || replay["last_failure"] == nil || *n != 2 {
		t.Fatal(replay, e, *n)
	}
	saveNativeMutationEvidence(t, s, p)
}
func TestNativeMutationFrozenSettingsPositive(t *testing.T) {
	s, r, client, n, clean := nativeMutationFixture(t, "")
	config, rev, e := s.Store.Configuration(context.Background())
	if e != nil {
		t.Fatal(e)
	}
	config["llm_profiles"].([]any)[0].(map[string]any)["model"] = "later-global-model"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(config, k)
	}
	raw, _ := json.Marshal(config)
	if _, _, e = s.Store.PutConfiguration(context.Background(), raw, uuid.NewString(), rev); e != nil {
		t.Fatal(e)
	}
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil || *n != 1 || p["settings_asset_id"] != clean["settings_asset_id"] {
		t.Fatal(p, e, *n)
	}
}
func TestNativeMutationInvalidOutputNegative(t *testing.T) {
	s, r, client, n, clean := nativeMutationFixture(t, "invalid")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e == nil || *n != 2 || p["candidate_id"] != nil || p["canonical_asset_id"] != clean["canonical_asset_id"] || p["phase_states"].(map[string]any)["mutation"] != "failed" {
		t.Fatal(p, e, *n)
	}
}
func TestNativeMutationProviderLimitNegative(t *testing.T) {
	s, r, client, n, clean := nativeMutationFixture(t, "limit")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e == nil || *n != 1 || p["mutation_manifest_asset_id"] != nil || p["canonical_asset_id"] != clean["canonical_asset_id"] {
		t.Fatal(p, e, *n)
	}
}
func TestNativeMutationChildRecoveryPositive(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil {
		t.Fatal(e)
	}
	rev := int64(p["revision"].(float64))
	p["revision"] = float64(rev + 1)
	p["phase_states"].(map[string]any)["mutation"] = "running"
	for _, k := range []string{"candidate_id", "mutated_asset_id", "mutation_manifest_asset_id"} {
		p[k] = nil
	}
	p["active_operation_id"] = p["operation_ids"].([]any)[1]
	raw, _ := json.Marshal(p)
	_, e = s.Store.WriteDocuments(context.Background(), []DocumentWrite{{ID: uuid.NewString(), Kind: "preparation-state", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: p["id"].(string), Expected: &rev, State: "running"}, References: []Reference{{Pointer: "/settings_asset_id", ID: p["settings_asset_id"].(string), Scope: p["settings_asset_id"].(string), Kind: "asset-bytes", SHA: p["settings_sha256"].(string), Relation: "settings_asset_id"}, {Pointer: "/canonical_asset_id", ID: p["canonical_asset_id"].(string), Scope: p["canonical_asset_id"].(string), Kind: "asset-bytes", SHA: p["canonical_sha256"].(string), Relation: "canonical_asset_id"}}}})
	if e != nil {
		t.Fatal(e)
	}
	r.Attempt = 3
	recovered, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil || *n != 1 || recovered["candidate_id"] == nil {
		t.Fatal(recovered, e, *n)
	}
	saveNativeMutationEvidence(t, s, recovered)
}
func TestNativeMutationRestartReadbackPositive(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil {
		t.Fatal(e)
	}
	other := NewServer(preparationNative(t), "http://localhost:3000", "")
	saved, e := other.Store.Preparation(context.Background(), p["id"].(string))
	if e != nil || *n != 1 || saved["mutation_manifest_asset_id"] != p["mutation_manifest_asset_id"] || saved["phase_states"].(map[string]any)["canonical_text"] != "complete" {
		t.Fatal(saved, e, *n)
	}
}
func TestNativeMutationActiveOwnerNegative(t *testing.T) {
	s, r, client, n, p := nativeMutationFixture(t, "")
	op, e := s.Store.ReserveOperation(context.Background(), OperationRequest{Name: "mutation_prepare", Key: uuid.NewString(), Path: "/prepare/mutation", Body: json.RawMessage(`{}`)})
	if e != nil {
		t.Fatal(e)
	}
	_, _ = s.Store.DB.Exec(context.Background(), "UPDATE operation SET state='running' WHERE id=$1", op.ID)
	if e = s.Store.takePreparation(context.Background(), p, op.ID, "mutation"); e != nil {
		t.Fatal(e)
	}
	r.Attempt = 3
	if _, e = s.PrepareMutation(context.Background(), r, uuid.NewString(), client); e == nil || *n != 0 {
		t.Fatal(e, *n)
	}
}
func TestNativeMutationDeadlineNegative(t *testing.T) {
	s, _, _, n, p := nativeMutationFixture(t, "")
	op, e := s.Store.ReserveOperation(context.Background(), OperationRequest{Name: "mutation_prepare", Key: uuid.NewString(), Path: "/prepare/mutation", Body: json.RawMessage(`{}`)})
	if e != nil {
		t.Fatal(e)
	}
	_, _ = s.Store.DB.Exec(context.Background(), "UPDATE operation SET state='running',started_at=$2 WHERE id=$1", op.ID, time.Now().Add(-271*time.Second))
	if e = s.Store.takePreparation(context.Background(), p, op.ID, "mutation"); e == nil || *n != 0 {
		t.Fatal(e, *n)
	}
}

func TestNativeMutationProvenancePositive(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil || *n != 1 {
		t.Fatal(p, e, *n)
	}
	var count int
	if e = s.Store.DB.QueryRow(context.Background(), "SELECT (event_payload->>'canonical_word_count')::int FROM audit_event WHERE action='preparation.mutation.completed' AND event_payload->>'preparation_id'=$1", p["id"]).Scan(&count); e != nil || count != 4 {
		t.Fatal("saved clean text has four words", count, e)
	}
}

func TestNativeMutationRecoveredProvenancePositive(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e != nil {
		t.Fatal(e)
	}
	rev := int64(p["revision"].(float64))
	p["revision"] = float64(rev + 1)
	p["phase_states"].(map[string]any)["mutation"] = "running"
	p["active_operation_id"] = p["operation_ids"].([]any)[1]
	for _, k := range []string{"candidate_id", "mutated_asset_id", "mutation_manifest_asset_id"} {
		p[k] = nil
	}
	raw, _ := json.Marshal(p)
	_, e = s.Store.WriteDocuments(context.Background(), []DocumentWrite{{ID: uuid.NewString(), Kind: "preparation-state", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: p["id"].(string), Expected: &rev, State: "running"}, References: []Reference{{Pointer: "/settings_asset_id", ID: p["settings_asset_id"].(string), Scope: p["settings_asset_id"].(string), Kind: "asset-bytes", SHA: p["settings_sha256"].(string), Relation: "settings_asset_id"}, {Pointer: "/canonical_asset_id", ID: p["canonical_asset_id"].(string), Scope: p["canonical_asset_id"].(string), Kind: "asset-bytes", SHA: p["canonical_sha256"].(string), Relation: "canonical_asset_id"}}}})
	if e != nil {
		t.Fatal(e)
	}
	r.Attempt = 3
	p, e = s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	var count int
	if e == nil {
		e = s.Store.DB.QueryRow(context.Background(), "SELECT (event_payload->>'canonical_word_count')::int FROM audit_event WHERE action='preparation.mutation.completed' AND event_payload->>'preparation_id'=$1 ORDER BY created_at DESC LIMIT 1", p["id"]).Scan(&count)
	}
	if e != nil || *n != 1 || count != 4 {
		t.Fatal("completed child recovery retains the four-word provenance without inference", count, e, *n)
	}
}

func TestNativeMutationUnattributedNegative(t *testing.T) {
	s, r, client, n, clean := nativeMutationFixture(t, "unattributed")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	if e == nil || *n != 2 || p["mutated_asset_id"] != nil || p["canonical_asset_id"] != clean["canonical_asset_id"] {
		t.Fatal("unlisted change must fail the sole repair and preserve clean text", p, e, *n)
	}
}

func TestNativeMutationInvalidProvenanceNegative(t *testing.T) {
	s, r, client, n, _ := nativeMutationFixture(t, "invalid")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	var count int
	queryErr := s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM audit_event WHERE action='preparation.mutation.completed' AND event_payload->>'preparation_id'=$1", p["id"]).Scan(&count)
	if e == nil || queryErr != nil || *n != 2 || count != 0 {
		t.Fatal("rejected output cannot record completed mutation provenance", count, e, queryErr, *n)
	}
}

func saveNativeMutationEvidence(t *testing.T, s *Server, p map[string]any) {
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
		if e := s.Store.DB.QueryRow(context.Background(), "SELECT child.id FROM operation parent JOIN operation child ON child.idempotency_key=parent.idempotency_key AND child.operation_name IN ('canonical_text','mutation') WHERE parent.id=$1", parent).Scan(&child); e != nil {
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
