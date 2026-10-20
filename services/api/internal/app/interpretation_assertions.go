package app

// Source ownership determines which component a quoted judgment assesses. It
// does not change the model's judgment, invent a reason, or assign numeric credit.
func normalizeAssertionOwnership(answer string, claim CanonicalClaim, decision *SemanticDecision) error {
	spans := [][]AnswerSpan{claim.Corrections, claim.Explanations}
	input := [][]ComponentAssertion{decision.Correction.Additional, decision.Explanation.Additional}
	output := [][]ComponentAssertion{{}, {}}
	for original, assertions := range input {
		for _, assertion := range assertions {
			if err := normalizeAnswerSpan(answer, &assertion.AnswerSpan); err != nil {
				return err
			}
			contained := []bool{false, false}
			for part := range spans {
				for _, span := range spans[part] {
					contained[part] = contained[part] || containsAnswerSpan(span, assertion.AnswerSpan)
				}
			}
			target := original
			if !contained[original] && contained[1-original] {
				target = 1 - original
			} else if !contained[0] && !contained[1] {
				if !containsAnswerSpan(claim.Span, assertion.AnswerSpan) {
					return interpretationInvalid("A contextual assertion must stay in its actual source claim.")
				}
				var candidate *AnswerSpan
				for part := range spans {
					for _, span := range spans[part] {
						if assertion.Start < span.End && span.Start < assertion.End {
							if candidate != nil || !containsAnswerSpan(assertion.AnswerSpan, span) {
								return interpretationInvalid("An assertion crossing distinct source components needs its actual component quote.")
							}
							copy := span
							candidate, target = &copy, part
						}
					}
				}
				if candidate == nil {
					return interpretationInvalid("An assertion must quote actual supplied correction or explanation wording.")
				}
				assertion.AnswerSpan = *candidate
			}
			duplicate := false
			for _, existing := range output[target] {
				duplicate = duplicate || existing == assertion
			}
			if !duplicate {
				output[target] = append(output[target], assertion)
			}
		}
	}
	decision.Correction.Additional, decision.Explanation.Additional = output[0], output[1]
	return nil
}
