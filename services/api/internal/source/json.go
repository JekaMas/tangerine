package source

import (
	"encoding/json"
	"fmt"
	"io"
)

// orderedJSON retains every original object occurrence/key order and exact number
// lexeme alongside the pointer-addressable value. Duplicate keys are never silently
// used as semantic truth; the complete source tree remains available for binding.
func orderedJSON(d *json.Decoder) (any, any, bool, error) {
	token, e := d.Token()
	if e != nil {
		return nil, nil, false, e
	}
	switch t := token.(type) {
	case json.Delim:
		if t == '{' {
			value := map[string]any{}
			entries := []any{}
			duplicate := false
			for d.More() {
				k, e := d.Token()
				if e != nil {
					return nil, nil, false, e
				}
				key, ok := k.(string)
				if !ok {
					return nil, nil, false, fmt.Errorf("JSON object key expected")
				}
				v, tree, dup, e := orderedJSON(d)
				if e != nil {
					return nil, nil, false, e
				}
				if _, ok := value[key]; ok {
					duplicate = true
				}
				duplicate = duplicate || dup
				value[key] = v
				entries = append(entries, map[string]any{"key": key, "value": tree})
			}
			if _, e = d.Token(); e != nil {
				return nil, nil, false, e
			}
			return value, map[string]any{"entries": entries}, duplicate, nil
		}
		if t == '[' {
			values, trees := []any{}, []any{}
			duplicate := false
			for d.More() {
				v, tree, dup, e := orderedJSON(d)
				if e != nil {
					return nil, nil, false, e
				}
				values = append(values, v)
				trees = append(trees, tree)
				duplicate = duplicate || dup
			}
			if _, e = d.Token(); e != nil {
				return nil, nil, false, e
			}
			return values, trees, duplicate, nil
		}
		return nil, nil, false, fmt.Errorf("unexpected JSON delimiter")
	case json.Number:
		return t, map[string]any{"number_lexeme": string(t)}, false, nil
	default:
		return token, token, false, nil
	}
}
func jsonEOF(d *json.Decoder) bool { _, e := d.Token(); return e == io.EOF }
