package app

import "testing"

func TestExtractionQuoteProjectionPositive(t *testing.T) {
	for _, tc := range []struct {
		answer, quote string
		start, end    int
		want          string
	}{
		{"“Many” requires a plural noun.", "Many requires a plural noun.", 0, 30, "“Many” requires a plural noun."},
		{"Use “books”.", `Use "books".`, 0, 12, "Use “books”."},
		{"😀 Use “books”.", "Use books.", 2, 14, "Use “books”."},
		{"“book” and “book”", "book", 11, 17, "“book”"},
	} {
		s := AnswerSpan{tc.start, tc.end, tc.quote}
		if err := normalizeAnswerSpan(tc.answer, &s); err != nil || s != (AnswerSpan{tc.start, tc.end, tc.want}) {
			t.Fatalf("source wording was not projected at the explicit coordinates: %+v %v", s, err)
		}
	}
}

func TestExtractionQuoteProjectionNegative(t *testing.T) {
	for _, tc := range []struct {
		answer, quote string
		start, end    int
	}{
		{"Use “books”.", "Use book.", 0, 12},
		{"Do not use “book”.", "Do use book.", 0, 18},
		{"Use “books” and Use “books”", "Use books", -1, 10},
		{"Use “books” and Use “books”", "Use books", 1, 10},
		{"Use “books”.", "", 0, 12},
		{"Don’t use “book”.", "Dont use book.", 0, 17},
	} {
		s := AnswerSpan{tc.start, tc.end, tc.quote}
		before := s
		if err := normalizeAnswerSpan(tc.answer, &s); err == nil || s != before {
			t.Fatalf("a substantive or unresolved source change was accepted: %+v %v", s, err)
		}
	}
}
