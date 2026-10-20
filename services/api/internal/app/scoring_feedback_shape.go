package app

// Complete harmless absent envelope metadata before the one output admission.
// Actual prose, subjects, references and supplied judgments are never invented.
func normalizeFeedbackShape(value any, language string) any {
	root, ok := value.(map[string]any)
	if !ok {
		return value
	}
	if root["schema_version"] == nil {
		root["schema_version"] = "2.0.0"
	}
	if root["language"] == nil {
		root["language"] = language
	}
	items, ok := root["items"].([]any)
	if !ok {
		return value
	}
	for _, v := range items {
		item, ok := v.(map[string]any)
		if !ok {
			continue
		}
		for _, field := range []string{"decision_ids", "unit_ids", "issue_ids", "rationale_ids"} {
			if item[field] == nil {
				item[field] = []any{}
			}
		}
		if item["grounding_status"] == nil {
			item["grounding_status"] = "llm_grounded"
			if item["kind"] == "recommendation" {
				item["grounding_status"] = "practice_recommendation"
			}
		}
		if item["status"] == nil {
			item["status"] = "final"
			if item["kind"] == "pending" {
				item["status"] = "needs_review"
			}
		}
	}
	return root
}
