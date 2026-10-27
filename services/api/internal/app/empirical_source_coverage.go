package app

import (
	"context"
	"encoding/json"
	"fmt"
	"tangerine.local/api/internal/empirical"
)

// Coverage records which observations exist. Corrections, ratings, task labels,
// accents and ASR are never promoted into localized mistake annotations.
func (s *Storage) empiricalSourceCoverage(ctx context.Context, selected EmpiricalSource, p empirical.Population, summary EmpiricalSourceSummary) (empirical.Input, EmpiricalSourceSummary, error) {
	rows, err := s.DB.Query(ctx, "SELECT ordinal,projection FROM source_row WHERE import_id=$1 AND member=$2 AND table_name=$3 ORDER BY ordinal", selected.Import, selected.Member, selected.Table)
	if err != nil {
		return empirical.Input{}, summary, err
	}
	defer rows.Close()
	out := empirical.Input{Population: p, AnnotatedLeaves: []string{}, Leaves: taxonomyLeafIDs(), Windows: []empirical.Window{}, Decisions: []empirical.Decision{}}
	var references, examples int64
	for rows.Next() {
		var ordinal int64
		var raw []byte
		if err = rows.Scan(&ordinal, &raw); err != nil {
			return out, summary, err
		}
		out.Windows = append(out.Windows, empirical.Window{ID: fmt.Sprintf("%s/%s/%d", selected.Import, selected.Member, ordinal), Events: []empirical.Event{}, Opportunities: map[string]int64{}})
		var projection map[string]any
		if len(raw) > 0 {
			if err = json.Unmarshal(raw, &projection); err != nil {
				return out, summary, err
			}
		}
		if projection["source_example"] != nil {
			examples++
		}
		if correction, ok := projection["written_correction_example"].(map[string]any); ok {
			if refs, ok := correction["references"].([]any); ok {
				references += int64(len(refs))
			}
		}
	}
	if err = rows.Err(); err != nil {
		return out, summary, err
	}
	summary.Unit = "records"
	switch summary.Source {
	case "FCE-2.1", "WILOCNESS-2.1":
		summary.Unit = "unlabelled sentences"
	case "EDACC":
		summary.Unit = "conversation segments"
	case "ELRD":
		summary.Unit = "conversation turns"
	case "DIPLOMAT":
		summary.Unit = "dialogue task examples"
	case "DRAL":
		summary.Unit = "audio-fragment records"
		if selected.Table == "sp_dral_conversation" {
			summary.Unit = "conversation records"
		}
	}
	summary.Coverage = []EmpiricalCoverageCount{{"Source records", int64(len(out.Windows))}}
	if selected.Table == "jfleg_source" {
		summary.Unit = "original sentences"
		summary.Coverage = append(summary.Coverage, EmpiricalCoverageCount{"Supplied alternative corrections", references})
	}
	if examples > 0 {
		summary.Coverage = append(summary.Coverage, EmpiricalCoverageCount{"Linked context examples", examples})
	}
	if summary.Source == "SPEECHOCEAN762" {
		var recordings int64
		if err = s.DB.QueryRow(ctx, "SELECT count(*) FROM source_member WHERE release_id=$1 AND lower(relative_path) LIKE '%.wav'", p.Release).Scan(&recordings); err != nil {
			return out, summary, err
		}
		summary.Unit = "rated utterances"
		summary.Coverage = append(summary.Coverage, EmpiricalCoverageCount{"Original recordings in this release", recordings})
	}
	summary.Notes = append(summary.Notes, "This source view supplies examples or ratings, not localized error labels. Category frequencies, category relationships and correct-opportunity rates are not measured. Zero mapped mistakes is not evidence of error-free language.")
	return out, summary, nil
}
