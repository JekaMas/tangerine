package app

// Only the remote model protocol is constructed. All controller, PostgreSQL,
// MinIO, exact scoring, HTTP, version publication and evidence owners are real.
import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"io"
	"math/rand"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"tangerine.local/api/internal/lab"
	"testing"
	"time"
)

type reviewNative struct {
	*scoringNative
	reviewModel         *httptest.Server
	reviewCalls, remaps atomic.Int32
	reviewMode          atomic.Value
	reviewPath          string
	reviewMu            sync.Mutex
	reviewInputs        []map[string]any
	block               chan struct{}
	arrived             chan struct{}
	blockOnce           sync.Once
}

func (f *reviewNative) modeReview() string {
	if f.reviewPath != "" {
		if b, e := os.ReadFile(f.reviewPath); e == nil {
			return strings.TrimSpace(string(b))
		}
	}
	return f.reviewMode.Load().(string)
}
func (f *reviewNative) reviewDecision(input map[string]any, claims []CanonicalClaim) map[string]any {
	key := input["ground_truth"].(map[string]any)
	u := key["units"].([]any)[0].(map[string]any)
	unit := u["id"].(string)
	option := u["corrections"].([]any)[0].(map[string]any)
	oid := option["id"].(string)
	decisions := []SemanticDecision{}
	for index, c := range claims {
		if index > 0 && index < len(key["units"].([]any)) {
			u = key["units"].([]any)[index].(map[string]any)
			unit = u["id"].(string)
			option = u["corrections"].([]any)[0].(map[string]any)
			oid = option["id"].(string)
		}
		unitID, optionID := unit, oid
		d := SemanticDecision{Claim: c.ID, Unit: &unitID, Decision: "matched_error", Reason: "supported", Correction: semanticEmpty(), Explanation: semanticEmpty(), Evidence: []string{}, Note: "The singular cafe requires opens."}
		if len(c.Corrections) > 0 {
			d.Correction.Supplied = true
			d.Correction.Option = &optionID
			d.Correction.Status = "accepted"
			for _, v := range option["required_propositions"].([]any) {
				d.Correction.Satisfied = append(d.Correction.Satisfied, v.(map[string]any)["id"].(string))
			}
		}
		if len(c.Explanations) > 0 {
			d.Explanation.Supplied = true
			d.Explanation.Status = "accepted"
			d.Explanation.Additional = []ComponentAssertion{{AnswerSpan: c.Explanations[0], Judgment: "supported", Reason: "The subject is singular."}}
			for _, v := range u["rationale_required_propositions"].([]any) {
				d.Explanation.Satisfied = append(d.Explanation.Satisfied, v.(map[string]any)["id"].(string))
			}
		}
		if index >= len(key["units"].([]any)) {
			d.Unit = nil
			d.Decision = "false_positive"
			d.Correction.Option = nil
			d.Correction.Status = "rejected"
			d.Correction.Satisfied = []string{}
			d.Correction.Additional = []ComponentAssertion{{AnswerSpan: c.Corrections[0], Judgment: "unsupported", Reason: "Constructed incomplete-key mapper error; retained for later adjudication."}}
		}
		decisions = append(decisions, d)
	}
	return map[string]any{"schema_version": "1.0.0", "decisions": decisions}
}
func reviewFixture(t *testing.T, mode string) *reviewNative {
	t.Helper()
	f := &reviewNative{scoringNative: scoringFixture(t, false), block: make(chan struct{}), arrived: make(chan struct{})}
	f.reviewMode.Store(mode)
	if mode == "omitted" {
		f.installOmitted(t)
	}
	f.reviewModel = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		body, _ := io.ReadAll(r.Body)
		var wire map[string]any
		_ = json.Unmarshal(body, &wire)
		var input map[string]any
		var claims []CanonicalClaim
		for _, v := range wire["input"].([]any) {
			text := v.(map[string]any)["content"].(string)
			if strings.Contains(text, "validation_detail") {
				t.Logf("Constructed protocol repair guidance: %s", text)
			}
			if strings.HasPrefix(text, "Complete stage input: ") {
				_ = json.Unmarshal([]byte(strings.TrimPrefix(text, "Complete stage input: ")), &input)
			}
			if strings.HasPrefix(text, "extraction: ") {
				var data struct {
					Claims []CanonicalClaim `json:"claims"`
				}
				_ = json.Unmarshal([]byte(strings.TrimPrefix(text, "extraction: ")), &data)
				claims = data.Claims
			}
		}
		mode := f.modeReview()
		var out any
		if input["purpose"] == nil && input["ground_truth"] == nil {
			text := input["answer_text"].(string)
			first := AnswerSpan{8, 13, "works"}
			second := AnswerSpan{21, 24, "are"}
			out = AnswerExtraction{Version: "2.0.0", Clauses: []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 14, text[:14]}, Stance: "assert_error", Correction: &first}, {LocalRef: "c1", Span: AnswerSpan{15, 24, text[15:]}, Stance: "assert_error", Correction: &second}}, Unparsed: []AnswerSpan{}, Coverage: []ClaimCoverage{}, Relations: []ClaimRelation{}}
		} else if input["purpose"] == nil {
			n := f.remaps.Add(1)
			if mode == "conditional-failure" && f.reviewCalls.Load() > 0 {
				w.WriteHeader(503)
				return
			}
			value := f.reviewDecision(input, claims)
			if mode == "mapping" && n == 1 {
				d := value["decisions"].([]SemanticDecision)[0]
				d.Correction.Option = nil
				d.Correction.Status = "rejected"
				d.Correction.Satisfied = []string{}
				d.Correction.Additional = []ComponentAssertion{{AnswerSpan: claims[0].Corrections[0], Judgment: "unsupported", Reason: "Constructed initial mapper mistake, corrected by the review fixture."}}
				value["decisions"] = []SemanticDecision{d}
			}
			if mode == "reason" && n == 1 {
				d := value["decisions"].([]SemanticDecision)[0]
				d.Explanation.Satisfied = []string{}
				value["decisions"] = []SemanticDecision{d}
			}
			out = value
		} else {
			f.reviewCalls.Add(1)
			f.reviewMu.Lock()
			f.reviewInputs = append(f.reviewInputs, input)
			f.reviewMu.Unlock()
			if mode == "failure" {
				w.WriteHeader(503)
				return
			}
			if mode == "blocked" {
				f.blockOnce.Do(func() { close(f.arrived) })
				select {
				case <-f.block:
				case <-r.Context().Done():
					return
				}
			}
			key := input["ground_truth"].(map[string]any)
			judgments := []any{}
			for _, v := range key["units"].([]any) {
				u := v.(map[string]any)
				judgments = append(judgments, map[string]any{"unit_id": u["id"], "taxonomy_id": u["primary_taxonomy_id"], "judgment": "true_error", "confirmation": "inferred", "evidence_ids": []any{}, "reason": "The singular cafe requires opens in the present context."})
			}
			value := map[string]any{"schema_version": "2.0.0", "resolution": "supported", "unit_judgments": judgments, "decisions": nil, "issues": []any{}, "reason": "The saved agreement key is supported by the unchanged text.", "key_repair": nil}
			if mode == "missing-unit" {
				value["unit_judgments"] = []any{}
			}
			if mode == "insufficient" {
				value["resolution"] = "insufficient_evidence"
				value["reason"] = "The supplied observations cannot resolve the disputed sound."
			}
			if mode == "mapping" || mode == "reason" {
				value["resolution"] = "mapping_defect"
				var prior SemanticMapping
				_ = json.Unmarshal(mustJSON(input["prior_decisions"]), &prior)
				d := prior.Decisions[0]
				u := key["units"].([]any)[0].(map[string]any)
				o := u["corrections"].([]any)[0].(map[string]any)
				oid := o["id"].(string)
				d.Correction.Option = &oid
				d.Correction.Status = "accepted"
				d.Correction.Additional = []ComponentAssertion{}
				d.Correction.Satisfied = []string{}
				for _, v := range o["required_propositions"].([]any) {
					d.Correction.Satisfied = append(d.Correction.Satisfied, v.(map[string]any)["id"].(string))
				}
				if mode == "reason" {
					d.Explanation.Status = "accepted"
					d.Explanation.Satisfied = []string{}
					for _, v := range u["rationale_required_propositions"].([]any) {
						d.Explanation.Satisfied = append(d.Explanation.Satisfied, v.(map[string]any)["id"].(string))
					}
				}
				value["decisions"] = map[string]any{"schema_version": "1.0.0", "decisions": []SemanticDecision{d}}
			}
			if strings.HasPrefix(mode, "key") || mode == "conditional-failure" || mode == "omitted" {
				value["resolution"] = "key_defect"
				candidate := reviewCandidate(key)
				units := candidate["planned_units"].([]any)
				units[0].(map[string]any)["rationale"] = "The singular subject cafe requires opens in present tense."
				relations := []any{}
				for _, v := range key["units"].([]any) {
					id := v.(map[string]any)["id"]
					relations = append(relations, map[string]any{"old_unit_ids": []any{id}, "new_unit_ids": []any{id}, "kind": "same", "reason": "The same heard agreement event."})
				}
				value["key_repair"] = map[string]any{"base_case_sha256": key["case_sha256"], "audio_sha256": key["audio"].(map[string]any)["sha256"], "affected_components": []any{"explanation"}, "proposed_units": units, "correspondence_relations": relations, "reason": "Clarify the versioned rationale."}
				if mode == "omitted" {
					var packet map[string]any
					_ = json.Unmarshal([]byte(omittedReviewPacket), &packet)
					proposal := reviewClone(packet["proposal"])
					proposal["base_case_sha256"] = key["case_sha256"]
					proposal["audio_sha256"] = key["audio"].(map[string]any)["sha256"]
					value["key_repair"] = proposal
				}
				if mode == "key-with-decisions" {
					value["decisions"] = input["prior_decisions"]
				}
				if mode == "key-bad-hash" {
					value["key_repair"].(map[string]any)["audio_sha256"] = strings.Repeat("0", 64)
				}
			}
			out = value
		}
		_ = json.NewEncoder(w).Encode(map[string]any{"id": "constructed-review", "status": "completed", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": string(mustJSON(out))}}}}})
	}))
	t.Cleanup(f.reviewModel.Close)
	ctx := context.Background()
	c, rev, e := f.s.Store.Configuration(ctx)
	requireListening(t, e)
	profile := reviewClone(c["llm_profiles"].([]any)[0])
	profile["id"] = "constructed-review"
	profile["endpoint"] = f.reviewModel.URL + "/v1/responses"
	profile["model"] = "constructed-review"
	profile["roles"] = []any{"case_review", "adjudication", "claim_mapping"}
	c["llm_profiles"] = append(c["llm_profiles"].([]any), profile)
	if mode == "omitted" {
		c["stage_profiles"].(map[string]any)["blind_claim_extraction"] = "constructed-review"
		profile["roles"] = append(profile["roles"].([]any), "blind_claim_extraction")
	}
	for _, stage := range []string{"case_review", "adjudication", "claim_mapping"} {
		c["stage_profiles"].(map[string]any)[stage] = "constructed-review"
	}
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = f.s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	f.attempt = f.start(t)
	answer := "Use opens."
	if mode == "omitted" {
		answer = "work -> works; is -> are"
	}
	if mode == "reason" {
		f.mode.Store("rubric-valid")
		answer = "Use opens because the cafe is singular."
	}
	_, _, e = f.s.Store.WriteAnswer(ctx, f.attempt, uuid.NewString(), 0, answerPacket(answer, "en"), true)
	requireListening(t, e)
	_, e = f.interpret(t, uuid.NewString())
	requireListening(t, e)
	return f
}
func (f *reviewNative) latestReview(t *testing.T) string {
	var id string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT id FROM review_checkpoint ORDER BY revision DESC LIMIT 1").Scan(&id))
	return id
}
func (f *reviewNative) create(t *testing.T, purpose string) ReviewRun {
	t.Helper()
	record, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	r := ReviewRun{Purpose: purpose, Case: f.id, Statement: "Please check the correction and optional explanation."}
	if purpose == "case_review" {
		r.AudioSHA = record.Attempt["audio_sha256"].(string)
	} else {
		r.Attempt = f.attempt
		r.BaseResult = record.Context["result_id"].(string)
	}
	r, e = f.s.CreateReview(context.Background(), r, uuid.NewString())
	requireListening(t, e)
	return r
}
func (f *reviewNative) run(t *testing.T, r ReviewRun) (ReviewRun, error) {
	t.Helper()
	return f.s.RunReview(context.Background(), r.ID, uuid.NewString(), r.Revision, f.reviewModel.Client())
}
func TestNativeReviewCasePositive(t *testing.T) {
	f := reviewFixture(t, "supported")
	r := f.create(t, "case_review")
	r, e := f.run(t, r)
	requireListening(t, e)
	if r.Status != "complete" || r.Resolution != "supported" || f.reviewCalls.Load() != 1 {
		t.Fatal(r)
	}
	input := f.reviewInputs[0]
	if input["answer"] != nil || input["prior_decisions"] != nil || input["candidate"] == nil || input["input_modality"] != "text" {
		t.Fatal(input)
	}
	var count int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='adjudication' AND payload->>'origin'='llm' AND payload->'adjudicator_person_id'='null'::jsonb").Scan(&count))
	if count != 1 {
		t.Fatal(count)
	}
}
func TestNativeReviewInsufficientNegative(t *testing.T) {
	f := reviewFixture(t, "insufficient")
	r := f.create(t, "dispute")
	base := r.BaseResult
	r, e := f.run(t, r)
	requireListening(t, e)
	record, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if r.Resolution != "insufficient_evidence" || record.Context["result_id"] != base || r.NewResult != "" {
		t.Fatal(r, record)
	}
}
func TestNativeReviewMappingPositive(t *testing.T) {
	f := reviewFixture(t, "mapping")
	r := f.create(t, "dispute")
	old, e := f.s.Store.readScoringResult(context.Background(), r.BaseResult)
	requireListening(t, e)
	if old["score"].(map[string]any)["composite"].(map[string]any)["display"] != "60.0" {
		t.Fatal(old)
	}
	r, e = f.run(t, r)
	requireListening(t, e)
	now, e := f.s.Store.readScoringResult(context.Background(), r.NewResult)
	requireListening(t, e)
	if now["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" || len(now["result_revision_ids"].([]any)) < 1 {
		t.Fatal(now)
	}
	unchanged, e := f.s.Store.readScoringResult(context.Background(), r.BaseResult)
	requireListening(t, e)
	if string(mustJSON(old)) != string(mustJSON(unchanged)) {
		t.Fatal("old result changed")
	}
}
func TestNativeReviewMissingUnitNegative(t *testing.T) {
	f := reviewFixture(t, "missing-unit")
	r := f.create(t, "case_review")
	r, e := f.run(t, r)
	if e == nil || r.Status != "failed" || f.reviewCalls.Load() != 2 {
		t.Fatal(r, e, f.reviewCalls.Load())
	}
}
func TestNativeReviewKeyPositive(t *testing.T) {
	f := reviewFixture(t, "key-with-decisions")
	r := f.create(t, "dispute")
	r, e := f.run(t, r)
	requireListening(t, e)
	if r.NewCase == "" || r.Correspondence == "" || r.NewResult == "" || f.remaps.Load() != 1 {
		t.Fatal(r, f.remaps.Load())
	}
	var sha string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT audio_sha256 FROM listening_case WHERE case_version_id=$1", r.NewCase).Scan(&sha))
	if sha != r.AudioSHA {
		t.Fatal("heard audio changed")
	}
}
func TestNativeReviewWrongAudioNegative(t *testing.T) {
	f := reviewFixture(t, "key-bad-hash")
	r := f.create(t, "dispute")
	r, e := f.run(t, r)
	if e == nil || r.Status != "failed" || r.Projection != "" {
		t.Fatal(r, e)
	}
}
func TestNativeReviewConditionalMappingPositive(t *testing.T) {
	f := reviewFixture(t, "key")
	r := f.create(t, "dispute")
	r, e := f.run(t, r)
	requireListening(t, e)
	if r.NewResult == "" || f.reviewCalls.Load() != 1 || f.remaps.Load() != 2 {
		t.Fatal(r, f.remaps.Load())
	}
}
func TestNativeReviewConditionalFailureNegative(t *testing.T) {
	f := reviewFixture(t, "conditional-failure")
	r := f.create(t, "dispute")
	base := r.BaseResult
	r, e := f.run(t, r)
	if e == nil || r.Status != "failed" || r.Output == "" || r.Projection == "" || r.Mapping != "" {
		t.Fatal(r, e)
	}
	record, err := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, err)
	if record.Context["result_id"] != base {
		t.Fatal("partial version selected")
	}
	saved := r.Projection
	f.reviewMode.Store("key")
	r, e = f.run(t, r)
	requireListening(t, e)
	if r.Projection != saved || f.reviewCalls.Load() != 1 || r.NewResult == "" {
		t.Fatal(r)
	}
}
func TestNativeReviewReasonPositive(t *testing.T) {
	f := reviewFixture(t, "reason")
	r := f.create(t, "answer_reconsideration")
	r, e := f.run(t, r)
	requireListening(t, e)
	v, e := f.s.Store.readScoringResult(context.Background(), r.NewResult)
	requireListening(t, e)
	score := v["score"].(map[string]any)
	if score["composite"].(map[string]any)["display"] != "100.0" || score["optional_explanation"].(map[string]any)["display"] != "100.0" {
		t.Fatal(score)
	}
}
func TestNativeReviewFailureNegative(t *testing.T) {
	f := reviewFixture(t, "failure")
	r := f.create(t, "dispute")
	base := r.BaseResult
	originalRevision, key := r.Revision, uuid.NewString()
	r, e := f.s.RunReview(context.Background(), r.ID, key, originalRevision, f.reviewModel.Client())
	if e == nil || r.Status != "failed" {
		t.Fatal(r, e)
	}
	record, err := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, err)
	if record.Context["result_id"] != base {
		t.Fatal("failed provider replaced result")
	}
	calls := f.reviewCalls.Load()
	req := httptest.NewRequest("POST", "/api/v1/reviews/"+r.ID+":run", strings.NewReader("{}"))
	req.Header.Set("Origin", "http://localhost:3000")
	req.Header.Set("Authorization", "Bearer listening-owned-token")
	req.Header.Set("If-Match", strconv.FormatInt(originalRevision, 10))
	req.Header.Set("Idempotency-Key", key)
	response := httptest.NewRecorder()
	f.s.Handler().ServeHTTP(response, req)
	if response.Code != 503 || f.reviewCalls.Load() != calls || !strings.Contains(response.Body.String(), `"status":"failed"`) {
		t.Fatal("failed replay lost saved status or dispatched", response.Code, response.Body.String())
	}
}
func TestNativeReviewReplayPositive(t *testing.T) {
	f := reviewFixture(t, "supported")
	r := f.create(t, "case_review")
	key := uuid.NewString()
	done, e := f.s.RunReview(context.Background(), r.ID, key, r.Revision, f.reviewModel.Client())
	requireListening(t, e)
	replay, e := f.s.RunReview(context.Background(), r.ID, key, r.Revision, f.reviewModel.Client())
	requireListening(t, e)
	if replay.ID != done.ID || replay.Revision != done.Revision || f.reviewCalls.Load() != 1 {
		t.Fatal(replay)
	}
}
func TestNativeReviewStaleResultNegative(t *testing.T) {
	f := reviewFixture(t, "mapping")
	first := f.create(t, "dispute")
	other := f.create(t, "dispute")
	_, e := f.run(t, first)
	requireListening(t, e)
	r, e := f.run(t, other)
	if e == nil || r.Status != "failed" {
		t.Fatal(r, e)
	}
}
func TestNativeReviewRetryPositive(t *testing.T) {
	f := reviewFixture(t, "failure")
	r := f.create(t, "case_review")
	r, e := f.run(t, r)
	if e == nil {
		t.Fatal("expected unavailable model")
	}
	f.reviewMode.Store("supported")
	r, e = f.run(t, r)
	requireListening(t, e)
	if r.Status != "complete" {
		t.Fatal(r)
	}
}
func TestNativeReviewRevisionNegative(t *testing.T) {
	f := reviewFixture(t, "supported")
	r := f.create(t, "case_review")
	_, e := f.s.RunReview(context.Background(), r.ID, uuid.NewString(), r.Revision+1, f.reviewModel.Client())
	if e == nil || f.reviewCalls.Load() != 0 {
		t.Fatal(e)
	}
}

