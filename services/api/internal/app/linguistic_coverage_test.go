package app

// Authored references exercise real selection/context and exact arithmetic.
// They do not make the deterministic owner a linguistic or acoustic judge.
import (
	"encoding/json"
	"math/big"
	"os"
	"strings"
	"tangerine.local/api/internal/scoring"
	"testing"

	"go.yaml.in/yaml/v3"
)

type linguisticContrast struct {
	ID       string   `json:"taxonomy_id"`
	Subtypes []string `json:"subtypes"`
	Context  string   `json:"contrast_context"`
	Clean    string   `json:"canonical"`
	Surface  string   `json:"surface"`
	Status   string   `json:"surface_status"`
	Modality string   `json:"modality"`
	Control  struct {
		Context string `json:"context"`
		Text    string `json:"text"`
		Reason  string `json:"reason"`
	} `json:"correct_control"`
}

func linguisticReferences(t *testing.T) []linguisticContrast {
	t.Helper()
	raw, e := os.ReadFile("testdata/linguistic-contrasts.json")
	if e != nil {
		t.Fatal(e)
	}
	var data struct {
		Examples []linguisticContrast `json:"examples"`
	}
	if e = json.Unmarshal(raw, &data); e != nil || len(data.Examples) != 122 {
		t.Fatal(e, len(data.Examples))
	}
	return data.Examples
}

func TestLinguisticContextPositive(t *testing.T) {
	a, _ := generationRegistry("error-taxonomy.v1.yaml")
	r, _ := generationRegistry("mutation-recipes.v1.json")
	p, _ := generationRegistry("acoustic-production.v1.json")
	for _, ref := range linguisticReferences(t) {
		t.Run(ref.ID, func(t *testing.T) {
			tax, _, _, e := mutationSelection(map[string]any{"targets": []any{map[string]any{"taxonomy_id": ref.ID}}}, a, r, p)
			if e != nil {
				t.Fatal(e)
			}
			entries := tax["entries"].([]any)
			if len(entries) != 1 || entries[0].(map[string]any)["id"] != ref.ID {
				t.Fatal("wrong selected identity", tax)
			}
			row := entries[0].(map[string]any)
			exclusion, _ := json.Marshal(row["exclusion"])
			var exclusions []string
			_ = json.Unmarshal(exclusion, &exclusions)
			joined := strings.Join(exclusions, "\n")
			if !strings.Contains(joined, ref.Control.Text) || !strings.Contains(joined, ref.Control.Reason) {
				t.Fatal("concrete correct variant lost at native generation boundary", joined)
			}
			inclusion, _ := json.Marshal(row["inclusion"])
			for _, subtype := range ref.Subtypes {
				if !strings.Contains(string(inclusion), subtype) {
					t.Fatal("subtype missing from generation context", subtype)
				}
			}
			// The actual mapper selector consumes the same definition/exclusion fields.
			mapperRow := map[string]any{"id": ref.ID, "exclusion_criteria": row["exclusion"]}
			resources := InterpretationResources{Key: map[string]any{"units": []any{map[string]any{"primary_taxonomy_id": ref.ID}}}, Taxonomy: []any{mapperRow}}
			mapped := mappingTaxonomyContext(resources, "")
			if len(mapped) != 1 || mapped[0].(map[string]any)["id"] != ref.ID {
				t.Fatal("mapper lost exact leaf", mapped)
			}
			mappedExclusion, _ := json.Marshal(mapped[0].(map[string]any)["exclusion_criteria"])
			if string(mappedExclusion) != string(exclusion) {
				t.Fatal("mapper lost the concrete correct control", string(mappedExclusion))
			}
		})
	}
}

