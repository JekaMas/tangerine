package app

import (
	"bytes"
	"strings"
	"tangerine.local/api/internal/lab"
)

// inferenceFrame keeps the complete typed input once. Component evidence remains
// separately saved. Mutation components already present verbatim in that input
// need no second message. Custom/different components are retained, never rejected.
func inferenceFrame(prepared lab.Prepared, stage string, phase *string, inputDTO map[string]any) (string, []any) {
	instructions := []string{}
	messages := []any{}
	mutation := stage == "case_generation" && phase != nil && *phase == "mutation"
	for _, part := range prepared.Parts {
		if part.Trust == "owned_instruction" {
			instructions = append(instructions, part.Kind+": "+string(part.Body))
		} else if !mutation || !mutationInputCovers(part, inputDTO) {
			messages = append(messages, map[string]any{"role": "user", "content": part.Kind + ": " + string(part.Body)})
		}
	}
	typed, _ := lab.Canonical(inputDTO)
	messages = append(messages, map[string]any{"role": "user", "content": "Complete stage input: " + string(typed)})
	return strings.Join(instructions, "\n"), messages
}

func mutationInputCovers(part lab.Part, input map[string]any) bool {
	var value any
	switch part.Kind {
	case "blueprint":
		value = input["blueprint"]
	case "taxonomy":
		value = input["taxonomy_context"]
	case "canonical_script":
		value = input["canonical_script"]
	case "recipes":
		value = map[string]any{"mutation_recipes": input["mutation_recipes"], "production_recipes": input["production_recipes"]}
	case "public_context":
		b, ok := input["blueprint"].(map[string]any)
		if !ok {
			return false
		}
		value = b["public_context"]
	default:
		return false
	}
	if value == nil {
		return false
	}
	raw, _ := lab.Canonical(value)
	return bytes.Equal(raw, part.Body)
}
