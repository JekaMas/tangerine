package app

import (
	"embed"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"go.yaml.in/yaml/v3"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
)

// Frozen registries are packaged byte-for-byte from the active specification.
//
//go:embed generationdata/*
var generationData embed.FS

func generationRegistry(name string) ([]byte, error) {
	return generationData.ReadFile("generationdata/" + name)
}

// ExpandBlueprint retains advanced controls and the verbatim simple request.
// Approximate length and requested CEFR are preferences, never hidden gates.
func ExpandBlueprint(raw []byte, configuration map[string]any) (map[string]any, error) {
	_, raw, e := contracts.Validate("blueprint-write", "2.0.0", raw)
	if e != nil {
		return nil, e
	}
	return expandBlueprint(raw, configuration)
}

func expandBlueprint(raw []byte, configuration map[string]any) (map[string]any, error) {
	var e error
	var input map[string]any
	_ = json.Unmarshal(raw, &input)
	var defaults map[string]any
	registry, _ := generationRegistry("configuration-registry.yaml")
	if e = yaml.Unmarshal(registry, &defaults); e != nil {
		return nil, e
	}
	prep := defaults["simple_preparation"].(map[string]any)
	if v, ok := configuration["preparation_defaults"].(map[string]any); ok {
		for k, x := range v {
			prep[k] = x
		}
	}
	if req, ok := input["exercise_request"].(map[string]any); ok {
		for _, k := range []string{"english_level", "mutation_count", "mutation_seed", "audio_backend"} {
			if _, ok := req[k]; !ok {
				req[k] = nil
			}
		}
		if _, ok := req["category_families"]; !ok {
			req["category_families"] = []any{}
		}
		count := req["speaker_count"].(float64)
		n := int(count)
		speech := "kokoro-local-en-v1"
		if v, ok := configuration["speech_profile"].(string); ok {
			speech = v
		}
		if req["audio_backend"] == "local" {
			speech = "kokoro-local-en-v1"
		}
		if req["audio_backend"] == "service" {
			speech = "azure-standard-en-v1"
		}
		if v, ok := input["provider_profile_id"].(string); ok {
			if req["audio_backend"] != nil && v != speech {
				return nil, ErrConflict
			}
			speech = v
		}
		variety := prep["variety_policy"]
		if v, ok := input["variety_policy"]; ok {
			variety = v
		}
		locale := variety.(map[string]any)["target_locale"].(string)
		providerBytes, _ := generationRegistry("providers.v1.yaml")
		var providers map[string]any
		if e = yaml.Unmarshal(providerBytes, &providers); e != nil {
			return nil, e
		}
		voices := []any{}
		for _, entry := range providers["profiles"].([]any) {
			p := entry.(map[string]any)
			if p["id"] == speech {
				if vs, ok := p["voices"].(map[string]any); ok {
					voices, _ = vs[locale].([]any)
				}
			}
		}
		if len(voices) == 0 {
			return nil, fmt.Errorf("speech profile has no voices for %s", locale)
		}
		speakers := []any{}
		for i := 0; i < n; i++ {
			speakers = append(speakers, map[string]any{"id": fmt.Sprintf("s%d", i+1), "voice_profile_id": voices[i%len(voices)], "learner_cefr": req["english_level"], "l1": nil, "requested_accent": nil, "pace_wpm": prep["pace_wpm"], "pace_tolerance_fraction": prep["pace_tolerance_fraction"]})
		}
		format := "monologue"
		if n > 1 {
			format = "dialogue"
		}
		expanded := map[string]any{"format": format, "public_context": req["topic"].(string) + "\nIdentify mistakes and offer corrections. " + variety.(map[string]any)["public_constraints"].(string), "variety_policy": variety, "duration_ms_min": nil, "duration_ms_max": nil, "speakers": speakers, "targets": []any{}, "task_components": prep["task_components"], "audio_origin_policy": "synthetic_only", "provider_profile_id": speech}
		for k, v := range expanded {
			if _, ok := input[k]; !ok {
				input[k] = v
			}
		}
		if len(input["speakers"].([]any)) != n {
			return nil, ErrConflict
		}
	}
	input["schema_version"] = "2.0.0"
	input["id"] = uuid.NewString()
	b := input
	speakers := b["speakers"].([]any)
	seen := map[string]bool{}
	for _, v := range speakers {
		id := v.(map[string]any)["id"].(string)
		if seen[id] {
			return nil, ErrConflict
		}
		seen[id] = true
	}
	return b, nil
}

