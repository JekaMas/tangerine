package app

import "strings"

// A unique literal is an unambiguous location. Derive its Unicode arithmetic
// during new-output admission; retain the original reply in provider evidence.
// Never guess repeated/absent/empty quotes or relocate an acoustic operation.
func normalizeMutationLocators(value any) any {
	root, ok := value.(map[string]any)
	if !ok {
		return value
	}
	turns := map[string]string{}
	duplicate := map[string]bool{}
	if rows, ok := root["utterances"].([]any); ok {
		for _, v := range rows {
			if row, ok := v.(map[string]any); ok {
				id, iok := row["id"].(string)
				text, tok := row["surface_text"].(string)
				if iok && tok {
					if _, exists := turns[id]; exists {
						duplicate[id] = true
					}
					turns[id] = text
				}
			}
		}
	}
	rows, _ := root["planned_units"].([]any)
	for _, v := range rows {
		row, ok := v.(map[string]any)
		if !ok {
			continue
		}
		r, ok := row["realization"].(map[string]any)
		if !ok || r["mode"] != "textual" {
			continue
		}
		spans, _ := row["text_spans"].([]any)
		for _, v := range spans {
			s, ok := v.(map[string]any)
			if !ok {
				continue
			}
			id, _ := s["utterance_id"].(string)
			text, known := turns[id]
			if !known || duplicate[id] {
				continue
			}
			span, ok := s["span"].(map[string]any)
			if !ok {
				continue
			}
			exact, ok := span["exact_text"].(string)
			if !ok || exact == "" {
				continue
			}
			// A reply may retain the canonical locator in span while explicitly
			// supplying the final locator as surface_span. Use that supplied
			// scope only if the first quote is absent and the final quote unique.
			if strings.Index(text, exact) < 0 {
				if surface, ok := s["surface_span"].(map[string]any); ok {
					quote, quoted := surface["exact_text"].(string)
					_, start := surface["start_cp"].(float64)
					_, end := surface["end_cp"].(float64)
					_, oldStart := span["start_cp"].(float64)
					_, oldEnd := span["end_cp"].(float64)
					a := strings.Index(text, quote)
					if quoted && quote != "" && start && end && oldStart && oldEnd && a >= 0 && a == strings.LastIndex(text, quote) {
						span = map[string]any{"start_cp": surface["start_cp"], "end_cp": surface["end_cp"], "exact_text": quote}
						s["span"], exact = span, quote
					}
				}
			}
			a := strings.Index(text, exact)
			if a < 0 || a != strings.LastIndex(text, exact) {
				continue
			}
			// Preserve malformed explicitly typed fields for the ordinary admission
			// error; this projection changes only numerical coordinate arithmetic.
			if _, ok := span["start_cp"].(float64); !ok {
				continue
			}
			if _, ok := span["end_cp"].(float64); !ok {
				continue
			}
			start := len([]rune(text[:a]))
			span["start_cp"], span["end_cp"] = float64(start), float64(start+len([]rune(exact)))
		}
	}
	return value
}
