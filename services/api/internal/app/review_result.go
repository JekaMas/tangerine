package app

// Application result preparation composes admitted semantic judgments with the
// pure numeric scorer. The storage finalizer receives already prepared data.
import (
	"context"
	"github.com/google/uuid"
)

type ReviewedResult struct {
	State    *InterpretationState
	Envelope map[string]any
	ID       string
}

func (s *Server) prepareReviewedResult(ctx context.Context, r *ReviewRun, f ReviewFrozen, resources InterpretationResources, mapping SemanticMapping, issues []InterpretationIssue) (ReviewedResult, error) {
	var state *InterpretationState
	var envelope map[string]any
	resultID := ""
	changed := r.Attempt != "" && (r.Resolution == "mapping_defect" || r.Resolution == "key_defect" || r.TargetCase != "" && r.Resolution == "supported")
	if changed {
		record := f.Record
		record.Attempt = reviewClone(record.Attempt)
		record.Attempt["case_version_id"] = resources.Key["case_version_id"]
		score, e := scoreInterpretation(record, resources, f.Extraction, mapping, issues)
		if e != nil {
			return ReviewedResult{}, e
		}
		envelope, e = s.Store.readScoringResult(ctx, r.BaseResult)
		if e != nil {
			return ReviewedResult{}, e
		}
		envelope["score"] = scoringJSON(score)
		envelope["status"] = score.Status
		envelope["feedback"] = nil
		envelope["feedback_status"] = "not_started"
		envelope["retry_operation"] = "retry_feedback"
		envelope["issues"] = publicInterpretationIssues(r.Attempt, issues)
		history := envelope["result_revision_ids"].([]any)
		history = append(history, r.BaseResult)
		envelope["result_revision_ids"] = history
		aux := reviewClone(envelope["auxiliary"])
		aux["case_version_id"] = resources.Key["case_version_id"]
		envelope["auxiliary"] = aux
		previous, e := s.Store.interpretationState(ctx, r.Attempt)
		if e != nil {
			return ReviewedResult{}, e
		}
		if previous == nil {
			return ReviewedResult{}, ErrAttemptState
		}
		next := *previous
		state = &next
		state.ID = uuid.NewString()
		state.Case = resources.Key["case_version_id"].(string)
		state.Status = score.Status
		state.Failure = nil
		state.FeedbackStatus = "not_started"
		state.Resources, e = s.Store.interpretationJSON(ctx, resources)
		if e != nil {
			return ReviewedResult{}, e
		}
		mapped, e := s.Store.interpretationJSON(ctx, mapping)
		if e != nil {
			return ReviewedResult{}, e
		}
		state.Mapping = &mapped
		state.Issues, e = s.Store.interpretationJSON(ctx, issues)
		if e != nil {
			return ReviewedResult{}, e
		}
		state.Stages, e = s.Store.interpretationJSON(ctx, r.Stages)
		if e != nil {
			return ReviewedResult{}, e
		}
		resultID = uuid.NewString()
		state.Result = &resultID
		envelope["result_id"] = resultID
		envelope["interpretation"] = publicInterpretation(state, f.Extraction, mapping, issues, r.Stages)
	}
	return ReviewedResult{State: state, Envelope: envelope, ID: resultID}, nil
}
