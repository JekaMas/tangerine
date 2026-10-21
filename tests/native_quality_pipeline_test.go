package app

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync/atomic"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"testing"
)

func qualitySimpleSubmission(t *testing.T, s *Server, scope string, input any) QualitySubmission {
	t.Helper()
	c, _, e := s.Store.Configuration(context.Background())
	requireListening(t, e)
	b, e := s.Store.ActiveLabBundle(context.Background())
	requireListening(t, e)
	raw := mustJSON(input)
	ex := mustJSON(map[string]any{"schema_version": "1.0.0", "expected_mapping": nil, "expected_metric_values": []any{}, "expected_canonical_sha256": nil, "semantic_propositions": []any{}})
	dataset := QualityDataset{Version: "2.0.0", Scope: scope, Cases: []QualityCase{{Version: "2.0.0", ID: "c", Stage: "case_generation", Polarity: "positive", Origin: "constructed", Basis: "authored_assertion", Group: "context-1", Split: "development", Taxonomy: []string{"grammar.verbs.subject_verb_agreement"}, Input: "input", InputSHA: contracts.Digest(raw), Expectations: "expected", ExpectationsSHA: contracts.Digest(ex), References: []string{}}}}
	var m map[string]any
	_ = json.Unmarshal(mustJSON(dataset), &m)
	delete(m, "dataset_sha256")
	dataset.SHA = lab.Hash(m)
	config := mustJSON(c)
	return QualitySubmission{Experiment: QualityExperiment{ID: uuid.NewString(), Scope: scope, Dataset: "dataset", DatasetSHA: dataset.SHA, Scorer: "quality-v1", Variants: []QualityVariant{{ID: "baseline", BundleID: "bundle", BundleSHA: b.SHA, Profile: c["llm_profile"].(string), Config: "config", ConfigSHA: contracts.Digest(config)}}, Repetitions: 1}, Assets: map[string]json.RawMessage{"dataset": mustJSON(dataset), "input": raw, "expected": ex, "config": config, "bundle": mustJSON(b)}}
}
func qualityGenerationServer(t *testing.T, invalid bool) (*Server, *atomic.Int32) {
	t.Helper()
	s := NewServer(listeningNative(t), "http://localhost:3000", "")
	calls := new(atomic.Int32)
	model := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls.Add(1)
		var wire map[string]any
		requireListening(t, json.NewDecoder(r.Body).Decode(&wire))
		var input map[string]any
		for _, v := range wire["input"].([]any) {
			part := v.(map[string]any)["content"].(string)
			if strings.HasPrefix(part, "Complete stage input: ") {
				requireListening(t, json.Unmarshal([]byte(strings.TrimPrefix(part, "Complete stage input: ")), &input))
			}
		}
		_, clean, mutation, _ := mutationFixture()
		candidate := clean
		if input["phase"] == "mutation" {
			candidate = mutation
			if invalid {
				candidate["utterances"].([]any)[0].(map[string]any)["canonical_text"] = "Silently rewritten source."
			}
		}
		candidate["blueprint_id"] = input["blueprint"].(map[string]any)["id"]
		_ = json.NewEncoder(w).Encode(map[string]any{"id": "constructed-generation", "object": "response", "status": "completed", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": string(mustJSON(candidate))}}}}})
	}))
	t.Cleanup(model.Close)
	c, rev, e := s.Store.Configuration(context.Background())
	requireListening(t, e)
	c["speech_profile"] = "kokoro-local-en-v1"
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	for k, v := range map[string]any{"provider": "local_responses", "model": "constructed-generator", "endpoint": model.URL + "/v1/responses", "auth_method": "local_none", "billing_mode": "local", "credential_ref": "local-none", "stream": false, "context_budget_tokens": 1000000, "structured_output": false, "max_output_tokens": 4096} {
		p[k] = v
	}
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = s.Store.PutConfiguration(context.Background(), mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	return s, calls
}
func qualityGenerationRequest() map[string]any {
	return map[string]any{"topic": "Café opening", "speaker_count": 1, "text_length_words": 50, "category_families": []any{"grammar"}, "mutation_count": 1}
}
func TestNativeQualityGenerationPositive(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	p, e := s.Store.AdmitExperiment(context.Background(), qualitySimpleSubmission(t, s, "generation_pipeline", qualityGenerationRequest()))
	requireListening(t, e)
	p, e = s.RunQualityExperiment(context.Background(), p.ID, false, nil)
	requireListening(t, e)
	if p.Status != "completed" || calls.Load() != 2 {
		t.Fatalf("%s calls=%d %+v", p.Status, calls.Load(), p.Rows[0])
	}
	if len(p.Rows[0].Receipts) != 2 {
		t.Fatal(p.Rows[0])
	}
	for _, m := range p.Rows[0].Metrics {
		if m.ID == "llm_lab.word_length_relative_deviation" && (m.Value == nil || *m.Value != "0.92") {
			t.Fatal(m)
		}
	}
}
func TestNativeQualityGenerationFailureNegative(t *testing.T) {
	s, calls := qualityGenerationServer(t, true)
	p, e := s.Store.AdmitExperiment(context.Background(), qualitySimpleSubmission(t, s, "generation_pipeline", qualityGenerationRequest()))
	requireListening(t, e)
	p, e = s.RunQualityExperiment(context.Background(), p.ID, false, nil)
	requireListening(t, e)
	if p.Status != "partial" || p.Rows[0].Status != "failed" || calls.Load() != 3 {
		t.Fatal(p.Status, calls.Load())
	}
	raw, e := s.Store.ReadAsset(context.Background(), *p.Rows[0].Output)
	requireListening(t, e)
	if !strings.Contains(string(raw), "canonical_sha256") {
		t.Fatal("clean checkpoint lost")
	}
}
func qualitySpeechTarget(t *testing.T, s *Server, fail bool) *atomic.Int32 {
	calls := new(atomic.Int32)
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var body map[string]any
		requireListening(t, json.NewDecoder(r.Body).Decode(&body))
		switch r.URL.Path {
		case "/internal/v1/plan":
			turn := body["plan"].(map[string]any)["turns"].([]any)[0]
			_ = json.NewEncoder(w).Encode(map[string]any{"pieces": []any{turn}, "model_context": map[string]any{"origin": "constructed_transport_fixture"}})
		case "/internal/v1/quality":
			_ = json.NewEncoder(w).Encode(map[string]any{"warnings": []any{}, "origin": "constructed_transport_fixture"})
		default:
			calls.Add(1)
			if fail {
				w.WriteHeader(503)
				_, _ = w.Write([]byte(`{"error":"SPEECH_UNAVAILABLE"}`))
				return
			}
			audio := speechWAV([]byte{7, 0, 8, 0, 9, 0})
			_ = json.NewEncoder(w).Encode(map[string]any{"audio_base64": base64.StdEncoding.EncodeToString(audio), "sample_count": 3, "receipt": map[string]any{"origin": "constructed_transport_fixture"}})
		}
	}))
	t.Cleanup(target.Close)
	s.SpeechURL = target.URL
	return calls
}
func TestNativeQualityFullFlowPositive(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	speech := qualitySpeechTarget(t, s, false)
	p, e := s.Store.AdmitExperiment(context.Background(), qualitySimpleSubmission(t, s, "full_flow", qualityGenerationRequest()))
	requireListening(t, e)
	p, e = s.RunQualityExperiment(context.Background(), p.ID, false, nil)
	requireListening(t, e)
	if p.Status != "completed" || calls.Load() != 2 || speech.Load() != 1 {
		t.Fatalf("%s model=%d speech=%d %+v", p.Status, calls.Load(), speech.Load(), p.Rows[0])
	}
	raw, e := s.Store.ReadAsset(context.Background(), *p.Rows[0].Output)
	requireListening(t, e)
	var packet map[string]any
	requireListening(t, json.Unmarshal(raw, &packet))
	details := packet["candidate_output"].(map[string]any)
	prep := details["preparation"].(map[string]any)
	if prep["audio_asset_id"] == nil || prep["key_id"] == nil {
		t.Fatal("full flow omitted stored audio/key", prep)
	}
}
func TestNativeQualitySpeechFailureNegative(t *testing.T) {
	s, _ := qualityGenerationServer(t, false)
	qualitySpeechTarget(t, s, true)
	p, e := s.Store.AdmitExperiment(context.Background(), qualitySimpleSubmission(t, s, "full_flow", qualityGenerationRequest()))
	requireListening(t, e)
	p, e = s.RunQualityExperiment(context.Background(), p.ID, false, nil)
	requireListening(t, e)
	if p.Status != "partial" || p.Rows[0].Output == nil || p.Rows[0].Error == nil {
		t.Fatal(p)
	}
	if len(p.Rows[0].Receipts) < 3 {
		t.Fatal("failed speech receipt absent", len(p.Rows[0].Receipts))
	}
}

var _ = fmt.Sprint
