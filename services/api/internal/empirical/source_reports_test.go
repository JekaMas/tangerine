package empirical

import (
	"encoding/json"
	"testing"
)

func sourceReportFixture() Input {
	in := Input{Population: Population{Release: "actual-release", View: "one-source-view", Window: "sentence", Origin: "native"}, Leaves: []string{"project-A"}, AnnotatedLeaves: []string{}}
	for i, labels := range [][]string{{"source-A", "source-B"}, {"source-A"}, {"source-B"}, {}} {
		tokens := int64(5 - i)
		w := Window{ID: string(rune('a' + i)), Annotated: true, Tokens: &tokens, Opportunities: map[string]int64{}}
		for j, label := range labels {
			w.Events = append(w.Events, Event{ID: w.ID + string(rune('0'+j)), Native: label})
		}
		in.Windows = append(in.Windows, w)
	}
	return in
}
func reportFields(t *testing.T, r Report) map[string]any {
	t.Helper()
	b, e := json.Marshal(r)
	if e != nil {
		t.Fatal(e)
	}
	var v map[string]any
	if e = json.Unmarshal(b, &v); e != nil {
		t.Fatal(e)
	}
	return v
}
func TestSourceNativeRelationshipsPositive(t *testing.T) {
	r, e := Build(sourceReportFixture())
	if e != nil {
		t.Fatal(e)
	}
	v := reportFields(t, r)
	pairs, ok := v["native_pairs"].([]any)
	if !ok || len(pairs) != 2 {
		t.Fatal("Native source relationships are absent", v["native_pairs"])
	}
	p := pairs[0].(map[string]any)
	for key, want := range map[string][2]string{"support": {"1", "4"}, "conditional": {"1", "2"}, "lift": {"1", "1"}} {
		exact := p[key].(map[string]any)["exact"].(map[string]any)
		if exact["numerator"] != want[0] || exact["denominator"] != want[1] {
			t.Fatal(key, exact)
		}
	}
	n := v["native_population"].(map[string]any)
	if n["annotated_windows"] != float64(4) || n["inspected_native_tokens"] != float64(14) || n["eligible_events"] != float64(4) {
		t.Fatal("Wrong source denominator", n)
	}
	if len(r.Pairs) != 0 || r.Events != 0 {
		t.Fatal("Unmapped source labels became project mistakes", r)
	}
}
func TestSourceNativeRelationshipsNegative(t *testing.T) {
	in := sourceReportFixture()
	for i := range in.Windows {
		in.Windows[i].Annotated = false
	}
	r, e := Build(in)
	if e != nil {
		t.Fatal(e)
	}
	v := reportFields(t, r)
	n, ok := v["native_population"].(map[string]any)
	if !ok {
		t.Fatal("Native denominator/missingness is absent")
	}
	if n["annotated_windows"] != float64(0) || n["observed_windows"] != float64(4) {
		t.Fatal(n)
	}
	if pairs, ok := v["native_pairs"].([]any); !ok || len(pairs) != 0 {
		t.Fatal("Uninspected source acquired pair rates", v["native_pairs"])
	}
	for _, leaf := range r.NativeFrequencies {
		if leaf.Prevalence.Exact != nil || leaf.Prevalence.Missing == nil {
			t.Fatal("Uninspected absence became zero", leaf)
		}
	}
}
