package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/url"
	"path"
	"strings"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
)

var ErrConflict = errors.New("conflicting idempotency request")
var ErrRevision = errors.New("stale entity revision")
var ErrReference = errors.New("invalid exact reference closure")
var ErrUnavailable = errors.New("asset is not linked")

type Node struct {
	ID          string  `json:"id"`
	Pointer     string  `json:"pointer"`
	Kind        string  `json:"kind"`
	CaseVersion *string `json:"case_version,omitempty"`
}
type Reference struct {
	Pointer  string `json:"pointer"`
	ID       string `json:"id"`
	Scope    string `json:"scope"`
	Kind     string `json:"kind"`
	SHA      string `json:"sha256"`
	Relation string `json:"relation"`
}
type HeadWrite struct {
	ID       string `json:"id"`
	Expected *int64 `json:"expected_revision"`
	State    string `json:"state"`
}
type DocumentWrite struct {
	ID         string          `json:"id"`
	Kind       string          `json:"kind"`
	Version    string          `json:"version"`
	Scope      string          `json:"scope"`
	Payload    json.RawMessage `json:"payload"`
	Nodes      []Node          `json:"nodes"`
	References []Reference     `json:"references"`
	Head       *HeadWrite      `json:"head,omitempty"`
}
type SavedDocument struct {
	ID        string          `json:"id"`
	Kind      string          `json:"kind"`
	Version   string          `json:"version"`
	SchemaSHA string          `json:"schema_sha256"`
	SHA       string          `json:"sha256"`
	Payload   json.RawMessage `json:"payload"`
}

func beginWrite(ctx context.Context, s *Storage) (pgx.Tx, error) {
	return beginWriteOn(ctx, s.DB)
}

type transactionStarter interface {
	Begin(context.Context) (pgx.Tx, error)
}

