package scoring

import "strconv"

// Micro pools admitted raw events. Repeated local unit IDs in different cases
// are namespaced; no per-attempt metric or rounded value enters the calculation.
func Micro(inputs []Input, enabled map[string]bool) (Result, error) {
	pooled := Input{Policy: "answer-components-v2", Enabled: enabled, Unresolved: map[string]bool{}}
	for index, in := range inputs {
		prefix := strconv.Itoa(index) + ":"
		for _, u := range in.Units {
			u.ID = prefix + u.ID
			pooled.Units = append(pooled.Units, u)
		}
		for _, d := range in.Decisions {
			d.ID = prefix + d.ID
			if d.Unit != "" {
				d.Unit = prefix + d.Unit
			}
			pooled.Decisions = append(pooled.Decisions, d)
		}
		for key, value := range in.Unresolved {
			pooled.Unresolved[key] = pooled.Unresolved[key] || value
		}
		pooled.DuplicateClaims += in.DuplicateClaims
		pooled.UnresolvedClaims += in.UnresolvedClaims
	}
	return Score(pooled)
}
