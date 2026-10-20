package app

// Assemble the saved language data required by interpretation. No current
// settings replace an attempt's frozen configuration or prompt bundle.
import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"unicode"

	"go.yaml.in/yaml/v3"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

type InterpretationResources struct {
	Key         map[string]any  `json:"key"`
	Taxonomy    []any           `json:"taxonomy"`
	TaxonomyIDs map[string]bool `json:"taxonomy_ids"`
	Aliases     []any           `json:"aliases"`
	AliasesSHA  string          `json:"aliases_sha256"`
	Evidence    []any           `json:"evidence"`
	Rationales  []any           `json:"rationales"`
}

func (s *Storage) interpretationResources(ctx context.Context, record AttemptRecord) (InterpretationResources, error) {
	out := InterpretationResources{Taxonomy: []any{}, TaxonomyIDs: map[string]bool{}, Aliases: []any{}, Evidence: []any{}, Rationales: []any{}}
	d, e := s.ReadDocument(ctx, record.Attempt["case_version_id"].(string))
	if e != nil {
		return out, e
	}
	var original map[string]any
	if e = json.Unmarshal(d.Payload, &original); e != nil {
		return out, e
	}
	out.Key = map[string]any{}
	for _, k := range []string{"schema_version", "case_version_id", "taxonomy_version", "public_context", "variety_policy", "audio", "speakers", "utterances", "units", "verification_policy_version", "case_sha256"} {
		out.Key[k] = original[k]
	}
	// Provider receipt IDs are not linguistic observations. The recorded authored
	// mutations remain the key; no reference corpus or new acoustic review is needed.
	for _, v := range out.Key["units"].([]any) {
		v.(map[string]any)["evidence_ids"] = []any{}
	}
	// Accepted linguistic/acoustic observations keep their actual subjects and
	// modality. Render/provider receipts are not converted into heard phones.
	rows, e := s.DB.Query(ctx, "SELECT payload FROM document WHERE kind='evidence' AND payload->>'case_version_id'=$1 ORDER BY id", record.Attempt["case_version_id"])
	if e != nil {
		return out, e
	}
	for rows.Next() {
		var payload []byte
		if e = rows.Scan(&payload); e != nil {
			rows.Close()
			return out, e
		}
		var observation map[string]any
		if e = json.Unmarshal(payload, &observation); e != nil {
			rows.Close()
			return out, e
		}
		out.Evidence = append(out.Evidence, observation)
	}
	e = rows.Err()
	rows.Close()
	if e != nil {
		return out, e
	}
	raw, e := generationRegistry("error-taxonomy.v1.yaml")
	if e != nil {
		return out, e
	}
	var taxonomy struct {
		Items []map[string]any `yaml:"items"`
	}
	if e = yaml.Unmarshal(raw, &taxonomy); e != nil {
		return out, e
	}
	for _, item := range taxonomy.Items {
		context := map[string]any{}
		for _, k := range []string{"id", "label", "definition", "reporting_domain", "inclusion_criteria", "exclusion_criteria"} {
			context[k] = item[k]
		}
		out.Taxonomy = append(out.Taxonomy, context)
		out.TaxonomyIDs[item["id"].(string)] = true
	}
	raw, e = generationRegistry("category-aliases.v1.yaml")
	if e != nil {
		return out, e
	}
	out.AliasesSHA = contracts.Digest(raw)
	var aliases struct {
		Entries []struct {
			ID      string   `yaml:"target_id"`
			English []string `yaml:"english"`
			Russian []string `yaml:"russian"`
		} `yaml:"entries"`
	}
	if e = yaml.Unmarshal(raw, &aliases); e != nil {
		return out, e
	}
	for _, entry := range aliases.Entries {
		// Preserve authored ancestor aliases supported by the actual taxonomy tree.
		valid := out.TaxonomyIDs[entry.ID]
		for leaf := range out.TaxonomyIDs {
			valid = valid || strings.HasPrefix(leaf, entry.ID+".")
		}
		if !valid {
			continue
		}
		out.TaxonomyIDs[entry.ID] = true
		for _, locale := range []string{"en", "ru"} {
			names := entry.English
			if locale == "ru" {
				names = entry.Russian
			}
			names = append(append([]string{}, names...), entry.ID)
			for _, name := range names {
				out.Aliases = append(out.Aliases, map[string]any{"normalized_alias": strings.ToLower(strings.Join(strings.Fields(name), " ")), "language": locale, "target_ids": []any{entry.ID}})
			}
		}
	}
	return out, nil
}
func interpretationProfile(record AttemptRecord, stage string) (provider.Profile, error) {
	for _, v := range record.Context["evaluator_bindings"].([]any) {
		binding := v.(map[string]any)
		if binding["stage"] == stage {
			raw, _ := json.Marshal(binding["profile"])
			var p provider.Profile
			e := json.Unmarshal(raw, &p)
			return p, e
		}
	}
	return provider.Profile{}, ErrReference
}
func interpretationBundle(record AttemptRecord) lab.Bundle {
	raw, _ := json.Marshal(record.Context["prompt_bundle"])
	var b lab.Bundle
	_ = json.Unmarshal(raw, &b)
	return b
}
func interpretationInput(record AttemptRecord, r InterpretationResources, c *CanonicalExtraction) (map[string]any, map[string]any) {
	a := record.Attempt
	input := map[string]any{"schema_version": "2.0.0", "answer_text": a["answer_text"], "answer_sha256": a["answer_utf8_sha256"]}
	parts := map[string]any{"answer": a["answer_text"], "taxonomy": r.Taxonomy, "public_context": r.Key["public_context"]}
	if c == nil {
		// Blind extraction locates source wording; definitions/rubrics are mapper context.
		compact := []any{}
		for _, v := range r.Taxonomy {
			row := v.(map[string]any)
			compact = append(compact, map[string]any{"id": row["id"], "label": row["label"]})
		}
		parts["taxonomy"] = compact
		input["source_tokens"] = sourceAnswerContext(a["answer_text"].(string))["source_tokens"]
		input["task_components"] = a["task_components"]
		input["requested_language"] = record.Context["requested_language"]
	} else {
		raw, _ := json.Marshal(c.Extraction)
		var extraction map[string]any
		_ = json.Unmarshal(raw, &extraction)
		input["extraction"] = extraction
		listener := []any{}
		for _, claim := range c.Claims {
			corrections, explanations := []string{}, []string{}
			for _, span := range claim.Corrections {
				corrections = append(corrections, span.Text)
			}
			for _, span := range claim.Explanations {
				explanations = append(explanations, span.Text)
			}
			listener = append(listener, map[string]any{"claim_id": claim.ID, "correction_quotes": corrections, "explanation_quotes": explanations})
		}
		input["listener_components"] = listener
		input["ground_truth"] = r.Key
		input["alias_registry_sha256"] = r.AliasesSHA
		aliases := []any{}
		russian := record.Context["requested_language"] == "ru" || strings.ContainsFunc(a["answer_text"].(string), func(c rune) bool { return unicode.In(c, unicode.Cyrillic) })
		for _, v := range r.Aliases {
			row := v.(map[string]any)
			if row["language"] == "en" || russian {
				aliases = append(aliases, row)
			}
		}
		input["alias_entries"] = aliases
		input["evidence"] = r.Evidence
		input["rationales"] = r.Rationales
		parts["taxonomy"] = mappingTaxonomyContext(r, a["answer_text"].(string))
		parts["public_context"] = r.Key["public_context"]
		parts["mutation_key"] = r.Key
		parts["evidence"] = r.Evidence
		parts["extraction"] = map[string]any{"claims": c.Claims, "conflicts": c.Conflicts, "coverage": c.Extraction.Coverage, "relations": c.Extraction.Relations, "identity": "Use claims[].id as output claim_id; claim local_ref is extraction-local. unit_id can use an exact frozen unit ID or one of the explicitly listed target_references, which is resolved to its canonical unit ID before saving.", "target_references": mappingTargetReferences(r.Key)}
	}
	return input, parts
}

