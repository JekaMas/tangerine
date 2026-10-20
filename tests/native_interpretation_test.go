package app

// The external model protocol is constructed. Application/provider/context,
// PostgreSQL, MinIO, exact spans and durable state are actual production owners.
import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/google/uuid"
	"tangerine.local/api/internal/contracts"
)

type nativeInterpretation struct {
	listeningFixture
	attempt                       string
	model                         *httptest.Server
	calls, extracts, maps, audits atomic.Int32
	mode                          atomic.Value
	mu                            sync.Mutex
	wires                         []map[string]any
	entered                       chan struct{}
	release                       chan struct{}
	once                          sync.Once
	modePath                      string
}

func interpretationNative(t *testing.T, mode string) *nativeInterpretation {
	t.Helper()
	f := &nativeInterpretation{listeningFixture: listeningCase(t), entered: make(chan struct{}), release: make(chan struct{})}
	f.mode.Store(mode)
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		f.calls.Add(1)
		body, _ := io.ReadAll(r.Body)
		var wire map[string]any
		_ = json.Unmarshal(body, &wire)
		f.mu.Lock()
		f.wires = append(f.wires, wire)
		f.mu.Unlock()
		var input map[string]any
		var claims []CanonicalClaim
		for _, v := range wire["input"].([]any) {
			content := v.(map[string]any)["content"].(string)
			if strings.HasPrefix(content, "Complete stage input: ") {
				_ = json.Unmarshal([]byte(strings.TrimPrefix(content, "Complete stage input: ")), &input)
			}
			if strings.HasPrefix(content, "extraction: ") {
				var c struct {
					Claims []CanonicalClaim `json:"claims"`
				}
				_ = json.Unmarshal([]byte(strings.TrimPrefix(content, "extraction: ")), &c)
				claims = c.Claims
			}
		}
		var output any
		answer := input["answer_text"].(string)
		if _, mapping := input["ground_truth"]; !mapping {
			f.extracts.Add(1)
			if f.currentMode() == "blocked" {
				f.once.Do(func() { close(f.entered) })
				<-f.release
			}
			text := []rune(answer)
			if f.currentMode() == "bad-extraction" {
				output = map[string]any{"schema_version": "2.0.0", "clauses": []any{}, "unparsed_spans": []any{}, "coverage": []any{}, "relations": []any{}}
				_ = json.NewEncoder(w).Encode(map[string]any{"id": "bad", "object": "response", "status": "completed", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": string(mustJSON(output))}}}}})
				return
			}
			span := &AnswerSpan{Start: 4, End: 9, Text: "opens"}
			if answer != "Use opens." {
				span = nil
			}
			output = AnswerExtraction{Version: "2.0.0", Clauses: []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, len(text), answer}, Stance: "assert_error", Correction: span}}, Unparsed: []AnswerSpan{}, Coverage: []ClaimCoverage{}, Relations: []ClaimRelation{}}

			if strings.HasPrefix(f.currentMode(), "attachment-") {
				correction := AnswerSpan{22, 27, "opens"}
				clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 18, "The verb is wrong."}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{19, 28, "Use opens."}, Stance: "assert_error", Correction: &correction}}
				relation := ClaimRelation{From: "c1", To: "c0", Kind: "correction_attachment"}
				relation.Evidence.Start = 19
				relation.Evidence.End = 28
				if f.currentMode() == "attachment-retracted" {
					target := clauses[1].Span
					clauses = append(clauses, ExtractedClause{LocalRef: "c2", Span: AnswerSpan{29, 43, "Withdraw that."}, Stance: "meta", Retraction: &target})
				}
				output = AnswerExtraction{Version: "2.0.0", Clauses: clauses, Relations: []ClaimRelation{relation}, Unparsed: []AnswerSpan{}, Coverage: []ClaimCoverage{}}
			}

			if strings.HasPrefix(f.currentMode(), "rubric-") {
				correction := AnswerSpan{4, 9, "opens"}
				reason := AnswerSpan{10, 39, "because the cafe is singular."}
				output = AnswerExtraction{Version: "2.0.0", Clauses: []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 39, answer}, Stance: "assert_error", Correction: &correction, Rationale: &reason}}, Unparsed: []AnswerSpan{}, Coverage: []ClaimCoverage{}, Relations: []ClaimRelation{}}
			}
		} else {
			audit := wire["model"] == "constructed-auditor"
			if audit {
				if f.currentMode() == "audit-blocked" {
					f.once.Do(func() { close(f.entered) })
					<-f.release
				}
				f.audits.Add(1)
			} else {
				f.maps.Add(1)
			}
			if f.currentMode() == "mapping-failure" || (f.currentMode() == "audit-retry-budget" && !audit && f.maps.Load() == 1) || (f.currentMode() == "audit-retry-budget" && audit) {
				w.WriteHeader(503)
				_, _ = io.WriteString(w, `{"error":{"code":"unavailable"}}`)
				return
			}
			if audit && f.currentMode() == "audit-failure" {
				w.WriteHeader(503)
				_, _ = io.WriteString(w, `{"error":{"code":"unavailable"}}`)
				return
			}
			unit := input["ground_truth"].(map[string]any)["units"].([]any)[0].(map[string]any)
			id := unit["id"].(string)
			if f.currentMode() == "bad-unit" {
				id = "other-case-unit"
			}
			option := unit["corrections"].([]any)[0].(map[string]any)
			optionID := option["id"].(string)
			decision := SemanticDecision{Claim: claims[0].ID, Unit: &id, Decision: "matched_error", Correction: semanticEmpty(), Explanation: semanticEmpty(), Evidence: []string{}, Reason: "supported", Note: "The present-tense verb should agree with its singular subject."}
			if answer == "Use opens." {
				decision.Correction.Supplied = true
				decision.Correction.Option = &optionID
				decision.Correction.Status = "accepted"
				for _, p := range option["required_propositions"].([]any) {
					decision.Correction.Satisfied = append(decision.Correction.Satisfied, p.(map[string]any)["id"].(string))
				}
			}
			if audit && f.currentMode() == "audit-disagreement" {
				decision.Correction.Satisfied = []string{}
				decision.Correction.Status = "rejected"
			}

			if strings.HasPrefix(f.currentMode(), "rubric-") {
				decision.Correction.Supplied = true
				decision.Correction.Option = &optionID
				decision.Correction.Status = "accepted"
				for _, p := range option["required_propositions"].([]any) {
					decision.Correction.Satisfied = append(decision.Correction.Satisfied, p.(map[string]any)["id"].(string))
				}
				decision.Explanation.Supplied = true
				decision.Explanation.Status = "accepted"
				decision.Explanation.Additional = []ComponentAssertion{{AnswerSpan: AnswerSpan{10, 39, "because the cafe is singular."}, Judgment: "supported", Reason: "The singular subject requires singular agreement."}}
				if f.currentMode() == "rubric-repair" && f.maps.Load() > 1 {
					for _, p := range unit["rationale_required_propositions"].([]any) {
						decision.Explanation.Satisfied = append(decision.Explanation.Satisfied, p.(map[string]any)["id"].(string))
					}
				}
			}
			output = SemanticMapping{Version: "1.0.0", Decisions: []SemanticDecision{decision}}
			if strings.HasPrefix(f.currentMode(), "attachment-") {
				decisions := []SemanticDecision{}
				for i, claim := range claims {
					d := SemanticDecision{Claim: claim.ID, Unit: &id, Decision: "matched_error", Correction: semanticEmpty(), Explanation: semanticEmpty(), Evidence: []string{}, Reason: "supported", Note: "Constructed attachment assessment"}
					if i == 1 || i == 0 && f.currentMode() == "attachment-kept" {
						d.Correction.Supplied = true
						d.Correction.Option = &optionID
						d.Correction.Status = "accepted"
						for _, v := range option["required_propositions"].([]any) {
							d.Correction.Satisfied = append(d.Correction.Satisfied, v.(map[string]any)["id"].(string))
						}
					}
					if i > 0 {
						d.Decision = "ignore"
					}
					decisions = append(decisions, d)
				}
				output = SemanticMapping{Version: "1.0.0", Decisions: decisions}
			}

		}
		encoded, _ := json.Marshal(output)
		response := map[string]any{"id": "constructed-response", "object": "response", "status": "completed", "model": wire["model"], "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": string(encoded)}}}}}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(response)
	}))
	f.model = target
	t.Cleanup(target.Close)
	c, rev, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	for k, v := range map[string]any{"provider": "local_responses", "model": "constructed-interpreter", "endpoint": target.URL + "/v1/responses", "adapter_version": "local-responses-v1", "auth_method": "local_none", "billing_mode": "local", "credential_ref": "local-none", "stream": false, "context_budget_tokens": 262144, "max_output_tokens": 4096} {
		p[k] = v
	}
	c["mapping_audit_enabled"] = strings.HasPrefix(mode, "audit")
	if c["mapping_audit_enabled"] == true {
		auditProfile := map[string]any{}
		for key, value := range p {
			auditProfile[key] = value
		}
		auditProfile["id"], auditProfile["model"], auditProfile["roles"] = "constructed-audit", "constructed-auditor", []any{"mapping_audit"}
		c["llm_profiles"] = append(c["llm_profiles"].([]any), auditProfile)
		c["stage_profiles"].(map[string]any)["mapping_audit"] = "constructed-audit"
	}
	for _, field := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, field)
	}
	raw, _ := json.Marshal(c)
	_, _, e = f.s.Store.PutConfiguration(context.Background(), raw, uuid.NewString(), rev)
	requireListening(t, e)
	f.attempt = f.start(t)
	answer := "Use opens."
	if strings.HasPrefix(mode, "rubric-") {
		answer = "Use opens because the cafe is singular."
	}
	if strings.HasPrefix(mode, "attachment-") {
		answer = "The verb is wrong. Use opens."
		if mode == "attachment-retracted" {
			answer += " Withdraw that."
		}
	}
	_, _, e = f.s.Store.WriteAnswer(context.Background(), f.attempt, uuid.NewString(), 0, answerPacket(answer, "en"), true)
	requireListening(t, e)
	return f
}
func (f *nativeInterpretation) interpret(t *testing.T, key string) (InterpretationState, error) {
	t.Helper()
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	return f.s.InterpretAttempt(context.Background(), f.attempt, key, int64(r.Attempt["revision"].(float64)), r.Attempt["answer_utf8_sha256"].(string), r.Attempt["configuration_sha256"].(string), f.model.Client())
}
func TestNativeInterpretationCompletePositive(t *testing.T) {
	f := interpretationNative(t, "good")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if state.Status != "complete" || state.Extraction == nil || state.Mapping == nil || f.extracts.Load() != 1 || f.maps.Load() != 1 {
		t.Fatal(state, f.calls.Load())
	}
	document, e := f.s.Store.ReadDocument(context.Background(), state.ID)
	requireListening(t, e)
	_, _, e = contracts.Validate("interpretation-checkpoint", "2.0.0", document.Payload)
	requireListening(t, e)
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if r.Attempt["answer_text"] != "Use opens." || r.Attempt["state"] != "saved" || r.Attempt["lease_token"] != nil {
		t.Fatal(r)
	}
}
func TestNativeInterpretationRepairExhaustedNegative(t *testing.T) {
	f := interpretationNative(t, "bad-unit")
	state, e := f.interpret(t, uuid.NewString())
	if e == nil || state.Status != "failed" || f.maps.Load() != 2 {
		t.Fatal(state, e, f.calls.Load())
	}
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if r.Attempt["answer_text"] != "Use opens." || r.Attempt["state"] != "evaluation_failed" || r.Attempt["lease_token"] != nil {
		t.Fatal(r)
	}
}
func TestNativeInterpretationResumePositive(t *testing.T) {
	f := interpretationNative(t, "mapping-failure")
	state, e := f.interpret(t, uuid.NewString())
	if e == nil || state.Extraction == nil || state.Mapping != nil {
		t.Fatal(state, e)
	}
	old := *state.Extraction
	f.mode.Store("good")
	next, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if next.Status != "complete" || *next.Extraction != old || f.extracts.Load() != 1 {
		t.Fatal(next, f.extracts.Load())
	}
}
func TestNativeInterpretationConcurrentNegative(t *testing.T) {
	f := interpretationNative(t, "blocked")
	t.Cleanup(func() {
		select {
		case <-f.release:
		default:
			close(f.release)
		}
	})
	result := make(chan error, 1)
	go func() { _, e := f.interpret(t, uuid.NewString()); result <- e }()
	select {
	case <-f.entered:
	case err := <-result:
		t.Fatal("first evaluation failed before dispatch", err)
	}
	var active string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT o.state FROM operation o JOIN interpretation_checkpoint c ON c.operation_id=o.id WHERE c.attempt_id=$1", f.attempt).Scan(&active))
	if active != "running" {
		t.Fatal(active)
	}
	w := f.request("GET", "/api/v1/attempts/"+f.attempt+"/results", "", "", "")
	if w.Code != 200 || !strings.Contains(w.Body.String(), `"status":"evaluating"`) {
		t.Fatal(w.Code, w.Body.String())
	}
	_, e := f.interpret(t, uuid.NewString())
	if e != ErrEvaluationActive {
		t.Fatal(e)
	}
	close(f.release)
	requireListening(t, <-result)
	if f.extracts.Load() != 1 || f.maps.Load() != 1 {
		t.Fatal(f.calls.Load())
	}
}

func TestNativeInterpretationEmptyPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	f.attempt = f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), f.attempt, uuid.NewString(), 0, answerPacket("", "ru"), true)
	requireListening(t, e)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if state.Status != "complete" || f.calls.Load() != 0 {
		t.Fatal(state, f.calls.Load())
	}
	var m SemanticMapping
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), *state.Mapping, &m))
	if len(m.Decisions) != 0 {
		t.Fatal(m)
	}
	f.attempt = f.start(t)
	_, _, e = f.s.Store.WriteAnswer(context.Background(), f.attempt, uuid.NewString(), 0, answerPacket(" \t\n ", "en"), true)
	requireListening(t, e)
	whitespace, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	var x CanonicalExtraction
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), *whitespace.Extraction, &x))
	if len(x.Extraction.Coverage) != 1 || x.Extraction.Coverage[0].Kind != "whitespace" || x.Extraction.Coverage[0].Span.Start != 0 || x.Extraction.Coverage[0].Span.End != 4 || f.calls.Load() != 0 {
		t.Fatal(x, f.calls.Load())
	}

}
func TestNativeInterpretationBeforeSubmitNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	f.attempt = f.start(t)
	_, e := f.interpret(t, uuid.NewString())
	if e != ErrAttemptState || f.calls.Load() != 0 {
		t.Fatal(e, f.calls.Load())
	}
}
func TestNativeInterpretationReplayPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	key := uuid.NewString()
	first, e := f.interpret(t, key)
	requireListening(t, e)
	second, e := f.s.InterpretAttempt(context.Background(), f.attempt, key, 1, r.Attempt["answer_utf8_sha256"].(string), r.Attempt["configuration_sha256"].(string), f.model.Client())
	requireListening(t, e)
	if first.ID != second.ID || f.calls.Load() != 2 {
		t.Fatal(first, second, f.calls.Load())
	}
}
func TestNativeInterpretationRetryConflictNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	_, e = f.s.InterpretAttempt(context.Background(), f.attempt, uuid.NewString(), 1, strings.Repeat("0", 64), r.Attempt["configuration_sha256"].(string), f.model.Client())
	if e != ErrConflict || f.calls.Load() != 0 {
		t.Fatal(e, f.calls.Load())
	}
}
func TestNativeInterpretationFrozenSettingsNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	c, rev, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	c["llm_profiles"].([]any)[0].(map[string]any)["model"] = "changed-after-start"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	raw, _ := json.Marshal(c)
	_, _, e = f.s.Store.PutConfiguration(context.Background(), raw, uuid.NewString(), rev)
	requireListening(t, e)
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if state.Status != "complete" {
		t.Fatal(state)
	}
	f.mu.Lock()
	defer f.mu.Unlock()
	for _, wire := range f.wires {
		if wire["model"] != "constructed-interpreter" {
			t.Fatal("attempt silently adopted new model")
		}
	}
}
func TestNativeInterpretationAuditPositive(t *testing.T) {
	f := interpretationNative(t, "audit-good")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if state.Status != "complete" || state.Audit == nil || f.audits.Load() != 1 {
		t.Fatal(state, f.calls.Load())
	}
	f.mu.Lock()
	defer f.mu.Unlock()
	wire, _ := json.Marshal(f.wires[2])
	if strings.Contains(string(wire), "The present-tense verb should agree with its singular subject.") || strings.Contains(string(wire), "prior_decisions") {
		t.Fatal("auditor received first mapping output")
	}
}
func TestNativeInterpretationAuditUnavailableNegative(t *testing.T) {
	f := interpretationNative(t, "audit-retry-budget")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if state.Status != "complete" || state.Mapping == nil || state.Audit != nil || f.maps.Load() != 2 || f.audits.Load() != 1 {
		t.Fatal(state)
	}
	var issues []InterpretationIssue
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), state.Issues, &issues))
	if len(issues) != 1 || issues[0].Code != "audit_disagreement" || issues[0].Blocks {
		t.Fatal(issues)
	}
	f.mode.Store("good")
	next, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if next.Audit == nil || f.extracts.Load() != 1 || f.maps.Load() != 2 || f.audits.Load() != 2 {
		t.Fatal(next, f.calls.Load())
	}
	w := f.request("GET", "/api/v1/attempts/"+f.attempt+"/results", "", "", "")
	if w.Code != 200 || !strings.Contains(w.Body.String(), `"audit_status":"complete"`) || !strings.Contains(w.Body.String(), `"issues":[]`) {
		t.Fatal(w.Code, w.Body.String())
	}
}
func TestNativeInterpretationBlindContextPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	_, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	f.mu.Lock()
	defer f.mu.Unlock()
	wire, _ := json.Marshal(f.wires[0])
	for _, hidden := range []string{"ground_truth", "mutation_key:", "canonical_text", "surface_text", "The café opens tomorrow."} {
		if strings.Contains(string(wire), hidden) {
			t.Fatal("blind key disclosure", hidden)
		}
	}
	if !strings.Contains(string(wire), "Use opens.") {
		t.Fatal("missing original answer")
	}
}
func TestNativeInterpretationFullRegistryPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	var r InterpretationResources
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), state.Resources, &r))
	if len(r.Taxonomy) != 122 {
		t.Fatal(len(r.Taxonomy))
	}
	covered := map[string]bool{}
	for _, v := range r.Aliases {
		a := v.(map[string]any)
		for _, id := range a["target_ids"].([]any) {
			covered[id.(string)] = true
		}
	}
	projection := mappingTaxonomyContext(r, "Use opens.")
	if len(projection) != 122 {
		t.Fatal("taxonomy member dropped")
	}
	found := false
	for _, v := range projection {
		row := v.(map[string]any)
		if row["id"] == "grammar.verbs.subject_verb_agreement" {
			found = row["definition"] != "" && row["definition"] != nil
		}
	}
	if !found {
		t.Fatal("actual target definition omitted")
	}
	for _, v := range r.Taxonomy {
		if !covered[v.(map[string]any)["id"].(string)] {
			t.Fatal("missing alias context")
		}
	}
	f.mu.Lock()
	defer f.mu.Unlock()
	unusedAliasesOmitted := false
	declaredReference := false
	for _, message := range f.wires[1]["input"].([]any) {
		text, _ := message.(map[string]any)["content"].(string)
		if strings.HasPrefix(text, "Complete stage input: ") {
			var input map[string]any
			requireListening(t, json.Unmarshal([]byte(strings.TrimPrefix(text, "Complete stage input: ")), &input))
			aliases, _ := input["alias_entries"].([]any)
			unusedAliasesOmitted = len(aliases) == 0
		}
		if strings.HasPrefix(text, "extraction: ") {
			var frame map[string]any
			requireListening(t, json.Unmarshal([]byte(strings.TrimPrefix(text, "extraction: ")), &frame))
			refs, _ := frame["target_references"].([]any)
			if len(refs) == 1 {
				row := refs[0].(map[string]any)
				declaredReference = row["local_ref"] == "u1" && row["unit_id"] == "e1"
			}
		}
	}
	if !unusedAliasesOmitted {
		t.Fatal("unnamed category has no alias-data consumer")
	}
	if !declaredReference {
		t.Fatal("target alias was not declared on the provider wire")
	}
	mappingPrompt, _ := f.wires[1]["instructions"].(string)
	if !strings.Contains(mappingPrompt, "For EVERY supplied explanation") || !strings.Contains(mappingPrompt, "rubric overlap is not a judgment") {
		t.Fatal("authored full-reason assessment is missing from the shipped provider input")
	}

}
func TestNativeInterpretationWrongConfigurationNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	_, e = f.s.InterpretAttempt(context.Background(), f.attempt, uuid.NewString(), 1, r.Attempt["answer_utf8_sha256"].(string), strings.Repeat("0", 64), f.model.Client())
	if e != ErrConflict || f.calls.Load() != 0 {
		t.Fatal(e, f.calls.Load())
	}
}
func TestNativeInterpretationPublicPrivacyNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	_, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	w := f.request("GET", "/api/v1/attempts/"+f.attempt+"/results", "", "", "")
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	if _, _, e := contracts.Validate("result-envelope", "2.0.0", w.Body.Bytes()); e != nil {
		t.Fatal(e)
	}
	for _, hidden := range []string{"resources_asset_id", "receipt_ids", "context_snapshot_id", "provider_request_id", "wire_request", "credential_ref", "mapping_asset_id", "canonical_text"} {
		if strings.Contains(w.Body.String(), hidden) {
			t.Fatal("private result field", hidden)
		}
	}
	if !strings.Contains(w.Body.String(), `"decision":"matched_error"`) || !strings.Contains(w.Body.String(), `"score":null`) {
		t.Fatal(w.Body.String())
	}
}

