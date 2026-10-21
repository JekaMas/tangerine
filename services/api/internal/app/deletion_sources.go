package app

import (
	"context"
	"encoding/json"
	"github.com/jackc/pgx/v5"
)

type SourceErasure struct {
	Releases    []string `json:"releases"`
	Imports     []string `json:"imports"`
	Files       []string `json:"files"`
	AssetIDs    []string `json:"asset_ids"`
	Reports     []string `json:"reports"`
	Experiments []string `json:"experiments"`
}

func erasureStrings(ctx context.Context, tx pgx.Tx, query string, args ...any) ([]string, error) {
	rows, e := tx.Query(ctx, query, args...)
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	out := []string{}
	for rows.Next() {
		var id string
		if e = rows.Scan(&id); e != nil {
			return nil, e
		}
		out = append(out, id)
	}
	return out, rows.Err()
}
func sourceErasure(ctx context.Context, tx pgx.Tx, ids []string) (SourceErasure, error) {
	p := SourceErasure{}
	var e error
	p.Releases, e = erasureStrings(ctx, tx, "SELECT id FROM source_release WHERE id=ANY($1) ORDER BY id", ids)
	if e != nil {
		return p, e
	}
	p.Imports, e = erasureStrings(ctx, tx, "SELECT id FROM source_import WHERE release_id=ANY($1) OR id=ANY($2) ORDER BY id", p.Releases, ids)
	if e != nil {
		return p, e
	}
	p.Files, e = erasureStrings(ctx, tx, `SELECT DISTINCT file_id FROM source_member m WHERE release_id=ANY($1) AND NOT EXISTS(SELECT 1 FROM source_member other WHERE other.file_id=m.file_id AND NOT(other.release_id=ANY($1))) ORDER BY file_id`, p.Releases)
	if e != nil {
		return p, e
	}
	p.AssetIDs, e = erasureStrings(ctx, tx, "SELECT asset_id FROM source_file WHERE id=ANY($1) ORDER BY asset_id", p.Files)
	if e != nil {
		return p, e
	}
	p.Reports, e = erasureStrings(ctx, tx, "SELECT id FROM empirical_report WHERE id=ANY($1) ORDER BY id", ids)
	if e != nil {
		return p, e
	}
	reportAssets, e := erasureStrings(ctx, tx, "SELECT asset_id FROM empirical_report WHERE id=ANY($1) UNION SELECT input_asset_id FROM empirical_report WHERE id=ANY($1)", p.Reports)
	if e != nil {
		return p, e
	}
	p.AssetIDs = append(p.AssetIDs, reportAssets...)
	p.Experiments, e = erasureStrings(ctx, tx, "SELECT id FROM quality_experiment WHERE id=ANY($1) ORDER BY id", ids)
	if e != nil {
		return p, e
	}
	rows, e := tx.Query(ctx, "SELECT frozen_asset_id,payload FROM quality_experiment WHERE id=ANY($1)", p.Experiments)
	if e != nil {
		return p, e
	}
	for rows.Next() {
		var id string
		var raw []byte
		if e = rows.Scan(&id, &raw); e != nil {
			rows.Close()
			return p, e
		}
		p.AssetIDs = append(p.AssetIDs, id)
		var exp QualityExperiment
		if e = json.Unmarshal(raw, &exp); e != nil {
			rows.Close()
			return p, e
		}
		if exp.Comparison != nil {
			p.AssetIDs = append(p.AssetIDs, *exp.Comparison)
		}
		for _, row := range exp.Rows {
			if row.Output != nil {
				p.AssetIDs = append(p.AssetIDs, *row.Output)
			}
		}
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return p, e
	}
	exports, e := erasureStrings(ctx, tx, "SELECT asset_id FROM quality_export WHERE experiment_id=ANY($1)", p.Experiments)
	if e != nil {
		return p, e
	}
	p.AssetIDs = append(p.AssetIDs, exports...)
	p.AssetIDs = sortedKeys(func() map[string]bool {
		m := map[string]bool{}
		for _, v := range p.AssetIDs {
			m[v] = true
		}
		return m
	}())
	return p, nil
}
func eraseSourceRows(ctx context.Context, tx pgx.Tx, p SourceErasure) error {
	queries := []struct {
		query string
		ids   []string
	}{
		{"DELETE FROM quality_export WHERE experiment_id=ANY($1)", p.Experiments}, {"DELETE FROM quality_experiment_event WHERE experiment_id=ANY($1)", p.Experiments}, {"DELETE FROM quality_experiment WHERE id=ANY($1)", p.Experiments}, {"DELETE FROM empirical_report WHERE id=ANY($1)", p.Reports},
		{"DELETE FROM source_action WHERE import_id=ANY($1)", p.Imports}, {"DELETE FROM source_issue WHERE import_id=ANY($1)", p.Imports}, {"DELETE FROM source_row WHERE import_id=ANY($1)", p.Imports}, {"DELETE FROM source_import_event WHERE import_id=ANY($1)", p.Imports}, {"DELETE FROM source_import WHERE id=ANY($1)", p.Imports}, {"DELETE FROM source_member WHERE release_id=ANY($1)", p.Releases}, {"DELETE FROM source_file WHERE id=ANY($1)", p.Files}, {"DELETE FROM source_release WHERE id=ANY($1)", p.Releases},
	}
	for _, q := range queries {
		if _, e := tx.Exec(ctx, q.query, q.ids); e != nil {
			return e
		}
	}
	return nil
}
