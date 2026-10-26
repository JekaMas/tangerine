package app

import (
	"encoding/json"
	"strings"
	"tangerine.local/api/internal/provider"
)

var controlledCapabilities = []any{"plain_text", "ipa", "prosody", "timed_pause", "multi_turn", "voice_identity", "locale", "word_stress", "phrase_stress", "intonation", "speech_rate"}

func acousticRequested(b map[string]any) bool {
	if r, ok := b["exercise_request"].(map[string]any); ok {
		if r["mutation_count"] == float64(0) {
			return false
		}
		if ids, ok := r["category_ids"].([]any); ok && len(ids) > 0 {
			for _, v := range ids {
				id := v.(string)
				if strings.HasPrefix(id, "pronunciation.") || strings.HasPrefix(id, "fluency.") {
					return true
				}
			}
			return false
		}
		if families, ok := r["category_families"].([]any); ok {
			if len(families) == 0 {
				return true
			}
			for _, v := range families {
				f := v.(string)
				if strings.HasPrefix(f, "pronunciation") || f == "fluency" {
					return true
				}
			}
		}
	}
	if targets, ok := b["targets"].([]any); ok {
		for _, v := range targets {
			t := v.(map[string]any)
			if id, ok := t["taxonomy_id"].(string); ok && (strings.HasPrefix(id, "pronunciation.") || strings.HasPrefix(id, "fluency.")) {
				return true
			}
		}
	}
	return false
}

// Resolve the composite local adapter before freezing a new preparation. No
// provider changes are permitted after its settings have been saved.
func resolvedPreparationSpeechProfile(b, c map[string]any) (map[string]any, error) {
	registry, _ := generationRegistry("providers.v1.yaml")
	if b["provider_profile_id"] != "kokoro-controlled-v1" {
		return speechProfile(map[string]any{"blueprint": b, "configuration": c}, registry)
	}
	for _, p := range speechProfiles(c) {
		if p["id"] == "kokoro-controlled-v1" {
			return p, nil
		}
	}
	baseSettings := map[string]any{"blueprint": map[string]any{"provider_profile_id": "kokoro-local-en-v1"}, "configuration": c}
	base, err := speechProfile(baseSettings, registry)
	if err != nil {
		return nil, err
	}
	base["id"] = "kokoro-controlled-v1"
	base["adapter_version"] = "kokoro-controlled-v1"
	base["capabilities"] = controlledCapabilities
	base["credential_refs"] = []any{}
	base["assets"] = []any{}
	base["catalogue_asset_id"] = nil
	base["voice_description_asset_id"] = nil
	for _, k := range []string{"stability", "similarity_boost", "style", "use_speaker_boost"} {
		base["voice_settings"].(map[string]any)[k] = nil
	}
	return base, nil
}

func requireAcousticProfile(profile map[string]any) error {
	if profile["provider"] == "elevenlabs" {
		return nil // The worker admits model-specific phone operations once at plan creation.
	}
	if profile["provider"] == "local_english_accents" && profile["adapter_version"] == localAccentProfile {
		return nil
	}
	if profile["provider"] == "azure_speech" {
		caps, _ := profile["capabilities"].([]any)
		for _, v := range caps {
			if v == "plain_text" {
				return nil
			}
		}
	}
	if profile["provider"] != "local_kokoro" || profile["adapter_version"] != "kokoro-controlled-v1" {
		return &provider.Failure{Code: "CAPABILITY_UNAVAILABLE"}
	}
	return nil
}

// Only explicit acoustic requirements need an initial capability decision.
// Unrestricted generation can choose any permitted category; its saved controls
// still undergo the native compiler's single meaningful-operation admission.
func requestedAcousticCapability(b, profile map[string]any) error {
	explicit := false
	if r, ok := b["exercise_request"].(map[string]any); ok {
		if r["mutation_count"] == float64(0) {
			return nil
		}
		if families, ok := r["category_families"].([]any); ok && len(families) > 0 {
			explicit = acousticRequested(b)
		}
	}
	raw, _ := generationRegistry("acoustic-production.v1.json")
	var registry map[string]any
	if e := json.Unmarshal(raw, &registry); e != nil {
		return e
	}
	routes := map[string]string{}
	for _, v := range registry["rows"].([]any) {
		r := v.(map[string]any)
		routes[r["taxonomy_id"].(string)] = r["controller"].(string)
	}
	targets, _ := b["targets"].([]any)
	if r, ok := b["exercise_request"].(map[string]any); ok {
		if ids, ok := r["category_ids"].([]any); ok {
			for _, id := range ids {
				targets = append(targets, map[string]any{"taxonomy_id": id})
			}
		}
	}
	for _, v := range targets {
		route := routes[v.(map[string]any)["taxonomy_id"].(string)]
		if route != "" && route != "surface_text" && route != "control_variant" {
			explicit = true
			if (profile["provider"] == "azure_speech" || profile["provider"] == "elevenlabs") && (route == "vowel_duration" || route == "vot_edit") {
				return &provider.Failure{Code: "CAPABILITY_UNAVAILABLE"}
			}
		}
	}
	if explicit {
		return requireAcousticProfile(profile)
	}
	return nil
}
