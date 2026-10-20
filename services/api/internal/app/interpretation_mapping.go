package app

// Mapper admission owns semantic references and component scope, never numeric grades.
import (
	"encoding/json"
	"sort"
)

type ComponentAssertion struct {
	AnswerSpan
	Judgment string `json:"judgment"`
	Reason   string `json:"reason"`
}
type SemanticComponent struct {
	Supplied   bool                 `json:"supplied"`
	Option     *string              `json:"option_id"`
	Satisfied  []string             `json:"satisfied_proposition_ids"`
	Violated   []string             `json:"violated_proposition_ids"`
	Status     string               `json:"status"`
	Evidence   []string             `json:"support_evidence_ids"`
	Unresolved *string              `json:"unresolved_reason"`
	Additional []ComponentAssertion `json:"additional_assertions"`
}
type SemanticDecision struct {
	Claim       string            `json:"claim_id"`
	Unit        *string           `json:"unit_id"`
	Decision    string            `json:"decision"`
	Duplicate   *string           `json:"duplicate_of_claim_id"`
	Category    *string           `json:"category_id"`
	Correction  SemanticComponent `json:"correction"`
	Explanation SemanticComponent `json:"explanation"`
	Evidence    []string          `json:"evidence_ids"`
	Reason      string            `json:"reason_code"`
	Note        string            `json:"note"`
}
type SemanticMapping struct {
	Groups    []SemanticGroup    `json:"groups,omitempty"`
	Version   string             `json:"schema_version"`
	Decisions []SemanticDecision `json:"decisions"`
}
type InterpretationIssue struct {
	Code        string   `json:"code"`
	Claims      []string `json:"claim_ids"`
	Units       []string `json:"unit_ids"`
	Components  []string `json:"affected_components"`
	Blocks      bool     `json:"blocks_final_score"`
	Explanation string   `json:"explanation"`
}

