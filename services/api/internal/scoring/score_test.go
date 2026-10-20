package scoring

import (
	"encoding/json"
	"math/big"
	"strings"
	"testing"
)

func authored() Input {
	return Input{Attempt: "a1", Case: "c1", DecisionSHA: strings.Repeat("a", 64), Policy: "answer-components-v2", Enabled: map[string]bool{"detection": true, "classification": true, "correction": true}, Unresolved: map[string]bool{}, Units: []Unit{
		{"a", "grammar", "grammar.verb.agreement", "true_error", []string{"grammar.verb.agreement"}, 3, true, true},
		{"b", "lexis", "lexis.word_choice", "true_error", []string{"lexis.word_choice"}, 2, true, true},
		{"c", "pronunciation.segmental", "pronunciation.segmental.vowel", "true_error", []string{"pronunciation.segmental.vowel"}, 1, true, true},
		{"d", "acceptable_variant", "acceptable_variant.dialect", "acceptable", []string{"acceptable_variant.dialect"}, 1, false, false},
		{"e", "acceptable_variant", "acceptable_variant.dialect", "acceptable", []string{"acceptable_variant.dialect"}, 1, false, false}}, Decisions: []Decision{
		{ID: "d1", Unit: "a", Verdict: "matched_error", Category: "grammar.verb", CorrectionSupplied: true, ExplanationSupplied: true, Correction: fraction(1, 2), Explanation: fraction(1, 1)},
		{ID: "d2", Unit: "b", Verdict: "matched_error", Category: "lexis.word_choice", CorrectionSupplied: true, Correction: fraction(1, 1)},
		{ID: "d3", Unit: "c", Verdict: "wrong_acceptance"},
		{ID: "d4", Unit: "d", Verdict: "false_positive", CorrectionSupplied: true},
		{ID: "d5", Unit: "e", Verdict: "confirmed_acceptable"},
		{ID: "d6", Verdict: "false_positive", CorrectionSupplied: true}}}
}
func expect(t *testing.T, m Metric, n, d string) {
	t.Helper()
	if m.Status != "available" || m.Numerator == nil || *m.Numerator != n || *m.Denominator != d {
		t.Fatalf("got%+v want%s/%s", m, n, d)
	}
}
func TestScoringDetectionPrecisionPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["detection.precision"], "1", "2")
}
func TestScoringDetectionPrecisionNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["detection.precision"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringDetectionRecallPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["detection.recall"], "2", "3")
}
func TestScoringDetectionRecallNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["detection.recall"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringDetectionF1Positive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["detection.f1"], "4", "7")
}
func TestScoringDetectionF1Negative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["detection.f1"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringDetectionMissRatePositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["detection.miss_rate"], "1", "3")
}
func TestScoringDetectionMissRateNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["detection.miss_rate"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringDetectionFalseDiscoveryRatePositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["detection.false_discovery_rate"], "1", "2")
}
func TestScoringDetectionFalseDiscoveryRateNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["detection.false_discovery_rate"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringClassificationCoveragePositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["classification.coverage"], "1", "1")
}
func TestScoringClassificationCoverageNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["classification.coverage"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringClassificationFamilyAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["classification.family_accuracy"], "1", "1")
}
func TestScoringClassificationFamilyAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["classification.family_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringClassificationExactAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["classification.exact_accuracy"], "1", "2")
}
func TestScoringClassificationExactAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["classification.exact_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringClassificationHierarchicalAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["classification.hierarchical_accuracy"], "9", "10")
}
func TestScoringClassificationHierarchicalAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["classification.hierarchical_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringClassificationHierarchicalRecallPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["classification.hierarchical_recall"], "3", "5")
}
func TestScoringClassificationHierarchicalRecallNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["classification.hierarchical_recall"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringCorrectionAttemptRatePositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["correction.attempt_rate"], "1", "1")
}
func TestScoringCorrectionAttemptRateNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["correction.attempt_rate"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringCorrectionStrictAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["correction.strict_accuracy"], "1", "2")
}
func TestScoringCorrectionStrictAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["correction.strict_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringCorrectionGradedAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["correction.graded_accuracy"], "3", "4")
}
func TestScoringCorrectionGradedAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["correction.graded_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringCorrectionStrictRecallPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["correction.strict_recall"], "1", "3")
}
func TestScoringCorrectionStrictRecallNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["correction.strict_recall"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringCorrectionGradedRecallPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["correction.graded_recall"], "1", "2")
}
func TestScoringCorrectionGradedRecallNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["correction.graded_recall"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringCorrectionAssertionPrecisionPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["correction.assertion_precision"], "1", "4")
}
func TestScoringCorrectionAssertionPrecisionNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["correction.assertion_precision"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringExplanationCoveragePositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["explanation.coverage"], "1", "2")
}
func TestScoringExplanationCoverageNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["explanation.coverage"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringExplanationStrictAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["explanation.strict_accuracy"], "1", "1")
}
func TestScoringExplanationStrictAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["explanation.strict_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringExplanationGradedAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["explanation.graded_accuracy"], "1", "1")
}
func TestScoringExplanationGradedAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["explanation.graded_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringExplanationGradedRecallPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["explanation.graded_recall"], "1", "3")
}
func TestScoringExplanationGradedRecallNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["explanation.graded_recall"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringDecoyOvercorrectionRatePositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["decoy.overcorrection_rate"], "1", "2")
}
func TestScoringDecoyOvercorrectionRateNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["decoy.overcorrection_rate"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringDecoyUnflaggedRatePositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["decoy.unflagged_rate"], "1", "2")
}
func TestScoringDecoyUnflaggedRateNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["decoy.unflagged_rate"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringDecoyExplicitAcceptabilityAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["decoy.explicit_acceptability_accuracy"], "1", "2")
}
func TestScoringDecoyExplicitAcceptabilityAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["decoy.explicit_acceptability_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringAcceptabilityExplicitAccuracyPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["acceptability.explicit_accuracy"], "3", "5")
}
func TestScoringAcceptabilityExplicitAccuracyNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["acceptability.explicit_accuracy"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringWeightedPrecisionPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["weighted.precision"], "5", "7")
}
func TestScoringWeightedPrecisionNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["weighted.precision"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringWeightedRecallPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["weighted.recall"], "5", "6")
}
func TestScoringWeightedRecallNegative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["weighted.recall"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}
func TestScoringWeightedF1Positive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["weighted.f1"], "10", "13")
}
func TestScoringWeightedF1Negative(t *testing.T) {
	x := authored()
	x.Units = nil
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	m := r.Metrics["weighted.f1"]
	if m.Value != nil || m.Numerator != nil || m.Status != "not_applicable" {
		t.Fatal(m)
	}
}

func TestScoringCompositePositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	if *r.Composite.Exact != (Exact{"1160", "21"}) || *r.Composite.Display != "55.2" || len(r.Domains) != 9 {
		t.Fatal(r)
	}
	expect(t, r.Explanation, "1", "1")
}
func TestScoringEmptyNegative(t *testing.T) {
	x := authored()
	x.Decisions = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["detection.f1"], "0", "1")
	if *r.Composite.Display != "0.0" || r.Metrics["detection.precision"].Status != "not_applicable" {
		t.Fatal(r)
	}
}
func TestScoringUnknownReasonPositive(t *testing.T) {
	x := authored()
	x.Decisions[0].Explanation = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if r.Status != "complete" || *r.Composite.Display != "55.2" || r.Statistics["EA"] != int64(1) || r.Statistics["EK"] != nil || r.Statistics["EQ"] != nil || r.Explanation.Status != "review_required" {
		t.Fatal(r)
	}
	expect(t, r.Metrics["explanation.coverage"], "1", "2")
}
func TestScoringUnknownRepairNegative(t *testing.T) {
	x := authored()
	x.Decisions[0].Correction = nil
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if r.Status != "review_required" || r.Composite.Exact != nil || r.Statistics["CK"] != nil {
		t.Fatal(r)
	}
	expect(t, r.Metrics["detection.recall"], "2", "3")
}
func TestScoringControlsPositive(t *testing.T) {
	x := authored()
	x.Units = x.Units[3:]
	x.Decisions = x.Decisions[3:]
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if r.Composite.Exact != nil || r.Counts.FP != 2 || r.Counts.TP != 0 {
		t.Fatal(r)
	}
	expect(t, r.Metrics["decoy.overcorrection_rate"], "1", "2")
}
func TestScoringPendingNegative(t *testing.T) {
	x := authored()
	x.Unresolved["detection"] = true
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if r.Counts != nil || r.Statistics != nil || r.Composite.Exact != nil || r.Status != "review_required" {
		t.Fatal(r)
	}
	for _, i := range r.Items {
		if i.Kind == "missed" {
			t.Fatal(i)
		}
	}
}
func TestScoringDomainsPositive(t *testing.T) {
	r, e := Score(authored())
	if e != nil {
		t.Fatal(e)
	}
	g, tp, fn, fp := int64(0), int64(0), int64(0), int64(0)
	for _, d := range r.Domains {
		g += d.G
		tp += d.TP
		fn += d.FN
		fp += d.FP
	}
	if g != 3 || tp != 2 || fn != 1 || fp != 2 {
		t.Fatal(r.Domains)
	}
	if r.Domains[8].FP != 1 {
		t.Fatal(r.Domains)
	}
}
func TestScoringNoBestOfNegative(t *testing.T) {
	x := authored()
	x.Unresolved["correction"] = true
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if r.Composite.Exact != nil || r.Statistics["CQ"] != nil {
		t.Fatal(r)
	}
	expect(t, r.Metrics["classification.hierarchical_recall"], "3", "5")
}
func TestScoringRoundingPositive(t *testing.T) {
	if Display(fraction(-1, 16), true) != "-6.3" || Display(fraction(-1, 100000), true) != "0.0" {
		t.Fatal("signed half-up rounding")
	}

	if Display(fraction(1, 16), true) != "6.3" || Display(fraction(1, 3), true) != "33.3" || Display(fraction(9995, 100), false) != "100.0" {
		t.Fatal("half up")
	}
	v, e := exact(fraction(100, 200))
	if e != nil || *v != (Exact{"1", "2"}) {
		t.Fatal(v, e)
	}
}
func TestScoringMagnitudeNegative(t *testing.T) {
	n, _ := new(big.Int).SetString("1"+strings.Repeat("0", 4096), 10)
	if _, e := exact(new(big.Rat).SetInt(n)); e != ErrMagnitude {
		t.Fatal(e)
	}
}
func TestScoringAuxiliaryPositive(t *testing.T) {
	raw, k := Agreement([][2]string{{"yes", "yes"}, {"yes", "no"}, {"no", "no"}, {"no", "no"}, {"", "yes"}})
	a, e := Auxiliary(map[string]Population{"annotation.agreement": raw, "annotation.cohen_kappa": k, "verification.wer": WordError([]string{"a", "cat"}, []string{"a", "small", "dog"})})
	if e != nil {
		t.Fatal(e)
	}
	if *a["annotation.agreement"].Display != "75.0%" || *a["annotation.cohen_kappa"].Display != "50.0%" {
		t.Fatal("ratio display is not native half-up percent", a)
	}
	if *a["annotation.agreement"].Exact != (Exact{"3", "4"}) || *a["annotation.cohen_kappa"].Exact != (Exact{"1", "2"}) || *a["verification.wer"].Exact != (Exact{"1", "1"}) {
		t.Fatal(a)
	}
}
func TestScoringAuxiliaryAbsentNegative(t *testing.T) {
	_, k := Agreement([][2]string{{"yes", "yes"}})
	a, e := Auxiliary(map[string]Population{"annotation.cohen_kappa": k})
	if e != nil {
		t.Fatal(e)
	}
	if len(a) != 15 || a["annotation.cohen_kappa"].Exact != nil || a["teacher.pronunciation"].Status != "not_observable" || a["audio.speech_rate_wpm"].Status != "not_run" {
		t.Fatal(a)
	}
	if _, e = json.Marshal(a); e != nil {
		t.Fatal(e)
	}
}
func TestScoringMicroPositive(t *testing.T) {
	x := authored()
	y := Input{Units: x.Units[:1], Decisions: x.Decisions[:1]}
	y.Decisions[0].Correction = fraction(1, 1)
	r, e := Micro([]Input{x, y}, map[string]bool{"detection": true})
	if e != nil {
		t.Fatal(e)
	}
	expect(t, r.Metrics["detection.f1"], "2", "3")
	if r.Counts.G != 4 || r.Counts.TP != 3 {
		t.Fatal(r.Counts)
	}
}
func TestScoringMicroNoMeanNegative(t *testing.T) {
	x := authored()
	y := Input{Units: x.Units[:1], Decisions: x.Decisions[:1]}
	r, e := Micro([]Input{x, y}, map[string]bool{"detection": true})
	if e != nil {
		t.Fatal(e)
	}
	if *r.Metrics["detection.f1"].Numerator == "11" && *r.Metrics["detection.f1"].Denominator == "14" {
		t.Fatal("averaged percentages")
	}
	expect(t, r.Metrics["detection.recall"], "3", "4")
}
func TestScoringObservedPopulationsPositive(t *testing.T) {
	p := SpeechPopulations(100, 60000, 50000, 10000, 3, "measured-v1", []string{"e1"})
	p["evaluation.coverage"] = Population{fraction(3, 1), fraction(4, 1), "gold-v1", []string{"gold1"}}
	p["evaluation.exact_mapping_agreement"] = Population{fraction(2, 1), fraction(4, 1), "gold-v1", []string{"gold1"}}
	a, e := Auxiliary(p)
	if e != nil {
		t.Fatal(e)
	}
	for name, want := range map[string]Exact{"audio.speech_rate_wpm": {"100", "1"}, "audio.articulation_rate_wpm": {"120", "1"}, "audio.pause_ratio": {"1", "6"}, "audio.disfluency_density": {"3", "1"}, "evaluation.coverage": {"3", "4"}, "evaluation.exact_mapping_agreement": {"1", "2"}} {
		if *a[name].Exact != want {
			t.Fatal(name, a[name])
		}
	}
}
func TestScoringNoFabricatedTraitsNegative(t *testing.T) {
	a, e := Auxiliary(map[string]Population{"teacher.pronunciation": {fraction(1, 1), fraction(1, 1), "invented", []string{}}})
	if e != nil {
		t.Fatal(e)
	}
	if a["teacher.pronunciation"].Exact != nil || a["teacher.pronunciation"].Status != "not_observable" {
		t.Fatal(a)
	}
}

