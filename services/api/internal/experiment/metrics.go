// Package experiment owns diagnostic arithmetic, never learner grading or inference.
package experiment

import (
	"fmt"
	"math/big"
	"sort"
	"strings"
)

type Metric struct {
	ID          string            `json:"metric_id"`
	Status      string            `json:"status"`
	Numerator   *string           `json:"numerator"`
	Denominator *string           `json:"denominator"`
	Samples     []string          `json:"samples"`
	Value       *string           `json:"value"`
	Missing     *string           `json:"missing_reason"`
	Basis       string            `json:"basis"`
	References  int               `json:"reference_count"`
	Excluded    int               `json:"excluded_count"`
	Stats       map[string]string `json:"sufficient_statistics"`
	Known       *string           `json:"known_subtotal"`
}
type Evidence struct {
	Detected  []string          `json:"detected_events"`
	Aligned   bool              `json:"event_correspondence_available"`
	Stats     map[string]string `json:"statistics"`
	Durations []string          `json:"durations_ms"`
	Tokens    []*string         `json:"token_components"`
	Costs     []*string         `json:"cost_micro_usd"`
	// Semantic statistics may only be supplied by the selected reference scorer/judge.
	Basis   map[string]string `json:"basis"`
	Missing map[string]string `json:"missing"`
}
type rate struct {
	id, n string
	d     []string
	scale int64
}

var rates = []rate{
	{"completion_rate", "completed", []string{"planned"}, 1},
	{"first_response_projection_rate", "projected_first_delivered_reply", []string{"logical_calls_with_delivered_reply"}, 1},
	{"repair_rate", "logical_calls_with_semantic_repair", []string{"initiated_logical_calls"}, 1},
	{"canonical_preservation_rate", "mutation_outputs_with_exact_saved_canonical", []string{"completed_mutation_outputs"}, 1},
	{"mutation_list_consistency_rate", "mutations_with_consistent_span_category_repair_and_surface", []string{"applicable_declared_mutations"}, 1},
	{"request_fulfillment_rate", "satisfied_applicable_request_predicates", []string{"applicable_request_predicates"}, 1},
	{"detection_precision", "TP", []string{"TP", "FP"}, 1},
	{"detection_recall", "TP", []string{"TP", "FN"}, 1},
	{"detection_f1", "TP", []string{"TP", "TP", "FP", "FN"}, 2},
	{"category_accuracy", "correct_reference_category_decisions", []string{"applicable_reference_category_decisions"}, 1},
	{"repair_accuracy", "correct_applicable_repair_propositions", []string{"applicable_reference_repair_propositions"}, 1},
	{"explanation_accuracy", "correct_applicable_explanation_propositions", []string{"applicable_reference_explanation_propositions"}, 1},
	{"feedback_grounding_rate", "supported_factual_items_or_correctly_labelled_practice", []string{"applicable_feedback_items"}, 1},
	{"audio_target_confirmation_rate", "actually_supported_target_realizations", []string{"targets_with_relevant_actual_observation"}, 1},
}
var IDs = func() []string {
	a := []string{}
	for _, r := range rates {
		a = append(a, "llm_lab."+r.id)
	}
	for _, s := range []string{"word_length_relative_deviation", "score_mae_pp", "latency_p50_ms", "latency_p95_ms", "reported_tokens_total", "cost_total_usd", "repeat_detection_jaccard", "leaf_macro_recall"} {
		a = append(a, "llm_lab."+s)
	}
	return a
}()

