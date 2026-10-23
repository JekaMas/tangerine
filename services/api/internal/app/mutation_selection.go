package app

import (
	"encoding/json"
	"go.yaml.in/yaml/v3"
	"strings"
	"tangerine.local/api/internal/contracts"
)

// MutationSelection projects the complete requested families/leaves from frozen
// source definitions. Corpus names inside recipes are metadata, never excerpts.
func mutationSelection(blueprint map[string]any, taxonomyBytes, recipeBytes, productionBytes []byte) (map[string]any, []any, []any, error) {
	var taxonomy map[string]any
	if e := yaml.Unmarshal(taxonomyBytes, &taxonomy); e != nil {
		return nil, nil, nil, e
	}
	var recipe, production map[string]any
	if e := json.Unmarshal(recipeBytes, &recipe); e != nil {
		return nil, nil, nil, e
	}
	if e := json.Unmarshal(productionBytes, &production); e != nil {
		return nil, nil, nil, e
	}
	requested := map[string]bool{}
	for _, v := range blueprint["targets"].([]any) {
		requested[v.(map[string]any)["taxonomy_id"].(string)] = true
	}
	families := []string{}
	exact := map[string]bool{}
	if r, ok := blueprint["exercise_request"].(map[string]any); ok {
		for _, v := range r["category_families"].([]any) {
			families = append(families, v.(string))
		}
		if ids, ok := r["category_ids"].([]any); ok {
			for _, id := range ids {
				exact[id.(string)] = true
				requested[id.(string)] = true
			}
		}
	}
	registered := map[string]string{}
	for _, v := range taxonomy["items"].([]any) {
		leaf := v.(map[string]any)
		registered[leaf["id"].(string)] = leaf["reporting_domain"].(string)
	}
	for id := range requested {
		domain, ok := registered[id]
		if !ok || len(families) > 0 && !mutationFamilyMatches(families, domain) {
			return nil, nil, nil, ErrConflict
		}
		if len(exact) > 0 && !exact[id] {
			return nil, nil, nil, ErrConflict
		}
	}
	selected := func(id, domain string) bool {
		if len(exact) > 0 {
			return exact[id]
		}
		if len(families) > 0 {
			return mutationFamilyMatches(families, domain)
		}
		return len(requested) == 0 || requested[id]
	}
	entries := []any{}
	ids := map[string]bool{}
	for _, v := range taxonomy["items"].([]any) {
		leaf := v.(map[string]any)
		id := leaf["id"].(string)
		domain := leaf["reporting_domain"].(string)
		if !selected(id, domain) {
			continue
		}
		ids[id] = true
		entries = append(entries, map[string]any{"id": id, "domain": domain, "definition": leaf["definition"], "inclusion": leaf["inclusion_criteria"], "exclusion": leaf["exclusion_criteria"], "correction_requirements": []any{leaf["correction_contract"]}, "verification_requirements": []any{leaf["verification_route"]}})
	}
	if len(entries) == 0 {
		return nil, nil, nil, ErrConflict
	}
	recipes := []any{}
	producers := []any{}
	for _, v := range recipe["recipes"].([]any) {
		if ids[v.(map[string]any)["taxonomy_id"].(string)] {
			recipes = append(recipes, v)
		}
	}
	for _, v := range production["rows"].([]any) {
		if ids[v.(map[string]any)["taxonomy_id"].(string)] {
			producers = append(producers, v)
		}
	}
	rules := []any{}
	if v, ok := taxonomy["judgment_rules"].([]any); ok {
		rules = v
	}
	return map[string]any{"taxonomy_sha256": contracts.Digest(taxonomyBytes), "entries": entries, "judgment_rules": rules}, recipes, producers, nil
}

func mutationFamilyMatches(families []string, domain string) bool {
	for _, family := range families {
		if domain == family || strings.HasPrefix(domain, family+".") {
			return true
		}
	}
	return false
}
