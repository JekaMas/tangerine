package provider

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func planProfile() Profile {
	return Profile{ID: "chatgpt-plan-responses-v1", Provider: "openai_chatgpt", Model: "gpt-6.1-sol", Endpoint: "https://api.openai.com/v1/responses", ContextBudget: 128000, Adapter: "chatgpt-plan-responses-v1", CredentialRef: "chatgpt:selected-registration", Stream: true, Tools: []any{}, Roles: []string{"case_generation"}, Auth: "chatgpt_plan_oauth", Billing: "included_subscription"}
}
func TestProviderWirePositive(t *testing.T) {
	p := planProfile()
	b, e := Serialize(p, "Owned instruction", []any{map[string]any{"role": "user", "content": "Untrusted data"}}, nil)
	if e != nil {
		t.Fatal(e)
	}
	expected := `{"input":[{"content":"Untrusted data","role":"user"}],"instructions":"Owned instruction","model":"gpt-6.1-sol","store":false,"stream":true,"tools":[]}`
	if string(b) != expected {
		t.Fatal(string(b))
	}
}
func TestProviderWireReasoningPositive(t *testing.T) {
	p := planProfile()
	effort := "low"
	p.Reasoning = &effort
	b, e := Serialize(p, "", []any{}, nil)
	if e != nil || !strings.Contains(string(b), `"reasoning":{"effort":"low"}`) {
		t.Fatal(e, string(b))
	}
}
func TestProviderWireUnsupportedNegative(t *testing.T) {
	p := planProfile()
	x := 0.5
	p.Temperature = &x
	if _, e := Serialize(p, "", []any{}, nil); e == nil {
		t.Fatal("preview temperature passed")
	}
	p = planProfile()
	n := 100
	p.MaxOutput = &n
	if _, e := Serialize(p, "", []any{}, nil); e == nil {
		t.Fatal("preview cap passed")
	}
}
func TestProviderWireSystemNegative(t *testing.T) {
	if _, e := Serialize(planProfile(), "", []any{map[string]any{"role": "system", "content": "bad"}}, nil); e == nil {
		t.Fatal("explicit system passed")
	}
}
func TestProviderLocalPolicyPositive(t *testing.T) {
	p := planProfile()
	p.Provider = "local_responses"
	p.Endpoint = "http://127.0.0.1:11434/v1/responses"
	p.Auth = "local_none"
	p.Billing = "local"
	if e := Included(p); e != nil {
		t.Fatal(e)
	}
}
func TestProviderIncludedProfilePositive(t *testing.T) {
	p := planProfile()
	before, _ := json.Marshal(p)
	if e := Included(p); e != nil {
		t.Fatal(e)
	}
	after, _ := json.Marshal(p)
	if string(before) != string(after) {
		t.Fatal("profile changed")
	}
}
func TestProviderMeteredNegative(t *testing.T) {
	for _, mode := range []string{"metered", "unknown", ""} {
		p := planProfile()
		p.Provider = "deepseek"
		p.Endpoint = "https://api.deepseek.com/responses"
		p.Auth = "api_key"
		p.Billing = mode
		if e := Included(p); e == nil {
			t.Fatal("metered/unknown accepted", mode)
		}
	}
}
func TestProviderBillingFallbackNegative(t *testing.T) {
	p := planProfile()
	p.Endpoint = "https://chatgpt.com/backend-api/responses"
	if e := Included(p); e == nil {
		t.Fatal("private backend accepted")
	}
	p = planProfile()
	p.Provider = "unsupported"
	if e := Included(p); e == nil {
		t.Fatal("invented adapter")
	}
}

type trip func(*http.Request) (*http.Response, error)

func (f trip) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }

type wireObservation struct {
	Body, Auth, Endpoint string
	Calls                int
}

func boundaryClient(t *testing.T, status int, body string) (*http.Client, *wireObservation) {
	t.Helper()
	seen := &wireObservation{}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		b, _ := io.ReadAll(r.Body)
		seen.Body = string(b)
		seen.Auth = r.Header.Get("Authorization")
		seen.Calls++
		w.Header().Set("x-request-id", "fixture-request-17")
		w.WriteHeader(status)
		io.WriteString(w, body)
	}))
	t.Cleanup(server.Close)
	underlying := server.Client().Transport
	client := &http.Client{Transport: trip(func(req *http.Request) (*http.Response, error) {
		seen.Endpoint = req.URL.String()
		copy := req.Clone(req.Context())
		u := *req.URL
		copy.URL = &u
		target, _ := http.NewRequest("POST", server.URL, nil)
		copy.URL.Scheme = target.URL.Scheme
		copy.URL.Host = target.URL.Host
		return underlying.RoundTrip(copy)
	})}
	return client, seen
}

const completed = `data: {"type":"response.output_text.delta","delta":"{\"answer_text\":\"ok\",\"requested_language\":\"en\"}"}

data: {"type":"response.completed","response":{"status":"completed","model":"gpt-6.1-sol","output":[],"usage":{"input_tokens":17,"output_tokens":5,"input_tokens_details":{"cached_tokens":3},"output_tokens_details":{"reasoning_tokens":2}}}}

`

