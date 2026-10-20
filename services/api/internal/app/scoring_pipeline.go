package app

// The scoring controller composes pure scoring, durable results and optional
// feedback. Interpretation remains responsible only for semantic stage ordering.
import (
	"context"
	"net/http"
	"tangerine.local/api/internal/provider"
	"time"
)

func (s *Server) finalizeScoring(ctx, work context.Context, lease InterpretationLease, state *InterpretationState, resources InterpretationResources, extraction CanonicalExtraction, mapping SemanticMapping, issues []InterpretationIssue, stages *[]InterpretationStage, client *http.Client, retry func() bool, checkpoint func(bool) error) error {
	// Persist arithmetic before optional commentary. A resumed result uses this
	// immutable document; retrying feedback cannot invoke the numeric scorer again.
	if state.Result == nil {
		score, err := scoreInterpretation(lease.Snapshot, resources, extraction, mapping, issues)
		if err != nil {
			return err
		}
		state.Status = score.Status
		envelope := savedResult(lease.Snapshot.Attempt)
		envelope["score"] = scoringJSON(score)
		envelope["status"] = score.Status
		envelope["issues"] = publicInterpretationIssues(lease.Attempt, issues)
		envelope["interpretation"] = publicInterpretation(state, extraction, mapping, issues, *stages)
		envelope["retry_operation"] = "retry_feedback"
		envelope["auxiliary"], err = s.Store.scoringAuxiliary(work, lease.Snapshot.Attempt)
		if err != nil {
			return err
		}
		result, err := s.Store.saveScoringResult(work, envelope, nil)
		if err != nil {
			return err
		}
		state.Result = &result
		if err = checkpoint(false); err != nil {
			return err
		}
	}
	envelope, err := s.Store.readScoringResult(work, *state.Result)
	if err != nil {
		return err
	}
	state.Status, _ = envelope["status"].(string)
	if lease.Previous != nil && optionalID(lease.Previous.Audit) != optionalID(state.Audit) {
		envelope["interpretation"] = publicInterpretation(state, extraction, mapping, issues, *stages)
		envelope["issues"] = publicInterpretationIssues(lease.Attempt, issues)
		result, e := s.Store.saveScoringResult(work, envelope, state.Result)
		if e != nil {
			return e
		}
		state.Result = &result
	}
	if envelope["feedback_status"] != "complete" {
		feedback, stage, feedbackErr := s.scoringFeedback(work, lease, resources, extraction, mapping, envelope, client, retry)
		if feedbackErr != nil {
			stage.Error, _ = provider.SafeError(feedbackErr)
			envelope["feedback_status"] = "unavailable"
			envelope["retry_operation"] = "retry_feedback"
		} else {
			envelope["feedback"] = feedback
			envelope["feedback_status"] = "complete"
			envelope["retry_operation"] = nil
		}
		*stages = append(*stages, stage)
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
		result, saveErr := s.Store.saveScoringResult(end, envelope, state.Result)
		done()
		if saveErr != nil {
			return saveErr
		}
		state.Result = &result
	}
	state.FeedbackStatus, _ = envelope["feedback_status"].(string)
	return nil
}
