package provider

import (
	"encoding/json"
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
