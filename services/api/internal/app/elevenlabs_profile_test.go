package app

import (
	"tangerine.local/api/internal/provider"
	"testing"
)

func TestElevenLabsAcousticBindingPositive(t *testing.T) {
	profile := map[string]any{"provider": "elevenlabs", "model": "eleven_flash_v2", "capabilities": []any{"plain_text", "ipa"}}
	b := map[string]any{"exercise_request": map[string]any{"category_ids": []any{"pronunciation.segmental.consonant_substitution"}}}
	if e := requestedAcousticCapability(b, profile); e != nil {
		t.Fatal("explicit dictionary binding rejected", e)
	}
	settings, candidate, _ := speechFixture(t)
	_, _, candidate, _ = acousticMutationFixture()
	profile["id"] = "selected-elevenlabs"
	profile["voices"] = []any{map[string]any{"id": "af_heart", "locale": "en-US"}}
	plan, e := compileSpeechPlan("i22", settings, candidate, profile)
	if e != nil || plan["provider_profile_id"] != "selected-elevenlabs" {
		t.Fatal("binding silently switched", e, plan)
	}
}
func TestElevenLabsUnsupportedTimingNegative(t *testing.T) {
	profile := map[string]any{"provider": "elevenlabs", "model": "eleven_flash_v2", "capabilities": []any{"plain_text", "ipa"}}
	for _, id := range []string{"pronunciation.segmental.vowel_length", "pronunciation.segmental.consonant_aspiration"} {
		b := map[string]any{"exercise_request": map[string]any{"category_ids": []any{id}}}
		if requestedAcousticCapability(b, profile) == nil {
			t.Fatal("native phone timing was falsely promised", id)
		}
	}
}

func TestElevenLabsPublicFailuresNegative(t *testing.T) {
	for native, want := range map[string]string{"PROVIDER_FAILED": "PROVIDER_FAILURE", "PROVIDER_QUOTA": "LOCAL_BUDGET_EXCEEDED", "CAPABILITY_UNAVAILABLE": "CAPABILITY_UNQUALIFIED"} {
		got, _ := speechPublicFailure(&provider.Failure{Code: native})
		if got != want {
			t.Fatal("native error changed its public mapping", native, got, want)
		}
	}
}
