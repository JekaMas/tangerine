package contracts

import (
	"bytes"
	"encoding/json"
	"fmt"
	"strings"
)

// WireSchema supplies the complete registered contract without network refs.
// Registry admission already owns validation; this is only a wire projection.
func WireSchema(kind string) ([]byte, error) {
	registry, err := Registry()
	if err != nil {
		return nil, err
	}
	definitions := map[string]any{}
	seen := map[string]bool{}
	pointer := func(name string) string {
		return "#/$defs/" + strings.ReplaceAll(strings.ReplaceAll(name, "~", "~0"), "/", "~1")
	}
	var include func(string) error
	var walk func(any, string) (any, error)
	walk = func(value any, scope string) (any, error) {
		switch node := value.(type) {
		case []any:
			out := make([]any, len(node))
			for i, v := range node {
				x, e := walk(v, scope)
				if e != nil {
					return nil, e
				}
				out[i] = x
			}
			return out, nil
		case map[string]any:
			out := map[string]any{}
			for key, v := range node {
				if key == "$id" {
					continue
				}
				if key == "const" || key == "enum" || key == "default" || key == "examples" {
					out[key] = v
					continue
				}
				if ref, ok := v.(string); key == "$ref" && ok {
					name, fragment, _ := strings.Cut(ref, "#")
					target := scope
					if name != "" {
						target = strings.TrimSuffix(strings.TrimPrefix(name, "https://tangerine.invalid/schemas/"), ".schema.json")
						if e := include(target); e != nil {
							return nil, e
						}
					}
					out[key] = pointer(target) + fragment
					continue
				}
				x, e := walk(v, scope)
				if e != nil {
					return nil, e
				}
				out[key] = x
			}
			return out, nil
		default:
			return value, nil
		}
	}
	include = func(name string) error {
		if seen[name] {
			return nil
		}
		c, ok := registry[name]
		if !ok {
			return fmt.Errorf("unknown wire contract: %s", name)
		}
		seen[name] = true
		var node any
		d := json.NewDecoder(bytes.NewReader(c.Bytes))
		d.UseNumber()
		if e := d.Decode(&node); e != nil {
			return e
		}
		value, e := walk(node, name)
		if e != nil {
			return e
		}
		definitions[name] = value
		return nil
	}
	if err = include(kind); err != nil {
		return nil, err
	}
	raw, err := json.Marshal(map[string]any{"$schema": "https://json-schema.org/draft/2020-12/schema", "$ref": pointer(kind), "$defs": definitions})
	if err != nil {
		return nil, err
	}
	return Canonical(raw)
}
