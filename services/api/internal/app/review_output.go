package app

// This is the single admission of newly returned review semantics. Stored
// checkpoints are reused without repeating schema or content qualification.
import (
	"encoding/json"
	"strings"
	"tangerine.local/api/internal/provider"
)

func reviewInvalid(text string) error { return &provider.OutputValidationError{Detail: text} }
func normalizeReviewShape(value any, extraction *CanonicalExtraction) any {
	root, ok := value.(map[string]any)
	if !ok {
		return value
	}
	if root["schema_version"] == nil {
		root["schema_version"] = "2.0.0"
	}
	if root["resolution"] != "key_defect" && root["key_repair"] == nil {
		root["key_repair"] = nil
	}
	if repair, ok := root["key_repair"].(map[string]any); ok {
		if reason, _ := repair["reason"].(string); strings.TrimSpace(reason) == "" {
			repair["reason"] = root["reason"]
		}
		if units, ok := repair["proposed_units"].([]any); ok {
			for _, value := range units {
				if unit, ok := value.(map[string]any); ok {
					// These are projected from the actual saved key/audio, never
					// controlled by a copied model envelope. Raw output is retained.
					for _, field := range []string{"audio_intervals", "context_evidence", "source", "verification", "evidence_ids", "difficulty_evidence_ref"} {
						delete(unit, field)
					}
				}
			}
		}
	}
	if rows, ok := root["decisions"].([]any); ok {
		root["decisions"] = map[string]any{"schema_version": "1.0.0", "decisions": rows}
	}
	if decisions, ok := root["decisions"].(map[string]any); ok {
		if decisions["claim_id"] != nil {
			decisions = map[string]any{"schema_version": "1.0.0", "decisions": []any{decisions}}
		} else if decisions["decisions"] != nil && decisions["schema_version"] == nil {
			decisions["schema_version"] = "1.0.0"
		}
		root["decisions"] = normalizeInterpretationShape(decisions, extraction)
	}
	return root
}
func admitReview(raw []byte, r ReviewRun, f ReviewFrozen) (map[string]any, error) {
	var out map[string]any
	if e := json.Unmarshal(raw, &out); e != nil {
		return nil, e
	}
	if strings.TrimSpace(out["reason"].(string)) == "" {
		return nil, reviewInvalid("Give a contextual resolution reason.")
	}
	units := map[string]map[string]any{}
	for _, v := range f.Key["units"].([]any) {
		u := v.(map[string]any)
		units[u["id"].(string)] = u
	}
	evidence := map[string]bool{}
	for _, v := range f.Resources.Evidence {
		evidence[v.(map[string]any)["id"].(string)] = true
	}
	seen := map[string]bool{}
	for _, v := range out["unit_judgments"].([]any) {
		j := v.(map[string]any)
		id := j["unit_id"].(string)
		u := units[id]
		if u == nil || seen[id] || !f.Resources.TaxonomyIDs[j["taxonomy_id"].(string)] {
			return nil, reviewInvalid("Judge each actual base unit exactly once using registered taxonomy IDs.")
		}
		seen[id] = true
		textual := u["realization"].(map[string]any)["mode"] == "textual" || u["realization"].(map[string]any)["mode"] == "text"
		contextEvidence := map[string]bool{}
		if textual {
			if records, ok := u["context_evidence"].([]any); ok {
				for _, value := range records {
					if record, ok := value.(map[string]any); ok {
						if hash, ok := record["evidence_hash"].(string); ok && hash != "" {
							contextEvidence[hash] = true
						}
					}
				}
			}
		}
		for _, id := range j["evidence_ids"].([]any) {
			if !evidence[id.(string)] && !contextEvidence[id.(string)] {
				return nil, reviewInvalid("Use supplied evidence IDs, or this textual unit's actual embedded context evidence_hash; text is not an acoustic observation.")
			}
		}
		if u["realization"].(map[string]any)["mode"] != "textual" && u["realization"].(map[string]any)["mode"] != "text" && j["confirmation"] == "supported" && len(j["evidence_ids"].([]any)) == 0 {
			return nil, reviewInvalid("Without an actual acoustic observation, use inferred or unknown confirmation; text is not direct hearing.")
		}
	}
	if len(seen) != len(units) {
		return nil, reviewInvalid("Retain a judgment for every planned base unit and control.")
	}
	resolution := out["resolution"].(string)
	if r.Attempt == "" && out["decisions"] != nil {
		return nil, reviewInvalid("Case review has no listener answer decisions.")
	}
	if resolution == "mapping_defect" && (r.Attempt == "" || out["decisions"] == nil) {
		return nil, reviewInvalid("An answer mapping defect requires complete corrected evaluator decisions.")
	}
	if resolution == "key_defect" {
		if out["key_repair"] == nil {
			return nil, reviewInvalid("Return the complete key repair, not only a reason.")
		}
		if e := admitKeyRepair(f.Key, out["key_repair"].(map[string]any), f.Resources.TaxonomyIDs); e != nil {
			return nil, e
		}
		domains := map[string]any{}
		for _, v := range f.Resources.Taxonomy {
			row := v.(map[string]any)
			domains[row["id"].(string)] = row["reporting_domain"]
		}
		for _, v := range out["key_repair"].(map[string]any)["proposed_units"].([]any) {
			unit := v.(map[string]any)
			if domains[unit["primary_taxonomy_id"].(string)] != unit["domain"] {
				return nil, reviewInvalid("A repaired unit must use its registered primary category's scoring domain.")
			}
		}
	} else if out["key_repair"] != nil {
		return nil, reviewInvalid("Only key_defect can replace the key.")
	}
	if resolution == "insufficient_evidence" && out["decisions"] != nil {
		return nil, reviewInvalid("Unresolved evidence cannot supply authoritative replacement decisions.")
	}
	if out["decisions"] != nil {
		key := f.Resources.Key
		if resolution == "key_defect" {
			key = reviewClone(key)
			key["units"] = out["key_repair"].(map[string]any)["proposed_units"]
		}
		normalizeReviewRubricReferences(out["decisions"].(map[string]any), key)
		b, _ := json.Marshal(out["decisions"])
		m, issues, e := normalizeMapping(f.Record.Attempt["answer_text"].(string), f.Extraction, key, f.Resources.TaxonomyIDs, f.Resources.Evidence, f.Record.Attempt["task_components"].(map[string]any), b)
		if e != nil {
			return nil, e
		}
		out["admitted_mapping"] = map[string]any{"mapping": m, "issues": issues}
	}
	return out, nil
}

