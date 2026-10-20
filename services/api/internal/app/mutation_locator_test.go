package app

import (
	"encoding/json"
	"strings"
	"testing"
)

func locatorEvidence(t *testing.T, hint string) map[string]any {
	t.Helper()
	parts := strings.Split(hint, "\nSurface coordinate evidence: ")
	if len(parts) != 2 {
		t.Fatal(hint)
	}
	var result map[string]any
	if err := json.Unmarshal([]byte(parts[1]), &result); err != nil {
		t.Fatal(err)
	}
	return result
}
func TestMutationLocatorUnicodePositive(t *testing.T) {
	e := locatorEvidence(t, surfaceLocatorHint("u1", []rune("The café open tomorrow."), 10, 14, "open"))
	found := false
	for _, v := range e["coordinate_window"].([]any) {
		p := v.(map[string]any)
		if p["cp"] == float64(7) && p["text"] == "é" {
			found = true
		}
	}
	if !found {
		t.Fatal("Unicode codepoints must not be UTF-8 byte offsets", e)
	}
}
func TestMutationLocatorNarrowPositive(t *testing.T) {
	e := locatorEvidence(t, surfaceLocatorHint("u1", []rune("The café open tomorrow."), 10, 14, "open"))
	s := e["unique_literal_scope"].(map[string]any)["span"].(map[string]any)
	if s["start_cp"] != float64(9) || s["end_cp"] != float64(13) || s["exact_text"] != "open" {
		t.Fatal(e)
	}
}
func TestMutationLocatorAmbiguousNegative(t *testing.T) {
	e := locatorEvidence(t, surfaceLocatorHint("u1", []rune("open then open"), 999, 1000, "open"))
	if e["unique_literal_scope"] != nil {
		t.Fatal("ambiguous location guessed", e)
	}
	e = locatorEvidence(t, surfaceLocatorHint("u1", []rune("aaa"), 0, 1, "aa"))
	if e["unique_literal_scope"] != nil {
		t.Fatal("overlapping matches guessed", e)
	}
}
func TestMutationLocatorEmptyNegative(t *testing.T) {
	e := locatorEvidence(t, surfaceLocatorHint("u1", []rune("The café open tomorrow."), -1, 999, ""))
	if e["unique_literal_scope"] != nil {
		t.Fatal("empty boundary guessed", e)
	}
	e = locatorEvidence(t, surfaceLocatorHint("u1", []rune("The café open tomorrow."), 9, 14, "opens"))
	if e["unique_literal_scope"] != nil {
		t.Fatal("absent canonical word located in the surface", e)
	}
	b, clean, c, tax := mutationFixture()
	c["planned_units"].([]any)[0].(map[string]any)["text_spans"].([]any)[0].(map[string]any)["span"].(map[string]any)["end_cp"] = float64(14)
	if admitMutation(t, b, clean, c, tax) == nil {
		t.Fatal("coordinate hint silently admitted an invalid key")
	}
}
