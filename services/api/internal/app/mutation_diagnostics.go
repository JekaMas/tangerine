package app

import (
	"encoding/json"
	"strings"
)

// These diagnostics supplement an already rejected structural projection during
// the same admission. They cannot admit a candidate or alter stored data. Partial
// data with unknown types gets only its structural error, without guessed scopes.
type partialGeneration struct {
	Utterances []struct {
		ID        string `json:"id"`
		Speaker   string `json:"speaker_id"`
		Canonical string `json:"canonical_text"`
		Surface   string `json:"surface_text"`
	} `json:"utterances"`
	Units []struct {
		ID    string `json:"id"`
		Spans []struct {
			Turn string `json:"utterance_id"`
			Span struct {
				Start *int    `json:"start_cp"`
				End   *int    `json:"end_cp"`
				Exact *string `json:"exact_text"`
			} `json:"span"`
		} `json:"text_spans"`
	} `json:"planned_units"`
	Acoustic []json.RawMessage `json:"acoustic_edits"`
}

func surfaceScopeHint(id string, text []rune) string {
	scope, _ := json.Marshal(map[string]any{"utterance_id": id, "span": map[string]any{"start_cp": 0, "end_cp": len(text), "exact_text": string(text)}})
	return "Final-surface span offsets/exact_text must match the actual surface, not the canonical wording. Fix every listed issue. A valid whole-turn scope is " + string(scope) + "; use this when a narrower affected scope cannot be located reliably."
}

// Coordinate evidence is feedback for the existing repair, never a rewritten
// candidate. An absent, empty or repeated literal receives no guessed locator.
func surfaceLocatorHint(id string, text []rune, start, end int, exact string) string {
	at := start
	if at < 0 {
		at = 0
	}
	if at > len(text) {
		at = len(text)
	}
	lo, hi := at-3, at+12
	if lo < 0 {
		lo = 0
	}
	if hi > len(text) {
		hi = len(text)
	}
	window := []any{}
	for cp := lo; cp < hi; cp++ {
		window = append(window, map[string]any{"cp": cp, "text": string(text[cp])})
	}
	var unique any
	surface := string(text)
	if exact != "" {
		first := strings.Index(surface, exact)
		if first >= 0 && first == strings.LastIndex(surface, exact) {
			a := len([]rune(surface[:first]))
			unique = map[string]any{"utterance_id": id, "span": map[string]any{"start_cp": a, "end_cp": a + len([]rune(exact)), "exact_text": exact}}
		}
	}
	evidence, _ := json.Marshal(map[string]any{"submitted_start_cp": start, "submitted_end_cp": end, "submitted_exact_text": exact, "coordinate_window": window, "unique_literal_scope": unique})
	return surfaceScopeHint(id, text) + "\nSurface coordinate evidence: " + string(evidence)
}
func mutationLocatorDiagnostic(raw []byte) string {
	var p partialGeneration
	if json.Unmarshal(raw, &p) != nil {
		return ""
	}
	turns := map[string][]rune{}
	for _, u := range p.Utterances {
		if u.ID != "" && u.Surface != "" {
			turns[u.ID] = []rune(u.Surface)
		}
	}
	hints := []string{}
	seen := map[string]bool{}
	for _, u := range p.Units {
		for _, s := range u.Spans {
			text, ok := turns[s.Turn]
			if !ok || s.Span.Start == nil || s.Span.End == nil || s.Span.Exact == nil {
				continue
			}
			a, z := *s.Span.Start, *s.Span.End
			if a < 0 || z < a || z > len(text) || string(text[a:z]) != *s.Span.Exact {
				if !seen[s.Turn] {
					hints = append(hints, surfaceLocatorHint(s.Turn, text, a, z, *s.Span.Exact))
					seen[s.Turn] = true
				}
			}
		}
	}
	return strings.Join(hints, "\n")
}
func canonicalPhaseDiagnostic(raw []byte, blueprint map[string]any) string {
	var p partialGeneration
	if json.Unmarshal(raw, &p) != nil {
		return ""
	}
	hints := []string{}
	if len(p.Units) > 0 || len(p.Acoustic) > 0 {
		hints = append(hints, "This is canonical_text: planned_units and acoustic_edits must both be empty. Mutation targets describe the next phase.")
	}
	speakers := map[string]bool{}
	for _, v := range blueprint["speakers"].([]any) {
		speakers[v.(map[string]any)["id"].(string)] = true
	}
	for _, u := range p.Utterances {
		if u.Speaker != "" && !speakers[u.Speaker] {
			hints = append(hints, "Use only the expanded blueprint speakers.")
		}
		if u.Canonical != "" && u.Surface != "" && u.Canonical != u.Surface {
			hints = append(hints, "The clean phase requires surface_text exactly equal to canonical_text.")
		}
	}
	return strings.Join(hints, "\n")
}
