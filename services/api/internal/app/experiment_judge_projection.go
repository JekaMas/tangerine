package app

import (
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
			if _, ok := source.Pointer(body, pointer); ok {
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
