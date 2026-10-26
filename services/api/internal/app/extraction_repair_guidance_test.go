package app

import (
	"encoding/json"
	"errors"
	"strings"
	"testing"

	"tangerine.local/api/internal/provider"
)

func TestExtractionRepairCoordinatesPositive(t *testing.T) {
	// Constructed regression for the repeated books failure in the actual I29
	// answer. The model, not a nearest-offset guess, must choose its occurrence.
	text := "Use books, not book. The word books is plural."
	s := AnswerSpan{5, 10, "books"}
	err := normalizeAnswerSpan(text, &s)
	var detail *provider.OutputValidationError
	if !errors.As(err, &detail) || !strings.Contains(detail.Detail, "[4,9)") || !strings.Contains(detail.Detail, "[30,35)") || !strings.Contains(detail.Detail, "[5,10)") {
		t.Fatalf("repair cannot see the actual quote coordinates: %v", err)
	}
	_, err = normalizeExtraction(text, "source", extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, len([]rune(text)), text}, Stance: "assert_error", Correction: &s}}, nil))
	if !errors.As(err, &detail) || !strings.Contains(detail.Detail, "correction_span") || !strings.Contains(detail.Detail, "[30,35)") {
		t.Fatal("the stage boundary lost its actionable repair detail", err)
	}
	// A corrected selection is accepted once, retaining the exact source.
	s = AnswerSpan{4, 9, "books"}
	if err := normalizeAnswerSpan(text, &s); err != nil || s != (AnswerSpan{4, 9, "books"}) {
		t.Fatal(s, err)
	}
}

func TestExtractionRepairCoordinatesNegative(t *testing.T) {
	text := "go go"
	s := AnswerSpan{1, 3, "go"}
	before := s
	if err := normalizeAnswerSpan(text, &s); err == nil || s != before {
		t.Fatal("repair guidance guessed or changed an ambiguous source", s, err)
	}
}

func TestExtractionRelationCoordinateAliasesPositive(t *testing.T) {
	var raw any
	_ = json.Unmarshal([]byte(`{"relations":[{"evidence_span":{"start_cp":4,"end_cp":9,"exact_text":"books"}}]}`), &raw)
	root := normalizeInterpretationShape(raw, nil).(map[string]any)
	span := root["relations"].([]any)[0].(map[string]any)["evidence_span"].(map[string]any)
	if span["start"] != float64(4) || span["end"] != float64(9) {
		t.Fatal("source-equivalent relation coordinates require a model call", span)
	}
}

func TestExtractionRelationCoordinateAliasesNegative(t *testing.T) {
	var raw any
	_ = json.Unmarshal([]byte(`{"relations":[{"evidence_span":{"start":2,"end":3,"start_cp":4,"end_cp":9}}]}`), &raw)
	root := normalizeInterpretationShape(raw, nil).(map[string]any)
	span := root["relations"].([]any)[0].(map[string]any)["evidence_span"].(map[string]any)
	if span["start"] != float64(2) || span["end"] != float64(3) {
		t.Fatal("normalization overwrote an explicit coordinate", span)
	}
}

func TestExtractionRedundantAttachmentPositive(t *testing.T) {
	text := "Use books because many needs a plural noun."
	correction, reason := AnswerSpan{4, 9, "books"}, AnswerSpan{18, 42, "many needs a plural noun"}
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 43, text}, Stance: "assert_error", Correction: &correction, Rationale: &reason}}
	rels := []ClaimRelation{}
	for _, kind := range []string{"correction_attachment", "explanation_attachment"} {
		rel := ClaimRelation{From: "c0", To: "c0", Kind: kind}
		rel.Evidence.Start, rel.Evidence.End = 0, 43
		rels = append(rels, rel)
	}
	x, err := normalizeExtraction(text, "source", extractionPacket(clauses, rels))
	if err != nil || len(x.Claims) != 1 || len(x.Extraction.Relations) != 0 || len(x.Claims[0].Corrections) != 1 || len(x.Claims[0].Explanations) != 1 {
		t.Fatal("a source-supported redundant edge blocks or duplicates its component", x, err)
	}
}

func TestExtractionSelfRelationNegative(t *testing.T) {
	text := "Use books."
	correction := AnswerSpan{4, 9, "books"}
	clauses := []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 10, text}, Stance: "assert_error", Correction: &correction}}
	for _, tc := range []struct {
		kind       string
		start, end int
	}{{"retracts", 0, 10}, {"exact_duplicate", 0, 10}, {"explanation_attachment", 0, 10}, {"correction_attachment", 8, 10}, {"correction_attachment", -1, 10}} {
		rel := ClaimRelation{From: "c0", To: "c0", Kind: tc.kind}
		rel.Evidence.Start, rel.Evidence.End = tc.start, tc.end
		if _, err := normalizeExtraction(text, "source", extractionPacket(clauses, []ClaimRelation{rel})); err == nil {
			t.Fatal("an unsupported or meaning-changing self relation was discarded", tc)
		}
	}
}
