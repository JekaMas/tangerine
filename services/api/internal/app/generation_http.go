package app

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/provider"
)

// generateExercise coordinates existing stage owners. Each completed checkpoint
// is durable; reads and Resume never replace its frozen settings with current ones.
func (s *Server) generateExercise(w http.ResponseWriter, r *http.Request) {
	var input CanonicalPreparationRequest
	if e := DecodeJSON(w, r, &input); e != nil {
		preparationHTTPError(w, 400, "SCHEMA_INVALID")
		return
	}
	key := r.Header.Get("Idempotency-Key")
	if id, e := uuid.Parse(key); e != nil || id.Version() != 4 {
		preparationHTTPError(w, 400, "SCHEMA_INVALID")
		return
	}
	p, e := s.GenerateExercise(r.Context(), input, key)
	s.generationResponse(w, p, e)
}

func (s *Server) resumeExercise(w http.ResponseWriter, r *http.Request) {
	key := r.Header.Get("Idempotency-Key")
	if id, e := uuid.Parse(key); e != nil || id.Version() != 4 {
		preparationHTTPError(w, 400, "SCHEMA_INVALID")
		return
	}
	p, attempt, e := s.Store.resumePreparation(r.Context(), r.PathValue("id"), key)
	if e != nil {
		s.generationResponse(w, nil, e)
		return
	}
	raw, e := s.Store.ReadAsset(r.Context(), p["settings_asset_id"].(string))
	if e != nil {
		s.generationResponse(w, p, e)
		return
	}
	var frozen map[string]any
	_ = json.Unmarshal(raw, &frozen)
	id := p["id"].(string)
	input := CanonicalPreparationRequest{BlueprintID: frozen["blueprint"].(map[string]any)["id"].(string), ConfigurationSHA: frozen["configuration"].(map[string]any)["configuration_sha256"].(string), Sources: []string{}, Attempt: attempt, PreparationID: &id}
	p, e = s.GenerateExercise(r.Context(), input, key)
	s.generationResponse(w, p, e)
}
func (s *Server) generationResponse(w http.ResponseWriter, p map[string]any, e error) {
	if e == nil {
		writeJSON(w, 200, speechSummary(p))
		return
	}
	status, code := 503, "INFRASTRUCTURE_UNAVAILABLE"
	if errors.Is(e, context.DeadlineExceeded) {
		code = "DEADLINE_EXCEEDED"
	}
	if errors.Is(e, pgx.ErrNoRows) {
		status, code = 404, "NOT_FOUND"
	}
	if errors.Is(e, ErrConflict) || errors.Is(e, ErrRevision) {
		status, code = 409, "REVISION_STALE"
	}
	message := "Generation did not finish. Completed stages, if any, are saved. Refresh and Resume to continue."
	var failure *provider.Failure
	if errors.As(e, &failure) {
		code = failure.Code
		if failure.ProviderCode == "service_unavailable" || failure.ProviderCode == "UNAVAILABLE" {
			message = "Your LLM provider is temporarily unavailable. The exercise has not been completed. Completed stages, if any, are saved. Retry later."
		}
		if code == "LEASE_ACTIVE" {
			status = 409
		}
	}
	result := map[string]any{"code": code, "message": message, "retryable": true}
	if p != nil {
		result["preparation"] = speechSummary(p)
	}
	writeJSON(w, status, result)
}