func TestScoringLegacyPositive(t *testing.T) {
	x := authored()
	x.Policy = "1.0.0"
	x.Enabled["explanation"] = true
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if *r.Composite.Exact != (Exact{"1114", "21"}) || *r.Composite.Display != "53.0" {
		t.Fatal(r.Composite)
	}
}
func TestScoringLegacyFlagNegative(t *testing.T) {
	x := authored()
	x.Enabled["explanation"] = true
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if *r.Composite.Exact != (Exact{"1160", "21"}) || len(r.Composite.Enabled) != 3 {
		t.Fatal("legacy invitation changed current primary", r.Composite)
	}
}
func TestScoringSinglePartialPositive(t *testing.T) {
	x := authored()
	x.Units = x.Units[:1]
	x.Decisions = x.Decisions[:1]
	x.Enabled["classification"] = false
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if *r.Composite.Exact != (Exact{"80", "1"}) || *r.Explanation.Display != "100.0" {
		t.Fatal(r.Composite, r.Explanation)
	}
}
func TestScoringFalseReasonNegative(t *testing.T) {
	x := authored()
	x.Units = x.Units[:1]
	x.Decisions = x.Decisions[:1]
	x.Decisions[0].Correction = fraction(1, 1)
	x.Decisions[0].Explanation = fraction(0, 1)
	x.Enabled["classification"] = false
	r, e := Score(x)
	if e != nil {
		t.Fatal(e)
	}
	if *r.Composite.Display != "100.0" || *r.Explanation.Display != "0.0" {
		t.Fatal("false reason cancelled a valid repair", r.Composite, r.Explanation)
	}
}
