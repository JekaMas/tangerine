package app

import (
	"context"
	"encoding/json"
)

// Called by the local Docker helper only after its explicit entire-Lab purge.
func (s *Storage) RecordLabPurge(ctx context.Context) error {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	rows, e := tx.Query(ctx, "SELECT id::text,plan FROM local_deletion WHERE state='erased' FOR UPDATE")
	if e != nil {
		return e
	}
	plans := []DeletionPlan{}
	for rows.Next() {
		var id string
		var raw []byte
		if e = rows.Scan(&id, &raw); e != nil {
			rows.Close()
			return e
		}
		var p DeletionPlan
		if e = json.Unmarshal(raw, &p); e != nil {
			rows.Close()
			return e
		}
		if p.LabCleanup == "pending_explicit_local_lab_cleanup" {
			p.LabCleanup = "erased"
			plans = append(plans, p)
		}
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return e
	}
	for _, p := range plans {
		if _, e = tx.Exec(ctx, "UPDATE local_deletion SET plan=$2 WHERE id=$1", p.ID, sourceBytes(p)); e != nil {
			return e
		}
	}
	return tx.Commit(ctx)
}
