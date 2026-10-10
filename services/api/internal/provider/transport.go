package provider

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"

	"tangerine.local/api/internal/contracts"
)

type Profile struct {
	ID            string   `json:"id"`
	Provider      string   `json:"provider"`
	Model         string   `json:"model"`
	Endpoint      string   `json:"endpoint"`
	Reasoning     *string  `json:"reasoning_effort"`
	Temperature   *float64 `json:"temperature"`
	MaxOutput     *int     `json:"max_output_tokens"`
	ContextBudget int      `json:"context_budget_tokens"`
	Adapter       string   `json:"adapter_version"`
	CredentialRef string   `json:"credential_ref"`
	Store         bool     `json:"store"`
	Stream        bool     `json:"stream"`
	Tools         []any    `json:"tools"`
	Roles         []string `json:"roles"`
	Auth          string   `json:"auth_method,omitempty"`
	Billing       string   `json:"billing_mode,omitempty"`
}
type Model struct {
	Slug        string `json:"slug"`
	DisplayName string `json:"display_name"`
	Visibility  string `json:"visibility"`
}

func (m *Manager) Models(ctx context.Context, id string) ([]Model, []byte, error) {
	_, token, e := m.Access(ctx, id)
	if e != nil {
		return nil, nil, e
	}
	req, e := http.NewRequestWithContext(ctx, "GET", m.Protocol.Resource+"/models", nil)
	if e != nil {
		return nil, nil, fail("PROVIDER_FAILURE")
	}
	req.Header.Set("Authorization", "Bearer "+token)
	r, e := m.Client.Do(req)
	if e != nil {
		return nil, nil, fail("PROVIDER_FAILURE")
	}
	defer r.Body.Close()
	b, e := io.ReadAll(r.Body)
	if e != nil {
		return nil, b, fail("PROVIDER_FAILURE")
	}
	if r.StatusCode != 200 {
		return nil, b, fail("PROVIDER_FAILURE")
	}
	var v struct {
		Models []Model `json:"models"`
	}
	if json.Unmarshal(b, &v) != nil || v.Models == nil {
		return nil, b, fail("PROVIDER_FAILURE")
	}
	out := []Model{}
	seen := map[string]bool{}
	for _, model := range v.Models {
		if model.Visibility != "list" {
			continue
		}
		if model.Slug == "" || seen[model.Slug] {
			return nil, b, fail("PROVIDER_FAILURE")
		}
		seen[model.Slug] = true
		out = append(out, model)
	}
	return out, b, nil
}
func ValidateProfile(p Profile) error {
	b, _ := json.Marshal(p)
	_, _, e := contracts.Validate("llm-profile", "2.0.0", b)
	if e != nil {
		return fail("CONSTRAINT_CONFLICT")
	}
	return nil
}
func Included(p Profile) error {
	if e := ValidateProfile(p); e != nil {
		return e
	}
	if p.Billing != "local" && p.Billing != "free_tier" && p.Billing != "included_subscription" {
		return fail("CONSTRAINT_CONFLICT")
	}
	switch p.Provider {
	case "openai_chatgpt":
		if p.Auth != "chatgpt_plan_oauth" || p.Billing != "included_subscription" || p.Endpoint != "https://api.openai.com/v1/responses" || !p.Stream || p.Temperature != nil || p.MaxOutput != nil {
			return fail("CONSTRAINT_CONFLICT")
		}
	case "openai", "deepseek":
		if p.Auth != "api_key" {
			return fail("CONSTRAINT_CONFLICT")
		}
		if (p.Provider == "openai" && p.Endpoint != "https://api.openai.com/v1/responses") || (p.Provider == "deepseek" && p.Endpoint != "https://api.deepseek.com/responses") {
			return fail("CONSTRAINT_CONFLICT")
		}
	case "local_responses":
		u, e := url.Parse(p.Endpoint)
		if e != nil || u.User != nil || u.Scheme != "http" || p.Auth != "local_none" || p.Billing != "local" || (u.Hostname() != "localhost" && u.Hostname() != "127.0.0.1" && u.Hostname() != "ollama" && u.Hostname() != "llm-local") {
			return fail("CONSTRAINT_CONFLICT")
		}
	default:
		return fail("CONSTRAINT_CONFLICT")
	}
	return nil
}

