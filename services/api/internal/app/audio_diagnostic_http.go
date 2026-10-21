package app

import (
	"errors"
	"github.com/jackc/pgx/v5"
	"net/http"
	"tangerine.local/api/internal/provider"
)

func (s *Server) audioDiagnosticList(w http.ResponseWriter, r *http.Request) {
	value, err := s.Store.listAudioDiagnostics(r.Context(), r.PathValue("id"), r.URL.Query().Get("after"))
	if err != nil {
		writeJSON(w, 503, map[string]any{"code": "INFRASTRUCTURE_UNAVAILABLE"})
		return
	}
	writeJSON(w, 200, value)
}
func (s *Server) audioDiagnosticCreate(w http.ResponseWriter, r *http.Request) {
	var request AudioMeasureRequest
	if err := DecodeJSON(w, r, &request); err != nil || request.Case != r.PathValue("id") {
		writeJSON(w, 400, map[string]any{"code": "INVALID_JSON"})
		return
	}
	value, err := s.MeasureCase(r.Context(), request, r.Header.Get("Idempotency-Key"), nil)
	if err == nil {
		writeJSON(w, 200, value)
		return
	}
	code, _ := provider.SafeError(err)
	status := 422
	if errors.Is(err, ErrAttemptRights) {
		code = "SOURCE_USE_RESTRICTED"
	}
	if errors.Is(err, ErrRevision) {
		code = "REVISION_STALE"
		status = 409
	}
	if errors.Is(err, ErrInput) {
		code = "SCHEMA_INVALID"
	}
	if errors.Is(err, pgx.ErrNoRows) {
		code = "NOT_FOUND"
		status = 404
	}
	writeJSON(w, status, map[string]any{"code": code, "diagnostic": value, "message": "Diagnostic unavailable. Saved audio, answers and scores are retained."})
}
