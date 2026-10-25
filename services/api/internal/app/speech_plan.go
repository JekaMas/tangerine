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
	if frozen, ok := settings["speech_profile"].(map[string]any); ok && frozen["id"] == id {
		return frozen, nil
	}
	if id == localAccentProfile {
		return localAccentSpeechProfile(), nil
	}
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
	byTurn := map[string][]any{}
	edits, _ := candidate["acoustic_edits"].([]any)
	if len(edits) > 0 {
		if e := requireAcousticProfile(profile); e != nil {
			return nil, e
		}
		units := map[string]string{}
		for _, v := range candidate["planned_units"].([]any) {
			u := v.(map[string]any)
			units[u["id"].(string)] = u["primary_taxonomy_id"].(string)
		}
		for _, v := range edits {
			original := v.(map[string]any)
			edit := map[string]any{}
			for k, x := range original {
				edit[k] = x
			}
			edit["taxonomy_id"] = units[edit["unit_id"].(string)]
			id := edit["utterance_id"].(string)
			byTurn[id] = append(byTurn[id], edit)
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
		turn := map[string]any{"id": u["id"], "utterance_id": u["id"], "speaker_id": u["speaker_id"], "voice_id": voice, "locale": selectedLocale, "operations": []any{map[string]any{"kind": "text", "text": u["surface_text"]}}, "gap_after_ms": gap}
		if ops := byTurn[u["id"].(string)]; len(ops) > 0 {
			turn["acoustic_edits"] = ops
			turn["target_wpm"] = sp["pace_wpm"]
		}
		turns = append(turns, turn)
	}

	required := []any{"plain_text", "multi_turn"}
	needed := map[string]bool{}
	for _, value := range edits {
		edit := value.(map[string]any)
		switch edit["controller"] {
		case "phone_pair":
			needed["ipa"] = true
		case "pause_insert":
			needed["timed_pause"] = true
		default:
			needed["prosody"] = true
		}
	}
	for _, capability := range []string{"ipa", "prosody", "timed_pause"} {
		if needed[capability] {
			required = append(required, capability)
		}
	}
	caseID := uuid.NewSHA1(uuid.NameSpaceOID, []byte(preparation+":speech-case")).String()
	plan := map[string]any{"schema_version": "2.0.0", "id": uuid.NewSHA1(uuid.NameSpaceOID, []byte(preparation+":speech-plan")).String(), "case_version_id": caseID, "blueprint_sha256": lab.Hash(blueprint), "provider_profile_id": profile["id"], "profile_sha256": lab.Hash(profile), "required_capabilities": required, "turns": turns, "audio_format": "riff_pcm_s16le_24000_mono"}
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
		if k != "id" && k != "schema_version" && k != "plan_sha256" && k != "production_plan_asset_id" {
			content[k] = v
		}
	}
	return lab.Hash(content)
}
