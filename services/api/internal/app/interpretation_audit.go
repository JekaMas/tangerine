package app

import (
	"sort"
	"tangerine.local/api/internal/lab"
)

// Audit compares admitted semantic content without mutating saved findings or
// allowing free prose differences to become a grading gate.
func compareMapping(a, b SemanticMapping) bool {
	normalize := func(m SemanticMapping) any {
		rows := []SemanticDecision{}
		for _, d := range m.Decisions {
			d.Note = ""
			d.Correction.Additional = comparisonAssertions(d.Correction.Additional, false)
			d.Explanation.Additional = comparisonAssertions(d.Explanation.Additional, false)
			rows = append(rows, d)
		}
		return rows
	}
	return lab.Hash(normalize(a)) == lab.Hash(normalize(b))
}

func duplicateComponentSignature(j SemanticComponent) string {
	j.Additional = comparisonAssertions(j.Additional, true)
	return lab.Hash(j)
}

// Assertion order and explanatory prose carry no credit. Exact source/judgment
// differences remain observable; only duplicate comparison removes coordinates.
func comparisonAssertions(input []ComponentAssertion, duplicate bool) []ComponentAssertion {
	out := append([]ComponentAssertion{}, input...)
	for i := range out {
		out[i].Reason = ""
		if duplicate {
			out[i].Start = 0
			out[i].End = 0
			out[i].Text = duplicateWording(out[i].Text)
		}
	}
	sort.Slice(out, func(i, j int) bool {
		a, b := out[i], out[j]
		if a.Start != b.Start {
			return a.Start < b.Start
		}
		if a.End != b.End {
			return a.End < b.End
		}
		if a.Text != b.Text {
			return a.Text < b.Text
		}
		return a.Judgment < b.Judgment
	})
	// Equal copied source/judgment tuples are one semantic finding. Their raw
	// reasons and multiplicity remain retained in the original model decisions.
	unique := out[:0]
	for _, assertion := range out {
		if len(unique) == 0 || unique[len(unique)-1] != assertion {
			unique = append(unique, assertion)
		}
	}
	return unique
}
