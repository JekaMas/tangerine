package app

import (
	"github.com/google/uuid"
	"strings"
	"tangerine.local/api/internal/lab"
)

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
	if len(overlapIntents(c)) > 0 {
		m["overlap_intents"] = overlapIntents(c)
	}
	m["manifest_sha256"] = lab.Hash(m)
	return m
}

func mutationAcousticEdits(c map[string]any) []any {
	if v, ok := c["acoustic_edits"].([]any); ok {
		return v
	}
	return []any{}
}
