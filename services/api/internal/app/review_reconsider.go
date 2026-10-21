package app

// Reconsider only an explicit selected list using an already resolved same-audio
// key. Completed children are read on continuation; no background or bulk regrade.
import (
	"context"
	"encoding/json"
	"github.com/jackc/pgx/v5"
	"net/http"
	"strconv"
	"tangerine.local/api/internal/contracts"
)

func (s *Server) reconsiderReviewedKey(w http.ResponseWriter, r *http.Request, id string) {
	raw, e := attemptBody(w, r)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	if _, _, e = contracts.Validate("reconsider-request", "2.0.0", raw); e != nil {
		attemptHTTPError(w, ErrInput)
		return
	}
	var input struct {
		Dispute        string   `json:"dispute_id"`
		Attempts       []string `json:"attempt_ids"`
		Correspondence string   `json:"unit_correspondence_id"`
	}
	_ = json.Unmarshal(raw, &input)
	resolved, e := s.Store.Review(r.Context(), id)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	if resolved.Status != "complete" || resolved.NewCase == "" || resolved.Correspondence != input.Correspondence || input.Dispute != id {
		attemptHTTPError(w, ErrReference)
		return
	}
	root, e := s.Store.ReserveOperation(r.Context(), OperationRequest{Name: "reconsider_selected", Key: r.Header.Get("Idempotency-Key"), Path: "/api/v1/reviews/" + id + ":reconsider", Body: raw})
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	results := []any{}
	var callErr error
	for _, attempt := range input.Attempts {
		if e = r.Context().Err(); e != nil {
			callErr = e
			break
		}
		createKey := interpretationCallKey(root.ID, attempt+"/create")
		var child string
		e = s.Store.DB.QueryRow(r.Context(), "SELECT subject_id FROM operation WHERE operation_name='create_review' AND idempotency_key=$1", createKey).Scan(&child)
		var run ReviewRun
		if e == nil {
			run, e = s.Store.Review(r.Context(), child)
		} else if e == pgx.ErrNoRows {
			var record AttemptRecord
			record, e = s.Store.Attempt(r.Context(), attempt)
			if e == nil {
				base, ok := record.Context["result_id"].(string)
				if !ok || base == "" {
					e = ErrAttemptState
				} else {
					run, e = s.CreateReview(r.Context(), ReviewRun{Purpose: "answer_reconsideration", Case: record.Attempt["case_version_id"].(string), TargetCase: resolved.NewCase, Attempt: attempt, BaseResult: base}, createKey)
				}
			}
		}
		if e != nil {
			callErr = e
			break
		}
		if run.Status != "complete" {
			run, e = s.RunReview(r.Context(), run.ID, interpretationCallKey(root.ID, attempt+"/run/"+strconv.FormatInt(run.Revision, 10)), run.Revision, nil)
		}
		results = append(results, reviewView(run, nil))
		if e != nil {
			callErr = e
			break
		}
	}
	status := 200
	if callErr != nil {
		status = 503
	} else {
		end, cancel := context.WithTimeout(context.WithoutCancel(r.Context()), 5e9)
		_, e = s.Store.DB.Exec(end, "UPDATE operation SET state='complete',finished_at=clock_timestamp() WHERE id=$1", root.ID)
		cancel()
		if e != nil {
			status = 503
		}
	}
	writeJSON(w, status, map[string]any{"schema_version": "2.0.0", "reviews": results, "complete": status == 200})
}