func send(t *testing.T, status int, body string) (Response, error, *wireObservation) {
	t.Helper()
	client, seen := boundaryClient(t, status, body)
	p := planProfile()
	wire, e := Serialize(p, "Owned", []any{map[string]any{"role": "user", "content": "data"}}, nil)
	if e != nil {
		t.Fatal(e)
	}
	out, e := Exchange(context.Background(), client, p, wire, "fixture-access-secret")
	return out, e, seen
}
func TestProviderCompletedStreamPositive(t *testing.T) {
	r, e, seen := send(t, 200, completed)
	if e != nil || r.Outcome != "complete" || r.Visible != `{"answer_text":"ok","requested_language":"en"}` || *r.Usage["input_tokens"] != 17 || *r.Usage["cached_tokens"] != 3 || *r.RequestID != "fixture-request-17" || seen.Calls != 1 {
		t.Fatal(e, r, seen)
	}
	if strings.Contains(string(r.Raw), "fixture-access-secret") {
		t.Fatal("credential in response artifact")
	}
}
func TestProviderCompletedOutputPositive(t *testing.T) {
	r, e, _ := send(t, 200, "data: {\"type\":\"response.completed\",\"response\":{\"status\":\"completed\",\"model\":\"returned-model\",\"output\":[{\"type\":\"message\",\"content\":[{\"type\":\"output_text\",\"text\":\"final\"}]},{\"type\":\"reasoning\",\"summary\":[{\"text\":\"visible summary\"}]}]}}\n\n")
	if e != nil || r.Visible != "final" || r.Reasoning != "visible summary" || *r.Model != "returned-model" || r.Usage["input_tokens"] != nil {
		t.Fatal(e, r)
	}
}
func TestProviderPartialStreamNegative(t *testing.T) {
	r, e, _ := send(t, 200, "data: {\"type\":\"response.output_text.delta\",\"delta\":\"partial\"}\n\n")
	if e == nil || r.Outcome != "incomplete" || r.Visible != "partial" || len(r.Raw) == 0 {
		t.Fatal("partial promoted", e, r)
	}
}
func TestProviderLateQuotaNegative(t *testing.T) {
	body := "data: {\"type\":\"response.output_text.delta\",\"delta\":\"partial\"}\n\ndata: {\"type\":\"response.failed\",\"response\":{\"error\":{\"code\":\"subscription_sharing_usage_limit_exceeded\"}}}\n\n"
	r, e, seen := send(t, 200, body)
	code, _ := SafeError(e)
	if code != "LOCAL_BUDGET_EXCEEDED" || r.Outcome == "complete" || seen.Calls != 1 || r.Visible != "partial" {
		t.Fatal("quota fallback", e, r, seen)
	}
}
func TestProviderActualRequestPositive(t *testing.T) {
	r, e, seen := send(t, 200, completed)
	if e != nil {
		t.Fatal(e)
	}
	if seen.Endpoint != "https://api.openai.com/v1/responses" || seen.Auth != "Bearer fixture-access-secret" || strings.Contains(seen.Body, "fixture-access-secret") || len(r.Raw) == 0 || r.Finished.Before(r.Started) {
		t.Fatal("wire/receipt identity", seen)
	}
}
func TestProviderNonstreamPositive(t *testing.T) {
	p := planProfile()
	p.Provider = "openai"
	p.Auth = "api_key"
	p.Billing = "free_tier"
	p.Stream = false
	client, seen := boundaryClient(t, 200, `{"status":"completed","model":"gpt-4.1-2025-04-14","output":[{"content":[{"type":"output_text","text":"fixture"}]}]}`)
	wire, e := Serialize(p, "", []any{}, nil)
	if e != nil {
		t.Fatal(e)
	}
	r, e := Exchange(context.Background(), client, p, wire, "fixture-key")
	if e != nil || r.Visible != "fixture" || seen.Calls != 1 {
		t.Fatal(e, r)
	}
}
func TestProviderMissingCredentialNegative(t *testing.T) {
	client, seen := boundaryClient(t, 200, completed)
	r, e := Exchange(context.Background(), client, planProfile(), []byte(`{}`), "")
	if e == nil || seen.Calls != 0 || r.HTTPStatus != nil {
		t.Fatal("missing credentials dispatched")
	}
}
func TestProviderRefusalNegative(t *testing.T) {
	r, e, seen := send(t, 200, "data: {\"type\":\"response.completed\",\"response\":{\"status\":\"completed\",\"output\":[{\"content\":[{\"type\":\"refusal\",\"refusal\":\"declined\"}]}]}}\n\n")
	if e == nil || r.Outcome != "refusal" || seen.Calls != 1 {
		t.Fatal("refusal promoted", r)
	}
}
func TestProviderCancelledPositive(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	client, seen := boundaryClient(t, 200, completed)
	r, e := Exchange(ctx, client, planProfile(), []byte(`{}`), "fixture")
	code, _ := SafeError(e)
	if code != "CANCELLED" || r.Outcome != "cancelled" || seen.Calls != 0 {
		t.Fatal(e, r)
	}
}
func TestProviderDeadlinePositive(t *testing.T) {
	ctx, cancel := context.WithDeadline(context.Background(), time.Now().Add(-time.Second))
	defer cancel()
	r, e := Exchange(ctx, &http.Client{}, planProfile(), []byte(`{}`), "fixture")
	code, _ := SafeError(e)
	if code != "DEADLINE_EXCEEDED" || r.Outcome != "deadline" {
		t.Fatal(e, r)
	}
}
func TestProviderIncompleteEventNegative(t *testing.T) {
	r, e, _ := send(t, 200, "data: {\"type\":\"response.incomplete\",\"response\":{\"status\":\"incomplete\"}}\n\n")
	if e == nil || r.Outcome != "incomplete" {
		t.Fatal("incomplete accepted")
	}
}
func TestProviderMalformedEventNegative(t *testing.T) {
	r, e, _ := send(t, 200, "data: malformed\n\n")
	if e == nil || r.Outcome == "complete" {
		t.Fatal("malformed accepted")
	}
}
