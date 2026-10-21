package app

import (
	"net/http"
	"strings"
)

func (s *Server) deletionCreate(w http.ResponseWriter, r *http.Request) {
	var input DeletionSelection
	if DecodeJSON(w, r, &input) != nil {
		preparationHTTPError(w, 400, "SCHEMA_INVALID")
		return
	}
	p, e := s.Store.PlanDeletion(r.Context(), input)
	if e != nil {
		preparationHTTPError(w, 422, "DELETION_PLAN_FAILED")
		return
	}
	writeJSON(w, 201, p)
}
func (s *Server) deletionApply(w http.ResponseWriter, r *http.Request) {
	id, ok := strings.CutSuffix(r.PathValue("action"), ":apply")
	if !ok {
		preparationHTTPError(w, 404, "NOT_FOUND")
		return
	}
	var input struct {
		Digest string `json:"confirmed_plan_sha256"`
	}
	if DecodeJSON(w, r, &input) != nil {
		preparationHTTPError(w, 400, "SCHEMA_INVALID")
		return
	}
	p, e := s.Store.ApplyDeletion(r.Context(), id, input.Digest)
	if e != nil {
		writeJSON(w, 409, map[string]any{"code": "DELETION_NOT_APPLIED", "message": "Deletion could not complete. Refresh the plan; active/shared records are retained. Retry pending byte cleanup explicitly.", "plan": p})
		return
	}
	writeJSON(w, 200, p)
}
