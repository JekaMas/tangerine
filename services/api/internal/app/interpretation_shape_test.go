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
