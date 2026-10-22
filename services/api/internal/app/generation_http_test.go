package app

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"tangerine.local/api/internal/provider"
	"testing"
)

func TestGenerationResponseSuccessPositive(t *testing.T) {
	s := &Server{}
	w := httptest.NewRecorder()
	s.generationResponse(w, map[string]any{"id": "saved-exercise", "phase_states": map[string]any{"canonical_text": "complete", "mutation": "complete", "render": "complete"}}, nil)
	var result map[string]any
	if err := json.Unmarshal(w.Body.Bytes(), &result); err != nil || w.Code != http.StatusOK || result["audio_available"] != true || result["id"] != "saved-exercise" || result["code"] != nil {
		t.Fatal("only completed audio is ready", err, w.Code, w.Body.String())
	}
}

func TestGenerationResponseProviderUnavailableNegative(t *testing.T) {
	w := httptest.NewRecorder()
	s := &Server{}
	s.generationResponse(w, nil, &provider.Failure{Code: "PROVIDER_FAILURE", ProviderCode: "service_unavailable"})
	var result map[string]any
	_ = json.Unmarshal(w.Body.Bytes(), &result)
	if w.Code != http.StatusServiceUnavailable || result["code"] != "PROVIDER_FAILURE" || !strings.Contains(result["message"].(string), "LLM provider is temporarily unavailable") || result["preparation"] != nil {
		t.Fatal("temporary provider failure hidden or content invented", w.Code, w.Body.String())
	}
}

func TestGenerationResponseFailureNegative(t *testing.T) {
	s := &Server{}
	w := httptest.NewRecorder()
	s.generationResponse(w, map[string]any{"id": "failed-exercise", "phase_states": map[string]any{"canonical_text": "failed", "mutation": "not_started", "render": "not_started"}}, context.DeadlineExceeded)
	var result map[string]any
	if err := json.Unmarshal(w.Body.Bytes(), &result); err != nil || w.Code != http.StatusServiceUnavailable || result["code"] != "DEADLINE_EXCEEDED" || result["retryable"] != true {
		t.Fatal("deadline must remain an explicit failure", err, w.Code, w.Body.String())
	}
	p := result["preparation"].(map[string]any)
	if p["audio_available"] != false || p["phase_states"].(map[string]any)["canonical_text"] != "failed" || strings.Contains(result["message"].(string), "Saved text, mutations and audio pieces are retained") {
		t.Fatal("failure invented completed content", w.Body.String())
	}
}