var _ = filepath.Join
var _ = time.Second

const omittedReviewPacket = `{"origin":"constructed_specification_fixture","canonical":"She works here. They are ready.","surface":"She work here. They is ready.","answer":"work -> works; is -> are","base_unit_ids":["u1"],"proposal":{"base_case_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","audio_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","affected_components":["key","detection","classification","correction","explanation"],"proposed_units":[{"id":"u1","primary_taxonomy_id":"grammar.verbs.subject_verb_agreement","accepted_taxonomy_ids":["grammar.verbs.subject_verb_agreement"],"secondary_taxonomy_ids":[],"domain":"grammar","expected_judgment":"true_error","status_label":"unequivocal_error","utterance_ids":["t1"],"text_spans":[{"utterance_id":"t1","span":{"start_cp":4,"end_cp":8,"exact_text":"work"}}],"realization":{"mode":"textual","canonical_text":"works","surface_text":"work","canonical_ipa":null,"intended_ipa":null,"observed_ipa":null,"prosody":[],"pace_target_wpm":null,"observed_pace_wpm":null,"planned_pause_ms":null,"observed_pause_ms":null},"severity":"moderate","weight":2,"difficulty":"unrated","correction_eligible":true,"corrections":[{"id":"o1","kind":"replace","text":"works","ipa":null,"approved_text_alternatives":[],"case_insensitive":false,"terminal_period_insensitive":true,"variety_constraints":["standard contemporary English"],"required_propositions":[{"id":"p1","description":"Replace work with works while retaining the present meaning and subject."}],"forbidden_propositions":[],"canonical":true}],"explanation_eligible":true,"rationale_required_propositions":[{"id":"r1","description":"The singular third-person subject she requires works in this present context."}],"rationale_forbidden_propositions":[],"rationale":"The singular third-person subject she requires works in this present context."},{"id":"new:u2","primary_taxonomy_id":"grammar.verbs.subject_verb_agreement","accepted_taxonomy_ids":["grammar.verbs.subject_verb_agreement"],"secondary_taxonomy_ids":[],"domain":"grammar","expected_judgment":"true_error","status_label":"unequivocal_error","utterance_ids":["t1"],"text_spans":[{"utterance_id":"t1","span":{"start_cp":20,"end_cp":22,"exact_text":"is"}}],"realization":{"mode":"textual","canonical_text":"are","surface_text":"is","canonical_ipa":null,"intended_ipa":null,"observed_ipa":null,"prosody":[],"pace_target_wpm":null,"observed_pace_wpm":null,"planned_pause_ms":null,"observed_pause_ms":null},"severity":"moderate","weight":2,"difficulty":"unrated","correction_eligible":true,"corrections":[{"id":"new:o2","kind":"replace","text":"are","ipa":null,"approved_text_alternatives":[],"case_insensitive":false,"terminal_period_insensitive":true,"variety_constraints":["standard contemporary English"],"required_propositions":[{"id":"new:p2","description":"Replace is with are while retaining the present meaning and subject."}],"forbidden_propositions":[],"canonical":true}],"explanation_eligible":true,"rationale_required_propositions":[{"id":"new:r2","description":"The plural subject they requires are in this present context."}],"rationale_forbidden_propositions":[],"rationale":"The plural subject they requires are in this present context."}],"correspondence_relations":[{"old_unit_ids":["u1"],"new_unit_ids":["u1"],"kind":"same","reason":"Same first agreement event."},{"old_unit_ids":[],"new_unit_ids":["new:u2"],"kind":"added","reason":"Second agreement error was omitted from the old key."}],"reason":"Both independently repairable audible agreement errors must be represented; the recording is unchanged."},"expected":{"G":2,"GC":2,"TP":2,"CQ":"2/1","primary":"100/1","audio_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","old_result_readable":true},"negative":{"changed_audio_sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","missing_repair_units":["u1"]},"negative_expected":{"new_key_committed":false,"old_result_readable":true}}`

