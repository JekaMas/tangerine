package app

import (
	"math/big"
	"testing"
)

func TestScoringProjectionSeparatePositive(t *testing.T) {
	_, _, k, _, m := interpretationMappingFixture()
	u := k["units"].([]any)[0].(map[string]any)
	if q := componentCredit(m.Decisions[0].Correction, u, false); q.Cmp(big.NewRat(1, 1)) != 0 {
		t.Fatal(q)
	}
	if q := componentCredit(m.Decisions[0].Explanation, u, true); q.Sign() != 0 {
		t.Fatal(q)
	}
}
func TestScoringProjectionUnknownNegative(t *testing.T) {
	_, _, k, _, m := interpretationMappingFixture()
	u := k["units"].([]any)[0].(map[string]any)
	c := m.Decisions[0].Explanation
	c.Additional[0].Judgment = "unknown"
	if q := componentCredit(c, u, true); q != nil {
		t.Fatal(q)
	}
}
func TestScoringProjectionDecisiveZeroPositive(t *testing.T) {
	_, _, k, _, m := interpretationMappingFixture()
	u := k["units"].([]any)[0].(map[string]any)
	c := m.Decisions[0].Explanation
	c.Additional = append(c.Additional, ComponentAssertion{Judgment: "unknown"})
	reason := "unknown"
	c.Unresolved = &reason
	if q := componentCredit(c, u, true); q == nil || q.Sign() != 0 {
		t.Fatal(q)
	}
}
func TestScoringProjectionMissingNegative(t *testing.T) {
	if q := componentCredit(semanticEmpty(), nil, true); q == nil || q.Sign() != 0 {
		t.Fatal(q)
	}
}
func TestScoringProjectionOffkeyDuplicatePositive(t *testing.T) {
	c, m, key := twoClaimGroupFixture()
	for i := range m.Decisions {
		m.Decisions[i].Unit = nil
		m.Decisions[i].Decision = "false_positive"
		m.Decisions[i].Correction = semanticEmpty()
		m.Decisions[i].Explanation = semanticEmpty()
	}
	earlier := m.Decisions[0].Claim
	m.Decisions[1].Duplicate = &earlier
	groups, issues := consolidateMapping(c, m, key, map[string]any{})
	if len(issues) != 0 || len(groups) != 1 || len(groups[0].Members) != 2 {
		t.Fatal("off-key duplicate counted twice", groups, issues)
	}
}
func TestScoringProjectionDistinctOffkeyNegative(t *testing.T) {
	c, m, key := twoClaimGroupFixture()
	for i := range m.Decisions {
		m.Decisions[i].Unit = nil
		m.Decisions[i].Decision = "false_positive"
		m.Decisions[i].Correction = semanticEmpty()
		m.Decisions[i].Explanation = semanticEmpty()
	}
	groups, issues := consolidateMapping(c, m, key, map[string]any{})
	if len(issues) != 0 || len(groups) != 2 {
		t.Fatal("distinct off-key assertions collapsed", groups, issues)
	}
}
func scoredCategoryFixture() (AttemptRecord, InterpretationResources, CanonicalExtraction, SemanticMapping) {
	_, c, key, _, m := interpretationMappingFixture()
	u := key["units"].([]any)[0].(map[string]any)
	u["domain"] = "grammar"
	u["primary_taxonomy_id"] = "grammar.verbs.subject_verb_agreement"
	u["accepted_taxonomy_ids"] = []any{"grammar.verbs.subject_verb_agreement"}
	u["weight"] = float64(2)
	u["correction_eligible"] = true
	u["explanation_eligible"] = true
	u["text_spans"] = []any{}
	u["audio_intervals"] = []any{}
	u["rationale"] = "A singular subject takes singular agreement."
	for _, v := range u["corrections"].([]any) {
		v.(map[string]any)["approved_text_alternatives"] = []any{}
	}
	m.Groups, _ = consolidateMapping(c, m, key, map[string]any{"classification": true, "correction": true})
	record := AttemptRecord{Attempt: map[string]any{"attempt_id": "a1", "case_version_id": "case1", "scoring_policy_version": "answer-components-v2", "task_components": map[string]any{"detection": true, "classification": true, "correction": true}}}
	return record, InterpretationResources{Key: key}, c, m
}
func TestScoringProjectionMissingCategoryPositive(t *testing.T) {
	r, k, c, m := scoredCategoryFixture()
	score, e := scoreInterpretation(r, k, c, m, nil)
	if e != nil {
		t.Fatal(e)
	}
	if score.Status != "complete" || score.Composite.Exact.Numerator != "250" || score.Composite.Exact.Denominator != "3" {
		t.Fatal(score.Composite)
	}
}
func TestScoringProjectionUnknownCategoryNegative(t *testing.T) {
	r, k, c, m := scoredCategoryFixture()
	issues := []InterpretationIssue{{Code: "unknown_alias", Claims: []string{c.Claims[0].ID}, Units: []string{"unit1"}, Components: []string{"classification"}, Blocks: true}}
	score, e := scoreInterpretation(r, k, c, m, issues)
	if e != nil {
		t.Fatal(e)
	}
	if score.Status != "review_required" || score.Composite.Exact != nil || score.Metrics["detection.f1"].Status != "available" || score.Metrics["correction.graded_recall"].Status != "available" {
		t.Fatal("unknown classification became zero/erased independent components", score)
	}
	// A category attached to a wrong acceptance cannot affect TP classification.
	m.Decisions[0].Decision = "wrong_acceptance"
	m.Groups[0].Stance = "assert_acceptable"
	issues[0].Blocks = false
	score, e = scoreInterpretation(r, k, c, m, issues)
	if e != nil {
		t.Fatal(e)
	}
	if score.Status != "complete" || score.Composite.Exact.Numerator != "0" || score.Counts.FN != 1 {
		t.Fatal("nongraded category uncertainty blocked the primary", score.Composite)
	}

}
