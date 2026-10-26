package app

// Normalize source-confirmed absence and missing optional prose. No proposal,
// assertion, identifier or judgment for supplied text is created or discarded.
func normalizeInterpretationShape(value any, extraction *CanonicalExtraction) any {
	root, ok := value.(map[string]any)
	if !ok {
		return value
	}
	if extraction == nil {
		// These aliases describe the same source codepoint coordinates. Normalize
		// their spelling before the existing schema check, without selecting a
		// location, changing an explicit coordinate or creating a relation.
		relations, _ := root["relations"].([]any)
		for _, raw := range relations {
			relation, _ := raw.(map[string]any)
			span, _ := relation["evidence_span"].(map[string]any)
			for _, name := range []string{"start", "end"} {
				if _, exists := span[name]; !exists {
					if coordinate, exists := span[name+"_cp"]; exists {
						span[name] = coordinate
					}
				}
			}
		}
		return value
	}
	rows, ok := root["decisions"].([]any)
	if !ok {
		return value
	}
	byID := map[string]CanonicalClaim{}
	for _, claim := range extraction.Claims {
		byID[claim.ID] = claim
	}
	for _, raw := range rows {
		decision, ok := raw.(map[string]any)
		if !ok {
			continue
		}
		id, _ := decision["claim_id"].(string)
		claim, known := byID[id]
		if !known {
			continue
		}
		if note, exists := decision["note"]; !exists || note == nil {
			decision["note"] = ""
		}
		for _, component := range []struct {
			name  string
			spans []AnswerSpan
		}{{"correction", claim.Corrections}, {"explanation", claim.Explanations}} {
			if len(component.spans) > 0 {
				continue
			}
			current := decision[component.name]
			empty := current == nil
			switch v := current.(type) {
			case []any:
				empty = len(v) == 0
			case map[string]any:
				empty = true
				for key, field := range v {
					switch key {
					case "supplied":
						empty = empty && field == false
					case "option_id":
						empty = empty && field == nil
					case "status", "unresolved_reason":
						// These labels have no consumer when source confirms absence and
						// no supplied flag, option, evidence or substantive findings exist.
						// Their original values remain in the raw provider diagnostic.
					case "satisfied_proposition_ids", "violated_proposition_ids", "support_evidence_ids", "additional_assertions":
						list, ok := field.([]any)
						empty = empty && ok && len(list) == 0
					default: /* Harmless additive fields remain in the retained raw response. */
					}
				}
			}
			if empty {
				decision[component.name] = map[string]any{"supplied": false, "option_id": nil, "satisfied_proposition_ids": []any{}, "violated_proposition_ids": []any{}, "status": "not_supplied", "support_evidence_ids": []any{}, "unresolved_reason": nil, "additional_assertions": []any{}}
			}
		}
	}
	return value
}
