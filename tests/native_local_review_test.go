package app

// Actual local review/adjudication; source cases and baseline semantic findings
// are constructed. Native arithmetic, persistence, dispatch and Lab capture are real.
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

func observeLocalReview(t *testing.T, purpose, mode, statement, expected, reference string) {
	f := reviewFixture(t, mode)
	ctx := context.Background()
	c, rev, e := f.s.Store.Configuration(ctx)
	requireListening(t, e)
	raw, e := os.ReadFile(os.Getenv("TANGERINE_LOCAL_MAPPING_PROFILE"))
	requireListening(t, e)
	var local map[string]any
	requireListening(t, json.Unmarshal(raw, &local))
	base := reviewClone(c["llm_profiles"].([]any)[0])
	for k, v := range local {
		base[k] = v
	}
	local = base
	local["id"] = "actual-local-review"
	local["roles"] = []any{"case_review", "adjudication"}
	c["llm_profiles"] = append(c["llm_profiles"].([]any), local)
	for _, role := range []string{"case_review", "adjudication"} {
		c["stage_profiles"].(map[string]any)[role] = "actual-local-review"
	}
	c["llm_lab_capture_content"] = true
	c["llm_lab_trace_enabled"] = true
	for _, key := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, key)
	}
	_, _, e = f.s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	if mode == "rationale-key" {
		doc, err := f.s.Store.ReadDocument(ctx, f.id)
		requireListening(t, err)
		var key map[string]any
		requireListening(t, json.Unmarshal(doc.Payload, &key))
		u := key["units"].([]any)[0].(map[string]any)
		u["rationale"] = "Every English verb always ends in s."
		for _, v := range u["rationale_required_propositions"].([]any) {
			v.(map[string]any)["description"] = "Every English verb always ends in s."
		}
		key["case_version_id"] = uuid.NewString()
		content := map[string]any{}
		for _, k := range []string{"public_context", "variety_policy", "audio", "speakers", "utterances", "units", "taxonomy_version", "verification_policy_version"} {
			content[k] = key[k]
		}
		key["case_sha256"] = lab.Hash(content)
		source, err := f.s.Store.saveGroundTruth(ctx, key)
		requireListening(t, err)
		tx, err := beginWrite(ctx, f.s.Store)
		requireListening(t, err)
		defer tx.Rollback(ctx)
		f.id, err = f.s.Store.publishListeningCase(ctx, tx, source, map[string]any{"detection": true, "correction": true, "classification": false, "explanation": false}, "Constructed rationale defect", "monologue")
		requireListening(t, err)
		requireListening(t, tx.Commit(ctx))
		f.sha = key["case_sha256"].(string)
	}
	if purpose != "case_review" {
		f.remaps.Store(0)
		f.attempt = f.start(t)
		answer := "Use opens."
		if mode == "false-reason" {
			f.mode.Store("scoring-false-reason")
			answer = "Use opens because every English verb always ends in s."
		}
		_, _, e = f.s.Store.WriteAnswer(ctx, f.attempt, uuid.NewString(), 0, answerPacket(answer, "en"), true)
		requireListening(t, e)
		_, e = f.interpret(t, uuid.NewString())
		requireListening(t, e)
	}
	dir := filepath.Join(os.Getenv("TANGERINE_INTERPRETATION_EVIDENCE"), t.Name())
	requireListening(t, os.MkdirAll(dir, 0700))
	defer func() {
		rows, err := f.s.Store.DB.Query(ctx, "SELECT asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND a.state='linked'")
		requireListening(t, err)
		ids := []string{}
		for rows.Next() {
			var id string
			requireListening(t, rows.Scan(&id))
			ids = append(ids, id)
		}
		rows.Close()
		for _, id := range ids {
			data, err := f.s.Store.ReadAsset(ctx, id)
			requireListening(t, err)
			requireListening(t, os.WriteFile(filepath.Join(dir, "diagnostic-"+id+".json"), data, 0600))
		}
	}()
	record, e := f.s.Store.Attempt(ctx, f.attempt)
	requireListening(t, e)
	request := ReviewRun{Purpose: purpose, Case: f.id, Statement: statement}
	if purpose != "case_review" {
		request.Attempt = f.attempt
		request.BaseResult = record.Context["result_id"].(string)
	} else {
		request.AudioSHA = f.audioSHA
	}
	r, e := f.s.CreateReview(ctx, request, uuid.NewString())
	requireListening(t, e)
	requireListening(t, os.WriteFile(filepath.Join(dir, "expectation.json"), mustJSON(map[string]any{"expected_resolution": expected, "semantic_reference": reference, "purpose": purpose, "origin": "independent authored source reference", "primary": "100.0"}), 0600))
	dispatch, e := os.Create(filepath.Join(dir, "dispatch-observations.jsonl"))
	requireListening(t, e)
	defer dispatch.Close()
	transport := &http.Transport{}
	defer transport.CloseIdleConnections()
	client := &http.Client{Transport: scoringTrip(func(request *http.Request) (*http.Response, error) {
		if request.URL.String() != "http://127.0.0.1:11434/v1/responses" {
			return transport.RoundTrip(request)
		}
		body, err := io.ReadAll(request.Body)
		if err != nil {
			return nil, err
		}
		request.Body = io.NopCloser(bytes.NewReader(body))
		response, err := transport.RoundTrip(request)
		event := map[string]any{"wire_request_sha256": contracts.Digest(body), "endpoint": request.URL.String(), "billing_mode": "local", "fixture_response": false}
		if err == nil {
			data, readErr := io.ReadAll(response.Body)
			response.Body.Close()
			response.Body = io.NopCloser(bytes.NewReader(data))
			event["wire_response_sha256"] = contracts.Digest(data)
			event["http_status"] = response.StatusCode
			if readErr != nil {
				err = readErr
			}
		}
		_ = json.NewEncoder(dispatch).Encode(event)
		return response, err
	})}
	r, e = f.s.RunReview(ctx, r.ID, uuid.NewString(), r.Revision, client)
	requireListening(t, os.WriteFile(filepath.Join(dir, "state.json"), mustJSON(r), 0600))
	if e != nil {
		t.Fatalf("actual local review failed: %v; state at %s", e, dir)
	}
	var output map[string]any
	requireListening(t, f.s.Store.readInterpretationJSON(ctx, r.Output, &output))
	requireListening(t, os.WriteFile(filepath.Join(dir, "output.json"), mustJSON(output), 0600))
	if r.Status != "complete" || expected != "supported_or_insufficient" && r.Resolution != expected || expected == "supported_or_insufficient" && r.Resolution != "supported" && r.Resolution != "insufficient_evidence" {
		t.Fatalf("expected %s, actual %s", expected, r.Resolution)
	}
	if strings.TrimSpace(output["reason"].(string)) == "" {
		t.Fatal("missing actual contextual explanation")
	}
	if purpose != "case_review" {
		selected, e := f.s.Store.Attempt(ctx, f.attempt)
		requireListening(t, e)
		value, e := f.s.Store.readScoringResult(ctx, selected.Context["result_id"].(string))
		requireListening(t, e)
		requireListening(t, os.WriteFile(filepath.Join(dir, "result.json"), mustJSON(value), 0600))
		score := value["score"].(map[string]any)
		if score["composite"].(map[string]any)["display"] != "100.0" {
			t.Fatal("supported primary score changed", score["composite"])
		}
		if mode == "false-reason" && score["optional_explanation"].(map[string]any)["display"] != "0.0" {
			t.Fatal("false reason did not receive zero independent optional credit")
		}
	}
}
func TestLocalReviewCasePositive(t *testing.T) {
	observeLocalReview(t, "case_review", "supported", "", "supported", "The singular cafe requires opens; the textual key is sound. Do not invent measured sound or a human reviewer.")
}
func TestLocalReviewSoundDisputeNegative(t *testing.T) {
	observeLocalReview(t, "dispute", "supported", "I think a sound in this recording is wrong. There are no acoustic observations in the supplied data; please state what can actually be concluded.", "supported_or_insufficient", "No measured sound is supplied. Preserve supported text-based agreement and the saved answer; do not invent auditory confirmation.")
}
func TestLocalReviewMappingPositive(t *testing.T) {
	observeLocalReview(t, "dispute", "mapping", "My proposed opens correction is correct for the singular cafe. Please reconsider the rejected correction.", "mapping_defect", "Accept the actual opens repair; correct the initial mistaken rejection and restore primary100 on the same answer/key/audio.")
}
func TestLocalReviewWrongDisputeNegative(t *testing.T) {
	observeLocalReview(t, "dispute", "supported", "The correct answer should be opening instead of opens.", "supported", "Reject the proposed opening claim in context; keep the valid opens repair and original100 result.")
}
func TestLocalReviewKeyPositive(t *testing.T) {
	observeLocalReview(t, "dispute", "rationale-key", "The saved key rationale says every English verb always ends in s. Repair that incorrect rule while preserving the valid opens correction and detection.", "key_defect", "Repair only the overbroad rationale/rubric in a complete same-audio successor, with exact correspondence and independently preserved primary100.")
}
func TestLocalReviewFalseReasonNegative(t *testing.T) {
	observeLocalReview(t, "dispute", "false-reason", "I think my rule that every English verb always ends in s should receive full explanation credit.", "mapping_defect", "The actual listener supplied a false universal rule. Reject it with optional0 while keeping the valid opens correction and primary100.")
}
