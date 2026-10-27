package app

import (
	"context"
	"fmt"
	"strconv"
	"tangerine.local/api/internal/source"
)

func (s *Storage) projectSource(ctx context.Context, run *SourceRun, members []source.Member) error {
	byName := map[string]source.Member{}
	for _, m := range members {
		byName[m.Path] = m
	}
	if e := s.sourceSummary(ctx, run); e != nil {
		return e
	}
	licence, e := s.sourceLicence(ctx, run.Frozen.Release, run.Frozen.Permissions)
	if e != nil {
		return e
	}
	speakers, e := s.sourceL2Speakers(ctx, *run)
	if e != nil {
		return e
	}
	cursor := stagedSourceRow{Ordinal: -1}
	for {
		batch, e := s.sourceProjectionBatch(ctx, run.Report.ID, cursor)
		if e != nil {
			return e
		}
		if len(batch) == 0 {
			return nil
		}
		writes := []sourceProjectionWrite{}
		for _, r := range batch {
			if e = ctx.Err(); e != nil {
				return e
			}
			m := source.BaseProjection(run.Frozen.Release.Source, run.Report.Release, r.Member, r.Table, int(r.Ordinal), r.Row)
			switch {
			case run.Frozen.Program != nil:
				p := run.Frozen.Program
				if r.Table != p.Record {
					m.Status = "metadata"
					break
				}
				tables, e := s.sourceJoinedTables(ctx, run.Report.ID, *p, r.Row)
				if e != nil {
					return e
				}
				mapped, e := source.Project(*p, tables)
				if e != nil {
					m.Issues = append(m.Issues, source.Issue{Locator: r.Member, Code: "mapping_failed", Detail: e.Error()})
				} else if len(mapped) == 1 {
					m = mapped[0]
					m.Ordinal = int(r.Ordinal)
					m.ID = source.StableID(p.Source, p.Release, r.Member, r.Table, fmt.Sprint(m.Identity), strconv.FormatInt(r.Ordinal, 10))
				}
			case run.Frozen.Native:
				m = source.NativeRecord(run.Frozen.Release.Source, run.Report.Release, r.Member, r.Table, int(r.Ordinal), r.Row)
				if m.Status == "unmapped" && nativeMetadata(run.Frozen.Release.Source, r.Table) {
					m.Status = "metadata"
				}
				if e = s.enrichNative(ctx, *run, &m, byName); e != nil {
					return e
				}
				if run.Frozen.Release.Source == "L2-ARCTIC" {
					sourceL2SpeakerProjection(&m, speakers, byName)
				}
			case run.Frozen.Binding != nil:
				m = source.LegacyRecord(run.Frozen.Release.Source, run.Report.Release, r.Member, r.Table, int(r.Ordinal), r.Row, run.Frozen.Binding)
			}
			write, err := prepareSourceProjection(*run, byName[r.Member], m, licence)
			if err != nil {
				return err
			}
			writes = append(writes, write)
		}
		if e = s.saveSourceProjections(ctx, *run, writes); e != nil {
			return e
		}
		for _, write := range writes {
			sourceAdvanceCounts(&run.Report, write.mapped.Status)
		}
		if e = s.checkpointSource(ctx, run, false); e != nil {
			return e
		}
		cursor = batch[len(batch)-1]
	}
}
func nativeMetadata(id, table string) bool {
	switch id {
	case "SPEECHOCEAN762":
		return true
	case "WILOCNESS-2.1", "FCE-2.1":
		return table == "edits"
	case "L2-ARCTIC":
		return table == "intervals" || table == "points" || table == "speakers"
	}
	return false
}

// Progress follows admitted writes in memory. This avoids a complete source-row
// recount after every64records. Reopen/failure/finish reports can query the saved
// rows once; accepted content is never revalidated.
func sourceAdvanceCounts(r *SourceReport, state string) {
	inc := func(s string, n int64) string { v, _ := strconv.ParseInt(s, 10, 64); return strconv.FormatInt(v+n, 10) }
	r.Quarantined = inc(r.Quarantined, -1)
	switch state {
	case "mapped", "metadata":
		r.Accepted = inc(r.Accepted, 1)
	case "unmapped":
		r.Accepted = inc(r.Accepted, 1)
		r.RawOnly = inc(r.RawOnly, 1)
	default:
		r.Quarantined = inc(r.Quarantined, 1)
	}
}
