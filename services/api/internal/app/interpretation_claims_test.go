package app

import (
	"encoding/json"
	"tangerine.local/api/internal/contracts"
	"testing"
)

func extractionPacket(clauses []ExtractedClause, relations []ClaimRelation) []byte {
	if clauses == nil {
		clauses = []ExtractedClause{}
	}
	if relations == nil {
		relations = []ClaimRelation{}
	}
	raw, _ := json.Marshal(AnswerExtraction{Version: "2.0.0", Clauses: clauses, Relations: relations, Unparsed: []AnswerSpan{}})
	return raw
}
func TestInterpretationIdentityPositive(t *testing.T) {
	text := "He go."
	raw := extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 6, text}, Stance: "assert_error"}}, nil)
	x, e := normalizeExtraction(text, contracts.Digest([]byte(text)), raw)
	if e != nil || len(x.Claims) != 1 || x.Claims[0].ID != "clm_0cf2bbae750d82b7c460e49a98cbf991" {
		t.Fatal(x, e)
	}
}
func TestInterpretationCoveragePositive(t *testing.T) {
	text := "\tHe go.\n"
	x, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{1, 7, "He go."}, Stance: "assert_error"}}, nil))
	if e != nil || len(x.Extraction.Coverage) != 3 {
		t.Fatal(x, e)
	}
	for i, want := range []string{"whitespace", "claim", "whitespace"} {
		if x.Extraction.Coverage[i].Kind != want {
			t.Fatal(x)
		}
	}
}
func TestInterpretationUnicodePositive(t *testing.T) {
	text := "🟠 Ошибка: He go. Use goes."
	s := AnswerSpan{22, 26, "goes"}
	x, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, len([]rune(text)), text}, Stance: "assert_error", Correction: &s}}, nil))
	if e != nil || x.Claims[0].Correction.Start != 21 || x.Claims[0].Correction.End != 25 || x.Claims[0].Correction.Text != "goes" {
		t.Fatal(x, e)
	}
}
func TestInterpretationRetractionPositive(t *testing.T) {
	text := "He go. Withdraw that."
	rel := ClaimRelation{From: "c1", To: "c0", Kind: "retracts"}
	rel.Evidence.Start = 7
	rel.Evidence.End = 21
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 6, "He go."}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{7, 21, "Withdraw that."}, Stance: "retracted"}}
	x, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket(clauses, []ClaimRelation{rel}))
	if e != nil || x.Claims[0].Active || x.Claims[1].Active {
		t.Fatal(x, e)
	}
}
func TestInterpretationFabricatedSpanNegative(t *testing.T) {
	text := "He go."
	_, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 6, "He goes."}, Stance: "assert_error"}}, nil))
	if e == nil {
		t.Fatal("invented answer accepted")
	}
}
func TestInterpretationAmbiguousQuoteNegative(t *testing.T) {
	text := "go go"
	_, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{20, 22, "go"}, Stance: "assert_error"}}, nil))
	if e == nil {
		t.Fatal("guessed repeated location")
	}
}
func TestInterpretationUncoveredNegative(t *testing.T) {
	text := "A substantive assertion"
	_, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket(nil, nil))
	if e == nil {
		t.Fatal("silently omitted source assertion")
	}
}
func TestInterpretationForwardRetractionNegative(t *testing.T) {
	text := "He go. Withdraw that."
	rel := ClaimRelation{From: "c0", To: "c1", Kind: "retracts"}
	rel.Evidence.Start = 0
	rel.Evidence.End = 6
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 6, "He go."}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{7, 21, "Withdraw that."}, Stance: "retracted"}}
	if _, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket(clauses, []ClaimRelation{rel})); e == nil {
		t.Fatal("forward retraction accepted")
	}
}

func TestInterpretationConflictRetainedPositive(t *testing.T) {
	text := "He go."
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 6, text}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{0, 6, text}, Stance: "assert_acceptable"}}
	x, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket(clauses, nil))
	if e != nil || len(x.Extraction.Clauses) != 2 || len(x.Claims) != 1 || len(x.Conflicts) != 1 || len(x.Extraction.Coverage) != 1 {
		t.Fatal(x, e)
	}
}
func TestInterpretationContainedAttachmentPositive(t *testing.T) {
	text := "He go. Use goes."
	correction := AnswerSpan{11, 15, "goes"}
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 16, text}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{7, 16, "Use goes."}, Stance: "assert_error", Correction: &correction}}
	rel := ClaimRelation{From: "c1", To: "c0", Kind: "correction_attachment"}
	rel.Evidence.Start = 7
	rel.Evidence.End = 16
	x, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket(clauses, []ClaimRelation{rel}))
	if e != nil || len(x.Claims) != 2 || x.Claims[1].Group != x.Claims[0].ID || len(x.Claims[0].Corrections) != 1 {
		t.Fatal(x, e)
	}
}
func TestInterpretationUndeclaredOverlapNegative(t *testing.T) {
	text := "He go. Use goes."
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 16, text}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{7, 16, "Use goes."}, Stance: "assert_error"}}
	if _, e := normalizeExtraction(text, contracts.Digest([]byte(text)), extractionPacket(clauses, nil)); e == nil {
		t.Fatal("undeclared overlap accepted")
	}
}
func TestInterpretationConflictSelectionNegative(t *testing.T) {
	answer, c, key, tax, m := interpretationMappingFixture()
	c.Conflicts = []string{c.Claims[0].ID}
	raw, _ := json.Marshal(m)
	mapping, issues, e := normalizeMapping(answer, c, key, tax, nil, map[string]any{}, raw)
	if e != nil || mapping.Decisions[0].Decision != "unresolved" || len(issues) == 0 || !issues[0].Blocks {
		t.Fatal("conflicted meaning scored as certain", mapping, issues, e)
	}
}

