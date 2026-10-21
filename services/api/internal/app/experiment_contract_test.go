package app

import (
	"context"
	"encoding/json"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/experiment"
	"testing"
	"time"
)

func qualityPropositions() []any {
	return []any{map[string]any{"id": "p", "proposition": "The correction fixes the local agreement error.", "scope": "answer_mapping"}}
}
func TestQualityJudgeSupportedPositive(t *testing.T) {
	raw := []byte(`{"schema_version":"2.0.0","verdicts":[{"proposition_id":"p","verdict":"supported","reason":"Source-supported","evidence":[{"asset_id":"candidate","pointer":"/correction"}],"missing_reason":null}]}`)
	e := validateQualityJudge(raw, qualityPropositions(), map[string]any{"candidate": map[string]any{"correction": "opens"}})
	if e != nil {
		t.Fatal(e)
	}
}
func TestQualityJudgeUnknownPositive(t *testing.T) {
	raw := []byte(`{"schema_version":"2.0.0","verdicts":[{"proposition_id":"p","verdict":"unknown","reason":"Audio absent","evidence":[],"missing_reason":"No recording"}]}`)
	if e := validateQualityJudge(raw, qualityPropositions(), nil); e != nil {
		t.Fatal(e)
	}
}
func TestQualityJudgePointerNegative(t *testing.T) {
	raw := []byte(`{"schema_version":"2.0.0","verdicts":[{"proposition_id":"p","verdict":"supported","reason":"claim","evidence":[{"asset_id":"candidate","pointer":"/absent"}],"missing_reason":null}]}`)
	if e := validateQualityJudge(raw, qualityPropositions(), map[string]any{"candidate": map[string]any{"correction": "opens"}}); e == nil {
		t.Fatal("invented evidence")
	}
}
func TestQualityJudgeMissingNegative(t *testing.T) {
	raw := []byte(`{"schema_version":"2.0.0","verdicts":[]}`)
	if e := validateQualityJudge(raw, qualityPropositions(), nil); e == nil {
		t.Fatal("missing verdict")
	}
}
func TestQualityJudgeNoNumericNegative(t *testing.T) {
	if _, _, e := validateQualityOutput([]byte(`{"schema_version":"2.0.0","verdicts":[],"score":100}`)); e == nil {
		t.Fatal("model numeric grade accepted")
	}
}
func validateQualityOutput(b []byte) (any, any, error) {
	return contracts.Validate("llm-quality-judge-output", "2.0.0", b)
}
func TestQualityJudgeSelfConsistencyPositive(t *testing.T) {
	e := experiment.Evidence{Stats: map[string]string{}}
	expected := map[string]any{"semantic_propositions": []any{map[string]any{"id": "p", "scope": "feedback", "expected": "supported"}}}
	judgment := map[string]any{"verdicts": []any{map[string]any{"proposition_id": "p", "verdict": "supported"}}}
	qualityJudgeEvidence(QualityCase{Basis: "self_consistency"}, expected, judgment, &e)
	if e.Basis["llm_lab.feedback_grounding_rate"] != "self_consistency" || e.Stats["supported_factual_items_or_correctly_labelled_practice"] != "1" {
		t.Fatal(e)
	}
}
func TestQualityUnsupportedNegative(t *testing.T) {
	e := experiment.Evidence{Stats: map[string]string{}}
	expected := map[string]any{"semantic_propositions": []any{map[string]any{"id": "p", "scope": "feedback", "expected": "unsupported"}}}
	judgment := map[string]any{"verdicts": []any{map[string]any{"proposition_id": "p", "verdict": "unsupported"}}}
	qualityJudgeEvidence(QualityCase{Basis: "authored_assertion"}, expected, judgment, &e)
	if e.Stats["supported_factual_items_or_correctly_labelled_practice"] != "0" || e.Stats["applicable_feedback_items"] != "1" {
		t.Fatal("unsupported claim became grounded", e)
	}
}
func TestQualityDisclosurePositive(t *testing.T) {
	input := map[string]any{"answer_text": "Use opens.", "ground_truth": "hidden", "prior_decisions": "hidden", "scoring_result": 100}
	parts := qualityStageComponents("blind_claim_extraction", input)
	if len(parts) != 2 || parts["answer"] != "Use opens." {
		t.Fatal(parts)
	}
}
func TestQualityAuditLeakNegative(t *testing.T) {
	parts := qualityStageComponents("mapping_audit", map[string]any{"prior_decisions": []string{"first-map"}, "extraction": "saved", "ground_truth": "key"})
	if _, ok := parts["prior_decisions"]; ok {
		t.Fatal("audit sees first-map decisions")
	}
}
func TestQualityIndependentComponentsPositive(t *testing.T) {
	reference := SemanticMapping{Decisions: []SemanticDecision{{Claim: "c", Unit: ptrQualityTest("u"), Decision: "matched_error", Category: ptrQualityTest("grammar.verbs.subject_verb_agreement"), Correction: SemanticComponent{Supplied: true, Satisfied: []string{"correct"}}, Explanation: SemanticComponent{Supplied: true, Violated: []string{"reason"}}}}}
	actual := reference
	var ref, got map[string]any
	_ = json.Unmarshal(sourceBytes(reference), &ref)
	_ = json.Unmarshal(sourceBytes(actual), &got)
	e := experiment.Evidence{Stats: map[string]string{}}
	qualityMappingEvidence(ref, got, &e)
	if e.Stats["TP"] != "1" || e.Stats["correct_applicable_repair_propositions"] != "1" || e.Stats["correct_applicable_explanation_propositions"] != "1" {
		t.Fatal(e)
	}
}
func TestQualityWrongMappingNegative(t *testing.T) {
	ref := map[string]any{"decisions": []any{map[string]any{"unit_id": "real", "decision": "matched_error"}}}
	got := map[string]any{"decisions": []any{map[string]any{"unit_id": "invented", "decision": "matched_error"}}}
	e := experiment.Evidence{Stats: map[string]string{}}
	qualityMappingEvidence(ref, got, &e)
	if e.Stats["TP"] != "0" || e.Stats["FP"] != "1" || e.Stats["FN"] != "1" {
		t.Fatal(e)
	}
}
func ptrQualityTest(s string) *string { return &s }
func TestQualityWrappedEvidencePositive(t *testing.T) {
	value := map[string]any{"verdicts": []any{map[string]any{"proposition_id": "p", "verdict": "supported", "evidence": []any{map[string]any{"asset_id": "input", "pointer": "/body/answer_text"}}}}}
	got := normalizeQualityJudge(value, map[string]any{"input": map[string]any{"answer_text": "Use opens."}}).(map[string]any)
	pointer := got["verdicts"].([]any)[0].(map[string]any)["evidence"].([]any)[0].(map[string]any)["pointer"]
	if pointer != "/answer_text" {
		t.Fatal(pointer)
	}
}
func TestQualityAbsentWrappedEvidenceNegative(t *testing.T) {
	value := map[string]any{"verdicts": []any{map[string]any{"proposition_id": "p", "verdict": "supported", "evidence": []any{map[string]any{"asset_id": "input", "pointer": "/body/absent"}}}}}
	got := normalizeQualityJudge(value, map[string]any{"input": map[string]any{"answer_text": "Use opens."}}).(map[string]any)
	if got["verdicts"].([]any)[0].(map[string]any)["evidence"].([]any)[0].(map[string]any)["pointer"] != "/body/absent" {
		t.Fatal("invented a target")
	}
}
func TestQualityNativeBudgetPositive(t *testing.T) {
	s := new(Storage)
	root := context.Background()
	first, cancel, e := s.qualityOwnerContext(root)
	if e != nil {
		t.Fatal(e)
	}
	deadline, ok := first.Deadline()
	if !ok || time.Until(deadline) > 270*time.Second || time.Until(deadline) < 269*time.Second {
		t.Fatal("native operation budget lost")
	}
	cancel()
	second, done, e := s.qualityOwnerContext(root)
	if e != nil {
		t.Fatal(e)
	}
	defer done()
	if first.Err() == nil || second.Err() != nil {
		t.Fatal("one completed operation cancelled its independent successor")
	}
}
func TestQualityNativeBudgetCancellationNegative(t *testing.T) {
	s := new(Storage)
	root, cancel := context.WithCancel(context.Background())
	cancel()
	operation, done, e := s.qualityOwnerContext(root)
	if e != nil {
		t.Fatal(e)
	}
	defer done()
	if operation.Err() == nil {
		t.Fatal("cancelled batch allowed work")
	}
}

