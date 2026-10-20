package app

import (
	"encoding/json"
	"testing"
)

func semanticEmpty() SemanticComponent {
	return SemanticComponent{Status: "not_supplied", Satisfied: []string{}, Violated: []string{}, Evidence: []string{}, Additional: []ComponentAssertion{}}
}
func interpretationMappingFixture() (string, CanonicalExtraction, map[string]any, map[string]bool, SemanticMapping) {
	answer := "Use goes because every verb ends in s."
	option := "option1"
	unit := "unit1"
	id := "clm_00000000000000000000000000000001"
	correction := AnswerSpan{0, 8, "Use goes"}
	reason := AnswerSpan{17, 38, "every verb ends in s."}
	c := CanonicalClaim{ExtractedClause: ExtractedClause{LocalRef: "c0", Span: AnswerSpan{0, 38, answer}, Stance: "assert_error", Correction: &correction, Rationale: &reason}, ID: id, Group: id, Active: true, Corrections: []AnswerSpan{correction}, Explanations: []AnswerSpan{reason}, Categories: []AnswerSpan{}}
	extraction := CanonicalExtraction{Extraction: AnswerExtraction{Version: "2.0.0", Unparsed: []AnswerSpan{}}, Claims: []CanonicalClaim{c}}
	key := map[string]any{"case_version_id": "case1", "units": []any{map[string]any{"id": unit, "expected_judgment": "true_error", "corrections": []any{map[string]any{"id": option, "required_propositions": []any{map[string]any{"id": "required1"}}, "forbidden_propositions": []any{map[string]any{"id": "forbidden1"}}}}, "rationale_required_propositions": []any{map[string]any{"id": "reason1"}}, "rationale_forbidden_propositions": []any{}}}}
	d := SemanticDecision{Claim: id, Unit: &unit, Decision: "matched_error", Reason: "supported", Correction: semanticEmpty(), Explanation: semanticEmpty(), Evidence: []string{}}
	d.Correction.Supplied = true
	d.Correction.Option = &option
	d.Correction.Satisfied = []string{"required1"}
	d.Correction.Status = "accepted"
	d.Explanation.Supplied = true
	d.Explanation.Status = "accepted"
	d.Explanation.Additional = []ComponentAssertion{{AnswerSpan: reason, Judgment: "unsupported", Reason: "Third-person singular is not a rule for every verb."}}
	return answer, extraction, key, map[string]bool{"grammar.verbs.subject_verb_agreement": true}, SemanticMapping{Version: "1.0.0", Decisions: []SemanticDecision{d}}
}
func admitMappingFixture(answer string, c CanonicalExtraction, k map[string]any, tax map[string]bool, m SemanticMapping) (SemanticMapping, []InterpretationIssue, error) {
	raw, _ := json.Marshal(m)
	return normalizeMapping(answer, c, k, tax, []any{}, map[string]any{"correction": true}, raw)
}
func TestInterpretationSeparateExplanationPositive(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	got, _, e := admitMappingFixture(a, c, k, tax, m)
	if e != nil || got.Decisions[0].Decision != "matched_error" || got.Decisions[0].Correction.Status != "accepted" || got.Decisions[0].Explanation.Status != "rejected" {
		t.Fatal(got, e)
	}
}
func TestInterpretationUnknownExplanationPositive(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Explanation.Additional[0].Judgment = "unknown"
	got, issues, e := admitMappingFixture(a, c, k, tax, m)
	if e != nil || got.Decisions[0].Correction.Status != "accepted" || got.Decisions[0].Explanation.Status != "unresolved" || len(issues) != 1 || issues[0].Blocks {
		t.Fatal(got, issues, e)
	}
}
func TestInterpretationMissingExplanationPositive(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	c.Claims[0].Rationale = nil
	c.Claims[0].Explanations = []AnswerSpan{}
	m.Decisions[0].Explanation = semanticEmpty()
	got, issues, e := admitMappingFixture(a, c, k, tax, m)
	if e != nil || got.Decisions[0].Explanation.Status != "not_supplied" || len(issues) != 0 {
		t.Fatal(got, issues, e)
	}
}
func TestInterpretationUnknownCorrectionPositive(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	reason := "novel_alternative"
	m.Decisions[0].Correction.Unresolved = &reason
	got, issues, e := admitMappingFixture(a, c, k, tax, m)
	if e != nil || got.Decisions[0].Decision != "matched_error" || len(issues) != 1 || !issues[0].Blocks {
		t.Fatal(got, issues, e)
	}
}
func TestInterpretationCategoryOmissionPositive(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	unsolicited := "grammar.verbs.subject_verb_agreement"
	for _, category := range []*string{nil, &unsolicited} {
		m.Decisions[0].Category = category
		got, _, e := admitMappingFixture(a, c, k, tax, m)
		if e != nil || got.Decisions[0].Category != nil || got.Decisions[0].Decision != "matched_error" || got.Decisions[0].Correction.Status != "accepted" {
			t.Fatal(got, e)
		}
	}
}
func TestInterpretationForbiddenDeterminesZeroPositive(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Explanation.Additional[0].Judgment = "unknown"
	m.Decisions[0].Correction.Violated = []string{"forbidden1"}
	got, issues, e := admitMappingFixture(a, c, k, tax, m)
	if e != nil || got.Decisions[0].Correction.Status != "rejected" || got.Decisions[0].Explanation.Additional[0].Judgment != "unknown" || len(issues) != 1 || issues[0].Blocks {
		t.Fatal(got, issues, e)
	}
}
func TestInterpretationUnknownUnitNegative(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	unit := "another-case-unit"
	m.Decisions[0].Unit = &unit
	if _, _, e := admitMappingFixture(a, c, k, tax, m); e == nil {
		t.Fatal("cross-case target accepted")
	}
}
func TestInterpretationInventedPropositionNegative(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Correction.Satisfied = []string{"someone-elses-proposition"}
	if _, _, e := admitMappingFixture(a, c, k, tax, m); e == nil {
		t.Fatal("invented rubric accepted")
	}
}
func TestInterpretationMissingDecisionNegative(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions = []SemanticDecision{}
	if _, _, e := admitMappingFixture(a, c, k, tax, m); e == nil {
		t.Fatal("claim omitted")
	}
}
func TestInterpretationBorrowedAssertionNegative(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Correction.Additional = []ComponentAssertion{{AnswerSpan: AnswerSpan{17, 38, "every verb ends in s."}, Judgment: "unsupported", Reason: "Wrong rule"}}
	if _, _, e := admitMappingFixture(a, c, k, tax, m); e == nil {
		t.Fatal("rationale borrowed into correction")
	}
}
func TestInterpretationInventedCategoryNegative(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	c.Claims[0].Categories = []AnswerSpan{{23, 27, "verb"}}
	category := "grammar.verbs.not_a_category"
	m.Decisions[0].Category = &category
	if _, _, e := admitMappingFixture(a, c, k, tax, m); e == nil {
		t.Fatal("invented taxonomy identity accepted")
	}
}
func TestInterpretationWrongStanceNegative(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Decision = "wrong_acceptance"
	if _, _, e := admitMappingFixture(a, c, k, tax, m); e == nil {
		t.Fatal("asserted error turned into acceptance")
	}
}
func TestInterpretationAuditProsePositive(t *testing.T) {
	_, _, _, _, a := interpretationMappingFixture()
	raw, _ := json.Marshal(a)
	var b SemanticMapping
	_ = json.Unmarshal(raw, &b)
	b.Decisions[0].Note = "Different prose"
	b.Decisions[0].Explanation.Additional[0].Reason = "Same unsupported rule, explained differently"
	if !compareMapping(a, b) || a.Decisions[0].Explanation.Additional[0].Reason != "Third-person singular is not a rule for every verb." {
		t.Fatal("audit mutated findings or used prose as gate")
	}
}
func TestInterpretationAuditDifferenceNegative(t *testing.T) {
	_, _, _, _, a := interpretationMappingFixture()
	raw, _ := json.Marshal(a)
	var b SemanticMapping
	_ = json.Unmarshal(raw, &b)
	b.Decisions[0].Explanation.Additional[0].Judgment = "supported"
	if compareMapping(a, b) {
		t.Fatal("substantive audit difference hidden")
	}
}

