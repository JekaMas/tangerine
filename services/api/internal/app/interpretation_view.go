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
	envelope := savedResult(record.Attempt)
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
	publicIssues := []any{}
	for i, issue := range issues {
		if issue.Code == "audit_disagreement" && auditStatus != "failed" {
			auditStatus = "disagreement"
		}
		id := uuid.NewSHA1(uuid.NameSpaceOID, []byte(state.ID+":"+issue.Code+":"+strconv.Itoa(i))).String()
		publicIssues = append(publicIssues, map[string]any{"schema_version": "2.0.0", "id": id, "code": issue.Code, "claim_ids": issue.Claims, "unit_ids": issue.Units, "evidence_ids": []any{}, "explanation": issue.Explanation, "blocks_final_score": issue.Blocks, "affected_components": issue.Components})
	}
	envelope["issues"] = publicIssues
	envelope["interpretation"] = map[string]any{"schema_version": "2.0.0", "status": state.Status, "claims": publicClaims, "decisions": decisions, "error_code": state.Failure, "audit_status": auditStatus}
	// The semantic handoff does not manufacture the next iteration's score.
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
