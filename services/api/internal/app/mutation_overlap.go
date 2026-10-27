package app

import "tangerine.local/api/internal/provider"

// Overlap is a timed discourse event, not a textual replacement or an accent.
// Fresh model output is checked here once; saved manifests/plans are trusted.
func overlapIntents(c map[string]any) []any {
	v, _ := c["overlap_intents"].([]any)
	if v == nil {
		return []any{}
	}
	return v
}
func admitOverlapIntents(c map[string]any) error {
	turns, order := map[string]map[string]any{}, map[string]int{}
	for i, v := range c["utterances"].([]any) {
		u := v.(map[string]any)
		id := u["id"].(string)
		turns[id] = u
		order[id] = i
	}
	units := map[string]map[string]any{}
	for _, v := range c["planned_units"].([]any) {
		u := v.(map[string]any)
		units[u["id"].(string)] = u
	}
	seen := map[string]bool{}
	seenOther := map[string]bool{}
	fail := func() error {
		return &provider.OutputValidationError{Detail: "overlap_intents must bind one discourse.turn_taking unit to two different saved speakers, with the target turn before the interrupting turn, an exact nonempty target_scope in its final surface and explicit gains. Obstructive units are true_error; cooperative backchannels are acceptable. Include both utterance_ids and the masked target span in the unit. No textual caption stands in for simultaneous audio."}
	}
	for _, v := range overlapIntents(c) {
		x := v.(map[string]any)
		id := x["unit_id"].(string)
		a, b := turns[x["target_utterance_id"].(string)], turns[x["overlapping_utterance_id"].(string)]
		u := units[id]
		if seen[id] || seenOther[x["overlapping_utterance_id"].(string)] || a == nil || b == nil || u == nil || a["speaker_id"] == b["speaker_id"] || order[a["id"].(string)] >= order[b["id"].(string)] || u["primary_taxonomy_id"] != "discourse.turn_taking" || u["realization"].(map[string]any)["mode"] != "discourse_context" {
			return fail()
		}
		seen[id] = true
		seenOther[x["overlapping_utterance_id"].(string)] = true
		if x["kind"] == "obstructive" && u["expected_judgment"] != "true_error" || x["kind"] == "cooperative_backchannel" && u["expected_judgment"] != "acceptable" {
			return fail()
		}
		scope := x["target_scope"].(map[string]any)
		start, end := int(scope["start_cp"].(float64)), int(scope["end_cp"].(float64))
		text := []rune(a["surface_text"].(string))
		if start >= end || end > len(text) || string(text[start:end]) != scope["exact_text"] {
			return fail()
		}
		linked, memberA, memberB := false, false, false
		for _, id := range u["utterance_ids"].([]any) {
			memberA = memberA || id == a["id"]
			memberB = memberB || id == b["id"]
		}
		for _, v := range u["text_spans"].([]any) {
			r := v.(map[string]any)
			s := r["span"].(map[string]any)
			linked = linked || r["utterance_id"] == a["id"] && s["start_cp"].(float64) <= float64(start) && s["end_cp"].(float64) >= float64(end)
		}
		if !linked || !memberA || !memberB {
			return fail()
		}
	}
	return nil
}
