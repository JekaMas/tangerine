package app

// Constructed historical text; native span/admission/manifest owners, no model.
import (
	"strings"
	"testing"
)

func TestHistoricalUnicodePositive(t *testing.T) {
	answer := "🙂 work; work"
	span := AnswerSpan{Start: 8, End: 12, Text: "work"}
	if err := normalizeAnswerSpan(answer, &span); err != nil {
		t.Fatal(err)
	}
	if span.Start != 8 || span.End != 12 || span.Text != "work" || !inAnswer([]rune(answer), span) || strings.Count(string([]rune(answer)[:span.End]), "work") != 2 || answer != "🙂 work; work" {
		t.Fatal(answer, span)
	}
}

func TestHistoricalUnicodeNegative(t *testing.T) {
	answer := "🙂 work; work"
	span := AnswerSpan{Start: 9, End: 13, Text: "work"}
	if inAnswer([]rune(answer), span) {
		t.Fatal("fabricated codepoint span accepted")
	}
	// The current provider normalization may recover genuine UTF-16 coordinates.
	// Recovery must point into the unchanged original answer, never invent text.
	if err := normalizeAnswerSpan(answer, &span); err != nil || span.Start != 8 || span.End != 12 || !inAnswer([]rune(answer), span) || answer != "🙂 work; work" {
		t.Fatal(answer, span, err)
	}
}

func historicalMutation(t *testing.T, surface string) (map[string]any, error) {
	t.Helper()
	b, clean, c, tax := mutationFixture()
	cleanTurn := clean["utterances"].([]any)[0].(map[string]any)
	cleanTurn["canonical_text"], cleanTurn["surface_text"] = "She works here.", "She works here."
	turn := c["utterances"].([]any)[0].(map[string]any)
	turn["canonical_text"], turn["surface_text"] = "She works here.", surface
	unit := c["planned_units"].([]any)[0].(map[string]any)
	unit["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(4), "end_cp": float64(8), "exact_text": "work"}
	unit["realization"].(map[string]any)["canonical_text"] = "works"
	unit["realization"].(map[string]any)["surface_text"] = "work"
	unit["corrections"].([]any)[0].(map[string]any)["text"] = "works"
	unit["rationale"] = "She requires third-person singular present works in this context."
	unit["rationale_required_propositions"].([]any)[0].(map[string]any)["description"] = "The third-person singular subject she requires works."
	unit["corrections"].([]any)[0].(map[string]any)["required_propositions"].([]any)[0].(map[string]any)["description"] = "Use works with she in this present context."
	if err := admitMutation(t, b, clean, c, tax); err != nil {
		return nil, err
	}
	return mutationManifest(c, "canonical", strings.Repeat("a", 64), "mutated", strings.Repeat("b", 64), strings.Repeat("c", 64), nil, nil), nil
}

func TestHistoricalMutationPositive(t *testing.T) {
	m, err := historicalMutation(t, "She work here.")
	if err != nil {
		t.Fatal(err)
	}
	edits := m["edits"].([]any)
	if len(edits) != 1 {
		t.Fatal(edits)
	}
	x := edits[0].(map[string]any)
	if x["start_cp"] != 8 || x["end_cp"] != 9 || x["original_text"] != "s" || x["replacement_text"] != "" || len(x["unit_ids"].([]any)) != 1 {
		t.Fatal(x)
	}
	cp := []rune("She works here.")
	if string(cp[:8])+string(cp[9:]) != "She work here." {
		t.Fatal("literal declared edit differs from saved surface")
	}
}

func TestHistoricalMutationNegative(t *testing.T) {
	if m, err := historicalMutation(t, "She work there."); err == nil || m != nil {
		t.Fatal("unattributed extra change admitted as a complete key", m, err)
	}
}
