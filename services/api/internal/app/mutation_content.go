package app

import (
	"encoding/json"
	"github.com/google/uuid"
	"go.yaml.in/yaml/v3"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

// MutationSelection projects the complete requested families/leaves from frozen
// source definitions. Corpus names inside recipes are metadata, never excerpts.
func mutationSelection(blueprint map[string]any, taxonomyBytes, recipeBytes, productionBytes []byte) (map[string]any, []any, []any, error) {
	var taxonomy map[string]any
	if e := yaml.Unmarshal(taxonomyBytes, &taxonomy); e != nil {
		return nil, nil, nil, e
	}
	var recipe, production map[string]any
	if e := json.Unmarshal(recipeBytes, &recipe); e != nil {
		return nil, nil, nil, e
	}
	if e := json.Unmarshal(productionBytes, &production); e != nil {
		return nil, nil, nil, e
	}
	requested := map[string]bool{}
	for _, v := range blueprint["targets"].([]any) {
		requested[v.(map[string]any)["taxonomy_id"].(string)] = true
	}
	families := []string{}
	if r, ok := blueprint["exercise_request"].(map[string]any); ok {
		for _, v := range r["category_families"].([]any) {
			families = append(families, v.(string))
		}
	}
	selected := func(id, domain string) bool {
		if len(requested) > 0 {
			return requested[id]
		}
		if len(families) == 0 {
			return true
		}
		for _, f := range families {
			if f == domain || strings.HasPrefix(domain, f+".") {
				return true
			}
		}
		return false
	}
	entries := []any{}
	ids := map[string]bool{}
	for _, v := range taxonomy["items"].([]any) {
		leaf := v.(map[string]any)
		id := leaf["id"].(string)
		domain := leaf["reporting_domain"].(string)
		if !selected(id, domain) {
			continue
		}
		ids[id] = true
		entries = append(entries, map[string]any{"id": id, "domain": domain, "definition": leaf["definition"], "inclusion": leaf["inclusion_criteria"], "exclusion": leaf["exclusion_criteria"], "correction_requirements": []any{leaf["correction_contract"]}, "verification_requirements": []any{leaf["verification_route"]}})
	}
	if len(entries) == 0 {
		return nil, nil, nil, ErrConflict
	}
	recipes := []any{}
	producers := []any{}
	for _, v := range recipe["recipes"].([]any) {
		if ids[v.(map[string]any)["taxonomy_id"].(string)] {
			recipes = append(recipes, v)
		}
	}
	for _, v := range production["rows"].([]any) {
		if ids[v.(map[string]any)["taxonomy_id"].(string)] {
			producers = append(producers, v)
		}
	}
	rules := []any{}
	if v, ok := taxonomy["judgment_rules"].([]any); ok {
		rules = v
	}
	return map[string]any{"taxonomy_sha256": contracts.Digest(taxonomyBytes), "entries": entries, "judgment_rules": rules}, recipes, producers, nil
}

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
	counts := map[string]int{}
	trueErrors := 0
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
		coveredAcoustic[unitID] = true
	}
	for id, u := range acousticUnits {
		if u["expected_judgment"] == "true_error" && !coveredAcoustic[id] {
			return nil, &provider.OutputValidationError{Detail: "Each true acoustic error needs a corresponding typed acoustic operation."}
		}
	}
	return c, nil
}

// mutationManifest derives one explicit composite edit per changed turn. This
// deterministic compiler records the accepted LLM plan; it never creates errors.
func mutationManifest(c map[string]any, canonicalID, canonicalSHA, mutatedID, mutatedSHA, recipeSHA string, recipes []any, seed any) map[string]any {
	edits := []any{}
	intents := []any{}
	recipeIDs := []any{}
	seenRecipes := map[string]bool{}
	canonicalWords, surfaceWords := 0, 0
	for _, v := range c["utterances"].([]any) {
		u := v.(map[string]any)
		old, new := []rune(u["canonical_text"].(string)), []rune(u["surface_text"].(string))
		canonicalWords += len(strings.Fields(string(old)))
		surfaceWords += len(strings.Fields(string(new)))
		if string(old) == string(new) {
			continue
		}
		start := 0
		for start < len(old) && start < len(new) && old[start] == new[start] {
			start++
		}
		oldEnd, newEnd := len(old), len(new)
		for oldEnd > start && newEnd > start && old[oldEnd-1] == new[newEnd-1] {
			oldEnd--
			newEnd--
		}
		unitIDs := []any{}
		for _, v := range c["planned_units"].([]any) {
			unit := v.(map[string]any)
			for _, v := range unit["text_spans"].([]any) {
				if v.(map[string]any)["utterance_id"] == u["id"] {
					unitIDs = append(unitIDs, unit["id"])
					break
				}
			}
		}
		edits = append(edits, map[string]any{"utterance_id": u["id"], "start_cp": start, "end_cp": oldEnd, "original_text": string(old[start:oldEnd]), "replacement_text": string(new[start:newEnd]), "order": 0, "unit_ids": unitIDs})
	}
	for _, v := range c["planned_units"].([]any) {
		unit := v.(map[string]any)
		id := unit["primary_taxonomy_id"].(string)
		if !seenRecipes[id] {
			recipeIDs = append(recipeIDs, id)
			seenRecipes[id] = true
		}
		r := unit["realization"].(map[string]any)
		if r["mode"] == "acoustic_segmental" || r["mode"] == "acoustic_suprasegmental" || r["mode"] == "temporal_fluency" {
			for _, v := range unit["text_spans"].([]any) {
				span := v.(map[string]any)
				scope := span["span"].(map[string]any)
				intents = append(intents, map[string]any{"unit_id": unit["id"], "utterance_id": span["utterance_id"], "surface_start_cp": scope["start_cp"], "surface_end_cp": scope["end_cp"], "realization": r})
			}
		}
	}
	m := map[string]any{"schema_version": "2.0.0", "id": uuid.NewString(), "canonical_asset_id": canonicalID, "canonical_sha256": canonicalSHA, "mutated_asset_id": mutatedID, "mutated_sha256": mutatedSHA, "recipe_registry_sha256": recipeSHA, "recipe_ids": recipeIDs, "seed": seed, "method_version": "canonical-composite-codepoint-v1", "canonical_word_count": canonicalWords, "surface_word_count": surfaceWords, "edits": edits, "acoustic_intents": intents, "acoustic_edits": mutationAcousticEdits(c), "planned_units": c["planned_units"]}
	m["manifest_sha256"] = lab.Hash(m)
	return m
}

func mutationAcousticEdits(c map[string]any) []any {
	if v, ok := c["acoustic_edits"].([]any); ok {
		return v
	}
	return []any{}
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
