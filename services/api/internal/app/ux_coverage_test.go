package app

// Constructed two-turn replies test the actual one-time mutation admission.
// They establish category/count behavior, not live linguistic model quality.
import (
	"encoding/json"
	"errors"
	"strings"
	"tangerine.local/api/internal/provider"
	"testing"
)

func uxCategoryCoverageFixture() (map[string]any, map[string]any, map[string]any, map[string]any) {
	b, clean, c, tax := mutationFixture()
	r := b["exercise_request"].(map[string]any)
	r["category_families"] = []any{}
	r["category_ids"] = []any{"grammar.verbs.subject_verb_agreement", "grammar.nouns.number"}
	r["mutation_count"] = float64(2)
	clean["utterances"] = append(clean["utterances"].([]any), map[string]any{"id": "u2", "speaker_id": "s1", "canonical_text": "I bought two tickets.", "surface_text": "I bought two tickets."})
	c["utterances"] = append(c["utterances"].([]any), map[string]any{"id": "u2", "speaker_id": "s1", "canonical_text": "I bought two tickets.", "surface_text": "I bought two ticket."})
	raw, _ := json.Marshal(c["planned_units"].([]any)[0])
	var second map[string]any
	_ = json.Unmarshal(raw, &second)
	second["id"] = "e2"
	second["primary_taxonomy_id"] = "grammar.nouns.number"
	second["accepted_taxonomy_ids"] = []any{"grammar.nouns.number"}
	second["utterance_ids"] = []any{"u2"}
	second["text_spans"] = []any{map[string]any{"utterance_id": "u2", "span": map[string]any{"start_cp": float64(13), "end_cp": float64(19), "exact_text": "ticket"}}}
	second["realization"].(map[string]any)["canonical_text"] = "tickets"
	second["realization"].(map[string]any)["surface_text"] = "ticket"
	second["corrections"].([]any)[0].(map[string]any)["text"] = "tickets"
	second["rationale"] = "The explicit two tickets requires a plural count noun."
	c["planned_units"] = append(c["planned_units"].([]any), second)
	tax["entries"] = append(tax["entries"].([]any), map[string]any{"id": "grammar.nouns.number", "domain": "grammar"})
	return b, clean, c, tax
}

func TestUXCategoryCoveragePositive(t *testing.T) {
	b, clean, c, tax := uxCategoryCoverageFixture()
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}

func TestUXCategoryCoverageNegative(t *testing.T) {
	b, clean, c, tax := uxCategoryCoverageFixture()
	clean["utterances"].([]any)[1] = map[string]any{"id": "u2", "speaker_id": "s1", "canonical_text": "The museum closes at five.", "surface_text": "The museum closes at five."}
	c["utterances"].([]any)[1] = map[string]any{"id": "u2", "speaker_id": "s1", "canonical_text": "The museum closes at five.", "surface_text": "The museum close at five."}
	u := c["planned_units"].([]any)[1].(map[string]any)
	u["primary_taxonomy_id"] = "grammar.verbs.subject_verb_agreement"
	u["accepted_taxonomy_ids"] = []any{"grammar.verbs.subject_verb_agreement"}
	u["text_spans"] = []any{map[string]any{"utterance_id": "u2", "span": map[string]any{"start_cp": float64(11), "end_cp": float64(16), "exact_text": "close"}}}
	u["realization"].(map[string]any)["canonical_text"] = "closes"
	u["realization"].(map[string]any)["surface_text"] = "close"
	u["corrections"].([]any)[0].(map[string]any)["text"] = "closes"
	e := admitMutation(t, b, clean, c, tax)
	var invalid *provider.OutputValidationError
	if !errors.As(e, &invalid) || !strings.Contains(invalid.Detail, "every explicitly selected") {
		t.Fatal("two errors from one leaf must not satisfy two requested categories", e)
	}
}
