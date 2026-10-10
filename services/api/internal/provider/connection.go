// Package provider owns provider authorization and text transport. It never reads
// another application's credential file and never chooses a billing fallback.
package provider

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
)

type Failure struct {
	Code         string
	ProviderCode string
	Diagnostic   string
}

func (e *Failure) Error() string { return e.Code }
func fail(code string) error     { return &Failure{Code: code} }

type Connection struct {
	ID              string   `json:"id"`
	Provider        string   `json:"provider"`
	ClientID        *string  `json:"client_id"`
	Host            string   `json:"ext_agent_host_id"`
	Label           *string  `json:"account_label"`
	Subject         *string  `json:"subject"`
	State           string   `json:"state"`
	Scopes          []string `json:"scopes"`
	CredentialRef   *string  `json:"credential_ref"`
	Expires         *string  `json:"expires_at"`
	CreditsDisabled *bool    `json:"credits_after_plan_limit_disabled"`
	ModelsAsset     *string  `json:"models_asset_id"`
	LastError       *string  `json:"last_error_code"`
	Updated         string   `json:"updated_at"`
}
type Repository interface {
	Serialize(context.Context) (func(), error)
	Load(context.Context) ([]Connection, string, error)
	Save(context.Context, Connection, bool) error
}
type Protocol struct{ Authorize, Token, Discovery, Resource string }

func OfficialProtocol() Protocol {
	return Protocol{"https://auth.openai.com/api/accounts/authorize", "https://auth.openai.com/api/accounts/oauth/token", "https://auth.openai.com/.well-known/openid-configuration", "https://api.openai.com/v1"}
}

type Tokens struct {
	Access    string          `json:"access_token"`
	Refresh   string          `json:"refresh_token"`
	ID        string          `json:"id_token"`
	Type      string          `json:"token_type"`
	Scope     string          `json:"scope"`
	ExpiresIn int64           `json:"expires_in"`
	Earliest  json.RawMessage `json:"earliest_refresh_at"`
	Expires   time.Time       `json:"expires_at"`
}
type pending struct {
	Connection                       Connection
	State, Nonce, Verifier, Redirect string
	Deadline                         time.Time
}
type Result struct {
	Connection Connection `json:"connection"`
	URL        *string    `json:"authorization_url"`
}
type Manager struct {
	mu       sync.Mutex
	Dir      string
	Repo     Repository
	Client   *http.Client
	Protocol Protocol
	Now      func() time.Time
	pending  map[string]pending
}

func New(dir string, repo Repository, client *http.Client, protocol Protocol) *Manager {
	if client == nil {
		client = &http.Client{Timeout: 30 * time.Second, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	}
	return &Manager{Dir: dir, Repo: repo, Client: client, Protocol: protocol, Now: time.Now, pending: map[string]pending{}}
}

// lock serializes protected grant/identity transitions across the API and CLI.
// The repository owns the cross-process lease; local waiting is cancellable.
func (m *Manager) lock(ctx context.Context) (func(), error) {
	for {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		if m.mu.TryLock() {
			break
		}
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-time.After(10 * time.Millisecond):
		}
	}
	release, err := m.Repo.Serialize(ctx)
	if err != nil {
		m.mu.Unlock()
		return nil, err
	}
	return func() { release(); m.mu.Unlock() }, nil
}

