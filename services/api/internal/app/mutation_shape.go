package app

import "strings"

// Omitted empty restrictions impose no additional condition. A sole correction
// is the unambiguous preferred option. Do not choose among alternatives, invent
// propositions, replace explicit flags or coerce malformed supplied values.
func normalizeMutationOutput(value any) any {
	root, ok := value.(map[string]any)
	if !ok {
		return value
	}
	rows, _ := root["planned_units"].([]any)
	for _, v := range rows {
		row, ok := v.(map[string]any)
		if !ok {
			continue
		}
		if _, exists := row["rationale_forbidden_propositions"]; !exists {
			row["rationale_forbidden_propositions"] = []any{}
		}
		if _, exists := row["utterance_ids"]; !exists {
			if spans, ok := row["text_spans"].([]any); ok && len(spans) > 0 {
				ids := []any{}
				seen := map[string]bool{}
				for _, value := range spans {
					span, ok := value.(map[string]any)
					if !ok {
						ids = nil
						break
					}
					id, ok := span["utterance_id"].(string)
					if !ok || id == "" {
						ids = nil
						break
					}
					if !seen[id] {
						seen[id] = true
						ids = append(ids, id)
					}
				}
				if len(ids) > 0 {
					row["utterance_ids"] = ids
				}
			}
		}
		// The display rationale can repeat the already supplied explanation
		// propositions verbatim. This supplies no new linguistic judgment.
		if _, exists := row["rationale"]; !exists {
			if propositions, ok := row["rationale_required_propositions"].([]any); ok && len(propositions) > 0 {
				texts := []string{}
				for _, value := range propositions {
					proposition, ok := value.(map[string]any)
					if !ok {
						texts = nil
						break
					}
					text, ok := proposition["description"].(string)
					if !ok || text == "" {
						texts = nil
						break
					}
					texts = append(texts, text)
				}
				if len(texts) == len(propositions) {
					row["rationale"] = strings.Join(texts, "\n")
				}
			}
		}
		corrections, _ := row["corrections"].([]any)
		if len(corrections) == 1 {
			if option, ok := corrections[0].(map[string]any); ok {
				if _, exists := option["canonical"]; !exists {
					option["canonical"] = true
				}
			}
		}
	}
	return normalizeMutationLocators(value)
}
