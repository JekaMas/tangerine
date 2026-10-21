package app

import (
	"context"
	"fmt"
	"github.com/jackc/pgx/v5"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
)

func (s *Storage) sourceJoinedTables(ctx context.Context, id string, p source.Program, record source.Row) (map[string][]source.Row, error) {
	tables := map[string][]source.Row{p.Record: {record}}
	pending := append([]source.Join(nil), p.Joins...)
	for len(pending) > 0 {
		next := []source.Join{}
		changed := false
		for _, join := range pending {
			left, ok := tables[join.Left]
			if !ok {
				next = append(next, join)
				continue
			}
			changed = true
			right := []source.Row{}
			for _, row := range left {
				v, ok := source.Pointer(row, join.LeftPointer)
				if !ok || v == nil {
					continue
				}
				tokens := pointerTokens(join.RightPointer)
				rows, e := s.DB.Query(ctx, "SELECT native_row FROM source_row WHERE import_id=$1 AND table_name=$2 AND native_row #> $3::text[] = $4::jsonb ORDER BY member,ordinal", id, join.Right, tokens, sourceBytes(v))
				if e != nil {
					return nil, e
				}
				for rows.Next() {
					var raw []byte
					if e = rows.Scan(&raw); e != nil {
						rows.Close()
						return nil, e
					}
					var r source.Row
					if e = source.Decode(raw, &r); e != nil {
						rows.Close()
						return nil, e
					}
					right = append(right, r)
				}
				rows.Close()
				if e = rows.Err(); e != nil {
					return nil, e
				}
			}
			tables[join.Right] = right
		}
		if !changed {
			return nil, fmt.Errorf("unconnected source joins")
		}
		pending = next
	}
	return tables, nil
}
func pointerTokens(p string) []string {
	tokens := strings.Split(strings.TrimPrefix(p, "/"), "/")
	for i, t := range tokens {
		tokens[i] = strings.ReplaceAll(strings.ReplaceAll(t, "~1", "/"), "~0", "~")
	}
	return tokens
}

type sourceProjectionWrite struct {
	mapped         source.Mapped
	raw            []byte
	corpus         any
	transformation map[string]any
}

func prepareSourceProjection(run SourceRun, member source.Member, m source.Mapped, licence map[string]any) (sourceProjectionWrite, error) {
	var native any
	if e := source.Decode(sourceBytes(m.Raw), &native); e != nil {
		return sourceProjectionWrite{}, e
	}
	raw := map[string]any{"schema_version": "2.0.0", "id": m.ID, "release_id": run.Report.Release, "file_sha256": member.SHA, "locator": sourceCursor(m.Member, m.Table, int64(m.Ordinal)), "value": source.RawValue(native), "raw_byte_asset_id": member.AssetID, "interpretation_status": "unmapped", "mapping_profile_id": nil}
	if run.Binding != "" && run.Binding != "native" && run.Binding != "raw-only" {
		raw["mapping_profile_id"] = run.Binding
	}
	if m.Status == "mapped" || m.Status == "metadata" {
		raw["interpretation_status"] = "mapped"
	} else if m.Status == "quarantined" {
		raw["interpretation_status"] = "quarantined"
	}
	_, rawBytes, e := contracts.Validate("raw-record", "2.0.0", sourceBytes(raw))
	if e != nil {
		return sourceProjectionWrite{}, e
	}
	if gold, ok := source.Pointer(m.Value, "/raw_metadata/gold"); ok {
		if _, e := sourceGoldAdmission(gold); e != nil {
			m.Status = "unmapped"
			m.Issues = append(m.Issues, source.Issue{Locator: m.Member, Code: "gold_unbound", Detail: e.Error()})
			raw["interpretation_status"] = "unmapped"
			rawBytes = sourceBytes(raw)
		}
	}
	if candidate, ok := m.Value["case_candidate"]; ok {
		if _, _, e := contracts.Validate("case-candidate", "1.0.0", sourceBytes(candidate)); e != nil {
			m.Status = "unmapped"
			m.Issues = append(m.Issues, source.Issue{Locator: m.Member, Code: "candidate_unbound", Detail: e.Error()})
			raw["interpretation_status"] = "unmapped"
			rawBytes = sourceBytes(raw)
		}
	}
	permissions := append([]string{}, run.Frozen.Permissions...)
	transformation := map[string]any{"schema_version": "2.0.0", "id": m.ID + "-parse", "operation": "parse", "method_id": run.Report.ParserVersion, "method_sha256": run.Frozen.MethodSHA, "input_asset_ids": []string{member.AssetID}, "input_sha256s": []string{member.SHA}, "output_asset_ids": []string{}, "output_sha256s": []string{}, "permission_grant_ids": permissions, "receipt_id": run.Operation, "created_at": sourceTime()}

	var corpus any
	if cp, ok := m.Value["corpus_record"].(map[string]any); ok && m.Status == "mapped" {
		corpus, e = sourceCorpus(run, m, member, cp, licence)
		if e != nil {
			m.Status = "unmapped"
			m.Issues = append(m.Issues, source.Issue{Locator: m.Member, Code: "corpus_projection", Detail: e.Error()})
			raw["interpretation_status"] = "unmapped"
			rawBytes = sourceBytes(raw)
		}
	}
	return sourceProjectionWrite{m, rawBytes, corpus, transformation}, nil
}

// One atomic write per mapped batch; accepted rows are never schema-checked on
// resume. A failed batch leaves its staged rows available for explicit retry.
func (s *Storage) saveSourceProjections(ctx context.Context, run SourceRun, writes []sourceProjectionWrite) error {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	if e = sourceOwned(ctx, tx, run); e != nil {
		return e
	}
	batch := &pgx.Batch{}
	for _, write := range writes {
		m := write.mapped
		batch.Queue("UPDATE source_row SET raw_record=$5,corpus_record=$6,projection=$7,state=$8,issues=$9,transformation=$10 WHERE import_id=$1 AND member=$2 AND table_name=$3 AND ordinal=$4 AND state='staged'", run.Report.ID, m.Member, m.Table, m.Ordinal, write.raw, nullableJSON(write.corpus), sourceBytes(m.Value), m.Status, sourceBytes(m.Issues), sourceBytes(write.transformation))
		for _, i := range m.Issues {
			batch.Queue("INSERT INTO source_issue(import_id,locator,code,detail) VALUES($1,$2,$3,$4) ON CONFLICT DO NOTHING", run.Report.ID, i.Locator, i.Code, i.Detail)
		}
	}
	results := tx.SendBatch(ctx, batch)
	for range batch.Len() {
		if _, e = results.Exec(); e != nil {
			_ = results.Close()
			return e
		}
	}
	if e = results.Close(); e != nil {
		return e
	}
	return tx.Commit(ctx)
}