func (f *reviewNative) installOmitted(t *testing.T) {
	ctx := context.Background()
	doc, e := f.s.Store.ReadDocument(ctx, f.id)
	requireListening(t, e)
	var key map[string]any
	requireListening(t, json.Unmarshal(doc.Payload, &key))
	var packet map[string]any
	requireListening(t, json.Unmarshal([]byte(omittedReviewPacket), &packet))
	old := key["units"].([]any)[0].(map[string]any)
	u := reviewClone(packet["proposal"].(map[string]any)["proposed_units"].([]any)[0])
	for _, k := range []string{"audio_intervals", "context_evidence", "evidence_ids", "verification", "difficulty_evidence_ref", "source"} {
		u[k] = old[k]
	}
	key["units"] = []any{u}
	turn := key["utterances"].([]any)[0].(map[string]any)
	turn["id"] = "t1"
	turn["canonical_text"] = packet["canonical"]
	turn["surface_text"] = packet["surface"]
	key["public_context"] = "A present-tense workplace description."
	key["case_version_id"] = uuid.NewString()
	content := map[string]any{}
	for _, k := range []string{"public_context", "variety_policy", "audio", "speakers", "utterances", "units", "taxonomy_version", "verification_policy_version"} {
		content[k] = key[k]
	}
	key["case_sha256"] = lab.Hash(content)
	source, e := f.s.Store.saveGroundTruth(ctx, key)
	requireListening(t, e)
	tx, e := beginWrite(ctx, f.s.Store)
	requireListening(t, e)
	defer tx.Rollback(ctx)
	f.id, e = f.s.Store.publishListeningCase(ctx, tx, source, map[string]any{"detection": true, "correction": true, "classification": false, "explanation": false}, "Constructed omitted-event fixture", "monologue")
	requireListening(t, e)
	requireListening(t, tx.Commit(ctx))
	f.sha = key["case_sha256"].(string)
}
func TestNativeReviewOmittedEventPositive(t *testing.T) {
	f := reviewFixture(t, "omitted")
	r := f.create(t, "dispute")
	r, e := f.run(t, r)
	requireListening(t, e)
	v, e := f.s.Store.readScoringResult(context.Background(), r.NewResult)
	requireListening(t, e)
	score := v["score"].(map[string]any)
	if score["composite"].(map[string]any)["display"] != "100.0" || score["counts"].(map[string]any)["tp"] != float64(2) || score["counts"].(map[string]any)["true_errors"] != float64(2) {
		t.Fatal(v)
	}
	if r.AudioSHA != f.audioSHA {
		t.Fatal("audio changed")
	}
}
func TestNativeReviewWrongVersionNegative(t *testing.T) {
	f := reviewFixture(t, "supported")
	r := ReviewRun{Purpose: "case_review", Case: f.id, AudioSHA: strings.Repeat("0", 64)}
	_, e := f.s.CreateReview(context.Background(), r, uuid.NewString())
	if e == nil || f.reviewCalls.Load() != 0 {
		t.Fatal(e)
	}
}
func TestNativeReviewFrozenRetryPositive(t *testing.T) {
	f := reviewFixture(t, "failure")
	r := f.create(t, "case_review")
	r, e := f.run(t, r)
	if e == nil {
		t.Fatal("expected provider failure")
	}
	f.reviewMode.Store("supported")
	c, rev, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	c["llm_profiles"].([]any)[0].(map[string]any)["model"] = "unselected"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = f.s.Store.PutConfiguration(context.Background(), mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	restarted := NewServer(f.s.Store, f.s.Origin, "http://unused.invalid")
	r, e = restarted.RunReview(context.Background(), r.ID, uuid.NewString(), r.Revision, f.reviewModel.Client())
	requireListening(t, e)
	if r.Status != "complete" {
		t.Fatal(r)
	}
}
func TestNativeReviewConcurrentNegative(t *testing.T) {
	f := reviewFixture(t, "blocked")
	r := f.create(t, "case_review")
	done := make(chan error, 1)
	go func() { _, e := f.run(t, r); done <- e }()
	<-f.arrived
	current, e := f.s.Store.Review(context.Background(), r.ID)
	requireListening(t, e)
	_, e = f.s.RunReview(context.Background(), r.ID, uuid.NewString(), current.Revision, f.reviewModel.Client())
	if !errors.Is(e, ErrEvaluationActive) {
		close(f.block)
		t.Fatal(e)
	}
	close(f.block)
	requireListening(t, <-done)
	if f.reviewCalls.Load() != 1 {
		t.Fatal("duplicate model dispatch")
	}
}
func TestNativeReviewStoredStatementPositive(t *testing.T) {
	f := reviewFixture(t, "supported")
	r := f.create(t, "dispute")
	r.Statement = "Unicode café\nPreserve my actual statement."
	fresh, e := f.s.Store.Review(context.Background(), r.ID)
	requireListening(t, e)
	input := ReviewRun{Purpose: "dispute", Case: f.id, Attempt: f.attempt, BaseResult: fresh.BaseResult, Statement: r.Statement}
	r, e = f.s.CreateReview(context.Background(), input, uuid.NewString())
	requireListening(t, e)
	r, e = f.run(t, r)
	requireListening(t, e)
	var statement string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT payload->>'statement' FROM document WHERE id=$1 AND kind='dispute'", r.ID).Scan(&statement))
	if statement != input.Statement {
		t.Fatal(statement)
	}
}
func TestNativeReviewLateNegative(t *testing.T) {
	f := reviewFixture(t, "blocked")
	r := f.create(t, "case_review")
	done := make(chan error, 1)
	go func() { _, e := f.run(t, r); done <- e }()
	<-f.arrived
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE review_checkpoint SET deadline_at=clock_timestamp()-interval '1 second' WHERE id=$1", r.ID)
	requireListening(t, e)
	close(f.block)
	if e = <-done; !errors.Is(e, ErrEvaluationLease) {
		t.Fatal(e)
	}
	var count int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='review-decision'").Scan(&count))
	if count != 0 {
		t.Fatal("late writer published review")
	}
}
func TestNativeReviewCaseHistoryPositive(t *testing.T) {
	f := reviewFixture(t, "supported")
	first := f.create(t, "case_review")
	second := f.create(t, "case_review")
	first, e := f.run(t, first)
	requireListening(t, e)
	second, e = f.run(t, second)
	requireListening(t, e)
	if first.ID == second.ID || f.reviewCalls.Load() != 2 {
		t.Fatal(first, second)
	}
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM review_checkpoint WHERE case_version_id=$1 AND payload->>'status'='complete'", f.id).Scan(&n))
	if n != 2 {
		t.Fatal(n)
	}
}
func TestNativeReviewObsoleteKeyNegative(t *testing.T) {
	f := reviewFixture(t, "key")
	a := f.create(t, "case_review")
	b := f.create(t, "case_review")
	_, e := f.run(t, a)
	requireListening(t, e)
	r, e := f.run(t, b)
	if e == nil || r.Status != "failed" {
		t.Fatal(r, e)
	}
}

func TestNativeReviewCaseDisputePositive(t *testing.T) {
	f := reviewFixture(t, "supported")
	r, e := f.s.CreateReview(context.Background(), ReviewRun{Purpose: "dispute", Case: f.id, Statement: "Check the agreement key for this recording."}, uuid.NewString())
	requireListening(t, e)
	r, e = f.run(t, r)
	requireListening(t, e)
	if r.Status != "complete" || f.reviewInputs[0]["answer"] != nil || f.reviewInputs[0]["dispute_statement"] != "Check the agreement key for this recording." {
		t.Fatal(r)
	}
}
func TestNativeReviewMissingAnswerNegative(t *testing.T) {
	f := reviewFixture(t, "supported")
	_, e := f.s.CreateReview(context.Background(), ReviewRun{Purpose: "answer_reconsideration", Case: f.id}, uuid.NewString())
	if e == nil || f.reviewCalls.Load() != 0 {
		t.Fatal(e)
	}
}
func TestNativeReviewSequencePositive(t *testing.T) {
	for _, seed := range []int64{127, 9001} {
		t.Run(strconv.FormatInt(seed, 10), func(t *testing.T) {
			f := reviewFixture(t, "supported")
			createKey, runKey := uuid.NewString(), uuid.NewString()
			input := ReviewRun{Purpose: "case_review", Case: f.id, AudioSHA: f.audioSHA}
			r, e := f.s.CreateReview(context.Background(), input, createKey)
			requireListening(t, e)
			state := "ready"
			calls := int32(0)
			coverage := map[string]int{"create.applied": 1}
			rng := rand.New(rand.NewSource(seed))
			read := func() {
				observed, err := f.s.Store.Review(context.Background(), r.ID)
				requireListening(t, err)
				if observed.Status != state || f.reviewCalls.Load() != calls {
					t.Fatalf("seed=%d state=%s calls=%d observed=%v", seed, state, calls, observed)
				}
				coverage["read.observed_no_mutation"]++
			}
			for n := 0; n < rng.Intn(4)+1; n++ {
				read()
			}
			_, e = f.s.RunReview(context.Background(), r.ID, uuid.NewString(), r.Revision+1, f.reviewModel.Client())
			if !errors.Is(e, ErrRevision) || f.reviewCalls.Load() != 0 {
				t.Fatal(e)
			}
			coverage["stale.observed_no_mutation"]++
			initial := r.Revision
			r, e = f.s.RunReview(context.Background(), r.ID, runKey, initial, f.reviewModel.Client())
			requireListening(t, e)
			state = "complete"
			calls = 1
			coverage["run.applied"]++
			for n := 0; n < rng.Intn(4)+1; n++ {
				if rng.Intn(2) == 0 {
					read()
				} else {
					replay, err := f.s.RunReview(context.Background(), r.ID, runKey, initial, f.reviewModel.Client())
					requireListening(t, err)
					if replay.Revision != r.Revision || f.reviewCalls.Load() != calls {
						t.Fatal(replay)
					}
					coverage["replay.observed_no_mutation"]++
				}
			}
			replay, err := f.s.RunReview(context.Background(), r.ID, runKey, initial, f.reviewModel.Client())
			requireListening(t, err)
			if replay.ID != r.ID || f.reviewCalls.Load() != 1 {
				t.Fatal(replay)
			}
			coverage["replay.observed_no_mutation"]++
			input.Statement = "Different request with same key"
			_, e = f.s.CreateReview(context.Background(), input, createKey)
			if !errors.Is(e, ErrConflict) {
				t.Fatal(e)
			}
			coverage["conflict.observed_no_mutation"]++
			for _, event := range []string{"create.applied", "read.observed_no_mutation", "stale.observed_no_mutation", "run.applied", "replay.observed_no_mutation", "conflict.observed_no_mutation"} {
				if coverage[event] == 0 {
					t.Fatal("missing effective event", seed, event)
				}
			}
			var decisions int
			requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='review-decision'").Scan(&decisions))
			if decisions != 1 {
				t.Fatal(decisions)
			}
			t.Logf("seed=%d effective_events=%v; zero skipped preconditions", seed, coverage)
		})
	}
}
func TestNativeReviewSequenceNegative(t *testing.T) {
	f := reviewFixture(t, "failure")
	r := f.create(t, "case_review")
	key := uuid.NewString()
	revision := r.Revision
	r, e := f.s.RunReview(context.Background(), r.ID, key, revision, f.reviewModel.Client())
	if e == nil || r.Status != "failed" || f.reviewCalls.Load() != 2 {
		t.Fatal(r, e, f.reviewCalls.Load())
	}
	for n := 0; n < 3; n++ {
		observed, err := f.s.Store.Review(context.Background(), r.ID)
		requireListening(t, err)
		if observed.Status != "failed" || f.reviewCalls.Load() != 2 {
			t.Fatal(observed)
		}
	}
	_, e = f.s.RunReview(context.Background(), r.ID, key, revision, f.reviewModel.Client())
	requireListening(t, e)
	if f.reviewCalls.Load() != 2 {
		t.Fatal("replay retried failed model implicitly")
	}
	f.reviewMode.Store("supported")
	r, e = f.run(t, r)
	requireListening(t, e)
	if r.Status != "complete" || f.reviewCalls.Load() != 3 {
		t.Fatal(r, f.reviewCalls.Load())
	}
}

func reviewHTTP(t *testing.T, f *reviewNative, method, path string, body any, key string) *httptest.ResponseRecorder {
	t.Helper()
	var data io.Reader
	if body != nil {
		data = strings.NewReader(string(mustJSON(body)))
	}
	request := httptest.NewRequest(method, path, data)
	request.Header.Set("Origin", "http://localhost:3000")
	request.Header.Set("Authorization", "Bearer listening-owned-token")
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("Idempotency-Key", key)
	response := httptest.NewRecorder()
	f.s.Handler().ServeHTTP(response, request)
	return response
}
func TestNativeReviewSelectedPositive(t *testing.T) {
	f := reviewFixture(t, "key-with-decisions")
	original := f.attempt
	f.attempt = f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), f.attempt, uuid.NewString(), 0, answerPacket("Use opens.", "en"), true)
	requireListening(t, e)
	_, e = f.interpret(t, uuid.NewString())
	requireListening(t, e)
	other := f.attempt
	f.attempt = original
	r := f.create(t, "dispute")
	r, e = f.run(t, r)
	requireListening(t, e)
	f.reviewMode.Store("supported")
	body := map[string]any{"dispute_id": r.ID, "attempt_ids": []any{other}, "unit_correspondence_id": r.Correspondence}
	key := uuid.NewString()
	response := reviewHTTP(t, f, "POST", "/api/v1/reviews/"+r.ID+":reconsider", body, key)
	if response.Code != 200 {
		t.Fatal(response.Code, response.Body.String())
	}
	record, e := f.s.Store.Attempt(context.Background(), other)
	requireListening(t, e)
	value, e := f.s.Store.readScoringResult(context.Background(), record.Context["result_id"].(string))
	requireListening(t, e)
	if value["score"].(map[string]any)["case_version_id"] != r.NewCase {
		t.Fatal(value)
	}
	var retained []byte
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT payload FROM document WHERE kind='result-revision' AND payload->>'new_result_id'=$1", record.Context["result_id"]).Scan(&retained))
	var revision map[string]any
	requireListening(t, json.Unmarshal(retained, &revision))
	if revision["unit_correspondence_id"] != r.Correspondence {
		t.Fatal("selected historical result lost exact correspondence", revision)
	}
	untouched, e := f.s.Store.Attempt(context.Background(), original)
	requireListening(t, e)
	if untouched.Context["result_id"] != r.NewResult {
		t.Fatal("unselected answer regraded")
	}
	calls := f.reviewCalls.Load()
	response = reviewHTTP(t, f, "POST", "/api/v1/reviews/"+r.ID+":reconsider", body, key)
	if response.Code != 200 || f.reviewCalls.Load() != calls {
		t.Fatal("batch continuation repeated completed work", response.Body.String())
	}

	// A second key repair must still offer answers whose original heard-case ID
	// differs from their selected result's current key.
	f.reviewMode.Store("key-with-decisions")
	second, e := f.s.CreateReview(context.Background(), ReviewRun{Purpose: "case_review", Case: r.NewCase}, uuid.NewString())
	requireListening(t, e)
	second, e = f.run(t, second)
	requireListening(t, e)
	rows, _, e := f.s.Store.AttemptHistoryForCase(context.Background(), 100, "", r.NewCase)
	requireListening(t, e)
	if len(rows) != 2 {
		t.Fatal("current-key answers vanished after one repair", rows)
	}
	f.reviewMode.Store("supported")
	response = reviewHTTP(t, f, "POST", "/api/v1/reviews/"+second.ID+":reconsider", map[string]any{"dispute_id": second.ID, "attempt_ids": []any{other}, "unit_correspondence_id": second.Correspondence}, uuid.NewString())
	if response.Code != 200 {
		t.Fatal("second explicit reconsideration", response.Body.String())
	}
	selected, e := f.s.Store.Attempt(context.Background(), other)
	requireListening(t, e)
	value, e = f.s.Store.readScoringResult(context.Background(), selected.Context["result_id"].(string))
	requireListening(t, e)
	if value["score"].(map[string]any)["case_version_id"] != second.NewCase {
		t.Fatal("second successor not selected", value)
	}
	untouched, e = f.s.Store.Attempt(context.Background(), original)
	requireListening(t, e)
	if untouched.Context["result_id"] != r.NewResult {
		t.Fatal("second repair regraded unselected answer")
	}
}
func TestNativeReviewWrongCorrespondenceNegative(t *testing.T) {
	f := reviewFixture(t, "key-with-decisions")
	rows, _, err := f.s.Store.AttemptHistoryForCase(context.Background(), 100, "", uuid.NewString())
	requireListening(t, err)
	if len(rows) != 0 {
		t.Fatal("unrelated key selection borrowed answers", rows)
	}
	r := f.create(t, "dispute")
	r, e := f.run(t, r)
	requireListening(t, e)
	calls := f.reviewCalls.Load()
	response := reviewHTTP(t, f, "POST", "/api/v1/reviews/"+r.ID+":reconsider", map[string]any{"dispute_id": r.ID, "attempt_ids": []any{f.attempt}, "unit_correspondence_id": uuid.NewString()}, uuid.NewString())
	if response.Code == 200 || f.reviewCalls.Load() != calls {
		t.Fatal(response.Body.String())
	}
}
func TestNativeReviewHistoricalReadPositive(t *testing.T) {
	f := reviewFixture(t, "mapping")
	r := f.create(t, "dispute")
	r, e := f.run(t, r)
	requireListening(t, e)
	response := reviewHTTP(t, f, "GET", "/api/v1/attempts/"+f.attempt+"/results?result_id="+r.BaseResult, nil, "")
	if response.Code != 200 {
		t.Fatal(response.Body.String())
	}
	var value map[string]any
	requireListening(t, json.Unmarshal(response.Body.Bytes(), &value))
	if value["score"].(map[string]any)["composite"].(map[string]any)["display"] != "60.0" {
		t.Fatal(value)
	}
}
func TestNativeReviewForeignHistoryNegative(t *testing.T) {
	f := reviewFixture(t, "supported")
	response := reviewHTTP(t, f, "GET", "/api/v1/attempts/"+f.attempt+"/results?result_id="+uuid.NewString(), nil, "")
	if response.Code == 200 || strings.Contains(response.Body.String(), "Use opens") {
		t.Fatal(response.Code, response.Body.String())
	}
}
func TestNativeReviewFeedbackRetryPositive(t *testing.T) {
	f := reviewFixture(t, "key-with-decisions")
	r := f.create(t, "dispute")
	r, e := f.run(t, r)
	requireListening(t, e)
	calls, maps := f.reviewCalls.Load(), f.remaps.Load()
	record, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	state, e := f.s.interpretAttempt(context.Background(), f.attempt, uuid.NewString(), int64(record.Attempt["revision"].(float64)), record.Attempt["answer_utf8_sha256"].(string), record.Attempt["configuration_sha256"].(string), f.feedback.Client(), true)
	requireListening(t, e)
	value, e := f.s.Store.readScoringResult(context.Background(), *state.Result)
	requireListening(t, e)
	if value["feedback_status"] != "complete" || f.reviewCalls.Load() != calls || f.remaps.Load() != maps || value["score"].(map[string]any)["case_version_id"] != r.NewCase {
		t.Fatal(value)
	}
}
func TestNativeReviewNoAutoRegradeNegative(t *testing.T) {
	f := reviewFixture(t, "key-with-decisions")
	original := f.attempt
	f.attempt = f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), f.attempt, uuid.NewString(), 0, answerPacket("Use opens.", "en"), true)
	requireListening(t, e)
	_, e = f.interpret(t, uuid.NewString())
	requireListening(t, e)
	other := f.attempt
	before, e := f.s.Store.Attempt(context.Background(), other)
	requireListening(t, e)
	f.attempt = original
	r := f.create(t, "dispute")
	_, e = f.run(t, r)
	requireListening(t, e)
	after, e := f.s.Store.Attempt(context.Background(), other)
	requireListening(t, e)
	if before.Context["result_id"] != after.Context["result_id"] || before.Attempt["revision"] != after.Attempt["revision"] {
		t.Fatal("unselected result changed")
	}
}

