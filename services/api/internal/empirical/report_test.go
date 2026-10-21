package empirical

import (
	"fmt"
	"math"
	"testing"
)

func sp(s string) *string { return &s }
func ip(n int64) *int64   { return &n }
func bp(b bool) *bool     { return &b }
func fixture() Input {
	return Input{Population: Population{Release: "FCE", View: "native-annotator-0", Window: "sentence", Origin: "native"}, Leaves: []string{"A", "B", "C"}, Windows: []Window{{ID: "1", Annotated: true, Tokens: ip(10), Events: []Event{{ID: "e1", Native: "V", Leaf: sp("A"), Secondary: []string{"B"}}, {ID: "e2", Native: "N", Leaf: sp("B")}}, Opportunities: map[string]int64{"A": 2, "B": 1}}, {ID: "2", Annotated: true, Tokens: ip(10), Events: []Event{{ID: "e3", Native: "V", Leaf: sp("A")}}, Opportunities: map[string]int64{"A": 2, "B": 1}}, {ID: "3", Annotated: true, Tokens: ip(10), Events: []Event{}, Opportunities: map[string]int64{"A": 2, "B": 1}}, {ID: "4", Annotated: false, Events: []Event{}}}}
}
func TestEmpiricalPopulationPositive(t *testing.T) {
	r, e := Build(fixture())
	if e != nil {
		t.Fatal(e)
	}
	if r.Annotated != 3 || r.Unannotated != 1 || r.Events != 3 || len(r.Leaves) != 3 || r.Native["V"] != 2 {
		t.Fatal(r)
	}
	a := r.Leaves[0]
	if a.Events != 2 || a.Share.Exact.Numerator != "2" || a.Share.Exact.Denominator != "3" || a.Prevalence.Denominator != "3" || a.Opportunity.Exact.Denominator != "3" || a.Density.Exact.Numerator != "200" || a.Density.Exact.Denominator != "3" {
		t.Fatal(a)
	}
}
func TestEmpiricalMissingNegative(t *testing.T) {
	in := fixture()
	in.Windows = []Window{{ID: "unlabelled", Tokens: ip(99), Annotated: false}}
	r, e := Build(in)
	if e != nil {
		t.Fatal(e)
	}
	for _, l := range r.Leaves {
		if l.Prevalence.Exact != nil || l.Opportunity.Exact != nil || l.Density.Exact != nil {
			t.Fatal("invented absence", l)
		}
	}
}
func TestEmpiricalRelationshipsPositive(t *testing.T) {
	r, e := Build(fixture())
	if e != nil {
		t.Fatal(e)
	}
	if len(r.Pairs) != 2 {
		t.Fatal(r.Pairs)
	}
	p := r.Pairs[0]
	if p.Count != 1 || p.Support.Exact.Denominator != "3" || p.Conditional.Exact.Denominator != "2" || p.Lift.Exact.Numerator != "3" || p.Lift.Exact.Denominator != "2" {
		t.Fatal(p)
	}
}
func TestEmpiricalSecondaryPairNegative(t *testing.T) {
	in := fixture()
	in.Windows = in.Windows[:1]
	in.Windows[0].Events = in.Windows[0].Events[:1]
	r, e := Build(in)
	if e != nil {
		t.Fatal(e)
	}
	if len(r.Pairs) != 0 || r.Leaves[1].Secondary != 1 || r.Leaves[1].Events != 0 {
		t.Fatal(r)
	}
}
func TestEmpiricalSameCategoryPositive(t *testing.T) {
	in := fixture()
	in.Windows = in.Windows[:1]
	in.Windows[0].Events[1].Leaf = sp("A")
	r, e := Build(in)
	if e != nil {
		t.Fatal(e)
	}
	if len(r.Pairs) != 1 || r.Pairs[0].A != "A" || r.Pairs[0].B != "A" || r.Pairs[0].Count != 1 {
		t.Fatal(r)
	}
}
func TestEmpiricalDuplicateNegative(t *testing.T) {
	in := fixture()
	in.Windows[0].Events = append(in.Windows[0].Events, in.Windows[0].Events[0])
	if _, e := Build(in); e == nil {
		t.Fatal("double counted event")
	}
}
func TestEmpiricalConfusionPositive(t *testing.T) {
	in := fixture()
	in.Decisions = []Decision{{"A", "A"}, {"A", "unknown"}, {"A", "abstention"}}
	r, e := Build(in)
	if e != nil {
		t.Fatal(e)
	}
	if len(r.Confusion) != 3 {
		t.Fatal(r)
	}
	for _, c := range r.Confusion {
		if c.Proportion.Denominator != "3" {
			t.Fatal(c)
		}
	}
}
func TestEmpiricalUnknownLabelNegative(t *testing.T) {
	in := fixture()
	in.Windows[0].Events[0].Leaf = sp("ZZ")
	if _, e := Build(in); e == nil {
		t.Fatal("invented mapping")
	}
}
func TestEmpiricalDifficultyPositive(t *testing.T) {
	rows := []Attempt{}
	for i := 0; i < 100; i++ {
		rows = append(rows, Attempt{ID: fmt.Sprint(i), Actor: fmt.Sprint(i), Origin: "genuine_teacher", Case: "c1", Policy: "v2", First: true, Success: bp(true)})
	}
	r, e := DifficultyReport(rows)
	if e != nil {
		t.Fatal(e)
	}
	if r.Rating != "easy" || r.Trials != 100 || r.Successes != 100 {
		t.Fatal(r)
	}
	var lo float64
	fmt.Sscan(*r.Lower, &lo)
	if math.Abs(lo-.9630065018) > 1e-9 {
		t.Fatal(lo)
	}
}
func TestEmpiricalMachineDifficultyNegative(t *testing.T) {
	rows := []Attempt{{ID: "model", Actor: "m", Origin: "model", Case: "c", Policy: "p", First: true, Success: bp(true)}}
	r, e := DifficultyReport(rows)
	if e != nil {
		t.Fatal(e)
	}
	if r.Rating != "unrated" || r.Trials != 0 || r.Lower != nil {
		t.Fatal(r)
	}
}
func TestEmpiricalFollowupPositive(t *testing.T) {
	rows := []Attempt{{ID: "a", Actor: "one", Origin: "genuine_teacher", Case: "c", Policy: "v2", First: true, Success: bp(false)}, {ID: "b", Actor: "one", Origin: "genuine_teacher", Case: "c", Policy: "v2", Success: bp(true), Before: sp("a")}}
	r, e := DifficultyReport(rows)
	if e != nil {
		t.Fatal(e)
	}
	if r.Followup.Exact.Numerator != "1" || r.Trials != 1 || r.Rating != "unrated" {
		t.Fatal(r)
	}
}
func TestEmpiricalMixedPolicyNegative(t *testing.T) {
	rows := []Attempt{{ID: "a", Actor: "one", Origin: "genuine_teacher", Case: "c", Policy: "v1", First: true, Success: bp(true)}, {ID: "b", Actor: "two", Origin: "genuine_teacher", Case: "c", Policy: "v2", First: true, Success: bp(true)}}
	if _, e := DifficultyReport(rows); e == nil {
		t.Fatal("mixed grading populations")
	}
}
func TestEmpiricalUnmappedAbsenceNegative(t *testing.T) {
	in := fixture()
	in.Windows = in.Windows[:1]
	in.Windows[0].Events[0].Leaf = nil
	r, e := Build(in)
	if e != nil {
		t.Fatal(e)
	}
	if r.SourceAnnotated != 1 || r.MappingIncomplete != 1 || r.Annotated != 0 || r.Unmapped != 1 {
		t.Fatal(r)
	}
	for _, l := range r.Leaves {
		if l.Prevalence.Exact != nil {
			t.Fatal("unmapped source became known project absence", l)
		}
	}
	if len(r.NativeFrequencies) != 2 || r.NativeFrequencies[0].Prevalence.Exact == nil {
		t.Fatal("native evidence lost", r.NativeFrequencies)
	}
}
func TestEmpiricalSpanningEventPositive(t *testing.T) {
	in := fixture()
	in.Windows = in.Windows[:2]
	in.Windows[1].Events = []Event{in.Windows[0].Events[0]}
	r, e := Build(in)
	if e != nil {
		t.Fatal(e)
	}
	if r.Events != 2 || r.Leaves[0].Events != 1 || r.Leaves[0].Prevalence.Numerator != "2" || r.Leaves[1].Secondary != 1 {
		t.Fatal("one spanning event duplicated", r)
	}
}
func TestEmpiricalConflictingIdentityNegative(t *testing.T) {
	in := fixture()
	in.Windows[1].Events[0].ID = "e1"
	in.Windows[1].Events[0].Native = "different label"
	if _, e := Build(in); e == nil {
		t.Fatal("ambiguous event counted")
	}
}
func TestEmpiricalUninspectedLeafNegative(t *testing.T) {
	in := fixture()
	in.AnnotatedLeaves = []string{"A"}
	r, e := Build(in)
	if e != nil {
		t.Fatal(e)
	}
	if r.Leaves[0].Prevalence.Exact == nil || r.Leaves[1].Prevalence.Exact != nil || r.Leaves[2].Prevalence.Exact != nil || r.Leaves[1].Prevalence.Missing == nil {
		t.Fatal("source scope became all-leaf absence", r.Leaves)
	}
}
