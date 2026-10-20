package app

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/provider"
)

func (s *Storage) mutationActionResult(ctx context.Context, operation string) (map[string]any, error) {
	var id string
	if e := s.DB.QueryRow(ctx, "SELECT result_document_id FROM operation WHERE id=$1", operation).Scan(&id); e != nil {
		return nil, e
	}
	doc, e := s.ReadDocument(ctx, id)
	if e != nil {
		return nil, e
	}
	var p map[string]any
	e = json.Unmarshal(doc.Payload, &p)
	return p, e
}
func (s *Storage) acknowledgeMutation(ctx context.Context, operation, preparation string) error {
	_, e := s.DB.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2::text,result_document_id=(SELECT document_id FROM entity_head WHERE id=$2::text),finished_at=clock_timestamp() WHERE id=$1 AND state='reserved'", operation, preparation)
	return e
}
func (s *Storage) claimMutation(ctx context.Context, operation string) error {
	tag, e := s.DB.Exec(ctx, "UPDATE operation SET state='running' WHERE id=$1 AND state='reserved'", operation)
	if e != nil {
		return e
	}
	if tag.RowsAffected() != 1 {
		return &provider.Failure{Code: "LEASE_ACTIVE"}
	}
	return nil
}
func (s *Storage) releaseMutation(ctx context.Context, operation string) {
	_, _ = s.DB.Exec(ctx, "UPDATE operation SET state='interrupted',finished_at=clock_timestamp() WHERE id=$1 AND state='running'", operation)
}

// Recovery is bounded to children of this preparation's recorded action lineage.
func (s *Storage) completedMutationChild(ctx context.Context, parents []any) (string, error) {
	for _, parent := range parents {
		var child string
		e := s.DB.QueryRow(ctx, "SELECT child.id FROM operation parent JOIN operation child ON child.idempotency_key=parent.idempotency_key AND child.operation_name='mutation' WHERE parent.id=$1 AND parent.operation_name='mutation_prepare' AND child.state='complete'", parent).Scan(&child)
		if errors.Is(e, pgx.ErrNoRows) {
			continue
		}
		return child, e
	}
	return "", nil
}

// The candidate content already passed its owning admission. This server-created
// envelope adds only routing/version metadata; persist it without checking the
// accepted candidate a second time. The preparation CAS owns its association.
func (s *Storage) saveMutationCandidate(ctx context.Context, id string, body []byte) error {
	registry, e := contracts.Registry()
	if e != nil {
		return e
	}
	c := registry["candidate-envelope"]
	write := DocumentWrite{ID: id, Kind: "candidate-envelope", Version: c.Version, Scope: "local", Payload: body, Head: &HeadWrite{ID: id, State: "candidate"}}
	saved := SavedDocument{ID: id, Kind: write.Kind, Version: c.Version, SchemaSHA: c.SHA, SHA: contracts.Digest(body), Payload: body}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	if e = insertDocument(ctx, tx, write, saved); e != nil {
		return e
	}
	return tx.Commit(ctx)
}