func TestInterpretationAuditReasonPositive(t *testing.T) {
	_, _, _, _, a := interpretationMappingFixture()
	b := a
	b.Decisions = append([]SemanticDecision{}, a.Decisions...)
	b.Decisions[0].Note = "Different linguistic prose"
	if !compareMapping(a, b) {
		t.Fatal("prose became a gate")
	}
}
func TestInterpretationAuditTargetNegative(t *testing.T) {
	_, _, _, _, a := interpretationMappingFixture()
	b := a
	b.Decisions = append([]SemanticDecision{}, a.Decisions...)
	id := "another-unit"
	b.Decisions[0].Unit = &id
	if compareMapping(a, b) {
		t.Fatal("target discrepancy erased")
	}
}

func stanceMappingFixture(t *testing.T, truth, stance, decision string) (SemanticMapping, []InterpretationIssue, error) {
	t.Helper()
	answer := "That form is acceptable."
	if stance == "assert_error" {
		answer = "That form is wrong."
	}
	if stance == "question" {
		answer = "Is that form acceptable?"
	}
	_, _, key, tax, _ := interpretationMappingFixture()
	key["units"].([]any)[0].(map[string]any)["expected_judgment"] = truth
	c, e := normalizeExtraction(answer, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, len([]rune(answer)), answer}, Stance: stance}}, nil))
	if e != nil {
		t.Fatal(e)
	}
	unit := "unit1"
	m := SemanticMapping{Version: "1.0.0", Decisions: []SemanticDecision{{Claim: c.Claims[0].ID, Unit: &unit, Decision: decision, Reason: "supported", Evidence: []string{}, Correction: semanticEmpty(), Explanation: semanticEmpty()}}}
	return admitMappingFixture(answer, c, key, tax, m)
}
func TestInterpretationWrongAcceptancePositive(t *testing.T) {
	m, issues, e := stanceMappingFixture(t, "true_error", "assert_acceptable", "wrong_acceptance")
	if e != nil || len(issues) != 0 || m.Decisions[0].Decision != "wrong_acceptance" || m.Groups[0].Stance != "assert_acceptable" {
		t.Fatal(m, issues, e)
	}
}
func TestInterpretationControlAcceptancePositive(t *testing.T) {
	m, issues, e := stanceMappingFixture(t, "acceptable", "assert_acceptable", "confirmed_acceptable")
	if e != nil || len(issues) != 0 || m.Decisions[0].Decision != "confirmed_acceptable" {
		t.Fatal(m, issues, e)
	}
}
func TestInterpretationControlFalseAssertionNegative(t *testing.T) {
	m, issues, e := stanceMappingFixture(t, "acceptable", "assert_error", "false_positive")
	if e != nil || len(issues) != 0 || m.Decisions[0].Decision != "false_positive" {
		t.Fatal(m, issues, e)
	}
	answer, c, key, tax, raw := interpretationMappingFixture()
	raw.Decisions[0].Unit = nil
	raw.Decisions[0].Decision = "false_positive"
	raw.Decisions[0].Correction = semanticEmpty()
	raw.Decisions[0].Explanation = semanticEmpty()
	c.Claims[0].Corrections = []AnswerSpan{}
	c.Claims[0].Explanations = []AnswerSpan{}
	off, _, e := admitMappingFixture(answer, c, key, tax, raw)
	if e != nil || off.Decisions[0].Unit != nil || off.Decisions[0].Decision != "false_positive" {
		t.Fatal(off, e)
	}
}
func TestInterpretationQuestionIgnoreNegative(t *testing.T) {
	m, issues, e := stanceMappingFixture(t, "true_error", "question", "ignore")
	if e != nil || len(issues) != 0 || len(m.Groups) != 0 {
		t.Fatal(m, issues, e)
	}
	answer, _, key, tax, _ := interpretationMappingFixture()
	c := CanonicalExtraction{Extraction: AnswerExtraction{Unparsed: []AnswerSpan{{0, len([]rune(answer)), answer}}}, Claims: []CanonicalClaim{}}
	raw := SemanticMapping{Version: "1.0.0", Decisions: []SemanticDecision{}}
	_, issues, e = admitMappingFixture(answer, c, key, tax, raw)
	if e != nil || len(issues) != 1 || issues[0].Code != "unparsed_substantive_text" || !issues[0].Blocks {
		t.Fatal(issues, e)
	}
}

