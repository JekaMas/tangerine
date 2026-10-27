package app

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"strconv"
	"strings"
	"tangerine.local/api/internal/empirical"
	"tangerine.local/api/internal/source"
)

type EmpiricalSubmission struct {
	ReuseInput    string                  `json:"reuse_input_asset_id,omitempty"`
	Title         string                  `json:"title"`
	Input         empirical.Input         `json:"input"`
	Attempts      []empirical.Attempt     `json:"attempts"`
	Source        *EmpiricalSource        `json:"source"`
	SourceSummary *EmpiricalSourceSummary `json:"source_summary,omitempty"`
}
type EmpiricalSource struct {
	Basis           string            `json:"basis,omitempty"`
	AnnotatedLeaves []string          `json:"annotated_leaf_ids"`
	WindowPointer   string            `json:"window_pointer"`
	Import          string            `json:"import_id"`
	Member          string            `json:"member"`
	Table           string            `json:"table"`
	Annotator       string            `json:"annotator"`
	LeafByEvent     map[string]string `json:"leaf_by_event"`
}

func (s *Storage) CreateEmpiricalReport(ctx context.Context, r EmpiricalSubmission) (map[string]any, error) {
	if r.Title == "" {
		return nil, ErrInput
	}
	var summary *EmpiricalSourceSummary
	if r.ReuseInput != "" {
		title, asset := r.Title, r.ReuseInput
		raw, e := s.ReadAsset(ctx, asset)
		if e != nil {
			return nil, e
		}
		var saved EmpiricalSubmission
		if e = json.Unmarshal(raw, &saved); e != nil {
			return nil, e
		}
		r = saved
		r.Title, r.ReuseInput, summary = title, asset, saved.SourceSummary
	} else if r.Source != nil && r.Source.Basis != "" {
		in, selected, e := s.empiricalImportedSource(ctx, *r.Source)
		if e != nil {
			return nil, e
		}
		r.Input, summary = in, &selected
	} else if r.Source != nil {
		in, e := s.empiricalSource(ctx, r.Input.Population, *r.Source)
		if e != nil {
			return nil, e
		}
		r.Input = in
	}
	// Taxonomy IDs are resolved from the shipped registry helper, never generated.
	if r.Input.AnnotatedLeaves == nil {
		r.Input.AnnotatedLeaves = append([]string{}, r.Input.Leaves...)
	}
	r.Input.Leaves = taxonomyLeafIDs()
	report, e := empirical.Build(r.Input)
	if e != nil {
		return nil, fmt.Errorf("%w: %v", ErrInput, e)
	}
	difficulty, e := empirical.DifficultyReport(r.Attempts)
	if e != nil {
		return nil, fmt.Errorf("%w: %v", ErrInput, e)
	}
	r.SourceSummary = summary
	input, e := s.saveProviderBytes(ctx, sourceBytes(r), "provider_input")
	if e != nil {
		return nil, e
	}
	id := uuid.NewString()
	out := map[string]any{"id": id, "title": r.Title, "source_input_asset_id": input.ID, "report": report, "difficulty": difficulty, "origin": "descriptive_selected_population", "effectiveness_claim": "paired change is descriptive; no causal claim"}
	labels := map[string]string{}
	categories, _, e := preparationCategories()
	if e != nil {
		return nil, e
	}
	for _, category := range categories {
		labels[category.ID] = category.Label
	}
	out["category_labels"] = labels
	if summary != nil {
		out["source_summary"] = summary
	}
	asset, e := s.saveProviderBytes(ctx, sourceBytes(out), "export")
	if e != nil {
		return nil, e
	}
	_, e = s.DB.Exec(ctx, "INSERT INTO empirical_report(id,asset_id,input_asset_id,title) VALUES($1,$2,$3,$4)", id, asset.ID, input.ID, r.Title)
	return out, e
}
func taxonomyLeafIDs() []string {
	raw, _ := generationRegistry("mutation-recipes.v1.json")
	var r map[string]any
	_ = json.Unmarshal(raw, &r)
	out := []string{}
	if rows, ok := r["recipes"].([]any); ok {
		for _, x := range rows {
			m := x.(map[string]any)
			id, _ := m["taxonomy_id"].(string)
			if id == "" {
				id, _ = m["category_id"].(string)
			}
			if id != "" {
				out = append(out, id)
			}
		}
	}
	return out
}
func (s *Storage) empiricalSource(ctx context.Context, p empirical.Population, selects EmpiricalSource) (empirical.Input, error) {
	run, e := s.SourceImport(ctx, selects.Import)
	if e != nil {
		return empirical.Input{}, e
	}
	var release string
	if e = s.DB.QueryRow(ctx, "SELECT release_id FROM source_import WHERE id=$1", selects.Import).Scan(&release); e != nil {
		return empirical.Input{}, e
	}
	p.Release = release
	found := false
	for _, file := range run.Frozen.Release.Files {
		if file.Path == selects.Member {
			found = true
			p.Split = "unknown"
			if file.Partition != nil {
				p.Split = *file.Partition
			}
		}
	}
	if !found {
		return empirical.Input{}, ErrInput
	}

	if selects.Member == "" || (selects.Table != "sentences" && selects.WindowPointer == "") {
		return empirical.Input{}, fmt.Errorf("%w: select one native sentence view/member or supply explicit localized windows", ErrInput)
	}
	p.View = selects.Member
	p.Annotator = selects.Annotator
	if p.Annotator == "" {
		p.Annotator = "lowest_integer_per_sentence"
	}
	if len(selects.LeafByEvent) > 0 {
		if p.Crosswalk == "" {
			return empirical.Input{}, ErrInput
		}
		p.Origin = "operator_localized_mapping"
	}
	if selects.WindowPointer == "" {
		p.Window = "sentence"
	} else if p.Window == "" {
		p.Window = "declared_source_window"
	}
	if p.Origin == "" {
		p.Origin = "native"
	}
	rows, e := s.DB.Query(ctx, "SELECT ordinal,native_row,projection FROM source_row WHERE import_id=$1 AND member=$2 AND table_name=$3 ORDER BY ordinal", selects.Import, selects.Member, selects.Table)
	if e != nil {
		return empirical.Input{}, e
	}
	defer rows.Close()
	out := empirical.Input{AnnotatedLeaves: append([]string{}, selects.AnnotatedLeaves...), Population: p, Leaves: taxonomyLeafIDs(), Windows: []empirical.Window{}, Decisions: []empirical.Decision{}}
	for rows.Next() {
		var n int64
		var raw, projection []byte
		if e = rows.Scan(&n, &raw, &projection); e != nil {
			return out, e
		}
		var row map[string]any
		if e = json.Unmarshal(raw, &row); e != nil {
			return out, e
		}
		id := fmt.Sprintf("%s/%s/%d", selects.Import, selects.Member, n)
		w := empirical.Window{ID: id, Events: []empirical.Event{}, Opportunities: map[string]int64{}}
		if selects.WindowPointer != "" {
			var projected any
			if len(projection) > 0 {
				_ = json.Unmarshal(projection, &projected)
			}
			value, ok := source.Pointer(projected, selects.WindowPointer)
			if !ok || value == nil {
				w.Events = []empirical.Event{{ID: id + "/projection-absent", Excluded: "empirical_window_projection_absent"}}
			} else {
				if err := json.Unmarshal(sourceBytes(value), &w); err != nil {
					return out, ErrInput
				}
				if w.ID == "" {
					w.ID = id
				}
				for i := range w.Events {
					if w.Events[i].ID == "" {
						w.Events[i].ID = fmt.Sprintf("%s/%d", id, i)
					}
				}
			}
			out.Windows = append(out.Windows, w)
			continue
		}

		w.Annotated = row["labels_state"] == "labels_supplied" && row["invalid"] != true
		if tokens, ok := row["tokens"].([]any); ok {
			v := int64(len(tokens))
			w.Tokens = &v
		}
		hasAnnotator := false
		edits, _ := row["edits"].([]any)
		selectedAnnotator := selects.Annotator
		if selectedAnnotator == "" {
			lowest := int64(0)
			found := false
			for _, x := range edits {
				v := fmt.Sprint(x.(map[string]any)["annotator"])
				n, err := strconv.ParseInt(v, 10, 64)
				if err == nil && (!found || n < lowest) {
					lowest = n
					selectedAnnotator = v
					found = true
				}
			}
		}
		for j, x := range edits {
			m := x.(map[string]any)
			if fmt.Sprint(m["annotator"]) != selectedAnnotator {
				continue
			}
			hasAnnotator = true
			event := empirical.Event{ID: fmt.Sprintf("%s/%d", id, j), Native: fmt.Sprint(m["label"]), Secondary: []string{}}
			if m["noop"] == true {
				event.Excluded = "noop"
			}
			if m["invalid"] == true {
				event.Excluded = "invalid"
			}
			if event.Native == "UNK" || event.Native == "Um" {
				event.Excluded = "unresolved_native_label"
			}
			if leaf, ok := selects.LeafByEvent[event.ID]; ok {
				event.Leaf = &leaf
			}
			if selects.Basis == "m2" && event.Excluded == "" {
				before := ""
				if tokens, ok := row["tokens"].([]any); ok {
					start, sok := m["start"].(float64)
					end, eok := m["end"].(float64)
					if sok && eok && start >= 0 && end >= start && end <= float64(len(tokens)) {
						parts := []string{}
						for _, token := range tokens[int(start):int(end)] {
							parts = append(parts, fmt.Sprint(token))
						}
						before = strings.Join(parts, " ")
					}
				}
				leaf, rule := empirical.WritingMapping(event.Native, before, fmt.Sprint(m["correction"]))
				event.Rule = rule
				if leaf != "" {
					event.Leaf = &leaf
				}
			}
			w.Events = append(w.Events, event)
		}
		w.Annotated = w.Annotated && hasAnnotator
		out.Windows = append(out.Windows, w)
	}
	return out, rows.Err()
}
func (s *Storage) EmpiricalReport(ctx context.Context, id string) (json.RawMessage, error) {
	var asset string
	e := s.DB.QueryRow(ctx, "SELECT asset_id FROM empirical_report WHERE id=$1", id).Scan(&asset)
	if e != nil {
		return nil, e
	}
	raw, e := s.ReadAsset(ctx, asset)
	return raw, e
}
func (s *Storage) EmpiricalReports(ctx context.Context) ([]map[string]any, error) {
	rows, e := s.DB.Query(ctx, "SELECT id,title,created_at FROM empirical_report ORDER BY created_at DESC,id")
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	out := []map[string]any{}
	for rows.Next() {
		var id, title string
		var at any
		if e = rows.Scan(&id, &title, &at); e != nil {
			return nil, e
		}
		out = append(out, map[string]any{"id": id, "title": title, "created_at": at})
	}
	return out, rows.Err()
}
