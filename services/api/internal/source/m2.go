package source

import (
	"bufio"
	"fmt"
	"io"
	"strconv"
	"strings"
	"unicode/utf8"
)

func parseM2(member, text string) (Native, error) {
	sentences, edits := []Row{}, []Row{}
	issues := []Issue{}
	r := bufio.NewReader(strings.NewReader(text))
	var current Row
	line := 0
	flush := func() {
		if current != nil {
			sentences = append(sentences, current)
			current = nil
		}
	}
	for {
		raw, e := r.ReadString('\n')
		line++
		s := strings.TrimSuffix(strings.TrimSuffix(raw, "\n"), "\r")
		switch {
		case strings.HasPrefix(s, "S "):
			flush()
			s = s[2:]
			tokens := strings.Split(s, " ")
			bounds := []any{}
			at := 0
			for _, t := range tokens {
				bounds = append(bounds, []int{at, at + utf8.RuneCountInString(t)})
				at += utf8.RuneCountInString(t) + 1
			}
			current = Row{"member": member, "sentence_index": len(sentences), "text": s, "tokens": tokens, "token_codepoints": bounds, "edits": []any{}, "line_ending": strings.TrimPrefix(raw, strings.TrimRight(raw, "\r\n")), "labels_state": "labels_supplied"}
		case strings.HasPrefix(s, "A "):
			if current == nil {
				return Native{}, Failure(fmt.Sprintf("%s:%d", member, line), "m2_sentence", "Annotation before S-line")
			}
			parts := strings.Split(s[2:], "|||")
			loc := fmt.Sprintf("%s:%d", member, line)
			if len(parts) < 6 {
				issues = append(issues, Issue{loc, "m2_annotation", "Expected six native annotation fields"})
				current["invalid"] = true
				break
			}
			span := strings.Fields(parts[0])
			a, b := -2, -2
			var ea, eb error
			if len(span) == 2 {
				a, ea = strconv.Atoi(span[0])
				b, eb = strconv.Atoi(span[1])
			}
			label := parts[1]
			invalid := len(span) != 2 || ea != nil || eb != nil || (a == -1 || b == -1) && (a != -1 || b != -1 || label != "noop") || (a >= 0 && (b < a || b > len(current["tokens"].([]string)))) || a < -1 || b < -1
			row := Row{"member": member, "sentence_index": len(sentences), "annotator": parts[5], "start": a, "end": b, "label": label, "correction": parts[2], "fields": parts, "raw": s, "noop": a == -1 && b == -1 && label == "noop"}
			if invalid {
				issues = append(issues, Issue{loc, "m2_span", "Invalid source sentinel or token bounds"})
				current["invalid"] = true
				row["invalid"] = true
			} else if a >= 0 {
				span, e := TokenSpan(current["text"].(string), a, b)
				if e != nil {
					return Native{}, e
				}
				row["codepoint_span"] = span
			}
			current["edits"] = append(current["edits"].([]any), row)
			edits = append(edits, row)
		case s == "":
			flush()
		default:
			if current != nil {
				a, _ := current["ancillary"].([]string)
				current["ancillary"] = append(a, s)
			}
		}
		if e == io.EOF {
			break
		}
		if e != nil {
			return Native{}, e
		}
	}
	flush()
	return Native{Tables: []Table{{"sentences", member, sentences}, {"edits", member, edits}}, Issues: issues}, nil
}
func TokenSpan(text string, a, b int) ([]int, error) {
	tokens := strings.Split(text, " ")
	if a < 0 || b < a || b > len(tokens) {
		return nil, fmt.Errorf("invalid token span")
	}
	at := 0
	bounds := make([]int, len(tokens)+1)
	for i, t := range tokens {
		bounds[i] = at
		at += utf8.RuneCountInString(t) + 1
	}
	bounds[len(tokens)] = utf8.RuneCountInString(text)
	end := bounds[b]
	if a < b && b < len(tokens) {
		end--
	}
	return []int{bounds[a], end}, nil
}