func rejectionFixture() (string, CanonicalExtraction, map[string]any, map[string]bool, SemanticMapping) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Correction.Option = nil
	m.Decisions[0].Correction.Satisfied = []string{}
	m.Decisions[0].Correction.Status = "rejected"
	return a, c, k, tax, m
}
func TestInterpretationDefiniteRejectionPositive(t *testing.T) {
	a, c, k, tax, m := rejectionFixture()
	got, issues, e := admitMappingFixture(a, c, k, tax, m)
	if e != nil || got.Decisions[0].Correction.Status != "rejected" || got.Decisions[0].Correction.Option != nil || len(issues) != 0 {
		t.Fatal(got, issues, e)
	}
}
func TestInterpretationRejectedRetainsUnknownPositive(t *testing.T) {
	a, c, k, tax, m := rejectionFixture()
	m.Decisions[0].Correction.Additional = []ComponentAssertion{{AnswerSpan: c.Claims[0].Corrections[0], Judgment: "unknown", Reason: "Separate assertion remains unknown"}}
	got, issues, e := admitMappingFixture(a, c, k, tax, m)
	if e != nil || got.Decisions[0].Correction.Status != "rejected" || len(got.Decisions[0].Correction.Additional) != 1 || len(issues) != 0 {
		t.Fatal(got, issues, e)
	}
}
func TestInterpretationUncertainRejectionNegative(t *testing.T) {
	a, c, k, tax, m := rejectionFixture()
	reason := "novel_alternative"
	m.Decisions[0].Correction.Unresolved = &reason
	got, issues, e := admitMappingFixture(a, c, k, tax, m)
	if e != nil || got.Decisions[0].Correction.Status != "unresolved" || len(issues) != 1 || !issues[0].Blocks {
		t.Fatal(got, issues, e)
	}
}
func TestInterpretationNoOptionCreditNegative(t *testing.T) {
	a, c, k, tax, m := rejectionFixture()
	m.Decisions[0].Correction.Status = "accepted"
	if _, _, e := admitMappingFixture(a, c, k, tax, m); e == nil {
		t.Fatal("positive label without rubric findings bypassed bounded repair")
	}
}

