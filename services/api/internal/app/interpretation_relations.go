package app

// Source relations retain original members and determine which attached
// component spans remain endorsed. They never assign targets or semantic credit.
import "sort"

func normalizeClaimRelations(answer string, result *CanonicalExtraction, byRef map[string]int) error {
	// A correction/reason already belongs to its containing claim. Some models
	// additionally describe that fact as a self attachment. When the exact source
	// component and enclosing evidence establish this redundancy, drop only the
	// redundant edge; retain the claim/component once. Self retractions and edges
	// without that source evidence still follow the ordinary relation rules.
	relations := result.Extraction.Relations[:0]
	for _, rel := range result.Extraction.Relations {
		if index, ok := byRef[rel.From]; ok && rel.From == rel.To {
			claim := result.Claims[index]
			var component *AnswerSpan
			if rel.Kind == "correction_attachment" {
				component = claim.Correction
			} else if rel.Kind == "explanation_attachment" {
				component = claim.Rationale
			}
			if component != nil && claim.Span.Start <= rel.Evidence.Start && rel.Evidence.Start <= component.Start && component.End <= rel.Evidence.End && rel.Evidence.End <= claim.Span.End {
				continue
			}
		}
		relations = append(relations, rel)
	}
	result.Extraction.Relations = relations
	sort.SliceStable(result.Extraction.Relations, func(i, j int) bool {
		return byRef[result.Extraction.Relations[i].From] < byRef[result.Extraction.Relations[j].From]
	})
	for _, rel := range result.Extraction.Relations {
		a, okA := byRef[rel.From]
		b, okB := byRef[rel.To]
		if !okA || !okB || a <= b || result.Claims[a].Span.Start <= result.Claims[b].Span.Start {
			return interpretationInvalid("Relations require an actual later source claim and an earlier distinct claim.")
		}
		if rel.Evidence.Start < 0 || rel.Evidence.Start >= rel.Evidence.End || rel.Evidence.End > len([]rune(answer)) {
			return interpretationInvalid("Relation evidence must be an actual original source interval.")
		}
		later, earlier := &result.Claims[a], &result.Claims[b]
		if rel.Kind == "retracts" {
			if rel.Evidence.Start < earlier.Span.End {
				return interpretationInvalid("A retraction must follow its earlier assertion.")
			}
			earlier.Active = false
		} else if rel.Kind == "exact_duplicate" {
			if duplicateWording(later.Span.Text) != duplicateWording(earlier.Span.Text) {
				return interpretationInvalid("Exact duplicate normalization cannot erase case or punctuation or change substantive wording.")
			}
		} else {
			// Attachments keep all original members and source spans, with one earliest
			// assertion representative. Target/stance semantics remain the mapper's job.
			group := earlier.Group
			var root *CanonicalClaim
			for j := range result.Claims {
				if result.Claims[j].ID == group {
					root = &result.Claims[j]
					break
				}
			}
			if root == nil {
				return interpretationInvalid("Attachment has no source representative.")
			}
			later.Group = group
		}
	}
	for i := range result.Claims {
		c := &result.Claims[i]
		if c.Retraction != nil {
			found := false
			for j := 0; j < i; j++ {
				if result.Claims[j].Span == *c.Retraction {
					result.Claims[j].Active = false
					found = true
					break
				}
			}
			if !found {
				return interpretationInvalid("The explicit retraction must name an earlier actual claim.")
			}
		}
	}

	// Project only currently endorsed attachments after all retractions are known.
	// Original component spans stay on each source member for readback.
	for _, rel := range result.Extraction.Relations {
		if rel.Kind == "retracts" || rel.Kind == "exact_duplicate" {
			continue
		}
		later := &result.Claims[byRef[rel.From]]
		if !later.Active {
			continue
		}
		var root *CanonicalClaim
		for i := range result.Claims {
			if result.Claims[i].ID == later.Group {
				root = &result.Claims[i]
				break
			}
		}
		if root == nil || !root.Active {
			continue
		}
		if (rel.Kind == "correction_attachment" || rel.Kind == "compatible_fragment") && later.Correction != nil {
			root.Corrections = append(root.Corrections, *later.Correction)
		}
		if (rel.Kind == "explanation_attachment" || rel.Kind == "compatible_fragment") && later.Rationale != nil {
			root.Explanations = append(root.Explanations, *later.Rationale)
		}
		if later.Category != nil {
			root.Categories = append(root.Categories, *later.Category)
		}
	}
	return nil
}