func beginWriteOn(ctx context.Context, db transactionStarter) (pgx.Tx, error) {
	tx, err := db.Begin(ctx)
	if err != nil {
		return nil, err
	}
	if _, err = tx.Exec(ctx, "SELECT pg_advisory_xact_lock_shared(79004731)"); err != nil {
		_ = tx.Rollback(ctx)
		return nil, err
	}
	var maintenance bool
	if err = tx.QueryRow(ctx, "SELECT maintenance_mode FROM workspace WHERE id='local'").Scan(&maintenance); err != nil || maintenance {
		_ = tx.Rollback(ctx)
		if err == nil {
			err = errors.New("workspace maintenance")
		}
		return nil, err
	}
	return tx, nil
}
func (s *Storage) WriteDocuments(ctx context.Context, writes []DocumentWrite) ([]SavedDocument, error) {
	if len(writes) == 0 {
		return nil, errors.New("empty document transaction")
	}
	saved := make([]SavedDocument, len(writes))
	for i, w := range writes {
		d, err := validateDocument(w)
		if err != nil {
			return nil, err
		}
		saved[i] = d
	}
	tx, err := beginWrite(ctx, s)
	if err != nil {
		return nil, err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	for i, w := range writes {
		if err = insertDocument(ctx, tx, w, saved[i]); err != nil {
			return nil, err
		}
	}
	if err = validateGraph(ctx, tx); err != nil {
		return nil, err
	}
	// Deferred foreign keys permit a forward reference in this same atomic batch.
	if err = tx.Commit(ctx); err != nil {
		return nil, err
	}
	return saved, nil
}

func validateDocument(w DocumentWrite) (SavedDocument, error) {
	c, b, err := contracts.Validate(w.Kind, w.Version, w.Payload)
	if err != nil {
		return SavedDocument{}, err
	}
	if parsed, parseErr := uuid.Parse(w.ID); parseErr != nil || parsed.Version() != 4 {
		return SavedDocument{}, errors.New("document envelope ID must be UUID")
	}
	if w.Scope == "" {
		return SavedDocument{}, ErrReference
	}
	if err = validateProjection(w, b); err != nil {
		return SavedDocument{}, err
	}
	return SavedDocument{w.ID, w.Kind, w.Version, c.SHA, contracts.Digest(b), b}, nil
}

func validateGraph(ctx context.Context, tx pgx.Tx) error {
	var cycle bool
	if err := tx.QueryRow(ctx, `WITH RECURSIVE parents AS (
 SELECT source_document_id AS origin,target_id AS next,target_scope_id AS scope,ARRAY[source_document_id]::text[] AS seen,false AS cycle FROM object_reference WHERE relation='parent-evidence'
 UNION ALL SELECT p.origin,r.target_id,r.target_scope_id,p.seen||r.source_document_id::text,r.source_document_id::text=ANY(p.seen) FROM parents p JOIN object_node n ON n.node_id=p.next AND n.scope_id=p.scope JOIN object_reference r ON r.source_document_id=n.document_id AND r.relation='parent-evidence' WHERE NOT p.cycle
 ) SELECT coalesce(bool_or(cycle),false) FROM parents`).Scan(&cycle); err != nil {
		return err
	}
	if cycle {
		return ErrReference
	}
	return nil
}
func insertDocument(ctx context.Context, tx pgx.Tx, w DocumentWrite, d SavedDocument) error {
	if w.Kind == "provider-receipt" || w.Kind == "llm-context-snapshot" {
		var lineage struct {
			Operation string `json:"operation_id"`
		}
		if err := json.Unmarshal(d.Payload, &lineage); err != nil {
			return err
		}
		var exists bool
		if err := tx.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM operation WHERE id=$1 AND workspace_id='local')", lineage.Operation).Scan(&exists); err != nil {
			return err
		}
		if !exists {
			return ErrReference
		}
	}

	if _, err := tx.Exec(ctx, "INSERT INTO document(id,workspace_id,kind,schema_version,schema_sha256,payload,payload_sha256) VALUES($1,'local',$2,$3,$4,$5,$6)", d.ID, d.Kind, d.Version, d.SchemaSHA, []byte(d.Payload), d.SHA); err != nil {
		return err
	}
	if _, err := tx.Exec(ctx, "INSERT INTO object_node(node_id,scope_id,kind,document_id,json_pointer,content_sha256) VALUES($1,$2,$3,$1,'',$4)", w.ID, w.Scope, w.Kind, d.SHA); err != nil {
		return err
	}
	for _, n := range w.Nodes {
		value, err := contracts.Pointer(d.Payload, n.Pointer)
		if err != nil {
			return err
		}
		b, _ := json.Marshal(value)
		canonical, err := contracts.Canonical(b)
		if err != nil {
			return err
		}
		if _, err = tx.Exec(ctx, "INSERT INTO object_node(node_id,scope_id,kind,document_id,json_pointer,content_sha256,case_version_id) VALUES($1,$2,$3,$4,$5,$6,$7)", n.ID, w.Scope, n.Kind, w.ID, n.Pointer, contracts.Digest(canonical), n.CaseVersion); err != nil {
			return err
		}
	}
	for _, r := range w.References {
		if _, err := tx.Exec(ctx, "INSERT INTO object_reference(source_document_id,source_pointer,target_id,target_scope_id,target_kind,expected_sha256,relation) VALUES($1,$2,$3,$4,$5,$6,$7)", w.ID, r.Pointer, r.ID, r.Scope, r.Kind, r.SHA, r.Relation); err != nil {
			return err
		}
	}
	if w.Head != nil {
		if w.Head.Expected == nil {
			if _, err := tx.Exec(ctx, "INSERT INTO entity_head(id,workspace_id,kind,document_id,revision,state) VALUES($1,'local',$2,$3,0,$4)", w.Head.ID, w.Kind, w.ID, w.Head.State); err != nil {
				return err
			}
		} else {
			tag, err := tx.Exec(ctx, "UPDATE entity_head SET document_id=$1,revision=revision+1,state=$2 WHERE id=$3 AND kind=$4 AND revision=$5", w.ID, w.Head.State, w.Head.ID, w.Kind, *w.Head.Expected)
			if err != nil {
				return err
			}
			if tag.RowsAffected() != 1 {
				return ErrRevision
			}
		}
	}
	_, err := tx.Exec(ctx, "INSERT INTO audit_event(workspace_id,action,subject_document_id,event_sha256,event_payload) VALUES('local','document.saved',$1,$2,$3)", w.ID, contracts.Digest([]byte(w.ID+d.SHA)), []byte(fmt.Sprintf(`{"document_id":%q,"sha256":%q}`, w.ID, d.SHA)))
	return err
}

