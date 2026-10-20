package app

import (
	"encoding/json"
	"regexp"
	"sort"
	"strings"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

// mutationContent is the semantic half of the single new model-output admission.
// The shared provider adapter already normalized and schema-checked this reply.
func mutationContent(raw []byte, blueprint, clean, taxonomy map[string]any) (map[string]any, error) {
	var c map[string]any
	if e := json.Unmarshal(raw, &c); e != nil {
		return nil, e
	}
	if c["blueprint_id"] != blueprint["id"] || c["status"] != "candidate" || c["failure_reason"] != nil {
		return nil, &provider.OutputValidationError{Detail: "Use candidate status, the saved blueprint_id and null failure_reason for a successful mutation. Recipe examples are illustrations, not required source text."}
	}
	turns := c["utterances"].([]any)
	old := clean["utterances"].([]any)
	if len(turns) != len(old) {
		return nil, &provider.OutputValidationError{Detail: "Preserve every saved canonical turn in its original order."}
	}
	byTurn := map[string]map[string]any{}
	for i, v := range turns {
		u := v.(map[string]any)
		base := old[i].(map[string]any)
		for _, k := range []string{"id", "speaker_id", "canonical_text"} {
			if u[k] != base[k] {
				return nil, &provider.OutputValidationError{Detail: "Preserve canonical_turn_identity: id, speaker_id and canonical_text must equal the saved clean turn."}
			}
		}
		if strings.TrimSpace(u["surface_text"].(string)) == "" {
			return nil, &provider.OutputValidationError{Detail: "Surface text must be nonempty."}
		}
		byTurn[u["id"].(string)] = u
	}
	leaves := map[string]string{}
	for _, v := range taxonomy["entries"].([]any) {
		x := v.(map[string]any)
		leaves[x["id"].(string)] = x["domain"].(string)
	}
	units := c["planned_units"].([]any)
	ids := map[string]bool{}
	cover := map[string]bool{}
	scopes := map[string][][2]int{}
	counts := map[string]int{}
	trueErrors := 0
	familyEvents := map[string]bool{}
	obligations := map[string]bool{}
	for _, v := range units {
		u := v.(map[string]any)
		id := u["id"].(string)
		primary := u["primary_taxonomy_id"].(string)
		if ids[id] || leaves[primary] == "" || leaves[primary] != u["domain"] || map[string]float64{"minor": 1, "moderate": 2, "major": 3, "communication_breakdown": 4}[u["severity"].(string)] != u["weight"] {
			return nil, &provider.OutputValidationError{Detail: "Use unique unit IDs, registered selected primary categories/domains and severity weights minor=1/moderate=2/major=3/communication_breakdown=4."}
		}
		ids[id] = true
		primaryAccepted := false
		for _, k := range []string{"accepted_taxonomy_ids", "secondary_taxonomy_ids"} {
			for _, v := range u[k].([]any) {
				if leaves[v.(string)] == "" {
					return nil, &provider.OutputValidationError{Detail: "Accepted and secondary category IDs must be selected registered leaves."}
				}
				if k == "accepted_taxonomy_ids" && v == primary {
					primaryAccepted = true
				}
			}
		}
		if !primaryAccepted {
			return nil, &provider.OutputValidationError{Detail: "accepted_taxonomy_ids must include the primary category."}
		}
		if u["expected_judgment"] == "true_error" {
			trueErrors++
			familyEvents[u["domain"].(string)] = true
			obligation := mutationObligation(u)
			if obligations[obligation] {
				return nil, &provider.OutputValidationError{Detail: "Copied units or renamed correction options do not create another independent repair obligation. Keep one unit for the same event."}
			}
			obligations[obligation] = true
		}
		counts[primary+":"+u["expected_judgment"].(string)]++
		utterances := map[string]bool{}
		for _, v := range u["utterance_ids"].([]any) {
			if byTurn[v.(string)] == nil {
				return nil, &provider.OutputValidationError{Detail: "Unit utterance_ids must name saved turns."}
			}
			utterances[v.(string)] = true
		}
		changedScope := false
		spans := u["text_spans"].([]any)
		if len(spans) == 0 {
			return nil, &provider.OutputValidationError{Detail: "Each planned unit needs its final-surface text_spans."}
		}
		for _, v := range spans {
			x := v.(map[string]any)
			turn := x["utterance_id"].(string)
			span := x["span"].(map[string]any)
			if !utterances[turn] {
				return nil, &provider.OutputValidationError{Detail: "Each text span must belong to that unit’s utterance_ids."}
			}
			text := []rune(byTurn[turn]["surface_text"].(string))
			start, end := int(span["start_cp"].(float64)), int(span["end_cp"].(float64))
			if start > end || end > len(text) || string(text[start:end]) != span["exact_text"] {
				return nil, &provider.OutputValidationError{Detail: "text_spans offsets are Unicode codepoints in the final surface_text; exact_text must equal that slice. Do not use canonical deletion characters or recipe-example coordinates as surface spans."}
			}
			scopes[turn] = append(scopes[turn], [2]int{start, end})
			old := []rune(byTurn[turn]["canonical_text"].(string))
			if string(old) != string(text) {
				a, z := mutationDifference(old, text)
				if (a == z && start <= a && end >= a) || (start < z && end > a) {
					cover[turn] = true
					changedScope = true
				}
			}
		}
		r := u["realization"].(map[string]any)
		acoustic := r["mode"] == "acoustic_segmental" || r["mode"] == "acoustic_suprasegmental" || r["mode"] == "temporal_fluency"
		if u["expected_judgment"] == "true_error" && !acoustic && !changedScope {
			return nil, &provider.OutputValidationError{Detail: "A textual true_error must point to its actual changed surface scope."}
		}
		if r["observed_ipa"] != nil || r["observed_pace_wpm"] != nil || r["observed_pause_ms"] != nil || u["difficulty"] != "unrated" {
			return nil, &provider.OutputValidationError{Detail: "Observed IPA/pace/pause must stay null, and difficulty must be unrated before audio/attempt observations."}
		}

		corrections := map[string]bool{}
		for _, v := range u["corrections"].([]any) {
			x := v.(map[string]any)
			id := x["id"].(string)
			if corrections[id] {
				return nil, &provider.OutputValidationError{Detail: "Correction IDs must be unique within their unit."}
			}
			corrections[id] = true
			if u["expected_judgment"] == "true_error" && r["mode"] == "textual" && len(spans) == 1 && x["kind"] == "replace" && x["text"] == spans[0].(map[string]any)["span"].(map[string]any)["exact_text"] {
				return nil, &provider.OutputValidationError{Detail: "A textual replacement correction must change the heard error, not repeat its exact surface text. Set the canonical option text to a valid repair; the original wrong form is not a correction."}
			}
		}
	}
	for _, v := range turns {
		u := v.(map[string]any)
		if u["canonical_text"] != u["surface_text"] && !cover[u["id"].(string)] {
			return nil, &provider.OutputValidationError{Detail: "Every changed turn needs an affected planned unit."}
		}
		if u["canonical_text"] != u["surface_text"] && !mutationScopedChanges(u["canonical_text"].(string), u["surface_text"].(string), scopes[u["id"].(string)]) {
			return nil, &provider.OutputValidationError{Detail: "Every textual change must belong to the planned units' final-surface scopes. Keep all text outside those scopes unchanged, or include the complete affected scope in the key."}
		}
	}
	for _, v := range blueprint["targets"].([]any) {
		x := v.(map[string]any)
		n := counts[x["taxonomy_id"].(string)+":"+x["expected_judgment"].(string)]
		if n < int(x["min_count"].(float64)) || n > int(x["max_count"].(float64)) {
			return nil, &provider.OutputValidationError{Detail: "Preserve each advanced category/judgment min_count and max_count."}
		}
	}
	if r, ok := blueprint["exercise_request"].(map[string]any); ok {
		if n, ok := r["mutation_count"].(float64); ok && trueErrors != int(n) {
			return nil, &provider.OutputValidationError{Detail: "The number of true_error units must equal the requested mutation_count."}
		}
	}
	if r, ok := blueprint["exercise_request"].(map[string]any); ok {
		if n, explicit := r["mutation_count"].(float64); !explicit || n != 0 {
			if trueErrors == 0 {
				return nil, &provider.OutputValidationError{Detail: "Automatic mutation_count chooses a positive number of true errors. Only explicit zero requests an empty/control-only key."}
			}
			if families, ok := r["category_families"].([]any); ok {
				for _, v := range families {
					family := v.(string)
					covered := false
					for domain := range familyEvents {
						if mutationFamilyMatches([]string{family}, domain) {
							covered = true
							break
						}
					}
					if !covered {
						return nil, &provider.OutputValidationError{Detail: "Include at least one independent true-error event in every requested category family; broad pronunciation may use either subdomain. Only explicit mutation_count=0 overrides family coverage."}
					}
				}
			}
		}
	}

	ops, _ := c["acoustic_edits"].([]any)
	acousticUnits := map[string]map[string]any{}
	for _, v := range units {
		u := v.(map[string]any)
		mode := u["realization"].(map[string]any)["mode"]
		if mode == "acoustic_segmental" || mode == "acoustic_suprasegmental" || mode == "temporal_fluency" {
			acousticUnits[u["id"].(string)] = u
		}
	}
	coveredAcoustic := map[string]bool{}
	for _, v := range ops {
		x := v.(map[string]any)
		turn := byTurn[x["utterance_id"].(string)]
		scope := x["scope"].(map[string]any)
		start, end := int(scope["start"].(float64)), int(scope["end"].(float64))
		unitID := x["unit_id"].(string)
		if !ids[unitID] || acousticUnits[unitID] == nil || turn == nil || start >= end || end > len([]rune(turn["surface_text"].(string))) {
			return nil, &provider.OutputValidationError{Detail: "Acoustic edits must name a valid acoustic unit/turn and usable final-surface scope."}
		}
		linked := false
		for _, v := range acousticUnits[unitID]["text_spans"].([]any) {
			xspan := v.(map[string]any)
			span := xspan["span"].(map[string]any)
			if xspan["utterance_id"] == x["utterance_id"] && start >= int(span["start_cp"].(float64)) && end <= int(span["end_cp"].(float64)) {
				linked = true
			}
		}
		if !linked || !mutationAcousticParameters(x) {
			return nil, &provider.OutputValidationError{Detail: "Acoustic edits must stay within a text span of their own unit and supply the selected controller's operands: phone_pair needs both IPA strings, vowel_duration a positive duration_ratio, pitch_duration an explicit pitch/duration/gain cue, pause_insert pause_ms and vot_edit vot_ms. Pitch fractions increase within [0,1]."}
		}
		coveredAcoustic[unitID] = true
	}
	for id, u := range acousticUnits {
		if u["expected_judgment"] == "true_error" && !coveredAcoustic[id] {
			return nil, &provider.OutputValidationError{Detail: "Each true acoustic error needs a corresponding typed acoustic operation."}
		}
	}
	return c, nil
}

// Unscoped text is literal and unchanged. Declared scopes may replace arbitrary
// canonical text, including deletion at an empty surface boundary. This checks
// only newly returned content, without a second diff or stored-value audit.
func mutationScopedChanges(canonical, surface string, scopes [][2]int) bool {
	sort.Slice(scopes, func(i, j int) bool { return scopes[i][0] < scopes[j][0] })
	runes := []rune(surface)
	position := 0
	var pattern strings.Builder
	pattern.WriteString("(?s)\\A")
	for _, scope := range scopes {
		if scope[0] > position {
			pattern.WriteString(regexp.QuoteMeta(string(runes[position:scope[0]])))
		}
		pattern.WriteString(".*")
		if scope[1] > position {
			position = scope[1]
		}
	}
	pattern.WriteString(regexp.QuoteMeta(string(runes[position:])))
	pattern.WriteString("\\z")
	matched, _ := regexp.MatchString(pattern.String(), canonical)
	return matched
}

func mutationAcousticParameters(edit map[string]any) bool {
	p := edit["parameters"].(map[string]any)
	if n, ok := p["duration_ratio"].(float64); ok && n <= 0 {
		return false
	}
	previous := -1.0
	points := p["pitch_points"].([]any)
	for _, v := range points {
		fraction := v.(map[string]any)["fraction"].(float64)
		if fraction < 0 || fraction > 1 || fraction <= previous {
			return false
		}
		previous = fraction
	}
	switch edit["controller"] {
	case "phone_pair":
		return p["reference_ipa"] != nil && p["mutated_ipa"] != nil
	case "vowel_duration":
		return p["duration_ratio"] != nil
	case "pitch_duration":
		return len(points) > 0 || p["duration_ratio"] != nil || p["gain_db"] != nil
	case "pause_insert":
		return p["pause_ms"] != nil
	case "vot_edit":
		return p["vot_ms"] != nil
	}
	return false
}

func mutationDifference(old, surface []rune) (int, int) {
	start := 0
	for start < len(old) && start < len(surface) && old[start] == surface[start] {
		start++
	}
	a, b := len(old), len(surface)
	for a > start && b > start && old[a-1] == surface[b-1] {
		a--
		b--
	}
	return start, b
}

// A literal copy cannot become another event merely by changing routing IDs or
// explanatory prose. Different locations or repair actions remain independent.
func mutationObligation(unit map[string]any) string {
	repairs := []any{}
	for _, v := range unit["corrections"].([]any) {
		option := v.(map[string]any)
		repairs = append(repairs, map[string]any{"kind": option["kind"], "text": option["text"], "ipa": option["ipa"], "alternatives": option["approved_text_alternatives"]})
	}
	return lab.Hash(map[string]any{"category": unit["primary_taxonomy_id"], "spans": unit["text_spans"], "realization": unit["realization"], "repairs": repairs})
}
