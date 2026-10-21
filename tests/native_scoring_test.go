package app

// Only model transport is constructed. Numeric/persistence/HTTP owners are real.
import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync/atomic"
	"tangerine.local/api/internal/contracts"
	"testing"
	"time"
)

type scoringNative struct {
	*nativeInterpretation
	feedback      *httptest.Server
	feedbackCalls atomic.Int32
	bad           atomic.Bool
	inputs        []map[string]any
	sourceViews   []any
}

func scoringFixture(t *testing.T, bad bool) *scoringNative {
	f := &scoringNative{nativeInterpretation: interpretationNative(t, "good")}
	f.bad.Store(bad)
	f.feedback = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		f.feedbackCalls.Add(1)
		if f.currentMode() == "feedback-blocked" {
			f.once.Do(func() { close(f.entered) })
			select {
			case <-f.release:
			case <-r.Context().Done():
				return
			}
		}

		b, _ := io.ReadAll(r.Body)
		var wire map[string]any
		_ = json.Unmarshal(b, &wire)
		var input map[string]any
		var sourceView map[string]any
		for _, x := range wire["input"].([]any) {
			s := x.(map[string]any)["content"].(string)
			if strings.HasPrefix(s, "prior_decisions: ") {
				_ = json.Unmarshal([]byte(strings.TrimPrefix(s, "prior_decisions: ")), &sourceView)
			}
			if strings.HasPrefix(s, "Complete stage input: ") {
				_ = json.Unmarshal([]byte(strings.TrimPrefix(s, "Complete stage input: ")), &input)
			}
		}
		f.inputs = append(f.inputs, input)
		f.sourceViews = append(f.sourceViews, sourceView["listener_answer_assessments"])
		if f.bad.Load() || f.currentMode() == "feedback-failure" {
			w.WriteHeader(500)
			return
		}
		if strings.HasPrefix(f.currentMode(), "feedback-empty-") {
			guided := false
			for _, message := range wire["input"].([]any) {
				content, _ := message.(map[string]any)["content"].(string)
				var repair map[string]any
				if json.Unmarshal([]byte(content), &repair) == nil {
					detail, _ := repair["validation_detail"].(string)
					guided = guided || strings.TrimSpace(detail) != ""
				}
			}
			if f.currentMode() == "feedback-empty-always" || f.feedbackCalls.Load() == 1 || !guided {
				_ = json.NewEncoder(w).Encode(map[string]any{"id": "constructed-empty-feedback", "status": "completed", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": ""}}}}})
				return
			}
		}

		key := input["ground_truth"].(map[string]any)
		unit := key["units"].([]any)[0].(map[string]any)["id"].(string)
		item := func(kind, text string, ds []any) map[string]any {
			return map[string]any{"kind": kind, "text": text, "unit_ids": []any{unit}, "decision_ids": ds, "issue_ids": []any{}, "rationale_ids": []any{}, "grounding_status": "llm_grounded", "status": "final"}
		}
		decisions := input["decisions"].(map[string]any)["decisions"].([]any)
		ids := []any{}
		if len(decisions) > 0 {
			ids = append(ids, decisions[0].(map[string]any)["claim_id"])
		}
		items := []any{item("detected", "The listener found the agreement mistake.", ids), item("correction", "Opens is the correct present-tense repair for the singular cafe.", ids), item("recommendation", "New practice example: The museum opens at nine. Listen for the singular subject and the verb ending.", ids)}
		items[2].(map[string]any)["grounding_status"] = "practice_recommendation"
		if len(decisions) > 0 {
			judgment := decisions[0].(map[string]any)["explanation"].(map[string]any)
			if judgment["supplied"] == true {
				text := "The singular cafe requires third-person singular present agreement."
				if judgment["status"] == "rejected" {
					text = "The universal rule is false: agreement applies to third-person singular present forms, not every verb."
				}
				items = append(items, item("explanation", text, ids))
			}
		}

		if strings.HasPrefix(f.currentMode(), "scoring-offkey") {
			items = []any{item("missed", "The actual agreement mistake remains: open should be opens.", []any{}), item("recommendation", "New practice: The shop opens at nine.", []any{})}
			items[1].(map[string]any)["grounding_status"] = "practice_recommendation"
			if f.currentMode() != "scoring-offkey-omitted" {
				finding := item("false_positive", "Cafe is acceptable. Your proposed replacement is unnecessary and does not repair the agreement error.", ids)
				finding["unit_ids"] = []any{}
				items = append(items, finding)
			}
		}

		out := map[string]any{"schema_version": "2.0.0", "language": input["requested_language"], "items": items}
		payload := string(mustJSON(out))
		if f.currentMode() == "feedback-identical-field" {
			payload = strings.Replace(payload, `"issue_ids":[]`, `"issue_ids":[],"issue_ids":[]`, 1)
		}
		if f.currentMode() == "feedback-conflicting-field" {
			payload = strings.Replace(payload, `"text":"The listener found the agreement mistake."`, `"text":"The listener did not find the mistake.","text":"The listener found the agreement mistake."`, 1)
		}
		_ = json.NewEncoder(w).Encode(map[string]any{"id": "constructed-feedback", "object": "response", "status": "completed", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": payload}}}}})
	}))
	t.Cleanup(f.feedback.Close)
	ctx := context.Background()
	c, rev, e := f.s.Store.Configuration(ctx)
	requireListening(t, e)
	var p map[string]any
	for _, v := range c["llm_profiles"].([]any) {
		row := v.(map[string]any)
		if row["id"] == "fixture-feedback-unselected" {
			p = row
		}
	}
	p["model"] = "constructed-feedback"
	p["endpoint"] = f.feedback.URL + "/v1/responses"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = f.s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	f.attempt = f.start(t)
	_, _, e = f.s.Store.WriteAnswer(ctx, f.attempt, uuid.NewString(), 0, answerPacket("Use opens.", "en"), true)
	requireListening(t, e)
	return f
}
func (f *scoringNative) envelope(t *testing.T, state InterpretationState) map[string]any {
	t.Helper()
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	v, e := f.s.Store.interpretationEnvelope(context.Background(), r, &state)
	requireListening(t, e)
	raw := mustJSON(v)
	_, _, e = contracts.Validate("result-envelope", "2.0.0", raw)
	requireListening(t, e)
	return v
}
func TestNativeScoringCompletePositive(t *testing.T) {
	f := scoringFixture(t, false)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	v := f.envelope(t, state)
	score := v["score"].(map[string]any)
	if v["status"] != "complete" || v["feedback_status"] != "complete" || score["composite"].(map[string]any)["display"] != "100.0" || f.feedbackCalls.Load() != 1 {
		t.Fatal(v)
	}
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if r.Attempt["state"] != "completed" || r.Context["result_id"] != v["result_id"] {
		t.Fatal(r)
	}
}
func TestNativeScoringFeedbackFailureNegative(t *testing.T) {
	f := scoringFixture(t, true)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	v := f.envelope(t, state)
	if v["feedback_status"] != "unavailable" || v["retry_operation"] != "retry_feedback" || v["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" {
		t.Fatal(v)
	}
}
func TestNativeScoringRetryPositive(t *testing.T) {
	f := scoringFixture(t, true)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	before := f.envelope(t, state)
	score := string(mustJSON(before["score"]))
	f.bad.Store(false)
	state, e = f.interpret(t, uuid.NewString())
	requireListening(t, e)
	after := f.envelope(t, state)
	if string(mustJSON(after["score"])) != score || after["feedback_status"] != "complete" || f.extracts.Load() != 1 || f.maps.Load() != 1 || len(after["result_revision_ids"].([]any)) != 2 {
		t.Fatal(after)
	}
}
func TestNativeScoringReadNoCallNegative(t *testing.T) {
	f := scoringFixture(t, false)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	before := f.calls.Load()
	for i := 0; i < 3; i++ {
		_ = f.envelope(t, state)
	}
	if f.calls.Load() != before || f.feedbackCalls.Load() != 1 {
		t.Fatal("read dispatched")
	}
}
func TestNativeScoringRestartPositive(t *testing.T) {
	f := scoringFixture(t, false)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	before := f.envelope(t, state)
	pool, e := pgxpool.New(context.Background(), f.s.Store.DB.Config().ConnString())
	requireListening(t, e)
	defer pool.Close()
	f.s = NewServer(&Storage{DB: pool, Media: f.s.Store.Media, Bucket: f.s.Store.Bucket}, f.s.Origin, "")
	saved, e := f.s.Store.interpretationState(context.Background(), f.attempt)
	requireListening(t, e)
	after := f.envelope(t, *saved)
	if string(mustJSON(before)) != string(mustJSON(after)) {
		t.Fatal("restart changed result")
	}
}
func TestNativeScoringReplayNegative(t *testing.T) {
	f := scoringFixture(t, false)
	key := uuid.NewString()
	state, e := f.interpret(t, key)
	requireListening(t, e)
	before := f.envelope(t, state)
	record, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	next, e := f.s.InterpretAttempt(context.Background(), f.attempt, key, 1, record.Attempt["answer_utf8_sha256"].(string), record.Attempt["configuration_sha256"].(string), f.model.Client())
	requireListening(t, e)
	if *next.Result != *state.Result || f.feedbackCalls.Load() != 1 || before["result_id"] != *next.Result {
		t.Fatal(next)
	}
}
func TestNativeScoringContextPositive(t *testing.T) {
	f := scoringFixture(t, false)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	v := f.envelope(t, state)
	x := f.inputs[0]
	if x["score_result"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" || x["ground_truth"] == nil || x["extraction"] == nil || x["result_id"] == nil || v["feedback"].(map[string]any)["receipt_id"] == nil {
		t.Fatal(x)
	}
}
func TestNativeScoringUnknownReferenceNegative(t *testing.T) {
	f := scoringFixture(t, false)
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	resources, e := f.s.Store.interpretationResources(context.Background(), r)
	requireListening(t, e)
	_, e = admitFeedback(mustJSON(map[string]any{"language": "en", "items": []any{map[string]any{"unit_ids": []any{"fake"}, "decision_ids": []any{}, "issue_ids": []any{}, "rationale_ids": []any{}}}}), r, resources, SemanticMapping{}, map[string]any{"issues": []any{}})
	if e == nil {
		t.Fatal("invented unit admitted")
	}
}
func TestNativeScoringBeforeFeedbackPositive(t *testing.T) {
	f := scoringFixture(t, false)
	f.mode.Store("feedback-blocked")
	done := make(chan error, 1)
	go func() { _, e := f.interpret(t, uuid.NewString()); done <- e }()
	select {
	case <-f.entered:
	case e := <-done:
		t.Fatal(e)
	case <-time.After(30 * time.Second):
		t.Fatal("feedback boundary not reached")
	}
	saved, e := f.s.Store.interpretationState(context.Background(), f.attempt)
	requireListening(t, e)
	if saved.Result == nil {
		close(f.release)
		t.Fatal("score not durable before feedback")
	}
	result, e := f.s.Store.readScoringResult(context.Background(), *saved.Result)
	requireListening(t, e)
	if result["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" {
		close(f.release)
		t.Fatal("incorrect early score")
	}
	close(f.release)
	requireListening(t, <-done)
}
func TestNativeScoringNoScoreNegative(t *testing.T) {
	f := scoringFixture(t, false)
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	body := string(mustJSON(map[string]any{"answer_sha256": r.Attempt["answer_utf8_sha256"], "configuration_sha256": r.Attempt["configuration_sha256"]}))
	w := f.request("POST", "/api/v1/attempts/"+f.attempt+":retry-feedback", body, uuid.NewString(), "1")
	if w.Code != 409 || f.calls.Load() != 0 || f.feedbackCalls.Load() != 0 {
		t.Fatal(w.Code, w.Body.String())
	}
}
func TestNativeScoringHTTPFeedbackPositive(t *testing.T) {
	f := scoringFixture(t, true)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	v := f.envelope(t, state)
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	body := string(mustJSON(map[string]any{"answer_sha256": r.Attempt["answer_utf8_sha256"], "configuration_sha256": r.Attempt["configuration_sha256"]}))
	f.bad.Store(false)
	w := f.request("POST", "/api/v1/attempts/"+f.attempt+":retry-feedback", body, uuid.NewString(), fmt.Sprint(r.Attempt["revision"]))
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	var after map[string]any
	requireListening(t, json.Unmarshal(w.Body.Bytes(), &after))
	if string(mustJSON(after["score"])) != string(mustJSON(v["score"])) || after["feedback_status"] != "complete" || f.extracts.Load() != 1 || f.maps.Load() != 1 {
		t.Fatal("feedback retry regraded")
	}
}
func TestNativeScoringLateNegative(t *testing.T) {
	f := scoringFixture(t, false)
	f.mode.Store("feedback-blocked")
	done := make(chan error, 1)
	go func() { _, e := f.interpret(t, uuid.NewString()); done <- e }()
	select {
	case <-f.entered:
	case e := <-done:
		t.Fatal(e)
	case <-time.After(30 * time.Second):
		t.Fatal("feedback boundary")
	}
	saved, e := f.s.Store.interpretationState(context.Background(), f.attempt)
	requireListening(t, e)
	original := *saved.Result
	_, e = f.s.Store.DB.Exec(context.Background(), "UPDATE interpretation_checkpoint SET deadline_at=clock_timestamp()-interval '1 second' WHERE attempt_id=$1", f.attempt)
	requireListening(t, e)
	close(f.release)
	e = <-done
	if !errors.Is(e, ErrEvaluationLease) {
		t.Fatal(e)
	}
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if r.Context["result_id"] != original || r.Attempt["answer_text"] != "Use opens." || r.Attempt["feedback_status"] == "complete" {
		t.Fatalf("late feedback: result=%v expected=%s answer=%q feedback_status=%v", r.Context["result_id"], original, r.Attempt["answer_text"], r.Attempt["feedback_status"])
	}
}
func TestNativeScoringReferencesPositive(t *testing.T) {
	f := scoringFixture(t, true)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	v := f.envelope(t, state)
	items := v["score"].(map[string]any)["items"].([]any)
	ref := items[0].(map[string]any)["reference"].(map[string]any)
	if len(ref["target_texts"].([]any)) == 0 || len(ref["repairs"].([]any)) == 0 || len(ref["audio_intervals"].([]any)) == 0 || v["interpretation"] == nil {
		t.Fatal("saved result lost key/source detail")
	}
}
func TestNativeScoringReadNoMediaNegative(t *testing.T) {
	f := scoringFixture(t, false)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	f.s.Store.Media = nil
	v := f.envelope(t, state)
	if v["score"] == nil || v["interpretation"] == nil || f.feedbackCalls.Load() != 1 {
		t.Fatal("numeric result depends on media or fresh inference")
	}
}
func unavailableScoringAudit(t *testing.T) *scoringNative {
	f := scoringFixture(t, true)
	ctx := context.Background()
	c, rev, e := f.s.Store.Configuration(ctx)
	requireListening(t, e)
	profile := map[string]any{}
	for k, v := range c["llm_profiles"].([]any)[0].(map[string]any) {
		profile[k] = v
	}
	profile["id"] = "unavailable-audit"
	profile["roles"] = []any{"mapping_audit"}
	profile["model"] = "unselected"
	c["llm_profiles"] = append(c["llm_profiles"].([]any), profile)
	c["mapping_audit_enabled"] = true
	c["stage_profiles"].(map[string]any)["mapping_audit"] = "unavailable-audit"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = f.s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	f.attempt = f.start(t)
	_, _, e = f.s.Store.WriteAnswer(ctx, f.attempt, uuid.NewString(), 0, answerPacket("Use opens.", "en"), true)
	requireListening(t, e)
	return f
}
func TestNativeScoringAuditStatusPositive(t *testing.T) {
	f := unavailableScoringAudit(t)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	v := f.envelope(t, state)
	if v["status"] != "complete" || len(v["issues"].([]any)) != 0 || v["interpretation"].(map[string]any)["audit_status"] != "failed" {
		t.Fatal("optional diagnostic became score uncertainty")
	}
}
func TestNativeScoringFeedbackOnlyNegative(t *testing.T) {
	f := unavailableScoringAudit(t)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	before := f.envelope(t, state)
	f.bad.Store(false)
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	body := string(mustJSON(map[string]any{"answer_sha256": r.Attempt["answer_utf8_sha256"], "configuration_sha256": r.Attempt["configuration_sha256"]}))
	w := f.request("POST", "/api/v1/attempts/"+f.attempt+":retry-feedback", body, uuid.NewString(), fmt.Sprint(r.Attempt["revision"]))
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	saved, e := f.s.Store.interpretationState(context.Background(), f.attempt)
	requireListening(t, e)
	stages := []InterpretationStage{}
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), saved.Stages, &stages))
	audits := 0
	for _, s := range stages {
		if s.Stage == "mapping_audit" {
			audits++
		}
	}
	var after map[string]any
	requireListening(t, json.Unmarshal(w.Body.Bytes(), &after))
	if audits != 1 || f.extracts.Load() != 1 || f.maps.Load() != 1 || string(mustJSON(before["score"])) != string(mustJSON(after["score"])) || after["feedback_status"] != "complete" {
		t.Fatal("feedback-only retry repeated a semantic/audit stage")
	}
}
func nativeScoredReason(t *testing.T, mode, answer string) map[string]any {
	f := scoringFixture(t, false)
	f.mode.Store(mode)
	f.attempt = f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), f.attempt, uuid.NewString(), 0, answerPacket(answer, "en"), true)
	requireListening(t, e)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	return f.envelope(t, state)
}
func TestNativeScoringExplanationPositive(t *testing.T) {
	v := nativeScoredReason(t, "rubric-repair", "Use opens because the cafe is singular.")
	s := v["score"].(map[string]any)
	if s["composite"].(map[string]any)["display"] != "100.0" || s["optional_explanation"].(map[string]any)["display"] != "100.0" || v["feedback_status"] != "complete" {
		t.Fatal("supported reason missing from independent score")
	}
}
func TestNativeScoringFalseReasonNegative(t *testing.T) {
	v := nativeScoredReason(t, "scoring-false-reason", "Use opens because every English verb always ends in s.")
	s := v["score"].(map[string]any)
	if s["composite"].(map[string]any)["display"] != "100.0" || s["optional_explanation"].(map[string]any)["display"] != "0.0" || v["feedback_status"] != "complete" {
		t.Fatal("false reason altered valid correction or feedback")
	}
}
func installScoringWriteFault(t *testing.T, f *scoringNative) {
	t.Helper()
	_, e := f.s.Store.DB.Exec(context.Background(), `CREATE FUNCTION reject_feedback_result() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.kind='result-envelope' AND NEW.payload->>'feedback_status'='complete' THEN RAISE EXCEPTION 'test-owned feedback write failure'; END IF; RETURN NEW; END $$`)
	requireListening(t, e)
	_, e = f.s.Store.DB.Exec(context.Background(), `CREATE TRIGGER reject_feedback_result BEFORE INSERT ON document FOR EACH ROW EXECUTE FUNCTION reject_feedback_result()`)
	requireListening(t, e)
}
func scoringWriteFault(t *testing.T) (*scoringNative, map[string]any) {
	f := scoringFixture(t, false)
	f.attempt = f.start(t)
	installScoringWriteFault(t, f)
	w := f.request("POST", "/api/v1/attempts/"+f.attempt+":submit", string(answerPacket("Use opens.", "en")), uuid.NewString(), "0")
	if w.Code != 503 {
		t.Fatal(w.Code, w.Body.String())
	}
	var v map[string]any
	requireListening(t, json.Unmarshal(w.Body.Bytes(), &v))
	return f, v
}
func TestNativeScoringWriteFailureNegative(t *testing.T) {
	f, v := scoringWriteFault(t)
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if r.Attempt["answer_text"] != "Use opens." || v["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" || v["feedback_status"] != "not_started" {
		t.Fatal("post-score failure lost the submission/score")
	}
}
func TestNativeScoringWriteRecoveryPositive(t *testing.T) {
	f, before := scoringWriteFault(t)
	_, e := f.s.Store.DB.Exec(context.Background(), "DROP TRIGGER reject_feedback_result ON document")
	requireListening(t, e)
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	body := string(mustJSON(map[string]any{"answer_sha256": r.Attempt["answer_utf8_sha256"], "configuration_sha256": r.Attempt["configuration_sha256"]}))
	w := f.request("POST", "/api/v1/attempts/"+f.attempt+":retry-feedback", body, uuid.NewString(), fmt.Sprint(r.Attempt["revision"]))
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	var after map[string]any
	requireListening(t, json.Unmarshal(w.Body.Bytes(), &after))
	if string(mustJSON(before["score"])) != string(mustJSON(after["score"])) || after["feedback_status"] != "complete" || f.extracts.Load() != 1 || f.maps.Load() != 1 {
		t.Fatal("write recovery changed primary semantics")
	}
}

func nativeOffkeyScoring(t *testing.T, omitted bool) {
	f := scoringFixture(t, false)
	mode, answer := "scoring-offkey-correction", "Use coffee."
	if omitted {
		mode, answer = "scoring-offkey-omitted", "The word cafe is incorrect."
	}
	f.mode.Store(mode)
	f.attempt = f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), f.attempt, uuid.NewString(), 0, answerPacket(answer, "en"), true)
	requireListening(t, e)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	result := f.envelope(t, state)
	score := result["score"].(map[string]any)
	counts := score["counts"].(map[string]any)
	if score["composite"].(map[string]any)["display"] != "0.0" || counts["fp"] != float64(1) || counts["fn"] != float64(1) {
		t.Fatal(score)
	}
	if omitted {
		if result["feedback_status"] != "unavailable" {
			t.Fatal("missing false-positive comment accepted", result)
		}
	} else {
		if result["feedback_status"] != "complete" {
			t.Fatal("combined off-key feedback rejected", result)
		}
		row := f.sourceViews[0].([]any)[0].(map[string]any)
		correction := row["correction"].(map[string]any)
		if row["listener_reports"].([]any)[0] != "Use coffee." || correction["source_texts"].([]any)[0] != "coffee" || correction["status"] != "rejected" {
			t.Fatal("actual feedback wire lost proposal roles", row)
		}
	}
}
func TestNativeScoringOffkeyPositive(t *testing.T)        { nativeOffkeyScoring(t, false) }
func TestNativeScoringOffkeyMissingNegative(t *testing.T) { nativeOffkeyScoring(t, true) }

