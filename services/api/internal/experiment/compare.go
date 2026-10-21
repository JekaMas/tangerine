package experiment

import (
	"fmt"
	"math/big"
)

type Row struct {
	Case       string   `json:"case_id"`
	Variant    string   `json:"variant_id"`
	Repetition int      `json:"repetition"`
	Status     string   `json:"status"`
	Receipts   []string `json:"receipt_ids"`
	Traces     []string `json:"trace_ids"`
	Output     *string  `json:"output_asset_id"`
	Metrics    []Metric `json:"metrics"`
	Error      *string  `json:"error_code"`
	Export     string   `json:"export_status"`
}
type Rational struct {
	Numerator   string `json:"numerator"`
	Denominator string `json:"denominator"`
}
type RowKey struct {
	Case       string `json:"case_id"`
	Repetition int    `json:"repetition"`
}
type Exclusion struct {
	Key    RowKey `json:"key"`
	Reason string `json:"reason"`
}
type Comparison struct {
	Baseline       string      `json:"baseline_variant_id"`
	Candidate      string      `json:"candidate_variant_id"`
	Metric         string      `json:"metric_id"`
	Paired         []RowKey    `json:"paired_row_keys"`
	Excluded       []Exclusion `json:"excluded_row_keys"`
	BaselineValue  *Rational   `json:"baseline_value"`
	CandidateValue *Rational   `json:"candidate_value"`
	Delta          *Rational   `json:"candidate_minus_baseline"`
	Missing        *string     `json:"missing_reason"`
}

func exact(r *big.Rat) *Rational {
	if r == nil {
		return nil
	}
	return &Rational{r.Num().String(), r.Denom().String()}
}
func metricValue(m Metric) *big.Rat {
	if m.Status != "observed" {
		return nil
	}
	if m.Numerator != nil && m.Denominator != nil {
		n, _ := Rat(*m.Numerator)
		d, _ := Rat(*m.Denominator)
		if n != nil && d != nil && d.Sign() != 0 {
			return n.Quo(n, d)
		}
	}
	if m.Value != nil {
		r, _ := Rat(*m.Value)
		return r
	}
	return nil
}
func find(ms []Metric, id string) Metric {
	for _, m := range ms {
		if m.ID == id {
			return m
		}
	}
	return empty(id, "deterministic", "missing_metric")
}

// Compare receives rows from one frozen experiment. It selects the same tuple
// population before recalculating either side; failed/unavailable rows stay named.
func Compare(rows []Row, evidence map[string]Evidence, baseline, candidate string) ([]Comparison, error) {
	out := []Comparison{}
	right := map[RowKey]Row{}
	for _, row := range rows {
		if row.Variant == candidate {
			right[RowKey{row.Case, row.Repetition}] = row
		}
	}
	for _, id := range IDs {
		c := Comparison{Baseline: baseline, Candidate: candidate, Metric: id, Paired: []RowKey{}, Excluded: []Exclusion{}}
		a, b := []Evidence{}, []Evidence{}
		for _, row := range rows {
			if row.Variant != baseline {
				continue
			}
			key := RowKey{row.Case, row.Repetition}
			other, ok := right[key]
			if id == "llm_lab.completion_rate" && ok {
				ea, oka := evidence[Key(row)]
				eb, okb := evidence[Key(other)]
				if !oka {
					ea = completionEvidence(row)
				}
				if !okb {
					eb = completionEvidence(other)
				}
				a = append(a, ea)
				b = append(b, eb)
				c.Paired = append(c.Paired, key)
				continue
			}
			if !ok || row.Status != "complete" || other.Status != "complete" {
				c.Excluded = append(c.Excluded, Exclusion{key, "incomplete_pair"})
				continue
			}
			if id == "llm_lab.repeat_detection_jaccard" {
				ea, oka := evidence[Key(row)]
				eb, okb := evidence[Key(other)]
				if oka && okb && ea.Aligned && eb.Aligned {
					a = append(a, ea)
					b = append(b, eb)
					c.Paired = append(c.Paired, key)
				} else {
					c.Excluded = append(c.Excluded, Exclusion{key, "event_correspondence_unavailable"})
				}
				continue
			}
			if metricValue(find(row.Metrics, id)) == nil || metricValue(find(other.Metrics, id)) == nil {
				c.Excluded = append(c.Excluded, Exclusion{key, "metric_unavailable"})
				continue
			}
			ea, oka := evidence[Key(row)]
			eb, okb := evidence[Key(other)]
			if !oka || !okb {
				return nil, fmt.Errorf("missing raw comparison evidence")
			}
			c.Paired = append(c.Paired, key)
			a = append(a, ea)
			b = append(b, eb)
		}
		if id == "llm_lab.repeat_detection_jaccard" {
			a = withPairEvidence(c.Paired, a, baseline)
			b = withPairEvidence(c.Paired, b, candidate)
		}
		am, e := Calculate(a)
		if e != nil {
			return nil, e
		}
		bm, e := Calculate(b)
		if e != nil {
			return nil, e
		}
		av, bv := metricValue(find(am, id)), metricValue(find(bm, id))
		c.BaselineValue = exact(av)
		c.CandidateValue = exact(bv)
		if av != nil && bv != nil {
			c.Delta = exact(new(big.Rat).Sub(bv, av))
		} else {
			c.Missing = ptr("no_common_applicable_population")
		}
		out = append(out, c)
	}
	return out, nil
}
func Key(r Row) string { return fmt.Sprintf("%s/%s/%d", r.Case, r.Variant, r.Repetition) }

