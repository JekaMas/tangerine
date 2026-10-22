package provider

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"testing"
	"time"
)

func geminiProfile() Profile {
	p := planProfile()
	p.Provider, p.Auth, p.Billing = "gemini_interactions", "api_key", "free_tier"
	p.Endpoint, p.Model, p.Adapter = GeminiEndpoint, "gemini-3.8-flash", "gemini-interactions-v1"
	p.CredentialRef, p.Stream = "GEMINI_API_KEY", false
	return p
}

func TestGeminiWirePositive(t *testing.T) {
	p := geminiProfile()
	n := 8192
	p.MaxOutput = &n
	input := []any{map[string]any{"role": "user", "content": "Untrusted topic: café ☕"}}
	raw, err := Serialize(p, "Owned stage instruction", input, nil)
	var wire map[string]any
	_ = json.Unmarshal(raw, &wire)
	expected, _ := json.Marshal(input)
	if err != nil || wire["system_instruction"] != "Owned stage instruction" || wire["input"] != string(expected) || wire["store"] != false || wire["background"] != false || wire["stream"] != false || wire["generation_config"].(map[string]any)["max_output_tokens"] != float64(8192) {
		t.Fatal("native wire changed task or enabled persistence", err, string(raw))
	}
}

func TestGeminiPolicyNegative(t *testing.T) {
	for _, change := range []func(*Profile){func(p *Profile) { p.Billing = "metered" }, func(p *Profile) { p.Billing = "included_subscription" }, func(p *Profile) { p.Endpoint = "https://example.com/interactions" }, func(p *Profile) { p.Stream = true }, func(p *Profile) { p.Auth = "local_none" }} {
		p := geminiProfile()
		change(&p)
		if Included(p) == nil {
			t.Fatal("unsupported or non-free route admitted", p)
		}
	}
}

func TestGeminiStructuredWirePositive(t *testing.T) {
	raw, err := Serialize(geminiProfile(), "Owned", []any{}, map[string]any{"type": "json_schema", "schema": map[string]any{"type": "object"}})
	var wire map[string]any
	_ = json.Unmarshal(raw, &wire)
	f := wire["response_format"].(map[string]any)
	if err != nil || f["type"] != "text" || f["mime_type"] != "application/json" || f["schema"].(map[string]any)["type"] != "object" || wire["text"] != nil {
		t.Fatal("Responses format leaked into native Gemini wire", err, string(raw))
	}
}

func TestGeminiResponsePositive(t *testing.T) {
	body := `{"id":"interaction-one","status":"completed","model":"gemini-3.8-flash","steps":[{"type":"model_output","content":[{"type":"text","text":"first"}]},{"type":"model_output","content":[{"type":"text","text":" second"}]}],"usage":{"total_input_tokens":17,"total_output_tokens":4}}`
	client := &http.Client{Transport: trip(func(req *http.Request) (*http.Response, error) {
		if req.Header.Get("x-goog-api-key") != "synthetic-private-key" || req.Header.Get("Authorization") != "" || req.URL.String() != GeminiEndpoint {
			t.Fatal("incorrect native credential transport")
		}
		wire, _ := io.ReadAll(req.Body)
		if strings.Contains(string(wire), "synthetic-private-key") {
			t.Fatal("secret entered saved wire")
		}
		return &http.Response{StatusCode: 200, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(body))}, nil
	})}
	r, err := Exchange(context.Background(), client, geminiProfile(), []byte(`{}`), "synthetic-private-key")
	if err != nil || r.Outcome != "complete" || r.Visible != "first second" || *r.Usage["input_tokens"] != 17 || *r.Usage["output_tokens"] != 4 || r.Usage["cached_tokens"] != nil || *r.Model != "gemini-3.8-flash" || *r.RequestID != "interaction-one" || string(r.Raw) != body {
		t.Fatal("actual native content/usage lost", err, r)
	}
}

func TestGeminiIncompleteNegative(t *testing.T) {
	r := Response{Usage: map[string]*int64{}}
	err := r.geminiContent([]byte(`{"status":"in_progress","steps":[{"type":"model_output","content":[{"type":"text","text":"partial"}]}]}`))
	if err == nil || r.Outcome != "incomplete" || r.Visible != "partial" {
		t.Fatal("partial response was accepted", err, r)
	}
}

func TestGeminiQuotaNegative(t *testing.T) {
	calls := 0
	client := &http.Client{Transport: trip(func(req *http.Request) (*http.Response, error) {
		calls++
		return &http.Response{StatusCode: 429, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(`{"error":{"code":429,"status":"RESOURCE_EXHAUSTED"}}`))}, nil
	})}
	_, attempts, err := Execute(context.Background(), client, ExecuteRequest{Profile: geminiProfile(), Input: []any{map[string]any{"role": "user", "content": "Synthetic quota probe"}}, OutputKind: "answer-write", Timeout: time.Second}, "synthetic-key")
	code, _ := SafeError(err)
	if code != "LOCAL_BUDGET_EXCEEDED" || calls != 1 || len(attempts) != 1 {
		t.Fatal("quota retried or changed route", code, calls, len(attempts))
	}
}

func TestGeminiMissingCredentialNegative(t *testing.T) {
	calls := 0
	client := &http.Client{Transport: trip(func(req *http.Request) (*http.Response, error) { calls++; return nil, nil })}
	_, err := Exchange(context.Background(), client, geminiProfile(), []byte(`{}`), "")
	if err == nil || calls != 0 {
		t.Fatal("missing key dispatched", err, calls)
	}
}

func TestGeminiUnavailableNegative(t *testing.T) {
	err := geminiError([]byte(`{"error":{"code":"service_unavailable","message":"Private raw diagnostic"}}`), http.StatusServiceUnavailable)
	code, _ := SafeError(err)
	failure, ok := err.(*Failure)
	if code != "PROVIDER_FAILURE" || !ok || failure.ProviderCode != "service_unavailable" || strings.Contains(err.Error(), "Private raw diagnostic") {
		t.Fatal("native failure reason lost or raw body exposed", err)
	}
}
