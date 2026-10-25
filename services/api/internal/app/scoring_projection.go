package app

// This adapter projects admitted source-bound semantic judgments into the pure
// numeric owner. It neither calls an LLM nor revalidates saved stage assets.
import (
	"math/big"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/scoring"
)

func componentCredit(c SemanticComponent, unit map[string]any, reason bool) *big.Rat {
	if !c.Supplied {
		return new(big.Rat)
	}
	if len(c.Violated) > 0 {
		return new(big.Rat)
	}
	unknown := c.Unresolved != nil
	for _, a := range c.Additional {
		if a.Judgment == "unsupported" {
			return new(big.Rat)
		}
		unknown = unknown || a.Judgment == "unknown"
	}
	if unknown {
		return nil
	}
	if c.Status == "rejected" {
		return new(big.Rat)
	}
	required := map[string]bool{}
	if reason {
		required = propositionSet(unit["rationale_required_propositions"])
	} else if options, ok := unit["corrections"].([]any); ok {
		for _, v := range options {
			o := v.(map[string]any)
			if o["id"] == optionalID(c.Option) {
				required = propositionSet(o["required_propositions"])
			}
		}
	}
	if len(required) == 0 {
		return nil
	}
	n := int64(0)
	for _, id := range c.Satisfied {
		if required[id] {
			n++
		}
	}
	return new(big.Rat).SetFrac64(n, int64(len(required)))
}
func scoreInterpretation(record AttemptRecord, resources InterpretationResources, claims CanonicalExtraction, mapping SemanticMapping, issues []InterpretationIssue) (scoring.Result, error) {
	a := record.Attempt
	policy := a["scoring_policy_version"].(string)
	in := scoring.Input{Attempt: a["attempt_id"].(string), Case: a["case_version_id"].(string), DecisionSHA: lab.Hash(mapping), Policy: policy, Enabled: map[string]bool{}, Unresolved: map[string]bool{}}
	for k, v := range a["task_components"].(map[string]any) {
		in.Enabled[k] = v == true
	}
	unresolvedClaims := map[string]bool{}
	trueDetections := map[string]bool{}
	for _, d := range mapping.Decisions {
		if d.Decision == "matched_error" {
			trueDetections[d.Claim] = true
		}
	}
	classificationRelevant := func(issue InterpretationIssue) bool {
		if len(issue.Claims) == 0 {
			return true
		}
		for _, id := range issue.Claims {
			if trueDetections[id] {
				return true
			}
		}
		return false
	}
	for _, issue := range issues {
		if issue.Code == "audit_disagreement" {
			continue
		}
		for _, c := range issue.Components {
			if c == "detection" || c == "key" || c == "classification" && classificationRelevant(issue) {
				if c == "key" {
					c = "detection"
				}
				in.Unresolved[c] = true
			}
		}
		if issue.Blocks && len(issue.Components) == 0 {
			in.Unresolved["detection"] = true
		}
		for _, id := range issue.Claims {
			unresolvedClaims[id] = true
		}
	}
	in.UnresolvedClaims = int64(len(unresolvedClaims))
	units := map[string]map[string]any{}
	for _, v := range resources.Key["units"].([]any) {
		u := v.(map[string]any)
		if u["expected_judgment"] == "excluded" {
			continue
		}
		id := u["id"].(string)
		units[id] = u
		accepted := []string{}
		for _, x := range u["accepted_taxonomy_ids"].([]any) {
			accepted = append(accepted, x.(string))
		}
		in.Units = append(in.Units, scoring.Unit{ID: id, Domain: u["domain"].(string), Category: u["primary_taxonomy_id"].(string), Accepted: accepted, Kind: u["expected_judgment"].(string), Weight: int64(u["weight"].(float64)), Correction: u["correction_eligible"] == true, Explanation: u["explanation_eligible"] == true})
	}
	in.DomainUnresolved = map[string]map[string]bool{}
	for _, issue := range issues {
		if issue.Code == "audit_disagreement" {
			continue
		}
		for _, part := range issue.Components {
			if part != "detection" && part != "key" && !(part == "classification" && classificationRelevant(issue)) {
				continue
			}
			if part == "key" {
				part = "detection"
			}
			for _, domain := range scoring.Domains {
				relevant := len(issue.Units) == 0
				for _, id := range issue.Units {
					if u := units[id]; u != nil && u["domain"] == domain {
						relevant = true
					}
				}
				if relevant {
					if in.DomainUnresolved[domain] == nil {
						in.DomainUnresolved[domain] = map[string]bool{}
					}
					in.DomainUnresolved[domain][part] = true
				}
			}
		}
	}
	byClaim := map[string]SemanticDecision{}
	for _, d := range mapping.Decisions {
		byClaim[d.Claim] = d
		if d.Duplicate != nil {
			in.DuplicateClaims++
		}
	}
	for _, g := range mapping.Groups {
		d := byClaim[g.Representative]
		u := units[optionalID(g.Unit)]
		in.Decisions = append(in.Decisions, scoring.Decision{ID: g.Representative, Unit: optionalID(g.Unit), Verdict: d.Decision, Category: optionalID(g.Category), Members: g.Members, CorrectionSupplied: g.Correction.Supplied, ExplanationSupplied: g.Explanation.Supplied, Correction: componentCredit(g.Correction, u, false), Explanation: componentCredit(g.Explanation, u, true)})
	}
	result, err := scoring.Score(in)
	if err != nil {
		return result, err
	}
	for i := range result.Items {
		item := &result.Items[i]
		u := units[item.Unit]
		if u == nil {
			continue
		}
		targets, repairs := []string{}, []string{}
		for _, v := range u["text_spans"].([]any) {
			targets = append(targets, v.(map[string]any)["span"].(map[string]any)["exact_text"].(string))
		}
		for _, v := range u["corrections"].([]any) {
			o := v.(map[string]any)
			if text, ok := o["text"].(string); ok {
				repairs = append(repairs, text)
			}
			for _, alternative := range o["approved_text_alternatives"].([]any) {
				repairs = append(repairs, alternative.(string))
			}
			if ipa, ok := o["ipa"].(string); ok {
				repairs = append(repairs, "IPA: "+ipa)
			}
		}
		item.Reference = map[string]any{"target_texts": targets, "repairs": repairs, "rationale": u["rationale"], "audio_intervals": u["audio_intervals"]}
		if recurrence := recurringSummary(u); recurrence != nil {
			item.Reference["recurrence"] = recurrence
		}
	}
	return result, nil
}
