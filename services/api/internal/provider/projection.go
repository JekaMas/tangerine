package provider

import (
	"encoding/json"
	"strings"
	"tangerine.local/api/internal/contracts"
)

// ProjectVisible never manufactures substantive fields. Raw visible output stays
// in the receipt; only additive fields are removed from the arithmetic projection.
func ProjectVisible(text, kind string) ([]byte, error) {
	registry, e := contracts.Registry()
	if e != nil {
		return nil, e
	}
	contract, ok := registry[kind]
	if !ok {
		return nil, fail("PROVIDER_OUTPUT_INVALID")
	}
	var schema map[string]any
	_ = json.Unmarshal(contract.Bytes, &schema)
	candidates := [][]byte{}
	var validationError error
	validationScore := -1
	recordError := func(score int, err error) {
		if score >= validationScore {
			validationScore, validationError = score, err
		}
	}
	quoted, escape := false, false
	starts := []int{}
	for i, c := range text {
		if quoted {
			if escape {
				escape = false
			} else if c == '\\' {
				escape = true
			} else if c == '"' {
				quoted = false
			}
			continue
		}
		if c == '"' {
			quoted = true
			continue
		}
		if c == '{' {
			starts = append(starts, i)
		}
		if c == '}' && len(starts) > 0 {
			a := starts[len(starts)-1]
			starts = starts[:len(starts)-1]
			raw := []byte(text[a : i+1])
			var object map[string]any
			_ = json.Unmarshal(raw, &object)
			score := 0
			properties, _ := schema["properties"].(map[string]any)
			for k := range object {
				if _, ok := properties[k]; ok {
					score++
				}
			}
			if _, e = contracts.Canonical(raw); e != nil {
				recordError(score, e)
				continue
			}
			var value any
			if json.Unmarshal(raw, &value) != nil {
				continue
			}
			value = projectValue(value, schema, registry)
			b, _ := json.Marshal(value)
			_, b, e = contracts.Validate(kind, contract.Version, b)
			if e == nil {
				candidates = append(candidates, b)
			} else {
				recordError(score, e)
			}
		}
	}
	if len(candidates) == 0 {
		if validationError != nil {
			return nil, &OutputValidationError{Detail: validationError.Error()}
		}
		return nil, fail("PROVIDER_OUTPUT_INVALID")
	}
	first := string(candidates[0])
	for _, c := range candidates[1:] {
		if string(c) != first {
			return nil, fail("PROVIDER_OUTPUT_INVALID")
		}
	}
	return candidates[0], nil
}
func resolveSchema(schema map[string]any, registry map[string]contracts.Contract) map[string]any {
	ref, _ := schema["$ref"].(string)
	if ref == "" {
		return schema
	}
	name, path, _ := strings.Cut(ref, "#")
	name = strings.TrimSuffix(name, ".schema.json")
	c, ok := registry[name]
	if !ok {
		return schema
	}
	var root any
	_ = json.Unmarshal(c.Bytes, &root)
	for _, p := range strings.Split(strings.TrimPrefix(path, "/"), "/") {
		if p == "" {
			continue
		}
		m, ok := root.(map[string]any)
		if !ok {
			return schema
		}
		root = m[p]
	}
	v, ok := root.(map[string]any)
	if !ok {
		return schema
	}
	return v
}
func projectValue(value any, schema map[string]any, registry map[string]contracts.Contract) any {
	schema = resolveSchema(schema, registry)
	for _, keyword := range []string{"anyOf", "oneOf"} {
		if alternatives, ok := schema[keyword].([]any); ok {
			for _, a := range alternatives {
				m, ok := a.(map[string]any)
				if !ok {
					continue
				}
				m = resolveSchema(m, registry)
				if matchesShape(value, m) {
					return projectValue(value, m, registry)
				}
			}
		}
	}
	switch v := value.(type) {
	case map[string]any:
		props, ok := schema["properties"].(map[string]any)
		if !ok {
			return value
		}
		out := map[string]any{}
		for k, x := range v {
			if spec, ok := props[k].(map[string]any); ok {
				out[k] = projectValue(x, spec, registry)
			} else if schema["additionalProperties"] != false {
				out[k] = x
			}
		}
		return out
	case []any:
		if item, ok := schema["items"].(map[string]any); ok {
			out := make([]any, len(v))
			for i, x := range v {
				out[i] = projectValue(x, item, registry)
			}
			return out
		}
	}
	return value
}
func matchesShape(v any, s map[string]any) bool {
	if c, ok := s["const"]; ok {
		a, _ := json.Marshal(c)
		b, _ := json.Marshal(v)
		if string(a) != string(b) {
			return false
		}
	}
	switch s["type"] {
	case "null":
		return v == nil
	case "string":
		_, ok := v.(string)
		return ok
	case "object":
		m, ok := v.(map[string]any)
		if !ok {
			return false
		}
		if required, ok := s["required"].([]any); ok {
			for _, k := range required {
				if _, ok = m[k.(string)]; !ok {
					return false
				}
			}
		}
		if ps, ok := s["properties"].(map[string]any); ok {
			for k, p := range ps {
				if x, ok := m[k]; ok {
					if d, ok := p.(map[string]any); ok {
						if c, ok := d["const"]; ok {
							a, _ := json.Marshal(c)
							b, _ := json.Marshal(x)
							if string(a) != string(b) {
								return false
							}
						}
					}
				}
			}
		}
		return true
	case "array":
		_, ok := v.([]any)
		return ok
	}
	return true
}
