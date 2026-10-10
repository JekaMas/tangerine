package app

import (
	"context"
	_ "embed"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"io"
	"net/http"
	"os"
	"strconv"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

//go:embed provider-default.json
var providerDefault []byte

func DefaultConfiguration() map[string]any {
	var c map[string]any
	_ = json.Unmarshal(providerDefault, &c)
	c["configuration_sha256"] = lab.Hash(c)
	return c
}
func (s *Storage) Configuration(ctx context.Context) (map[string]any, int64, error) {
	var raw []byte
	var rev int64
	e := s.DB.QueryRow(ctx, "SELECT d.payload,h.revision FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id='local-configuration' AND h.kind='configuration'").Scan(&raw, &rev)
	if errors.Is(e, pgx.ErrNoRows) {
		return DefaultConfiguration(), -1, nil
	}
	if e != nil {
		return nil, 0, e
	}
	var c map[string]any
	e = json.Unmarshal(raw, &c)
	return c, rev, e
}
func (s *Storage) PutConfiguration(ctx context.Context, raw []byte, key string, revision int64) (map[string]any, int64, error) {
	_, raw, e := contracts.Validate("put-config-request", "2.0.0", raw)
	if e != nil {
		return nil, 0, e
	}
	var c map[string]any
	_ = json.Unmarshal(raw, &c)
	if e = validateProfileSelection(c); e != nil {
		return nil, 0, e
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return nil, 0, e
	}
	defer tx.Rollback(context.Background())
	// Same serialization lock as connection changes, so a selected profile cannot
	// race a registration disconnect or catalogue replacement during configuration save.
	if _, e = tx.Exec(ctx, "SELECT pg_advisory_xact_lock(79004744)"); e != nil {
		return nil, 0, e
	}
	request := OperationRequest{Name: "put_config", Key: key, Path: "/api/v1/configuration", Revision: &revision, Body: raw}
	digest, e := operationDigest(request)
	if e != nil {
		return nil, 0, e
	}
	op, _, e := reserveOperation(ctx, tx, request, digest)
	if e != nil {
		return nil, 0, e
	}
	if op.Result != nil {
		var saved []byte
		e = tx.QueryRow(ctx, "SELECT payload FROM document WHERE id=$1", *op.Result).Scan(&saved)
		if e != nil {
			return nil, 0, e
		}
		_ = json.Unmarshal(saved, &c)
		if e = tx.Commit(ctx); e != nil {
			return nil, 0, e
		}
		return c, revision + 1, nil
	}
	var previous []byte
	current := int64(-1)
	e = tx.QueryRow(ctx, "SELECT d.payload,h.revision FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id='local-configuration' AND h.kind='configuration' FOR UPDATE OF h").Scan(&previous, &current)
	if e != nil && !errors.Is(e, pgx.ErrNoRows) {
		return nil, 0, e
	}
	if current != revision {
		return nil, current, ErrRevision
	}
	var old map[string]any
	if len(previous) > 0 {
		_ = json.Unmarshal(previous, &old)
	}
	// Billing exclusion is not editable through an ordinary settings request.
	c["provider_access_policy"] = DefaultConfiguration()["provider_access_policy"]
	if policy, ok := old["provider_access_policy"]; ok {
		c["provider_access_policy"] = policy
	}
	c["workspace_id"] = "local"
	c["configuration_sha256"] = lab.Hash(c)
	body, _ := lab.Canonical(c)
	w := DocumentWrite{ID: uuid.NewString(), Kind: "configuration", Version: "2.0.0", Scope: "local", Payload: body, Head: &HeadWrite{ID: "local-configuration", State: "active"}}
	if revision >= 0 {
		w.Head.Expected = &revision
	}
	if id, ok := c["active_prompt_bundle_id"].(string); ok {
		var sha string
		e = tx.QueryRow(ctx, "SELECT payload_sha256 FROM document WHERE id=$1 AND kind='prompt-bundle'", id).Scan(&sha)
		if e != nil {
			return nil, 0, e
		}
		w.References = []Reference{{Pointer: "/active_prompt_bundle_id", ID: id, Scope: "local", Kind: "prompt-bundle", SHA: sha, Relation: "active-prompt-bundle"}}
	}
	saved, e := validateDocument(w)
	if e != nil {
		return nil, 0, e
	}
	if e = insertDocument(ctx, tx, w, saved); e != nil {
		return nil, 0, e
	}
	if e = validateGraph(ctx, tx); e != nil {
		return nil, 0, e
	}
	if _, e = tx.Exec(ctx, "UPDATE operation SET state='complete',finished_at=clock_timestamp(),result_document_id=$2 WHERE id=$1", op.ID, w.ID); e != nil {
		return nil, 0, e
	}
	if e = tx.Commit(ctx); e != nil {
		return nil, 0, e
	}
	return c, current + 1, nil
}
func validateProfileSelection(c map[string]any) error {
	raw, _ := json.Marshal(c["llm_profiles"])
	var ps []provider.Profile
	if json.Unmarshal(raw, &ps) != nil {
		return ErrConflict
	}
	ids := map[string]provider.Profile{}
	for _, p := range ps {
		if _, ok := ids[p.ID]; ok {
			return ErrConflict
		}
		if e := provider.ValidateProfile(p); e != nil {
			return e
		}
		ids[p.ID] = p
	}
	selected, ok := c["llm_profile"].(string)
	if !ok {
		return ErrConflict
	}
	if _, ok = ids[selected]; !ok {
		return ErrReference
	}
	stages, ok := c["stage_profiles"].(map[string]any)
	if !ok {
		return ErrReference
	}
	for role, id := range stages {
		name := selected
		if id != nil {
			var ok bool
			name, ok = id.(string)
			if !ok {
				return ErrReference
			}
		}
		p, ok := ids[name]
		if !ok {
			return ErrReference
		}
		found := false
		for _, r := range p.Roles {
			found = found || role == r
		}
		if !found {
			return ErrReference
		}
	}
	return nil
}
func configurationView(c map[string]any) map[string]any {
	ids := []string{}
	for _, x := range c["llm_profiles"].([]any) {
		ids = append(ids, x.(map[string]any)["id"].(string))
	}
	creds := []any{}
	now := time.Now().UTC().Format(time.RFC3339Nano)
	for _, name := range []string{"OPENAI_API_KEY", "DEEPSEEK_API_KEY", "AZURE_SPEECH_KEY"} {
		creds = append(creds, map[string]any{"name": name, "present": os.Getenv(name) != "", "last_checked_at": now})
	}
	return map[string]any{"configuration_sha256": c["configuration_sha256"], "profile_ids": ids, "credentials": creds, "source_statuses": []any{}, "intended_uses": c["intended_uses"], "limits": c["limits"], "configuration": c}
}
func (s *Server) configurationGet(w http.ResponseWriter, r *http.Request) {
	c, rev, e := s.Store.Configuration(r.Context())
	if e != nil {
		providerError(w, e)
		return
	}
	w.Header().Set("ETag", strconv.Quote(strconv.FormatInt(rev, 10)))
	writeJSON(w, 200, configurationView(c))
}
func (s *Server) configurationPut(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		providerError(w, &provider.Failure{Code: "INVALID_JSON"})
		return
	}
	raw, e := io.ReadAll(http.MaxBytesReader(w, r.Body, 2*1024*1024))
	if e != nil {
		providerError(w, &provider.Failure{Code: "INPUT_CAPACITY_EXCEEDED"})
		return
	}
	// Ignore additive interface fields, then persist the exact closed contract.
	reg, _ := contracts.Registry()
	var schema struct{ Properties map[string]any }
	_ = json.Unmarshal(reg["put-config-request"].Bytes, &schema)
	if _, e = contracts.Canonical(raw); e != nil {
		providerError(w, &provider.Failure{Code: "INVALID_JSON"})
		return
	}
	var c map[string]json.RawMessage
	if json.Unmarshal(raw, &c) != nil {
		providerError(w, &provider.Failure{Code: "INVALID_JSON"})
		return
	}
	for k := range c {
		if _, ok := schema.Properties[k]; !ok {
			delete(c, k)
		}
	}
	raw, _ = json.Marshal(c)
	revision, e := strconv.ParseInt(strings.Trim(r.Header.Get("If-Match"), "\""), 10, 64)
	if e != nil || revision < -1 {
		providerError(w, &provider.Failure{Code: "REVISION_STALE"})
		return
	}
	conf, rev, e := s.Store.PutConfiguration(r.Context(), raw, r.Header.Get("Idempotency-Key"), revision)
	if e != nil {
		code := "SCHEMA_INVALID"
		if errors.Is(e, ErrConflict) {
			code = "IDEMPOTENCY_CONFLICT"
		}
		if errors.Is(e, ErrRevision) {
			code = "REVISION_STALE"
		}
		providerError(w, &provider.Failure{Code: code})
		return
	}
	w.Header().Set("ETag", strconv.Quote(strconv.FormatInt(rev, 10)))
	writeJSON(w, 200, configurationView(conf))
}

