package app

// Transactions own the foreground lease, immutable checkpoints and final handoff.
// Linked accepted stage assets are trusted on explicit retry; no model call or
// transaction-spanning external work belongs here.
import (
	"context"
	"encoding/json"
	"errors"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
)

var ErrEvaluationActive = errors.New("evaluation already active")
var ErrEvaluationLease = errors.New("evaluation owner is stale or late")

type InterpretationState struct {
	Version    string  `json:"schema_version"`
	ID         string  `json:"id"`
	Attempt    string  `json:"attempt_id"`
	Case       string  `json:"case_version_id"`
	AnswerSHA  string  `json:"answer_sha256"`
	ConfigSHA  string  `json:"configuration_sha256"`
	BundleSHA  string  `json:"prompt_bundle_sha256"`
	Status     string  `json:"status"`
	Resources  string  `json:"resources_asset_id"`
	Extraction *string `json:"extraction_asset_id"`
	Mapping    *string `json:"mapping_asset_id"`
	Audit      *string `json:"audit_asset_id"`
	Issues     string  `json:"issues_asset_id"`
	Stages     string  `json:"stages_asset_id"`
	Failure    *string `json:"failure_code"`
}
type InterpretationLease struct {
	Attempt, Operation, Token string
	Epoch, Revision           int64
	Deadline                  time.Time
	Snapshot                  AttemptRecord
	Previous                  *InterpretationState
	Replay                    bool
}