func mustJSON(v any) []byte { b, _ := json.Marshal(v); return b }
func TestNativeInterpretationMalformedExtractionNegative(t *testing.T) {
	f := interpretationNative(t, "bad-extraction")
	state, e := f.interpret(t, uuid.NewString())
	if e == nil || state.Extraction != nil || state.Status != "failed" || f.extracts.Load() != 2 || f.maps.Load() != 0 {
		t.Fatal(state, e, f.calls.Load())
	}
}
func TestNativeInterpretationLateNegative(t *testing.T) {
	f := interpretationNative(t, "blocked")
	t.Cleanup(func() {
		select {
		case <-f.release:
		default:
			close(f.release)
		}
	})
	done := make(chan error, 1)
	go func() { _, e := f.interpret(t, uuid.NewString()); done <- e }()
	select {
	case <-f.entered:
	case err := <-done:
		t.Fatal("expected fixture stage returned before its blocking hook", err)
	}
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE interpretation_checkpoint SET deadline_at=clock_timestamp()-interval '1 second' WHERE attempt_id=$1", f.attempt)
	requireListening(t, e)
	close(f.release)
	if e = <-done; e == nil {
		t.Fatal("late output accepted")
	}
	state, e := f.s.Store.interpretationState(context.Background(), f.attempt)
	requireListening(t, e)
	if state.Extraction != nil || state.Mapping != nil || state.Status != "failed" {
		t.Fatal(state)
	}
	f.mode.Store("good")
	next, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if next.Status != "complete" || f.extracts.Load() != 2 {
		t.Fatal(next, f.extracts.Load())
	}
	lateAuditFinalizer(t)
}
func TestNativeInterpretationCancellationPositive(t *testing.T) {
	f := interpretationNative(t, "blocked")
	t.Cleanup(func() {
		select {
		case <-f.release:
		default:
			close(f.release)
		}
	})
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	done := make(chan error, 1)
	go func() {
		_, e := f.s.InterpretAttempt(ctx, f.attempt, uuid.NewString(), 1, r.Attempt["answer_utf8_sha256"].(string), r.Attempt["configuration_sha256"].(string), f.model.Client())
		done <- e
	}()
	select {
	case <-f.entered:
	case err := <-done:
		t.Fatal("expected fixture stage returned before its blocking hook", err)
	}
	cancel()
	if e = <-done; e == nil {
		t.Fatal("cancellation accepted")
	}
	close(f.release)
	f.mode.Store("good")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if state.Status != "complete" || f.extracts.Load() != 2 {
		t.Fatal(state, f.extracts.Load())
	}
}
func TestNativeInterpretationExpiredRecoveryPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	lease, e := f.s.Store.acquireInterpretation(context.Background(), f.attempt, uuid.NewString(), 1, r.Attempt["answer_utf8_sha256"].(string), r.Attempt["configuration_sha256"].(string))
	requireListening(t, e)
	// Test-owned DB time fixture models a crashed owner, not a claim of waiting 300 seconds.
	tx, e := beginWrite(context.Background(), f.s.Store)
	requireListening(t, e)
	a, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	a.Attempt["lease_expires_at"] = time.Now().Add(-time.Hour).UTC().Format(time.RFC3339Nano)
	a.Attempt["revision"] = float64(3)
	requireListening(t, f.s.Store.writeInterpretationAttempt(context.Background(), tx, a.Attempt, 2))
	requireListening(t, tx.Commit(context.Background()))
	next, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if next.Status != "complete" {
		t.Fatal(next)
	}
	_, e = f.s.Store.failInterpretationLease(context.Background(), lease, "STALE")
	if e != ErrEvaluationLease {
		t.Fatal("old owner finalized", e)
	}
	current, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if current.Attempt["lease_epoch"] != float64(2) || current.Attempt["state"] != "saved" {
		t.Fatal(current)
	}
}

