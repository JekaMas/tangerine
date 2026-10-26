package provider

import (
	"encoding/json"
	"strings"
	"tangerine.local/api/internal/contracts"
)

const GeminiEndpoint = "https://generativelanguage.googleapis.com/v1beta/interactions"

// Gemini uses its native Interactions wire. The shared owner still records the
// exact request, response, admission, retry policy and operation lineage.
func serializeGemini(p Profile, instructions string, input []any, format any) ([]byte, error) {
	data, err := json.Marshal(input)
	if err != nil {
		return nil, err
	}
	config := map[string]any{}
	if p.MaxOutput != nil {
		config["max_output_tokens"] = *p.MaxOutput
	}
	if p.Temperature != nil {
		config["temperature"] = *p.Temperature
	}
	wire := map[string]any{"model": p.Model, "system_instruction": instructions, "input": string(data), "store": false, "stream": false, "background": false, "tools": []any{}, "generation_config": config}
	if f, ok := format.(map[string]any); ok {
		if schema, present := f["schema"]; present {
			wire["response_format"] = map[string]any{"type": "text", "mime_type": "application/json", "schema": schema}
		}
	}
	raw, err := json.Marshal(wire)
	if err != nil {
		return nil, err
	}
	return contracts.Canonical(raw)
}

func geminiError(raw []byte, status int) error {
	var body struct {
		Error struct {
			Status string
			Code   json.RawMessage
		}
	}
	_ = json.Unmarshal(raw, &body)
	code := body.Error.Status
	if code == "" {
		_ = json.Unmarshal(body.Error.Code, &code)
	}
	// Interactions returns lowercase error.code; older Google errors carry an
	// uppercase error.status. Keep the private native reason and use the existing
	// public categories so callers never mistake setup/budget errors for outages.
	reason := strings.ToLower(code)
	if status == 402 || status == 429 || reason == "resource_exhausted" || reason == "payment_required" || reason == "quota_exceeded" || reason == "rate_limit_exceeded" || reason == "too_many_requests" {
		return &Failure{Code: "LOCAL_BUDGET_EXCEEDED", ProviderCode: code}
	}
	if status == 401 || reason == "unauthenticated" || reason == "authentication" {
		return &Failure{Code: "MISSING_CREDENTIALS", ProviderCode: code}
	}
	if status == 403 || reason == "permission_denied" || reason == "model_not_found" {
		return &Failure{Code: "CONSTRAINT_CONFLICT", ProviderCode: code}
	}
	return &Failure{Code: "PROVIDER_FAILURE", ProviderCode: code}
}

func (r *Response) geminiContent(raw []byte) error {
	var v struct {
		Status string
		Model  string
		ID     string
		Steps  []struct {
			Type    string
			Content []struct{ Type, Text string }
		}
		Usage map[string]json.RawMessage
	}
	if json.Unmarshal(raw, &v) != nil {
		return fail("PROVIDER_INCOMPLETE")
	}
	if v.Model != "" {
		r.Model = &v.Model
	}
	if v.ID != "" {
		r.RequestID = &v.ID
	}
	var visible strings.Builder
	for _, step := range v.Steps {
		if step.Type != "model_output" {
			continue
		}
		for _, part := range step.Content {
			if part.Type == "text" {
				visible.WriteString(part.Text)
			}
		}
	}
	r.Visible = visible.String()
	if v.Status != "completed" {
		r.Outcome = "incomplete"
		return fail("PROVIDER_INCOMPLETE")
	}
	for source, target := range map[string]string{"total_input_tokens": "input_tokens", "total_output_tokens": "output_tokens", "total_thought_tokens": "reasoning_tokens", "total_cached_tokens": "cached_tokens"} {
		var value *int64
		if json.Unmarshal(v.Usage[source], &value) == nil && value != nil && *value >= 0 {
			r.Usage[target] = value
		}
	}
	r.Outcome = "complete"
	return nil
}