func readInterpretationState(ctx context.Context, q interface {
	QueryRow(context.Context, string, ...any) pgx.Row
}, id string) (*InterpretationState, error) {
	var raw []byte
	var kind string
	var document, operationState string
	var failureRaw []byte
	e := q.QueryRow(ctx, "SELECT coalesce(d.payload,f.payload),coalesce(d.kind,f.kind),coalesce(d.id,f.id),o.state,f.payload FROM interpretation_checkpoint c JOIN operation o ON o.id=c.operation_id LEFT JOIN document d ON d.id=c.document_id LEFT JOIN document f ON f.id=o.error_document_id WHERE c.attempt_id=$1 AND (d.id IS NOT NULL OR f.id IS NOT NULL)", id).Scan(&raw, &kind, &document, &operationState, &failureRaw)
	if e == pgx.ErrNoRows {
		return nil, nil
	}
	if e != nil {
		return nil, e
	}
	var state InterpretationState
	if kind == "error-response" {
		var failure struct {
			Code string `json:"code"`
		}
		e = json.Unmarshal(raw, &failure)
		state = InterpretationState{Version: "2.0.0", ID: document, Status: "failed", Failure: &failure.Code}
	} else {
		e = json.Unmarshal(raw, &state)
	}
	if e == nil && operationState == "failed" && len(failureRaw) > 0 {
		var failure struct {
			Code string `json:"code"`
		}
		_ = json.Unmarshal(failureRaw, &failure)
		state.Status = "failed"
		state.Failure = &failure.Code
	}
	if e == nil && (operationState == "reserved" || operationState == "running") {
		state.Status = "running"
		state.Failure = nil
	}
	return &state, e
}
func (s *Storage) interpretationState(ctx context.Context, id string) (*InterpretationState, error) {
	return readInterpretationState(ctx, s.DB, id)
}
func (s *Storage) acquireInterpretation(ctx context.Context, id, key string, revision int64, answerSHA, configurationSHA string) (InterpretationLease, error) {
	lease := InterpretationLease{Attempt: id}
	record, e := s.Attempt(ctx, id)
	if e != nil {
		return lease, e
	}
	if record.Attempt["submitted_at"] == nil {
		return lease, ErrAttemptState
	}
	if record.Attempt["answer_utf8_sha256"] != answerSHA || record.Attempt["configuration_sha256"] != configurationSHA {
		return lease, ErrConflict
	}
	raw, _ := lab.Canonical(map[string]any{"answer_sha256": answerSHA, "configuration_sha256": configurationSHA})
	request := OperationRequest{Name: "interpret_answer", Path: "/api/v1/attempts/" + id + ":retry", Key: key, Revision: &revision, Body: raw}
	digest, e := operationDigest(request)
	if e != nil {
		return lease, ErrInput
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return lease, e
	}
	defer tx.Rollback(context.Background())
	op, _, e := reserveOperation(ctx, tx, request, digest)
	if e != nil {
		return lease, e
	}
	lease.Operation = op.ID
	if op.Result != nil || op.State == "failed" {
		lease.Replay = true
		return lease, tx.Commit(ctx)
	}
	var payload []byte
	var current int64
	var now time.Time
	e = tx.QueryRow(ctx, "SELECT d.payload,h.revision,clock_timestamp() FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id=$1 AND h.kind='attempt' FOR UPDATE OF h", id).Scan(&payload, &current, &now)
	if e != nil {
		return lease, e
	}
	var a map[string]any
	_ = json.Unmarshal(payload, &a)
	if a["lease_token"] != nil && a["lease_expires_at"] != nil {
		expires, _ := time.Parse(time.RFC3339Nano, a["lease_expires_at"].(string))
		if expires.After(now) {
			return lease, ErrEvaluationActive
		}
	}
	if current != revision {
		return lease, ErrRevision
	}
	previous, e := readInterpretationState(ctx, tx, id)
	if e != nil {
		return lease, e
	}
	lease.Previous = previous
	lease.Snapshot = record
	lease.Token = uuid.NewString()
	lease.Epoch = int64(a["lease_epoch"].(float64)) + 1
	lease.Deadline = now.Add(270 * time.Second)
	lease.Revision = current + 1
	a["revision"] = float64(lease.Revision)
	a["state"] = "evaluating"
	a["lease_token"] = lease.Token
	a["lease_epoch"] = lease.Epoch
	a["lease_expires_at"] = now.Add(300 * time.Second).UTC().Format(time.RFC3339Nano)
	if e = s.writeInterpretationAttempt(ctx, tx, a, current); e != nil {
		return lease, e
	}
	if _, e = tx.Exec(ctx, "UPDATE operation SET state='running',subject_id=$2 WHERE id=$1", op.ID, id); e != nil {
		return lease, e
	}
	_, e = tx.Exec(ctx, "INSERT INTO interpretation_checkpoint(attempt_id,operation_id,epoch,deadline_at) VALUES($1,$2,$3,$4) ON CONFLICT(attempt_id) DO UPDATE SET operation_id=$2,epoch=$3,deadline_at=$4", id, op.ID, lease.Epoch, lease.Deadline)
	if e != nil {
		return lease, e
	}
	return lease, tx.Commit(ctx)
}
func (s *Storage) writeInterpretationAttempt(ctx context.Context, tx pgx.Tx, a map[string]any, revision int64) error {
	var initial, caseSHA string
	if e := tx.QueryRow(ctx, "SELECT x.payload_sha256,c.payload_sha256 FROM document x JOIN document c ON c.id=$2 WHERE x.id=$1", a["attempt_id"], a["case_version_id"]).Scan(&initial, &caseSHA); e != nil {
		return e
	}
	w := attemptWrite(a, uuid.NewString(), &revision, caseSHA, initial)
	// This is an application transition of an accepted attempt, not another schema
	// or definition qualification. CAS/FKs retain actual operation ownership.
	registry, e := contracts.Registry()
	if e != nil {
		return e
	}
	d := SavedDocument{ID: w.ID, Kind: w.Kind, Version: w.Version, SchemaSHA: registry["attempt"].SHA, SHA: contracts.Digest(w.Payload), Payload: w.Payload}
	return insertDocument(ctx, tx, w, d)
}
func (s *Storage) checkpointInterpretation(ctx context.Context, lease InterpretationLease, state *InterpretationState, finish bool) error {
	state.ID = uuid.NewString()
	raw, _ := lab.Canonical(state)
	refs := []Reference{}
	for _, v := range []struct{ field, id, kind string }{{"attempt_id", state.Attempt, "attempt"}, {"case_version_id", state.Case, "ground-truth"}} {
		var digest string
		if e := s.DB.QueryRow(ctx, "SELECT payload_sha256 FROM document WHERE id=$1", v.id).Scan(&digest); e != nil {
			return e
		}
		refs = append(refs, Reference{Pointer: "/" + v.field, ID: v.id, Scope: "local", Kind: v.kind, SHA: digest, Relation: "interpretation-input"})
	}
	for field, id := range map[string]string{"resources_asset_id": state.Resources, "issues_asset_id": state.Issues, "stages_asset_id": state.Stages, "extraction_asset_id": optionalID(state.Extraction), "mapping_asset_id": optionalID(state.Mapping), "audit_asset_id": optionalID(state.Audit)} {
		if id == "" {
			continue
		}
		ref, err := s.assetByteReference(ctx, id, "/"+field, "interpretation-stage")
		if err != nil {
			return err
		}
		refs = append(refs, ref)
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	var payload []byte
	var revision, epoch int64
	var live bool
	e = tx.QueryRow(ctx, `SELECT d.payload,h.revision,c.epoch,clock_timestamp()<c.deadline_at FROM entity_head h JOIN document d ON d.id=h.document_id JOIN interpretation_checkpoint c ON c.attempt_id=h.id WHERE h.id=$1 AND c.operation_id=$2 FOR UPDATE OF h`, lease.Attempt, lease.Operation).Scan(&payload, &revision, &epoch, &live)
	if e == pgx.ErrNoRows {
		return ErrEvaluationLease
	}
	if e != nil {
		return e
	}
	var a map[string]any
	_ = json.Unmarshal(payload, &a)
	if (!live && !(finish && state.Status == "failed")) || revision != lease.Revision || epoch != lease.Epoch || a["lease_token"] != lease.Token {
		return ErrEvaluationLease
	}
	registry, e := contracts.Registry()
	if e != nil {
		return e
	}
	w := DocumentWrite{ID: state.ID, Kind: "interpretation-checkpoint", Version: "2.0.0", Scope: "local", Payload: raw, References: refs}
	doc := SavedDocument{ID: w.ID, Kind: w.Kind, Version: w.Version, SchemaSHA: registry[w.Kind].SHA, SHA: contracts.Digest(raw), Payload: raw}
	if e = insertDocument(ctx, tx, w, doc); e != nil {
		return e
	}
	if _, e = tx.Exec(ctx, "UPDATE interpretation_checkpoint SET document_id=$2 WHERE attempt_id=$1", lease.Attempt, state.ID); e != nil {
		return e
	}
	if finish {
		a["lease_token"] = nil
		a["lease_expires_at"] = nil
		a["revision"] = float64(revision + 1)
		next := "saved"
		if state.Status == "failed" {
			next = "evaluation_failed"
		}
		if state.Status == "review_required" {
			next = "review_required"
		}
		a["state"] = next
		if e = s.writeInterpretationAttempt(ctx, tx, a, revision); e != nil {
			return e
		}
		if _, e = tx.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2,result_document_id=$3,finished_at=clock_timestamp() WHERE id=$1", lease.Operation, lease.Attempt, state.ID); e != nil {
			return e
		}
	}
	return tx.Commit(ctx)
}