// Each domain owner declares exact foreign-field roles here. Unknown kinds may be
// retained as complete typed snapshots, but cannot claim unprojected _id links.
// Opaque external provider/registry/request IDs are explicitly excluded.
func validateProjection(w DocumentWrite, b []byte) error {
	refs := map[string]Reference{}
	for _, r := range w.References {
		if _, ok := refs[r.Pointer]; ok {
			return ErrReference
		}
		v, err := contracts.Pointer(b, r.Pointer)
		if err != nil || v != r.ID || r.Scope == "" || len(r.SHA) != 64 || r.Kind == "" || r.Relation == "" {
			return ErrReference
		}
		refs[r.Pointer] = r
		if strings.Contains(r.Pointer, "/parent_evidence_ids/") && (r.Relation != "parent-evidence" || r.Kind != "evidence") {
			return ErrReference
		}
	}
	nodes := map[string]bool{w.ID: true}
	for _, n := range w.Nodes {
		if nodes[n.ID] || n.Pointer == "" || n.Kind == "" {
			return ErrReference
		}
		v, err := contracts.Pointer(b, n.Pointer+"/id")
		if err != nil || v != n.ID {
			return ErrReference
		}
		nodes[n.ID] = true
	}
	var v any
	d := json.NewDecoder(strings.NewReader(string(b)))
	d.UseNumber()
	if err := d.Decode(&v); err != nil {
		return err
	}
	foreign := map[string]bool{}
	var walk func(any, string)
	walk = func(value any, p string) {
		switch x := value.(type) {
		case map[string]any:
			for k, val := range x {
				path := p + "/" + strings.ReplaceAll(strings.ReplaceAll(k, "~", "~0"), "/", "~1")
				if val == nil {
					continue
				}
				if (strings.HasSuffix(k, "_id") || strings.HasSuffix(k, "_ids")) && !externalID(w.Kind, k) {
					switch vv := val.(type) {
					case string:
						foreign[path] = true
					case []any:
						for i := range vv {
							foreign[fmt.Sprintf("%s/%d", path, i)] = true
						}
					}
				}
				walk(val, path)
			}
		case []any:
			for i, val := range x {
				walk(val, fmt.Sprintf("%s/%d", p, i))
			}
		}
	}
	walk(v, "")
	for p := range foreign {
		if _, ok := refs[p]; !ok {
			return fmt.Errorf("%w: missing %s", ErrReference, p)
		}
	}
	for p := range refs {
		if !foreign[p] {
			return fmt.Errorf("%w: extraneous %s", ErrReference, p)
		}
	}
	return nil
}
func externalID(kind, key string) bool {
	if (kind == "provider-receipt" || kind == "llm-context-snapshot") && key == "operation_id" {
		return true
	} // validated against the relational operation owner inside the same transaction.

	if kind == "provider-connection" && (key == "client_id" || key == "ext_agent_host_id") {
		return true
	}
	if key == "workspace_id" || key == "provider_request_id" || key == "trace_id" || key == "span_id" || key == "source_request_id" || key == "selection_event_id" || (kind == "error-response" && key == "request_id") {
		return true
	}
	if (kind == "prompt-bundle" || kind == "effective-binding") && key == "prompt_id" {
		return true
	}
	return kind == "asset" && key == "version_id" // owner/version lineage is guarded by asset reservation.
}
func (s *Storage) ReadDocument(ctx context.Context, id string) (SavedDocument, error) {
	var d SavedDocument
	err := s.DB.QueryRow(ctx, "SELECT id,kind,schema_version,schema_sha256,payload_sha256,payload FROM document WHERE id=$1 AND workspace_id='local'", id).Scan(&d.ID, &d.Kind, &d.Version, &d.SchemaSHA, &d.SHA, &d.Payload)
	if err != nil {
		return d, err
	}
	c, b, err := contracts.Validate(d.Kind, d.Version, d.Payload)
	if err != nil || c.SHA != d.SchemaSHA || contracts.Digest(b) != d.SHA {
		return d, errors.New("saved document integrity mismatch")
	}
	d.Payload = b
	return d, nil
}

