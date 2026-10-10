package app

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"strings"
	"sync"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"testing"
	"time"
)

func providerNative(t *testing.T) *Storage {
	t.Helper()
	s, e := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(s.DB.Close)
	return s
}
func connNative() provider.Connection {
	client, sub, label := "oaiapp_fixture", "signed-fixture-sub", "Fixture account"
	return provider.Connection{ID: uuid.NewString(), Provider: "openai_chatgpt", ClientID: &client, Host: "urn:uuid:" + uuid.NewString(), Subject: &sub, Label: &label, State: "disconnected", Scopes: []string{}, Updated: time.Now().UTC().Format(time.RFC3339Nano)}
}
func TestNativeProviderMetadataPositive(t *testing.T) {
	s := providerNative(t)
	repo := providerRepository{s}
	c := connNative()
	if e := repo.Save(context.Background(), c, true); e != nil {
		t.Fatal(e)
	}
	rows, id, e := repo.Load(context.Background())
	if e != nil || id != c.ID {
		t.Fatal(e, id)
	}
	for _, r := range rows {
		if r.ID == id && (r.Subject == nil || *r.Subject != "signed-fixture-sub") {
			t.Fatal(r)
		}
	}
	raw, _ := json.Marshal(rows)
	for _, secret := range []string{"access_token", "refresh_token", "id_token", "code_verifier"} {
		if strings.Contains(string(raw), secret) {
			t.Fatal("secret exposed")
		}
	}
}
func TestNativeProviderSelectionPositive(t *testing.T) {
	s := providerNative(t)
	repo := providerRepository{s}
	a, b := connNative(), connNative()
	if e := repo.Save(context.Background(), a, true); e != nil {
		t.Fatal(e)
	}
	if e := repo.Save(context.Background(), b, true); e != nil {
		t.Fatal(e)
	}
	_, id, e := repo.Load(context.Background())
	if e != nil || id != b.ID {
		t.Fatal(e, id)
	}
	a.State = "unavailable"
	if e = repo.Save(context.Background(), a, false); e != nil {
		t.Fatal(e)
	}
	_, id, e = repo.Load(context.Background())
	if e != nil || id != b.ID {
		t.Fatal("frozen account overwrote active", e, id)
	}
}
func TestNativeProviderMetadataFailureNegative(t *testing.T) {
	s := providerNative(t)
	repo := providerRepository{s}
	c := connNative()
	if e := repo.Save(context.Background(), c, true); e != nil {
		t.Fatal(e)
	}
	before, active, e := repo.Load(context.Background())
	if e != nil {
		t.Fatal(e)
	}
	c.State = "invented"
	if e = repo.Save(context.Background(), c, true); e == nil {
		t.Fatal("invalid metadata committed")
	}
	after, id, e := repo.Load(context.Background())
	if e != nil || id != active || len(after) != len(before) {
		t.Fatal("partial commit", e)
	}
}
func TestNativeProviderCatalogueReferenceNegative(t *testing.T) {
	s := providerNative(t)
	repo := providerRepository{s}
	c := connNative()
	id := uuid.NewString()
	c.ModelsAsset = &id
	if e := repo.Save(context.Background(), c, false); e == nil {
		t.Fatal("missing native catalogue allowed")
	}
	ctx := context.Background()
	started, release := make(chan struct{}), make(chan struct{})
	var once sync.Once
	finish := func() { once.Do(func() { close(release) }) }
	defer finish()
	remote := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/models" {
			w.WriteHeader(404)
			return
		}
		close(started)
		<-release
		io.WriteString(w, `{"models":[{"slug":"actual-fixture","visibility":"list"}]}`)
	}))
	defer func() { finish(); remote.Close() }()
	ready := connNative()
	ready.State = "ready"
	ready.CredentialRef = &ready.ID
	ready.Scopes = []string{"chatgpt.tokens.use.direct"}
	yes := true
	ready.CreditsDisabled = &yes
	if err := repo.Save(ctx, ready, true); err != nil {
		t.Fatal(err)
	}
	dir := t.TempDir()
	grant, _ := json.Marshal(provider.Tokens{Access: "native-fixture-grant", Refresh: "native-fixture-refresh", Type: "Bearer", Scope: "chatgpt.tokens.use.direct", Expires: time.Now().Add(time.Hour)})
	if err := os.WriteFile(dir+"/host-id", []byte(ready.Host), 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(dir+"/"+ready.ID+".json", grant, 0600); err != nil {
		t.Fatal(err)
	}
	manager := provider.New(dir, repo, remote.Client(), provider.Protocol{Resource: remote.URL})
	server := NewServer(s, "http://localhost:3000", "")
	server.Providers = manager
	observed := httptest.NewRecorder()
	done := make(chan struct{})
	go func() {
		defer close(done)
		request := httptest.NewRequest("POST", "/api/v1/provider-connections:action", strings.NewReader(`{"action":"select","connection_id":"`+ready.ID+`","credits_after_plan_limit_disabled":true}`))
		request.Header.Set("Content-Type", "application/json")
		server.providerAction(observed, request)
	}()
	select {
	case <-started:
	case <-done:
		t.Fatal("model request did not start", observed.Code)
	case <-time.After(5 * time.Second):
		t.Fatal("model request not observed")
	}
	if _, err := manager.Disconnect(ctx, ready.ID); err != nil {
		t.Fatal(err)
	}
	finish()
	select {
	case <-done:
	case <-time.After(5 * time.Second):
		t.Fatal("late catalogue did not finish")
	}
	rows, active, err := repo.Load(ctx)
	if err != nil {
		t.Fatal(err)
	}
	for _, row := range rows {
		if row.ID == ready.ID && (row.State != "disconnected" || row.CredentialRef != nil || row.ModelsAsset != nil || active == row.ID) {
			t.Fatal("late catalogue revived disconnected grant", row.State, active)
		}
	}
	if observed.Code != 422 {
		t.Fatal("late catalogue accepted", observed.Code)
	}

}
func configRequest(c map[string]any) []byte {
	delete(c, "configuration_sha256")
	delete(c, "workspace_id")
	delete(c, "provider_access_policy")
	b, _ := json.Marshal(c)
	return b
}
func TestNativeProviderConfigurationPositive(t *testing.T) {
	s := providerNative(t)
	ctx := context.Background()
	_, rev, e := s.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	raw := configRequest(DefaultConfiguration())
	key := uuid.NewString()
	saved, next, e := s.PutConfiguration(ctx, raw, key, rev)
	if e != nil || next != rev+1 {
		t.Fatal(e, next, rev)
	}
	again, n, e := s.PutConfiguration(ctx, raw, key, rev)
	if e != nil || n != next || again["configuration_sha256"] != saved["configuration_sha256"] {
		t.Fatal("replay", e)
	}
	loaded, n, e := s.Configuration(ctx)
	if e != nil || n != next || loaded["configuration_sha256"] != saved["configuration_sha256"] {
		t.Fatal("restart readback", e)
	}
}
func TestNativeProviderConfigurationViewPositive(t *testing.T) {
	s := providerNative(t)
	c, _, e := s.Configuration(context.Background())
	if e != nil {
		t.Fatal(e)
	}
	b, _ := json.Marshal(configurationView(c))
	if _, _, e = contracts.Validate("configuration-view", "2.0.0", b); e != nil {
		t.Fatal(e)
	}
	if strings.Contains(string(b), "access_token") {
		t.Fatal("secret")
	}
}
func TestNativeProviderConfigurationRevisionNegative(t *testing.T) {
	s := providerNative(t)
	_, rev, e := s.Configuration(context.Background())
	if e != nil {
		t.Fatal(e)
	}
	_, _, e = s.PutConfiguration(context.Background(), configRequest(DefaultConfiguration()), uuid.NewString(), rev-1)
	if !errors.Is(e, ErrRevision) {
		t.Fatal(e)
	}
}
func TestNativeProviderConfigurationReferencesNegative(t *testing.T) {
	s := providerNative(t)
	c, rev, e := s.Configuration(context.Background())
	if e != nil {
		t.Fatal(e)
	}
	before := c["configuration_sha256"]
	c["llm_profile"] = "missing"
	if _, _, e = s.PutConfiguration(context.Background(), configRequest(c), uuid.NewString(), rev); e == nil {
		t.Fatal("absent default")
	}
	after, _, e := s.Configuration(context.Background())
	if e != nil || after["configuration_sha256"] != before {
		t.Fatal("changed on rejected input", e)
	}
}
func TestNativeProviderFrozenPositive(t *testing.T) {
	c := DefaultConfiguration()
	rows := c["llm_profiles"].([]any)
	p := rows[0].(map[string]any)
	p["model"] = "fixture-account-model"
	got, e := FreezeProfile(c, "blind_claim_extraction")
	if e != nil {
		t.Fatal(e)
	}
	p["model"] = "new-choice"
	if got.Model != "fixture-account-model" {
		t.Fatal("frozen alias")
	}
}
func TestNativeProviderOverridePositive(t *testing.T) {
	c := DefaultConfiguration()
	base := c["llm_profiles"].([]any)[0].(map[string]any)
	base["model"] = "default"
	raw, _ := json.Marshal(base)
	var second map[string]any
	_ = json.Unmarshal(raw, &second)
	second["id"] = "explicit"
	second["model"] = "overridden"
	c["llm_profiles"] = append(c["llm_profiles"].([]any), second)
	c["stage_profiles"].(map[string]any)["feedback"] = "explicit"
	p, e := FreezeProfile(c, "feedback")
	if e != nil || p.Model != "overridden" {
		t.Fatal(e, p)
	}
}
func TestNativeProviderFrozenMissingNegative(t *testing.T) {
	if _, e := FreezeProfile(DefaultConfiguration(), "feedback"); e == nil {
		t.Fatal("unselected used")
	}
	c := DefaultConfiguration()
	c["stage_profiles"].(map[string]any)["feedback"] = "missing"
	if _, e := FreezeProfile(c, "feedback"); e == nil {
		t.Fatal("fallback")
	}
}
func TestNativeProviderFrozenMeteredNegative(t *testing.T) {
	c := DefaultConfiguration()
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	p["model"] = "actual"
	p["billing_mode"] = "metered"
	if _, e := FreezeProfile(c, "feedback"); e == nil {
		t.Fatal("metered")
	}
}