func TestQualityRequestMeasurementsPositive(t *testing.T) {
	_, _, candidate, _ := mutationFixture()
	e := experiment.Evidence{Stats: map[string]string{}}
	qualityGenerationEvidence(map[string]any{"text_length_words": float64(50), "speaker_count": float64(1), "mutation_count": float64(1), "category_families": []any{"grammar"}}, candidate, map[string]any{"surface_word_count": float64(4), "canonical_word_count": float64(4)}, &e)
	if e.Stats["applicable_request_predicates"] != "3" || e.Stats["satisfied_applicable_request_predicates"] != "3" || e.Stats["surface_word_absolute_deviation"] != "46" {
		t.Fatal(e)
	}
}
func TestQualityRequestMeasurementsNegative(t *testing.T) {
	_, _, candidate, _ := mutationFixture()
	e := experiment.Evidence{Stats: map[string]string{}}
	qualityGenerationEvidence(map[string]any{"text_length_words": float64(50), "speaker_count": float64(2), "mutation_count": float64(2), "category_families": []any{"lexis"}}, candidate, map[string]any{"surface_word_count": float64(4)}, &e)
	if e.Stats["applicable_request_predicates"] != "3" || e.Stats["satisfied_applicable_request_predicates"] != "0" {
		t.Fatal(e)
	}
}
func TestQualityPreservationPositive(t *testing.T) {
	e := experiment.Evidence{Stats: map[string]string{}}
	qualityDeterministicEvidence(QualityCase{}, QualityExperiment{Scope: "generation_pipeline"}, nil, nil, nil, map[string]any{"initial_canonical_sha256": "saved", "canonical_sha256": "saved"}, &e)
	if e.Stats["completed_mutation_outputs"] != "1" || e.Stats["mutation_outputs_with_exact_saved_canonical"] != "1" {
		t.Fatal(e)
	}
}
func TestQualityPreservationNegative(t *testing.T) {
	e := experiment.Evidence{Stats: map[string]string{}}
	qualityDeterministicEvidence(QualityCase{}, QualityExperiment{Scope: "generation_pipeline"}, nil, nil, nil, map[string]any{"initial_canonical_sha256": "saved", "canonical_sha256": "changed"}, &e)
	if e.Stats["mutation_outputs_with_exact_saved_canonical"] != "0" {
		t.Fatal(e)
	}
}