type Detection struct {
	Case, Variant     string
	Repetition        int
	Complete, Aligned bool
	Events            []string
}

// RepetitionEvidence uses all unordered completed pairs, with no invented alignment
// for separately generated events. Both-empty aligned sets have similarity one.
func RepetitionEvidence(rows []Detection) Evidence {
	out := Evidence{Stats: map[string]string{}}
	for i, a := range rows {
		for j := i + 1; j < len(rows); j++ {
			b := rows[j]
			if a.Case != b.Case || a.Variant != b.Variant || !a.Complete || !b.Complete {
				continue
			}
			if !a.Aligned || !b.Aligned {
				if out.Missing == nil {
					out.Missing = map[string]string{}
				}
				out.Missing["llm_lab.repeat_detection_jaccard"] = "event_correspondence_unavailable"
				continue
			}
			set := map[string]bool{}
			for _, s := range a.Events {
				set[s] = true
			}
			union := map[string]bool{}
			for k := range set {
				union[k] = true
			}
			intersection := map[string]bool{}
			for _, s := range b.Events {
				union[s] = true
				if set[s] {
					intersection[s] = true
				}
			}
			suffix := fmt.Sprintf("%s:%d:%d", a.Case, a.Repetition, b.Repetition)
			out.Stats["jaccard_intersection:"+suffix] = fmt.Sprint(len(intersection))
			out.Stats["jaccard_union:"+suffix] = fmt.Sprint(len(union))
		}
	}
	return out
}

func withPairEvidence(keys []RowKey, es []Evidence, variant string) []Evidence {
	if len(es) == 0 {
		return es
	}
	d := []Detection{}
	for i, e := range es {
		d = append(d, Detection{Case: keys[i].Case, Variant: variant, Repetition: keys[i].Repetition, Complete: true, Aligned: e.Aligned, Events: e.Detected})
	}
	pairs := RepetitionEvidence(d)
	out := append([]Evidence{}, es...)
	first := map[string]string{}
	for k, v := range out[0].Stats {
		first[k] = v
	}
	for k, v := range pairs.Stats {
		first[k] = v
	}
	out[0].Stats = first
	return out
}

func completionEvidence(row Row) Evidence {
	completed := "0"
	if row.Status == "complete" {
		completed = "1"
	}
	return Evidence{Stats: map[string]string{"planned": "1", "completed": completed}}
}
