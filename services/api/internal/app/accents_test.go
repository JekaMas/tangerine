package app

import (
	"encoding/json"
	"reflect"
	"testing"
)

func accentBlueprint(t *testing.T, choices []any) map[string]any {
	t.Helper()
	req := map[string]any{"topic": "Planning a train trip", "speaker_count": 2, "text_length_words": 70, "category_families": []any{"lexis"}, "speaker_voice_ids": choices}
	raw, _ := json.Marshal(map[string]any{"exercise_request": req})
	b, e := ExpandBlueprint(raw, DefaultConfiguration())
	if e != nil {
		t.Fatal(e)
	}
	return b
}
func TestAccentBlueprintPositive(t *testing.T) {
	b := accentBlueprint(t, []any{"melo_en_au", "melo_en_in"})
	ss := b["speakers"].([]any)
	if b["provider_profile_id"] != localAccentProfile {
		t.Fatal(b)
	}
	for i, expected := range []struct{ voice, accent string }{{"melo_en_au", "Australian English"}, {"melo_en_in", "Indian English"}} {
		s := ss[i].(map[string]any)
		if s["voice_profile_id"] != expected.voice || s["requested_accent"] != expected.accent {
			t.Fatal(s)
		}
	}
	if b["variety_policy"].(map[string]any)["target_locale"] != "en-US" {
		t.Fatal("speaker accent changed text variety")
	}
}
func TestAccentDefaultsNegative(t *testing.T) {
	before := DefaultConfiguration()
	raw, _ := json.Marshal(before)
	b := accentBlueprint(t, []any{nil, nil})
	if b["provider_profile_id"] == localAccentProfile || b["speakers"].([]any)[0].(map[string]any)["voice_profile_id"] != "af_heart" {
		t.Fatal(b)
	}
	after, _ := json.Marshal(DefaultConfiguration())
	if !reflect.DeepEqual(raw, after) {
		t.Fatal("global configuration changed")
	}
}
func TestAccentProfilePositive(t *testing.T) {
	b := accentBlueprint(t, []any{"melo_en_au", "melo_en_in"})
	p, e := resolvedPreparationSpeechProfile(b, DefaultConfiguration())
	if e != nil {
		t.Fatal(e)
	}
	if p["provider"] != "local_english_accents" || p["billing_mode"] != "local" || len(p["voices"].([]any)) != 6 {
		t.Fatal(p)
	}
	c := map[string]any{"utterances": []any{map[string]any{"id": "u1", "speaker_id": "s1", "surface_text": "The train leaves soon."}, map[string]any{"id": "u2", "speaker_id": "s2", "surface_text": "Let us book tickets."}}, "acoustic_edits": []any{}, "planned_units": []any{}}
	plan, e := compileSpeechPlan("p", map[string]any{"blueprint": b, "configuration": DefaultConfiguration()}, c, p)
	if e != nil {
		t.Fatal(e)
	}
	turns := plan["turns"].([]any)
	for i, locale := range []string{"en-AU", "en-IN"} {
		if turns[i].(map[string]any)["locale"] != locale {
			t.Fatal(turns)
		}
	}
	if e = requireAcousticProfile(p); e != nil {
		t.Fatal(e)
	}
}
func TestAccentUnknownNegative(t *testing.T) {
	for _, choices := range []any{[]any{"unknown", "melo_en_in"}, []any{"melo_en_au"}} {
		raw, _ := json.Marshal(map[string]any{"exercise_request": map[string]any{"topic": "Travel", "speaker_count": 2, "text_length_words": 70, "speaker_voice_ids": choices}})
		if _, e := ExpandBlueprint(raw, DefaultConfiguration()); e == nil {
			t.Fatal("unknown/count mismatch admitted", choices)
		}
	}
}
func TestAccentCheckpointPositive(t *testing.T) {
	if e := validateProjection(DocumentWrite{ID: "checkpoint", Kind: "preparation-state"}, []byte(`{"exercise_request":{"speaker_voice_ids":["melo_en_au","melo_en_in"]}}`)); e != nil {
		t.Fatal(e)
	}
}
func TestAccentFrozenProfilePositive(t *testing.T) {
	// A preparation admitted before a catalogue change keeps its saved profile.
	frozen := localAccentSpeechProfile()
	frozen["voice_settings"].(map[string]any)["speed"] = 0.9
	settings := map[string]any{"blueprint": map[string]any{"provider_profile_id": localAccentProfile}, "speech_profile": frozen}
	actual, err := speechProfile(settings, nil)
	if err != nil || !reflect.DeepEqual(actual, frozen) {
		t.Fatalf("saved profile replaced: %v, %v", actual, err)
	}
}
func TestAccentAdvancedSpeakersPositive(t *testing.T) {
	raw := []byte(`{"exercise_request":{"topic":"Travel","speaker_count":1,"text_length_words":70,"category_families":["lexis"],"speaker_voice_ids":["melo_en_au","melo_en_in"]},"speakers":[{"id":"custom","voice_profile_id":"bf_emma","learner_cefr":null,"l1":null,"requested_accent":"British English","pace_wpm":150,"pace_tolerance_fraction":0.2}]}`)
	b, err := ExpandBlueprint(raw, DefaultConfiguration())
	if err != nil {
		t.Fatal(err)
	}
	if b["provider_profile_id"] != "kokoro-local-en-v1" || b["speakers"].([]any)[0].(map[string]any)["voice_profile_id"] != "bf_emma" {
		t.Fatal("advanced speakers lost precedence", b)
	}
}
func TestAccentCheckpointNegative(t *testing.T) {
	if e := validateProjection(DocumentWrite{ID: "checkpoint", Kind: "preparation-state"}, []byte(`{"exercise_request":{"speaker_voice_ids":["melo_en_au"]},"settings_asset_id":"missing"}`)); e == nil {
		t.Fatal("real settings association lost")
	}
}
