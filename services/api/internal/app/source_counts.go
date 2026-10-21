package app

import (
	"context"
	"fmt"
	"math/big"
	"strings"
	"tangerine.local/api/internal/source"
)

// Reconcile only named native counting units. Unknown counts stay unbound; rows,
// files, rating events and unique populations are never silently interchanged.
func (s *Storage) sourceExpectedCounts(ctx context.Context, run *SourceRun, members []source.Member) (bool, error) {
	complete := true
	for _, expected := range run.Frozen.Release.Expected {
		var n int64
		known := true
		selected := []string{}
		for _, m := range members {
			if expected.Partition == nil || m.Partition != nil && *m.Partition == *expected.Partition {
				selected = append(selected, m.Path)
			}
		}
		unit := expected.Unit
		switch {
		case unit == "files":
			n = int64(len(selected))
		case strings.HasPrefix(unit, "component:"):
			for _, m := range members {
				if m.Component == strings.TrimPrefix(unit, "component:") && (expected.Partition == nil || m.Partition != nil && *m.Partition == *expected.Partition) {
					n++
				}
			}
		default:
			tables := []string{}
			switch unit {
			case "records":
				tables = nil
			case "sentences":
				tables = []string{"sentences", "withheld"}
			case "writings":
				tables = []string{"writings", "essays"}
			case "utterances":
				if run.Frozen.Release.Source == "SPEECHOCEAN762" {
					tables = []string{"scores.json"}
				} else if run.Frozen.Release.Source == "L2-ARCTIC" {
					tables = []string{"transcripts"}
				} else {
					known = false
				}
			default:
				if strings.HasPrefix(unit, "table:") {
					tables = []string{strings.TrimPrefix(unit, "table:")}
				} else {
					known = false
				}
			}
			if known {
				if e := s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND member=ANY($2) AND ($3::text[] IS NULL OR table_name=ANY($3))", run.Report.ID, selected, tables).Scan(&n); e != nil {
					return false, e
				}
			}
		}
		matches := known
		if expected.Value != nil {
			want, ok := new(big.Int).SetString(*expected.Value, 10)
			matches = known && ok && want.Cmp(big.NewInt(n)) == 0
		}
		name := unit
		if expected.Partition != nil {
			name += "-" + *expected.Partition
		}
		run.Report.Components = append(run.Report.Components, SourceComponentCount{name, expected.Value, sourceNumber(n), matches})
		if !matches {
			complete = false
			code := "count_mismatch"
			detail := fmt.Sprintf("%s expected %v; actual %d in its stated native counting unit", name, expected.Value, n)
			if !known {
				code = "count_unbound"
				detail = "Native counting unit has no supplied deterministic binding: " + unit
			}
			if e := s.sourceIssue(ctx, *run, source.Issue{Locator: run.Report.Release + ":" + name, Code: code, Detail: detail}); e != nil {
				return false, e
			}
		}
	}
	return complete, nil
}