func (f *nativeInterpretation) currentMode() string {
	if f.modePath != "" {
		if b, e := os.ReadFile(f.modePath); e == nil {
			return strings.TrimSpace(string(b))
		}
	}
	return f.mode.Load().(string)
}

func TestNativeInterpretationRestartPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	server := NewServer(f.s.Store, f.s.Origin, "")
	server.token = f.s.token
	f.s = server
	w := f.request("GET", "/api/v1/attempts/"+f.attempt+"/results", "", "", "")
	if w.Code != 200 || !strings.Contains(w.Body.String(), `"decision":"matched_error"`) || f.calls.Load() != 2 {
		t.Fatal(w.Code, w.Body.String())
	}
	saved, e := f.s.Store.interpretationState(context.Background(), f.attempt)
	requireListening(t, e)
	if saved.ID != state.ID {
		t.Fatal(saved)
	}
}
func TestNativeInterpretationAuditDiagnosticPositive(t *testing.T) {
	f := interpretationNative(t, "audit-disagreement")
	state, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	var issues []InterpretationIssue
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), state.Issues, &issues))
	if state.Status != "complete" || len(issues) != 1 || issues[0].Blocks {
		t.Fatal(state, issues)
	}
}
func TestNativeInterpretationAuditIndependenceNegative(t *testing.T) {
	f := interpretationNative(t, "audit-good")
	_, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	f.mu.Lock()
	defer f.mu.Unlock()
	wire := string(mustJSON(f.wires[2]))
	for _, forbidden := range []string{"prior_decisions", "The present-tense verb should agree with its singular subject."} {
		if strings.Contains(wire, forbidden) {
			t.Fatal("auditor received mapper finding", forbidden)
		}
	}
	if f.audits.Load() != 1 || f.maps.Load() != 1 {
		t.Fatal(f.calls.Load())
	}
}

