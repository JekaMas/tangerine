package app

// Source normalization owns exact spans, stable identities and source relations.
// It does not see the exercise key, assign targets, or calculate a grade.
import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
	"unicode"
	"unicode/utf8"

	"golang.org/x/text/unicode/norm"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

type AnswerSpan struct {
	Start int    `json:"start_cp"`
	End   int    `json:"end_cp"`
	Text  string `json:"exact_text"`
}
type ExtractedClause struct {
	Span       AnswerSpan  `json:"claim_span"`
	Stance     string      `json:"stance"`
	Target     *AnswerSpan `json:"target_span"`
	Category   *AnswerSpan `json:"category_span"`
	Correction *AnswerSpan `json:"correction_span"`
	Rationale  *AnswerSpan `json:"rationale_span"`
	Retraction *AnswerSpan `json:"explicit_retraction_of_span"`
	LocalRef   string      `json:"local_ref"`
}
type ClaimRelation struct {
	From     string `json:"from_claim_ref"`
	To       string `json:"to_claim_ref"`
	Kind     string `json:"kind"`
	Evidence struct {
		Start int `json:"start"`
		End   int `json:"end"`
	} `json:"evidence_span"`
}
type ClaimCoverage struct {
	Span struct {
		Start int `json:"start"`
		End   int `json:"end"`
	} `json:"span"`
	Kind   string   `json:"kind"`
	Refs   []string `json:"claim_refs"`
	Reason string   `json:"reason"`
}
type AnswerExtraction struct {
	Version   string            `json:"schema_version"`
	Clauses   []ExtractedClause `json:"clauses"`
	Unparsed  []AnswerSpan      `json:"unparsed_spans"`
	Coverage  []ClaimCoverage   `json:"coverage"`
	Relations []ClaimRelation   `json:"relations"`
}
type CanonicalClaim struct {
	ExtractedClause
	ID           string       `json:"id"`
	Group        string       `json:"group_id"`
	Active       bool         `json:"active"`
	Corrections  []AnswerSpan `json:"correction_spans"`
	Explanations []AnswerSpan `json:"explanation_spans"`
	Categories   []AnswerSpan `json:"category_spans"`
}
type CanonicalExtraction struct {
	Extraction AnswerExtraction `json:"extraction"`
	Claims     []CanonicalClaim `json:"claims"`
	Conflicts  []string         `json:"conflicts"`
}

func interpretationInvalid(detail string) error {
	return &provider.OutputValidationError{Detail: detail}
}
func inAnswer(runes []rune, s AnswerSpan) bool {
	return s.Start >= 0 && s.Start < s.End && s.End <= len(runes) && string(runes[s.Start:s.End]) == s.Text
}
func containsAnswerSpan(outer, inner AnswerSpan) bool {
	return outer.Start <= inner.Start && inner.End <= outer.End
}

