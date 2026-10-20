package app

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/provider"
	"time"
)

func (s *Server) attemptInterpretationRetry(w http.ResponseWriter, r *http.Request) {
	revision, e := strconv.ParseInt(strings.Trim(r.Header.Get("If-Match"), "\""), 10, 64)
	if e != nil || revision < 0 {
		attemptHTTPError(w, ErrRevision)
		return
	}
	raw, e := attemptBody(w, r)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	var input map[string]any
	if json.Unmarshal(raw, &input) != nil {
		attemptHTTPError(w, ErrInput)
		return
	}
	projected, _ := json.Marshal(map[string]any{"answer_sha256": input["answer_sha256"], "configuration_sha256": input["configuration_sha256"]})
	if _, _, e = contracts.Validate("retry-request", "2.0.0", projected); e != nil {
		attemptHTTPError(w, ErrInput)
		return
	}
	feedbackOnly := strings.HasSuffix(r.URL.Path, ":retry-feedback")
	state, e := s.interpretAttempt(r.Context(), r.PathValue("id"), r.Header.Get("Idempotency-Key"), revision, input["answer_sha256"].(string), input["configuration_sha256"].(string), nil, feedbackOnly)
	s.interpretationResponse(w, r, state, e)
}
func (s *Server) interpretationResponse(w http.ResponseWriter, r *http.Request, state InterpretationState, callErr error) {
	if callErr != nil && (state.ID == "" || errors.Is(callErr, ErrEvaluationLease)) {
		attemptHTTPError(w, callErr)
		return
	}
	end, done := context.WithTimeout(context.WithoutCancel(r.Context()), 5*time.Second)
	defer done()
	record, e := s.Store.Attempt(end, r.PathValue("id"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	envelope, e := s.Store.interpretationEnvelope(end, record, &state)
	if e != nil {
		if callErr == nil {
			attemptHTTPError(w, e)
			return
		}
		// Submission already committed. Dependency loss must not tell the browser
		// that its frozen answer was never saved. Return the minimal durable state.
		minimal := state
		minimal.Extraction = nil
		minimal.Mapping = nil
		minimal.Issues = ""
		minimal.Stages = ""
		envelope, _ = s.Store.interpretationEnvelope(end, record, &minimal)
	}
	attemptETag(w, record.Attempt)
	status := 200
	if callErr != nil {
		code, _ := provider.SafeError(callErr)
		status = 503
		if code == "PROVIDER_OUTPUT_INVALID" {
			status = 502
		}
		if errors.Is(callErr, context.DeadlineExceeded) {
			status = 504
		}
	}
	writeJSON(w, status, envelope)
}
