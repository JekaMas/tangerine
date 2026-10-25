package app

import (
	"encoding/json"
	"strings"
	"testing"
)

// Authored English contrasts pass through the real mutation admission and
// manifest owners. This is deterministic integration, not a model/hearing claim.
func functionalContrast(t *testing.T, ref linguisticContrast) (map[string]any, map[string]any, map[string]any, map[string]any) {
	t.Helper()
	b, clean, candidate, _ := mutationFixture()
	family := strings.Split(ref.ID, ".")[0]
	b["exercise_request"].(map[string]any)["category_families"] = []any{family}
	b["exercise_request"].(map[string]any)["category_ids"] = []any{ref.ID}
	cleanTurn := clean["utterances"].([]any)[0].(map[string]any)
	cleanTurn["canonical_text"], cleanTurn["surface_text"] = ref.Clean, ref.Clean
	turn := candidate["utterances"].([]any)[0].(map[string]any)
	turn["canonical_text"], turn["surface_text"] = ref.Clean, ref.Surface
	u := candidate["planned_units"].([]any)[0].(map[string]any)
	u["primary_taxonomy_id"], u["accepted_taxonomy_ids"], u["domain"] = ref.ID, []any{ref.ID}, family
	u["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(0), "end_cp": float64(len([]rune(ref.Surface))), "exact_text": ref.Surface}
	realization := u["realization"].(map[string]any)
	realization["canonical_text"], realization["surface_text"] = ref.Clean, ref.Surface
	correction := u["corrections"].([]any)[0].(map[string]any)
	correction["text"] = ref.Clean
	correction["required_propositions"] = []any{map[string]any{"id": "repair1", "description": "Restore the authored reference in its declared context: " + ref.Clean}}
	u["rationale"] = ref.Context + " The authored correct reference is: " + ref.Clean
	u["rationale_required_propositions"] = []any{map[string]any{"id": "reason1", "description": u["rationale"]}}
	a, _ := generationRegistry("error-taxonomy.v1.yaml")
	r, _ := generationRegistry("mutation-recipes.v1.json")
	p, _ := generationRegistry("acoustic-production.v1.json")
	tax, recipes, _, err := mutationSelection(b, a, r, p)
	if err != nil || len(recipes) != 1 {
		t.Fatal("exact selected recipe absent", ref.ID, err)
	}
	return b, clean, candidate, tax
}

func TestFXWrittenMutationPositive(t *testing.T) {
	count := 0
	for _, ref := range linguisticReferences(t) {
		if strings.HasPrefix(ref.ID, "pronunciation.") || strings.HasPrefix(ref.ID, "acceptable_variant.") || ref.Modality != "written_contextual_language" {
			continue
		}
		count++
		t.Run(ref.ID, func(t *testing.T) {
			b, clean, candidate, tax := functionalContrast(t, ref)
			if err := admitMutation(t, b, clean, candidate, tax); err != nil {
				t.Fatal("native authored mutation rejected", err)
			}
			m := mutationManifest(candidate, "clean", strings.Repeat("a", 64), "mutated", strings.Repeat("b", 64), strings.Repeat("c", 64), nil, nil)
			text, err := ReplayMutation(ref.Clean, m["edits"].([]any))
			if err != nil || text != ref.Surface {
				t.Fatal("native replay differs from independent literal", text, ref.Surface, err)
			}
			unit := m["planned_units"].([]any)[0].(map[string]any)
			if unit["primary_taxonomy_id"] != ref.ID || unit["corrections"].([]any)[0].(map[string]any)["text"] != ref.Clean {
				t.Fatal("key lost category or correction", unit)
			}
			if unit["rationale"] != ref.Context+" The authored correct reference is: "+ref.Clean {
				t.Fatal("key inherited an unrelated category's rationale", unit)
			}
		})
	}
	if count != 83 {
		t.Fatal("written non-pronunciation population changed", count)
	}
}

func TestFXWrittenMutationNegative(t *testing.T) {
	for _, ref := range linguisticReferences(t) {
		if strings.HasPrefix(ref.ID, "pronunciation.") || strings.HasPrefix(ref.ID, "acceptable_variant.") || ref.Modality != "written_contextual_language" {
			continue
		}
		t.Run(ref.ID, func(t *testing.T) {
			b, clean, candidate, tax := functionalContrast(t, ref)
			unit := candidate["planned_units"].([]any)[0].(map[string]any)
			unit["primary_taxonomy_id"] = "unselected.category"
			if admitMutation(t, b, clean, candidate, tax) == nil {
				t.Fatal("unselected leaf admitted")
			}
			unit["primary_taxonomy_id"] = ref.ID
			unit["corrections"].([]any)[0].(map[string]any)["text"] = ref.Surface
			if admitMutation(t, b, clean, candidate, tax) == nil {
				t.Fatal("no-op textual correction admitted")
			}
			unit["corrections"].([]any)[0].(map[string]any)["text"] = ref.Clean
			candidate["utterances"].([]any)[0].(map[string]any)["canonical_text"] = "An unrelated baseline."
			if admitMutation(t, b, clean, candidate, tax) == nil {
				t.Fatal("rewritten clean checkpoint admitted")
			}
		})
	}
}

func TestFXHistorySummaryPositive(t *testing.T) {
	a := map[string]any{"attempt_id": "original", "answer_text": "  Use\n two\t tickets.  ", "state": "completed"}
	heard := map[string]any{"title": "The original conversation", "key": "private"}
	v := attemptHistorySummary(a, heard, "result")
	if v["exercise_title"] != "The original conversation" || v["answer_excerpt"] != "Use two tickets." || v["result_id"] != "result" || v["id"] != "original" {
		t.Fatal(v)
	}
	if _, leak := v["key"]; leak {
		t.Fatal("private context escaped")
	}
}

func TestFXHistorySummaryUnicodePositive(t *testing.T) {
	a := map[string]any{"answer_text": strings.Repeat("🙂", 161)}
	v := attemptHistorySummary(a, map[string]any{"title": strings.Repeat("Ж", 201)}, nil)
	if v["exercise_title"] != strings.Repeat("Ж", 199)+"…" || v["answer_excerpt"] != strings.Repeat("🙂", 160)+"…" {
		t.Fatal("truncation split Unicode or changed the specified lengths", v)
	}
}

func TestFXHistoryLegacyNegative(t *testing.T) {
	v := attemptHistorySummary(map[string]any{"answer_text": "\n\t "}, nil, nil)
	if v["exercise_title"] != nil || v["answer_excerpt"] != nil || v["started_at"] != nil {
		t.Fatal("invented legacy metadata", v)
	}
	if attemptHistorySummary(nil, map[string]any{"title": " ", "topic": "Saved topic"}, nil)["exercise_title"] != "Saved topic" {
		t.Fatal("saved topic fallback lost")
	}
}

func TestFXPreparationDatePositive(t *testing.T) {
	summary := speechSummary(map[string]any{"id": "p", "phase_states": map[string]any{"render": "complete"}, "created_at": "2026-10-20T12:34:00Z"})
	if summary["created_at"] != "2026-10-20T12:34:00Z" {
		t.Fatal("creation date changed at read", summary)
	}
	// Read back a JSON projection to ensure optional fields stay ordinary values.
	raw, _ := json.Marshal(summary)
	if !strings.Contains(string(raw), `"created_at":"2026-10-20T12:34:00Z"`) {
		t.Fatal(string(raw))
	}
}