func TestInterpretationUniqueRubricPositive(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Correction.Option = nil
	got, _, err := admitMappingFixture(a, c, k, tax, m)
	if err != nil || optionalID(got.Decisions[0].Correction.Option) != "option1" || got.Decisions[0].Correction.Status != "accepted" {
		t.Fatal(got, err)
	}
}
func TestInterpretationAmbiguousRubricNegative(t *testing.T) {
	a, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Correction.Option = nil
	u := k["units"].([]any)[0].(map[string]any)
	u["corrections"] = append(u["corrections"].([]any), map[string]any{"id": "option2", "required_propositions": []any{map[string]any{"id": "required1"}}, "forbidden_propositions": []any{}})
	if _, _, err := admitMappingFixture(a, c, k, tax, m); err == nil {
		t.Fatal("selected a favorable option from ambiguous proposition IDs")
	}
}

func TestInterpretationContextAssertionPositive(t *testing.T) {
	answer := "The verb open is wrong. Change it to opening."
	_, c, k, tax, m := rejectionFixture()
	claim := &c.Claims[0]
	claim.Span = AnswerSpan{0, 45, answer}
	claim.Corrections = []AnswerSpan{{37, 44, "opening"}}
	claim.Explanations = []AnswerSpan{}
	m.Decisions[0].Explanation = semanticEmpty()
	m.Decisions[0].Correction.Additional = []ComponentAssertion{{AnswerSpan: AnswerSpan{0, 45, answer}, Judgment: "unsupported", Reason: "Opening does not repair the finite singular verb."}}
	got, issues, err := admitMappingFixture(answer, c, k, tax, m)
	if err != nil || len(issues) != 0 || got.Decisions[0].Correction.Status != "rejected" || got.Decisions[0].Correction.Additional[0].AnswerSpan != (AnswerSpan{37, 44, "opening"}) {
		t.Fatal(got, issues, err)
	}
}
func TestInterpretationCrossComponentContextNegative(t *testing.T) {
	answer, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Correction.Additional = []ComponentAssertion{{AnswerSpan: AnswerSpan{0, len([]rune(answer)), answer}, Judgment: "unsupported", Reason: "This quote includes both components."}}
	if _, _, err := admitMappingFixture(answer, c, k, tax, m); err == nil {
		t.Fatal("borrowed rationale through a broad correction quote")
	}
}
func TestInterpretationRepresentedReasonPositive(t *testing.T) {
	answer, c, k, tax, m := interpretationMappingFixture()
	answer = "Use goes because the subject is singular."
	c.Claims[0].Span = AnswerSpan{0, 41, answer}
	c.Claims[0].Explanations = []AnswerSpan{{17, 41, "the subject is singular."}}
	m.Decisions[0].Explanation.Additional = []ComponentAssertion{{AnswerSpan: AnswerSpan{17, 41, "the subject is singular."}, Judgment: "supported", Reason: "The present-tense third-person singular subject requires agreement."}}
	m.Decisions[0].Explanation.Satisfied = []string{"reason1"}
	got, issues, err := admitMappingFixture(answer, c, k, tax, m)
	if err != nil || len(issues) != 0 || got.Decisions[0].Explanation.Status != "accepted" {
		t.Fatal(got, issues, err)
	}
}
func TestInterpretationUnrepresentedReasonNegative(t *testing.T) {
	answer, c, k, tax, m := interpretationMappingFixture()
	m.Decisions[0].Explanation.Additional = []ComponentAssertion{}
	for _, status := range []string{"rejected", "accepted"} {
		m.Decisions[0].Explanation.Status = status
		m.Decisions[0].Explanation.Satisfied = []string{}
		if status == "accepted" {
			m.Decisions[0].Explanation.Satisfied = []string{"reason1"}
		}
		if _, _, err := admitMappingFixture(answer, c, k, tax, m); err == nil {
			t.Fatal("supplied reason was never assessed beyond rubric overlap", status)
		}
	}
}
