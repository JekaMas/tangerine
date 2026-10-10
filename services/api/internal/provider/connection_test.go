package provider

import (
	"context"
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"math/big"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"
)

// The remote OIDC/HTTP boundary and metadata repository below are controlled
// substitutes. Literal expectations test the production protocol and file owner,
// never account admission or a hosted model's quality. Native storage has separate cases.
type memoryRepo struct {
	mu, serial sync.Mutex
	rows       map[string]Connection
	active     string
	fail       bool
}

func (r *memoryRepo) Load(context.Context) ([]Connection, string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	out := []Connection{}
	for _, c := range r.rows {
		out = append(out, c)
	}
	return out, r.active, nil
}
func (r *memoryRepo) Save(_ context.Context, c Connection, selected bool) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.fail {
		return fmt.Errorf("storage unavailable")
	}
	r.rows[c.ID] = c
	if selected {
		r.active = c.ID
	} else if r.active == c.ID {
		r.active = ""
	}
	return nil
}

func (r *memoryRepo) Serialize(ctx context.Context) (func(), error) {
	for {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		if r.serial.TryLock() {
			return r.serial.Unlock, nil
		}
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-time.After(time.Millisecond):
		}
	}
}

type fixture struct {
	handlerMu                             sync.Mutex
	refreshDelay                          time.Duration
	m                                     *Manager
	repo                                  *memoryRepo
	server                                *httptest.Server
	key                                   *rsa.PrivateKey
	q                                     url.Values
	scope, subject, model                 string
	nonceOverride, clientOverride         string
	status, exchanges, refreshes, revokes int
	now                                   time.Time
	revoked                               bool
}

