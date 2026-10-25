package app

import "strings"

// Project accepted saved values; no secondary metadata store or read validation.
func historyText(value any, limit int, ellipsisInside bool) any {
	text, _ := value.(string)
	text = strings.Join(strings.Fields(text), " ")
	if text == "" {
		return nil
	}
	cp := []rune(text)
	if len(cp) > limit {
		if ellipsisInside {
			limit--
		}
		text = string(cp[:limit]) + "…"
	}
	return text
}

func attemptHistorySummary(a, heard map[string]any, result any) map[string]any {
	title := historyText(heard["title"], 200, true)
	if title == nil {
		title = historyText(heard["topic"], 200, true)
	}
	return map[string]any{"id": a["attempt_id"], "case_version_id": a["case_version_id"], "state": a["state"], "started_at": a["started_at"], "submitted_at": a["submitted_at"], "result_id": result, "exercise_title": title, "answer_excerpt": historyText(a["answer_text"], 160, false)}
}
