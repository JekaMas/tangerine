package app

import (
	"regexp"
	"strings"
	"tangerine.local/api/internal/source"
)

// The context frame wraps an asset as {asset_id,sha256,body}. Accept the observed
// unambiguous /body/... locator once, while saving its canonical asset-relative
// pointer. Unknown assets, absent targets and substantive verdicts stay unchanged.
func normalizeQualityJudge(value any, assets map[string]any) any {
	out, ok := value.(map[string]any)
	if !ok {
		return value
	}
	verdicts, _ := out["verdicts"].([]any)
	for _, v := range verdicts {
		m, ok := v.(map[string]any)
		if !ok {
			continue
		}
		evidence, _ := m["evidence"].([]any)
		for _, v := range evidence {
			ref, ok := v.(map[string]any)
			if !ok {
				continue
			}
			id, _ := ref["asset_id"].(string)
			pointer, _ := ref["pointer"].(string)
			body, ok := assets[id]
			if !ok {
				continue
			}
			if converted, ok := simpleQualityJSONPath(pointer); ok {
				pointer = converted
			}
			if _, ok := source.Pointer(body, pointer); ok {
				ref["pointer"] = pointer
				continue
			}
			if len(pointer) > 5 && pointer[:5] == "/body" {
				if _, ok := source.Pointer(body, pointer[5:]); ok {
					ref["pointer"] = pointer[5:]
				}
			}
		}
	}
	return out
}

var qualityJSONPath = regexp.MustCompile(`^\$(?:\.[A-Za-z_][A-Za-z0-9_]*|\[(?:0|[1-9][0-9]*)\])*$`)
var qualityJSONPathPart = regexp.MustCompile(`\.([A-Za-z_][A-Za-z0-9_]*)|\[([0-9]+)\]`)

// Convert only literal field/index paths; never execute JSONPath expressions.
func simpleQualityJSONPath(path string) (string, bool) {
	if !qualityJSONPath.MatchString(path) {
		return path, false
	}
	parts := []string{}
	for _, m := range qualityJSONPathPart.FindAllStringSubmatch(path, -1) {
		p := m[1]
		if p == "" {
			p = m[2]
		}
		parts = append(parts, strings.ReplaceAll(strings.ReplaceAll(p, "~", "~0"), "/", "~1"))
	}
	if len(parts) == 0 {
		return "", true
	}
	return "/" + strings.Join(parts, "/"), true
}