func TestNativeScoringIdenticalFieldPositive(t *testing.T) {
	f := scoringFixture(t, false)
	f.mode.Store("feedback-identical-field")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	result := f.envelope(t, state)
	if result["feedback_status"] != "complete" || result["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" {
		t.Fatal(result)
	}
}
func TestNativeScoringConflictingFieldNegative(t *testing.T) {
	f := scoringFixture(t, false)
	f.mode.Store("feedback-conflicting-field")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	result := f.envelope(t, state)
	if result["feedback_status"] != "unavailable" || result["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" {
		t.Fatal("ambiguous model assertion accepted or score lost", result)
	}
}

func TestNativeScoringEmptyRepairPositive(t *testing.T) {
	f := scoringFixture(t, false)
	f.mode.Store("feedback-empty-first")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	result := f.envelope(t, state)
	if result["feedback_status"] != "complete" || f.feedbackCalls.Load() != 2 || result["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" {
		t.Fatal("missing stage-specific repair guidance", result, f.feedbackCalls.Load())
	}
}
func TestNativeScoringEmptyOutputNegative(t *testing.T) {
	f := scoringFixture(t, false)
	f.mode.Store("feedback-empty-always")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	result := f.envelope(t, state)
	if result["feedback_status"] != "unavailable" || f.feedbackCalls.Load() != 2 || result["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" {
		t.Fatal("blank feedback invented or repair unbounded", result, f.feedbackCalls.Load())
	}
}
