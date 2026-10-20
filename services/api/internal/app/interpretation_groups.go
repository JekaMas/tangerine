package app

// Consolidation preserves all members and combines actual compatible components.
// It never picks the highest-scoring correction or turns a false reason into a
// wrong detection. Numeric credit remains the native scorer's next owner.
import "strings"

type SemanticGroup struct {
	Representative string            `json:"representative_claim_id"`
	Members        []string          `json:"member_claim_ids"`
	Unit           *string           `json:"unit_id"`
	Stance         string            `json:"stance"`
	Category       *string           `json:"category_id"`
	Correction     SemanticComponent `json:"correction"`
	Explanation    SemanticComponent `json:"explanation"`
}

func mergeSemanticComponent(a, b SemanticComponent, unit map[string]any, reason bool) (SemanticComponent, bool) {
	if !a.Supplied {
		return b, false
	}
	if !b.Supplied {
		return a, false
	}
	out := a
	out.Additional = append(append([]ComponentAssertion{}, a.Additional...), b.Additional...)
	merge := func(a, b []string) []string {
		out := []string{}
		seen := map[string]bool{}
		for _, v := range append(append([]string{}, a...), b...) {
			if !seen[v] {
				seen[v] = true
				out = append(out, v)
			}
		}
		return out
	}
	out.Satisfied = merge(a.Satisfied, b.Satisfied)
	out.Violated = merge(a.Violated, b.Violated)
	out.Evidence = merge(a.Evidence, b.Evidence)
	if !reason && optionalID(a.Option) != optionalID(b.Option) {
		r := "unclear_meaning"
		out.Status = "unresolved"
		out.Unresolved = &r
		return out, true
	}
	bad := len(out.Violated) > 0
	unknown := a.Unresolved != nil || b.Unresolved != nil
	rejectedAndAccepted := (a.Status == "rejected" && b.Status == "accepted") || (a.Status == "accepted" && b.Status == "rejected")
	for _, x := range out.Additional {
		bad = bad || x.Judgment == "unsupported"
		unknown = unknown || x.Judgment == "unknown"
	}
	if bad {
		out.Status = "rejected"
		out.Unresolved = nil
		return out, false
	}
	if !reason && rejectedAndAccepted {
		r := "unclear_meaning"
		out.Status = "unresolved"
		out.Unresolved = &r
		return out, true
	}
	if unknown {
		r := "unclear_meaning"
		out.Status = "unresolved"
		out.Unresolved = &r
		return out, false
	}
	required := map[string]bool{}
	if unit != nil {
		if reason {
			required = propositionSet(unit["rationale_required_propositions"])
		} else {
			for _, v := range unit["corrections"].([]any) {
				o := v.(map[string]any)
				if o["id"] == optionalID(out.Option) {
					required = propositionSet(o["required_propositions"])
				}
			}
		}
	}
	if len(required) > 0 {
		if len(out.Satisfied) == len(required) {
			out.Status = "accepted"
		} else if len(out.Satisfied) > 0 {
			out.Status = "partial"
		} else {
			out.Status = "rejected"
		}
	}
	return out, false
}
func consolidateMapping(claims CanonicalExtraction, m SemanticMapping, key map[string]any, enabled map[string]any) ([]SemanticGroup, []InterpretationIssue) {
	groups := []SemanticGroup{}
	issues := []InterpretationIssue{}
	index := map[string]int{}
	groupByClaim := map[string]int{}
	categoryConflict := map[int]bool{}
	byClaim := map[string]CanonicalClaim{}
	units := map[string]map[string]any{}
	stanceByUnit := map[string]string{}
	for _, c := range claims.Claims {
		byClaim[c.ID] = c
	}
	for _, v := range key["units"].([]any) {
		u := v.(map[string]any)
		units[u["id"].(string)] = u
	}
	add := func(g SemanticGroup, part string, blocks bool) {
		ids := []string{}
		if g.Unit != nil {
			ids = append(ids, *g.Unit)
		}
		issues = append(issues, InterpretationIssue{"contradiction", append([]string{}, g.Members...), ids, []string{part}, blocks, "Unretracted endorsed statements disagree in their " + part + " component; compatible supported components are retained."})
	}
	for _, d := range m.Decisions {
		c := byClaim[d.Claim]
		if c.Group != c.ID {
			if i, exists := groupByClaim[c.Group]; exists {
				groups[i].Members = append(groups[i].Members, c.ID)
			}
			continue
		}
		if !c.Active || d.Decision == "ignore" {
			continue
		}
		groupKey := d.Claim
		if d.Unit != nil {
			groupKey = *d.Unit + ":" + c.Stance
		}
		i, exists := index[groupKey]
		if !exists {
			g := SemanticGroup{Representative: d.Claim, Members: []string{d.Claim}, Unit: d.Unit, Stance: c.Stance, Category: d.Category, Correction: d.Correction, Explanation: d.Explanation}
			index[groupKey] = len(groups)
			groupByClaim[c.ID] = len(groups)
			groups = append(groups, g)
			if d.Unit != nil {
				if earlier, ok := stanceByUnit[*d.Unit]; ok && earlier != c.Stance {
					add(g, "detection", true)
				}
				stanceByUnit[*d.Unit] = c.Stance
			}
			continue
		}
		groupByClaim[c.ID] = i
		g := &groups[i]
		g.Members = append(g.Members, d.Claim)
		if d.Duplicate != nil {
			continue
		}
		if !categoryConflict[i] && g.Category == nil {
			g.Category = d.Category
		} else if !categoryConflict[i] && d.Category != nil && *d.Category != *g.Category {
			if strings.HasPrefix(*d.Category, *g.Category+".") {
				g.Category = d.Category
			} else if !strings.HasPrefix(*g.Category, *d.Category+".") {
				g.Category = nil
				categoryConflict[i] = true
				add(*g, "classification", enabled["classification"] == true)
			}
		}
		var incompatible bool
		g.Correction, incompatible = mergeSemanticComponent(g.Correction, d.Correction, units[optionalID(g.Unit)], false)
		if incompatible {
			add(*g, "correction", enabled["correction"] == true)
		}
		g.Explanation, _ = mergeSemanticComponent(g.Explanation, d.Explanation, units[optionalID(g.Unit)], true)
	}
	return groups, issues
}
