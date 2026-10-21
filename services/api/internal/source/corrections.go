package source

import (
	"fmt"
	"sort"
	"strings"
)

func CorrectionViews(row Row) map[string]any {
	by := map[string][]map[string]any{}
	for _, v := range asArray(row["edits"]) {
		var m map[string]any
		switch x := v.(type) {
		case map[string]any:
			m = x
		case Row:
			m = map[string]any(x)
		}
		if m == nil {
			continue
		}
		annotator, _ := m["annotator"].(string)
		by[annotator] = append(by[annotator], m)
	}
	views := map[string]any{}
	text, _ := row["text"].(string)
	for annotator, edits := range by {
		type edit struct {
			a, b int
			text string
		}
		list := []edit{}
		ambiguous := false
		for _, e := range edits {
			if e["noop"] == true {
				continue
			}
			a, ea := strconvInteger(e["start"])
			b, eb := strconvInteger(e["end"])
			correction, _ := e["correction"].(string)
			if ea != nil || eb != nil || a < 0 || b < a || e["invalid"] == true {
				ambiguous = true
				continue
			}
			list = append(list, edit{a, b, correction})
		}
		sort.SliceStable(list, func(i, j int) bool { return list[i].a < list[j].a })
		for i := 1; i < len(list); i++ {
			if list[i].a < list[i-1].b || list[i].a == list[i-1].a {
				ambiguous = true
			}
		}
		if ambiguous {
			views[annotator] = map[string]any{"text": nil, "status": "ambiguous_native_edit_set"}
			continue
		}
		tokens := strings.Split(text, " ")
		for i := len(list) - 1; i >= 0; i-- {
			e := list[i]
			if e.b > len(tokens) {
				ambiguous = true
				break
			}
			replacement := []string{}
			if e.text != "" && e.text != "-NONE-" {
				replacement = strings.Split(e.text, " ")
			}
			t := append([]string{}, tokens[:e.a]...)
			t = append(t, replacement...)
			tokens = append(t, tokens[e.b:]...)
		}
		if ambiguous {
			views[annotator] = map[string]any{"text": nil, "status": "invalid_native_edit_set"}
		} else {
			views[annotator] = map[string]any{"text": strings.Join(tokens, " "), "status": "derived_single_annotator", "method": "native-m2-reverse-v1"}
		}
	}
	return views
}
func strconvInteger(v any) (int, error) {
	s := fmt.Sprint(v)
	var n int
	_, e := fmt.Sscan(s, &n)
	return n, e
}
