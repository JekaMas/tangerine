package app

import "testing"

func twoClaimGroupFixture() (CanonicalExtraction, SemanticMapping, map[string]any) {
	_, c, k, _, m := interpretationMappingFixture()
	second := c.Claims[0]
	second.ID = "clm_00000000000000000000000000000002"
	second.Group = second.ID
	second.LocalRef = "c1"
	second.Span = AnswerSpan{38, 46, "Use opens"}
	c.Claims = append(c.Claims, second)
	first := m.Decisions[0]
	first.Correction = semanticEmpty()
	first.Explanation = semanticEmpty()
	m.Decisions[0] = first
	secondDecision := m.Decisions[0]
	secondDecision.Claim = second.ID
	secondDecision.Correction = mappingGroupCorrection()
	m.Decisions = append(m.Decisions, secondDecision)
	return c, m, k
}
func mappingGroupCorrection() SemanticComponent {
	j := semanticEmpty()
	j.Supplied = true
	j.Status = "accepted"
	option := "option1"
	j.Option = &option
	j.Satisfied = []string{"required1"}
	return j
}
func TestInterpretationFragmentsPositive(t *testing.T) {
	c, m, k := twoClaimGroupFixture()
	groups, issues := consolidateMapping(c, m, k, map[string]any{"correction": true})
	if len(groups) != 1 || len(groups[0].Members) != 2 || groups[0].Representative != c.Claims[0].ID || groups[0].Correction.Status != "accepted" || len(issues) != 0 {
		t.Fatal(groups, issues)
	}
}
func TestInterpretationDuplicateMembersPositive(t *testing.T) {
	c, m, k := twoClaimGroupFixture()
	m.Decisions[0].Correction = mappingGroupCorrection()
	id := m.Decisions[0].Claim
	m.Decisions[1].Duplicate = &id
	groups, issues := consolidateMapping(c, m, k, map[string]any{})
	if len(groups) != 1 || len(groups[0].Members) != 2 || groups[0].Representative != id || len(issues) != 0 {
		t.Fatal(groups, issues)
	}
}
func TestInterpretationContradictoryRepairsNegative(t *testing.T) {
	c, m, k := twoClaimGroupFixture()
	m.Decisions[0].Correction = mappingGroupCorrection()
	other := "other-option"
	m.Decisions[1].Correction.Option = &other
	groups, issues := consolidateMapping(c, m, k, map[string]any{"correction": true})
	if len(issues) != 1 || !issues[0].Blocks || groups[0].Correction.Status != "unresolved" || groups[0].Representative != c.Claims[0].ID {
		t.Fatal(groups, issues)
	}
	c, m, k = twoClaimGroupFixture()
	m.Decisions[0].Correction = mappingGroupCorrection()
	m.Decisions[1].Correction.Status = "rejected"
	m.Decisions[1].Correction.Satisfied = []string{}
	groups, issues = consolidateMapping(c, m, k, map[string]any{"correction": true})
	if len(issues) != 1 || !issues[0].Blocks || groups[0].Correction.Status != "unresolved" {
		t.Fatal("same-rubric rejected alternative disappeared", groups, issues)
	}

}
func TestInterpretationOppositeStanceNegative(t *testing.T) {
	c, m, k := twoClaimGroupFixture()
	c.Claims[1].Stance = "assert_acceptable"
	m.Decisions[1].Decision = "wrong_acceptance"
	_, issues := consolidateMapping(c, m, k, map[string]any{})
	if len(issues) != 1 || issues[0].Components[0] != "detection" || !issues[0].Blocks {
		t.Fatal(issues)
	}
}

func TestInterpretationAttachedMembersPositive(t *testing.T) {
	c, m, k := twoClaimGroupFixture()
	c.Claims[1].Group = c.Claims[0].ID
	m.Decisions[0].Correction = mappingGroupCorrection()
	m.Decisions[1].Decision = "ignore"
	groups, issues := consolidateMapping(c, m, k, map[string]any{})
	if len(groups) != 1 || len(groups[0].Members) != 2 || groups[0].Members[0] != c.Claims[0].ID || groups[0].Members[1] != c.Claims[1].ID || groups[0].Correction.Status != "accepted" || len(issues) != 0 {
		t.Fatal("attached source member lost", groups, issues)
	}
}
func TestInterpretationWithdrawnMemberNegative(t *testing.T) {
	c, m, k := twoClaimGroupFixture()
	c.Claims[1].Group = c.Claims[0].ID
	c.Claims[1].Active = false
	m.Decisions[0].Correction = mappingGroupCorrection()
	m.Decisions[1].Decision = "ignore"
	groups, issues := consolidateMapping(c, m, k, map[string]any{})
	if len(groups) != 1 || len(groups[0].Members) != 2 || groups[0].Correction.Status != "accepted" || len(issues) != 0 {
		t.Fatal("withdrawal must retain source membership without merging its decision", groups, issues)
	}
}
