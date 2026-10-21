package app

import (
	"bytes"
	"net/http"
	"strings"
	"tangerine.local/api/internal/provider"
	"time"
)

func (s *Server) speechPlayback(w http.ResponseWriter, r *http.Request) {
	p, e := s.Store.Preparation(r.Context(), r.PathValue("id"))
	if e != nil {
		preparationHTTPError(w, 404, "NOT_FOUND")
		return
	}
	if p["phase_states"].(map[string]any)["render"] != "complete" {
		preparationHTTPError(w, 409, "AUDIO_NOT_READY")
		return
	}
	audio, e := s.Store.ReadAsset(r.Context(), p["audio_asset_id"].(string))
	if e != nil {
		preparationHTTPError(w, 503, "STORAGE_UNAVAILABLE")
		return
	}
	w.Header().Set("Content-Type", "audio/wav")
	w.Header().Set("Cache-Control", "no-store")
	http.ServeContent(w, r, "exercise.wav", time.Time{}, bytes.NewReader(audio))
}
func (s *Server) speechRender(w http.ResponseWriter, r *http.Request) {
	var input struct {
		PreparationID string `json:"preparation_id"`
		Attempt       int    `json:"render_attempt"`
	}
	if e := DecodeJSON(w, r, &input); e != nil {
		preparationHTTPError(w, 400, "INVALID_JSON")
		return
	}
	if input.PreparationID != r.PathValue("id") {
		preparationHTTPError(w, 400, "CONSTRAINT_CONFLICT")
		return
	}
	p, e := s.RenderPreparation(r.Context(), input.PreparationID, r.Header.Get("Idempotency-Key"), input.Attempt, nil)
	if e != nil {
		code, _ := speechPublicFailure(e)
		writeJSON(w, 422, map[string]any{"preparation": speechSummary(p), "code": code})
		return
	}
	writeJSON(w, 200, speechSummary(p))
}
func speechSummary(p map[string]any) map[string]any {
	if p == nil {
		return nil
	}
	summary := map[string]any{"id": p["id"], "revision": p["revision"], "phase_states": p["phase_states"], "audio_available": p["phase_states"].(map[string]any)["render"] == "complete", "last_failure": p["last_failure"]}
	counter, _ := p["render_progress_summary"].(map[string]any)
	if counter == nil {
		counter = speechProgressSummary(nil)
	}
	summary["render_progress_summary"] = map[string]any{"complete_pieces": counter["complete_pieces"], "total_pieces": counter["total_pieces"], "first_unfinished_piece_id": counter["first_unfinished_piece"], "ready_to_assemble": counter["ready_to_assemble"]}
	if profile, ok := p["selected_speech_profile"]; ok {
		summary["speech_profile_id"] = profile
	}
	for _, field := range []string{"canonical_word_count", "surface_word_count"} {
		if value, present := p[field]; present {
			summary[field] = value
		}
	}
	return summary
}

func speechPublicFailure(err error) (string, string) {
	code, _ := provider.SafeError(err)
	native := code
	switch code {
	case "PAID_USE_FORBIDDEN", "PROVIDER_QUOTA":
		code = "LOCAL_BUDGET_EXCEEDED"
	case "MODEL_SETUP_REQUIRED", "VOICE_SETUP_REQUIRED", "VOICE_UNAVAILABLE", "CAPABILITY_UNAVAILABLE", "ACOUSTIC_RENDER_REQUIRED", "MODEL_BINDING_MISMATCH", "ALIGNMENT_UNAVAILABLE", "ACOUSTIC_NOT_MEASURABLE":
		code = "CAPABILITY_UNQUALIFIED"
	case "AUDIO_FORMAT_INVALID", "AUDIO_SILENT":
		code = "PROVIDER_OUTPUT_INVALID"
	case "SPEECH_TIMEOUT":
		code = "DEADLINE_EXCEEDED"
	case "SPEECH_UNAVAILABLE":
		code = "INFRASTRUCTURE_UNAVAILABLE"
	case "PROVIDER_FAILED", "SYNTHESIS_FAILED":
		code = "PROVIDER_FAILURE"
	}
	return code, strings.ReplaceAll(strings.ToLower(native), "_", " ") + ". Saved text and completed audio pieces are retained."
}