func reviewAtomicFault(t *testing.T, f *reviewNative, enabled bool) {
	t.Helper()
	sql := `CREATE FUNCTION review_write_fault() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.kind='result-envelope' THEN RAISE EXCEPTION 'test-owned review result failure'; END IF; RETURN NEW; END $$; CREATE TRIGGER review_write_fault BEFORE INSERT ON document FOR EACH ROW EXECUTE FUNCTION review_write_fault();`
	if !enabled {
		sql = `DROP TRIGGER review_write_fault ON document; DROP FUNCTION review_write_fault();`
	}
	_, e := f.s.Store.DB.Exec(context.Background(), sql)
	requireListening(t, e)
}
func TestNativeReviewAtomicRecoveryPositive(t *testing.T) {
	f := reviewFixture(t, "key-with-decisions")
	r := f.create(t, "dispute")
	reviewAtomicFault(t, f, true)
	r, e := f.run(t, r)
	if e == nil || r.Status != "failed" || r.Output == "" || r.Mapping == "" {
		t.Fatal(r, e)
	}
	key, projection, mapping := r.NewCase, r.Projection, r.Mapping
	reviewAtomicFault(t, f, false)
	r, e = f.run(t, r)
	requireListening(t, e)
	if r.Status != "complete" || r.NewCase != key || r.Projection != projection || r.Mapping != mapping || f.reviewCalls.Load() != 1 {
		t.Fatal(r)
	}
	var event int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM audit_event WHERE action='review.selection' AND event_payload->>'id'=$1", r.SelectionID).Scan(&event))
	if event != 1 {
		t.Fatal(event)
	}
}
func TestNativeReviewAtomicFailureNegative(t *testing.T) {
	f := reviewFixture(t, "key-with-decisions")
	r := f.create(t, "dispute")
	reviewAtomicFault(t, f, true)
	r, e := f.run(t, r)
	if e == nil {
		t.Fatal("fault not reached")
	}
	var successors, records int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM reviewed_case_successor").Scan(&successors))
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind IN('rationale','unit-correspondence','review-decision','result-revision')").Scan(&records))
	a, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if successors != 0 || records != 0 || a.Context["result_id"] != r.BaseResult {
		t.Fatal(successors, records, a)
	}
}

