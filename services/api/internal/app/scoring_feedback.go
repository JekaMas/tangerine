package app

// Feedback admission checks actual references and finding scope once. It never
// chooses or changes numerical credit; semantic prose remains the model's work.
import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"tangerine.local/api/internal/lab"
	"time"
)

func scoringFeedbackInput(record AttemptRecord, r InterpretationResources, c CanonicalExtraction, m SemanticMapping, envelope map[string]any) (map[string]any, map[string]any) {
	score := envelope["score"].(map[string]any)
	summary := map[string]any{}
	for _, field := range []string{"schema_version", "attempt_id", "case_version_id", "decision_set_sha256", "scoring_policy_version", "status", "counts", "composite", "optional_explanation", "items"} {
		summary[field] = score[field]
	}
	input := map[string]any{"schema_version": "2.0.0", "attempt_id": record.Attempt["attempt_id"], "result_id": envelope["result_id"], "requested_language": record.Context["requested_language"], "decisions": map[string]any{"schema_version": "1.0.0", "decisions": m.Decisions}, "ground_truth": r.Key, "rationales": r.Rationales, "issues": envelope["issues"], "score_result": summary, "extraction": c.Extraction}
	// Native matrices remain in the immutable result. This declared feedback DTO
	// includes all facts needed for comments, without asking an LLM to re-score.
	parts := map[string]any{"taxonomy": mappingTaxonomyContext(r, ""), "public_context": r.Key["public_context"], "mutation_key": "Use the complete ground_truth in Complete stage input, including actual repair/rationale propositions.", "answer": record.Attempt["answer_text"], "prior_decisions": map[string]any{"groups": m.Groups, "claims": c.Claims}, "scoring_result": "Use the native score_result facts in Complete stage input. Full numerical matrices remain stored under result_id; no recalculation or numeric commentary is requested."}
	return input, parts
}
func admitFeedback(raw []byte, record AttemptRecord, r InterpretationResources, m SemanticMapping, envelope map[string]any) (map[string]any, error) {
	var out map[string]any
	if e := json.Unmarshal(raw, &out); e != nil {
		return nil, e
	}
	if out["language"] != record.Context["requested_language"] {
		return nil, fmt.Errorf("use the requested response language")
	}
	allowed := map[string]map[string]bool{"decision_ids": {}, "unit_ids": {}, "issue_ids": {}, "rationale_ids": {}}
	for _, d := range m.Decisions {
		allowed["decision_ids"][d.Claim] = true
	}
	for _, v := range r.Key["units"].([]any) {
		allowed["unit_ids"][v.(map[string]any)["id"].(string)] = true
	}
	for _, v := range r.Rationales {
		allowed["rationale_ids"][v.(map[string]any)["id"].(string)] = true
	}
	for _, v := range envelope["issues"].([]any) {
		allowed["issue_ids"][v.(map[string]any)["id"].(string)] = true
	}
	for _, v := range out["items"].([]any) {
		item := v.(map[string]any)
		for field, ids := range allowed {
			for _, id := range item[field].([]any) {
				if !ids[id.(string)] {
					return nil, fmt.Errorf("feedback references unknown %s", field)
				}
			}
		}
		// New practice may address this saved result as a whole. It is not an
		// assertion that an additional mistake occurred in the recording.
		if item["kind"] != "recommendation" && len(item["unit_ids"].([]any))+len(item["decision_ids"].([]any))+len(item["issue_ids"].([]any)) == 0 {
			return nil, fmt.Errorf("ground each finding/recommendation in the supplied findings")
		}
		if item["kind"] == "missed" {
			if len(item["decision_ids"].([]any)) > 0 {
				return nil, fmt.Errorf("a missed item has no invented listener decision")
			}
			for _, id := range item["unit_ids"].([]any) {
				found := false
				for _, entry := range envelope["score"].(map[string]any)["items"].([]any) {
					u := entry.(map[string]any)
					found = found || (u["unit_id"] == id && (u["kind"] == "missed" || u["kind"] == "wrong_acceptance"))
				}
				if !found {
					return nil, fmt.Errorf("pending or detected units are not confirmed misses")
				}
			}
		}
	}
	// Coverage is a single output-admission obligation, not another model audit.
	// Grouped comments can cover several real units without repeating prose.
	covered := func(kind, field, id string) bool {
		for _, v := range out["items"].([]any) {
			item := v.(map[string]any)
			actual := item["kind"]
			// A source-bound factual comment may discuss the finding, repair
			// and optional reason together. Item labels are presentation hints.
			combined := actual == "detected" || actual == "correction" || actual == "explanation"
			component := actual != "recommendation" && actual != "missed"
			if actual != kind && !(kind == "detected" && combined || kind == "component" && component) {
				continue
			}
			for _, ref := range item[field].([]any) {
				if ref == id {
					return true
				}
			}
		}
		return false
	}
	needsPractice := false
	for _, v := range envelope["score"].(map[string]any)["items"].([]any) {
		item := v.(map[string]any)
		kind := item["kind"].(string)
		id := item["unit_id"].(string)
		if kind == "unjudged_control" {
			continue
		}
		if kind == "wrong_acceptance" {
			kind = "missed"
		}
		needsPractice = true
		if id != "" && !covered(kind, "unit_ids", id) {
			return nil, fmt.Errorf("include %s feedback for unit %s", kind, id)
		}
		if id == "" {
			for _, claim := range item["decision_ids"].([]any) {
				if !covered(kind, "decision_ids", claim.(string)) {
					return nil, fmt.Errorf("include %s feedback for claim %s", kind, claim)
				}
			}
		}
	}
	for _, g := range m.Groups {
		for _, component := range []struct {
			kind     string
			supplied bool
		}{{"correction", g.Correction.Supplied}, {"explanation", g.Explanation.Supplied}} {
			if component.supplied && !covered("component", "decision_ids", g.Representative) {
				return nil, fmt.Errorf("include factual feedback linked to supplied %s claim %s", component.kind, g.Representative)
			}
		}
	}
	if needsPractice {
		found := false
		for _, v := range out["items"].([]any) {
			found = found || v.(map[string]any)["kind"] == "recommendation"
		}
		if !found {
			return nil, fmt.Errorf("include actionable practice grounded in the findings")
		}
	}
	return out, nil
}
func (s *Server) scoringFeedback(ctx context.Context, lease InterpretationLease, r InterpretationResources, c CanonicalExtraction, m SemanticMapping, envelope map[string]any, client *http.Client, retry func() bool) (map[string]any, InterpretationStage, error) {
	stage := InterpretationStage{Stage: "feedback"}
	p, e := interpretationProfile(lease.Snapshot, "feedback")
	if e != nil {
		return nil, stage, e
	}
	input, parts := scoringFeedbackInput(lease.Snapshot, r, c, m, envelope)
	cap := min(40*time.Second, time.Until(lease.Deadline)-5*time.Second)
	if cap <= 0 {
		return nil, stage, context.DeadlineExceeded
	}
	var out map[string]any
	diagnostic := "Return concise source-bound factual comments covering the findings, supplied repairs and optional reasons. Related assessments may share one comment."
	result, e := s.InvokeLLM(ctx, LLMRequest{NormalizeProjection: func(v any) any {
		return normalizeFeedbackShape(v, lease.Snapshot.Context["requested_language"].(string))
	}, DiagnoseInvalid: func([]byte) string { return diagnostic }, FrozenProfile: &p, TransportRetry: retry, Timeout: cap, Stage: "feedback", Operation: OperationRequest{Name: "feedback", Key: interpretationCallKey(lease.Operation, "feedback"), Path: "/api/v1/attempts/" + lease.Attempt + "/feedback", Body: json.RawMessage(`{}`)}, Input: input, Components: parts, Configuration: lease.Snapshot.Context["configuration"].(map[string]any), Bundle: interpretationBundle(lease.Snapshot), Validate: func(raw []byte) error {
		var err error
		out, err = admitFeedback(raw, lease.Snapshot, r, m, envelope)
		if err != nil {
			diagnostic = err.Error()
			return interpretationInvalid(diagnostic)
		}
		return nil
	}}, client)
	stage.Result = result
	if len(result.ReceiptIDs) > 0 {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
		defer done()
		cfg := lease.Snapshot.Context["configuration"].(map[string]any)
		if diagnostic, err := s.Store.LLMDiagnostic(end, result, cfg["llm_lab_capture_content"] == true, cfg["llm_lab_trace_enabled"] == true); err == nil {
			stage.Diagnostic = &diagnostic.ID
		}
	}
	if e != nil {
		return nil, stage, e
	}
	out["origin"] = "llm"
	out["receipt_id"] = result.ReceiptIDs[len(result.ReceiptIDs)-1]
	return out, stage, nil
}

func scoringJSON(value any) map[string]any {
	raw, _ := lab.Canonical(value)
	var out map[string]any
	_ = json.Unmarshal(raw, &out)
	return out
}