// An explicit source-quoted rejection can list its unmet required condition in
// the forbidden-ID field. Normalize that reference only; never invent a judgment
// or remove an unknown ID. The mapper still admits the actual source assertions.
func normalizeReviewRubricReferences(decisions, key map[string]any) {
	units := map[string]map[string]any{}
	for _, v := range key["units"].([]any) {
		u := v.(map[string]any)
		units[u["id"].(string)] = u
	}
	for _, v := range decisions["decisions"].([]any) {
		d := v.(map[string]any)
		id, _ := d["unit_id"].(string)
		unit := units[id]
		if unit == nil {
			continue
		}
		for _, name := range []string{"correction", "explanation"} {
			component, ok := d[name].(map[string]any)
			if !ok || component["status"] != "rejected" {
				continue
			}
			unsupported := false
			for _, v := range component["additional_assertions"].([]any) {
				a := v.(map[string]any)
				unsupported = unsupported || a["judgment"] == "unsupported" && a["exact_text"] != ""
			}
			if !unsupported {
				continue
			}
			required, forbidden := unit["rationale_required_propositions"], unit["rationale_forbidden_propositions"]
			if name == "correction" {
				required, forbidden = []any{}, []any{}
				for _, v := range unit["corrections"].([]any) {
					option := v.(map[string]any)
					if option["id"] == component["option_id"] {
						required, forbidden = option["required_propositions"], option["forbidden_propositions"]
						break
					}
				}
			}
			unmet, prohibited := map[string]bool{}, map[string]bool{}
			for _, v := range required.([]any) {
				unmet[v.(map[string]any)["id"].(string)] = true
			}
			for _, v := range forbidden.([]any) {
				prohibited[v.(map[string]any)["id"].(string)] = true
			}
			retained := []any{}
			for _, v := range component["violated_proposition_ids"].([]any) {
				id := v.(string)
				if !unmet[id] || prohibited[id] {
					retained = append(retained, id)
				}
			}
			component["violated_proposition_ids"] = retained
		}
	}
}
