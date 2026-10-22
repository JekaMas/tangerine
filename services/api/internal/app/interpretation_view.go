package app

// Closed teacher projections are built only after submission. Provider records,
// bindings, credentials and native evidence identities stay private.
import (
	"context"
	"github.com/google/uuid"
	"strconv"
)

func publicSemanticComponent(j SemanticComponent, spans []AnswerSpan) map[string]any {
	texts := []string{}
	for _, s := range spans {
		texts = append(texts, s.Text)
	}
	additional := j.Additional
	if additional == nil {
		additional = []ComponentAssertion{}
	}
	return map[string]any{"supplied": j.Supplied, "status": j.Status, "source_texts": texts, "additional_assertions": additional}
}
func (s *Storage) interpretationEnvelope(ctx context.Context, record AttemptRecord, state *InterpretationState) (map[string]any, error) {
	envelope, err := s.interpretationContent(ctx, record, state)
	if err == nil {
		envelope["checking_stage"] = checkingStage(record, state)
	}
	return envelope, err
}

// A read-only projection of accepted checkpoints. This exposes no private IDs
// and cannot dispatch or resume evaluation.
func checkingStage(record AttemptRecord, state *InterpretationState) string {
	if state == nil {
		return "not_started"
	}
	if state.Status == "failed" {
		return "failed"
	}
	if state.Status != "running" && record.Attempt["state"] != "evaluating" {
		return "complete"
	}
	if state.Result != nil {
		return "feedback"
	}
	if state.Extraction == nil {
		return "extraction"
	}
	if state.Mapping == nil {
		return "matching"
	}
	configuration, _ := record.Context["configuration"].(map[string]any)
	if configuration["mapping_audit_enabled"] == true && state.Audit == nil {
		return "audit"
	}
	return "scoring"
}

func (s *Storage) interpretationContent(ctx context.Context, record AttemptRecord, state *InterpretationState) (map[string]any, error) {
	envelope := savedResult(record.Attempt)
	if selected, ok := record.Context["result_id"].(string); ok && selected != "" {
		return s.readScoringResult(ctx, selected)
	}
	if state != nil && state.Result != nil {
		return s.readScoringResult(ctx, *state.Result)
	}
	switch record.Attempt["state"] {
	case "evaluating":
		envelope["status"] = "evaluating"
	case "evaluation_failed":
		envelope["status"] = "evaluation_failed"
	case "review_required":
		envelope["status"] = "review_required"
	}
	if state == nil {
		return envelope, nil
	}
	claims := CanonicalExtraction{}
	mapping := SemanticMapping{}
	issues := []InterpretationIssue{}
	stages := []InterpretationStage{}
	for _, v := range []struct {
		id    string
		value any
	}{{optionalID(state.Extraction), &claims}, {optionalID(state.Mapping), &mapping}, {state.Issues, &issues}, {state.Stages, &stages}} {
		if v.id != "" {
			if e := s.readInterpretationJSON(ctx, v.id, v.value); e != nil {
				return nil, e
			}
		}
	}
	envelope["issues"] = publicInterpretationIssues(state.Attempt, issues)
	envelope["interpretation"] = publicInterpretation(state, claims, mapping, issues, stages)
	switch state.Status {
	case "failed":
		envelope["status"] = "evaluation_failed"
	case "review_required":
		envelope["status"] = "review_required"
	case "running":
		envelope["status"] = "evaluating"
	default:
		envelope["status"] = "saved"
	}

	return envelope, nil
}

func publicInterpretation(state *InterpretationState, claims CanonicalExtraction, mapping SemanticMapping, issues []InterpretationIssue, stages []InterpretationStage) map[string]any {
	publicClaims := []any{}
	byID := map[string]CanonicalClaim{}
	for _, c := range claims.Claims {
		byID[c.ID] = c
		publicClaims = append(publicClaims, map[string]any{"id": c.ID, "group_id": c.Group, "claim_span": c.Span, "stance": c.Stance, "active": c.Active})
	}
	decisions := []any{}
	for _, d := range mapping.Decisions {
		c := byID[d.Claim]
		decisions = append(decisions, map[string]any{"claim_id": d.Claim, "unit_id": d.Unit, "decision": d.Decision, "category_id": d.Category, "correction": publicSemanticComponent(d.Correction, c.Corrections), "explanation": publicSemanticComponent(d.Explanation, c.Explanations), "note": d.Note})
	}
	auditStatus := "not_run"
	if state.Audit != nil {
		auditStatus = "complete"
	}
	for _, stage := range stages {
		if stage.Stage == "mapping_audit" && state.Audit == nil {
			auditStatus = "failed"
		}
	}
	for _, issue := range issues {
		if issue.Code == "audit_disagreement" && auditStatus != "failed" {
			auditStatus = "disagreement"
		}
	}
	return map[string]any{"schema_version": "2.0.0", "status": state.Status, "claims": publicClaims, "decisions": decisions, "error_code": state.Failure, "audit_status": auditStatus}
}

func publicInterpretationIssues(attempt string, issues []InterpretationIssue) []any {
	public := []any{}
	for i, issue := range issues {
		if issue.Code == "audit_disagreement" && len(issue.Components) == 0 {
			continue
		}
		id := uuid.NewSHA1(uuid.NameSpaceOID, []byte(attempt+":"+issue.Code+":"+strconv.Itoa(i))).String()
		public = append(public, map[string]any{"schema_version": "2.0.0", "id": id, "code": issue.Code, "claim_ids": issue.Claims, "unit_ids": issue.Units, "evidence_ids": []any{}, "explanation": issue.Explanation, "blocks_final_score": issue.Blocks, "affected_components": issue.Components})
	}
	return public
}