func TestInterpretationWholeWordPositive(t *testing.T) {
	answer := "The verb open should be opens."
	target := AnswerSpan{13, 18, "open"}
	x, err := normalizeExtraction(answer, "answer-sha", extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 30, answer}, Stance: "assert_error", Target: &target}}, nil))
	if err != nil || len(x.Claims) != 1 || *x.Claims[0].Target != (AnswerSpan{9, 13, "open"}) {
		t.Fatal(x, err)
	}
}
func TestInterpretationRepeatedWordNegative(t *testing.T) {
	for _, answer := range []string{"open opens open", "go go", "打开 打开"} {
		span := AnswerSpan{90, 95, "open"}
		if answer == "go go" {
			span.Text = "go"
		} else if answer == "打开 打开" {
			span.Text = "打开"
		}
		if err := normalizeAnswerSpan(answer, &span); err == nil {
			t.Fatal("guessed repeated complete word", answer, span)
		}
	}
}

func attachmentRetractionFixture(t *testing.T, retract bool, reason bool) CanonicalExtraction {
	t.Helper()
	text := "Wrong verb. Use goes. Withdraw that."
	component := AnswerSpan{16, 20, "goes"}
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 11, "Wrong verb."}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{12, 21, "Use goes."}, Stance: "assert_error"}, {LocalRef: "c2", Span: AnswerSpan{22, 36, "Withdraw that."}, Stance: "meta"}}
	kind := "correction_attachment"
	if reason {
		clauses[1].Rationale = &component
		kind = "explanation_attachment"
	} else {
		clauses[1].Correction = &component
	}
	relation := ClaimRelation{From: "c1", To: "c0", Kind: kind}
	relation.Evidence.Start = 12
	relation.Evidence.End = 21
	relations := []ClaimRelation{relation}
	if retract {
		target := clauses[1].Span
		clauses[2].Retraction = &target
	}
	x, err := normalizeExtraction(text, "fixture-answer", extractionPacket(clauses, relations))
	if err != nil {
		t.Fatal(err)
	}
	return x
}
func TestInterpretationEndorsedAttachmentPositive(t *testing.T) {
	for _, reason := range []bool{false, true} {
		x := attachmentRetractionFixture(t, false, reason)
		spans := x.Claims[0].Corrections
		if reason {
			spans = x.Claims[0].Explanations
		}
		if len(spans) != 1 || spans[0].Text != "goes" || !x.Claims[1].Active {
			t.Fatal("endorsed attachment lost", x)
		}
	}
}
func TestInterpretationWithdrawnAttachmentNegative(t *testing.T) {
	for _, reason := range []bool{false, true} {
		x := attachmentRetractionFixture(t, true, reason)
		spans := x.Claims[0].Corrections
		if reason {
			spans = x.Claims[0].Explanations
		}
		if len(spans) != 0 || x.Claims[1].Active || len(x.Extraction.Clauses) != 3 {
			t.Fatal("withdrawn attachment remains in parent assessment", x)
		}
	}
}

func TestInterpretationRelationWithdrawalNegative(t *testing.T) {
	text := "Wrong verb. Use goes. Withdraw that."
	span := AnswerSpan{16, 20, "goes"}
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 11, "Wrong verb."}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{12, 21, "Use goes."}, Stance: "assert_error", Correction: &span}, {LocalRef: "c2", Span: AnswerSpan{22, 36, "Withdraw that."}, Stance: "meta"}}
	attach := ClaimRelation{From: "c1", To: "c0", Kind: "correction_attachment"}
	attach.Evidence.Start = 12
	attach.Evidence.End = 21
	retract := ClaimRelation{From: "c2", To: "c1", Kind: "retracts"}
	retract.Evidence.Start = 22
	retract.Evidence.End = 36
	x, err := normalizeExtraction(text, "fixture-answer", extractionPacket(clauses, []ClaimRelation{attach, retract}))
	if err != nil || len(x.Claims[0].Corrections) != 0 || x.Claims[1].Active {
		t.Fatal("relation withdrawal left endorsed text", x, err)
	}
}
func TestInterpretationIndependentAttachmentPositive(t *testing.T) {
	text := "Wrong verb. Use goes. Because singular. Withdraw correction."
	correction := AnswerSpan{16, 20, "goes"}
	reason := AnswerSpan{29, 37, "singular"}
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 11, "Wrong verb."}, Stance: "assert_error"}, {LocalRef: "c1", Span: AnswerSpan{12, 21, "Use goes."}, Stance: "assert_error", Correction: &correction}, {LocalRef: "c2", Span: AnswerSpan{22, 38, "Because singular."}, Stance: "assert_error", Rationale: &reason}, {LocalRef: "c3", Span: AnswerSpan{39, 59, "Withdraw correction."}, Stance: "meta", Retraction: &AnswerSpan{12, 21, "Use goes."}}}
	first := ClaimRelation{From: "c1", To: "c0", Kind: "correction_attachment"}
	first.Evidence.Start = 12
	first.Evidence.End = 21
	second := ClaimRelation{From: "c2", To: "c0", Kind: "explanation_attachment"}
	second.Evidence.Start = 22
	second.Evidence.End = 38
	x, err := normalizeExtraction(text, "fixture-answer", extractionPacket(clauses, []ClaimRelation{first, second}))
	if err != nil || len(x.Claims[0].Corrections) != 0 || len(x.Claims[0].Explanations) != 1 || x.Claims[0].Explanations[0].Text != "singular" {
		t.Fatal("withdrawal erased independent reason or kept withdrawn correction", x, err)
	}
}
