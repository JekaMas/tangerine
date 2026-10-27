package app

import (
	"context"
	"encoding/json"
	"fmt"
	"path"
	"sort"
	"strconv"
	"strings"
	"tangerine.local/api/internal/source"
)

func (s *Storage) sourceSummary(ctx context.Context, run *SourceRun) error {
	var observed, accepted, quarantine, rawOnly, staged int64
	e := s.DB.QueryRow(ctx, "SELECT count(*),count(*) FILTER(WHERE state IN ('mapped','metadata','unmapped')),count(*) FILTER(WHERE state='quarantined'),count(*) FILTER(WHERE state='unmapped'),count(*) FILTER(WHERE state='staged') FROM source_row WHERE import_id=$1", run.Report.ID).Scan(&observed, &accepted, &quarantine, &rawOnly, &staged)
	if e != nil {
		return e
	}
	run.Report.Observed = sourceNumber(observed)
	run.Report.Accepted = sourceNumber(accepted)
	run.Report.Quarantined = sourceNumber(quarantine + staged)
	run.Report.Rejected = "0"
	run.Report.RawOnly = sourceNumber(rawOnly)
	members, e := s.sourceMembers(ctx, run.Report.Release)
	if e != nil {
		return e
	}
	counts := map[string]int64{}
	for _, m := range members {
		counts[m.Component]++
	}
	run.Report.Components = []SourceComponentCount{}
	for _, name := range sourceKeys(counts) {
		run.Report.Components = append(run.Report.Components, SourceComponentCount{name, nil, sourceNumber(counts[name]), true})
	}
	complete := true
	for _, component := range run.Frozen.Release.Components {
		var n int64
		for _, member := range members {
			matches := false
			for _, glob := range component.Globs {
				m, e := path.Match(glob, member.Path)
				if e != nil {
					return e
				}
				matches = matches || m
			}
			if matches {
				n++
			}
		}
		matches := n > 0
		if component.Expected != nil {
			expected, e := strconv.ParseInt(*component.Expected, 10, 64)
			if e != nil {
				return e
			}
			matches = expected == n || n > 0 && component.Reason != ""
		}
		run.Report.Components = append(run.Report.Components, SourceComponentCount{component.Name, component.Expected, sourceNumber(n), matches})
		complete = complete && matches
	}
	run.Report.Issues = []source.Issue{}
	countsComplete, e := s.sourceExpectedCounts(ctx, run, members)
	if e != nil {
		return e
	}
	complete = complete && countsComplete
	// Recovered foreground failures remain in issue/event history. They are
	// not outstanding record problems after successful completion. Current count
	// findings were freshly projected above; historical count snapshots remain in
	// issue/event history instead of resurfacing after their population recovers.
	rows, e := s.DB.Query(ctx, "SELECT locator,code,detail FROM source_issue WHERE import_id=$1 AND ($2 OR code<>'import_failed') AND code NOT IN ('count_mismatch','count_unbound') ORDER BY locator,code LIMIT 1000", run.Report.ID, run.Report.State == "failed")
	if e != nil {
		return e
	}
	for rows.Next() {
		var i source.Issue
		if e = rows.Scan(&i.Locator, &i.Code, &i.Detail); e != nil {
			rows.Close()
			return e
		}
		run.Report.Issues = append(run.Report.Issues, i)
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return e
	}
	var parseFailures int64
	if e = s.DB.QueryRow(ctx, "SELECT count(*) FROM source_issue WHERE import_id=$1 AND code IN ('parse_failed','mapping_failed')", run.Report.ID).Scan(&parseFailures); e != nil {
		return e
	}
	bound := run.Frozen.Program != nil || run.Frozen.Native || run.Frozen.Binding != nil
	run.Report.Normalized = bound && complete && rawOnly == 0 && quarantine == 0 && staged == 0 && parseFailures == 0 && observed > 0 && len(source.MissingNative(run.Frozen.Release.Source, members)) == 0
	run.Report.FullMissing, e = s.sourceFullMissing(ctx, run.Frozen.Release, run.Report.ID, members)
	if e != nil {
		return e
	}
	for _, component := range run.Report.Components {
		if !component.Complete {
			run.Report.FullMissing = append(run.Report.FullMissing, "Unreconciled component: "+component.Component)
		}
	}
	// Original full-source acceptance is kept separate from all raw supplied files
	// having actual complete accepted assets. Save this assessment once here;
	// ordinary Sources reads trust the report instead of recounting saved rows.
	return nil
}
func sourceKeys(m map[string]int64) []string {
	a := []string{}
	for k := range m {
		a = append(a, k)
	}
	sortStrings(a)
	return a
}
func sortStrings(a []string) { sort.Strings(a) }
func (s *Storage) SourceRows(ctx context.Context, id, cursor string, limit int) ([]map[string]any, string, error) {
	if limit < 1 || limit > 200 {
		limit = 50
	}
	members, table, ordinal := "", "", int64(-1)
	if cursor != "" {
		var c []any
		if e := source.Decode([]byte(cursor), &c); e != nil || len(c) != 3 {
			return nil, "", ErrInput
		}
		var ok bool
		members, ok = c[0].(string)
		if !ok {
			return nil, "", ErrInput
		}
		table, ok = c[1].(string)
		if !ok {
			return nil, "", ErrInput
		}
		n, ok := c[2].(json.Number)
		if !ok {
			return nil, "", ErrInput
		}
		var e error
		ordinal, e = n.Int64()
		if e != nil {
			return nil, "", ErrInput
		}
	}
	rows, e := s.DB.Query(ctx, "SELECT member,table_name,ordinal,raw_record,corpus_record,projection,state,issues,transformation FROM source_row WHERE import_id=$1 AND (member,table_name,ordinal)>($2,$3,$4) ORDER BY member,table_name,ordinal LIMIT $5", id, members, table, ordinal, limit+1)
	if e != nil {
		return nil, "", e
	}
	defer rows.Close()
	out := []map[string]any{}
	next := ""
	for rows.Next() {
		var m, t, state string
		var n int64
		var raw, corpus, projection, issues, transformation []byte
		if e = rows.Scan(&m, &t, &n, &raw, &corpus, &projection, &state, &issues, &transformation); e != nil {
			return nil, "", e
		}
		if len(out) == limit {
			next = sourceCursor(members, table, ordinal)
			break
		}
		var rr, cc, pp, ii, tt any
		for _, v := range []struct {
			b []byte
			p *any
		}{{raw, &rr}, {corpus, &cc}, {projection, &pp}, {issues, &ii}, {transformation, &tt}} {
			if len(v.b) > 0 {
				if e = source.Decode(v.b, v.p); e != nil {
					return nil, "", e
				}
			}
		}
		out = append(out, map[string]any{"member": m, "table": t, "ordinal": n, "raw_record": rr, "corpus_record": cc, "projection": pp, "state": state, "issues": ii, "transformation": tt})
		members, table, ordinal = m, t, n
	}
	return out, next, rows.Err()
}
func (s *Storage) SourceIssues(ctx context.Context, id, cursor string) ([]source.Issue, string, error) {
	locator, code := "", ""
	if cursor != "" {
		var value []string
		if source.Decode([]byte(cursor), &value) != nil || len(value) != 2 {
			return nil, "", ErrInput
		}
		locator, code = value[0], value[1]
	}
	rows, e := s.DB.Query(ctx, "SELECT locator,code,detail FROM source_issue WHERE import_id=$1 AND (locator,code)>($2,$3) ORDER BY locator,code LIMIT 1001", id, locator, code)
	if e != nil {
		return nil, "", e
	}
	defer rows.Close()
	out := []source.Issue{}
	next := ""
	for rows.Next() {
		var i source.Issue
		if e = rows.Scan(&i.Locator, &i.Code, &i.Detail); e != nil {
			return nil, "", e
		}
		if len(out) == 1000 {
			prev := out[len(out)-1]
			next = string(sourceBytes([]string{prev.Locator, prev.Code}))
			break
		}
		out = append(out, i)
	}
	return out, next, rows.Err()
}
func issueDetail(e error) string { return strings.TrimSpace(fmt.Sprint(e)) }
