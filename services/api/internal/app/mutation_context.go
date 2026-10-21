package app

// All selected identities and operative rules remain visible. Full source
// records (including illustrations/acquisition/benchmark metadata) remain in
// the frozen registry assets; they are not another exercise for the LLM to copy.
func mutationContextRecipes(recipes, production []any) ([]any, []any) {
	selected := []any{}
	for _, value := range recipes {
		source := value.(map[string]any)
		row := map[string]any{}
		for _, field := range []string{"taxonomy_id", "reporting_domain", "realization_mode", "operator", "procedure"} {
			row[field] = source[field]
		}
		selected = append(selected, row)
	}
	controls := []any{}
	for _, value := range production {
		row := map[string]any{}
		for field, value := range value.(map[string]any) {
			if field != "source_recipe_id" && field != "observation" && field != "original_operator" {
				row[field] = value
			}
		}
		controls = append(controls, row)
	}
	return selected, controls
}
