package app

import (
	"encoding/json"
	"testing"
)

func projectionCandidate(t *testing.T, text, exact string, a, b float64, mode string) map[string]any {
	t.Helper()
	return map[string]any{"utterances": []any{map[string]any{"id": "u1", "surface_text": text}}, "planned_units": []any{map[string]any{"id": "e1", "realization": map[string]any{"mode": mode}, "text_spans": []any{map[string]any{"utterance_id": "u1", "span": map[string]any{"exact_text": exact, "start_cp": a, "end_cp": b}}}}}}
}
func projectedSpan(v map[string]any) map[string]any {
	return v["planned_units"].([]any)[0].(map[string]any)["text_spans"].([]any)[0].(map[string]any)["span"].(map[string]any)
}
func TestReleaseMutationUniqueLocatorPositive(t *testing.T) {
	v := projectionCandidate(t, "The café open tomorrow.", "open", 10, 14, "textual")
	normalizeMutationLocators(v)
	s := projectedSpan(v)
	if s["start_cp"] != float64(9) || s["end_cp"] != float64(13) || s["exact_text"] != "open" {
		t.Fatal(s)
	}
}
func TestReleaseMutationCorrectLocatorPositive(t *testing.T) {
	v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
	before, _ := json.Marshal(v)
	normalizeMutationLocators(v)
	after, _ := json.Marshal(v)
	if string(before) != string(after) {
		t.Fatal(v)
	}
}
func TestReleaseMutationAmbiguousLocatorNegative(t *testing.T) {
	for _, text := range []string{"open then open", "aaa"} {
		exact := "open"
		if text == "aaa" {
			exact = "aa"
		}
		v := projectionCandidate(t, text, exact, 99, 100, "textual")
		normalizeMutationLocators(v)
		if projectedSpan(v)["start_cp"] != float64(99) {
			t.Fatal("ambiguous occurrence guessed", v)
		}
	}
}
func TestReleaseMutationAbsentLocatorNegative(t *testing.T) {
	for _, exact := range []string{"opens", ""} {
		v := projectionCandidate(t, "The café open tomorrow.", exact, 99, 100, "textual")
		normalizeMutationLocators(v)
		if projectedSpan(v)["start_cp"] != float64(99) {
			t.Fatal("absent/empty quote guessed", v)
		}
	}
}
func TestReleaseMutationAcousticLocatorNegative(t *testing.T) {
	v := projectionCandidate(t, "pan ready", "pan", 99, 100, "acoustic_segmental")
	normalizeMutationLocators(v)
	if projectedSpan(v)["start_cp"] != float64(99) {
		t.Fatal("acoustic operation relocated", v)
	}
}
