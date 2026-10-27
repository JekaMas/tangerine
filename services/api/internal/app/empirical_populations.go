package app

import (
	"context"
	"encoding/json"
	"net/http"
	"path"
	"strings"
	"tangerine.local/api/internal/empirical"
	"time"
)

type EmpiricalPopulationChoice struct {
	Title       string          `json:"title"`
	Description string          `json:"description"`
	Source      EmpiricalSource `json:"source"`
	Release     string          `json:"release"`
	SourceName  string          `json:"source_name"`
	DataOrigin  string          `json:"data_origin"`
	ImportedAt  string          `json:"imported_at,omitempty"`
	ReleaseID   string          `json:"release_id"`
	Manifest    string          `json:"source_manifest"`
}
type EmpiricalCoverageCount struct {
	Label string `json:"label"`
	Count int64  `json:"count"`
}
type EmpiricalSourceSummary struct {
	Source      string                   `json:"source_id"`
	Name        string                   `json:"source_name"`
	Version     string                   `json:"source_version"`
	View        string                   `json:"view_label"`
	Unit        string                   `json:"unit"`
	Mapping     string                   `json:"mapping_version"`
	Notes       []string                 `json:"notes"`
	Coverage    []EmpiricalCoverageCount `json:"coverage"`
	Constructed bool                     `json:"constructed"`
	Manifest    string                   `json:"source_manifest"`
}

func empiricalSourceName(id string) string {
	switch id {
	case "FCE-2.1":
		return "Cambridge FCE writing"
	case "WILOCNESS-2.1":
		return "Write & Improve and LOCNESS writing"
	case "L2-ARCTIC":
		return "L2-ARCTIC learner speech"
	case "JFLEG":
		return "JFLEG writing corrections"
	case "SPEECHOCEAN762":
		return "SpeechOcean pronunciation ratings"
	case "EDACC":
		return "EdAcc accented conversation"
	case "ELRD":
		return "ELRD everyday conversation"
	case "DIPLOMAT":
		return "DiPlomat dialogue tasks"
	case "DRAL":
		return "DRAL bilingual dialogue"
	}
	return id
}
func empiricalViewName(member string) string {
	base := path.Base(member)
	if label := map[string]string{"train": "Training", "dev": "Development", "test": "Test", "val": "Validation"}[strings.TrimSuffix(base, path.Ext(base))]; label != "" {
		return label
	}
	parts := strings.Split(base, ".")
	if len(parts) >= 2 {
		label := map[string]string{"train": "Training", "dev": "Development", "test": "Test"}[parts[1]]
		if label != "" {
			if parts[0] != "fce" {
				label += " — group " + parts[0]
			}
			return label
		}
	}
	return strings.NewReplacer("_", " ", "-", " ").Replace(strings.TrimSuffix(path.Base(member), path.Ext(member)))
}