// Serialize is the final noncredential wire projection. The same returned bytes
// are saved and sent; no SDK adds hidden defaults or changes their order.
func Serialize(p Profile, instructions string, input []any, format any) ([]byte, error) {
	if e := Included(p); e != nil {
		return nil, e
	}
	if input == nil {
		return nil, fail("CONSTRAINT_CONFLICT")
	}
	if p.Provider == "openai_chatgpt" {
		for _, item := range input {
			if message, ok := item.(map[string]any); ok && message["role"] == "system" {
				return nil, fail("CONSTRAINT_CONFLICT")
			}
		}
	}
	wire := map[string]any{"model": p.Model, "instructions": instructions, "input": input, "store": false, "stream": p.Stream, "tools": []any{}}
	if p.Reasoning != nil {
		wire["reasoning"] = map[string]any{"effort": *p.Reasoning}
	}
	if p.Provider != "openai_chatgpt" {
		if p.Temperature != nil {
			wire["temperature"] = *p.Temperature
		}
		if p.MaxOutput != nil {
			wire["max_output_tokens"] = *p.MaxOutput
		}
	}
	if format != nil {
		wire["text"] = map[string]any{"format": format}
	}
	b, e := json.Marshal(wire)
	if e != nil {
		return nil, fail("CONSTRAINT_CONFLICT")
	}
	return contracts.Canonical(b)
}

type Response struct {
	Raw               []byte
	Visible           string
	Reasoning         string
	Model             *string
	RequestID         *string
	HTTPStatus        *int
	Outcome           string
	ErrorCode         *string
	Usage             map[string]*int64
	Started, Finished time.Time
}

