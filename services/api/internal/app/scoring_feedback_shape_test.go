package app

import (
	"encoding/json"
	"testing"
)

func TestScoringShapeMetadataPositive(t *testing.T) {
	item := map[string]any{"kind": "recommendation", "text": "New practice: The shop opens.", "unit_ids": []any{"u1"}}
	root := map[string]any{"items": []any{item}}
	normalizeFeedbackShape(root, "en")
	if root["language"] != "en" || item["grounding_status"] != "practice_recommendation" || len(item["decision_ids"].([]any)) != 0 {
		t.Fatal(root)
	}
}
func TestScoringShapePendingPositive(t *testing.T) {
	item := map[string]any{"kind": "pending", "text": "Meaning is uncertain."}
	normalizeFeedbackShape(map[string]any{"items": []any{item}}, "ru")
	if item["status"] != "needs_review" {
		t.Fatal(item)
	}
}
func TestScoringShapeMeaningNegative(t *testing.T) {
	item := map[string]any{"kind": "missed", "unit_ids": []any{"invented"}, "status": "wrong", "text": "actual prose"}
	normalizeFeedbackShape(map[string]any{"language": "ru", "items": []any{item}}, "en")
	if item["status"] != "wrong" || item["unit_ids"].([]any)[0] != "invented" || item["text"] != "actual prose" {
		t.Fatal(item)
	}
}
func TestScoringShapeNoFindingsNegative(t *testing.T) {
	root := map[string]any{}
	normalizeFeedbackShape(root, "en")
	if root["items"] != nil {
		t.Fatal("invented findings")
	}
}
func TestScoringResultScopedPracticePositive(t *testing.T) {
	root := map[string]any{"items": []any{map[string]any{"kind": "recommendation", "text": "New practice: The shop opens."}}}
	normalizeFeedbackShape(root, "en")
	_, e := admitFeedback(mustScoringJSON(root), AttemptRecord{Context: map[string]any{"requested_language": "en"}}, InterpretationResources{Key: map[string]any{"units": []any{}}, Rationales: []any{}}, SemanticMapping{}, map[string]any{"issues": []any{}, "score": map[string]any{"items": []any{}}})
	if e != nil {
		t.Fatal(e)
	}
}
func TestScoringUnscopedFindingNegative(t *testing.T) {
	root := map[string]any{"items": []any{map[string]any{"kind": "detected", "text": "An additional mistake was heard."}}}
	normalizeFeedbackShape(root, "en")
	_, e := admitFeedback(mustScoringJSON(root), AttemptRecord{Context: map[string]any{"requested_language": "en"}}, InterpretationResources{Key: map[string]any{"units": []any{}}, Rationales: []any{}}, SemanticMapping{}, map[string]any{"issues": []any{}, "score": map[string]any{"items": []any{}}})
	if e == nil {
		t.Fatal("unscoped recording assertion accepted")
	}
}
func mustScoringJSON(v any) []byte { b, _ := json.Marshal(v); return b }
