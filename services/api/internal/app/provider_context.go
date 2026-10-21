package app

import (
	"bytes"
	"encoding/json"
	"strings"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
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

// Decoding is an explicit profile choice, separate from the single admission.
func inferenceOutputFormat(p provider.Profile, schema json.RawMessage) (any, error) {
	mode := p.ResponseFormat
	if mode == "" {
		if p.StructuredOutput {
			mode = "json_schema"
		} else {
			mode = "text"
		}
	}
	switch mode {
	case "text":
		return nil, nil
	case "json_object", "json_schema":
		if p.Provider == "openai_chatgpt" {
			return nil, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
		}
	default:
		return nil, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
	}
	if mode == "json_object" {
		// Ollama Responses accepts schema format, not OpenAI's json_object type.
		// This grammar constrains JSON syntax only. The complete stage contract is
		// still supplied in context and admitted once by the application.
		if p.Provider != "local_responses" {
			return map[string]any{"type": "json_object"}, nil
		}
		schema = json.RawMessage(`{"type":"object"}`)
	}
	return map[string]any{"type": "json_schema", "name": "tangerine_output", "strict": true, "schema": schema}, nil
}
