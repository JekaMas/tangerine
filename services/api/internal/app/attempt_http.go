package app

import (
	"bytes"
	"errors"
	"github.com/jackc/pgx/v5"
	"io"
	"net/http"
	"strconv"
	"strings"
	"tangerine.local/api/internal/provider"
	"time"
)

func attemptHTTPError(w http.ResponseWriter, e error) {
	status, code := 503, "INFRASTRUCTURE_UNAVAILABLE"
	switch {
	case errors.Is(e, ErrEvaluationActive):
		status, code = 409, "EVALUATION_ACTIVE"
	case errors.Is(e, ErrEvaluationLease):
		status, code = 409, "EVALUATION_LEASE_STALE"
	case errors.Is(e, ErrInput):
		status, code = 400, "INVALID_JSON"
	case errors.Is(e, ErrCapacity):
		status, code = 413, "INPUT_CAPACITY_EXCEEDED"
	case errors.Is(e, ErrRevision):
		status, code = 412, "REVISION_STALE"
	case errors.Is(e, ErrConflict):
		status, code = 409, "IDEMPOTENCY_CONFLICT"
	case errors.Is(e, ErrAttemptState):
		status, code = 409, "INVALID_TRANSITION"
	case errors.Is(e, ErrCaseUnavailable):
		status, code = 409, "CASE_UNAVAILABLE"
	case errors.Is(e, pgx.ErrNoRows):
		status, code = 404, "NOT_FOUND"
	}
	var failure *provider.Failure
	if errors.As(e, &failure) {
		status, code = 409, "CAPABILITY_UNQUALIFIED"
	}
	preparationHTTPError(w, status, code)
}
func attemptBody(w http.ResponseWriter, r *http.Request) ([]byte, error) {
	if r.Header.Get("Content-Type") != "application/json" {
		return nil, ErrInput
	}
	b, e := io.ReadAll(http.MaxBytesReader(w, r.Body, 256*1024))
	if e != nil {
		return nil, ErrCapacity
	}
	return b, nil
}
func attemptETag(w http.ResponseWriter, a map[string]any) {
	w.Header().Set("ETag", strconv.Quote(strconv.Itoa(int(a["revision"].(float64)))))
	w.Header().Set("X-Tangerine-Audio-SHA256", a["audio_sha256"].(string))
	w.Header().Set("X-Tangerine-Answer-SHA256", a["answer_utf8_sha256"].(string))
	w.Header().Set("X-Tangerine-Configuration-SHA256", a["configuration_sha256"].(string))
}
func (s *Server) attemptStart(w http.ResponseWriter, r *http.Request) {
	raw, e := attemptBody(w, r)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	v, e := s.Store.StartAttempt(r.Context(), raw, r.Header.Get("Idempotency-Key"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	record, e := s.Store.Attempt(r.Context(), v["attempt_id"].(string))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	attemptETag(w, record.Attempt)
	writeJSON(w, 201, v)
}
func (s *Server) attemptGet(w http.ResponseWriter, r *http.Request) {
	v, e := s.Store.Attempt(r.Context(), r.PathValue("id"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	attemptETag(w, v.Attempt)
	writeJSON(w, 200, attemptView(v.Attempt, v.Context))
}
func (s *Server) attemptAnswer(w http.ResponseWriter, r *http.Request, submit bool) {
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
	a, op, e := s.Store.WriteAnswer(r.Context(), r.PathValue("id"), r.Header.Get("Idempotency-Key"), revision, raw, submit)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	attemptETag(w, a)
	if submit {
		state, callErr := s.InterpretAttempt(r.Context(), r.PathValue("id"), r.Header.Get("Idempotency-Key"), int64(a["revision"].(float64)), a["answer_utf8_sha256"].(string), a["configuration_sha256"].(string), nil)
		s.interpretationResponse(w, r, state, callErr)
	} else {
		writeJSON(w, 200, attemptOperation(op, a))
	}
}
func (s *Server) attemptPlaybackEvent(w http.ResponseWriter, r *http.Request) {
	raw, e := attemptBody(w, r)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	v, e := s.Store.RecordPlayback(r.Context(), r.PathValue("id"), r.Header.Get("Idempotency-Key"), raw)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	writeJSON(w, 200, v)
}
func (s *Server) attemptAudio(w http.ResponseWriter, r *http.Request) {
	audio, sha, e := s.Store.AttemptAudio(r.Context(), r.PathValue("id"))
	if e != nil {
		if errors.Is(e, ErrAttemptRights) {
			preparationHTTPError(w, 403, "RIGHTS_BLOCKED")
		} else if errors.Is(e, ErrUnavailable) {
			preparationHTTPError(w, 503, "STORAGE_UNAVAILABLE")
		} else {
			attemptHTTPError(w, e)
		}
		return
	}
	if strings.Contains(r.Header.Get("Range"), ",") {
		w.Header().Set("Content-Range", "bytes */"+strconv.Itoa(len(audio)))
		w.WriteHeader(416)
		return
	}
	w.Header().Set("Content-Type", "audio/wav")
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("ETag", strconv.Quote(sha))
	http.ServeContent(w, r, "exercise.wav", time.Time{}, bytes.NewReader(audio))
}
func (s *Server) attemptList(w http.ResponseWriter, r *http.Request) {
	limit := 50
	if raw := r.URL.Query().Get("limit"); raw != "" {
		n, e := strconv.Atoi(raw)
		if e != nil {
			attemptHTTPError(w, ErrInput)
			return
		}
		limit = n
	}
	rows, next, e := s.Store.AttemptHistory(r.Context(), limit, r.URL.Query().Get("cursor"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	w.Header().Set("X-Tangerine-Next-Cursor", next)
	writeJSON(w, 200, rows)
}
func (s *Server) attemptResults(w http.ResponseWriter, r *http.Request) {
	v, e := s.Store.Attempt(r.Context(), r.PathValue("id"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	if v.Attempt["submitted_at"] == nil {
		attemptHTTPError(w, ErrAttemptState)
		return
	}
	state, e := s.Store.interpretationState(r.Context(), r.PathValue("id"))
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	envelope, e := s.Store.interpretationEnvelope(r.Context(), v, state)
	if e != nil {
		attemptHTTPError(w, e)
		return
	}
	writeJSON(w, 200, envelope)
}