// Source coordinate hints contain only the answer itself. They help an LLM
// reference repeated wording without guessing offsets or seeing the hidden key.
func sourceAnswerContext(answer string) map[string]any {
	runes := []rune(answer)
	tokens := []AnswerSpan{}
	for i := 0; i < len(runes); {
		if unicode.IsSpace(runes[i]) {
			i++
			continue
		}
		start := i
		for i < len(runes) && !unicode.IsSpace(runes[i]) {
			i++
		}
		tokens = append(tokens, AnswerSpan{start, i, string(runes[start:i])})
	}
	return map[string]any{"original_text": answer, "source_tokens": tokens, "coordinate_unit": "Unicode codepoints; half-open, punctuation retained"}
}

func mappingTaxonomyContext(r InterpretationResources, answer string) []any {
	needed := map[string]bool{}
	for _, v := range r.Key["units"].([]any) {
		unit := v.(map[string]any)
		if id, ok := unit["primary_taxonomy_id"].(string); ok {
			needed[id] = true
		}
		if ids, ok := unit["accepted_taxonomy_ids"].([]any); ok {
			for _, id := range ids {
				needed[id.(string)] = true
			}
		}
	}
	normalized := strings.ToLower(strings.Join(strings.Fields(answer), " "))
	for _, v := range r.Aliases {
		row := v.(map[string]any)
		alias := row["normalized_alias"].(string)
		if strings.Contains(normalized, alias) {
			for _, id := range row["target_ids"].([]any) {
				needed[id.(string)] = true
			}
		}
	}
	out := []any{}
	for _, v := range r.Taxonomy {
		row := v.(map[string]any)
		if needed[row["id"].(string)] {
			out = append(out, row)
		} else {
			out = append(out, map[string]any{"id": row["id"], "label": row["label"]})
		}
	}
	return out
}

func mappingTargetHint(key map[string]any, claim CanonicalClaim) string {
	raw, _ := json.Marshal(map[string]any{"actual_frozen_units": key["units"], "target_references": mappingTargetReferences(key), "original_claim": claim})
	return "Use these exact unit/option/proposition IDs and this source wording: " + string(raw) + ". Detection follows the source stance and target truth; judge the proposed repair and optional reason separately. Every supplied explanation needs its own source-quoted supported/unsupported/unknown assertion and contextual reason, including rubric-covered assertions; record its actually satisfied rationale IDs as well."
}

// Short references are explicit per-call data, never guesses for unknown IDs.
type MappingTargetReference struct {
	LocalRef string `json:"local_ref"`
	Unit     string `json:"unit_id"`
}

func mappingTargetReferences(key map[string]any) []MappingTargetReference {
	rows := key["units"].([]any)
	occupied := map[string]bool{}
	for _, value := range rows {
		occupied[value.(map[string]any)["id"].(string)] = true
	}
	refs := []MappingTargetReference{}
	next := 1
	for _, value := range rows {
		for occupied[fmt.Sprintf("u%d", next)] {
			next++
		}
		ref := fmt.Sprintf("u%d", next)
		refs = append(refs, MappingTargetReference{ref, value.(map[string]any)["id"].(string)})
		occupied[ref] = true
		next++
	}
	return refs
}