func newFixture(t *testing.T) *fixture {
	t.Helper()
	key, e := rsa.GenerateKey(rand.Reader, 2048)
	if e != nil {
		t.Fatal(e)
	}
	f := &fixture{key: key, scope: "openid email offline_access resource.invoke chatgpt.tokens.use.direct", subject: "subject-A", status: 200, now: time.Date(2026, 10, 10, 10, 0, 0, 0, time.UTC), repo: &memoryRepo{rows: map[string]Connection{}}}
	f.server = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		f.handlerMu.Lock()
		defer f.handlerMu.Unlock()
		switch r.URL.Path {
		case "/discovery":
			json.NewEncoder(w).Encode(map[string]any{"issuer": f.server.URL, "jwks_uri": f.server.URL + "/jwks", "revocation_endpoint": f.server.URL + "/revoke"})
		case "/jwks":
			json.NewEncoder(w).Encode(map[string]any{"keys": []any{map[string]any{"kty": "RSA", "kid": "fixture", "alg": "RS256", "n": base64.RawURLEncoding.EncodeToString(f.key.N.Bytes()), "e": base64.RawURLEncoding.EncodeToString(big.NewInt(int64(f.key.E)).Bytes())}}})
		case "/token":
			if r.Method != "POST" || r.Header.Get("Content-Type") != "application/x-www-form-urlencoded" {
				t.Errorf("wrong token wire")
				w.WriteHeader(400)
				return
			}
			r.ParseForm()
			f.exchanges++
			client := r.Form.Get("client_id")
			nonce := f.q.Get("nonce")
			if r.Form.Get("grant_type") == "refresh_token" {
				f.refreshes++
				time.Sleep(f.refreshDelay)
				if r.Form.Get("scope") != "" || r.Form.Get("refresh_token") != "refresh-1" {
					t.Errorf("wrong refresh wire")
				}
				nonce = ""
			} else {
				if r.Form.Get("redirect_uri") != "http://127.0.0.1:3000/auth/callback" || r.Form.Get("resource") != f.server.URL {
					t.Errorf("wrong exchange URI/resource")
				}
				digest := sha256.Sum256([]byte(r.Form.Get("code_verifier")))
				if base64.RawURLEncoding.EncodeToString(digest[:]) != f.q.Get("code_challenge") {
					t.Errorf("PKCE mismatch")
				}
			}
			if f.status != 200 {
				w.WriteHeader(f.status)
				fmt.Fprint(w, `{"error":"invalid_grant"}`)
				return
			}
			if f.nonceOverride != "" {
				nonce = f.nonceOverride
			}
			if f.clientOverride != "" {
				client = f.clientOverride
			}
			token := f.sign(client, nonce, f.subject, f.now.Add(time.Hour))
			json.NewEncoder(w).Encode(map[string]any{"access_token": fmt.Sprintf("access-%d", f.exchanges), "refresh_token": fmt.Sprintf("refresh-%d", f.exchanges), "id_token": token, "token_type": "Bearer", "scope": f.scope, "expires_in": 3600})
		case "/models":
			if r.Header.Get("Authorization") != "Bearer access-1" {
				t.Error("catalogue token wire")
			}
			w.WriteHeader(f.status)
			fmt.Fprint(w, f.model)
		case "/revoke":
			f.revokes++
			if f.status != 200 {
				w.WriteHeader(f.status)
				return
			}
			f.revoked = true
		default:
			w.WriteHeader(404)
		}
	}))
	t.Cleanup(f.server.Close)
	f.m = New(t.TempDir(), f.repo, f.server.Client(), Protocol{f.server.URL + "/authorize", f.server.URL + "/token", f.server.URL + "/discovery", f.server.URL})
	f.m.Now = func() time.Time { return f.now }
	return f
}
func (f *fixture) sign(client any, nonce, sub string, expires time.Time) string {
	h, _ := json.Marshal(map[string]any{"alg": "RS256", "kid": "fixture"})
	b, _ := json.Marshal(map[string]any{"iss": f.server.URL, "aud": client, "sub": sub, "email": "same@example.invalid", "nonce": nonce, "exp": expires.Unix()})
	message := base64.RawURLEncoding.EncodeToString(h) + "." + base64.RawURLEncoding.EncodeToString(b)
	d := sha256.Sum256([]byte(message))
	s, e := rsa.SignPKCS1v15(rand.Reader, f.key, crypto.SHA256, d[:])
	if e != nil {
		panic(e)
	}
	return message + "." + base64.RawURLEncoding.EncodeToString(s)
}
func (f *fixture) connect(t *testing.T, id string, credits *bool) Result {
	t.Helper()
	r, e := f.m.Connect(context.Background(), id, "http://127.0.0.1:3000/auth/callback", credits)
	if e != nil {
		t.Fatal(e)
	}
	u, _ := url.Parse(*r.URL)
	f.q = u.Query()
	return r
}
func (f *fixture) callback(t *testing.T) Connection {
	t.Helper()
	c, e := f.m.Callback(context.Background(), url.Values{"state": {f.q.Get("state")}, "code": {"fixture-code"}, "client_id": {"oaiapp_fixture"}})
	if e != nil {
		t.Fatal(e)
	}
	return c
}
func yes() *bool { x := true; return &x }
func TestProviderHostStablePositive(t *testing.T) {
	f := newFixture(t)
	a := f.connect(t, "", yes())
	n := New(f.m.Dir, f.repo, f.server.Client(), f.m.Protocol)
	b, e := n.Connect(context.Background(), "", "http://127.0.0.1:3000/auth/callback", nil)
	if e != nil || a.Connection.Host != b.Connection.Host {
		t.Fatal(e, a.Connection.Host, b.Connection.Host)
	}
}
func TestProviderHostDistinctPositive(t *testing.T) {
	a := newFixture(t)
	b := newFixture(t)
	if a.connect(t, "", nil).Connection.Host == b.connect(t, "", nil).Connection.Host {
		t.Fatal("hosts conflated")
	}
}
func TestProviderHostDamagedNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", nil)
	os.WriteFile(filepath.Join(f.m.Dir, "host-id"), []byte("broken"), 0600)
	if _, e := f.m.Connect(context.Background(), "", "http://127.0.0.1:3000/auth/callback", nil); e == nil {
		t.Fatal("damaged host silently regenerated")
	}
}
func TestProviderCredentialsModeNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	os.Chmod(filepath.Join(f.m.Dir, c.ID+".json"), 0644)
	if _, _, e := f.m.Access(context.Background(), c.ID); e == nil {
		t.Fatal("public credential file used")
	}
}
func TestProviderPKCEPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	if f.q.Get("client_id") != "dynamic_agent_client" || f.q.Get("agent_name_hint") != "Tangerine" || f.q.Get("code_challenge_method") != "S256" || f.q.Get("response_type") != "code" || f.q.Get("nonce") == "" {
		t.Fatal("authorization wire")
	}
	c := f.callback(t)
	if c.State != "ready" || f.exchanges != 1 {
		t.Fatal(c, f.exchanges)
	}
}
func TestProviderPendingSeparatePositive(t *testing.T) {
	f := newFixture(t)
	a := f.connect(t, "", yes())
	qa := f.q
	b := f.connect(t, "", yes())
	if qa.Get("state") == f.q.Get("state") || a.Connection.ID == b.Connection.ID || f.repo.active != "" || len(f.repo.rows) != 0 {
		t.Fatal("pending overwrote durable state")
	}
}
func TestProviderCallbackHostNegative(t *testing.T) {
	f := newFixture(t)
	for _, s := range []string{"http://localhost:3000/auth/callback", "https://127.0.0.1:3000/auth/callback"} {
		if _, e := f.m.Connect(context.Background(), "", s, nil); e == nil {
			t.Fatal("unsupported callback")
		}
	}
}
func TestProviderCallbackPathNegative(t *testing.T) {
	f := newFixture(t)
	for _, s := range []string{"http://127.0.0.1:3000/callback", "http://127.0.0.1:3000/auth/callback?key=secret"} {
		if _, e := f.m.Connect(context.Background(), "", s, nil); e == nil {
			t.Fatal("changed callback")
		}
	}
}
func TestProviderStateOneUsePositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	if _, e := f.m.Callback(context.Background(), url.Values{"state": {f.q.Get("state")}, "code": {"fixture-code"}, "client_id": {"oaiapp_fixture"}}); e == nil || f.exchanges != 1 || f.repo.active != c.ID {
		t.Fatal("callback replay")
	}
}
func TestProviderDeniedNoExchangePositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	if _, e := f.m.Callback(context.Background(), url.Values{"state": {f.q.Get("state")}, "error": {"access_denied"}, "code": {"ignored"}}); e == nil || f.exchanges != 0 || len(f.repo.rows) != 0 {
		t.Fatal("denied exchanged")
	}
}
func TestProviderWrongStateNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	if _, e := f.m.Callback(context.Background(), url.Values{"state": {"wrong"}, "code": {"fixture-code"}}); e == nil || f.exchanges != 0 {
		t.Fatal("wrong state")
	}
}
func TestProviderExpiredAttemptNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	f.now = f.now.Add(10 * time.Minute)
	if _, e := f.m.Callback(context.Background(), url.Values{"state": {f.q.Get("state")}, "code": {"fixture-code"}, "client_id": {"oaiapp_fixture"}}); e == nil || f.exchanges != 0 {
		t.Fatal("expired attempt")
	}
}
func TestProviderOIDCPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	if c.Subject == nil || *c.Subject != "subject-A" || *c.ClientID != "oaiapp_fixture" || *c.Label != "same@example.invalid" {
		t.Fatal("identity")
	}
}
func TestProviderAudienceArrayPositive(t *testing.T) {
	f := newFixture(t)
	token := f.sign([]string{"other", "client"}, "nonce", "subject", f.now.Add(time.Hour))
	sub, _, e := f.m.validateID(context.Background(), token, "client", "nonce")
	if e != nil || sub != "subject" {
		t.Fatal(e)
	}
}
func TestProviderNonceNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	f.nonceOverride = "wrong"
	if _, e := f.m.Callback(context.Background(), url.Values{"state": {f.q.Get("state")}, "code": {"fixture"}, "client_id": {"oaiapp_fixture"}}); e == nil || len(f.repo.rows) != 0 {
		t.Fatal("nonce accepted")
	}
}
func TestProviderSignatureNegative(t *testing.T) {
	f := newFixture(t)
	token := f.sign("client", "nonce", "subject", f.now.Add(time.Hour))
	p := strings.Split(token, ".")
	p[2] = base64.RawURLEncoding.EncodeToString(make([]byte, 256))
	if _, _, e := f.m.validateID(context.Background(), strings.Join(p, "."), "client", "nonce"); e == nil {
		t.Fatal("bad signature")
	}
	if _, _, e := f.m.validateID(context.Background(), token, "wrong", "nonce"); e == nil {
		t.Fatal("wrong audience")
	}
}
func TestProviderReconnectPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	a := f.callback(t)
	f.connect(t, a.ID, nil)
	if f.q.Get("client_id") != "oaiapp_fixture" || f.q.Get("agent_name_hint") != "" || f.q.Get("id_token_hint") == "" {
		t.Fatal("new registration on reconnect")
	}
	b := f.callback(t)
	if a.ID != b.ID || a.Host != b.Host {
		t.Fatal("lineage changed")
	}
}
func TestProviderRestartPendingPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.connect(t, c.ID, nil)
	m := New(f.m.Dir, f.repo, f.server.Client(), f.m.Protocol)
	m.Now = f.m.Now
	if _, e := m.Callback(context.Background(), url.Values{"state": {f.q.Get("state")}, "code": {"old"}}); e == nil {
		t.Fatal("pending survived restart")
	}
	rows, active, e := m.List(context.Background())
	if e != nil || len(rows) != 1 || active != c.ID {
		t.Fatal("registration lost")
	}
}
func TestProviderReconnectClientNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.connect(t, c.ID, nil)
	if _, e := f.m.Callback(context.Background(), url.Values{"state": {f.q.Get("state")}, "code": {"x"}, "client_id": {"another"}}); e == nil || f.exchanges != 1 || f.repo.active != c.ID {
		t.Fatal("client replaced")
	}
}
func TestProviderReconnectSubjectNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.connect(t, c.ID, nil)
	f.subject = "subject-B"
	if _, e := f.m.Callback(context.Background(), url.Values{"state": {f.q.Get("state")}, "code": {"x"}}); e == nil || *f.repo.rows[c.ID].Subject != "subject-A" {
		t.Fatal("subject replaced")
	}
}
func TestProviderScopeGrantedPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	if !hasScope(c.Scopes, "chatgpt.tokens.use.direct") || c.State != "ready" {
		t.Fatal("scope lost")
	}
}
func TestProviderCreditConfirmationPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", nil)
	c := f.callback(t)
	if c.State != "connected_no_usage" || f.repo.active != "" {
		t.Fatal("invented credit exclusion")
	}
	selected, e := f.m.Select(context.Background(), c.ID, yes())
	if e != nil || selected.State != "ready" {
		t.Fatal(e)
	}
}
func TestProviderScopeAbsentNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	first := f.callback(t)
	f.scope = "openid email"
	f.connect(t, "", yes())
	c := f.callback(t)
	if c.State != "connected_no_usage" || f.repo.active != first.ID {
		t.Fatal("absent grant replaced selected account")
	}
	if _, _, e := f.m.Access(context.Background(), c.ID); e == nil {
		t.Fatal("missing grant dispatched")
	}
	second := newFixture(t)
	second.connect(t, "", yes())
	saved := second.callback(t)
	second.now = second.now.Add(time.Hour)
	second.scope = "openid email"
	second.repo.fail = true
	if _, _, err := second.m.Access(context.Background(), saved.ID); err == nil {
		t.Fatal("metadata failure accepted")
	}
	second.repo.fail = false
	if _, _, err := second.m.Access(context.Background(), saved.ID); err == nil || second.exchanges != 2 {
		t.Fatal("withdrawn scope reused from retained rotated file", err, second.exchanges)
	}
	if second.repo.rows[saved.ID].State != "connected_no_usage" || second.repo.active == saved.ID {
		t.Fatal("scope recovery metadata stayed executable")
	}

}
func TestProviderCreditEnabledNegative(t *testing.T) {
	f := newFixture(t)
	x := false
	f.connect(t, "", &x)
	c := f.callback(t)
	if _, _, e := f.m.Access(context.Background(), c.ID); e == nil {
		t.Fatal("credits route dispatched")
	}
}
func TestProviderRefreshPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.now = f.now.Add(time.Hour)
	_, token, e := f.m.Access(context.Background(), c.ID)
	if e != nil || token != "access-2" || f.refreshes != 1 {
		t.Fatal(e, token, f.refreshes)
	}
	saved, e := f.m.readTokens(c)
	if e != nil || saved.Refresh != "refresh-2" {
		t.Fatal("rotation lost")
	}
}
func TestProviderRefreshSerializedPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.now = f.now.Add(time.Hour)
	f.refreshDelay = 100 * time.Millisecond
	var wg sync.WaitGroup
	for i := 0; i < 4; i++ {
		manager := New(f.m.Dir, f.repo, f.server.Client(), f.m.Protocol)
		manager.Now = f.m.Now
		wg.Go(func() {
			if _, token, e := manager.Access(context.Background(), c.ID); e != nil || token != "access-2" {
				t.Error(e)
			}
		})
	}
	wg.Wait()
	if f.refreshes != 1 {
		t.Fatal("duplicate rotation", f.refreshes)
	}
}
func TestProviderRefreshInvalidNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.now = f.now.Add(time.Hour)
	f.status = 400
	if _, _, e := f.m.Access(context.Background(), c.ID); e == nil || f.repo.rows[c.ID].State != "disconnected" || f.repo.active != "" {
		t.Fatal("revoked grant usable")
	}
}
func TestProviderRefreshTransientNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	before, _ := os.ReadFile(filepath.Join(f.m.Dir, c.ID+".json"))
	f.now = f.now.Add(time.Hour)
	f.status = 503
	if _, _, e := f.m.Access(context.Background(), c.ID); e == nil {
		t.Fatal("transient passed")
	}
	after, _ := os.ReadFile(filepath.Join(f.m.Dir, c.ID+".json"))
	if string(before) != string(after) || f.repo.rows[c.ID].State != "ready" || f.repo.active != c.ID {
		t.Fatal("prior credentials overwritten")
	}
}
func TestProviderDisconnectPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	d, e := f.m.Disconnect(context.Background(), c.ID)
	if e != nil || !f.revoked || d.State != "disconnected" || d.CredentialRef != nil || d.ClientID == nil || d.Host != c.Host {
		t.Fatal(e, d)
	}
	if _, _, e = f.m.Access(context.Background(), c.ID); e == nil {
		t.Fatal("signed out dispatch")
	}
}
func TestProviderSelectionFrozenPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	a := f.callback(t)
	f.connect(t, "", yes())
	b := f.callback(t)
	if f.repo.active != b.ID {
		t.Fatal("selection")
	}
	c, token, e := f.m.Access(context.Background(), a.ID)
	if e != nil || c.ID != a.ID || token != "access-1" {
		t.Fatal("frozen account switched", e)
	}
	f.now = f.now.Add(time.Hour)
	if _, _, e = f.m.Access(context.Background(), a.ID); e != nil || f.repo.active != b.ID {
		t.Fatal("refresh changed selection", e)
	}
}
func TestProviderDisconnectRevocationNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.status = 503
	d, e := f.m.Disconnect(context.Background(), c.ID)
	if e != nil || d.LastError == nil || *d.LastError != "remote_revocation_unconfirmed" {
		t.Fatal(e)
	}
	if _, e = os.Stat(filepath.Join(f.m.Dir, c.ID+".json")); !os.IsNotExist(e) {
		t.Fatal("local tokens retained")
	}
}
func TestProviderSelectionUnknownNegative(t *testing.T) {
	f := newFixture(t)
	if _, e := f.m.Select(context.Background(), "unknown", yes()); e == nil {
		t.Fatal("unknown registration")
	}
}

func TestProviderModelsPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.model = `{"models":[{"slug":"actual-A","display_name":"Actual A","visibility":"list"},{"slug":"hidden","display_name":"Hidden","visibility":"hidden"},{"slug":"actual-B","display_name":"Actual B","visibility":"list"}]}`
	models, raw, e := f.m.Models(context.Background(), c.ID)
	if e != nil || string(raw) != f.model || len(models) != 2 || models[0].Slug != "actual-A" || models[1].Slug != "actual-B" {
		t.Fatal(e, models)
	}
}
func TestProviderModelsEmptyPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.model = `{"models":[]}`
	models, raw, e := f.m.Models(context.Background(), c.ID)
	if e != nil || len(models) != 0 || string(raw) != f.model {
		t.Fatal(e)
	}
}
func TestProviderModelsQuotaNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.status = 429
	f.model = `{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}`
	_, raw, e := f.m.Models(context.Background(), c.ID)
	if e == nil || string(raw) != f.model {
		t.Fatal(e)
	}
}
func TestProviderModelsMalformedNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	for _, raw := range []string{`{"data":[]}`, `{"models":[{"slug":"a","visibility":"list"},{"slug":"a","visibility":"list"}]}`} {
		f.model = raw
		if _, _, e := f.m.Models(context.Background(), c.ID); e == nil {
			t.Fatal("missing or duplicate model catalogue accepted")
		}
	}
}
