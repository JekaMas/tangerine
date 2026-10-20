package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"time"
)

// Dependency failure can be committed without media storage. It never publishes
// late model decisions, and an old owner cannot overwrite a replacement lease.
func (s *Storage) failInterpretationLease(ctx context.Context, lease InterpretationLease, code string) (string, error) {
	end, done := context.WithTimeout(ctx, 5*time.Second)
	defer done()
	tx, e := beginWrite(end, s)
	if e != nil {
		return "", e
	}
	defer tx.Rollback(context.Background())
	var payload []byte
	var revision, epoch int64
	e = tx.QueryRow(end, "SELECT d.payload,h.revision,c.epoch FROM entity_head h JOIN document d ON d.id=h.document_id JOIN interpretation_checkpoint c ON c.attempt_id=h.id WHERE h.id=$1 AND c.operation_id=$2 FOR UPDATE OF h", lease.Attempt, lease.Operation).Scan(&payload, &revision, &epoch)
	if e == pgx.ErrNoRows {
		return "", ErrEvaluationLease
	}
	if e != nil {
		return "", e
	}
	var a map[string]any
	_ = json.Unmarshal(payload, &a)
	if revision != lease.Revision || epoch != lease.Epoch || a["lease_token"] != lease.Token {
		return "", ErrEvaluationLease
	}
	id := uuid.NewString()
	raw, _ := lab.Canonical(map[string]any{"code": code, "message": "Checking is unavailable. The original answer is saved.", "request_id": lease.Operation, "retryable": true, "object_id": nil, "details": []any{}})
	registry, e := contracts.Registry()
	if e != nil {
		return "", e
	}
	w := DocumentWrite{ID: id, Kind: "error-response", Version: "2.0.0", Scope: "local", Payload: raw}
	d := SavedDocument{ID: id, Kind: w.Kind, Version: w.Version, SchemaSHA: registry[w.Kind].SHA, SHA: contracts.Digest(raw), Payload: raw}
	if e = insertDocument(end, tx, w, d); e != nil {
		return "", e
	}
	a["state"] = "evaluation_failed"
	a["revision"] = float64(revision + 1)
	a["lease_token"] = nil
	a["lease_expires_at"] = nil
	if e = s.writeInterpretationAttempt(end, tx, a, revision); e != nil {
		return "", e
	}
	if _, e = tx.Exec(end, "UPDATE operation SET state='failed',subject_id=$2,error_document_id=$3,finished_at=clock_timestamp() WHERE id=$1", lease.Operation, lease.Attempt, id); e != nil {
		return "", e
	}
	// Keep accepted prior stage documents for retry. A missing initial checkpoint
	// remains absent rather than fabricating a linked output blob.
	return id, tx.Commit(end)
}
