package app

// Actual local feedback inference; independent authored semantic findings are
// constructed through the native interpretation fixture. No hosted model calls.
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
	"testing"
	"unicode"
)

type scoringTrip func(*http.Request) (*http.Response, error)

func (f scoringTrip) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }
func observeLocalScoring(t *testing.T, answer, mode, grade string, wantKind string, locale string) {
	f := scoringFixture(t, false)
	f.mode.Store(mode)
	ctx := context.Background()
	c, rev, e := f.s.Store.Configuration(ctx)
	requireListening(t, e)
	raw, e := os.ReadFile(os.Getenv("TANGERINE_LOCAL_MAPPING_PROFILE"))
	requireListening(t, e)
	var local map[string]any
	requireListening(t, json.Unmarshal(raw, &local))
	for _, v := range c["llm_profiles"].([]any) {
		p := v.(map[string]any)
		if p["id"] == "fixture-feedback-unselected" {
			for k, v := range local {
				p[k] = v
			}
		}
	}
	c["llm_lab_capture_content"] = true
	c["llm_lab_trace_enabled"] = true
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = f.s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	started, e := f.s.Store.StartAttempt(ctx, mustJSON(map[string]any{"case_version_id": f.id, "case_sha256": f.sha, "requested_language": locale}), uuid.NewString())
	requireListening(t, e)
	f.attempt = started["attempt_id"].(string)
	_, _, e = f.s.Store.WriteAnswer(ctx, f.attempt, uuid.NewString(), 0, answerPacket(answer, locale), true)
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
	client := &http.Client{Transport: scoringTrip(func(r *http.Request) (*http.Response, error) {
		if r.URL.String() != "http://127.0.0.1:11434/v1/responses" {
			return transport.RoundTrip(r)
		}
		b, e := io.ReadAll(r.Body)
		if e != nil {
			return nil, e
		}
		r.Body = io.NopCloser(bytes.NewReader(b))
		response, e := transport.RoundTrip(r)
		event := map[string]any{"wire_request_sha256": contracts.Digest(b), "endpoint": r.URL.String(), "billing_mode": "local", "fixture_response": false}
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
	requireListening(t, e)
	envelope := f.envelope(t, state)
	requireListening(t, os.WriteFile(filepath.Join(dir, "result.json"), mustJSON(envelope), 0600))
	score := envelope["score"].(map[string]any)
	if score["composite"].(map[string]any)["display"] != grade || envelope["feedback_status"] != "complete" {
		t.Fatalf("expected grade%s and actual local feedback; status%v", grade, envelope["feedback_status"])
	}
	found := false
	for _, v := range envelope["feedback"].(map[string]any)["items"].([]any) {
		item := v.(map[string]any)
		if item["kind"] == wantKind && strings.TrimSpace(item["text"].(string)) != "" {
			found = true
		}
	}
	if locale == "ru" {
		cyrillic := false
		for _, v := range envelope["feedback"].(map[string]any)["items"].([]any) {
			cyrillic = cyrillic || strings.ContainsFunc(v.(map[string]any)["text"].(string), func(r rune) bool { return unicode.In(r, unicode.Cyrillic) })
		}
		if !cyrillic {
			t.Fatal("requested Russian prose is absent")
		}
	}
	if mode == "scoring-false-reason" && score["optional_explanation"].(map[string]any)["display"] != "0.0" {
		t.Fatal("false reason changed primary or gained reason credit")
	}
	if !found {
		t.Fatal("missing independently expected feedback subject", wantKind)
	}
	requireListening(t, os.WriteFile(filepath.Join(dir, "expectation.json"), mustJSON(map[string]any{"answer": answer, "grade": grade, "feedback_kind": wantKind, "semantic_fixture": "authored cafe agreement and supplied correction/reason", "actual_model_stage": "feedback"}), 0600))
}
func TestLocalScoringRepairPositive(t *testing.T) {
	observeLocalScoring(t, "Use opens.", "good", "100.0", "correction", "en")
}
func TestLocalScoringReasonPositive(t *testing.T) {
	observeLocalScoring(t, "Use opens because the cafe is singular.", "rubric-repair", "100.0", "explanation", "en")
}
func TestLocalScoringWrongRepairNegative(t *testing.T) {
	observeLocalScoring(t, "Use opening.", "scoring-wrong", "60.0", "correction", "en")
}
func TestLocalScoringMissNegative(t *testing.T) {
	observeLocalScoring(t, "", "good", "0.0", "missed", "en")
}

func TestLocalScoringRussianPositive(t *testing.T) {
	observeLocalScoring(t, "Use opens.", "good", "100.0", "correction", "ru")
}
func TestLocalScoringFalseReasonNegative(t *testing.T) {
	observeLocalScoring(t, "Use opens because every English verb always ends in s.", "scoring-false-reason", "100.0", "explanation", "en")
}
