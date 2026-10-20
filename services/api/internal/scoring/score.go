package scoring

import "math/big"

type formula struct {
	id, numerator, denominator, no string
	nscale                         int64
	parts                          []string
}

// These are the27unchanged registry equations. Sums are composed from raw
// sufficient statistics, never from percentages or floating-point values.
var formulas = []formula{
	{"detection.precision", "TP", "", "no_assertions", 1, []string{"TP", "FP"}},
	{"detection.recall", "TP", "G", "no_opportunities", 1, nil},
	{"detection.f1", "TP", "", "no_opportunities", 2, []string{"TP", "TP", "FP", "FN"}},
	{"detection.miss_rate", "FN", "G", "no_opportunities", 1, nil},
	{"detection.false_discovery_rate", "FP", "", "no_assertions", 1, []string{"TP", "FP"}},
	{"classification.coverage", "LC", "TP", "no_opportunities", 1, nil},
	{"classification.family_accuracy", "LF", "LC", "no_assertions", 1, nil},
	{"classification.exact_accuracy", "LE", "LC", "no_assertions", 1, nil},
	{"classification.hierarchical_accuracy", "H", "LC", "no_assertions", 1, nil},
	{"classification.hierarchical_recall", "H", "G", "no_opportunities", 1, nil},
	{"correction.attempt_rate", "CA", "TC", "no_opportunities", 1, nil},
	{"correction.strict_accuracy", "CK", "CA", "no_assertions", 1, nil},
	{"correction.graded_accuracy", "CQ", "CA", "no_assertions", 1, nil},
	{"correction.strict_recall", "CK", "GC", "no_opportunities", 1, nil},
	{"correction.graded_recall", "CQ", "GC", "no_opportunities", 1, nil},
	{"correction.assertion_precision", "CK", "", "no_assertions", 1, []string{"CA", "FC"}},
	{"explanation.coverage", "EA", "TE", "no_opportunities", 1, nil},
	{"explanation.strict_accuracy", "EK", "EA", "no_assertions", 1, nil},
	{"explanation.graded_accuracy", "EQ", "EA", "no_assertions", 1, nil},
	{"explanation.graded_recall", "EQ", "GE", "no_opportunities", 1, nil},
	{"decoy.overcorrection_rate", "DF", "D", "no_opportunities", 1, nil},
	{"decoy.unflagged_rate", "DU", "D", "no_opportunities", 1, nil},
	{"decoy.explicit_acceptability_accuracy", "DA", "", "no_assertions", 1, []string{"DA", "DF"}},
	{"acceptability.explicit_accuracy", "SA", "SN", "no_assertions", 1, nil},
	{"weighted.precision", "WTP", "", "no_assertions", 1, []string{"WTP", "WFP"}},
	{"weighted.recall", "WTP", "", "no_opportunities", 1, []string{"WTP", "WFN"}},
	{"weighted.f1", "WTP", "", "no_opportunities", 2, []string{"WTP", "WTP", "WFP", "WFN"}},
}

