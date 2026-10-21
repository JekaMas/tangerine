package experiment

import (
	"fmt"
	"testing"
)

func sampleEvidence() Evidence {
	s := map[string]string{}
	for _, r := range rates {
		s[r.n] = "2"
		for _, d := range r.d {
			s[d] = "4"
		}
	}
	s["TP"] = "2"
	s["FP"] = "2"
	s["FN"] = "2"
	s["completed"] = "2"
	s["planned"] = "4"
	s["surface_word_absolute_deviation"] = "20"
	s["requested_words"] = "100"
	s["absolute_score_error_pp"] = "6"
	s["paired_reference_scores"] = "1"
	s["leaf_tp:A"] = "1"
	s["leaf_fn:A"] = "3"
	s["leaf_tp:B"] = "3"
	s["leaf_fn:B"] = "1"
	s["jaccard_intersection:1"] = "1"
	s["jaccard_union:1"] = "2"
	return Evidence{Stats: s, Durations: []string{"30", "10", "20"}, Tokens: []*string{ptr("12"), ptr("8")}, Costs: []*string{ptr("1250000"), ptr("250000")}}
}
func TestExperimentMetricPositive(t *testing.T) {
	e := sampleEvidence()
	got, err := Calculate([]Evidence{e})
	if err != nil {
		t.Fatal(err)
	}
	want := map[string]string{"word_length_relative_deviation": "1/5", "score_mae_pp": "6", "latency_p50_ms": "20", "latency_p95_ms": "30", "reported_tokens_total": "20", "cost_total_usd": "3/2", "leaf_macro_recall": "1/2", "repeat_detection_jaccard": "1/2"}
	for _, m := range got {
		t.Run(m.ID, func(t *testing.T) {
			w := want[m.ID[len("llm_lab."):]]
			if w == "" {
				w = "1/2"
			}
			a := metricValue(m)
			b, _ := Rat(w)
			if a == nil || a.Cmp(b) != 0 {
				t.Fatalf("%s: got %+v expected %s", m.ID, m, w)
			}
		})
	}
}
func TestExperimentMetricNegative(t *testing.T) {
	got, err := Calculate([]Evidence{})
	if err != nil {
		t.Fatal(err)
	}
	for _, m := range got {
		t.Run(m.ID, func(t *testing.T) {
			if m.Status != "insufficient_data" || m.Value != nil || m.Missing == nil {
				t.Fatalf("invented metric %+v", m)
			}
		})
	}
}
func TestExperimentRawPoolingPositive(t *testing.T) {
	a := Evidence{Stats: map[string]string{"TP": "1", "FP": "0", "FN": "0"}}
	b := Evidence{Stats: map[string]string{"TP": "0", "FP": "9", "FN": "9"}}
	m, e := Calculate([]Evidence{a, b})
	if e != nil {
		t.Fatal(e)
	}
	v := metricValue(find(m, "llm_lab.detection_f1"))
	w, _ := Rat("1/10")
	if v.Cmp(w) != 0 {
		t.Fatal(v)
	}
	if *find(m, "llm_lab.detection_f1").Denominator != "20" {
		t.Fatal("lost population")
	}
}
func TestExperimentUnknownUsageNegative(t *testing.T) {
	e := sampleEvidence()
	e.Tokens = append(e.Tokens, nil)
	e.Costs = []*string{nil, ptr("0")}
	m, err := Calculate([]Evidence{e})
	if err != nil {
		t.Fatal(err)
	}
	for _, id := range []string{"reported_tokens_total", "cost_total_usd"} {
		x := find(m, "llm_lab."+id)
		if x.Status != "insufficient_data" || x.Value != nil || x.Known == nil {
			t.Fatal(x)
		}
	}
	if *find(m, "llm_lab.reported_tokens_total").Known != "20" || *find(m, "llm_lab.cost_total_usd").Known != "0" {
		t.Fatal(m)
	}
}
func TestExperimentMeanPositive(t *testing.T) {
	a := Evidence{Stats: map[string]string{"surface_word_absolute_deviation": "1", "requested_words": "3"}}
	b := Evidence{Stats: map[string]string{"surface_word_absolute_deviation": "0", "requested_words": "100"}}
	ms, e := Calculate([]Evidence{a, b})
	if e != nil {
		t.Fatal(e)
	}
	m := find(ms, "llm_lab.word_length_relative_deviation")
	if *m.Numerator != "1" || *m.Denominator != "6" || m.Value != nil {
		t.Fatal(m)
	}
}
func TestExperimentDurationNegative(t *testing.T) {
	if _, e := Calculate([]Evidence{{Durations: []string{"-1"}}}); e == nil {
		t.Fatal("negative latency accepted")
	}
}
func TestExperimentPairsPositive(t *testing.T) {
	e := RepetitionEvidence([]Detection{{"c", "v", 1, true, true, []string{"A"}}, {"c", "v", 2, true, true, []string{"A", "B"}}, {"c", "v", 3, true, true, []string{}}})
	m, err := Calculate([]Evidence{e})
	if err != nil {
		t.Fatal(err)
	}
	v := find(m, "llm_lab.repeat_detection_jaccard")
	if *v.Numerator != "1" || *v.Denominator != "6" || v.References != 3 {
		t.Fatal(v)
	}
}
func TestExperimentAlignmentNegative(t *testing.T) {
	e := RepetitionEvidence([]Detection{{"c", "v", 1, true, false, []string{"A"}}, {"c", "v", 2, true, true, []string{"A"}}})
	m, _ := Calculate([]Evidence{e})
	if find(m, "llm_lab.repeat_detection_jaccard").Status != "insufficient_data" {
		t.Fatal("invented alignment")
	}
}
func TestExperimentComparisonPositive(t *testing.T) {
	rows := []Row{}
	evidence := map[string]Evidence{}
	for i, v := range []string{"a", "b"} {
		e := Evidence{Stats: map[string]string{"TP": fmt.Sprint(i + 1), "FP": "0", "FN": fmt.Sprint(2 - i)}}
		m, _ := Calculate([]Evidence{e})
		r := Row{Case: "c", Variant: v, Repetition: 1, Status: "complete", Metrics: m}
		rows = append(rows, r)
		evidence[Key(r)] = e
	}
	cs, e := Compare(rows, evidence, "a", "b")
	if e != nil {
		t.Fatal(e)
	}
	for _, c := range cs {
		if c.Metric == "llm_lab.detection_recall" {
			if c.Delta == nil || c.Delta.Numerator != "1" || c.Delta.Denominator != "3" || len(c.Paired) != 1 {
				t.Fatal(c)
			}
		}
	}
}
func TestExperimentComparisonNegative(t *testing.T) {
	rows := []Row{{Case: "c", Variant: "a", Repetition: 1, Status: "complete"}, {Case: "c", Variant: "b", Repetition: 1, Status: "failed"}}
	cs, e := Compare(rows, nil, "a", "b")
	if e != nil {
		t.Fatal(e)
	}
	for _, c := range cs {
		if c.Metric == "llm_lab.completion_rate" {
			if len(c.Paired) != 1 {
				t.Fatal(c)
			}
			continue
		}
		if c.Delta != nil || len(c.Excluded) != 1 || len(c.Paired) != 0 {
			t.Fatal(c)
		}
	}
}
func TestExperimentCompletionComparisonNegative(t *testing.T) {
	a := Evidence{Stats: map[string]string{"planned": "1", "completed": "1"}}
	b := Evidence{Stats: map[string]string{"planned": "1", "completed": "0"}}
	am, _ := Calculate([]Evidence{a})
	bm, _ := Calculate([]Evidence{b})
	rows := []Row{{Case: "c", Variant: "a", Repetition: 1, Status: "complete", Metrics: am}, {Case: "c", Variant: "b", Repetition: 1, Status: "failed", Metrics: bm}}
	cs, e := Compare(rows, map[string]Evidence{Key(rows[0]): a, Key(rows[1]): b}, "a", "b")
	if e != nil {
		t.Fatal(e)
	}
	for _, c := range cs {
		if c.Metric == "llm_lab.completion_rate" && (c.Delta == nil || c.Delta.Numerator != "-1" || c.Delta.Denominator != "1" || len(c.Paired) != 1) {
			t.Fatal("failure hidden from completion", c)
		}
	}
}
func TestExperimentRepeatComparisonPositive(t *testing.T) {
	rows := []Row{}
	evidence := map[string]Evidence{}
	for _, v := range []string{"a", "b"} {
		for n := 1; n <= 2; n++ {
			events := []string{"A"}
			if v == "a" && n == 2 {
				events = []string{"B"}
			}
			e := Evidence{Stats: map[string]string{}, Aligned: true, Detected: events}
			ms, _ := Calculate([]Evidence{e})
			r := Row{Case: "c", Variant: v, Repetition: n, Status: "complete", Metrics: ms}
			rows = append(rows, r)
			evidence[Key(r)] = e
		}
	}
	cs, e := Compare(rows, evidence, "a", "b")
	if e != nil {
		t.Fatal(e)
	}
	for _, c := range cs {
		if c.Metric == "llm_lab.repeat_detection_jaccard" && (c.Delta == nil || c.Delta.Numerator != "1" || c.Delta.Denominator != "1" || len(c.Paired) != 2) {
			t.Fatal("repetition pairs lost", c)
		}
	}
}

func TestExperimentMixedBasisNegative(t *testing.T) {
	a := Evidence{Stats: map[string]string{"TP": "1", "FP": "0", "FN": "0"}, Basis: map[string]string{"llm_lab.detection_recall": "self_consistency"}}
	b := Evidence{Stats: map[string]string{"TP": "1", "FP": "0", "FN": "0"}, Basis: map[string]string{"llm_lab.detection_recall": "deterministic"}}
	ms, e := Calculate([]Evidence{a, b})
	if e != nil {
		t.Fatal(e)
	}
	if find(ms, "llm_lab.detection_recall").Basis != "self_consistency" {
		t.Fatal("self labels promoted to independent evidence")
	}
}
