package app

import (
	"github.com/google/uuid"
	"go.yaml.in/yaml/v3"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

func speechProfile(settings map[string]any, registry []byte) (map[string]any, error) {
	blueprint := settings["blueprint"].(map[string]any)
	id := blueprint["provider_profile_id"].(string)
	if rows, ok := settings["configuration"].(map[string]any)["speech_profiles"].([]any); ok {
		for _, v := range rows {
			p := v.(map[string]any)
			if p["id"] == id {
				return p, nil
			}
		}
	}
	var catalog map[string]any
	if e := yaml.Unmarshal(registry, &catalog); e != nil {
		return nil, e
	}
	for _, v := range catalog["profiles"].([]any) {
		p := v.(map[string]any)
		if p["id"] != id {
			continue
		}
		groups, available := p["voices"].(map[string]any)
		if !available {
			return nil, &provider.Failure{Code: "CAPABILITY_UNAVAILABLE"}
		}
		voices := []any{}
		for locale, items := range groups {
			for _, voice := range items.([]any) {
				voices = append(voices, map[string]any{"id": voice, "locale": locale, "accent_description": nil})
			}
		}
		model, _ := p["model"].(string)
		mode := "unknown"
		if p["provider"] == "local_kokoro" {
			mode = "local"
		}
		return map[string]any{"id": id, "provider": p["provider"], "adapter_version": id, "model": model, "endpoint": nil, "billing_mode": mode, "account_tier": nil, "overage_disabled": nil, "voices": voices, "capabilities": p["capabilities"], "voice_settings": map[string]any{"speed": nil}}, nil
	}
	return nil, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
}

func compileSpeechPlan(preparation string, settings, candidate, profile map[string]any) (map[string]any, error) {
	blueprint := settings["blueprint"].(map[string]any)
	speakers := map[string]map[string]any{}
	for _, value := range blueprint["speakers"].([]any) {
		sp := value.(map[string]any)
		speakers[sp["id"].(string)] = sp
	}
	locale := blueprint["variety_policy"].(map[string]any)["target_locale"]
	gap := float64(250)
	if configuration, ok := settings["configuration"].(map[string]any); ok {
		if defaults, ok := configuration["preparation_defaults"].(map[string]any); ok {
			if v, ok := defaults["gap_after_ms"].(float64); ok {
				gap = v
			}
		}
	}
	turns := []any{}
	for _, value := range candidate["utterances"].([]any) {
		u := value.(map[string]any)
		sp := speakers[u["speaker_id"].(string)]
		if sp == nil {
			return nil, ErrReference
		}
		voice := sp["voice_profile_id"]
		selectedLocale := locale
		for _, v := range profile["voices"].([]any) {
			p := v.(map[string]any)
			if p["id"] == voice {
				selectedLocale = p["locale"]
				break
			}
		}
		turns = append(turns, map[string]any{"id": u["id"], "utterance_id": u["id"], "speaker_id": u["speaker_id"], "voice_id": voice, "locale": selectedLocale, "operations": []any{map[string]any{"kind": "text", "text": u["surface_text"]}}, "gap_after_ms": gap})
	}
	if edits, ok := candidate["acoustic_edits"].([]any); ok && len(edits) > 0 {
		return nil, &provider.Failure{Code: "ACOUSTIC_RENDER_REQUIRED"}
	}
	caseID := uuid.NewSHA1(uuid.NameSpaceOID, []byte(preparation+":speech-case")).String()
	plan := map[string]any{"schema_version": "2.0.0", "id": uuid.NewSHA1(uuid.NameSpaceOID, []byte(preparation+":speech-plan")).String(), "case_version_id": caseID, "blueprint_sha256": lab.Hash(blueprint), "provider_profile_id": profile["id"], "profile_sha256": lab.Hash(profile), "required_capabilities": []any{"plain_text", "multi_turn"}, "turns": turns, "audio_format": "riff_pcm_s16le_24000_mono"}
	plan["plan_sha256"] = speechPlanHash(plan)
	return plan, nil
}

func speechProfiles(configuration map[string]any) []map[string]any {
	result := []map[string]any{}
	if rows, ok := configuration["speech_profiles"].([]any); ok {
		for _, row := range rows {
			result = append(result, row.(map[string]any))
		}
	}
	return result
}

func speechPlanHash(plan map[string]any) string {
	content := map[string]any{}
	for k, v := range plan {
		if k != "id" && k != "schema_version" && k != "plan_sha256" {
			content[k] = v
		}
	}
	return lab.Hash(content)
}