func linguisticScore(t *testing.T, ref linguisticContrast, kind, verdict string, suppliedReason bool) scoring.Result {
	t.Helper()
	domain := strings.Join(strings.Split(ref.ID, ".")[:1], ".")
	if strings.HasPrefix(ref.ID, "pronunciation.") {
		domain = strings.Join(strings.Split(ref.ID, ".")[:2], ".")
	}
	in := scoring.Input{Attempt: "constructed-reference", Case: ref.ID, DecisionSHA: strings.Repeat("a", 64), Policy: "answer-components-v2", Enabled: map[string]bool{"detection": true, "classification": true, "correction": true}, Unresolved: map[string]bool{}, Units: []scoring.Unit{{ID: "u", Domain: domain, Category: ref.ID, Kind: kind, Accepted: []string{ref.ID}, Weight: 1, Correction: kind == "true_error", Explanation: kind == "true_error"}}, Decisions: []scoring.Decision{{ID: "d", Unit: "u", Verdict: verdict, Category: ref.ID, CorrectionSupplied: verdict == "matched_error" || verdict == "false_positive", ExplanationSupplied: suppliedReason, Correction: big.NewRat(1, 1), Explanation: big.NewRat(0, 1)}}}
	result, e := scoring.Score(in)
	if e != nil {
		t.Fatal(e)
	}
	return result
}

func TestLinguisticControlPositive(t *testing.T) {
	for _, ref := range linguisticReferences(t) {
		t.Run(ref.ID, func(t *testing.T) {
			r := linguisticScore(t, ref, "acceptable", "confirmed_acceptable", false)
			if r.Counts.G != 0 || r.Counts.TP != 0 || r.Counts.FN != 0 || r.Counts.FP != 0 || r.Counts.D != 1 || r.Items[0].Kind != "acceptable" {
				t.Fatal("permitted variant created error opportunity/penalty", r.Counts, r.Items)
			}
		})
	}
}

func TestLinguisticSelectionNegative(t *testing.T) {
	a, _ := generationRegistry("error-taxonomy.v1.yaml")
	r, _ := generationRegistry("mutation-recipes.v1.json")
	p, _ := generationRegistry("acoustic-production.v1.json")
	for _, ref := range linguisticReferences(t) {
		t.Run(ref.ID, func(t *testing.T) {
			family := "grammar"
			if strings.HasPrefix(ref.ID, "grammar.") {
				family = "lexis"
			}
			_, _, _, e := mutationSelection(map[string]any{"targets": []any{map[string]any{"taxonomy_id": ref.ID}}, "exercise_request": map[string]any{"category_families": []any{family}}}, a, r, p)
			if e != ErrConflict {
				t.Fatal("conflicting selected family was silently replaced or allowed", family, ref.ID, e)
			}
		})
	}
}

func TestLinguisticControlNegative(t *testing.T) {
	for _, ref := range linguisticReferences(t) {
		t.Run(ref.ID, func(t *testing.T) {
			r := linguisticScore(t, ref, "acceptable", "false_positive", false)
			m := r.Metrics["detection.precision"]
			if r.Counts.FP != 1 || r.Counts.DF != 1 || r.Counts.TP != 0 || r.Counts.FN != 0 || m.Numerator == nil || *m.Numerator != "0" || *m.Denominator != "1" {
				t.Fatal("unnecessary rewrite received error-detection credit", r.Counts, m)
			}
		})
	}
}

func TestLinguisticPrimaryPositive(t *testing.T) {
	for _, ref := range linguisticReferences(t) {
		if ref.Status != "true_error" {
			continue
		}
		t.Run(ref.ID, func(t *testing.T) {
			r := linguisticScore(t, ref, "true_error", "matched_error", false)
			m := r.Metrics["correction.strict_accuracy"]
			if r.Counts.TP != 1 || r.Counts.FN != 0 || r.Counts.FP != 0 || m.Value == nil || *m.Value != 1 || r.Explanation.Status != "not_applicable" {
				t.Fatal("omitted optional reason cancelled a correct primary answer", r.Counts, m, r.Explanation)
			}
		})
	}
}