func TestNativeReviewRightsRecoveryPositive(t *testing.T) {
	f := reviewFixture(t, "supported")
	r := f.create(t, "case_review")
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE exercise_catalog SET availability='rights_restricted' WHERE id::text=$1", f.id)
	requireListening(t, e)
	r, e = f.run(t, r)
	if e == nil {
		t.Fatal("restriction not observed")
	}
	_, e = f.s.Store.DB.Exec(context.Background(), "UPDATE exercise_catalog SET availability='published' WHERE id::text=$1", f.id)
	requireListening(t, e)
	r, e = f.run(t, r)
	requireListening(t, e)
	if r.Status != "complete" || f.reviewCalls.Load() != 1 {
		t.Fatal(r)
	}
}
func TestNativeReviewRightsNegative(t *testing.T) {
	f := reviewFixture(t, "supported")
	r := f.create(t, "case_review")
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE exercise_catalog SET availability='rights_restricted' WHERE id::text=$1", f.id)
	requireListening(t, e)
	r, e = f.run(t, r)
	if !errors.Is(e, ErrAttemptRights) || r.Failure != "SOURCE_USE_RESTRICTED" || f.reviewCalls.Load() != 0 {
		t.Fatal(r, e)
	}
}

func reviewPre006(t *testing.T, f *reviewNative) {
	t.Helper()
	_, e := f.s.Store.DB.Exec(context.Background(), `DROP TABLE reviewed_case_successor; DROP TABLE review_event; DROP TABLE review_checkpoint; DELETE FROM schema_migrations WHERE version='006_reviews.sql'`)
	requireListening(t, e)
}
func TestNativeReviewUpgradePositive(t *testing.T) {
	f := reviewFixture(t, "supported")
	before, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	reviewPre006(t, f)
	requireListening(t, f.s.Store.Migrate(context.Background()))
	after, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	audio, sha, e := f.s.Store.AttemptAudio(context.Background(), f.attempt)
	requireListening(t, e)
	if before.Context["result_id"] != after.Context["result_id"] || after.Attempt["answer_text"] != "Use opens." || sha != f.audioSHA || !bytes.Equal(audio, f.audio) {
		t.Fatal("pre006 data changed")
	}
	r := f.create(t, "case_review")
	r, e = f.run(t, r)
	requireListening(t, e)
	if r.Status != "complete" {
		t.Fatal(r)
	}
}
func TestNativeReviewUpgradeFailureNegative(t *testing.T) {
	f := reviewFixture(t, "supported")
	before, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	reviewPre006(t, f)
	_, e = f.s.Store.DB.Exec(context.Background(), "CREATE TABLE review_checkpoint(test_owned_conflict integer)")
	requireListening(t, e)
	if e = f.s.Store.Migrate(context.Background()); e == nil {
		t.Fatal("DDL conflict ignored")
	}
	after, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	var applied bool
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT EXISTS(SELECT 1 FROM schema_migrations WHERE version='006_reviews.sql')").Scan(&applied))
	if applied || after.Context["result_id"] != before.Context["result_id"] || f.reviewCalls.Load() != 0 {
		t.Fatal("failed migration changed data or completed")
	}
}

