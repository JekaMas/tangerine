package app

import (
	"context"
	"encoding/json"

	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
)

type DeletionSelection struct {
	IDs     []string `json:"subject_ids"`
	Orphans bool     `json:"orphan_cleanup"`
}
type DeletionPlan struct {
	Source     SourceErasure     `json:"source"`
	ID         string            `json:"id"`
	Selection  DeletionSelection `json:"selection"`
	Documents  []string          `json:"documents"`
	Assets     []string          `json:"assets"`
	Keys       []string          `json:"storage_keys"`
	Operations []string          `json:"operations"`
	Heads      []string          `json:"heads"`
	Blocked    []string          `json:"blocked"`
	Digest     string            `json:"confirmation_sha256"`
	State      string            `json:"state"`
	LabCleanup string            `json:"lab_cleanup"`
}

func (s *Storage) PlanDeletion(ctx context.Context, input DeletionSelection) (DeletionPlan, error) {
	if input.IDs == nil {
		input.IDs = []string{}
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return DeletionPlan{}, e
	}
	defer tx.Rollback(context.Background())
	p, e := s.deletionPlan(ctx, tx, input)
	if e != nil {
		return p, e
	}
	p.ID = uuid.NewString()
	if _, e = tx.Exec(ctx, "INSERT INTO local_deletion(id,plan) VALUES($1,$2)", p.ID, sourceBytes(p)); e != nil {
		return p, e
	}
	return p, tx.Commit(ctx)
}
func (s *Storage) ApplyDeletion(ctx context.Context, id, digest string) (DeletionPlan, error) {
	tx, e := s.DB.Begin(ctx)
	if e != nil {
		return DeletionPlan{}, e
	}
	defer tx.Rollback(context.Background())
	// This is a deletion/write race guard, not revalidation of stored content.
	if _, e = tx.Exec(ctx, "SELECT pg_advisory_xact_lock(79004731)"); e != nil {
		return DeletionPlan{}, e
	}
	if _, e = tx.Exec(ctx, "LOCK TABLE document,entity_head,operation,asset_location IN EXCLUSIVE MODE"); e != nil {
		return DeletionPlan{}, e
	}
	var raw []byte
	var state string
	e = tx.QueryRow(ctx, "SELECT plan,state FROM local_deletion WHERE id=$1 FOR UPDATE", id).Scan(&raw, &state)
	if e != nil {
		return DeletionPlan{}, e
	}
	var p DeletionPlan
	if e = json.Unmarshal(raw, &p); e != nil {
		return p, e
	}
	if p.Digest != digest {
		return p, ErrConflict
	}
	if state == "erased" {
		if e = tx.Commit(ctx); e != nil {
			return p, e
		}
		return s.finishDeletionBytes(ctx, p)
	}
	current, e := s.deletionPlan(ctx, tx, p.Selection)
	if e != nil {
		return p, e
	}
	if current.Digest != p.Digest || len(current.Blocked) > 0 {
		return p, ErrRevision
	}
	if _, e = tx.Exec(ctx, "SET LOCAL tangerine.maintenance_delete='on'"); e != nil {
		return p, e
	}
	if e = eraseSourceRows(ctx, tx, p.Source); e != nil {
		return p, e
	}
	// Remove payload-bearing diagnostics, then their relational indexes. No answer
	// or audio copy is kept in a tombstone or the plan.
	statements := []string{
		`DELETE FROM quality_call WHERE receipt_id=ANY($1) OR row_operation_id=ANY($4)`,
		`DELETE FROM stage_cache_index WHERE document_id=ANY($1) OR attempt_id=ANY($2)`,
		`DELETE FROM playback_index WHERE event_id=ANY($1) OR attempt_id=ANY($2)`,
		`DELETE FROM interpretation_checkpoint WHERE attempt_id=ANY($2)`,
		`DELETE FROM evaluation_lease WHERE attempt_id=ANY($2)`,
		`DELETE FROM reviewed_case_successor WHERE review_id IN(SELECT id FROM review_checkpoint WHERE case_version_id=ANY($1) OR attempt_id=ANY($2)) OR old_case_version_id=ANY($1) OR new_case_version_id=ANY($1)`,
		`DELETE FROM review_event WHERE review_id IN(SELECT id FROM review_checkpoint WHERE case_version_id=ANY($1) OR attempt_id=ANY($2))`,
		`DELETE FROM review_checkpoint WHERE case_version_id=ANY($1) OR attempt_id=ANY($2)`,
		`DELETE FROM attempt_context WHERE attempt_id=ANY($2) OR case_version_id=ANY($1)`,
		`DELETE FROM exercise_catalog WHERE id::text=ANY($1)`,
		`DELETE FROM listening_case WHERE case_version_id=ANY($1) OR source_key_id=ANY($1)`,
		`DELETE FROM usage_ledger WHERE receipt_id=ANY($1) OR operation_id=ANY($4)`,
		`DELETE FROM audit_event WHERE subject_document_id=ANY($1) OR details_document_id=ANY($1) OR operation_id=ANY($4)`,
		`DELETE FROM object_reference WHERE source_document_id=ANY($1)`,
		`DELETE FROM asset_location WHERE asset_id=ANY($3)`,
		`DELETE FROM operation WHERE id=ANY($4) OR input_document_id=ANY($1) OR result_document_id=ANY($1) OR error_document_id=ANY($1)`,
		`DELETE FROM entity_head WHERE id=ANY($2)`,
		`DELETE FROM object_node WHERE document_id=ANY($1)`,
		`DELETE FROM document WHERE id=ANY($1)`,
	}
	for _, statement := range statements {
		// Bind all four typed arrays even when an individual statement uses a subset.
		query := "WITH inputs AS (SELECT $1::varchar[],$2::varchar[],$3::varchar[],$4::varchar[]) " + statement
		if _, e = tx.Exec(ctx, query, p.Documents, p.Heads, p.Assets, p.Operations); e != nil {
			return p, e
		}
	}
	if _, e = tx.Exec(ctx, `INSERT INTO deletion_tombstone(id,original_document_id,deletion_request_id,permitted_retention_basis,deleted_at) SELECT gen_random_uuid()::text,unnest($1::varchar[]),$2,'operator_delete',clock_timestamp()`, p.Documents, id); e != nil {
		return p, e
	}
	p.State = "native_erased"
	if p.LabCleanup == "not_requested" {
		p.State = "erased"
	}
	if _, e = tx.Exec(ctx, "UPDATE local_deletion SET state='erased',plan=$2 WHERE id=$1", id, sourceBytes(p)); e != nil {
		return p, e
	}
	if e = tx.Commit(ctx); e != nil {
		return p, e
	}
	return s.finishDeletionBytes(ctx, p)
}
func (s *Storage) finishDeletionBytes(ctx context.Context, p DeletionPlan) (DeletionPlan, error) {
	for _, key := range p.Keys {
		if e := s.Media.RemoveObject(ctx, s.Bucket, key, minio.RemoveObjectOptions{}); e != nil {
			p.State = "native_erased_media_cleanup_pending"
			return p, e
		}
	}
	return p, nil
}