func TestLinguisticExplanationNegative(t *testing.T) {
	for _, ref := range linguisticReferences(t) {
		if ref.Status != "true_error" {
			continue
		}
		t.Run(ref.ID, func(t *testing.T) {
			r := linguisticScore(t, ref, "true_error", "matched_error", true)
			m := r.Metrics["correction.strict_accuracy"]
			if r.Counts.TP != 1 || r.Counts.FN != 0 || m.Value == nil || *m.Value != 1 || r.Explanation.Value == nil || *r.Explanation.Value != 0 {
				t.Fatal("false supplied explanation changed supported detection/correction", r.Counts, m, r.Explanation)
			}
		})
	}
}

func TestLinguisticRecipePositive(t *testing.T) {
	references := map[string]linguisticContrast{}
	for _, ref := range linguisticReferences(t) {
		references[ref.ID] = ref
	}
	raw, _ := generationRegistry("mutation-recipes.v1.json")
	var recipes struct {
		Rows []struct {
			ID      string `json:"taxonomy_id"`
			Clean   string `json:"canonical_example"`
			Surface string `json:"surface_example"`
			Edit    *struct {
				Start        int    `json:"start_cp"`
				End          int    `json:"end_cp"`
				Quote        string `json:"exact_text"`
				Text         string `json:"replacement"`
				SurfaceStart int    `json:"surface_start_cp"`
				SurfaceEnd   int    `json:"surface_end_cp"`
			} `json:"codepoint_edit"`
		} `json:"recipes"`
	}
	if e := json.Unmarshal(raw, &recipes); e != nil {
		t.Fatal(e)
	}
	for _, row := range recipes.Rows {
		t.Run(row.ID, func(t *testing.T) {
			ref, exists := references[row.ID]
			if !exists || row.Clean != ref.Clean || row.Surface != ref.Surface {
				t.Fatal("recipe differs from its independently authored literal contrast", row.ID, row.Clean, row.Surface)
			}
			if row.Edit != nil {
				cp := []rune(row.Clean)
				x := row.Edit
				if string(cp[x.Start:x.End]) != x.Quote || string(cp[:x.Start])+x.Text+string(cp[x.End:]) != row.Surface {
					t.Fatal("written example replay differs from its literal reference")
				}
				if !mutationScopedChanges(row.Clean, row.Surface, [][2]int{{x.SurfaceStart, x.SurfaceEnd}}) {
					t.Fatal("native mutation scope rejected the declared example")
				}
			}
		})
	}
}

func TestLinguisticAliasesPositive(t *testing.T) {
	raw, _ := generationRegistry("category-aliases.v1.yaml")
	var registry struct {
		Entries []struct {
			ID      string   `yaml:"target_id"`
			English []string `yaml:"english"`
		} `yaml:"entries"`
	}
	if e := yaml.Unmarshal(raw, &registry); e != nil {
		t.Fatal(e)
	}
	r := InterpretationResources{Aliases: []any{}}
	for _, entry := range registry.Entries {
		for _, alias := range entry.English {
			r.Aliases = append(r.Aliases, map[string]any{"language": "en", "normalized_alias": strings.ToLower(alias), "target_ids": []any{entry.ID}})
		}
	}
	aliases := mappingAliasEntries(r, "consonant metathesis", false)
	found := false
	for _, value := range aliases {
		row := value.(map[string]any)
		if row["normalized_alias"] == "consonant metathesis" {
			if row["target_ids"].([]any)[0] != "pronunciation.segmental.consonant_substitution" {
				t.Fatal("metathesis created a different primary identity", row)
			}
			found = true
		}
	}
	if !found {
		t.Fatal("authored alias did not reach the real mapper context")
	}
}

func TestLinguisticAliasesNegative(t *testing.T) {
	r := InterpretationResources{Aliases: []any{map[string]any{"language": "en", "normalized_alias": "consonant metathesis", "target_ids": []any{"pronunciation.segmental.consonant_substitution"}}}}
	if got := mappingAliasEntries(r, "", false); len(got) != 0 {
		t.Fatal("invented category wording for an answer with no category supplied", got)
	}
}