func ptr(s string) *string { return &s }
func Rat(s string) (*big.Rat, error) {
	v, ok := new(big.Rat).SetString(s)
	if !ok {
		return nil, fmt.Errorf("invalid exact observation %q", s)
	}
	return v, nil
}
func decimal(r *big.Rat) *string {
	d := new(big.Int).Set(r.Denom())
	two, five := 0, 0
	z := new(big.Int)
	for new(big.Int).Mod(d, big.NewInt(2)).Sign() == 0 {
		d.Quo(d, big.NewInt(2))
		two++
	}
	for new(big.Int).Mod(d, big.NewInt(5)).Sign() == 0 {
		d.Quo(d, big.NewInt(5))
		five++
	}
	if d.Cmp(big.NewInt(1)) != 0 {
		return nil
	}
	_ = z
	n := two
	if five > n {
		n = five
	}
	s := r.FloatString(n)
	if strings.Contains(s, ".") {
		s = strings.TrimRight(strings.TrimRight(s, "0"), ".")
	}
	return ptr(s)
}
func empty(id, basis, reason string) Metric {
	return Metric{ID: id, Status: "insufficient_data", Missing: ptr(reason), Basis: basis, Samples: []string{}, Stats: map[string]string{}}
}
func observed(m Metric, n, d *big.Rat) Metric {
	if d.Sign() == 0 {
		if m.References > 0 && (m.Missing == nil || *m.Missing == "no_applicable_observations") {
			m.Missing = ptr("zero_denominator")
		}
		return m
	}
	m.Status = "observed"
	m.Missing = nil
	m.Numerator = decimal(n)
	m.Denominator = decimal(d)
	m.Value = decimal(new(big.Rat).Quo(n, d))
	return m
}
func fractionMetric(m Metric, r *big.Rat) Metric {
	return observed(m, new(big.Rat).SetInt(r.Num()), new(big.Rat).SetInt(r.Denom()))
}
func get(stats map[string]string, k string) (*big.Rat, bool) {
	s, ok := stats[k]
	if !ok {
		return nil, false
	}
	v, e := Rat(s)
	return v, e == nil
}

