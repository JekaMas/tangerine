package app

import "tangerine.local/api/internal/lab"

// Audit compares admitted semantic content without mutating saved findings or
// allowing free prose differences to become a grading gate.
func compareMapping(a, b SemanticMapping) bool {
	normalize := func(m SemanticMapping) any {
		rows := []SemanticDecision{}
		for _, d := range m.Decisions {
			d.Note = ""
			d.Correction.Additional = append([]ComponentAssertion(nil), d.Correction.Additional...)
			d.Explanation.Additional = append([]ComponentAssertion(nil), d.Explanation.Additional...)
			for i := range d.Correction.Additional {
				d.Correction.Additional[i].Reason = ""
			}
			for i := range d.Explanation.Additional {
				d.Explanation.Additional[i].Reason = ""
			}
			rows = append(rows, d)
		}
		return rows
	}
	return lab.Hash(normalize(a)) == lab.Hash(normalize(b))
}

func duplicateComponentSignature(j SemanticComponent) string {
	j.Additional = append([]ComponentAssertion{}, j.Additional...)
	for i := range j.Additional {
		j.Additional[i].Start = 0
		j.Additional[i].End = 0
		j.Additional[i].Reason = ""
		j.Additional[i].Text = duplicateWording(j.Additional[i].Text)
	}
	return lab.Hash(j)
}
