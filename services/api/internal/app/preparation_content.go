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
	"tangerine.local/api/internal/provider"
	"time"
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
		if e := admitRecurringRequest(req, n); e != nil {
			return nil, e
		}
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
		_, advancedSpeakers := input["speakers"]
		var choiceIDs []any
		useLocal := false
		if !advancedSpeakers {
			var choiceErr error
			choiceIDs, useLocal, choiceErr = requestedLocalVoices(req, n)
			if choiceErr != nil {
				return nil, choiceErr
			}
		}
		if useLocal && !advancedSpeakers {
			if explicit, ok := input["provider_profile_id"]; ok && explicit != localAccentProfile {
				return nil, ErrConflict
			}
			if req["audio_backend"] == "service" {
				return nil, ErrConflict
			}
			speech = localAccentProfile
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
		lookupSpeech := speech
		if speech == "kokoro-controlled-v1" {
			lookupSpeech = "kokoro-local-en-v1"
		}
		for _, entry := range providers["profiles"].([]any) {
			p := entry.(map[string]any)
			if p["id"] == lookupSpeech {
				if vs, ok := p["voices"].(map[string]any); ok {
					voices, _ = vs[locale].([]any)
				}
			}
		}
		for _, entry := range speechProfiles(configuration) {
			if entry["id"] == speech {
				voices = []any{}
				for _, v := range entry["voices"].([]any) {
					voice := v.(map[string]any)
					if voice["locale"] == locale {
						voices = append(voices, voice["id"])
					}
				}
			}
		}
		if speech == localAccentProfile {
			voices = []any{"af_heart", "am_adam"}
		}
		speakers, explicit := input["speakers"].([]any)
		if !explicit {
			if len(voices) == 0 {
				return nil, fmt.Errorf("speech profile has no voices for %s", locale)
			}
			speakers = []any{}
			for i := 0; i < n; i++ {
				voiceID := voices[i%len(voices)]
				var accent any
				if useLocal {
					if choiceIDs[i] != nil {
						voiceID = choiceIDs[i]
					}
					selected, _ := findLocalVoice(voiceID.(string))
					accent = selected.AccentLabel
				}
				speakers = append(speakers, map[string]any{"id": fmt.Sprintf("s%d", i+1), "voice_profile_id": voiceID, "learner_cefr": req["english_level"], "l1": nil, "requested_accent": accent, "pace_wpm": prep["pace_wpm"], "pace_tolerance_fraction": prep["pace_tolerance_fraction"]})
			}
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
	if acousticRequested(input) && input["provider_profile_id"] == "kokoro-local-en-v1" {
		_, explicit := input["exercise_request"]
		var original map[string]any
		_ = json.Unmarshal(raw, &original)
		if explicit && original["provider_profile_id"] == nil {
			input["provider_profile_id"] = "kokoro-controlled-v1"
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
		return nil, 0, &provider.OutputValidationError{Detail: "Preserve the saved blueprint_id, candidate status and null failure_reason. This is canonical_text: planned_units must be empty; targets describe the later mutation phase."}
	}
	if ops, ok := c["acoustic_edits"].([]any); ok && len(ops) != 0 {
		return nil, 0, &provider.OutputValidationError{Detail: "This clean canonical_text phase requires acoustic_edits empty; acoustic mutations belong to the next phase."}
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
			return nil, 0, &provider.OutputValidationError{Detail: "Use only the expanded blueprint speakers and retain their exact speaker_id values."}
		}
		if ids[id] || strings.TrimSpace(text) == "" || text != v["surface_text"] {
			return nil, 0, &provider.OutputValidationError{Detail: "Keep unique turn IDs, nonempty canonical_text and surface_text exactly equal to canonical_text in this clean phase."}
		}
		ids[id] = true
		expected[speaker] = true
		words += len(strings.Fields(text))
	}
	for _, present := range expected {
		if !present {
			return nil, 0, &provider.OutputValidationError{Detail: "Give every requested blueprint speaker at least one clean utterance."}
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
			wireSchema, err := contracts.WireSchema(strings.TrimSuffix(v.OutputSchema, ".schema.json"))
			if err != nil {
				return nil, err
			}
			effective["wire_schema_sha256"] = contracts.Digest(wireSchema)
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

// Preparation bindings were admitted and saved at creation. Reuse their phase
// budget, including an earlier deployment's policy, without revalidating assets.
func preparationTimeout(settings map[string]any, phase string) time.Duration {
	for _, item := range settings["generation_bindings"].([]any) {
		binding := item.(map[string]any)
		if binding["phase"] == phase {
			switch seconds := binding["timeout_seconds"].(type) {
			case int:
				return time.Duration(seconds) * time.Second
			case float64:
				return time.Duration(seconds) * time.Second
			}
		}
	}
	return 0
}