func random() string {
	b := make([]byte, 32)
	if _, e := rand.Read(b); e != nil {
		panic("system random source unavailable")
	}
	return base64.RawURLEncoding.EncodeToString(b)
}
func (m *Manager) privateWrite(name string, b []byte) error {
	if e := os.MkdirAll(m.Dir, 0700); e != nil {
		return fail("MISSING_CREDENTIALS")
	}
	if e := os.Chmod(m.Dir, 0700); e != nil {
		return fail("MISSING_CREDENTIALS")
	}
	f, e := os.CreateTemp(m.Dir, ".rotation-")
	if e != nil {
		return fail("MISSING_CREDENTIALS")
	}
	defer os.Remove(f.Name())
	if e = f.Chmod(0600); e == nil {
		_, e = f.Write(b)
	}
	if e == nil {
		e = f.Sync()
	}
	closeErr := f.Close()
	if e == nil {
		e = closeErr
	}
	if e == nil {
		e = os.Rename(f.Name(), filepath.Join(m.Dir, name))
	}
	if e != nil {
		return fail("MISSING_CREDENTIALS")
	}
	d, e := os.Open(m.Dir)
	if e == nil {
		defer d.Close()
		e = d.Sync()
	}
	return e
}
func (m *Manager) host() (string, error) {
	p := filepath.Join(m.Dir, "host-id")
	b, e := os.ReadFile(p)
	if e == nil {
		id, e := uuid.Parse(strings.TrimPrefix(string(b), "urn:uuid:"))
		if e != nil || id.Version() != 4 {
			return "", fail("MISSING_CREDENTIALS")
		}
		return "urn:uuid:" + id.String(), nil
	}
	if !errors.Is(e, os.ErrNotExist) {
		return "", fail("MISSING_CREDENTIALS")
	}
	h := "urn:uuid:" + uuid.NewString()
	return h, m.privateWrite("host-id", []byte(h))
}
func (m *Manager) readTokens(c Connection) (Tokens, error) {
	var t Tokens
	if c.CredentialRef == nil || *c.CredentialRef != c.ID {
		return t, fail("MISSING_CREDENTIALS")
	}
	if _, e := uuid.Parse(c.ID); e != nil {
		return t, fail("MISSING_CREDENTIALS")
	}
	f, e := os.Lstat(filepath.Join(m.Dir, c.ID+".json"))
	if e != nil || !f.Mode().IsRegular() || f.Mode().Perm()&0077 != 0 {
		return t, fail("MISSING_CREDENTIALS")
	}
	b, e := os.ReadFile(filepath.Join(m.Dir, c.ID+".json"))
	if e != nil || json.Unmarshal(b, &t) != nil || t.Access == "" {
		return t, fail("MISSING_CREDENTIALS")
	}
	return t, nil
}
func (m *Manager) saveTokens(c Connection, t Tokens) error {
	b, e := json.Marshal(t)
	if e != nil {
		return e
	}
	return m.privateWrite(c.ID+".json", b)
}
func connection(rows []Connection, id string) (Connection, error) {
	for _, c := range rows {
		if c.ID == id {
			return c, nil
		}
	}
	return Connection{}, fail("CONSTRAINT_CONFLICT")
}
func (m *Manager) List(ctx context.Context) ([]Connection, string, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.Repo.Load(ctx)
}
func (m *Manager) Connect(ctx context.Context, id, redirect string, credits *bool) (Result, error) {
	release, lockErr := m.lock(ctx)
	if lockErr != nil {
		return Result{}, lockErr
	}
	defer release()
	u, e := url.Parse(redirect)
	if e != nil || u.Scheme != "http" || u.Hostname() != "127.0.0.1" || u.Path != "/auth/callback" || u.RawQuery != "" || u.Fragment != "" {
		return Result{}, fail("CONSTRAINT_CONFLICT")
	}
	host, e := m.host()
	if e != nil {
		return Result{}, e
	}
	c := Connection{ID: uuid.NewString(), Provider: "openai_chatgpt", Host: host, State: "awaiting_consent", Scopes: []string{}, CreditsDisabled: credits, Updated: m.Now().UTC().Format(time.RFC3339Nano)}
	client := "dynamic_agent_client"
	var hints Tokens
	if id != "" {
		rows, _, e := m.Repo.Load(ctx)
		if e != nil {
			return Result{}, e
		}
		c, e = connection(rows, id)
		if e != nil {
			return Result{}, e
		}
		if c.ClientID == nil || c.Subject == nil || c.Host != host {
			return Result{}, fail("CONSTRAINT_CONFLICT")
		}
		client = *c.ClientID
		hints, _ = m.readTokens(c)
		if credits != nil {
			c.CreditsDisabled = credits
		}
		c.State = "awaiting_consent"
	}
	state, nonce, verifier := random(), random(), random()
	challenge := sha256.Sum256([]byte(verifier))
	q := url.Values{"client_id": {client}, "ext_agent_host_id": {host}, "response_type": {"code"}, "redirect_uri": {redirect}, "resource": {m.Protocol.Resource}, "scope": {"openid profile email offline_access resource.invoke chatgpt.tokens.use.direct"}, "state": {state}, "nonce": {nonce}, "code_challenge_method": {"S256"}, "code_challenge": {base64.RawURLEncoding.EncodeToString(challenge[:])}}
	if client == "dynamic_agent_client" {
		q.Set("agent_name_hint", "Tangerine")
	} else {
		if hints.ID != "" {
			q.Set("id_token_hint", hints.ID)
		}
		if c.Label != nil {
			q.Set("login_hint", *c.Label)
		}
	}
	for k, p := range m.pending {
		if !m.Now().Before(p.Deadline) {
			delete(m.pending, k)
		}
	}
	m.pending[state] = pending{c, state, nonce, verifier, redirect, m.Now().Add(10 * time.Minute)}
	auth := m.Protocol.Authorize + "?" + q.Encode()
	return Result{c, &auth}, nil
}
func (m *Manager) token(ctx context.Context, form url.Values) (Tokens, error) {
	var t Tokens
	req, e := http.NewRequestWithContext(ctx, "POST", m.Protocol.Token, strings.NewReader(form.Encode()))
	if e != nil {
		return t, fail("PROVIDER_FAILURE")
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	r, e := m.Client.Do(req)
	if e != nil {
		return t, &Failure{Code: "PROVIDER_FAILURE", Diagnostic: "token_transport_failed"}
	}
	defer r.Body.Close()
	b, e := io.ReadAll(io.LimitReader(r.Body, 1024*1024))
	if e != nil {
		return t, fail("PROVIDER_FAILURE")
	}
	if r.StatusCode != 200 {
		var v struct {
			Error string `json:"error"`
		}
		_ = json.Unmarshal(b, &v)
		if v.Error == "invalid_grant" && (r.StatusCode == 400 || r.StatusCode == 401) {
			return t, &Failure{Code: "MISSING_CREDENTIALS", ProviderCode: v.Error}
		}
		return t, &Failure{Code: "PROVIDER_FAILURE", ProviderCode: v.Error, Diagnostic: fmt.Sprintf("token_http_%d", r.StatusCode)}
	}
	if json.Unmarshal(b, &t) != nil || t.Access == "" || !strings.EqualFold(t.Type, "Bearer") || t.ExpiresIn <= 0 {
		return t, &Failure{Code: "PROVIDER_FAILURE", Diagnostic: "token_response_fields_invalid"}
	}
	t.Expires = m.Now().Add(time.Duration(t.ExpiresIn) * time.Second)
	return t, nil
}
func hasScope(scopes []string, s string) bool {
	for _, x := range scopes {
		if x == s {
			return true
		}
	}
	return false
}
func ready(c Connection) bool {
	return hasScope(c.Scopes, "chatgpt.tokens.use.direct") && c.CreditsDisabled != nil && *c.CreditsDisabled
}
func (m *Manager) Callback(ctx context.Context, q url.Values) (out Connection, err error) {
	phase := "callback_fields"
	defer func() {
		if err != nil {
			code, _ := SafeError(err)
			detail := ""
			var failure *Failure
			if errors.As(err, &failure) {
				detail = failure.Diagnostic
			}
			b, _ := json.Marshal(map[string]string{"phase": phase, "code": code, "diagnostic": detail, "at": m.Now().UTC().Format(time.RFC3339Nano)})
			_ = m.privateWrite("callback-failure.json", b)
		} else {
			_ = os.Remove(filepath.Join(m.Dir, "callback-failure.json"))
		}
	}()

	release, lockErr := m.lock(ctx)
	if lockErr != nil {
		return Connection{}, lockErr
	}
	defer release()
	for _, key := range []string{"state", "code", "client_id", "error", "scope", "error_description"} {
		if len(q[key]) > 1 {
			return Connection{}, fail("CONSTRAINT_CONFLICT")
		}
	}
	state := q.Get("state")
	p, ok := m.pending[state]
	if !ok {
		return Connection{}, fail("CONSTRAINT_CONFLICT")
	}
	delete(m.pending, state)
	if !m.Now().Before(p.Deadline) {
		return Connection{}, fail("CONSTRAINT_CONFLICT")
	}
	if q.Get("error") != "" {
		return Connection{}, fail("PROVIDER_FAILURE")
	}
	c := p.Connection
	client := q.Get("client_id")
	if c.ClientID != nil {
		if client != "" && client != *c.ClientID {
			return Connection{}, fail("CONSTRAINT_CONFLICT")
		}
		client = *c.ClientID
	}
	if client == "" || client == "dynamic_agent_client" || q.Get("code") == "" {
		return Connection{}, fail("CONSTRAINT_CONFLICT")
	}
	phase = "token_exchange"
	t, e := m.token(ctx, url.Values{"grant_type": {"authorization_code"}, "client_id": {client}, "code": {q.Get("code")}, "code_verifier": {p.Verifier}, "redirect_uri": {p.Redirect}, "resource": {m.Protocol.Resource}})
	if e != nil {
		return Connection{}, e
	}
	phase = "identity_validation"
	subject, label, e := m.validateID(ctx, t.ID, client, p.Nonce)
	if e != nil {
		return Connection{}, e
	}
	if c.Subject != nil && *c.Subject != subject {
		return Connection{}, fail("CONSTRAINT_CONFLICT")
	}
	c.ClientID = &client
	c.Subject = &subject
	c.Label = nil
	if label != "" {
		c.Label = &label
	}
	c.Scopes = strings.Fields(t.Scope)
	c.CredentialRef = &c.ID
	expiry := t.Expires.UTC().Format(time.RFC3339Nano)
	c.Expires = &expiry
	c.LastError = nil
	c.State = "connected_no_usage"
	if ready(c) {
		c.State = "ready"
	}
	c.Updated = m.Now().UTC().Format(time.RFC3339Nano)
	_, active, e := m.Repo.Load(ctx)
	if e != nil {
		return Connection{}, e
	}
	phase = "credential_persistence"
	if e = m.saveTokens(c, t); e != nil {
		return Connection{}, e
	}
	phase = "metadata_persistence"
	if e = m.Repo.Save(ctx, c, ready(c) || active == c.ID); e != nil {
		return Connection{}, e
	}
	return c, nil
}
func (m *Manager) Select(ctx context.Context, id string, credits *bool) (Connection, error) {
	release, lockErr := m.lock(ctx)
	if lockErr != nil {
		return Connection{}, lockErr
	}
	defer release()
	rows, _, e := m.Repo.Load(ctx)
	if e != nil {
		return Connection{}, e
	}
	c, e := connection(rows, id)
	if e != nil {
		return c, e
	}
	host, e := m.host()
	if e != nil {
		return c, e
	}
	if c.Host != host {
		return c, fail("MISSING_CREDENTIALS")
	}
	if _, e = m.readTokens(c); e != nil {
		return c, e
	}
	if credits != nil {
		c.CreditsDisabled = credits
	}
	c.State = "connected_no_usage"
	if ready(c) {
		c.State = "ready"
	}
	c.Updated = m.Now().UTC().Format(time.RFC3339Nano)
	return c, m.Repo.Save(ctx, c, true)
}
func (m *Manager) Disconnect(ctx context.Context, id string) (Connection, error) {
	release, lockErr := m.lock(ctx)
	if lockErr != nil {
		return Connection{}, lockErr
	}
	defer release()
	rows, _, e := m.Repo.Load(ctx)
	if e != nil {
		return Connection{}, e
	}
	c, e := connection(rows, id)
	if e != nil {
		return c, e
	}
	// Persist dispatch refusal before remote revocation. Other registrations stay saved.
	c.State = "disconnected"
	c.Updated = m.Now().UTC().Format(time.RFC3339Nano)
	if e = m.Repo.Save(ctx, c, false); e != nil {
		return c, e
	}
	t, tokenErr := m.readTokens(c)
	confirmed := false
	if tokenErr == nil && t.Refresh != "" {
		d, e := m.discovery(ctx)
		if e == nil && d.Revocation != "" {
			form := url.Values{"token": {t.Refresh}, "token_type_hint": {"refresh_token"}, "client_id": {*c.ClientID}}
			req, e := http.NewRequestWithContext(ctx, "POST", d.Revocation, strings.NewReader(form.Encode()))
			if e == nil {
				req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				res, e := m.Client.Do(req)
				if e == nil {
					confirmed = res.StatusCode == 200
					res.Body.Close()
				}
			}
		}
	}
	if e = os.Remove(filepath.Join(m.Dir, c.ID+".json")); e != nil && !errors.Is(e, os.ErrNotExist) {
		return c, fail("MISSING_CREDENTIALS")
	}
	c.CredentialRef = nil
	c.Expires = nil
	c.LastError = nil
	if !confirmed {
		s := "remote_revocation_unconfirmed"
		c.LastError = &s
	}
	return c, m.Repo.Save(ctx, c, false)
}
func (m *Manager) Access(ctx context.Context, id string) (Connection, string, error) {
	release, lockErr := m.lock(ctx)
	if lockErr != nil {
		return Connection{}, "", lockErr
	}
	defer release()
	rows, active, e := m.Repo.Load(ctx)
	if e != nil {
		return Connection{}, "", e
	}
	c, e := connection(rows, id)
	if e != nil {
		return c, "", e
	}
	host, e := m.host()
	if e != nil {
		return c, "", e
	}
	if c.Host != host || c.State != "ready" || !ready(c) {
		return c, "", fail("CONSTRAINT_CONFLICT")
	}
	t, e := m.readTokens(c)
	if e != nil {
		return c, "", e
	}
	if !hasScope(strings.Fields(t.Scope), "chatgpt.tokens.use.direct") {
		c.Scopes = strings.Fields(t.Scope)
		c.State = "connected_no_usage"
		c.Updated = m.Now().UTC().Format(time.RFC3339Nano)
		if err := m.Repo.Save(ctx, c, false); err != nil {
			return c, "", err
		}
		return c, "", fail("CONSTRAINT_CONFLICT")
	}
	if m.Now().Before(t.Expires.Add(-30 * time.Second)) {
		return c, t.Access, nil
	}
	if t.Refresh == "" {
		return c, "", fail("MISSING_CREDENTIALS")
	}
	if len(t.Earliest) > 0 && string(t.Earliest) != "null" {
		var seconds int64
		var text string
		if json.Unmarshal(t.Earliest, &seconds) == nil {
			if m.Now().Before(time.Unix(seconds, 0)) {
				return c, "", fail("PROVIDER_FAILURE")
			}
		} else if json.Unmarshal(t.Earliest, &text) == nil {
			x, e := time.Parse(time.RFC3339, text)
			if e != nil || m.Now().Before(x) {
				return c, "", fail("PROVIDER_FAILURE")
			}
		} else {
			return c, "", fail("PROVIDER_FAILURE")
		}
	}
	next, e := m.token(ctx, url.Values{"grant_type": {"refresh_token"}, "client_id": {*c.ClientID}, "refresh_token": {t.Refresh}, "resource": {m.Protocol.Resource}})
	if e != nil {
		var f *Failure
		if errors.As(e, &f) && f.Code == "MISSING_CREDENTIALS" && f.ProviderCode == "invalid_grant" {
			c.State = "disconnected"
			s := "invalid_grant"
			c.LastError = &s
			_ = m.Repo.Save(ctx, c, false)
		}
		return c, "", e
	}
	if next.Refresh == "" {
		return c, "", fail("PROVIDER_FAILURE")
	}
	if next.ID != "" {
		subject, _, e := m.validateID(ctx, next.ID, *c.ClientID, "")
		if e != nil || c.Subject == nil || subject != *c.Subject {
			return c, "", fail("CONSTRAINT_CONFLICT")
		}
	} else {
		next.ID = t.ID
	}
	if next.Scope == "" {
		next.Scope = t.Scope
	}
	c.Scopes = strings.Fields(next.Scope)
	if !ready(c) {
		c.State = "connected_no_usage"
	}
	expiry := next.Expires.UTC().Format(time.RFC3339Nano)
	c.Expires = &expiry
	c.Updated = m.Now().UTC().Format(time.RFC3339Nano)
	// Keep a rotated secret even if metadata persistence fails; the previous refresh
	// token may already have been revoked. No inference follows a failed save.
	if e = m.saveTokens(c, next); e != nil {
		return c, "", e
	}
	if e = m.Repo.Save(ctx, c, active == id); e != nil {
		return c, "", e
	}
	if !ready(c) {
		return c, "", fail("CONSTRAINT_CONFLICT")
	}
	return c, next.Access, nil
}
func (m *Manager) Mark(ctx context.Context, id, state, code string) error {
	release, lockErr := m.lock(ctx)
	if lockErr != nil {
		return lockErr
	}
	defer release()
	rows, active, e := m.Repo.Load(ctx)
	if e != nil {
		return e
	}
	c, e := connection(rows, id)
	if e != nil {
		return e
	}
	// A failed in-flight request owns its receipt, not a later user transition.
	// Preserve disconnect/revocation warnings and withdrawn usage confirmation.
	if c.State != "ready" && c.State != "usage_limited" && c.State != "unavailable" {
		return nil
	}
	c.State = state
	c.LastError = &code
	c.Updated = m.Now().UTC().Format(time.RFC3339Nano)
	return m.Repo.Save(ctx, c, active == id)
}
func SafeError(e error) (string, string) {
	if errors.Is(e, context.DeadlineExceeded) {
		return "DEADLINE_EXCEEDED", ""
	}
	if errors.Is(e, context.Canceled) {
		return "CANCELLED", ""
	}
	var f *Failure
	if errors.As(e, &f) {
		return f.Code, f.ProviderCode
	}
	return "PROVIDER_FAILURE", ""
}
func (c Connection) String() string { return fmt.Sprintf("provider connection %s (%s)", c.ID, c.State) }

// Configured is a local configuration check, never hosted entitlement/inference.
func (m *Manager) Configured(ctx context.Context, id string) error {
	release, lockErr := m.lock(ctx)
	if lockErr != nil {
		return lockErr
	}
	defer release()
	rows, _, e := m.Repo.Load(ctx)
	if e != nil {
		return e
	}
	c, e := connection(rows, id)
	if e != nil {
		return e
	}
	if c.State != "ready" || !ready(c) {
		return fail("MISSING_CREDENTIALS")
	}
	h, e := m.host()
	if e != nil || h != c.Host {
		return fail("MISSING_CREDENTIALS")
	}
	t, e := m.readTokens(c)
	if e != nil {
		return e
	}
	if !hasScope(strings.Fields(t.Scope), "chatgpt.tokens.use.direct") {
		return fail("CONSTRAINT_CONFLICT")
	}
	return nil
}

// CredentialValues is used only for in-memory diagnostic redaction. It performs
// no refresh/remote call and its values never enter metadata or export packets.
func (m *Manager) CredentialValues(ctx context.Context, id string) []string {
	m.mu.Lock()
	defer m.mu.Unlock()
	rows, _, e := m.Repo.Load(ctx)
	if e != nil {
		return nil
	}
	c, e := connection(rows, id)
	if e != nil {
		return nil
	}
	t, e := m.readTokens(c)
	if e != nil {
		return nil
	}
	return []string{t.Access, t.Refresh, t.ID}
}

// SaveModels rechecks the current registration after the remote response. A late
// catalogue cannot overwrite disconnect, selection or newer rotating metadata.
func (m *Manager) SaveModels(ctx context.Context, id, asset string) (Connection, error) {
	release, err := m.lock(ctx)
	if err != nil {
		return Connection{}, err
	}
	defer release()
	rows, active, err := m.Repo.Load(ctx)
	if err != nil {
		return Connection{}, err
	}
	c, err := connection(rows, id)
	if err != nil {
		return c, err
	}
	if c.State != "ready" || !ready(c) || c.CredentialRef == nil {
		return c, fail("CONSTRAINT_CONFLICT")
	}
	c.ModelsAsset = &asset
	c.Updated = m.Now().UTC().Format(time.RFC3339Nano)
	return c, m.Repo.Save(ctx, c, active == id)
}
