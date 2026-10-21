package app

// Pure same-audio projection. Identity allocation is injected once and the whole
// projection is checkpointed before any new key/result publication.
import (
	"encoding/json"
	"github.com/google/uuid"
	"reflect"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
)

func admitKeyRepair(key, p map[string]any, tax map[string]bool) error {
	if p["base_case_sha256"] != key["case_sha256"] || p["audio_sha256"] != key["audio"].(map[string]any)["sha256"] {
		return reviewInvalid("Repair only the exact frozen key and heard audio.")
	}
	old := map[string]bool{}
	for _, v := range key["units"].([]any) {
		old[v.(map[string]any)["id"].(string)] = true
	}
	next := map[string]bool{}
	turns := map[string]map[string]any{}
	for _, v := range key["utterances"].([]any) {
		u := v.(map[string]any)
		turns[u["id"].(string)] = u
	}
	for _, v := range p["proposed_units"].([]any) {
		u := v.(map[string]any)
		id := u["id"].(string)
		if next[id] || !tax[u["primary_taxonomy_id"].(string)] {
			return reviewInvalid("Use distinct unit IDs and actual registered categories.")
		}
		next[id] = true
		if map[string]float64{"minor": 1, "moderate": 2, "major": 3, "communication_breakdown": 4}[u["severity"].(string)] != u["weight"] {
			return reviewInvalid("Use the fixed severity weights: minor=1, moderate=2, major=3, communication_breakdown=4.")
		}
		for _, field := range []string{"accepted_taxonomy_ids", "secondary_taxonomy_ids"} {
			for _, cat := range u[field].([]any) {
				if !tax[cat.(string)] {
					return reviewInvalid("Accepted and secondary categories must be registered.")
				}
			}
		}
		for _, id := range u["utterance_ids"].([]any) {
			if turns[id.(string)] == nil {
				return reviewInvalid("A repaired unit must reference the unchanged heard utterances.")
			}
		}
		for _, v := range u["text_spans"].([]any) {
			scope := v.(map[string]any)
			turn := turns[scope["utterance_id"].(string)]
			if turn == nil {
				return reviewInvalid("Unknown repaired text scope.")
			}
			span := scope["span"].(map[string]any)
			a, b := int(span["start_cp"].(float64)), int(span["end_cp"].(float64))
			text := []rune(turn["surface_text"].(string))
			if a < 0 || b < a || b > len(text) || string(text[a:b]) != span["exact_text"] {
				return reviewInvalid("Preserve exact original surface scopes; key repair does not change the recording.")
			}
		}
	}
	before, after := map[string]bool{}, map[string]bool{}
	for _, v := range p["correspondence_relations"].([]any) {
		r := v.(map[string]any)
		a, b := r["old_unit_ids"].([]any), r["new_unit_ids"].([]any)
		valid := false
		switch r["kind"] {
		case "same":
			valid = len(a) == 1 && len(b) == 1
		case "added":
			valid = len(a) == 0 && len(b) == 1
		case "removed":
			valid = len(a) == 1 && len(b) == 0
		case "split":
			valid = len(a) == 1 && len(b) > 1
		case "merge":
			valid = len(a) > 1 && len(b) == 1
		}
		if !valid {
			return reviewInvalid("Use explicit same/added/removed/split/merge cardinalities.")
		}
		for _, id := range a {
			if !old[id.(string)] || before[id.(string)] {
				return reviewInvalid("Every old unit must occur in exactly one correspondence.")
			}
			before[id.(string)] = true
		}
		for _, id := range b {
			if !next[id.(string)] || after[id.(string)] {
				return reviewInvalid("Every proposed unit must occur in exactly one correspondence.")
			}
			after[id.(string)] = true
		}
	}
	if len(before) != len(old) || len(after) != len(next) {
		return reviewInvalid("Correspondence must cover the complete old and proposed keys.")
	}
	return nil
}
func remapReviewIDs(value any, ids map[string]string) any {
	switch v := value.(type) {
	case map[string]any:
		out := map[string]any{}
		for k, x := range v {
			if k == "id" || k == "unit_id" || k == "option_id" || strings.HasSuffix(k, "_ids") {
				out[k] = remapReviewReference(x, ids)
			} else {
				out[k] = remapReviewIDs(x, ids)
			}
		}
		return out
	case []any:
		out := []any{}
		for _, x := range v {
			out = append(out, remapReviewIDs(x, ids))
		}
		return out
	}
	return value
}
func remapReviewReference(v any, ids map[string]string) any {
	if s, ok := v.(string); ok {
		if n, ok := ids[s]; ok {
			return n
		}
	}
	if a, ok := v.([]any); ok {
		b := []any{}
		for _, x := range a {
			b = append(b, remapReviewReference(x, ids))
		}
		return b
	}
	return remapReviewIDs(v, ids)
}
func projectReviewKey(key, p map[string]any, review string, allocate func() string) (ReviewProjection, error) {
	out := ReviewProjection{IDs: map[string]string{}, Rationales: []map[string]any{}}
	retained := map[string]bool{}
	var collect func(any, bool)
	collect = func(value any, old bool) {
		switch v := value.(type) {
		case map[string]any:
			if id, ok := v["id"].(string); ok {
				if old {
					retained[id] = true
				} else if !retained[id] && out.IDs[id] == "" {
					out.IDs[id] = allocate()
				}
			}
			for _, x := range v {
				collect(x, old)
			}
		case []any:
			for _, x := range v {
				collect(x, old)
			}
		}
	}
	collect(key["units"], true)
	collect(p["proposed_units"], false)
	next := reviewClone(key)
	next["case_version_id"] = allocate()
	next["review_decisions"] = []any{}
	next["status"] = "published"
	oldUnits := map[string]map[string]any{}
	for _, v := range key["units"].([]any) {
		u := v.(map[string]any)
		oldUnits[u["id"].(string)] = u
	}
	turns := map[string]map[string]any{}
	for _, v := range key["utterances"].([]any) {
		u := v.(map[string]any)
		turns[u["id"].(string)] = u
	}
	units := []any{}
	for _, v := range p["proposed_units"].([]any) {
		original := v.(map[string]any)
		u := remapReviewIDs(reviewClone(original), out.IDs).(map[string]any)
		old := oldUnits[original["id"].(string)]
		intervals := []any{}
		for _, id := range original["utterance_ids"].([]any) {
			intervals = append(intervals, turns[id.(string)]["audio_interval"])
		}
		u["audio_intervals"] = intervals
		u["context_evidence"] = []any{}
		u["evidence_ids"] = []any{}
		u["verification"] = "candidate"
		u["difficulty"] = "unrated"
		u["difficulty_evidence_ref"] = nil
		if old != nil {
			for _, k := range []string{"context_evidence", "evidence_ids", "verification", "source"} {
				u[k] = old[k]
			}
			same := true
			for _, k := range []string{"primary_taxonomy_id", "expected_judgment", "text_spans", "realization", "corrections", "correction_eligible"} {
				same = same && reflect.DeepEqual(old[k], original[k])
			}
			if same {
				for _, k := range []string{"audio_intervals", "difficulty", "difficulty_evidence_ref"} {
					u[k] = old[k]
				}
			}
		} else {
			u["source"] = reviewUnitSource(key, original)
		}
		units = append(units, u)
		required, forbidden := []any{}, []any{}
		for _, v := range u["rationale_required_propositions"].([]any) {
			required = append(required, v.(map[string]any)["id"])
		}
		for _, v := range u["rationale_forbidden_propositions"].([]any) {
			forbidden = append(forbidden, v.(map[string]any)["id"])
		}
		out.Rationales = append(out.Rationales, map[string]any{"schema_version": "2.0.0", "id": allocate(), "case_version_id": next["case_version_id"], "unit_id": u["id"], "language": "en", "text": u["rationale"], "required_proposition_ids": required, "forbidden_proposition_ids": forbidden, "evidence_ids": u["evidence_ids"], "review_decision_ids": []any{review}, "text_sha256": contracts.Digest([]byte(u["rationale"].(string)))})
	}
	next["units"] = units
	content := map[string]any{}
	for _, k := range []string{"public_context", "variety_policy", "audio", "speakers", "utterances", "units", "taxonomy_version", "verification_policy_version"} {
		content[k] = next[k]
	}
	next["case_sha256"] = lab.Hash(content)
	out.Key = next
	out.Correspondence = map[string]any{"schema_version": "2.0.0", "id": allocate(), "old_case_version_id": key["case_version_id"], "new_case_version_id": next["case_version_id"], "audio_sha256": key["audio"].(map[string]any)["sha256"], "relations": remapReviewReference(p["correspondence_relations"], out.IDs), "review_decision_ids": []any{review}}
	return out, nil
}
func allocateReviewID() string { return uuid.NewString() }
func reviewBytes(v any) []byte { b, _ := json.Marshal(v); return b }

// A new machine finding does not change the media's native source or its terms.
// Existing same-utterance metadata is authoritative; the machine observation
// itself is identified by the appended review and its actual provider receipts.
func reviewUnitSource(key, unit map[string]any) map[string]any {
	wanted := map[string]bool{}
	for _, id := range unit["utterance_ids"].([]any) {
		wanted[id.(string)] = true
	}
	for _, v := range key["units"].([]any) {
		old := v.(map[string]any)
		for _, id := range old["utterance_ids"].([]any) {
			if wanted[id.(string)] {
				return reviewClone(old["source"])
			}
		}
	}
	return map[string]any{"source_id": key["audio"].(map[string]any)["source_profile_id"], "source_record_id": nil, "rights_approval_id": nil, "uses": []any{}, "status": "pending", "licence_evidence_hash": nil}
}
