package provider

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"reflect"
	"strings"
)

// An opt-in stage can complete missing container punctuation after complete JSON
// values. No quote, value, property or assertion is invented; raw receipts stay raw.
func completeStageContainers(text string) string {
	trimmed := strings.TrimSpace(text)
	if !strings.HasPrefix(trimmed, "{") {
		return text
	}
	stack := []byte{}
	quoted, escaped := false, false
	for i := 0; i < len(trimmed); i++ {
		c := trimmed[i]
		if quoted {
			if escaped {
				escaped = false
			} else if c == '\\' {
				escaped = true
			} else if c == '"' {
				quoted = false
			}
			continue
		}
		switch c {
		case '"':
			quoted = true
		case '{':
			stack = append(stack, '}')
		case '[':
			stack = append(stack, ']')
		case '}', ']':
			if len(stack) == 0 || stack[len(stack)-1] != c {
				return text
			}
			stack = stack[:len(stack)-1]
		}
	}
	if quoted || len(stack) == 0 {
		return text
	}
	for i, j := 0, len(stack)-1; i < j; i, j = i+1, j-1 {
		stack[i], stack[j] = stack[j], stack[i]
	}
	completed := trimmed + string(stack)
	if !json.Valid([]byte(completed)) {
		return text
	}
	return completed
}

// Normalize identical repeated model fields at the existing admission. Keep
// conflicting values ambiguous; never choose a favorable assertion or rewrite it.
func stageJSON(raw []byte) ([]byte, error) {
	d := json.NewDecoder(bytes.NewReader(raw))
	d.UseNumber()
	var read func() (any, error)
	read = func() (any, error) {
		token, e := d.Token()
		if e != nil {
			return nil, e
		}
		switch token {
		case json.Delim('{'):
			out := map[string]any{}
			for d.More() {
				key, e := d.Token()
				if e != nil {
					return nil, e
				}
				name, ok := key.(string)
				if !ok {
					return nil, errors.New("invalid model object key")
				}
				value, e := read()
				if e != nil {
					return nil, e
				}
				if previous, exists := out[name]; exists && !reflect.DeepEqual(previous, value) {
					return nil, errors.New("conflicting repeated model field")
				}
				out[name] = value
			}
			if _, e = d.Token(); e != nil {
				return nil, e
			}
			return out, nil
		case json.Delim('['):
			out := []any{}
			for d.More() {
				value, e := read()
				if e != nil {
					return nil, e
				}
				out = append(out, value)
			}
			if _, e = d.Token(); e != nil {
				return nil, e
			}
			return out, nil
		default:
			return token, nil
		}
	}
	value, e := read()
	if e != nil {
		return nil, e
	}
	if _, e = d.Token(); e != io.EOF {
		return nil, errors.New("invalid trailing model content")
	}
	return json.Marshal(value)
}
