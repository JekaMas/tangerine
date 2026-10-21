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
		for _, id := range j["evidence_ids"].([]any) {
			if !evidence[id.(string)] {
				return nil, reviewInvalid("Use actual supplied evidence IDs only.")
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
		b, _ := json.Marshal(out["decisions"])
		m, issues, e := normalizeMapping(f.Record.Attempt["answer_text"].(string), f.Extraction, key, f.Resources.TaxonomyIDs, f.Resources.Evidence, f.Record.Attempt["task_components"].(map[string]any), b)
		if e != nil {
			return nil, e
		}
		out["admitted_mapping"] = map[string]any{"mapping": m, "issues": issues}
	}
	return out, nil
}
