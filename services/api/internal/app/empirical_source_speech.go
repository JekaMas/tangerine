package app

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
	"tangerine.local/api/internal/empirical"
)

func (s *Storage) empiricalSourceSpeech(ctx context.Context, selected EmpiricalSource, p empirical.Population, summary EmpiricalSourceSummary) (empirical.Input, EmpiricalSourceSummary, error) {
	rows, err := s.DB.Query(ctx, "SELECT member,ordinal,projection FROM source_row WHERE import_id=$1 AND table_name='intervals' AND projection #>> '{raw_metadata,annotation_origin}'='source_manual' AND lower(native_row->>'tier')='phones' ORDER BY member,ordinal", selected.Import)
	if err != nil {
		return empirical.Input{}, summary, err
	}
	defer rows.Close()
	windows := map[string]*empirical.Window{}
	var intervals, controls, uncertain int64
	for rows.Next() {
		var member string
		var ordinal int64
		var projected []byte
		if err = rows.Scan(&member, &ordinal, &projected); err != nil {
			return empirical.Input{}, summary, err
		}
		if strings.Contains(strings.ToLower(member), "suitcase") != (selected.Basis == "manual_phones_suitcase") {
			continue
		}
		id := selected.Import + "/" + member
		if windows[id] == nil {
			windows[id] = &empirical.Window{ID: id, Annotated: true, Events: []empirical.Event{}, Opportunities: map[string]int64{}}
		}
		var projection struct {
			Raw map[string]any `json:"raw_metadata"`
		}
		if err = json.Unmarshal(projected, &projection); err != nil {
			return empirical.Input{}, summary, err
		}
		phone, _ := projection.Raw["phone_annotation"].(map[string]any)
		operation, _ := phone["operation"].(string)
		canonical, _ := phone["canonical"].(string)
		perceived, _ := phone["perceived"].(string)
		e := empirical.Event{ID: fmt.Sprintf("%s/%d", id, ordinal), Native: operation}
		intervals++
		switch operation {
		case "unchanged":
			controls++
			continue
		case "s", "d", "a":
			leaf, rule := empirical.PhoneMapping(canonical, perceived, operation, phone["approximate"] == true)
			e.Rule = rule
			if leaf != "" {
				e.Leaf = &leaf
			} else {
				uncertain++
			}
		default:
			e.Excluded = "unresolved_native_label"
			e.Native = "unresolved"
			uncertain++
		}
		windows[id].Events = append(windows[id].Events, e)
	}
	if err = rows.Err(); err != nil {
		return empirical.Input{}, summary, err
	}
	ids := make([]string, 0, len(windows))
	for id := range windows {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	ordered := make([]empirical.Window, 0, len(ids))
	for _, id := range ids {
		ordered = append(ordered, *windows[id])
	}
	summary.Coverage = []EmpiricalCoverageCount{{"Manual phone intervals", intervals}, {"Intervals without a marked phone change", controls}, {"Operations without a resolved category", uncertain}}
	var available int64
	if err = s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name='transcripts' AND (strpos(lower(member),'suitcase')>0)=$2", selected.Import, selected.Basis == "manual_phones_suitcase").Scan(&available); err != nil {
		return empirical.Input{}, summary, err
	}
	summary.Coverage = append(summary.Coverage, EmpiricalCoverageCount{"Available transcript utterances in this task", available}, EmpiricalCoverageCount{"Utterances with manual phone annotations", int64(len(ordered))})
	summary.Notes = append(summary.Notes, "Native phone operations describe source annotations, not an independent judgement of the sound. Words, silence, annotator comments and automatic alignments are not extra mistakes. No word-token exposure is supplied for these phone windows.")
	p.Annotator = "source manual phone annotation"
	return empirical.Input{Population: p, AnnotatedLeaves: []string{}, Leaves: taxonomyLeafIDs(), Windows: ordered, Decisions: []empirical.Decision{}}, summary, nil
}
