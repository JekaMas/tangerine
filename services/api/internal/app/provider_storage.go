package app

import (
	"context"
	"tangerine.local/api/internal/provider"
)

// Shared inference persistence stays with Storage; the application owner controls
// dispatch/evidence construction and retains the same operation write ordering.
func (s *Storage) claimInference(ctx context.Context, id string) error {
	tag, err := s.DB.Exec(ctx, "UPDATE operation SET state='running' WHERE id=$1 AND state='reserved'", id)
	if err != nil {
		return err
	}
	if tag.RowsAffected() != 1 {
		return &provider.Failure{Code: "LEASE_ACTIVE"}
	}
	return nil
}
func (s *Storage) releaseInference(ctx context.Context, id string) {
	_, _ = s.DB.Exec(ctx, "UPDATE operation SET state='interrupted',finished_at=clock_timestamp() WHERE id=$1 AND state='running'", id)
}
func (s *Storage) bindInference(ctx context.Context, id, binding string) error {
	_, err := s.DB.Exec(ctx, "UPDATE operation SET input_document_id=$2 WHERE id=$1", id, binding)
	return err
}
func (s *Storage) completeInference(ctx context.Context, id, asset string) error {
	_, err := s.DB.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2::text,result_document_id=(SELECT document_id FROM entity_head WHERE id=$2),finished_at=clock_timestamp() WHERE id=$1 AND state='running'", id, asset)
	return err
}

func (s *Storage) ReadLLMResult(ctx context.Context, id string) (LLMResult, error) {
	r := LLMResult{OperationID: id, ReceiptIDs: []string{}, ContextIDs: []string{}}
	var asset string
	e := s.DB.QueryRow(ctx, "SELECT subject_id,input_document_id FROM operation WHERE id=$1 AND state='complete'", id).Scan(&asset, &r.BindingID)
	if e != nil {
		return r, e
	}
	b, e := s.ReadAsset(ctx, asset)
	if e != nil {
		return r, e
	}
	r.Output = b
	rows, e := s.DB.Query(ctx, "SELECT id,payload->>'context_snapshot_id' FROM document WHERE kind='provider-receipt' AND payload->>'operation_id'=$1 ORDER BY (payload->>'transport_attempt')::int", id)
	if e != nil {
		return r, e
	}
	defer rows.Close()
	for rows.Next() {
		var a, b string
		if e = rows.Scan(&a, &b); e != nil {
			return r, e
		}
		r.ReceiptIDs = append(r.ReceiptIDs, a)
		r.ContextIDs = append(r.ContextIDs, b)
	}
	return r, rows.Err()
}
