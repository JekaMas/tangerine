package app

import "strings"

// A preferred replacement may quote canonical wording beyond its selected
// scope. Trim only that already supplied, unchanged context. Unknown mappings,
// other valid alternatives and missing corrective words are never guessed.
func normalizeMutationCorrectionScopes(value any) any {
	root, ok := value.(map[string]any)
	if !ok {
		return value
	}
	turns := map[string]map[string]any{}
	duplicates := map[string]bool{}
	utterances, _ := root["utterances"].([]any)
	for _, v := range utterances {
		if row, ok := v.(map[string]any); ok {
			if id, ok := row["id"].(string); ok {
				if turns[id] != nil {
					duplicates[id] = true
				}
				turns[id] = row
			}
		}
	}
	units, _ := root["planned_units"].([]any)
	for _, v := range units {
		u, ok := v.(map[string]any)
		if !ok || u["expected_judgment"] != "true_error" {
			continue
		}
		realization, _ := u["realization"].(map[string]any)
		spans, _ := u["text_spans"].([]any)
		if realization["mode"] != "textual" || len(spans) != 1 || u["recurrence"] != nil {
			continue
		}
		s, ok := spans[0].(map[string]any)
		if !ok {
			continue
		}
		id, _ := s["utterance_id"].(string)
		turn := turns[id]
		if turn == nil || duplicates[id] {
			continue
		}
		original, cok := turn["canonical_text"].(string)
		surface, sok := turn["surface_text"].(string)
		scope, _ := s["span"].(map[string]any)
		start, aok := scope["start_cp"].(float64)
		end, bok := scope["end_cp"].(float64)
		if !cok || !sok || !aok || !bok {
			continue
		}
		old, heard := []rune(original), []rune(surface)
		a, b := int(start), int(end)
		oldEnd := len(old) - (len(heard) - b)
		if a < 0 || b <= a || b > len(heard) || oldEnd <= a || oldEnd > len(old) {
			continue
		}
		if string(old[:a]) != string(heard[:a]) || string(old[oldEnd:]) != string(heard[b:]) {
			continue
		}
		canonical := string(old[a:oldEnd])
		if canonical == string(heard[a:b]) {
			continue
		}
		options, _ := u["corrections"].([]any)
		for _, v := range options {
			option, ok := v.(map[string]any)
			if !ok || option["kind"] != "replace" || option["canonical"] != true {
				continue
			}
			text, ok := option["text"].(string)
			if !ok || text == "" || text == canonical {
				continue
			}
			at := strings.Index(original, text)
			if at < 0 || at != strings.LastIndex(original, text) {
				continue
			}
			first := len([]rune(original[:at]))
			last := first + len([]rune(text))
			if first <= a && last >= oldEnd {
				option["text"] = canonical
				// The supplied IPA described a wider phrase. Its narrower value
				// is unknown; do not fabricate a phone alignment.
				option["ipa"] = nil
			}
		}
	}
	return value
}