type OperationRequest struct {
	Name     string          `json:"operation_name"`
	Key      string          `json:"idempotency_key"`
	Path     string          `json:"path"`
	Query    json.RawMessage `json:"query"`
	Revision *int64          `json:"if_match"`
	Body     json.RawMessage `json:"body"`
}
type Operation struct {
	ID     string  `json:"id"`
	SHA    string  `json:"request_sha256"`
	State  string  `json:"state"`
	Result *string `json:"result_document_id"`
}

func operationDigest(r OperationRequest) (string, error) {
	if id, err := uuid.Parse(r.Key); err != nil || id.Version() != 4 || r.Name == "" || !strings.HasPrefix(r.Path, "/") {
		return "", errors.New("invalid operation identity")
	}
	u, err := url.ParseRequestURI(r.Path)
	if err != nil || u.RawQuery != "" || u.Fragment != "" {
		return "", errors.New("invalid concrete operation path")
	}
	r.Path = path.Clean(u.Path)
	if r.Query == nil {
		r.Query = json.RawMessage(`{}`)
	}
	if r.Body == nil {
		r.Body = json.RawMessage(`null`)
	}
	b, err := json.Marshal(struct {
		Name     string          `json:"operation_name"`
		Path     string          `json:"path"`
		Query    json.RawMessage `json:"query"`
		Revision *int64          `json:"if_match"`
		Body     json.RawMessage `json:"body"`
	}{r.Name, r.Path, r.Query, r.Revision, r.Body})
	if err != nil {
		return "", err
	}
	b, err = contracts.Canonical(b)
	if err != nil {
		return "", err
	}
	digest := contracts.Digest(b)
	return digest, nil
}

func (s *Storage) ReserveOperation(ctx context.Context, r OperationRequest) (Operation, error) {
	digest, err := operationDigest(r)
	if err != nil {
		return Operation{}, err
	}
	tx, err := beginWrite(ctx, s)
	if err != nil {
		return Operation{}, err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	o, _, err := reserveOperation(ctx, tx, r, digest)
	if err != nil {
		return o, err
	}
	return o, tx.Commit(ctx)
}
func reserveOperation(ctx context.Context, tx pgx.Tx, r OperationRequest, digest string) (Operation, bool, error) {
	id := uuid.NewString()
	_, err := tx.Exec(ctx, "INSERT INTO operation(id,workspace_id,operation_name,idempotency_key,request_sha256,state) VALUES($1,'local',$2,$3,$4,'reserved') ON CONFLICT(workspace_id,operation_name,idempotency_key) DO NOTHING", id, r.Name, r.Key, digest)
	if err != nil {
		return Operation{}, false, err
	}
	var o Operation
	err = tx.QueryRow(ctx, "SELECT id,request_sha256,state,result_document_id FROM operation WHERE workspace_id='local' AND operation_name=$1 AND idempotency_key=$2 FOR UPDATE", r.Name, r.Key).Scan(&o.ID, &o.SHA, &o.State, &o.Result)
	if err == nil && o.SHA != digest {
		err = ErrConflict
	}
	return o, o.ID == id, err
}