// FreezeProfile resolves an explicit role override or the selected default; no
// error fallback. Saved returned values are used through every logical retry.
func FreezeProfile(c map[string]any, stage string) (provider.Profile, error) {
	if e := validateProfileSelection(c); e != nil {
		return provider.Profile{}, e
	}
	id := c["llm_profile"].(string)
	if x := c["stage_profiles"].(map[string]any)[stage]; x != nil {
		id = x.(string)
	}
	raw, _ := json.Marshal(c["llm_profiles"])
	var rows []provider.Profile
	_ = json.Unmarshal(raw, &rows)
	for _, p := range rows {
		if p.ID == id {
			if p.Model == "unselected" {
				return p, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
			}
			return p, provider.Included(p)
		}
	}
	return provider.Profile{}, ErrReference
}

func (s *Server) providerReadiness(ctx context.Context) string {
	c, _, e := s.Store.Configuration(ctx)
	if e != nil {
		return "missing_credentials"
	}
	p, e := FreezeProfile(c, "case_generation")
	if e != nil {
		return "missing_credentials"
	}
	if p.Auth == "chatgpt_plan_oauth" {
		if s.Providers.Configured(ctx, p.CredentialRef) != nil {
			return "missing_credentials"
		}
		conn, e := s.Store.providerByID(ctx, p.CredentialRef)
		if e != nil || conn.ModelsAsset == nil {
			return "missing_credentials"
		}
		raw, e := s.Store.ReadAsset(ctx, *conn.ModelsAsset)
		if e != nil {
			return "missing_credentials"
		}
		var catalogue struct{ Models []provider.Model }
		if json.Unmarshal(raw, &catalogue) != nil {
			return "missing_credentials"
		}
		for _, m := range catalogue.Models {
			if m.Slug == p.Model && m.Visibility == "list" {
				return "ready"
			}
		}
		return "missing_credentials"
	}
	if p.Auth == "local_none" {
		return "ready"
	}
	if (p.CredentialRef == "OPENAI_API_KEY" || p.CredentialRef == "DEEPSEEK_API_KEY") && strings.TrimSpace(os.Getenv(p.CredentialRef)) != "" {
		return "ready"
	}
	return "missing_credentials"
}