// Recover only exact evidence: correct codepoints, matching UTF-16 coordinates,
// or one unique literal quote. Ambiguous repeated quotes remain unresolved.
func normalizeAnswerSpan(text string, s *AnswerSpan) error {
	if s == nil {
		return nil
	}
	runes := []rune(text)
	if inAnswer(runes, *s) {
		return nil
	}
	utf16Start, utf16End, clock := -1, -1, 0
	for i, r := range runes {
		if clock == s.Start {
			utf16Start = i
		}
		if clock == s.End {
			utf16End = i
		}
		clock++
		if r > 0xffff {
			clock++
		}
	}
	if clock == s.End {
		utf16End = len(runes)
	}
	translated := AnswerSpan{Start: utf16Start, End: utf16End, Text: s.Text}
	if inAnswer(runes, translated) {
		*s = translated
		return nil
	}
	if s.Text != "" {
		pos := strings.Index(text, s.Text)
		if pos >= 0 && !strings.Contains(text[pos+len(s.Text):], s.Text) {
			s.Start = utf8.RuneCountInString(text[:pos])
			s.End = s.Start + utf8.RuneCountInString(s.Text)
			return nil
		}
	}
	return interpretationInvalid("A source span must quote its exact original answer location; an ambiguous repeated quote cannot be guessed.")
}
func sourceIdentity(answerSHA string, s AnswerSpan) string {
	raw, _ := lab.Canonical([]any{answerSHA, s.Start, s.End, s.Text})
	h := sha256.Sum256(raw)
	return "clm_" + hex.EncodeToString(h[:])[:32]
}
func duplicateWording(s string) string {
	return strings.Join(strings.Fields(norm.NFC.String(strings.NewReplacer("’", "'", "‘", "'").Replace(s))), " ")
}
func normalizeExtraction(answer, answerSHA string, raw []byte) (CanonicalExtraction, error) {
	result := CanonicalExtraction{Claims: []CanonicalClaim{}, Conflicts: []string{}}
	if err := json.Unmarshal(raw, &result.Extraction); err != nil {
		return result, interpretationInvalid("Extraction must be a JSON object.")
	}
	x := &result.Extraction
	if x.Clauses == nil {
		x.Clauses = []ExtractedClause{}
	}
	if x.Unparsed == nil {
		x.Unparsed = []AnswerSpan{}
	}
	if x.Relations == nil {
		x.Relations = []ClaimRelation{}
	}
	byRef := map[string]int{}
	ids := map[string]ExtractedClause{}
	conflicting := map[string]bool{}
	for i := range x.Clauses {
		c := &x.Clauses[i]
		if _, exists := byRef[c.LocalRef]; exists {
			return result, interpretationInvalid("Extraction-local references must identify distinct original claims.")
		}
		byRef[c.LocalRef] = i
		for _, span := range []*AnswerSpan{&c.Span, c.Target, c.Category, c.Correction, c.Rationale, c.Retraction} {
			if err := normalizeAnswerSpan(answer, span); err != nil {
				return result, err
			}
		}
		for _, span := range []*AnswerSpan{c.Target, c.Category, c.Correction, c.Rationale} {
			if span != nil && !containsAnswerSpan(c.Span, *span) {
				return result, interpretationInvalid("Keep each component inside its original claim, or use an explicit attachment clause/relation.")
			}
		}
		id := sourceIdentity(answerSHA, c.Span)
		if previous, exists := ids[id]; exists {
			left, right := previous, *c
			left.LocalRef = ""
			right.LocalRef = ""
			if lab.Hash(left) != lab.Hash(right) {
				conflicting[id] = true
			}
		} else {
			ids[id] = *c
		}
	}
	sort.SliceStable(x.Clauses, func(i, j int) bool {
		a, b := x.Clauses[i], x.Clauses[j]
		if a.Span.Start != b.Span.Start {
			return a.Span.Start < b.Span.Start
		}
		if a.Span.End != b.Span.End {
			return a.Span.End < b.Span.End
		}
		return false // Stable original output position resolves equal source spans.
	})
	byRef = map[string]int{}
	canonicalIndex := map[string]int{}
	for _, c := range x.Clauses {
		id := sourceIdentity(answerSHA, c.Span)
		if existing, ok := canonicalIndex[id]; ok {
			byRef[c.LocalRef] = existing
			continue
		}
		byRef[c.LocalRef] = len(result.Claims)
		canonicalIndex[id] = len(result.Claims)
		out := CanonicalClaim{ExtractedClause: c, ID: id, Group: id, Active: c.Stance != "retracted", Corrections: []AnswerSpan{}, Explanations: []AnswerSpan{}, Categories: []AnswerSpan{}}
		if c.Correction != nil {
			out.Corrections = append(out.Corrections, *c.Correction)
		}
		if c.Rationale != nil {
			out.Explanations = append(out.Explanations, *c.Rationale)
		}
		if c.Category != nil {
			out.Categories = append(out.Categories, *c.Category)
		}
		if conflicting[id] {
			out.Active = true
			result.Conflicts = append(result.Conflicts, id)
		}
		result.Claims = append(result.Claims, out)
	}
	sort.SliceStable(x.Relations, func(i, j int) bool { return byRef[x.Relations[i].From] < byRef[x.Relations[j].From] })
	for _, rel := range x.Relations {
		a, okA := byRef[rel.From]
		b, okB := byRef[rel.To]
		if !okA || !okB || a <= b || result.Claims[a].Span.Start <= result.Claims[b].Span.Start {
			return result, interpretationInvalid("Relations require an actual later source claim and an earlier distinct claim.")
		}
		if rel.Evidence.Start < 0 || rel.Evidence.Start >= rel.Evidence.End || rel.Evidence.End > len([]rune(answer)) {
			return result, interpretationInvalid("Relation evidence must be an actual original source interval.")
		}
		later, earlier := &result.Claims[a], &result.Claims[b]
		if rel.Kind == "retracts" {
			if rel.Evidence.Start < earlier.Span.End {
				return result, interpretationInvalid("A retraction must follow its earlier assertion.")
			}
			earlier.Active = false
		} else if rel.Kind == "exact_duplicate" {
			if duplicateWording(later.Span.Text) != duplicateWording(earlier.Span.Text) {
				return result, interpretationInvalid("Exact duplicate normalization cannot erase case or punctuation or change substantive wording.")
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
				return result, interpretationInvalid("Attachment has no source representative.")
			}
			if rel.Kind == "correction_attachment" || rel.Kind == "compatible_fragment" {
				root.Corrections = append(root.Corrections, later.Corrections...)
			}
			if rel.Kind == "explanation_attachment" || rel.Kind == "compatible_fragment" {
				root.Explanations = append(root.Explanations, later.Explanations...)
			}
			root.Categories = append(root.Categories, later.Categories...)
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
				return result, interpretationInvalid("The explicit retraction must name an earlier actual claim.")
			}
		}
	}
	for i := range x.Unparsed {
		if err := normalizeAnswerSpan(answer, &x.Unparsed[i]); err != nil {
			return result, err
		}
	}
	// Derive a complete disjoint partition; optional model coverage hints never
	// erase source text. Uncovered substantive content invokes the existing repair.
	runes := []rune(answer)
	x.Coverage = []ClaimCoverage{}
	for start := 0; start < len(runes); {
		refs := []string{}
		kind, reason := "", ""
		end := len(runes)
		for _, c := range x.Clauses {
			if c.Span.Start > start && c.Span.Start < end {
				end = c.Span.Start
			}
			if c.Span.Start <= start && start < c.Span.End {
				refs = append(refs, c.LocalRef)
				if c.Span.End < end {
					end = c.Span.End
				}
			}
		}
		if len(refs) > 0 {
			kind = "claim"
		} else {
			for _, span := range x.Unparsed {
				if span.Start > start && span.Start < end {
					end = span.Start
				}
				if span.Start <= start && start < span.End {
					kind = "unparsed"
					reason = "Substantive meaning explicitly remains unresolved"
					if span.End < end {
						end = span.End
					}
				}
			}
			if kind == "" {
				end = start
				for end < len(runes) && unicode.IsSpace(runes[end]) {
					end++
				}
				if end == start {
					return result, interpretationInvalid(fmt.Sprintf("Interpret or explicitly retain the uncovered substantive answer beginning at codepoint %d; do not invent missing text.", start))
				}
				kind = "whitespace"
			}
		}
		if len(refs) > 1 {
			first := result.Claims[byRef[refs[0]]]
			for _, ref := range refs[1:] {
				other := result.Claims[byRef[ref]]
				if first.ID != other.ID && (first.Group != other.Group || (!containsAnswerSpan(first.Span, other.Span) && !containsAnswerSpan(other.Span, first.Span))) {
					return result, interpretationInvalid("Overlapping claims require a declared contained attachment; competing identical spans stay explicitly unresolved.")
				}
			}
		}
		cell := ClaimCoverage{Kind: kind, Refs: refs, Reason: reason}
		cell.Span.Start = start
		cell.Span.End = end
		x.Coverage = append(x.Coverage, cell)
		start = end
	}
	return result, nil
}
