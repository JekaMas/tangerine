package app

import (
	"context"
	"github.com/jackc/pgx/v5"
	"path"
	"tangerine.local/api/internal/source"
)

func (s *Storage) stageSource(ctx context.Context, run *SourceRun, members []source.Member) error {
	for _, member := range members {
		if run.Member != "" && member.Path <= run.Member {
			continue
		}
		if e := ctx.Err(); e != nil {
			return e
		}
		plans := []source.TableSpec{}
		if p := run.Frozen.Program; p != nil {
			for _, t := range p.Tables {
				matches, e := path.Match(t.Glob, member.Path)
				if e != nil {
					return e
				}
				if matches {
					plans = append(plans, t)
				}
			}
		} else {
			o, name, ok := source.NativePlan(run.Frozen.Release.Source, member)
			if ok {
				if run.Frozen.Binding != nil && !run.Frozen.Native {
					selector, _ := run.Frozen.Binding["record_selector"].(string)
					o.Selector = selector
				}
				plans = append(plans, source.TableSpec{Name: name, Options: o})
			}
		}
		for _, plan := range plans {
			r, e := s.sourceFileReader(ctx, run.Report.Release, member.Path)
			if e != nil {
				return e
			}
			counters := map[string]int64{}
			batch := []stagedSourceRow{}
			var writeErr error
			flush := func() error {
				if len(batch) == 0 {
					return nil
				}
				if e := s.writeSourceRows(ctx, *run, batch); e != nil {
					writeErr = e
					return e
				}
				batch = nil
				return nil
			}
			e = source.Walk(ctx, member.Path, r, plan.Options, func(table string, row source.Row) error {
				if run.Frozen.Program != nil {
					if plan.Selector != "records" && plan.Selector != "keyed_records" && plan.Selector != "" && plan.Selector != table {
						return nil
					}
					table = plan.Name
				} else if plan.Name == "essays" || plan.Name == "transcripts" || plan.Name == "withheld" || plan.Name == "scores.json" || plan.Name == "scores-detail.json" || plan.Name == "writings" {
					table = plan.Name
				}
				ordinal := counters[table]
				counters[table]++
				// Existing admitted rows are reused under their unique source locator. They
				// are never hashed/schema-checked again on explicit interruption recovery.
				batch = append(batch, stagedSourceRow{member.Path, table, ordinal, row})
				if len(batch) >= 128 {
					return flush()
				}
				return nil
			})
			closeErr := r.Close()
			if writeErr != nil {
				return writeErr
			}
			if e == nil {
				e = closeErr
			}
			if e != nil {
				if ctx.Err() != nil {
					return ctx.Err()
				}
				if ie := s.sourceIssue(ctx, *run, source.Issue{Locator: member.Path, Code: "parse_failed", Detail: e.Error()}); ie != nil {
					return ie
				}
			}
			if e = flush(); e != nil {
				return e
			}
		}
		run.Member = member.Path
		run.Row = -1
		if e := s.checkpointSource(ctx, run, false); e != nil {
			return e
		}
	}
	return nil
}

type stagedSourceRow struct {
	Member, Table string
	Ordinal       int64
	Row           source.Row
}

func (s *Storage) writeSourceRows(ctx context.Context, run SourceRun, batch []stagedSourceRow) error {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	if e = sourceOwned(ctx, tx, run); e != nil {
		return e
	}
	b := &pgx.Batch{}
	for _, r := range batch {
		var key any
		if k, ok := r.Row["key"].(string); ok {
			key = k
		}
		b.Queue("INSERT INTO source_row(import_id,member,table_name,ordinal,join_key,native_row) VALUES($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING", run.Report.ID, r.Member, r.Table, r.Ordinal, key, sourceBytes(r.Row))
	}
	results := tx.SendBatch(ctx, b)
	for range batch {
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