func requestError(code string) error {
	if code == "subscription_sharing_usage_limit_exceeded" || code == "subscription_sharing_usage_unavailable" {
		return &Failure{Code: "LOCAL_BUDGET_EXCEEDED", ProviderCode: code}
	}
	return &Failure{Code: "PROVIDER_FAILURE", ProviderCode: code}
}
func (r *Response) content(b []byte) error {
	var v struct {
		Status string `json:"status"`
		Model  string `json:"model"`
		Output []struct {
			Type    string `json:"type"`
			Content []struct{ Type, Text, Refusal string }
			Summary []struct{ Text string }
		}
		Usage map[string]json.RawMessage
		Error *struct{ Code string }
	}
	if json.Unmarshal(b, &v) != nil {
		return fail("PROVIDER_INCOMPLETE")
	}
	if v.Model != "" {
		r.Model = &v.Model
	}
	var visible, reason strings.Builder
	for _, item := range v.Output {
		for _, c := range item.Content {
			if c.Type == "refusal" || c.Refusal != "" {
				r.Outcome = "refusal"
				return fail("PROVIDER_FAILURE")
			}
			if c.Type == "output_text" {
				visible.WriteString(c.Text)
			}
		}
		for _, s := range item.Summary {
			reason.WriteString(s.Text)
		}
	}
	if visible.Len() > 0 {
		r.Visible = visible.String()
	}
	r.Reasoning = reason.String()
	if v.Error != nil && v.Error.Code != "" {
		r.ErrorCode = &v.Error.Code
		return requestError(v.Error.Code)
	}
	if v.Status != "completed" {
		r.Outcome = "incomplete"
		return fail("PROVIDER_INCOMPLETE")
	}

	for _, field := range []string{"input_tokens", "output_tokens"} {
		var n int64
		if raw := v.Usage[field]; raw != nil && json.Unmarshal(raw, &n) == nil {
			r.Usage[field] = &n
		}
	}
	for _, pair := range [][2]string{{"input_tokens_details", "cached_tokens"}, {"output_tokens_details", "reasoning_tokens"}} {
		var details map[string]int64
		if raw := v.Usage[pair[0]]; raw != nil && json.Unmarshal(raw, &details) == nil {
			if n, ok := details[pair[1]]; ok {
				key := pair[1]
				r.Usage[key] = &n
			}
		}
	}
	r.Outcome = "complete"
	return nil
}
func Exchange(ctx context.Context, client *http.Client, p Profile, wire []byte, credential string) (out Response, err error) {
	out = Response{Outcome: "transport_error", Usage: map[string]*int64{}, Started: time.Now().UTC()}
	defer func() {
		out.Finished = time.Now().UTC()
		if err != nil && ctx.Err() != nil {
			out.Outcome = "cancelled"
			if errors.Is(ctx.Err(), context.DeadlineExceeded) {
				out.Outcome = "deadline"
			}
		}
	}()
	if e := Included(p); e != nil {
		return out, e
	}
	if p.Auth != "local_none" && credential == "" {
		return out, fail("MISSING_CREDENTIALS")
	}
	if ctx.Err() != nil {
		return out, ctx.Err()
	}
	req, e := http.NewRequestWithContext(ctx, "POST", p.Endpoint, bytes.NewReader(wire))
	if e != nil {
		return out, fail("PROVIDER_FAILURE")
	}
	req.Header.Set("Content-Type", "application/json")
	if p.Auth != "local_none" {
		req.Header.Set("Authorization", "Bearer "+credential)
	}
	if client == nil {
		client = &http.Client{CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	}
	res, e := client.Do(req)
	if e != nil {
		if ctx.Err() != nil {
			return out, ctx.Err()
		}
		return out, fail("PROVIDER_FAILURE")
	}
	defer res.Body.Close()
	status := res.StatusCode
	out.HTTPStatus = &status
	if id := res.Header.Get("x-request-id"); id != "" {
		out.RequestID = &id
	}
	if status < 200 || status >= 300 {
		out.Raw, _ = io.ReadAll(res.Body)
		var v struct{ Error struct{ Code string } }
		_ = json.Unmarshal(out.Raw, &v)
		if v.Error.Code != "" {
			out.ErrorCode = &v.Error.Code
		}
		return out, requestError(v.Error.Code)
	}
	if !p.Stream {
		out.Raw, e = io.ReadAll(res.Body)
		if e != nil {
			return out, fail("PROVIDER_FAILURE")
		}
		return out, out.content(out.Raw)
	}
	var raw bytes.Buffer
	reader := bufio.NewReader(io.TeeReader(res.Body, &raw))
	data := []string{}
	terminal := false
	event := func() error {
		if len(data) == 0 {
			return nil
		}
		b := []byte(strings.Join(data, "\n"))
		data = nil
		if bytes.Equal(b, []byte("[DONE]")) {
			return nil
		}
		var v struct {
			Type     string
			Delta    string
			Response json.RawMessage
			Error    struct{ Code string }
			Code     string
		}
		if json.Unmarshal(b, &v) != nil {
			return fail("PROVIDER_INCOMPLETE")
		}
		switch v.Type {
		case "response.output_text.delta":
			if !terminal {
				out.Visible += v.Delta
			}
		case "response.completed":
			if terminal {
				return fail("PROVIDER_INCOMPLETE")
			}
			terminal = true
			return out.content(v.Response)
		case "response.failed":
			terminal = true
			out.Outcome = "incomplete"
			var f struct{ Error struct{ Code string } }
			_ = json.Unmarshal(v.Response, &f)
			code := f.Error.Code
			if code == "" {
				code = v.Error.Code
			}
			out.ErrorCode = &code
			return requestError(code)
		case "response.incomplete":
			terminal = true
			out.Outcome = "incomplete"
			return fail("PROVIDER_INCOMPLETE")
		case "error":
			terminal = true
			code := v.Code
			if code == "" {
				code = v.Error.Code
			}
			out.ErrorCode = &code
			return requestError(code)
		case "response.refusal.delta":
			out.Outcome = "refusal"
			return fail("PROVIDER_FAILURE")
		}
		return nil
	}
	for {
		line, readErr := reader.ReadString('\n')
		line = strings.TrimSuffix(strings.TrimSuffix(line, "\n"), "\r")
		if strings.HasPrefix(line, "data:") {
			data = append(data, strings.TrimSpace(strings.TrimPrefix(line, "data:")))
		}
		if line == "" {
			if e = event(); e != nil {
				out.Raw = raw.Bytes()
				return out, e
			}
			if terminal {
				out.Raw = raw.Bytes()
				return out, nil
			}
		}
		if readErr != nil {
			if readErr != io.EOF {
				out.Raw = raw.Bytes()
				return out, fail("PROVIDER_FAILURE")
			}
			if e = event(); e != nil {
				out.Raw = raw.Bytes()
				return out, e
			}
			break
		}
	}
	out.Raw = raw.Bytes()
	if !terminal {
		out.Outcome = "incomplete"
		return out, fail("PROVIDER_INCOMPLETE")
	}
	return out, nil
}