// This literal stored metadata fixture isolates lineage lookup. Preparation
// schema admission is covered by its existing owner; real DB/media/query here.
func reviewManifestMetadata(t *testing.T, f *reviewNative, source string) {
	t.Helper()
	ctx := context.Background()
	doc, e := f.s.Store.ReadDocument(ctx, f.id)
	requireListening(t, e)
	var key map[string]any
	requireListening(t, json.Unmarshal(doc.Payload, &key))
	canonical := map[string]any{"text": "The café opens tomorrow."}
	surface := reviewCandidate(key)
	clean, e := f.s.Store.interpretationJSON(ctx, canonical)
	requireListening(t, e)
	mutated, e := f.s.Store.interpretationJSON(ctx, surface)
	requireListening(t, e)
	recipes, e := generationRegistry("mutation-recipes.v1.json")
	requireListening(t, e)
	manifest := map[string]any{"schema_version": "2.0.0", "id": "literal-authored-manifest", "canonical_asset_id": clean, "canonical_sha256": lab.Hash(canonical), "mutated_asset_id": mutated, "mutated_sha256": lab.Hash(surface), "recipe_registry_sha256": lab.Hash(json.RawMessage(recipes)), "recipe_ids": []any{"grammar.verbs.subject_verb_agreement"}, "seed": nil, "method_version": "canonical-composite-codepoint-v1", "canonical_word_count": 4, "surface_word_count": 4, "edits": []any{map[string]any{"utterance_id": "u1", "start_cp": 13, "end_cp": 14, "original_text": "s", "replacement_text": "", "order": 0, "unit_ids": []any{"e1"}}}, "acoustic_intents": []any{}, "planned_units": surface["planned_units"]}
	manifest["manifest_sha256"] = lab.Hash(manifest)
	asset, e := f.s.Store.interpretationJSON(ctx, manifest)
	requireListening(t, e)
	payload := mustJSON(map[string]any{"key_id": source, "mutation_manifest_asset_id": asset})
	id := uuid.NewString()
	_, e = f.s.Store.DB.Exec(ctx, "INSERT INTO document(id,workspace_id,kind,schema_version,schema_sha256,payload_sha256,payload) SELECT $1,'local','preparation-state',version,sha256,$2,$3 FROM schema_registry WHERE kind='preparation-state'", id, lab.Hash(json.RawMessage(payload)), payload)
	requireListening(t, e)
	_, e = f.s.Store.DB.Exec(ctx, "INSERT INTO entity_head(id,workspace_id,kind,document_id,revision,state) VALUES($1,'local','preparation-state',$1,0,'complete')", id)
	requireListening(t, e)
}
func TestNativeReviewManifestPositive(t *testing.T) {
	f := reviewFixture(t, "key-with-decisions")
	ctx := context.Background()
	var source string
	requireListening(t, f.s.Store.DB.QueryRow(ctx, "SELECT source_key_id FROM listening_case WHERE case_version_id=$1", f.id).Scan(&source))
	reviewManifestMetadata(t, f, source)
	r := f.create(t, "case_review")
	var frozen ReviewFrozen
	requireListening(t, f.s.Store.readInterpretationJSON(ctx, r.Frozen, &frozen))
	if frozen.Manifest.(map[string]any)["id"] != "literal-authored-manifest" {
		t.Fatal("original manifest missing", frozen.Manifest)
	}
	r, e := f.run(t, r)
	requireListening(t, e)
	next, e := f.s.CreateReview(ctx, ReviewRun{Purpose: "case_review", Case: r.NewCase}, uuid.NewString())
	requireListening(t, e)
	requireListening(t, f.s.Store.readInterpretationJSON(ctx, next.Frozen, &frozen))
	if frozen.Manifest.(map[string]any)["id"] != "literal-authored-manifest" {
		t.Fatal("successor lost original authored manifest", frozen.Manifest)
	}
}
func TestNativeReviewForeignManifestNegative(t *testing.T) {
	f := reviewFixture(t, "supported")
	reviewManifestMetadata(t, f, uuid.NewString())
	r := f.create(t, "case_review")
	var frozen ReviewFrozen
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), r.Frozen, &frozen))
	if frozen.Manifest != nil {
		t.Fatal("unrelated preparation borrowed", frozen.Manifest)
	}
}
