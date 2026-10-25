package app

import (
	"fmt"
	"tangerine.local/api/internal/provider"
)

// Request settings and new-output admission belong here. Accepted ledgers are
// reused by storage, rendering and scoring without a second validation pass.
func recurringProfiles(blueprint map[string]any) map[int]map[string]any {
	profiles := map[int]map[string]any{}
	request, _ := blueprint["exercise_request"].(map[string]any)
	if request["mutation_count"] == float64(0) {
		return profiles
	}
	rows, _ := request["recurring_errors"].([]any)
	for _, value := range rows {
		row := value.(map[string]any)
		profiles[int(row["speaker_number"].(float64))] = row
	}
	return profiles
}

func admitRecurringRequest(request map[string]any, speakerCount int) error {
	rows, _ := request["recurring_errors"].([]any)
	seen := map[int]bool{}
	for _, value := range rows {
		row := value.(map[string]any)
		number := int(row["speaker_number"].(float64))
		if number > speakerCount || seen[number] {
			return fmt.Errorf("%w: recurring patterns need distinct active speaker numbers", ErrConflict)
		}
		seen[number] = true
	}
	if n, ok := request["mutation_count"].(float64); ok && n > 0 && int(n) < len(rows) {
		return fmt.Errorf("%w: the exact count must include one recurring pattern per enabled speaker, or use zero", ErrConflict)
	}
	return nil
}

func recurringQuota(percent, opportunities int) int {
	return max(1, min(opportunities, (percent*opportunities+50)/100))
}

func literalRecurringSpan(value, turn map[string]any, field string) (int, int, bool) {
	a, b := int(value["start_cp"].(float64)), int(value["end_cp"].(float64))
	text := []rune(turn[field].(string))
	return a, b, a >= 0 && a <= b && b <= len(text) && string(text[a:b]) == value["exact_text"]
}

func admitRecurringPatterns(candidate, blueprint map[string]any) error {
	fail := func(detail string) error { return &provider.OutputValidationError{Detail: detail} }
	profiles := recurringProfiles(blueprint)
	turns := map[string]map[string]any{}
	for _, value := range candidate["utterances"].([]any) {
		turn := value.(map[string]any)
		turns[turn["id"].(string)] = turn
	}
	seen := map[int]bool{}
	for _, value := range candidate["planned_units"].([]any) {
		unit := value.(map[string]any)
		recurrence, ok := unit["recurrence"].(map[string]any)
		if !ok {
			continue
		}
		number := int(recurrence["speaker_number"].(float64))
		profile := profiles[number]
		if profile == nil || seen[number] || unit["expected_judgment"] != "true_error" || recurrence["target_percent"] != profile["target_percent"] {
			return fail("Use exactly one true recurring unit per enabled speaker, its requested target_percent, and no unsolicited recurring groups. Explicit zero has no recurring units.")
		}
		seen[number] = true
		speaker := blueprint["speakers"].([]any)[number-1].(map[string]any)["id"]
		rows := recurrence["opportunities"].([]any)
		if len(rows) < 2 {
			return fail("A recurring rule needs at least two actual eligible contexts; include correct exceptions as well as mutations.")
		}
		canonical := map[string][][2]int{}
		matched := map[int]bool{}
		changed := 0
		for _, value := range rows {
			row := value.(map[string]any)
			id := row["utterance_id"].(string)
			turn := turns[id]
			if turn == nil || turn["speaker_id"] != speaker {
				return fail("Every recurring opportunity must belong to its selected frozen speaker; other speakers are not in this denominator.")
			}
			old, surface := row["canonical_span"].(map[string]any), row["surface_span"].(map[string]any)
			a, b, valid := literalRecurringSpan(old, turn, "canonical_text")
			c, d, validSurface := literalRecurringSpan(surface, turn, "surface_text")
			if !valid || !validSurface || a == b {
				return fail("Recurring canonical/surface spans must quote their actual saved words with Unicode codepoint coordinates.")
			}
			for _, prior := range canonical[id] {
				if a < prior[1] && b > prior[0] {
					return fail("Duplicated or overlapping canonical contexts cannot inflate the recurring denominator.")
				}
			}
			canonical[id] = append(canonical[id], [2]int{a, b})
			mutated := row["mutated"] == true
			acoustic := false
			for _, value := range mutationAcousticEdits(candidate) {
				edit := value.(map[string]any)
				scope := edit["scope"].(map[string]any)
				x, y := int(scope["start"].(float64)), int(scope["end"].(float64))
				if edit["utterance_id"] != id || x >= d || y <= c {
					continue
				}
				if !mutated {
					return fail("A correct recurring exception cannot also receive an overlapping acoustic mutation.")
				}
				if edit["unit_id"] == unit["id"] && x >= c && y <= d {
					acoustic = true
				}
			}
			if !mutated {
				if old["exact_text"] != surface["exact_text"] {
					return fail("A correct recurring exception must retain its original correct wording.")
				}
				continue
			}
			changed++
			if old["exact_text"] == surface["exact_text"] && !acoustic {
				return fail("Each recurring mutation must actually change its wording or have its own typed acoustic operation.")
			}
			found := false
			for index, value := range unit["text_spans"].([]any) {
				span := value.(map[string]any)
				text := span["span"].(map[string]any)
				if span["utterance_id"] == id && text["start_cp"] == surface["start_cp"] && text["end_cp"] == surface["end_cp"] && text["exact_text"] == surface["exact_text"] && !matched[index] {
					matched[index], found = true, true
					break
				}
			}
			if !found {
				return fail("Every changed recurring opportunity must name its own exact final-surface unit text span.")
			}
		}
		if changed != recurringQuota(int(profile["target_percent"].(float64)), len(rows)) || len(matched) != len(unit["text_spans"].([]any)) {
			return fail("Recurring changed opportunities must equal floor((target_percent*N+50)/100), clamped to1..N, and exactly cover the unit text_spans; include unchanged eligible contexts in N.")
		}
	}
	if len(seen) != len(profiles) {
		return fail("Create one recurring true-error group for every enabled speaker; the same category alone does not define a recurring rule.")
	}
	return nil
}

func recurringSummary(unit map[string]any) map[string]any {
	r, ok := unit["recurrence"].(map[string]any)
	if !ok {
		return nil
	}
	rows := r["opportunities"].([]any)
	changed := 0
	correct := []any{}
	for _, value := range rows {
		row := value.(map[string]any)
		if row["mutated"] == true {
			changed++
		} else {
			correct = append(correct, row["surface_span"].(map[string]any)["exact_text"])
		}
	}
	return map[string]any{"speaker_number": r["speaker_number"], "rule": r["rule"], "target_percent": r["target_percent"], "opportunity_count": len(rows), "mutation_count": changed, "realized_percent_display": fmt.Sprintf("%.1f", 100*float64(changed)/float64(len(rows))), "correct_examples": correct}
}
