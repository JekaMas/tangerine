package app

import (
	"encoding/json"
	"testing"
)

func TestReleaseMutationContextPositive(t *testing.T) {
	a, _ := generationRegistry("error-taxonomy.v1.yaml")
	r, _ := generationRegistry("mutation-recipes.v1.json")
	p, _ := generationRegistry("acoustic-production.v1.json")
	_, recipes, production, err := mutationSelection(map[string]any{"targets": []any{}}, a, r, p)
	if err != nil {
		t.Fatal(err)
	}
	selected, controls := mutationContextRecipes(recipes, production)
	if len(selected) != 122 || len(controls) != 122 {
		t.Fatal(len(selected), len(controls))
	}
	for i, v := range selected {
		row := v.(map[string]any)
		source := recipes[i].(map[string]any)
		if len(row) != 5 {
			t.Fatal(row)
		}
		for k, v := range row {
			a, _ := json.Marshal(v)
			b, _ := json.Marshal(source[k])
			if string(a) != string(b) {
				t.Fatal(k)
			}
		}
	}
	for i := range controls {
		source := production[i].(map[string]any)
		for k, v := range source {
			if k == "observation" || k == "source_recipe_id" || k == "original_operator" {
				continue
			}
			a, _ := json.Marshal(v)
			b, _ := json.Marshal(controls[i].(map[string]any)[k])
			if string(a) != string(b) {
				t.Fatal(k)
			}
		}
	}
}
func TestReleaseMutationContextSourcePreservedNegative(t *testing.T) {
	recipes := []any{map[string]any{"taxonomy_id": "leaf", "operator": "text", "procedure": "Apply the leaf.", "canonical_example": "Illustration only.", "empirical_leaf_frequency": nil}}
	production := []any{map[string]any{"taxonomy_id": "leaf", "controller": "phone_pair", "default_parameters": map[string]any{"reference_ipa": "pæn", "mutated_ipa": "pɛn"}, "future_control_operand": "retained", "observation": "not_run"}}
	before, _ := json.Marshal([]any{recipes, production})
	selected, controls := mutationContextRecipes(recipes, production)
	after, _ := json.Marshal([]any{recipes, production})
	if string(before) != string(after) {
		t.Fatal("Source records mutated")
	}
	if _, ok := selected[0].(map[string]any)["canonical_example"]; ok {
		t.Fatal("Illustration sent as exercise context")
	}
	if controls[0].(map[string]any)["future_control_operand"] != "retained" {
		t.Fatal("Control operand lost")
	}
}
