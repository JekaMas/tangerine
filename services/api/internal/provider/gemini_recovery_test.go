package provider

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"testing"
)

// Literal native error dialects; no hosted call or actual allowance exhaustion.
func TestGeminiTerminalRecoveryNegative(t *testing.T) {
	for _, tc := range []struct {
		name, body, want, private string
		status                    int
	}{
		{"authentication", `{"error":{"code":"authentication","message":"private key detail"}}`, "MISSING_CREDENTIALS", "authentication", 401},
		{"legacy_auth", `{"error":{"code":401,"status":"UNAUTHENTICATED"}}`, "MISSING_CREDENTIALS", "UNAUTHENTICATED", 401},
		{"payment", `{"error":{"code":"payment_required","message":"Buy credits private detail"}}`, "LOCAL_BUDGET_EXCEEDED", "payment_required", 402},
		{"permission", `{"error":{"code":"permission_denied","message":"private project detail"}}`, "CONSTRAINT_CONFLICT", "permission_denied", 403},
		{"legacy_permission", `{"error":{"code":403,"status":"PERMISSION_DENIED"}}`, "CONSTRAINT_CONFLICT", "PERMISSION_DENIED", 403},
		{"model", `{"error":{"code":"model_not_found","message":"private model detail"}}`, "CONSTRAINT_CONFLICT", "model_not_found", 404},
		{"quota", `{"error":{"code":"quota_exceeded","message":"private limit detail"}}`, "LOCAL_BUDGET_EXCEEDED", "quota_exceeded", 429},
		{"unknown_client", `{"error":{"code":"unrecognized","message":"private diagnostic"}}`, "PROVIDER_FAILURE", "unrecognized", 400},
	} {
		t.Run(tc.name, func(t *testing.T) {
			r, _, _ := executeFixture(t, nil, nil)
			r.Profile = geminiProfile()
			calls := 0
			client := &http.Client{Transport: trip(func(req *http.Request) (*http.Response, error) {
				calls++
				if req.URL.String() != GeminiEndpoint || req.Header.Get("x-goog-api-key") != "synthetic-key" {
					t.Fatal("provider/credential was substituted")
				}
				return &http.Response{StatusCode: tc.status, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(tc.body))}, nil
			})}
			_, attempts, err := Execute(context.Background(), client, r, "synthetic-key")
			code, private := SafeError(err)
			if code != tc.want || private != tc.private || calls != 1 || len(attempts) != 1 || string(attempts[0].Response.Raw) != tc.body || strings.Contains(err.Error(), "private") {
				t.Fatalf("terminal recovery: code=%s private=%s calls=%d err=%v", code, private, calls, err)
			}
		})
	}
}

func TestGeminiTransientRecoveryPositive(t *testing.T) {
	r, _, _ := executeFixture(t, nil, nil)
	r.Profile = geminiProfile()
	calls := 0
	var first string
	client := &http.Client{Transport: trip(func(req *http.Request) (*http.Response, error) {
		calls++
		wire, _ := io.ReadAll(req.Body)
		if calls == 1 {
			first = string(wire)
			return &http.Response{StatusCode: 503, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(`{"error":{"code":"service_unavailable","message":"private temporary detail"}}`))}, nil
		}
		if string(wire) != first || req.URL.String() != GeminiEndpoint {
			t.Fatal("retry altered the selected request")
		}
		body, _ := json.Marshal(map[string]any{"status": "completed", "steps": []any{map[string]any{"type": "model_output", "content": []any{map[string]any{"type": "text", "text": goodAnswer}}}}})
		return &http.Response{StatusCode: 200, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(string(body)))}, nil
	})}
	b, attempts, err := Execute(context.Background(), client, r, "synthetic-key")
	if err != nil || calls != 2 || len(attempts) != 2 || string(b) != goodAnswer {
		t.Fatal("transient same-request recovery failed", err, calls)
	}
}
