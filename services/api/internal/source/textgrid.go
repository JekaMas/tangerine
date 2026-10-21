package source

import (
	"fmt"
	"math/big"
	"strconv"
	"strings"
	"unicode"
)

func gridTokens(s string) ([]string, error) {
	a := []string{}
	for len(s) > 0 {
		s = strings.TrimLeftFunc(s, unicode.IsSpace)
		if s == "" {
			break
		}
		if s[0] == '"' {
			s = s[1:]
			var b strings.Builder
			closed := false
			for len(s) > 0 {
				if s[0] == '"' {
					if len(s) > 1 && s[1] == '"' {
						b.WriteByte('"')
						s = s[2:]
						continue
					}
					s = s[1:]
					closed = true
					break
				}
				b.WriteByte(s[0])
				s = s[1:]
			}
			if !closed {
				return nil, fmt.Errorf("unterminated Praat string")
			}
			a = append(a, b.String())
		} else {
			i := strings.IndexFunc(s, unicode.IsSpace)
			if i < 0 {
				i = len(s)
			}
			a = append(a, s[:i])
			s = s[i:]
		}
	}
	return a, nil
}
func parseTextGrid(member, text string) (Native, error) {
	intervals, points := []Row{}, []Row{}
	issues := []Issue{}
	var tier, kind string
	idx := 0
	start, end, label := "", "", ""
	var previous *big.Rat
	add := func() error {
		a, ok := new(big.Rat).SetString(start)
		if !ok {
			return fmt.Errorf("invalid interval start")
		}
		b, ok := new(big.Rat).SetString(end)
		if !ok {
			return fmt.Errorf("invalid interval end")
		}
		invalid := a.Sign() < 0 || b.Cmp(a) < 0 || (previous != nil && a.Cmp(previous) < 0)
		row := Row{"member": member, "tier": tier, "index": idx, "kind": kind, "start_seconds": start, "end_seconds": end, "label": label}
		if invalid {
			row["invalid"] = true
			issues = append(issues, Issue{fmt.Sprintf("%s:%s:%d", member, tier, idx), "textgrid_clock", "Negative, reversed or nonmonotonic native interval"})
		}
		if kind == "interval" {
			intervals = append(intervals, row)
		} else {
			points = append(points, row)
		}
		previous = b
		return nil
	}
	if strings.Contains(text, "item []:") {
		lines, e := gridLines(text)
		if e != nil {
			return Native{}, Failure(member, "textgrid_syntax", e.Error())
		}
		for _, line := range lines {
			line = strings.TrimSpace(line)
			k, v, ok := strings.Cut(line, "=")
			if !ok {
				continue
			}
			k = strings.TrimSpace(k)
			v = strings.TrimSpace(v)
			switch k {
			case "class":
				t, e := gridTokens(v)
				if e != nil || len(t) != 1 {
					return Native{}, Failure(member, "textgrid_syntax", "Invalid class")
				}
				if t[0] == "IntervalTier" {
					kind = "interval"
				} else if t[0] == "TextTier" {
					kind = "point"
				} else {
					kind = "unknown"
				}
				previous = nil
				idx = 0
			case "name":
				t, e := gridTokens(v)
				if e != nil || len(t) != 1 {
					return Native{}, Failure(member, "textgrid_syntax", "Invalid tier name")
				}
				tier = t[0]
			case "xmin":
				start = v
			case "xmax":
				end = v
			case "number":
				start = v
				end = v
			case "text", "mark":
				t, e := gridTokens(v)
				if e != nil || len(t) != 1 {
					return Native{}, Failure(member, "textgrid_syntax", "Invalid label")
				}
				label = t[0]
				idx++
				if e = add(); e != nil {
					return Native{}, Failure(member, "textgrid_clock", e.Error())
				}
			}
		}
	} else {
		t, e := gridTokens(text)
		if e != nil {
			return Native{}, Failure(member, "textgrid_syntax", e.Error())
		}
		at := -1
		for i, v := range t {
			if v == "<exists>" {
				at = i + 1
				break
			}
		}
		if at < 0 || at >= len(t) {
			return Native{}, Failure(member, "textgrid_syntax", "Missing short-syntax tier inventory")
		}
		count, e := strconv.Atoi(t[at])
		if e != nil {
			return Native{}, e
		}
		at++
		for j := 0; j < count; j++ {
			if at+5 > len(t) {
				return Native{}, Failure(member, "textgrid_syntax", "Truncated short tier")
			}
			cl := t[at]
			tier = t[at+1]
			n, e := strconv.Atoi(t[at+4])
			if e != nil {
				return Native{}, e
			}
			at += 5
			kind = "interval"
			width := 3
			if cl == "TextTier" {
				kind = "point"
				width = 2
			} else if cl != "IntervalTier" {
				return Native{}, Failure(member, "textgrid_syntax", "Unknown short tier structure retained raw")
			}
			previous = nil
			for i := 0; i < n; i++ {
				if at+width > len(t) {
					return Native{}, Failure(member, "textgrid_syntax", "Truncated short interval")
				}
				start = t[at]
				end = start
				if width == 3 {
					end = t[at+1]
				}
				label = t[at+width-1]
				at += width
				idx = i + 1
				if e = add(); e != nil {
					return Native{}, Failure(member, "textgrid_clock", e.Error())
				}
			}
		}
		if at != len(t) {
			return Native{}, Failure(member, "textgrid_syntax", "Unaccounted short-syntax values")
		}
	}
	return Native{Tables: []Table{{"intervals", member, intervals}, {"points", member, points}}, Issues: issues}, nil
}

// Praat quoted values may contain literal line breaks. Keep those bytes in the
// label while separating only unquoted structural lines; doubled quotes escape.
func gridLines(text string) ([]string, error) {
	lines := []string{}
	start := 0
	quoted := false
	for i := 0; i < len(text); i++ {
		if text[i] == '"' {
			if quoted && i+1 < len(text) && text[i+1] == '"' {
				i++
				continue
			}
			quoted = !quoted
		}
		if text[i] == '\n' && !quoted {
			lines = append(lines, text[start:i])
			start = i + 1
		}
	}
	if quoted {
		return nil, fmt.Errorf("unterminated Praat string")
	}
	if start < len(text) {
		lines = append(lines, text[start:])
	}
	return lines, nil
}