func Score(in Input) (Result, error) {
	return score(in, true)
}
func score(in Input, withDomains bool) (Result, error) {
	s, domains, items := count(in)
	s.n["DU"] = s.n["D"] - s.n["DF"]
	get := func(key string) *big.Rat {
		switch key {
		case "H":
			return s.h
		case "CQ":
			return s.cq
		case "EQ":
			return s.eq
		}
		return fraction(s.n[key], 1)
	}
	out := Result{Version: "2.0.0", Attempt: in.Attempt, Case: in.Case, DecisionSHA: in.DecisionSHA, Policy: in.Policy, Status: "complete", Metrics: map[string]Metric{}, Domains: domains, Items: items, Semantic: true, Decisions: []string{}}
	for _, d := range in.Decisions {
		out.Decisions = append(out.Decisions, d.ID)
	}
	for _, f := range formulas {
		n := new(big.Rat).Mul(get(f.numerator), fraction(f.nscale, 1))
		d := new(big.Rat)
		if f.denominator != "" {
			d.Set(get(f.denominator))
		} else {
			for _, part := range f.parts {
				d.Add(d, get(part))
			}
		}
		unknown := in.Unresolved["detection"]
		if f.numerator == "CK" || f.numerator == "CQ" {
			unknown = unknown || s.cUnknown || in.Unresolved["correction"]
		}
		if f.numerator == "EK" || f.numerator == "EQ" {
			unknown = unknown || s.eUnknown || in.Unresolved["explanation"]
		}
		if f.numerator == "LC" || f.denominator == "LC" || f.numerator == "H" {
			unknown = unknown || in.Unresolved["classification"]
		}
		m, err := ratio(n, d, f.no, unknown)
		if err != nil {
			return out, err
		}
		out.Metrics[f.id] = m
	}
	for i := range out.Domains {
		d := &out.Domains[i]
		var err error
		d.Precision, err = ratio(fraction(d.TP, 1), fraction(d.TP+d.FP, 1), "no_assertions", in.Unresolved["detection"])
		if err != nil {
			return out, err
		}
		d.Recall, err = ratio(fraction(d.TP, 1), fraction(d.G, 1), "no_opportunities", in.Unresolved["detection"])
		if err != nil {
			return out, err
		}
		d.F1, err = ratio(fraction(2*d.TP, 1), fraction(2*d.TP+d.FP+d.FN, 1), "no_opportunities", in.Unresolved["detection"])
		if err != nil {
			return out, err
		}
		if withDomains {
			part := in
			part.Units = nil
			part.Decisions = nil
			ids := map[string]bool{}
			for _, u := range in.Units {
				if u.Domain == d.Domain {
					part.Units = append(part.Units, u)
					ids[u.ID] = true
				}
			}
			for _, decision := range in.Decisions {
				if ids[decision.Unit] || decision.Unit == "" && reportingDomain(decision.Category) == d.Domain {
					part.Decisions = append(part.Decisions, decision)
				}
			}
			if in.DomainUnresolved != nil {
				part.Unresolved = in.DomainUnresolved[d.Domain]
			}
			result, err := score(part, false)
			if err != nil {
				return out, err
			}
			d.Metrics = result.Metrics
			d.Precision = d.Metrics["detection.precision"]
			d.Recall = d.Metrics["detection.recall"]
			d.F1 = d.Metrics["detection.f1"]
		}
	}
	if !in.Unresolved["detection"] {
		out.Counts = &Counts{s.n["G"], s.n["TP"], s.n["FN"], s.n["FP"], s.n["D"], s.n["DF"], in.DuplicateClaims, in.UnresolvedClaims}
	}
	if !in.Unresolved["detection"] && !in.Unresolved["classification"] {
		out.Statistics = map[string]any{}
		for _, key := range []string{"G", "D", "TP", "FP", "FN", "LC", "LF", "LE", "GC", "TC", "CA", "CK", "GE", "TE", "EA", "EK", "FC", "DF", "DA", "SN", "SA", "WTP", "WFN", "WFP"} {
			out.Statistics[key] = s.n[key]
		}
		for _, key := range []string{"H", "CQ", "EQ"} {
			v, err := exact(get(key))
			if err != nil {
				return out, err
			}
			out.Statistics[key] = v
		}
		if s.cUnknown || in.Unresolved["correction"] {
			out.Statistics["CK"] = nil
			out.Statistics["CQ"] = nil
		}
		if s.eUnknown || in.Unresolved["explanation"] {
			out.Statistics["EK"] = nil
			out.Statistics["EQ"] = nil
		}
	}
	out.Explanation = out.Metrics["explanation.graded_accuracy"]
	out.Composite = Composite{Enabled: []string{}}
	sum, weights := new(big.Rat), int64(0)
	unresolved := false
	type weightedComponent struct {
		name, metric, opportunity string
		weight                    int64
	}
	components := []weightedComponent{{"detection", "detection.f1", "G", 45}, {"classification", "classification.hierarchical_recall", "G", 15}, {"correction", "correction.graded_recall", "GC", 30}}
	// Only an explicitly frozen original policy enables its historical term.
	if in.Policy == "1.0.0" {
		components = append(components, weightedComponent{"explanation", "explanation.graded_recall", "GE", 10})
	}
	for _, c := range components {
		if !in.Enabled[c.name] || s.n[c.opportunity] == 0 {
			continue
		}
		out.Composite.Enabled = append(out.Composite.Enabled, c.name)
		weights += c.weight
		m := out.Metrics[c.metric]
		if m.Status == "review_required" {
			unresolved = true
			continue
		}
		if m.Numerator != nil {
			r, _ := new(big.Rat).SetString(*m.Numerator + "/" + *m.Denominator)
			sum.Add(sum, new(big.Rat).Mul(r, fraction(c.weight, 1)))
		}
	}
	if unresolved {
		out.Status = "review_required"
		r := "unresolved"
		out.Composite.Reason = &r
	} else if weights == 0 {
		r := "no_opportunities"
		out.Composite.Reason = &r
	} else {
		r := new(big.Rat).Mul(new(big.Rat).Quo(sum, fraction(weights, 1)), fraction(100, 1))
		v, _ := r.Float64()
		display := Display(r, false)
		var err error
		out.Composite.Exact, err = exact(r)
		if err != nil {
			return out, err
		}
		out.Composite.Value = &v
		out.Composite.Display = &display
	}
	return out, nil
}