func lateAuditFinalizer(t *testing.T) {
	f := interpretationNative(t, "audit-blocked")
	t.Cleanup(func() {
		select {
		case <-f.release:
		default:
			close(f.release)
		}
	})
	done := make(chan error, 1)
	go func() { _, e := f.interpret(t, uuid.NewString()); done <- e }()
	select {
	case <-f.entered:
	case err := <-done:
		t.Fatal("expected fixture stage returned before its blocking hook", err)
	}
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE interpretation_checkpoint SET deadline_at=clock_timestamp()-interval '1 second' WHERE attempt_id=$1", f.attempt)
	requireListening(t, e)
	close(f.release)
	if e = <-done; e == nil {
		t.Fatal("late finalizer accepted")
	}
	state, e := f.s.Store.interpretationState(context.Background(), f.attempt)
	requireListening(t, e)
	if state.Status != "failed" || state.Mapping == nil || state.Audit != nil {
		t.Fatal(state)
	}
	f.mode.Store("good")
	next, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	if next.Status != "complete" || f.extracts.Load() != 1 || f.maps.Load() != 1 {
		t.Fatal(next, f.calls.Load())
	}
}

func nativeAttachmentResult(t *testing.T, mode, want string) {
	t.Helper()
	f := interpretationNative(t, mode)
	state, err := f.interpret(t, uuid.NewString())
	requireListening(t, err)
	if state.Status != "complete" || state.Mapping == nil || f.calls.Load() != 2 {
		t.Fatal(state, f.calls.Load())
	}
	var mapping SemanticMapping
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), *state.Mapping, &mapping))
	if len(mapping.Groups) != 1 || len(mapping.Groups[0].Members) != 2 || mapping.Groups[0].Correction.Status != want || mapping.Decisions[1].Decision != "ignore" {
		t.Fatal("wrong persisted attachment semantics", mapping)
	}
	record, err := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, err)
	before := f.calls.Load()
	saved, err := f.s.Store.interpretationState(context.Background(), f.attempt)
	requireListening(t, err)
	view, err := f.s.Store.interpretationEnvelope(context.Background(), record, saved)
	requireListening(t, err)
	decisions := view["interpretation"].(map[string]any)["decisions"].([]any)
	if decisions[0].(map[string]any)["correction"].(map[string]any)["status"] != want || f.calls.Load() != before {
		t.Fatal("readback changed source semantics", view)
	}
	if mode == "attachment-retracted" && record.Attempt["answer_text"] != "The verb is wrong. Use opens. Withdraw that." {
		t.Fatal("source changed", record.Attempt)
	}
}
func TestNativeInterpretationEndorsedAttachmentPositive(t *testing.T) {
	nativeAttachmentResult(t, "attachment-kept", "accepted")
}
func TestNativeInterpretationWithdrawnAttachmentNegative(t *testing.T) {
	nativeAttachmentResult(t, "attachment-retracted", "not_supplied")
}

