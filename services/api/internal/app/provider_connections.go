package app

import (
	"context"
	"encoding/json"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/provider"
)

type providerRepository struct{ store *Storage }

// Serialize owns the installation-wide grant lease. Waiters release unsuccessful
// pool acquisitions, so they cannot starve the lease holder's native writes.
func (p providerRepository) Serialize(ctx context.Context) (func(), error) {
	for {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		connection, err := p.store.DB.Acquire(ctx)
		if err != nil {
			return nil, err
		}
		var acquired bool
		err = connection.QueryRow(ctx, "SELECT pg_try_advisory_lock(79004745)").Scan(&acquired)
		if err != nil {
			connection.Release()
			return nil, err
		}
		if acquired {
			return func() {
				end, done := context.WithTimeout(context.Background(), 5*time.Second)
				defer done()
				if _, err := connection.Exec(end, "SELECT pg_advisory_unlock(79004745)"); err != nil {
					_ = connection.Hijack().Close(end)
				} else {
					connection.Release()
				}
			}, nil
		}
		connection.Release()
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-time.After(10 * time.Millisecond):
		}
	}
}

func (p providerRepository) Load(ctx context.Context) ([]provider.Connection, string, error) {
	rows, e := p.store.DB.Query(ctx, "SELECT d.payload,h.state FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.kind='provider-connection' ORDER BY h.id")
	if e != nil {
		return nil, "", e
	}
	defer rows.Close()
	out := []provider.Connection{}
	active := ""
	for rows.Next() {
		var b []byte
		var state string
		if e = rows.Scan(&b, &state); e != nil {
			return nil, "", e
		}
		if _, _, e = contracts.Validate("provider-connection", "2.0.0", b); e != nil {
			return nil, "", e
		}
		var c provider.Connection
		if e = json.Unmarshal(b, &c); e != nil {
			return nil, "", e
		}
		if state == "active" {
			if active != "" {
				return nil, "", ErrConflict
			}
			active = c.ID
		}
		out = append(out, c)
	}
	return out, active, rows.Err()
}
func (p providerRepository) Save(ctx context.Context, c provider.Connection, active bool) error {
	tx, e := beginWrite(ctx, p.store)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	if _, e = tx.Exec(ctx, "SELECT pg_advisory_xact_lock(79004744)"); e != nil {
		return e
	}
	var writes []DocumentWrite
	rows, e := tx.Query(ctx, "SELECT h.id,h.revision,h.state,d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.kind='provider-connection' ORDER BY h.id")
	if e != nil {
		return e
	}
	type current struct {
		id       string
		revision int64
		state    string
		body     []byte
	}
	var existing []current
	for rows.Next() {
		var r current
		if e = rows.Scan(&r.id, &r.revision, &r.state, &r.body); e != nil {
			rows.Close()
			return e
		}
		existing = append(existing, r)
	}
	e = rows.Err()
	rows.Close()
	if e != nil {
		return e
	}
	target := "provider:" + c.ID
	var expected *int64
	for _, r := range existing {
		if r.id == target {
			revision := r.revision
			expected = &revision
			continue
		}
		if active && r.state == "active" {
			revision := r.revision
			writes = append(writes, DocumentWrite{ID: uuid.NewString(), Kind: "provider-connection", Version: "2.0.0", Scope: "local", Payload: r.body, Head: &HeadWrite{ID: r.id, Expected: &revision, State: "saved"}})
		}
	}
	body, _ := json.Marshal(c)
	state := "saved"
	if active {
		state = "active"
	}
	w := DocumentWrite{ID: uuid.NewString(), Kind: "provider-connection", Version: "2.0.0", Scope: "local", Payload: body, Head: &HeadWrite{ID: target, Expected: expected, State: state}}
	writes = append(writes, w)
	for i := range writes {
		var metadata provider.Connection
		_ = json.Unmarshal(writes[i].Payload, &metadata)
		if metadata.ModelsAsset != nil {
			ref := Reference{ID: *metadata.ModelsAsset, Pointer: "/models_asset_id", Relation: "provider-model-catalogue"}
			if e = tx.QueryRow(ctx, "SELECT scope_id,kind,content_sha256 FROM object_node WHERE node_id=$1 AND scope_id=$1 AND kind='asset-bytes'", ref.ID).Scan(&ref.Scope, &ref.Kind, &ref.SHA); e != nil {
				return e
			}
			writes[i].References = []Reference{ref}
		}
		saved, e := validateDocument(writes[i])
		if e != nil {
			return e
		}
		if e = insertDocument(ctx, tx, writes[i], saved); e != nil {
			return e
		}
	}
	if e = validateGraph(ctx, tx); e != nil {
		return e
	}
	return tx.Commit(ctx)
}
func (s *Storage) assetByteReference(ctx context.Context, id, pointer, relation string) (Reference, error) {
	r := Reference{Pointer: pointer, ID: id, Relation: relation}
	e := s.DB.QueryRow(ctx, "SELECT scope_id,kind,content_sha256 FROM object_node WHERE node_id=$1 AND scope_id=$1 AND kind='asset-bytes'", id).Scan(&r.Scope, &r.Kind, &r.SHA)
	return r, e
}
func newProviderManager(s *Storage) *provider.Manager {
	dir := os.Getenv("TANGERINE_PROVIDER_CREDENTIAL_DIR")
	if dir == "" {
		dir = "/provider-secrets"
	}
	return provider.New(dir, providerRepository{s}, nil, provider.OfficialProtocol())
}
func providerError(w http.ResponseWriter, e error) {
	code, _ := provider.SafeError(e)
	status := 503
	switch code {
	case "INVALID_JSON", "INVALID_UTF8":
		status = 400
	case "IDEMPOTENCY_CONFLICT", "INVALID_TRANSITION", "LEASE_ACTIVE", "LEASE_STALE", "CANCELLED":
		status = 409
	case "REVISION_STALE":
		status = 412
	case "INPUT_CAPACITY_EXCEEDED":
		status = 413
	case "SCHEMA_INVALID", "CONSTRAINT_CONFLICT":
		status = 422
	case "LOCAL_BUDGET_EXCEEDED", "LOCAL_CONCURRENCY_LIMIT":
		status = 429
	case "PROVIDER_FAILURE", "PROVIDER_REFUSAL", "PROVIDER_INCOMPLETE", "PROVIDER_OUTPUT_INVALID", "PROVIDER_SCHEMA_INCOMPATIBLE":
		status = 502
	case "DEADLINE_EXCEEDED":
		status = 504
	}
	writeJSON(w, status, map[string]any{"code": code, "message": "Provider connection is unavailable. Your saved content is retained.", "request_id": uuid.NewString(), "retryable": code == "PROVIDER_FAILURE" || code == "DEADLINE_EXCEEDED" || code == "CANCELLED", "object_id": nil, "details": []any{}})
}
func (s *Server) providerConnections(w http.ResponseWriter, r *http.Request) {
	rows, active, e := s.Providers.List(r.Context())
	if e != nil {
		providerError(w, e)
		return
	}
	w.Header().Set("X-Tangerine-Active-Connection", active)
	writeJSON(w, 200, rows)
}
func (s *Server) providerAction(w http.ResponseWriter, r *http.Request) {
	var v struct {
		Action  string  `json:"action"`
		ID      *string `json:"connection_id"`
		Credits *bool   `json:"credits_after_plan_limit_disabled"`
	}
	if e := DecodeJSON(w, r, &v); e != nil {
		writeJSON(w, 400, map[string]string{"error": "invalid_request"})
		return
	}
	id := ""
	if v.ID != nil {
		id = *v.ID
	}
	var result provider.Result
	var e error
	switch v.Action {
	case "connect":
		u, _ := url.Parse(s.Origin)
		result, e = s.Providers.Connect(r.Context(), id, "http://127.0.0.1:"+u.Port()+"/auth/callback", v.Credits)
	case "select":
		result.Connection, e = s.Providers.Select(r.Context(), id, v.Credits)
		if e == nil && result.Connection.State == "ready" {
			_, raw, me := s.Providers.Models(r.Context(), id)
			if me == nil {
				a, ae := s.Store.saveProviderBytes(r.Context(), raw, "provider_output")
				if ae == nil {
					result.Connection, ae = s.Providers.SaveModels(r.Context(), id, a.ID)
				}
				if ae != nil {
					e = ae
				}
			} else {
				e = me
			}
		}
	case "disconnect":
		result.Connection, e = s.Providers.Disconnect(r.Context(), id)
	default:
		e = &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
	}
	if e != nil {
		providerError(w, e)
		return
	}
	writeJSON(w, 200, result)
}
func (s *Server) providerCallback(w http.ResponseWriter, r *http.Request) {
	c, e := s.Providers.Callback(r.Context(), r.URL.Query())
	if e != nil {
		providerError(w, e)
		return
	}
	writeJSON(w, 200, c)
}
func (s *Server) providerModelBytes(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	rows, _, e := s.Providers.List(r.Context())
	if e != nil {
		providerError(w, e)
		return
	}
	allowed := false
	for _, c := range rows {
		allowed = allowed || (c.ModelsAsset != nil && *c.ModelsAsset == id)
	}
	if !allowed {
		writeJSON(w, 404, map[string]string{"error": "not_implemented"})
		return
	}
	b, e := s.Store.ReadAsset(r.Context(), id)
	if e != nil {
		providerError(w, e)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	w.Write(b)
}
func (s *Storage) saveProviderBytes(ctx context.Context, b []byte, purpose string) (Asset, error) {
	body, _ := json.Marshal(map[string]any{"kind": purpose, "sha256": contracts.Digest(b)})
	a, e := s.ReserveAsset(ctx, AssetRequest{Operation: OperationRequest{Name: "provider-artifact", Key: uuid.NewString(), Path: "/provider/artifact", Body: body}, SHA: contracts.Digest(b), Size: int64(len(b)), Purpose: purpose, MIME: providerMIME(b)})
	if e != nil {
		return a, e
	}
	if _, e = s.UploadAsset(ctx, a.ID, b); e != nil {
		return a, e
	}
	return s.LinkAsset(ctx, a.ID, nil)
}
func (s *Storage) providerByID(ctx context.Context, id string) (provider.Connection, error) {
	rows, _, e := providerRepository{s}.Load(ctx)
	if e != nil {
		return provider.Connection{}, e
	}
	for _, c := range rows {
		if c.ID == id {
			return c, nil
		}
	}
	return provider.Connection{}, pgx.ErrNoRows
}

// Resolve frozen registration identity, never the now-selected account. API keys
// are resolved only after the explicit included-only profile guard passes.
func providerCredential(ctx context.Context, m *provider.Manager, p provider.Profile, id string) (string, error) {
	if e := provider.Included(p); e != nil {
		return "", e
	}
	if p.Auth == "chatgpt_plan_oauth" {
		c, token, e := m.Access(ctx, id)
		if e != nil {
			return "", e
		}
		if c.CredentialRef == nil || p.CredentialRef != *c.CredentialRef {
			return "", &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
		}
		return token, nil
	}
	if p.Auth == "local_none" {
		return "", nil
	}
	// Profile refs are names, never arbitrary file paths or borrowed app credentials.
	if p.CredentialRef != "OPENAI_API_KEY" && p.CredentialRef != "DEEPSEEK_API_KEY" {
		return "", &provider.Failure{Code: "MISSING_CREDENTIALS"}
	}
	value := os.Getenv(p.CredentialRef)
	if strings.TrimSpace(value) == "" {
		return "", &provider.Failure{Code: "MISSING_CREDENTIALS"}
	}
	return value, nil
}

func providerMIME(b []byte) string {
	if json.Valid(b) {
		return "application/json"
	}
	if strings.Contains(string(b), "data:") {
		return "text/event-stream"
	}
	return "text/plain"
}