// One choice is one original view. Component and aggregate M2 files, dialogue
// task variants and DRAL release/fragment views are never pooled implicitly.
func (s *Storage) empiricalChoices(ctx context.Context, importID string, release SourceRelease) ([]EmpiricalPopulationChoice, error) {
	rows, err := s.DB.Query(ctx, "SELECT member,table_name FROM source_row WHERE import_id=$1 GROUP BY member,table_name ORDER BY member,table_name", importID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	out := []EmpiricalPopulationChoice{}
	add := func(basis, member, table, label, description string) {
		origin, name := "native", empiricalSourceName(release.Source)
		if empiricalConstructed(release) {
			origin = "constructed"
			name = "Constructed example · " + name
			description = "Constructed developer example, not an acquired corpus. " + description
		}
		out = append(out, EmpiricalPopulationChoice{Title: name + " · " + empiricalEdition(release) + " · " + label, SourceName: name, Release: release.Release, ReleaseID: release.ID, Manifest: release.Manifest, DataOrigin: origin, Description: description, Source: EmpiricalSource{Import: importID, Member: member, Table: table, Basis: basis}})
	}
	seen := map[string]bool{}
	for rows.Next() {
		var member, table string
		if err = rows.Scan(&member, &table); err != nil {
			return nil, err
		}
		switch release.Source {
		case "FCE-2.1", "WILOCNESS-2.1":
			if table == "sentences" && strings.HasSuffix(member, ".m2") {
				add("m2", member, table, empiricalViewName(member), "Original writing-error annotations. One annotator per sentence; overlapping views stay separate.")
			}
			if table == "withheld" {
				add("coverage", member, table, empiricalViewName(member)+" · unlabelled", "Original test sentences with no supplied error annotations. Frequencies remain unmeasured.")
			}
		case "L2-ARCTIC":
			if table == "intervals" && strings.Contains(strings.ToLower(member), "/annotation/") {
				basis, label := "manual_phones_read", "Read speech · manually annotated utterances"
				if strings.Contains(strings.ToLower(member), "suitcase") {
					basis, label = "manual_phones_suitcase", "Suitcase story · manually annotated utterances"
				}
				if !seen[basis] {
					seen[basis] = true
					add(basis, "", "intervals", label, "Source phone substitutions, deletions and additions. Selected manual utterances are not a random sample of all learner speech.")
				}
			}
		case "JFLEG":
			if table == "jfleg_source" {
				add("coverage", member, table, empiricalViewName(member), "Original sentences and alternative corrections. Alternatives are not counted as separate mistakes.")
			}
		case "SPEECHOCEAN762":
			if table == "scores.json" {
				add("coverage", member, table, "Rated utterances", "Native ratings and recording coverage. Ratings do not establish localized mistake counts.")
			}
		case "EDACC":
			if table == "sp_edacc_segments" {
				add("coverage", member, table, empiricalViewName(path.Dir(member)), "Reference conversation segments. Accents and automatic transcripts are not error labels.")
			}
		case "ELRD":
			if table == "sp_elrd_turns" {
				add("coverage", member, table, empiricalViewName(member), "Conversation turns with automatic transcripts. These are context examples, not verified mistakes.")
			}
		case "DIPLOMAT":
			if table == "sp_diplomat" {
				add("coverage", member, table, empiricalViewName(path.Dir(member))+" · "+empiricalViewName(member), "One dialogue task view. Task answers, translations and overlapping views are not independent mistake populations.")
			}
		case "DRAL":
			if table == "sp_dral_conversation" || table == "sp_dral_fragments_short" || table == "sp_dral_fragments_long" {
				add("coverage", member, table, empiricalViewName(member), "One release and dialogue view. Fragments share recordings; no transcript or mistake labels are inferred.")
			}
		}
	}
	return out, rows.Err()
}

func (s *Storage) EmpiricalPopulations(ctx context.Context) ([]EmpiricalPopulationChoice, error) {
	rows, err := s.DB.Query(ctx, "SELECT DISTINCT ON (r.source_id,r.payload->>'source_version',r.payload->>'manifest_sha256') i.id,r.payload,i.created_at FROM source_import i JOIN source_release r ON r.id=i.release_id WHERE i.published=true AND i.phase='complete' ORDER BY r.source_id,r.payload->>'source_version',r.payload->>'manifest_sha256',i.created_at DESC,i.id DESC")
	if err != nil {
		return nil, err
	}
	type item struct {
		id      string
		release SourceRelease
		at      time.Time
	}
	items := []item{}
	for rows.Next() {
		var a item
		var raw []byte
		if err = rows.Scan(&a.id, &raw, &a.at); err != nil {
			rows.Close()
			return nil, err
		}
		if err = json.Unmarshal(raw, &a.release); err != nil {
			rows.Close()
			return nil, err
		}
		items = append(items, a)
	}
	err = rows.Err()
	rows.Close()
	if err != nil {
		return nil, err
	}
	out := []EmpiricalPopulationChoice{}
	for _, a := range items {
		choices, e := s.empiricalChoices(ctx, a.id, a.release)
		if e != nil {
			return nil, e
		}
		for i := range choices {
			choices[i].ImportedAt = a.at.UTC().Format(time.RFC3339)
		}
		out = append(out, choices...)
	}
	return out, nil
}
func (s *Server) empiricalPopulations(w http.ResponseWriter, r *http.Request) {
	items, err := s.Store.EmpiricalPopulations(r.Context())
	if err != nil {
		sourceHTTPError(w, err)
		return
	}
	writeJSON(w, 200, items)
}

func (s *Storage) empiricalImportedSource(ctx context.Context, selected EmpiricalSource) (empirical.Input, EmpiricalSourceSummary, error) {
	var raw []byte
	err := s.DB.QueryRow(ctx, "SELECT r.payload FROM source_import i JOIN source_release r ON r.id=i.release_id WHERE i.id=$1 AND i.published=true AND i.phase='complete'", selected.Import).Scan(&raw)
	if err != nil {
		return empirical.Input{}, EmpiricalSourceSummary{}, err
	}
	var release SourceRelease
	if err = json.Unmarshal(raw, &release); err != nil {
		return empirical.Input{}, EmpiricalSourceSummary{}, err
	}
	choices, err := s.empiricalChoices(ctx, selected.Import, release)
	if err != nil {
		return empirical.Input{}, EmpiricalSourceSummary{}, err
	}
	var choice *EmpiricalPopulationChoice
	for i := range choices {
		c := &choices[i]
		if c.Source.Basis == selected.Basis && c.Source.Member == selected.Member && c.Source.Table == selected.Table {
			choice = c
			break
		}
	}
	if choice == nil {
		return empirical.Input{}, EmpiricalSourceSummary{}, ErrInput
	}
	_, taxonomy, err := preparationCategories()
	if err != nil {
		return empirical.Input{}, EmpiricalSourceSummary{}, err
	}
	view := selected.Member
	if view == "" {
		view = selected.Basis
	}
	p := empirical.Population{Release: release.ID, View: view, Split: "unknown", Window: "sentence", Modality: "written", Origin: "native_with_derived_mapping", Taxonomy: taxonomy, Crosswalk: empirical.SourceMappingVersion}
	for _, file := range release.Files {
		if file.Path == selected.Member && file.Partition != nil {
			p.Split = *file.Partition
			break
		}
	}
	summary := EmpiricalSourceSummary{Source: release.Source, Name: empiricalSourceName(release.Source), Version: release.Release, View: strings.TrimPrefix(choice.Title, choice.SourceName+" · "), Unit: "sentences", Mapping: empirical.SourceMappingVersion, Notes: []string{choice.Description, "Category mappings are derived rules. A missing mapping does not mean a category is absent. Correct-opportunity rates and population-wide learner frequencies are not measured."}, Coverage: []EmpiricalCoverageCount{}}
	summary.Manifest = release.Manifest
	summary.Constructed = empiricalConstructed(release)
	if summary.Constructed {
		p.Origin = "constructed"
		summary.Name = "Constructed example · " + summary.Name
	}
	if selected.Basis == "m2" {
		selected.AnnotatedLeaves = []string{}
		selected.LeafByEvent = nil
		selected.WindowPointer = ""
		in, e := s.empiricalSource(ctx, p, selected)
		return in, summary, e
	}
	if strings.HasPrefix(selected.Basis, "manual_phones_") {
		p.Window = "utterance"
		p.Modality = "speech"
		summary.Unit = "utterances"
		return s.empiricalSourceSpeech(ctx, selected, p, summary)
	}
	p.Origin = "native_coverage_only"
	p.Window = "record"
	p.Modality = "speech"
	p.Crosswalk = "not-supplied"
	if release.Source == "FCE-2.1" || release.Source == "WILOCNESS-2.1" || release.Source == "JFLEG" {
		p.Modality = "written"
	}
	if release.Source == "DIPLOMAT" {
		p.Modality = "dialogue_text"
	}
	summary.Mapping = "not-supplied"
	return s.empiricalSourceCoverage(ctx, selected, p, summary)
}

func empiricalConstructed(release SourceRelease) bool {
	return strings.HasPrefix(release.Origin, "constructed:") || strings.HasPrefix(release.Release, "constructed-")
}

// Readable editions distinguish related versions without displaying commit hashes.
func empiricalEdition(r SourceRelease) string {
	switch r.Source {
	case "FCE-2.1", "WILOCNESS-2.1":
		return "BEA 2.1"
	case "L2-ARCTIC":
		if strings.Contains(r.Release, "v5") {
			return "Version 5"
		}
	case "DRAL":
		if strings.HasPrefix(r.Release, "8.0") {
			return "Version 8.0"
		}
		if strings.HasPrefix(r.Release, "16kHz") {
			return "Base release, 16 kHz"
		}
	case "EDACC":
		if strings.HasPrefix(r.Release, "1.0") {
			return "Version 1.0"
		}
	}
	return "Imported snapshot"
}
