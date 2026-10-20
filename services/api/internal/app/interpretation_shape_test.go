package app

import (
	"encoding/json"
	"testing"
)

func emptyShapeFixture(component any, supplied bool) (map[string]any, *CanonicalExtraction) {
	id := "claim1"
	c := CanonicalClaim{ID: id}
	if supplied {
		c.Explanations = []AnswerSpan{{0, 4, "rule"}}
	}
	return map[string]any{"decisions": []any{map[string]any{"claim_id": id, "explanation": component}}}, &CanonicalExtraction{Claims: []CanonicalClaim{c}}
}
func TestInterpretationEmptyArrayPositive(t *testing.T) {
	value, c := emptyShapeFixture([]any{}, false)
	root := normalizeInterpretationShape(value, c).(map[string]any)
	component := root["decisions"].([]any)[0].(map[string]any)["explanation"].(map[string]any)
	if component["supplied"] != false || component["status"] != "not_supplied" || component["option_id"] != nil || len(component["satisfied_proposition_ids"].([]any)) != 0 {
		t.Fatal(component)
	}
}
func TestInterpretationEmptyObjectPositive(t *testing.T) {
	value, c := emptyShapeFixture(map[string]any{}, false)
	root := normalizeInterpretationShape(value, c).(map[string]any)
	component := root["decisions"].([]any)[0].(map[string]any)["explanation"].(map[string]any)
	if len(component) != 8 || component["supplied"] != false || component["status"] != "not_supplied" {
		t.Fatal(component)
	}
}
func TestInterpretationPresentComponentNegative(t *testing.T) {
	value, c := emptyShapeFixture([]any{}, true)
	before, _ := json.Marshal(value["decisions"].([]any)[0].(map[string]any)["explanation"])
	normalized := normalizeInterpretationShape(value, c).(map[string]any)
	after, _ := json.Marshal(normalized["decisions"].([]any)[0].(map[string]any)["explanation"])
	if string(before) != string(after) {
		t.Fatal("invented assessment for supplied text")
	}
}
func TestInterpretationMeaningfulTupleNegative(t *testing.T) {
	value, c := emptyShapeFixture(map[string]any{"supplied": false, "option_id": "fabricated", "satisfied_proposition_ids": []any{"p1"}}, false)
	before, _ := json.Marshal(value["decisions"].([]any)[0].(map[string]any)["explanation"])
	normalized := normalizeInterpretationShape(value, c).(map[string]any)
	after, _ := json.Marshal(normalized["decisions"].([]any)[0].(map[string]any)["explanation"])
	if string(before) != string(after) {
		t.Fatal("meaningful wrong fields discarded")
	}
}

func TestInterpretationMissingNotePositive(t *testing.T) {
	for _, explicitNull := range []bool{false, true} {
		value, c := emptyShapeFixture(nil, false)
		decision := value["decisions"].([]any)[0].(map[string]any)
		if explicitNull {
			decision["note"] = nil
		}
		normalizeInterpretationShape(value, c)
		if decision["note"] != "" {
			t.Fatal("missing optional prose consumed repair", decision)
		}
	}
}
func TestInterpretationMeaningfulNoteNegative(t *testing.T) {
	for _, note := range []any{"Keep this context", 17, true} {
		value, c := emptyShapeFixture(nil, false)
		decision := value["decisions"].([]any)[0].(map[string]any)
		decision["note"] = note
		normalizeInterpretationShape(value, c)
		if decision["note"] != note {
			t.Fatal("existing prose or meaningful wrong type was erased", decision)
		}
	}
}

func TestInterpretationAbsentUncertaintyPositive(t *testing.T) {
	for _, status := range []string{"not_supplied", "unresolved", "accepted"} {
		value, c := emptyShapeFixture(map[string]any{"supplied": false, "status": status, "option_id": nil, "unresolved_reason": "insufficient_context", "satisfied_proposition_ids": []any{}, "violated_proposition_ids": []any{}, "support_evidence_ids": []any{}, "additional_assertions": []any{}}, false)
		result := normalizeInterpretationShape(value, c).(map[string]any)["decisions"].([]any)[0].(map[string]any)["explanation"].(map[string]any)
		if result["status"] != "not_supplied" || result["unresolved_reason"] != nil || result["supplied"] != false {
			t.Fatal("absent explanation labels consumed the answer's repair budget or invented credit", result)
		}
	}
}
func TestInterpretationPresentUncertaintyNegative(t *testing.T) {
	component := map[string]any{"supplied": true, "status": "unresolved", "option_id": nil, "unresolved_reason": "unsupported_rationale", "satisfied_proposition_ids": []any{}, "violated_proposition_ids": []any{}, "support_evidence_ids": []any{}, "additional_assertions": []any{map[string]any{"judgment": "unknown", "exact_text": "rule"}}}
	value, c := emptyShapeFixture(component, true)
	before, _ := json.Marshal(component)
	normalized := normalizeInterpretationShape(value, c).(map[string]any)
	after, _ := json.Marshal(normalized["decisions"].([]any)[0].(map[string]any)["explanation"])
	if string(before) != string(after) {
		t.Fatal("actual supplied uncertainty erased", string(after))
	}
}
