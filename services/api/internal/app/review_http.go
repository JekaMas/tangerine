package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"net/http"
	"strconv"
	"strings"
	"tangerine.local/api/internal/contracts"
)

func (s *Server) reviewCreate(w http.ResponseWriter, r *http.Request) {
	raw, e := attemptBody(w, r)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	var input struct {
		TargetCase string   `json:"target_case_version_id"`
		Purpose    string   `json:"purpose"`
		Case       string   `json:"case_version_id"`
		Attempt    string   `json:"attempt_id"`
		Result     string   `json:"result_id"`
		Audio      string   `json:"audio_sha256"`
		Statement  string   `json:"statement"`
		Claims     []string `json:"claim_ids"`
		Units      []string `json:"unit_ids"`
		Evidence   []string `json:"evidence_ids"`
	}
	if _, _, e = contracts.Validate("review-request", "2.0.0", raw); e != nil {
		attemptHTTPError(w, ErrInput)
		return
	}
	_ = json.Unmarshal(raw, &input)
	run, e := s.CreateReview(r.Context(), ReviewRun{TargetCase: input.TargetCase, Purpose: input.Purpose, Case: input.Case, Attempt: input.Attempt, BaseResult: input.Result, AudioSHA: input.Audio, Statement: input.Statement, Claims: input.Claims, Units: input.Units, Evidence: input.Evidence}, r.Header.Get("Idempotency-Key"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	writeJSON(w, 201, reviewView(run, nil))
}
func (s *Server) reviewRun(w http.ResponseWriter, r *http.Request) {
	if id, ok := strings.CutSuffix(r.PathValue("action"), ":reconsider"); ok {
		s.reconsiderReviewedKey(w, r, id)
		return
	}
	id, ok := strings.CutSuffix(r.PathValue("action"), ":run")
	if !ok {
		attemptHTTPError(w, ErrInput)
		return
	}
	revision, e := strconv.ParseInt(strings.Trim(r.Header.Get("If-Match"), "\""), 10, 64)
	if e != nil || revision < 0 {
		attemptHTTPError(w, ErrRevision)
		return
	}
	run, e := s.RunReview(r.Context(), id, r.Header.Get("Idempotency-Key"), revision, nil)
	if e != nil && run.ID == "" {
		attemptHTTPError(w, e)
		return
	}
	out := map[string]any(nil)
	if run.Output != "" {
		_ = s.Store.readInterpretationJSON(context.WithoutCancel(r.Context()), run.Output, &out)
	}
	status := 200
	if e != nil || run.Status == "failed" {
		status = 503
	}
	writeJSON(w, status, reviewView(run, out))
}
func (s *Server) reviewGet(w http.ResponseWriter, r *http.Request) {
	run, e := s.Store.Review(r.Context(), r.PathValue("id"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	var output map[string]any
	if run.Output != "" {
		if e = s.Store.readInterpretationJSON(r.Context(), run.Output, &output); e != nil {
			attemptHTTPError(w, e)
			return
		}
	}
	writeJSON(w, 200, reviewView(run, output))
}
func (s *Server) reviewList(w http.ResponseWriter, r *http.Request) {
	caseID, attemptID := r.URL.Query().Get("case_version_id"), r.URL.Query().Get("attempt_id")
	if caseID == "" && attemptID == "" {
		attemptHTTPError(w, ErrInput)
		return
	}
	for _, id := range []string{caseID, attemptID, r.URL.Query().Get("cursor")} {
		if id != "" {
			if _, e := uuid.Parse(id); e != nil {
				attemptHTTPError(w, ErrInput)
				return
			}
		}
	}
	rows, e := s.Store.DB.Query(r.Context(), "SELECT payload FROM review_checkpoint WHERE ($1='' OR case_version_id=$1) AND ($2='' OR attempt_id=$2) AND ($3='' OR id>$3) ORDER BY id LIMIT 51", caseID, attemptID, r.URL.Query().Get("cursor"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	defer rows.Close()
	items := []any{}
	next := ""
	for rows.Next() {
		var raw []byte
		var run ReviewRun
		if e = rows.Scan(&raw); e != nil {
			attemptHTTPError(w, e)
			return
		}
		_ = json.Unmarshal(raw, &run)
		if len(items) == 50 {
			next = items[49].(map[string]any)["id"].(string)
			break
		}
		items = append(items, reviewView(run, nil))
	}
	if e = rows.Err(); e != nil {
		attemptHTTPError(w, e)
		return
	}
	w.Header().Set("X-Tangerine-Next-Cursor", next)
	writeJSON(w, 200, items)
}
