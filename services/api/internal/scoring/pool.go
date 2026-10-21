package scoring

import (
	"errors"
	"strconv"
)

var ErrPolicy = errors.New("cannot pool different scoring policies")

// Micro pools admitted raw events. Repeated local unit IDs in different cases
// are namespaced; no per-attempt metric or rounded value enters the calculation.
func Micro(inputs []Input, enabled map[string]bool) (Result, error) {
	pooled := Input{Policy: "answer-components-v2", Enabled: enabled, Unresolved: map[string]bool{}, DomainUnresolved: map[string]map[string]bool{}}
	if len(inputs) > 0 {
		pooled.Policy = inputs[0].Policy
	}
	for index, in := range inputs {
		// Policy is part of the cohort, not a default to overwrite at aggregation.
		if in.Policy != pooled.Policy {
			return Result{}, ErrPolicy
		}
		for _, domain := range Domains {
			parts := in.Unresolved
			if in.DomainUnresolved != nil {
				parts = in.DomainUnresolved[domain]
			}
			if pooled.DomainUnresolved[domain] == nil {
				pooled.DomainUnresolved[domain] = map[string]bool{}
			}
			for part, unknown := range parts {
				pooled.DomainUnresolved[domain][part] = pooled.DomainUnresolved[domain][part] || unknown
			}
		}
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
