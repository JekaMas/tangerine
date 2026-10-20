package scoring

import (
	"math/big"
	"strings"
)

type statistics struct {
	n                  map[string]int64
	h, cq, eq          *big.Rat
	cUnknown, eUnknown bool
}

func newStats() statistics {
	return statistics{n: map[string]int64{}, h: new(big.Rat), cq: new(big.Rat), eq: new(big.Rat)}
}
func reportingDomain(category string) string {
	for _, d := range Domains {
		if category == d || strings.HasPrefix(category, d+".") {
			return d
		}
	}
	return "unattributed_fp"
}
func hierarchy(pred string, gold []string) *big.Rat {
	best := new(big.Rat)
	if pred == "" {
		return best
	}
	p := strings.Split(pred, ".")
	for _, g := range gold {
		x := strings.Split(g, ".")
		common := 0
		for common < len(p) && common < len(x) && p[common] == x[common] {
			common++
		}
		v := fraction(int64(2*common), int64(len(p)+len(x)))
		if v.Cmp(best) > 0 {
			best = v
		}
	}
	return best
}
func count(in Input) (statistics, []DomainResult, []Item) {
	s := newStats()
	decisions := map[string][]Decision{}
	domains := map[string]*DomainResult{}
	for _, d := range Domains {
		domains[d] = &DomainResult{Domain: d}
	}
	for _, d := range in.Decisions {
		if d.Unit != "" {
			decisions[d.Unit] = append(decisions[d.Unit], d)
		}
	}
	items := []Item{}
	for _, u := range in.Units {
		n := s.n
		domain := domains[u.Domain]
		if u.Kind == "true_error" {
			n["G"]++
			domain.G++
			n["WFN"] += u.Weight
			if u.Correction {
				n["GC"]++
			}
			if u.Explanation {
				n["GE"]++
			}
		} else {
			n["D"]++
		}
		detected, flagged, accepted := false, false, false
		ids := []string{}
		kind := "missed"
		if u.Kind != "true_error" {
			kind = "unjudged_control"
		}
		for _, d := range decisions[u.ID] {
			ids = append(ids, d.ID)
			switch d.Verdict {
			case "matched_error":
				if detected {
					continue
				}
				detected = true
				n["TP"]++
				domain.TP++
				n["WTP"] += u.Weight
				n["WFN"] -= u.Weight
				n["SN"]++
				n["SA"]++
				kind = "detected"
				if d.Category != "" {
					n["LC"]++
					if reportingDomain(d.Category) == u.Domain {
						n["LF"]++
					}
					for _, g := range u.Accepted {
						if g == d.Category {
							n["LE"]++
							break
						}
					}
					s.h.Add(s.h, hierarchy(d.Category, u.Accepted))
				}
				if u.Correction {
					n["TC"]++
					if d.CorrectionSupplied {
						n["CA"]++
						if d.Correction == nil {
							s.cUnknown = true
						} else {
							s.cq.Add(s.cq, d.Correction)
							if d.Correction.Cmp(fraction(1, 1)) == 0 {
								n["CK"]++
							}
						}
					}
				}
				if u.Explanation {
					n["TE"]++
					if d.ExplanationSupplied {
						n["EA"]++
						if d.Explanation == nil {
							s.eUnknown = true
						} else {
							s.eq.Add(s.eq, d.Explanation)
							if d.Explanation.Cmp(fraction(1, 1)) == 0 {
								n["EK"]++
							}
						}
					}
				}
			case "false_positive":
				if flagged {
					continue
				}
				flagged = true
				n["FP"]++
				n["DF"]++
				domain.FP++
				n["SN"]++
				kind = "false_positive"
				if d.CorrectionSupplied {
					n["FC"]++
				}
			case "confirmed_acceptable":
				if accepted {
					continue
				}
				accepted = true
				n["DA"]++
				n["SN"]++
				n["SA"]++
				kind = "acceptable"
			case "wrong_acceptance":
				n["SN"]++
				kind = "wrong_acceptance"
			case "unresolved":
				kind = "pending"
			}
		}
		if in.Unresolved["detection"] && (kind == "missed" || kind == "wrong_acceptance" || kind == "unjudged_control") {
			kind = "pending"
		}
		items = append(items, Item{Unit: u.ID, Kind: kind, Category: u.Category, DecisionIDs: ids})
	}
	for _, d := range in.Decisions {
		if d.Unit == "" && d.Verdict == "false_positive" {
			s.n["FP"]++
			domains[reportingDomain(d.Category)].FP++
			if d.CorrectionSupplied {
				s.n["FC"]++
			}
			items = append(items, Item{Kind: "false_positive", Category: d.Category, DecisionIDs: []string{d.ID}})
		}
	}
	s.n["FN"] = s.n["G"] - s.n["TP"]
	s.n["WFP"] = s.n["FP"]
	rows := []DomainResult{}
	for _, name := range Domains {
		d := domains[name]
		d.FN = d.G - d.TP
		rows = append(rows, *d)
	}
	return s, rows, items
}