// ValidateCanonical checks the independently knowable clean-text invariants.
// Linguistic correctness/coherence require actual model quality observations.
func ValidateCanonical(raw []byte, blueprint map[string]any) (map[string]any, int, error) {
	registry, e := contracts.Registry()
	if e != nil {
		return nil, 0, e
	}
	_, raw, e = contracts.Validate("case-candidate", registry["case-candidate"].Version, raw)
	if e != nil {
		return nil, 0, e
	}
	return canonicalContent(raw, blueprint)
}

// canonicalContent is the semantic part of the single provider acceptance step.
// Its input was already projected and schema-checked by the shared adapter.
func canonicalContent(raw []byte, blueprint map[string]any) (map[string]any, int, error) {
	var c map[string]any
	if e := json.Unmarshal(raw, &c); e != nil {
		return nil, 0, e
	}
	if c["blueprint_id"] != blueprint["id"] || c["status"] != "candidate" || c["failure_reason"] != nil || len(c["planned_units"].([]any)) != 0 {
		return nil, 0, ErrConflict
	}
	if ops, ok := c["acoustic_edits"].([]any); ok && len(ops) != 0 {
		return nil, 0, ErrConflict
	}
	expected := map[string]bool{}
	for _, s := range blueprint["speakers"].([]any) {
		expected[s.(map[string]any)["id"].(string)] = false
	}
	ids := map[string]bool{}
	words := 0
	for _, u := range c["utterances"].([]any) {
		v := u.(map[string]any)
		id := v["id"].(string)
		speaker := v["speaker_id"].(string)
		text := v["canonical_text"].(string)
		if _, ok := expected[speaker]; !ok {
			return nil, 0, ErrConflict
		}
		if ids[id] || strings.TrimSpace(text) == "" || text != v["surface_text"] {
			return nil, 0, ErrConflict
		}
		ids[id] = true
		expected[speaker] = true
		words += len(strings.Fields(text))
	}
	for _, present := range expected {
		if !present {
			return nil, 0, ErrConflict
		}
	}
	return c, words, nil
}

func preparationBindings(c map[string]any, b lab.Bundle) ([]any, error) {
	p, e := FreezeProfile(c, "case_generation")
	if e != nil {
		return nil, e
	}
	bindings := []any{}
	for _, phase := range []string{"canonical_text", "mutation"} {
		found := false
		for _, v := range b.Bindings {
			if v.Stage != "case_generation" || v.Phase == nil || *v.Phase != phase {
				continue
			}
			found = true
			raw, _ := json.Marshal(p)
			var effective map[string]any
			_ = json.Unmarshal(raw, &effective)
			delete(effective, "roles")
			delete(effective, "id")
			effective["schema_version"] = "2.0.0"
			effective["stage"] = "case_generation"
			effective["phase"] = phase
			effective["prompt_id"] = v.PromptID
			effective["prompt_sha256"] = v.PromptSHA
			effective["input_schema_sha256"] = v.InputSHA
			effective["output_schema_sha256"] = v.OutputSHA
			effective["wire_schema_sha256"] = v.OutputSHA
			effective["timeout_seconds"] = int(stageTimeout("case_generation", &phase).Seconds())
			effective["prompt_bundle_sha256"] = b.SHA
			effective["context_policy_sha256"] = v.PolicySHA
			effective["binding_sha256"] = lab.Hash(effective)
			effective["id"] = uuid.NewString()
			bindings = append(bindings, effective)
		}
		if !found {
			return nil, ErrReference
		}
	}
	return bindings, nil
}