const nativeExtraction = `{"schema_version":"2.0.0","clauses":[],"unparsed_spans":[],"relations":[]}`

func inferenceNative(t *testing.T, body string, status int) (*Server, LLMRequest, *http.Client, *int) {
	t.Helper()
	s := providerNative(t)
	calls := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		b, _ := io.ReadAll(r.Body)
		if !strings.Contains(string(b), "Complete stage input") || strings.Contains(string(b), "Authorization") {
			t.Fatal("wire input")
		}
		requestID := uuid.NewString()
		w.Header().Set("x-request-id", requestID)
		w.WriteHeader(status)
		io.WriteString(w, body)
		if dir := os.Getenv("TANGERINE_PROVIDER_TEST_EVIDENCE"); dir != "" {
			event, _ := json.Marshal(map[string]any{"request_id": requestID, "wire_request_sha256": contracts.Digest(b), "wire_response_sha256": contracts.Digest([]byte(body)), "http_status": status, "method": r.Method, "path": r.URL.Path, "origin": "test_owned_remote_protocol_observer"})
			f, e := os.OpenFile(dir+"/dispatch-observations.jsonl", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
			if e != nil {
				t.Fatal(e)
			}
			_, e = f.Write(append(event, '\n'))
			_ = f.Close()
			if e != nil {
				t.Fatal(e)
			}
		}
	}))
	t.Cleanup(server.Close)
	c := DefaultConfiguration()
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	p["provider"] = "local_responses"
	p["endpoint"] = server.URL + "/v1/responses"
	p["auth_method"] = "local_none"
	p["billing_mode"] = "local"
	p["model"] = "test-owned-protocol-fixture"
	p["credential_ref"] = "local-none"
	p["stream"] = false
	delete(c, "configuration_sha256")
	c["configuration_sha256"] = lab.Hash(c)
	text := "No mistakes."
	input := map[string]any{"schema_version": "2.0.0", "answer_text": text, "answer_sha256": contracts.Digest([]byte(text)), "task_components": map[string]any{"detection": true, "classification": true, "correction": true, "explanation": false}, "requested_language": "en"}
	req := LLMRequest{Operation: OperationRequest{Name: "native-provider-execution", Key: uuid.NewString(), Path: "/native/provider", Body: json.RawMessage(`{"test":"literal"}`)}, Stage: "blind_claim_extraction", Input: input, Components: map[string]any{"taxonomy": []string{"G01"}, "public_context": "Two friends", "answer": text}, Configuration: c, Bundle: lab.Shipped()}
	return NewServer(s, "http://localhost:3000", ""), req, server.Client(), &calls
}
func nativeReply(text string) string {
	b, _ := json.Marshal(map[string]any{"status": "completed", "model": "actual-fixture-returned", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": text}}}}, "usage": map[string]any{"input_tokens": 17, "output_tokens": 5}})
	return string(b)
}
func TestNativeProviderReceiptPositive(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil || *n != 1 || string(out.Output) != `{"clauses":[],"relations":[],"schema_version":"2.0.0","unparsed_spans":[]}` || len(out.ReceiptIDs) != 1 {
		t.Fatal(e, *n, string(out.Output))
	}
	doc, e := s.Store.ReadDocument(context.Background(), out.ReceiptIDs[0])
	if e != nil {
		t.Fatal(e)
	}
	var receipt map[string]any
	_ = json.Unmarshal(doc.Payload, &receipt)
	if receipt["input_tokens"] != "17" || receipt["output_tokens"] != "5" || receipt["cost_micro_usd"] != nil || receipt["model_returned"] != "actual-fixture-returned" {
		t.Fatal(receipt)
	}
	b, e := s.Store.ReadAsset(context.Background(), receipt["wire_response_asset_id"].(string))
	if e != nil || string(b) != nativeReply(nativeExtraction) {
		t.Fatal("native bytes", e)
	}
}
func TestNativeProviderSnapshotPositive(t *testing.T) {
	s, r, c, _ := inferenceNative(t, nativeReply(nativeExtraction), 200)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	d, e := s.Store.ReadDocument(context.Background(), out.ContextIDs[0])
	if e != nil {
		t.Fatal(e)
	}
	var snap map[string]any
	_ = json.Unmarshal(d.Payload, &snap)
	if snap["receipt_id"] != out.ReceiptIDs[0] || snap["operation_id"] != out.OperationID || snap["tokenizer"] != nil || snap["budget_method"] != "conservative_utf8_bytes" {
		t.Fatal(snap)
	}
	wire, e := s.Store.ReadAsset(context.Background(), snap["rendered_request_asset_id"].(string))
	if e != nil || int(snap["input_budget_used"].(float64)) != len(wire) {
		t.Fatal(e)
	}
	for _, x := range snap["components"].([]any) {
		v := x.(map[string]any)
		if v["included"] == true {
			b, e := s.Store.ReadAsset(context.Background(), v["asset_id"].(string))
			if e != nil || contracts.Digest(b) != v["asset_sha256"] {
				t.Fatal("part", e)
			}
		}
	}
}
func TestNativeProviderPartialNegative(t *testing.T) {
	s, r, c, n := inferenceNative(t, `{"status":"incomplete","output":[]}`, 200)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e == nil || out.Output != nil || *n != 2 || len(out.ReceiptIDs) != 2 {
		t.Fatal(e, *n, len(out.ReceiptIDs))
	}
	for _, id := range out.ReceiptIDs {
		d, e := s.Store.ReadDocument(context.Background(), id)
		var payload map[string]any
		decode := json.Unmarshal(d.Payload, &payload)
		if e != nil || decode != nil || payload["outcome"] != "incomplete" {
			t.Fatal(e, string(d.Payload))
		}
	}
}
func TestNativeProviderQuotaNegative(t *testing.T) {
	s, r, c, n := inferenceNative(t, `{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}`, 429)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e == nil || *n != 1 || out.Output != nil || len(out.ReceiptIDs) != 1 {
		t.Fatal(e, *n)
	}
	d, e := s.Store.ReadDocument(context.Background(), out.ReceiptIDs[0])
	var payload map[string]any
	decode := json.Unmarshal(d.Payload, &payload)
	value, present := payload["input_tokens"]
	if e != nil || decode != nil || !present || value != nil {
		t.Fatal(e, string(d.Payload))
	}
}
func TestNativeProviderReplayPositive(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)

	t.Setenv("OPENAI_API_KEY", "OWNED_REPLAY_CREDENTIAL")
	profile := r.Configuration["llm_profiles"].([]any)[0].(map[string]any)
	endpoint, err := url.Parse(profile["endpoint"].(string))
	if err != nil {
		t.Fatal(err)
	}
	profile["provider"] = "openai"
	profile["endpoint"] = "https://api.openai.com/v1/responses"
	profile["auth_method"] = "api_key"
	profile["billing_mode"] = "free_tier"
	profile["credential_ref"] = "OPENAI_API_KEY"
	delete(r.Configuration, "configuration_sha256")
	r.Configuration["configuration_sha256"] = lab.Hash(r.Configuration)
	underlying := c.Transport
	if underlying == nil {
		underlying = http.DefaultTransport
	}
	c.Transport = nativeProviderTrip(func(req *http.Request) (*http.Response, error) {
		copy := req.Clone(req.Context())
		u := *req.URL
		u.Scheme = endpoint.Scheme
		u.Host = endpoint.Host
		copy.URL = &u
		return underlying.RoundTrip(copy)
	})
	a, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	t.Setenv("OPENAI_API_KEY", "")
	b, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil || *n != 1 || string(a.Output) != string(b.Output) || a.BindingID != b.BindingID || a.ReceiptIDs[0] != b.ReceiptIDs[0] {
		t.Fatal("replay dispatched", e, *n)
	}
}
func TestNativeProviderRestartReadbackPositive(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	a, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	fresh := providerNative(t)
	b, e := fresh.ReadLLMResult(context.Background(), a.OperationID)
	if e != nil || *n != 1 || string(a.Output) != string(b.Output) || a.BindingID != b.BindingID {
		t.Fatal(e)
	}
}
func TestNativeProviderReplayChangedNegative(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	if _, e := s.InvokeLLM(context.Background(), r, c); e != nil {
		t.Fatal(e)
	}
	r.Configuration["feedback_language"] = "ru"
	delete(r.Configuration, "configuration_sha256")
	r.Configuration["configuration_sha256"] = lab.Hash(r.Configuration)
	if _, e := s.InvokeLLM(context.Background(), r, c); !errors.Is(e, ErrConflict) || *n != 1 {
		t.Fatal(e, *n)
	}
}
func TestNativeProviderReplayIncompleteNegative(t *testing.T) {
	s, r, c, n := inferenceNative(t, `{"status":"incomplete","output":[]}`, 200)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e == nil {
		t.Fatal("incomplete")
	}
	if _, e = s.Store.ReadLLMResult(context.Background(), out.OperationID); e == nil {
		t.Fatal("false complete")
	}
	if _, e = s.InvokeLLM(context.Background(), r, c); e == nil || *n != 2 {
		t.Fatal("automatic retry", e, *n)
	}
}
func TestNativeProviderDiagnosticPositive(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	r.Configuration["llm_lab_trace_enabled"] = true
	delete(r.Configuration, "configuration_sha256")
	r.Configuration["configuration_sha256"] = lab.Hash(r.Configuration)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	asset, e := s.Store.LLMDiagnostic(context.Background(), out, true, true)
	if e != nil {
		t.Fatal(e)
	}
	raw, e := s.Store.ReadAsset(context.Background(), asset.ID)
	if e != nil || !strings.Contains(string(raw), "native_provider_transport") || *n != 1 {
		t.Fatal(e, *n)
	}
	if dir := os.Getenv("TANGERINE_PROVIDER_TEST_EVIDENCE"); dir != "" {
		if e = os.WriteFile(dir+"/positive-diagnostic.json", raw, 0600); e != nil {
			t.Fatal(e)
		}
	}
}
func TestNativeProviderFailedDiagnosticPositive(t *testing.T) {
	s, r, c, n := inferenceNative(t, `{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}`, 429)
	r.Configuration["llm_lab_trace_enabled"] = true
	delete(r.Configuration, "configuration_sha256")
	r.Configuration["configuration_sha256"] = lab.Hash(r.Configuration)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e == nil {
		t.Fatal("quota")
	}
	asset, e := s.Store.LLMDiagnostic(context.Background(), out, true, true)
	if e != nil {
		t.Fatal(e)
	}
	raw, e := s.Store.ReadAsset(context.Background(), asset.ID)
	if e != nil || *n != 1 || !strings.Contains(string(raw), "subscription_sharing_usage_limit_exceeded") {
		t.Fatal(e)
	}
	if dir := os.Getenv("TANGERINE_PROVIDER_TEST_EVIDENCE"); dir != "" {
		if e = os.WriteFile(dir+"/negative-diagnostic.json", raw, 0600); e != nil {
			t.Fatal(e)
		}
	}
}
func TestNativeProviderDiagnosticMissingNegative(t *testing.T) {
	s := providerNative(t)
	r := LLMResult{OperationID: uuid.NewString(), BindingID: uuid.NewString()}
	if _, e := s.LLMDiagnostic(context.Background(), r, false, false); e == nil {
		t.Fatal("missing evidence")
	}
}
func TestNativeProviderDiagnosticChangedNegative(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	if _, e = s.Store.LLMDiagnostic(context.Background(), out, false, false); e != nil {
		t.Fatal(e)
	}
	if _, e = s.Store.LLMDiagnostic(context.Background(), out, true, true); !errors.Is(e, ErrConflict) || *n != 1 {
		t.Fatal("immutable export packet replaced", e)
	}
}
func TestNativeProviderDefaultProfilesPositive(t *testing.T) {
	c := DefaultConfiguration()
	raw, _ := json.Marshal(c)
	if _, _, e := contracts.Validate("configuration", "2.0.0", raw); e != nil {
		t.Fatal(e)
	}
	if len(c["llm_profiles"].([]any)) != 3 || c["provider_access_policy"].(map[string]any)["mode"] != "included_only" {
		t.Fatal("retained defaults")
	}
}
func TestNativeProviderScopedSettingsPositive(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	r.Configuration["stage_profiles"].(map[string]any)["feedback"] = "deepseek-flash-low-v1"
	delete(r.Configuration, "configuration_sha256")
	r.Configuration["configuration_sha256"] = lab.Hash(r.Configuration)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil || *n != 1 || out.Output == nil {
		t.Fatal(e, *n)
	}
}
func TestNativeProviderConfigurationHashNegative(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	r.Configuration["feedback_language"] = "ru"
	if out, e := s.InvokeLLM(context.Background(), r, c); e != nil || *n != 1 || len(out.Output) == 0 {
		t.Fatal("accepted configuration was requalified instead of reused", e, *n)
	}
}
func TestNativeProviderReadinessMissingNegative(t *testing.T) {
	t.Setenv("OPENAI_API_KEY", "test-owned-nonbillable-sentinel")
	s := providerNative(t)
	ctx := context.Background()
	_, rev, e := s.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	if _, _, e = s.PutConfiguration(ctx, configRequest(DefaultConfiguration()), uuid.NewString(), rev); e != nil {
		t.Fatal(e)
	}
	if got := NewServer(s, "http://localhost:3000", "").providerReadiness(ctx); got != "missing_credentials" {
		t.Fatal(got)
	}
}
func cliNative(t *testing.T, s *Server, r LLMRequest) ([]byte, error) {
	t.Helper()
	ctx := context.Background()
	_, rev, e := s.Store.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	if _, _, e = s.Store.PutConfiguration(ctx, configRequest(r.Configuration), uuid.NewString(), rev); e != nil {
		t.Fatal(e)
	}
	raw, _ := json.Marshal(map[string]any{"operation": r.Operation, "stage": r.Stage, "phase": r.Phase, "input": r.Input, "components": r.Components})
	return raw, nil
}
func readDiagnosticNative(t *testing.T, s *Server, id string) map[string]any {
	t.Helper()
	var out strings.Builder
	raw, _ := json.Marshal(map[string]any{"action": "diagnostic-read", "id": id})
	if e := s.Store.LabCommand(context.Background(), strings.NewReader(string(raw)), &out); e != nil {
		t.Fatal(e)
	}
	var packet map[string]any
	_ = json.Unmarshal([]byte(out.String()), &packet)
	return packet
}
func TestNativeProviderCLIPositive(t *testing.T) {
	s, r, _, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	raw, _ := cliNative(t, s, r)
	var out strings.Builder
	if e := s.ProviderCommand(context.Background(), strings.NewReader(string(raw)), &out); e != nil {
		t.Fatal(e)
	}
	var v struct {
		Result    LLMResult
		ErrorCode string `json:"error_code"`
	}
	_ = json.Unmarshal([]byte(out.String()), &v)
	if *n != 1 || v.ErrorCode != "" || string(v.Result.Output) != `{"clauses":[],"relations":[],"schema_version":"2.0.0","unparsed_spans":[]}` {
		t.Fatal(*n, out.String())
	}
	p := readDiagnosticNative(t, s, v.Result.OperationID)
	if p["capture"] != false || p["trace_enabled"] != false {
		t.Fatal(p)
	}
}
func TestNativeProviderCLIOverlayPositive(t *testing.T) {
	s, r, _, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	raw, _ := cliNative(t, s, r)
	before, _, _ := s.Store.Configuration(context.Background())
	hash := before["configuration_sha256"]
	var command map[string]any
	_ = json.Unmarshal(raw, &command)
	command["trace_enabled"] = true
	command["capture_content"] = true
	raw, _ = json.Marshal(command)
	var out strings.Builder
	if e := s.ProviderCommand(context.Background(), strings.NewReader(string(raw)), &out); e != nil {
		t.Fatal(e)
	}
	var v struct{ Result LLMResult }
	_ = json.Unmarshal([]byte(out.String()), &v)
	p := readDiagnosticNative(t, s, v.Result.OperationID)
	after, _, e := s.Store.Configuration(context.Background())
	if e != nil || *n != 1 || p["capture"] != true || p["trace_enabled"] != true || after["configuration_sha256"] != hash {
		t.Fatal(e, *n, p)
	}
}
func TestNativeProviderCLIMalformedNegative(t *testing.T) {
	s, _, _, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	var out strings.Builder
	if e := s.ProviderCommand(context.Background(), strings.NewReader(`{"unknown":"secret","trace_enabled":true}`), &out); e == nil || *n != 0 || out.Len() != 0 {
		t.Fatal(e, *n, out.String())
	}
}
func TestNativeProviderCLIMeteredNegative(t *testing.T) {
	s, r, _, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	r.Configuration["llm_profiles"].([]any)[0].(map[string]any)["billing_mode"] = "metered"
	raw, _ := cliNative(t, s, r)
	var out strings.Builder
	e := s.ProviderCommand(context.Background(), strings.NewReader(string(raw)), &out)
	if e == nil || *n != 0 || !strings.Contains(out.String(), `"error_code":"CONSTRAINT_CONFLICT"`) {
		t.Fatal(e, *n, out.String())
	}
}
func TestNativeProviderDiagnosticCanaryNegative(t *testing.T) {
	const canary = "OWNED_PROVIDER_CREDENTIAL_CANARY"
	t.Setenv("OPENAI_API_KEY", canary)
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	r.Input["answer_text"] = canary
	r.Input["answer_sha256"] = contracts.Digest([]byte(canary))
	r.Components["answer"] = canary
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	a, e := s.Store.LLMDiagnostic(context.Background(), out, true, false)
	if e != nil {
		t.Fatal(e)
	}
	raw, e := s.Store.ReadAsset(context.Background(), a.ID)
	if e != nil || *n != 1 || strings.Contains(string(raw), canary) {
		t.Fatal("credential value enters export packet", e, *n)
	}
	if dir := os.Getenv("TANGERINE_PROVIDER_TEST_EVIDENCE"); dir != "" {
		if e = os.WriteFile(dir+"/canary-diagnostic.json", raw, 0600); e != nil {
			t.Fatal(e)
		}
	}
}
func TestNativeProviderDiagnosticOriginalPositive(t *testing.T) {
	const canary = "OWNED_PRIVATE_INPUT_CANARY"
	t.Setenv("OPENAI_API_KEY", canary)
	s, r, c, _ := inferenceNative(t, nativeReply(nativeExtraction), 200)
	r.Input["answer_text"] = canary
	r.Input["answer_sha256"] = contracts.Digest([]byte(canary))
	r.Components["answer"] = canary
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	receipt, e := s.Store.ReadDocument(context.Background(), out.ReceiptIDs[0])
	if e != nil {
		t.Fatal(e)
	}
	var metadata map[string]any
	_ = json.Unmarshal(receipt.Payload, &metadata)
	wire, e := s.Store.ReadAsset(context.Background(), metadata["wire_request_asset_id"].(string))
	if e != nil || !strings.Contains(string(wire), canary) {
		t.Fatal("native original lost", e)
	}
	a, e := s.Store.LLMDiagnostic(context.Background(), out, true, false)
	if e != nil {
		t.Fatal(e)
	}
	copy, e := s.Store.ReadAsset(context.Background(), a.ID)
	again, e := s.Store.ReadAsset(context.Background(), metadata["wire_request_asset_id"].(string))
	if e != nil || string(again) != string(wire) || strings.Contains(string(copy), canary) || !strings.Contains(string(copy), "native_original_sha256") {
		t.Fatal("original/copy lineage", e)
	}
}
func TestNativeProviderDiagnosticReplayPositive(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	a, e := s.Store.LLMDiagnostic(context.Background(), out, true, false)
	if e != nil {
		t.Fatal(e)
	}
	t.Setenv("OPENAI_API_KEY", "new-unused-key")
	b, e := s.Store.LLMDiagnostic(context.Background(), out, true, false)
	if e != nil || a.ID != b.ID || a.SHA != b.SHA || *n != 1 {
		t.Fatal(e, *n)
	}
}
func TestNativeProviderDiagnosticSecretStorageNegative(t *testing.T) {
	s, r, c, n := inferenceNative(t, nativeReply(nativeExtraction), 200)
	out, e := s.InvokeLLM(context.Background(), r, c)
	if e != nil {
		t.Fatal(e)
	}
	out.privateSecrets = []string{"actual-used-credential"}
	a, e := s.Store.LLMDiagnostic(context.Background(), out, true, false)
	if e != nil {
		t.Fatal(e)
	}
	raw, e := s.Store.ReadAsset(context.Background(), a.ID)
	if e != nil || *n != 1 || strings.Contains(string(raw), "actual-used-credential") || strings.Contains(string(raw), `"secrets"`) {
		t.Fatal("ephemeral credential set persisted", e)
	}
}

type nativeProviderTrip func(*http.Request) (*http.Response, error)

func (f nativeProviderTrip) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }

func TestNativeProviderSerializationPositive(t *testing.T) {
	s := providerNative(t)
	repo := providerRepository{s}
	ctx := context.Background()
	release, err := repo.Serialize(ctx)
	if err != nil {
		t.Fatal(err)
	}
	release()
	bounded, cancel := context.WithTimeout(ctx, time.Second)
	defer cancel()
	second, err := repo.Serialize(bounded)
	if err != nil {
		t.Fatal("released lease not reusable", err)
	}
	second()
}
func TestNativeProviderSerializationParallelPositive(t *testing.T) {
	s := providerNative(t)
	fresh := providerNative(t)
	repo := providerRepository{s}
	other := providerRepository{fresh}
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	release, err := repo.Serialize(ctx)
	if err != nil {
		t.Fatal(err)
	}
	var once sync.Once
	finish := func() { once.Do(release) }
	defer finish()
	arrived := make(chan error, 1)
	go func() {
		unlock, err := other.Serialize(ctx)
		if err == nil {
			unlock()
		}
		arrived <- err
	}()
	select {
	case err := <-arrived:
		t.Fatal("another process entered held lease", err)
	case <-time.After(30 * time.Millisecond):
	}
	finish()
	if err := <-arrived; err != nil {
		t.Fatal("waiter did not recover", err)
	}
}
func TestNativeProviderSerializationCancelledNegative(t *testing.T) {
	s := providerNative(t)
	repo := providerRepository{s}
	ctx := context.Background()
	release, err := repo.Serialize(ctx)
	if err != nil {
		t.Fatal(err)
	}
	defer release()
	bounded, cancel := context.WithTimeout(ctx, 30*time.Millisecond)
	defer cancel()
	unlock, err := repo.Serialize(bounded)
	code, _ := provider.SafeError(err)
	if code != "DEADLINE_EXCEEDED" || unlock != nil {
		t.Fatal("cancelled waiter admitted", code)
	}
	again, stop := context.WithTimeout(ctx, 30*time.Millisecond)
	defer stop()
	if unlock, err := repo.Serialize(again); err == nil {
		unlock()
		t.Fatal("cancelled waiter released another owner's lease")
	}
}
func TestNativeProviderSerializationFailureNegative(t *testing.T) {
	s := providerNative(t)
	repo := providerRepository{s}
	s.DB.Close()
	release, err := repo.Serialize(context.Background())
	if err == nil || release != nil {
		t.Fatal("unavailable database admitted lease")
	}
}