// Calculate pools unreduced raw statistics. Missing rows stay explicit; latency
// includes all actual attempts while cache inspections have no duration sample.
func Calculate(rows []Evidence) ([]Metric, error) {
	out := make([]Metric, 0, len(IDs))
	for _, id := range IDs {
		basis := "deterministic"
		m := empty(id, basis, "no_applicable_observations")
		evidence := []Evidence{}
		for _, row := range rows {
			if b := row.Basis[id]; b == "self_consistency" {
				m.Basis = b
			} else if b != "" && m.Basis != "self_consistency" {
				m.Basis = b
			}
			if reason := row.Missing[id]; reason != "" {
				m.Missing = ptr(reason)
				m.Excluded++
				continue
			}
			evidence = append(evidence, row)
		}
		name := strings.TrimPrefix(id, "llm_lab.")
		handled := false
		for _, r := range rates {
			if r.id != name {
				continue
			}
			handled = true
			n, d := new(big.Rat), new(big.Rat)
			for _, row := range evidence {
				v, ok := get(row.Stats, r.n)
				dv := new(big.Rat)
				for _, k := range r.d {
					a, has := get(row.Stats, k)
					ok = ok && has
					if has {
						dv.Add(dv, a)
					}
				}
				if !ok {
					m.Excluded++
					continue
				}
				if v.Sign() < 0 || dv.Sign() < 0 {
					return nil, fmt.Errorf("negative population for %s", id)
				}
				n.Add(n, v)
				d.Add(d, dv)
				m.References++
				for k, s := range row.Stats {
					v, e := Rat(s)
					if e != nil {
						return nil, e
					}
					before, _ := Rat(m.Stats[k])
					if before == nil {
						before = new(big.Rat)
					}
					m.Stats[k] = *decimal(before.Add(before, v))
				}
			}
			n.Mul(n, big.NewRat(r.scale, 1))
			m = observed(m, n, d)
			break
		}
		if !handled {
			switch name {
			case "word_length_relative_deviation", "score_mae_pp":
				sum := new(big.Rat)
				for _, row := range evidence {
					nkey, dkey := "surface_word_absolute_deviation", "requested_words"
					if name == "score_mae_pp" {
						nkey, dkey = "absolute_score_error_pp", "paired_reference_scores"
					}
					n, ok := get(row.Stats, nkey)
					if name == "score_mae_pp" {
						if num, found := get(row.Stats, "absolute_score_error_pp_numerator"); found {
							den, has := get(row.Stats, "absolute_score_error_pp_denominator")
							if !has || den.Sign() == 0 {
								return nil, fmt.Errorf("invalid exact score-error denominator")
							}
							n = num.Quo(num, den)
							ok = true
						}
					}
					d, has := get(row.Stats, dkey)
					if !ok || !has || d.Sign() == 0 {
						m.Excluded++
						continue
					}
					sum.Add(sum, new(big.Rat).Quo(n, d))
					m.References++
				}
				if m.References > 0 {
					m = fractionMetric(m, new(big.Rat).Quo(sum, big.NewRat(int64(m.References), 1)))
					m.Stats["applicable_rows"] = fmt.Sprint(m.References)
					if name == "score_mae_pp" {
						m.Stats["absolute_score_error_pp_numerator"] = sum.Num().String()
						m.Stats["absolute_score_error_pp_denominator"] = sum.Denom().String()
						m.Stats["paired_reference_scores"] = fmt.Sprint(m.References)
					}
				}
			case "latency_p50_ms", "latency_p95_ms":
				for _, row := range evidence {
					for _, s := range row.Durations {
						v, e := Rat(s)
						if e != nil || v.Sign() < 0 {
							return nil, fmt.Errorf("invalid duration")
						}
						m.Samples = append(m.Samples, s)
					}
				}
				sort.SliceStable(m.Samples, func(i, j int) bool { a, _ := Rat(m.Samples[i]); b, _ := Rat(m.Samples[j]); return a.Cmp(b) < 0 })
				m.References = len(m.Samples)
				if m.References > 0 {
					percent := 50
					if name == "latency_p95_ms" {
						percent = 95
					}
					m.Status = "observed"
					m.Missing = nil
					m.Value = ptr(m.Samples[(percent*m.References+99)/100-1])
				}
			case "reported_tokens_total", "cost_total_usd":
				sum := new(big.Rat)
				unknown := false
				for _, row := range evidence {
					parts := row.Tokens
					if name == "cost_total_usd" {
						parts = row.Costs
					}
					for _, s := range parts {
						m.References++
						if s == nil {
							unknown = true
							m.Excluded++
							continue
						}
						v, e := Rat(*s)
						if e != nil || v.Sign() < 0 {
							return nil, fmt.Errorf("invalid usage")
						}
						sum.Add(sum, v)
					}
				}
				if name == "cost_total_usd" {
					sum.Quo(sum, big.NewRat(1000000, 1))
				}
				if unknown {
					m.Known = decimal(sum)
					m.Missing = ptr("unknown_receipt_component")
				} else if m.References > 0 {
					m = observed(m, sum, big.NewRat(1, 1))
				}
			case "leaf_macro_recall":
				counts := map[string][2]*big.Rat{}
				for _, row := range evidence {
					for k, s := range row.Stats {
						if !strings.HasPrefix(k, "leaf_tp:") {
							continue
						}
						leaf := strings.TrimPrefix(k, "leaf_tp:")
						tp, e := Rat(s)
						if e != nil {
							return nil, e
						}
						fn, ok := get(row.Stats, "leaf_fn:"+leaf)
						if !ok {
							continue
						}
						p := counts[leaf]
						if p[0] == nil {
							p = [2]*big.Rat{new(big.Rat), new(big.Rat)}
						}
						p[0].Add(p[0], tp)
						p[1].Add(p[1], fn)
						counts[leaf] = p
					}
				}
				sum := new(big.Rat)
				for leaf, p := range counts {
					d := new(big.Rat).Add(p[0], p[1])
					m.Stats["leaf_tp:"+leaf] = *decimal(p[0])
					m.Stats["leaf_fn:"+leaf] = *decimal(p[1])
					if d.Sign() > 0 {
						sum.Add(sum, new(big.Rat).Quo(p[0], d))
						m.References++
					}
				}
				if m.References > 0 {
					m = fractionMetric(m, new(big.Rat).Quo(sum, big.NewRat(int64(m.References), 1)))
				}
			case "repeat_detection_jaccard":
				// Pair counts are produced from aligned detected event sets by RepetitionEvidence.
				sum := new(big.Rat)
				for _, row := range evidence {
					for k, s := range row.Stats {
						if !strings.HasPrefix(k, "jaccard_intersection:") {
							continue
						}
						n, e := Rat(s)
						if e != nil {
							return nil, e
						}
						d, ok := get(row.Stats, strings.Replace(k, "intersection", "union", 1))
						if !ok {
							m.Excluded++
							continue
						}
						if d.Sign() == 0 {
							sum.Add(sum, big.NewRat(1, 1))
						} else {
							sum.Add(sum, new(big.Rat).Quo(n, d))
						}
						m.References++
					}
				}
				if m.References > 0 {
					m = fractionMetric(m, new(big.Rat).Quo(sum, big.NewRat(int64(m.References), 1)))
				}
			}
		}
		out = append(out, m)
	}
	return out, nil
}
