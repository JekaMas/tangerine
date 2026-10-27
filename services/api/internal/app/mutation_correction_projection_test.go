package app

import "testing"

func TestLocalCorrectionScopeTrimPositive(t *testing.T) {
	for _, item := range []struct {
		clean, surface, quote, correction, want string
		start, end                              float64
	}{
		{"We make a decision.", "We do a decision.", "do a", "make a decision", "make a", 3, 7},
		{"🙂We make a decision.", "🙂We do a decision.", "do a", "🙂We make a decision.", "make a", 4, 8},
	} {
		v := projectionCandidate(t, item.surface, item.quote, item.start, item.end, "textual")
		v["utterances"].([]any)[0].(map[string]any)["canonical_text"] = item.clean
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["expected_judgment"] = "true_error"
		u["corrections"] = []any{map[string]any{"kind": "replace", "canonical": true, "text": item.correction, "ipa": "wider phrase"}}
		normalizeMutationOutput(v)
		if u["corrections"].([]any)[0].(map[string]any)["text"] != item.want || u["corrections"].([]any)[0].(map[string]any)["ipa"] != nil {
			t.Fatal(v)
		}
	}
}

func TestLocalCorrectionScopePreserveNegative(t *testing.T) {
	for _, correction := range []string{"take a", "wrong wording", "a"} {
		v := projectionCandidate(t, "We do a decision.", "do a", 3, 7, "textual")
		v["utterances"].([]any)[0].(map[string]any)["canonical_text"] = "We make a decision."
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["expected_judgment"] = "true_error"
		u["corrections"] = []any{map[string]any{"kind": "replace", "canonical": true, "text": correction}, map[string]any{"kind": "replace", "canonical": false, "text": "take a"}}
		normalizeMutationOutput(v)
		if u["corrections"].([]any)[0].(map[string]any)["text"] != correction || u["corrections"].([]any)[1].(map[string]any)["text"] != "take a" {
			t.Fatal(v)
		}
	}
	// Other changed context makes the canonical coordinate association unknown.
	v := projectionCandidate(t, "They do a decision.", "do a", 5, 9, "textual")
	v["utterances"].([]any)[0].(map[string]any)["canonical_text"] = "We make a decision."
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["expected_judgment"] = "true_error"
	u["corrections"] = []any{map[string]any{"kind": "replace", "canonical": true, "text": "make a decision"}}
	normalizeMutationOutput(v)
	if u["corrections"].([]any)[0].(map[string]any)["text"] != "make a decision" {
		t.Fatal(v)
	}
}
