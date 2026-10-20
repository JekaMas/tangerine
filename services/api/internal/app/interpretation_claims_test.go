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
