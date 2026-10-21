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

// Literal counterexample: one truthful comment covers the finding, correction
// and optional reason. Separate cards do not establish semantic correctness.
func combinedFeedbackFixture() (map[string]any, AttemptRecord, InterpretationResources, SemanticMapping, map[string]any) {
	root := map[string]any{"items": []any{
		map[string]any{"kind": "detected", "text": "Use opens: the cafe is singular. Your correction and reason are correct.", "unit_ids": []any{"e1"}, "decision_ids": []any{"c1"}},
		map[string]any{"kind": "recommendation", "text": "New practice: The shop opens at nine."},
	}}
	normalizeFeedbackShape(root, "en")
	mapping := SemanticMapping{Groups: []SemanticGroup{{Representative: "c1"}}}
	mapping.Groups[0].Correction.Supplied = true
	mapping.Groups[0].Explanation.Supplied = true
	mapping.Decisions = append(mapping.Decisions, SemanticDecision{Claim: "c1"})
	return root, AttemptRecord{Context: map[string]any{"requested_language": "en"}}, InterpretationResources{Key: map[string]any{"units": []any{map[string]any{"id": "e1"}}}, Rationales: []any{}}, mapping, map[string]any{"issues": []any{}, "score": map[string]any{"items": []any{map[string]any{"kind": "detected", "unit_id": "e1"}}}}
}
func TestScoringCombinedCommentPositive(t *testing.T) {
	root, record, resources, mapping, result := combinedFeedbackFixture()
	if _, e := admitFeedback(mustScoringJSON(root), record, resources, mapping, result); e != nil {
		t.Fatal(e)
	}
}
func TestScoringMissingFactualCommentNegative(t *testing.T) {
	root, record, resources, mapping, result := combinedFeedbackFixture()
	root["items"] = root["items"].([]any)[1:]
	if _, e := admitFeedback(mustScoringJSON(root), record, resources, mapping, result); e == nil {
		t.Fatal("practice alone covered no factual finding")
	}
}

func offkeyFeedbackFixture() (map[string]any, AttemptRecord, InterpretationResources, SemanticMapping, map[string]any) {
	root, record, resources, mapping, result := combinedFeedbackFixture()
	resources.Key["units"] = []any{}
	finding := root["items"].([]any)[0].(map[string]any)
	finding["kind"] = "false_positive"
	finding["unit_ids"] = []any{}
	finding["text"] = "The claimed mistake is not present. Your proposed change is unnecessary; the heard form is acceptable."
	mapping.Groups[0].Explanation.Supplied = false
	result["score"].(map[string]any)["items"] = []any{map[string]any{"kind": "false_positive", "unit_id": "", "decision_ids": []any{"c1"}}}
	return root, record, resources, mapping, result
}
func TestScoringOffkeyCombinedPositive(t *testing.T) {
	root, record, resources, mapping, result := offkeyFeedbackFixture()
	if _, e := admitFeedback(mustScoringJSON(root), record, resources, mapping, result); e != nil {
		t.Fatal(e)
	}
}
func TestScoringOffkeyMissingNegative(t *testing.T) {
	root, record, resources, mapping, result := offkeyFeedbackFixture()
	mapping.Groups = nil // Pure detection assertion with no repair or reason.
	root["items"] = root["items"].([]any)[1:]
	if _, e := admitFeedback(mustScoringJSON(root), record, resources, mapping, result); e == nil {
		t.Fatal("unmapped false positive omitted from feedback")
	}
}

func TestScoringFeedbackProposalPositive(t *testing.T) {
	claim := CanonicalClaim{ID: "c1", Group: "c1", Active: true, ExtractedClause: ExtractedClause{Span: AnswerSpan{0, 11, "Use coffee."}}, Corrections: []AnswerSpan{{4, 10, "coffee"}}}
	component := semanticEmpty()
	component.Supplied = true
	component.Status = "rejected"
	component.Additional = []ComponentAssertion{{AnswerSpan: AnswerSpan{4, 10, "coffee"}, Judgment: "unsupported", Reason: "Replacing cafe with coffee changes meaning and misses agreement."}}
	mapping := SemanticMapping{Groups: []SemanticGroup{{Representative: "c1", Members: []string{"c1"}, Correction: component, Explanation: semanticEmpty()}}}
	row := listenerFeedbackAssessments(CanonicalExtraction{Claims: []CanonicalClaim{claim}}, mapping)[0].(map[string]any)
	correction := row["correction"].(map[string]any)
	if row["listener_reports"].([]string)[0] != "Use coffee." || correction["source_texts"].([]string)[0] != "coffee" || correction["status"] != "rejected" || correction["additional_assertions"].([]ComponentAssertion)[0].Judgment != "unsupported" || row["recording_unit_id"].(*string) != nil {
		t.Fatal(row)
	}
}
func TestScoringFeedbackWithdrawnNegative(t *testing.T) {
	active := CanonicalClaim{ID: "c1", Group: "c1", Active: true, ExtractedClause: ExtractedClause{Span: AnswerSpan{0, 11, "Use coffee."}}, Corrections: []AnswerSpan{{4, 10, "coffee"}}}
	withdrawn := CanonicalClaim{ID: "c2", Group: "c2", Active: false, Corrections: []AnswerSpan{{12, 17, "opens"}}}
	component := semanticEmpty()
	component.Supplied = true
	component.Status = "rejected"
	m := SemanticMapping{Groups: []SemanticGroup{{Representative: "c1", Members: []string{"c1", "c2"}, Correction: component, Explanation: semanticEmpty()}}}
	row := listenerFeedbackAssessments(CanonicalExtraction{Claims: []CanonicalClaim{active, withdrawn}}, m)[0].(map[string]any)
	if texts := row["correction"].(map[string]any)["source_texts"].([]string); len(texts) != 1 || texts[0] != "coffee" {
		t.Fatal("withdrawn repair leaked into model context", texts)
	}
}
