package app

import (
	"encoding/json"
	"strings"
	"testing"

	"tangerine.local/api/internal/contracts"
)

// Literal sibling packets exercise source attribution, not hosted model quality.
// The actual Gemini regression keeps the same saved case and developer answer.
func TestInterpretationAttributionPositive(t *testing.T) {
	for _, prefix := range []string{"Speaker 1 says ", "In the second turn, ", "Первый говорящий говорит: "} {
		t.Run(prefix, func(t *testing.T) {
			answer := prefix + "He go. Use goes."
			start := len([]rune(prefix)) + 11
			correction := AnswerSpan{start, start + 4, "goes"}
			full := AnswerSpan{0, len([]rune(answer)), answer}
			x, e := normalizeExtraction(answer, contracts.Digest([]byte(answer)), extractionPacket([]ExtractedClause{{LocalRef: "c0", Span: full, Stance: "assert_error", Correction: &correction}}, nil))
			if e != nil || len(x.Claims) != 1 || x.Claims[0].Span != full || len(x.Extraction.Unparsed) != 0 || len(x.Extraction.Coverage) != 1 || x.Extraction.Coverage[0].Kind != "claim" || x.Claims[0].Correction.Text != "goes" {
				t.Fatal("attribution/correction was lost or made a separate mistake", x, e)
			}
		})
	}
}

func TestInterpretationGenuineUnparsedNegative(t *testing.T) {
	answer := "He go. Another assertion I cannot interpret."
	packet := AnswerExtraction{Version: "2.0.0", Clauses: []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{0, 6, "He go."}, Stance: "assert_error"}}, Unparsed: []AnswerSpan{{7, len([]rune(answer)), "Another assertion I cannot interpret."}}}
	raw, _ := json.Marshal(packet)
	x, e := normalizeExtraction(answer, contracts.Digest([]byte(answer)), raw)
	if e != nil || len(x.Extraction.Unparsed) != 1 || len(x.Extraction.Coverage) != 3 || x.Extraction.Coverage[2].Kind != "unparsed" || !strings.Contains(x.Extraction.Coverage[2].Reason, "unresolved") {
		t.Fatal("substantive ambiguity was silently discarded", x, e)
	}
}