func TestNativeInterpretationRubricCompletenessPositive(t *testing.T) {
	f := interpretationNative(t, "rubric-repair")
	state, err := f.interpret(t, uuid.NewString())
	requireListening(t, err)
	if state.Status != "complete" || state.Mapping == nil || f.maps.Load() != 2 || f.calls.Load() != 3 {
		t.Fatal(state, f.calls.Load())
	}
	var m SemanticMapping
	requireListening(t, f.s.Store.readInterpretationJSON(context.Background(), *state.Mapping, &m))
	if m.Decisions[0].Explanation.Status != "accepted" || len(m.Decisions[0].Explanation.Satisfied) == 0 || m.Decisions[0].Correction.Status != "accepted" {
		t.Fatal(m)
	}
	f.mu.Lock()
	defer f.mu.Unlock()
	wire := f.wires[len(f.wires)-1]
	serialized := string(mustJSON(wire))
	if !strings.Contains(serialized, "Complete the supplied positive explanation assessment") || !strings.Contains(serialized, "Existing explanation rubric") {
		t.Fatal("repair omitted actionable scoped rubric")
	}
}
func TestNativeInterpretationRubricExhaustedNegative(t *testing.T) {
	f := interpretationNative(t, "rubric-exhausted")
	state, err := f.interpret(t, uuid.NewString())
	if err == nil || state.Status != "failed" || state.Mapping != nil || state.Extraction == nil || f.maps.Load() != 2 || f.calls.Load() != 3 {
		t.Fatal(state, err, f.calls.Load())
	}
	r, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	if r.Attempt["answer_text"] != "Use opens because the cafe is singular." || r.Attempt["state"] != "evaluation_failed" || r.Attempt["lease_token"] != nil {
		t.Fatal(r.Attempt)
	}
}
