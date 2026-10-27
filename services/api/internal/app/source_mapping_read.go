package app

import (
	"context"
	"tangerine.local/api/internal/source"
)

// Staging is finished before projection. Advance within this call instead of
// rescanning an increasingly large accepted prefix for every batch. On reopen,
// durable row states still own progress; no accepted row is re-admitted.
func (s *Storage) sourceProjectionBatch(ctx context.Context, id string, cursor stagedSourceRow) ([]stagedSourceRow, error) {
	rows, e := s.DB.Query(ctx, "SELECT member,table_name,ordinal,native_row FROM source_row WHERE import_id=$1 AND state='staged' AND (member,table_name,ordinal)>($2,$3,$4) ORDER BY member,table_name,ordinal LIMIT 64", id, cursor.Member, cursor.Table, cursor.Ordinal)
	if e != nil {
		return nil, e
	}
	batch := []stagedSourceRow{}
	for rows.Next() {
		var r stagedSourceRow
		var raw []byte
		if e = rows.Scan(&r.Member, &r.Table, &r.Ordinal, &raw); e != nil {
			rows.Close()
			return nil, e
		}
		if e = source.Decode(raw, &r.Row); e != nil {
			rows.Close()
			return nil, e
		}
		batch = append(batch, r)
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return nil, e
	}
	return batch, nil
}
