package app

// These are actual local inference observations. The stored one-error cafe case
// is a fixed independently authored linguistic fixture, not model-generated truth.
import (
	"bytes"
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"tangerine.local/api/internal/contracts"
	"testing"
)

type interpretationTrip func(*http.Request) (*http.Response, error)

func (f interpretationTrip) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }
func observeLocalInterpretation(t *testing.T, answer string, wantCorrection, wantReason string) {
	f := interpretationNative(t, "good")
	ctx := context.Background()
	c, rev, e := f.s.Store.Configuration(ctx)
	requireListening(t, e)
	raw, e := os.ReadFile(os.Getenv("TANGERINE_LOCAL_MUTATION_PROFILE"))
	requireListening(t, e)
	var profile map[string]any
	requireListening(t, json.Unmarshal(raw, &profile))
	selected := c["llm_profiles"].([]any)[0].(map[string]any)
	for k, v := range profile {
		selected[k] = v
	}
	mapRaw, e := os.ReadFile(os.Getenv("TANGERINE_LOCAL_MAPPING_PROFILE"))
	requireListening(t, e)
	var mapProfile map[string]any
	requireListening(t, json.Unmarshal(mapRaw, &mapProfile))
	c["llm_profiles"] = append(c["llm_profiles"].([]any), mapProfile)
	for _, stage := range []string{"claim_mapping", "mapping_audit"} {
		c["stage_profiles"].(map[string]any)[stage] = mapProfile["id"]
	}
	c["mapping_audit_enabled"] = wantReason == "accepted"
	c["llm_lab_capture_content"] = true
	c["llm_lab_trace_enabled"] = true
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = f.s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	f.attempt = f.start(t)
	_, _, e = f.s.Store.WriteAnswer(ctx, f.attempt, uuid.NewString(), 0, answerPacket(answer, "en"), true)
	requireListening(t, e)
	dir := filepath.Join(os.Getenv("TANGERINE_INTERPRETATION_EVIDENCE"), t.Name())
	requireListening(t, os.MkdirAll(dir, 0700))
	defer func() {
		rows, e := f.s.Store.DB.Query(ctx, "SELECT asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND a.state='linked'")
		requireListening(t, e)
		ids := []string{}
		for rows.Next() {
			var id string
			requireListening(t, rows.Scan(&id))
			ids = append(ids, id)
		}
		rows.Close()
		for _, id := range ids {
			b, e := f.s.Store.ReadAsset(ctx, id)
			requireListening(t, e)
			requireListening(t, os.WriteFile(filepath.Join(dir, "diagnostic-"+id+".json"), b, 0600))
		}
	}()
	dispatch, e := os.Create(filepath.Join(dir, "dispatch-observations.jsonl"))
	requireListening(t, e)
	defer dispatch.Close()
	transport := &http.Transport{}
	defer transport.CloseIdleConnections()
	client := &http.Client{Transport: interpretationTrip(func(r *http.Request) (*http.Response, error) {
		body, e := io.ReadAll(r.Body)
		if e != nil {
			return nil, e
		}
		r.Body = io.NopCloser(bytes.NewReader(body))
		response, e := transport.RoundTrip(r)
		event := map[string]any{"wire_request_sha256": contracts.Digest(body), "endpoint": r.URL.String(), "billing_mode": "local", "fixture_response": false}
		if e == nil {
			b, err := io.ReadAll(response.Body)
			response.Body.Close()
			response.Body = io.NopCloser(bytes.NewReader(b))
			event["wire_response_sha256"] = contracts.Digest(b)
			event["http_status"] = response.StatusCode
			if err != nil {
				e = err
			}
		}
		_ = json.NewEncoder(dispatch).Encode(event)
		return response, e
	})}
	r, e := f.s.Store.Attempt(ctx, f.attempt)
	requireListening(t, e)
	state, e := f.s.InterpretAttempt(ctx, f.attempt, uuid.NewString(), 1, r.Attempt["answer_utf8_sha256"].(string), r.Attempt["configuration_sha256"].(string), client)
	requireListening(t, os.WriteFile(filepath.Join(dir, "state.json"), mustJSON(state), 0600))
	if e != nil {
		t.Fatal("actual local interpretation", e)
	}
	var m SemanticMapping
	requireListening(t, f.s.Store.readInterpretationJSON(ctx, *state.Mapping, &m))
	requireListening(t, os.WriteFile(filepath.Join(dir, "mapping.json"), mustJSON(m), 0600))
	var x CanonicalExtraction
	requireListening(t, f.s.Store.readInterpretationJSON(ctx, *state.Extraction, &x))
	requireListening(t, os.WriteFile(filepath.Join(dir, "extraction.json"), mustJSON(x), 0600))
	// Independent truth: cafe open is the singular agreement error; opens fixes it.
	found := false
	for _, d := range m.Groups {
		if optionalID(d.Unit) == "e1" && d.Stance == "assert_error" {
			found = true
			if d.Correction.Status != wantCorrection || d.Explanation.Status != wantReason {
				t.Fatalf("components: %+v", d)
			}
		}
	}
	if !found {
		t.Fatal("missed authored agreement target", m)
	}
	if wantReason == "rejected" {
		supportedFailure := false
		for _, g := range m.Groups {
			for _, a := range g.Explanation.Additional {
				supportedFailure = supportedFailure || (a.Judgment == "unsupported" && a.Reason != "")
			}
		}
		if !supportedFailure {
			t.Fatal("false reason lacks actual contextual unsupported-assertion finding", m)
		}
	}
	requireListening(t, os.WriteFile(filepath.Join(dir, "expectation.json"), mustJSON(map[string]any{"answer": answer, "detection": "matched_error", "correction_status": wantCorrection, "explanation_status": wantReason, "independent_fixture": "The cafe open tomorrow -> The cafe opens tomorrow; singular present agreement, false universal-s rule rejected"}), 0600))
}
func TestLocalInterpretationCorrectionPositive(t *testing.T) {
	observeLocalInterpretation(t, "The verb open should be opens.", "accepted", "not_supplied")
}
func TestLocalInterpretationExplanationPositive(t *testing.T) {
	observeLocalInterpretation(t, "The verb open should be opens because the singular subject cafe requires third-person singular agreement.", "accepted", "accepted")
}
func TestLocalInterpretationFalseCorrectionNegative(t *testing.T) {
	observeLocalInterpretation(t, "The verb open is wrong. Change it to opening.", "rejected", "not_supplied")
}
func TestLocalInterpretationFalseExplanationNegative(t *testing.T) {
	observeLocalInterpretation(t, "The verb open should be opens because every English verb must always end in s.", "accepted", "rejected")
}