func stringSet(values []any) map[string]bool {
	out := map[string]bool{}
	for _, v := range values {
		if s, ok := v.(string); ok {
			out[s] = true
		}
	}
	return out
}
func propositionSet(values any) map[string]bool {
	out := map[string]bool{}
	if rows, ok := values.([]any); ok {
		for _, v := range rows {
			out[v.(map[string]any)["id"].(string)] = true
		}
	}
	return out
}
func subsetDistinct(values []string, allowed map[string]bool) bool {
	seen := map[string]bool{}
	for _, s := range values {
		if !allowed[s] || seen[s] {
			return false
		}
		seen[s] = true
	}
	return true
}
func optionalID(p *string) string {
	if p == nil {
		return ""
	}
	return *p
}
func normalizeComponent(answer string, j *SemanticComponent, source AnswerSpan, spans, otherSpans []AnswerSpan, unit map[string]any, explanation bool, allowedEvidence map[string]bool) error {
	if j.Supplied != (len(spans) > 0) {
		return interpretationInvalid("Supplied flags must match actual original correction/explanation spans, including declared attachments.")
	}
	if !subsetDistinct(j.Evidence, allowedEvidence) {
		return interpretationInvalid("Use existing subject-scoped evidence IDs only.")
	}
	if !j.Supplied {
		if j.Option != nil || len(j.Satisfied)+len(j.Violated)+len(j.Additional) > 0 || j.Unresolved != nil {
			return interpretationInvalid("No credit-bearing findings may be invented for a missing component.")
		}
		j.Status = "not_supplied"
		return nil
	}
	required, forbidden := map[string]bool{}, map[string]bool{}
	if unit != nil {
		if explanation {
			if j.Option != nil {
				return interpretationInvalid("Explanation propositions belong to the unit rationale; option_id must be null.")
			}
			required = propositionSet(unit["rationale_required_propositions"])
			forbidden = propositionSet(unit["rationale_forbidden_propositions"])
		} else if j.Option != nil {
			found := false
			for _, v := range unit["corrections"].([]any) {
				o := v.(map[string]any)
				if o["id"] == *j.Option {
					required = propositionSet(o["required_propositions"])
					forbidden = propositionSet(o["forbidden_propositions"])
					found = true
					break
				}
			}
			if !found {
				return interpretationInvalid("The correction option must belong to this exact unit.")
			}
		}
	}
	if !subsetDistinct(j.Satisfied, required) || !subsetDistinct(j.Violated, forbidden) {
		return interpretationInvalid("Required and forbidden proposition IDs must belong to the selected unit and exact correction/rationale rubric.")
	}
	explicitRejection := !explanation && unit != nil && j.Option == nil && j.Status == "rejected" && j.Unresolved == nil
	unknown, bad := false, len(j.Violated) > 0 || explicitRejection
	for i := range j.Additional {
		a := &j.Additional[i]
		if err := normalizeAnswerSpan(answer, &a.AnswerSpan); err != nil {
			return err
		}
		contained := false
		for _, s := range spans {
			if containsAnswerSpan(s, a.AnswerSpan) {
				contained = true
				break
			}
		}
		if !contained {
			// Models sometimes quote the containing claim as context. Preserve
			// its raw output, but anchor this judgment to the one whole component
			// it contains. A quote crossing the other component cannot be narrowed.
			if !containsAnswerSpan(source, a.AnswerSpan) {
				return interpretationInvalid("A contextual assertion quote must stay inside its original source claim.")
			}
			var candidate *AnswerSpan
			for _, s := range spans {
				if containsAnswerSpan(a.AnswerSpan, s) {
					if candidate != nil {
						return interpretationInvalid("An assertion quote covering multiple source components needs an exact component location.")
					}
					copy := s
					candidate = &copy
				}
			}
			for _, other := range otherSpans {
				if a.Start < other.End && other.Start < a.End {
					candidate = nil
					break
				}
			}
			if candidate == nil {
				return interpretationInvalid("An additional assertion must quote its actual component, without borrowing the other component's words.")
			}
			a.AnswerSpan = *candidate
		}
		unknown = unknown || a.Judgment == "unknown"
		bad = bad || a.Judgment == "unsupported"
	}
	if explanation && len(j.Additional) == 0 && j.Unresolved == nil {
		return interpretationInvalid("Assess the listener's entire supplied explanation, independently of its rubric overlap. Include a source-quoted supported/unsupported/unknown judgment and a contextual reason in explanation.additional_assertions. Proposition IDs alone do not assess the full assertion or its scope. Do not substitute the narrower gold rationale for the listener's words.")
	}
	if bad {
		j.Status = "rejected"
	} else if unknown || j.Unresolved != nil {
		j.Status = "unresolved"
		if j.Unresolved == nil {
			reason := "unclear_meaning"
			j.Unresolved = &reason
		}
	} else if unit != nil && len(required) > 0 {
		if len(j.Satisfied) == len(required) {
			j.Status = "accepted"
		} else if len(j.Satisfied) > 0 {
			j.Status = "partial"
		} else {
			j.Status = "rejected"
		}
	} else if unit != nil {
		j.Status = "unresolved"
		reason := "novel_alternative"
		if explanation {
			reason = "unsupported_rationale"
		}
		j.Unresolved = &reason
	}
	if j.Status != "unresolved" {
		j.Unresolved = nil
	}
	sort.Strings(j.Satisfied)
	sort.Strings(j.Violated)
	sort.Strings(j.Evidence)
	return nil
}
func normalizeMapping(answer string, claims CanonicalExtraction, key map[string]any, taxonomy map[string]bool, evidence []any, components map[string]any, raw []byte) (SemanticMapping, []InterpretationIssue, error) {
	var out SemanticMapping
	issues := []InterpretationIssue{}
	if err := json.Unmarshal(raw, &out); err != nil {
		return out, issues, interpretationInvalid("Mapping must be JSON.")
	}
	byClaim := map[string]CanonicalClaim{}
	order := map[string]int{}
	units := map[string]map[string]any{}
	ev := map[string]bool{}
	evidenceByID := map[string]map[string]any{}
	for i, c := range claims.Claims {
		byClaim[c.ID] = c
		order[c.ID] = i
	}
	for _, v := range key["units"].([]any) {
		u := v.(map[string]any)
		units[u["id"].(string)] = u
	}
	for _, v := range evidence {
		row := v.(map[string]any)
		id := row["id"].(string)
		ev[id] = true
		evidenceByID[id] = row
	}
	seen := map[string]bool{}
	for _, d := range out.Decisions {
		if _, ok := byClaim[d.Claim]; !ok || seen[d.Claim] {
			return out, issues, interpretationInvalid("Return exactly one decision for each canonical server claim ID.")
		}
		seen[d.Claim] = true
	}
	if len(seen) != len(byClaim) {
		return out, issues, interpretationInvalid("A substantive or uncertain claim cannot be omitted from mapping.")
	}
	sort.SliceStable(out.Decisions, func(i, j int) bool { return order[out.Decisions[i].Claim] < order[out.Decisions[j].Claim] })
	decisions := map[string]*SemanticDecision{}
	addIssue := func(code string, d SemanticDecision, parts []string, blocks bool, explanation string) {
		ids := []string{}
		if d.Unit != nil {
			ids = append(ids, *d.Unit)
		}
		issues = append(issues, InterpretationIssue{code, []string{d.Claim}, ids, parts, blocks, explanation})
	}
	for i := range out.Decisions {
		d := &out.Decisions[i]
		c := byClaim[d.Claim]
		unit := units[optionalID(d.Unit)]
		if d.Unit != nil && unit == nil {
			return out, issues, interpretationInvalid("A mapped target must exist in this frozen case.")
		}
		// Classification can only credit what the listener supplied. An
		// unsolicited model label is discarded, not a failed whole answer.
		if len(c.Categories) == 0 {
			d.Category = nil
		}
		if d.Category != nil && !taxonomy[*d.Category] {
			return out, issues, interpretationInvalid("A category must be an existing taxonomy ID justified by actual category wording.")
		}
		if !subsetDistinct(d.Evidence, ev) {
			return out, issues, interpretationInvalid("Mapping evidence IDs must be supplied in the same frozen case.")
		}
		conflict := false
		for _, id := range claims.Conflicts {
			conflict = conflict || id == c.ID
		}
		if conflict && d.Decision != "unresolved" {
			return out, issues, interpretationInvalid("Competing interpretations of this identical source span remain unresolved; do not select a favorable interpretation.")
		}
		nonassertive := !conflict && (!c.Active || c.Stance == "meta" || c.Stance == "question" || c.Stance == "retracted" || c.Group != c.ID)
		if nonassertive && d.Decision != "ignore" {
			return out, issues, interpretationInvalid("Questions, comments, retractions and attached fragments cannot become independent scored assertions.")
		}
		if !nonassertive && d.Decision == "ignore" {
			return out, issues, interpretationInvalid("Retain an unresolved substantive assertion rather than silently ignoring it.")
		}
		if d.Decision != "ignore" && d.Decision != "unresolved" {
			want := "false_positive"
			if unit != nil {
				truth := unit["expected_judgment"]
				switch {
				case truth == "true_error" && c.Stance == "assert_error":
					want = "matched_error"
				case truth == "true_error" && c.Stance == "assert_acceptable":
					want = "wrong_acceptance"
				case truth == "acceptable" && c.Stance == "assert_acceptable":
					want = "confirmed_acceptable"
				case truth == "acceptable" && c.Stance == "assert_error":
					want = "false_positive"
				default:
					return out, issues, interpretationInvalid("Uncertain target truth must remain unresolved.")
				}
			} else if c.Stance != "assert_error" {
				return out, issues, interpretationInvalid("An off-key acceptance requires an identified target or explicit uncertainty.")
			}
			if d.Decision != want {
				return out, issues, interpretationInvalid("Decision must agree with the actual assertion stance and the frozen target judgment.")
			}
		}
		scopedEvidence := map[string]bool{}
		for eid, row := range evidenceByID {
			if row["case_version_id"] != key["case_version_id"] {
				continue
			}
			subjects, _ := row["subject_ids"].([]any)
			scope := stringSet(subjects)
			valid := scope[key["case_version_id"].(string)]
			if d.Unit != nil {
				valid = valid || scope[*d.Unit]
			}
			switch row["type"] {
			case "observed_phone", "prosody", "mutation", "alignment":
				valid = d.Unit != nil && scope[*d.Unit]
			}
			if valid {
				scopedEvidence[eid] = true
			}
		}
		if !subsetDistinct(d.Evidence, scopedEvidence) {
			return out, issues, interpretationInvalid("Cited evidence must belong to this exact case and target unit.")
		}
		if err := normalizeComponent(answer, &d.Correction, c.Span, c.Corrections, c.Explanations, unit, false, scopedEvidence); err != nil {
			return out, issues, err
		}
		if err := normalizeComponent(answer, &d.Explanation, c.Span, c.Explanations, c.Corrections, unit, true, scopedEvidence); err != nil {
			return out, issues, err
		}
		if d.Duplicate != nil {
			previous, ok := decisions[*d.Duplicate]
			if !ok || previous.Duplicate != nil || previous.Unit == nil || d.Unit == nil || *previous.Unit != *d.Unit || byClaim[previous.Claim].Stance != c.Stance || !byClaim[previous.Claim].Active {
				return out, issues, interpretationInvalid("A duplicate requires an earlier active compatible representative for the same exact event.")
			}
			// Additional component findings cannot disappear behind duplicate suppression.
			if optionalID(previous.Category) != optionalID(d.Category) || duplicateComponentSignature(previous.Correction) != duplicateComponentSignature(d.Correction) || duplicateComponentSignature(previous.Explanation) != duplicateComponentSignature(d.Explanation) {
				return out, issues, interpretationInvalid("Combine compatible source fragments explicitly; do not discard different correction/explanation findings as duplicates.")
			}
		}
		if d.Decision == "unresolved" {
			code := d.Reason
			if code != "potential_key_defect" && code != "contradiction" {
				code = "ambiguous_location"
			}
			addIssue(code, *d, []string{"detection"}, true, d.Note)
		}
		for _, part := range []struct {
			name  string
			value SemanticComponent
		}{{"correction", d.Correction}, {"explanation", d.Explanation}} {
			if part.value.Status == "unresolved" {
				blocks := part.name == "correction" && components["correction"] == true && d.Decision == "matched_error"
				code := "unsupported_rationale"
				if part.name == "correction" {
					code = "novel_alternative"
				}
				addIssue(code, *d, []string{part.name}, blocks, "The supplied "+part.name+" retains unresolved meaning; other supported components remain available.")
			}
		}
		if len(c.Categories) > 0 && d.Category == nil {
			addIssue("unknown_alias", *d, []string{"classification"}, false, "The supplied category is not mapped; supported detection is preserved.")
		}
		decisions[d.Claim] = d
	}
	if len(claims.Extraction.Unparsed) > 0 {
		issues = append(issues, InterpretationIssue{"unparsed_substantive_text", []string{}, []string{}, []string{"detection"}, true, "Substantive original answer spans remain explicitly unresolved."})
	}
	groups, groupIssues := consolidateMapping(claims, out, key, components)
	out.Groups = groups
	issues = append(issues, groupIssues...)
	return out, issues, nil
}
