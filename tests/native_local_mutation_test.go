package app

import (
	"bytes"
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"testing"
)

// These are opt-in actual model observations, never fixed-response acceptance.
// The host-native observer connects directly to the existing local Ollama. It preserves request and response bytes and never uses a cloud model.
func observeLocalMutation(t *testing.T, count int) {
	t.Helper()
	ctx := context.Background()
	store, openErr := OpenStorage(ctx, os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	if openErr != nil {
		t.Fatal(openErr)
	}
	t.Cleanup(store.DB.Close)
	c, rev, e := store.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	p["provider"], p["model"], p["endpoint"] = "local_responses", "gpt-oss:20b", "http://127.0.0.1:11434/v1/responses"
	p["adapter_version"] = "local-responses-v1"
	p["auth_method"], p["billing_mode"], p["credential_ref"], p["stream"] = "local_none", "local", "local-none", false
	p["context_budget_tokens"], p["max_output_tokens"] = float64(131072), float64(8000)
	p["reasoning_effort"] = "low"
	p["temperature"] = float64(0.7)
	p["structured_output"] = true
	c["llm_lab_capture_content"], c["llm_lab_trace_enabled"] = true, true
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	raw, _ := json.Marshal(c)
	_, _, e = store.PutConfiguration(ctx, raw, uuid.NewString(), rev)
	if e != nil {
		t.Fatal(e)
	}
	activation, e := os.ReadFile(os.Getenv("TANGERINE_LOCAL_MUTATION_BUNDLE"))
	if e != nil {
		t.Fatal(e)
	}
	var bundle lab.Bundle
	if e = json.Unmarshal(activation, &bundle); e != nil {
		t.Fatal(e)
	}
	if _, e = store.ActivateLabBundle(ctx, bundle, nil); e != nil {
		t.Fatal(e)
	}
	c, _, e = store.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	request := map[string]any{"exercise_request": map[string]any{"topic": "Describe a café’s opening hours and fresh coffee in the simple present, with the café as the singular subject. For the clean text use opens and serves exactly once each as its two finite verbs. The later mutation may intentionally change one of these forms.", "speaker_count": 1, "text_length_words": 20, "english_level": "B1", "mutation_count": count, "category_families": []any{"grammar"}}, "targets": []any{map[string]any{"taxonomy_id": "grammar.verbs.subject_verb_agreement", "min_count": count, "max_count": count, "expected_judgment": "true_error", "hard_render_constraints": []any{}}}}
	raw, _ = json.Marshal(request)
	b, e := store.WriteBlueprint(ctx, raw, uuid.NewString())
	if e != nil {
		t.Fatal(e)
	}
	root := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	dir := filepath.Join(root, t.Name())
	if e = os.MkdirAll(dir, 0700); e != nil {
		t.Fatal(e)
	}
	defer saveLocalDiagnostics(t, store, dir)
	dispatchFile, e := os.OpenFile(filepath.Join(dir, "dispatch-observations.jsonl"), os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	if e != nil {
		t.Fatal(e)
	}
	defer dispatchFile.Close()
	transport := &http.Transport{}
	defer transport.CloseIdleConnections()
	client := &http.Client{Transport: preparationTrip(func(req *http.Request) (*http.Response, error) {
		body, e := io.ReadAll(req.Body)
		if e != nil {
			return nil, e
		}
		req.Body = io.NopCloser(bytes.NewReader(body))
		response, e := transport.RoundTrip(req)
		event := map[string]any{"wire_request_sha256": contracts.Digest(body), "endpoint": req.URL.String(), "route": "127.0.0.1:11434", "model": "gpt-oss:20b", "billing_mode": "local", "fixture_response": false}
		if e == nil {
			bytes, e2 := io.ReadAll(response.Body)
			response.Body.Close()
			response.Body = io.NopCloser(bytesReader(bytes))
			event["wire_response_sha256"] = contracts.Digest(bytes)
			event["http_status"] = response.StatusCode
			if e2 != nil {
				e = e2
			}
		}
		if e != nil {
			event["transport_error"] = e.Error()
		}
		_ = json.NewEncoder(dispatchFile).Encode(event)
		return response, e
	})}
	s := NewServer(store, "http://localhost:3000", "")
	r := CanonicalPreparationRequest{BlueprintID: b["id"].(string), ConfigurationSHA: c["configuration_sha256"].(string), Sources: []string{}, Attempt: 1}
	clean, e := s.PrepareCanonical(ctx, r, uuid.NewString(), client)
	if clean != nil {
		saveActualLocalEvidence(t, s, clean)
	}
	if e != nil {
		t.Fatal("actual local canonical phase", e)
	}
	cleanRaw, readErr := store.ReadAsset(ctx, clean["canonical_asset_id"].(string))
	if readErr != nil {
		t.Fatal(readErr)
	}
	var cleanContent map[string]any
	_ = json.Unmarshal(cleanRaw, &cleanContent)
	cleanParts := []string{}
	for _, v := range cleanContent["utterances"].([]any) {
		cleanParts = append(cleanParts, v.(map[string]any)["canonical_text"].(string))
	}
	if err := agreementFixtureCanonical(strings.Join(cleanParts, "\n")); err != nil {
		t.Fatal("independent clean agreement expectation", err)
	}
	ident := clean["id"].(string)
	r.PreparationID = &ident
	r.Attempt = 2
	mutated, e := s.PrepareMutation(ctx, r, uuid.NewString(), client)
	if mutated != nil {
		saveActualLocalEvidence(t, s, mutated)
	}

	if e != nil {
		t.Fatal("actual local mutation phase", e)
	}
	raw, e = store.ReadAsset(ctx, mutated["mutated_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var content map[string]any
	_ = json.Unmarshal(raw, &content)
	if len(content["planned_units"].([]any)) != count {
		t.Fatal("independent requested count", content)
	}
	if count > 0 {
		canonicalParts, surfaceParts := []string{}, []string{}
		for _, v := range content["utterances"].([]any) {
			turn := v.(map[string]any)
			canonicalParts = append(canonicalParts, turn["canonical_text"].(string))
			surfaceParts = append(surfaceParts, turn["surface_text"].(string))
		}
		expected, err := agreementFixtureMutation(strings.Join(canonicalParts, "\n"), strings.Join(surfaceParts, "\n"))
		if err != nil {
			t.Fatal("independent mutation direction", err)
		}
		preferred := 0
		for _, v := range content["planned_units"].([]any)[0].(map[string]any)["corrections"].([]any) {
			option := v.(map[string]any)
			if option["canonical"] == true {
				preferred++
				if !agreementFixtureCorrection(expected, option["kind"].(string), option["text"].(string)) {
					t.Fatal("independent preferred correction", expected, option)
				}
			}
		}
		if preferred == 0 {
			t.Fatal("missing independently expected preferred correction", expected)
		}
		// Independent linguistic expectations: an agreement error has a changed verb,
		// an actual repair, and supported optional-explanation rubrics.
		u := content["planned_units"].([]any)[0].(map[string]any)
		if u["primary_taxonomy_id"] != "grammar.verbs.subject_verb_agreement" || u["expected_judgment"] != "true_error" || u["correction_eligible"] != true || u["explanation_eligible"] != true || len(u["corrections"].([]any)) == 0 {
			t.Fatal("independent target category and judgment", u)
		}
		spans := u["text_spans"].([]any)
		if len(spans) != 1 {
			t.Fatal("expected one localized agreement error", u)
		}
		span := spans[0].(map[string]any)
		var heard string
		for _, v := range content["utterances"].([]any) {
			turn := v.(map[string]any)
			if turn["id"] == span["utterance_id"] {
				text := []rune(turn["surface_text"].(string))
				heard = string(text[int(span["span"].(map[string]any)["start_cp"].(float64)):int(span["span"].(map[string]any)["end_cp"].(float64))])
			}
		}
		if heard == "" {
			t.Fatal("expected audible error scope")
		}
		for _, v := range u["corrections"].([]any) {
			option := v.(map[string]any)
			if strings.TrimSpace(option["text"].(string)) == heard || len(option["required_propositions"].([]any)) == 0 {
				t.Fatal("independently expected repaired verb and rubric", option)
			}
		}
		if len(u["rationale_required_propositions"].([]any)) == 0 {
			t.Fatal("expected optional-explanation rubric")
		}
	}

	if count == 0 {
		for _, v := range content["utterances"].([]any) {
			u := v.(map[string]any)
			if u["canonical_text"] != u["surface_text"] {
				t.Fatal("zero-mutation text changed", u)
			}
		}
	}
}

func bytesReader(v []byte) *bytes.Reader               { return bytes.NewReader(v) }
func TestNativeLocalMutationPositive(t *testing.T)     { observeLocalMutation(t, 1) }
func TestNativeLocalZeroMutationNegative(t *testing.T) { observeLocalMutation(t, 0) }

func saveLocalDiagnostics(t *testing.T, store *Storage, dir string) {
	t.Helper()
	ctx := context.Background()
	// Retain all diagnostic packets before teardown, including failed calls.
	rows, e2 := store.DB.Query(ctx, "SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND a.state='linked'")
	if e2 != nil {
		t.Fatal(e2)
	}
	ids := []string{}
	for rows.Next() {
		var id string
		_ = rows.Scan(&id)
		ids = append(ids, id)
	}
	rows.Close()
	for _, id := range ids {
		raw, err := store.ReadAsset(ctx, id)
		if err != nil {
			t.Fatal(err)
		}
		if err = os.WriteFile(filepath.Join(dir, "diagnostic-"+id+".json"), raw, 0600); err != nil {
			t.Fatal(err)
		}
	}
}

func saveActualLocalEvidence(t *testing.T, s *Server, p map[string]any) {
	t.Helper()
	saveNativeMutationEvidence(t, s, p)
	raw, _ := json.MarshalIndent(map[string]any{"origin": "actual_local_ollama_with_native_preparation_storage", "model": "gpt-oss:20b", "billing_mode": "local", "fixture_response": false, "preparation": p}, "", "  ")
	if e := os.WriteFile(filepath.Join(os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE"), t.Name(), "state.json"), raw, 0600); e != nil {
		t.Fatal(e)
	}
}
