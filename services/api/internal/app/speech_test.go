package app

import (
	"encoding/binary"
	"encoding/json"
	"strings"
	"testing"
)

func explicitSpeechInput(n int, speakers []any) ([]byte, map[string]any) {
	c := DefaultConfiguration()
	c["speech_profile"] = "british-only"
	c["speech_profiles"] = []any{map[string]any{"id": "british-only", "voices": []any{map[string]any{"id": "bf_emma", "locale": "en-GB"}}}}
	input := map[string]any{"exercise_request": map[string]any{"topic": "A café visit", "speaker_count": n, "text_length_words": 50}}
	if speakers != nil {
		input["speakers"] = speakers
	}
	raw, _ := json.Marshal(input)
	return raw, c
}
func explicitSpeechSpeaker(id, voice string) map[string]any {
	return map[string]any{"id": id, "voice_profile_id": voice, "learner_cefr": "B1", "l1": nil, "requested_accent": "British English", "pace_wpm": 150, "pace_tolerance_fraction": .1}
}
func TestSpeechExplicitLocalePositive(t *testing.T) {
	raw, c := explicitSpeechInput(1, []any{explicitSpeechSpeaker("s1", "bf_emma")})
	b, err := ExpandBlueprint(raw, c)
	if err != nil {
		t.Fatal(err)
	}
	if b["variety_policy"].(map[string]any)["target_locale"] != "en-US" || b["speakers"].([]any)[0].(map[string]any)["voice_profile_id"] != "bf_emma" {
		t.Fatal("explicit accent changed the assessment variety", b)
	}
}
func TestSpeechExplicitVoiceSetPositive(t *testing.T) {
	raw, c := explicitSpeechInput(2, []any{explicitSpeechSpeaker("s1", "bf_emma"), explicitSpeechSpeaker("s2", "bm_george")})
	c["speech_profiles"].([]any)[0].(map[string]any)["voices"] = []any{map[string]any{"id": "bf_emma", "locale": "en-GB"}, map[string]any{"id": "bm_george", "locale": "en-GB"}}
	b, err := ExpandBlueprint(raw, c)
	if err != nil {
		t.Fatal(err)
	}
	speakers := b["speakers"].([]any)
	if speakers[0].(map[string]any)["voice_profile_id"] != "bf_emma" || speakers[1].(map[string]any)["voice_profile_id"] != "bm_george" {
		t.Fatal(b)
	}
}
func TestSpeechExplicitCountNegative(t *testing.T) {
	raw, c := explicitSpeechInput(2, []any{explicitSpeechSpeaker("s1", "bf_emma")})
	if _, err := ExpandBlueprint(raw, c); err == nil {
		t.Fatal("wrong explicit speaker count admitted")
	}
}
func TestSpeechMissingDefaultLocaleNegative(t *testing.T) {
	raw, c := explicitSpeechInput(1, nil)
	if _, err := ExpandBlueprint(raw, c); err == nil {
		t.Fatal("missing default voice silently substituted")
	}
}

func speechFixture(t *testing.T) (map[string]any, map[string]any, map[string]any) {
	t.Helper()
	blueprint, _, candidate, _ := mutationFixture()
	profile := map[string]any{"id": "kokoro-local-en-v1", "provider": "local_kokoro", "voices": []any{map[string]any{"id": "af_heart", "locale": "en-US"}}, "billing_mode": "local"}
	blueprint["provider_profile_id"] = "kokoro-local-en-v1"
	blueprint["speakers"] = []any{map[string]any{"id": "s1", "voice_profile_id": "af_heart"}}
	blueprint["variety_policy"] = map[string]any{"target_locale": "en-US"}
	return map[string]any{"blueprint": blueprint}, candidate, profile
}
func TestSpeechPlanPositive(t *testing.T) {
	s, c, p := speechFixture(t)
	plan, e := compileSpeechPlan("p1", s, c, p)
	if e != nil {
		t.Fatal(e)
	}
	turn := plan["turns"].([]any)[0].(map[string]any)
	if turn["operations"].([]any)[0].(map[string]any)["text"] != "The café open tomorrow." || turn["voice_id"] != "af_heart" || turn["gap_after_ms"] != float64(250) {
		t.Fatal(turn)
	}
}
func TestSpeechPlanStablePositive(t *testing.T) {
	s, c, p := speechFixture(t)
	s["blueprint"].(map[string]any)["speakers"] = append(s["blueprint"].(map[string]any)["speakers"].([]any), map[string]any{"id": "s2", "voice_profile_id": "bf_emma"})
	p["voices"] = append(p["voices"].([]any), map[string]any{"id": "bf_emma", "locale": "en-GB"})
	c["utterances"] = append(c["utterances"].([]any), map[string]any{"id": "u2", "speaker_id": "s2", "surface_text": "The station is nearby."}, map[string]any{"id": "u3", "speaker_id": "s1", "surface_text": "Thank you."})
	a, e := compileSpeechPlan("p1", s, c, p)
	if e != nil {
		t.Fatal(e)
	}
	turns := a["turns"].([]any)
	for i, expected := range []struct{ speaker, voice, locale, text string }{{"s1", "af_heart", "en-US", "The café open tomorrow."}, {"s2", "bf_emma", "en-GB", "The station is nearby."}, {"s1", "af_heart", "en-US", "Thank you."}} {
		turn := turns[i].(map[string]any)
		if turn["speaker_id"] != expected.speaker || turn["voice_id"] != expected.voice || turn["locale"] != expected.locale || turn["operations"].([]any)[0].(map[string]any)["text"] != expected.text {
			t.Fatal("dialogue voice/text/order changed", turn)
		}
	}
	b, _ := compileSpeechPlan("p1", s, c, p)
	if a["plan_sha256"] != b["plan_sha256"] || a["case_version_id"] != b["case_version_id"] {
		t.Fatal(a, b)
	}
}
func TestSpeechPlanSpeakerNegative(t *testing.T) {
	s, c, p := speechFixture(t)
	c["utterances"].([]any)[0].(map[string]any)["speaker_id"] = "missing"
	if _, e := compileSpeechPlan("p1", s, c, p); e == nil {
		t.Fatal("unknown speaker accepted")
	}
}
func TestSpeechPlanAcousticNegative(t *testing.T) {
	s, c, p := speechFixture(t)
	c["acoustic_edits"] = []any{map[string]any{"unit_id": "u1"}}
	if _, e := compileSpeechPlan("p1", s, c, p); e == nil {
		t.Fatal("unrendered acoustic intent claimed ready")
	}
}
func TestSpeechWAVPositive(t *testing.T) {
	pcm := []byte{1, 0, 255, 127, 0, 128}
	out := speechWAV(pcm)
	if string(out[:4]) != "RIFF" || binary.LittleEndian.Uint32(out[4:]) != 42 || binary.LittleEndian.Uint32(out[40:]) != 6 || binary.LittleEndian.Uint32(out[24:]) != 24000 {
		t.Fatal(out)
	}
}
func TestSpeechWAVSamplesPositive(t *testing.T) {
	pcm := []byte{7, 0, 0, 0, 8, 0}
	out := speechWAV(pcm)
	if string(out[44:]) != string(pcm) || binary.LittleEndian.Uint16(out[22:]) != 1 || binary.LittleEndian.Uint16(out[34:]) != 16 {
		t.Fatal(out)
	}
}
func TestSpeechProfileUnknownNegative(t *testing.T) {
	s, _, _ := speechFixture(t)
	s["configuration"] = map[string]any{}
	s["blueprint"].(map[string]any)["provider_profile_id"] = "missing"
	if _, e := speechProfile(s, []byte("profiles: []")); e == nil {
		t.Fatal("unconfigured profile accepted")
	}
}
func TestSpeechProfileMalformedNegative(t *testing.T) {
	s, _, _ := speechFixture(t)
	s["configuration"] = map[string]any{}
	if _, e := speechProfile(s, []byte("profiles: [")); e == nil {
		t.Fatal("malformed registry accepted")
	}
}
func TestSpeechProfileLocalPositive(t *testing.T) {
	s, _, _ := speechFixture(t)
	s["configuration"] = map[string]any{}
	raw, e := generationRegistry("providers.v1.yaml")
	if e != nil {
		t.Fatal(e)
	}
	p, e := speechProfile(s, raw)
	if e != nil || p["billing_mode"] != "local" || len(p["voices"].([]any)) != 4 {
		t.Fatal(p, e)
	}
}
func TestSpeechProfileExtensionPositive(t *testing.T) {
	s, _, p := speechFixture(t)
	p["id"] = "selected"
	s["blueprint"].(map[string]any)["provider_profile_id"] = "selected"
	s["configuration"] = map[string]any{"speech_profiles": []any{p}}
	got, e := speechProfile(s, nil)
	if e != nil || got["id"] != "selected" {
		t.Fatal(got, e)
	}
}
func TestSpeechSummaryKeyNegative(t *testing.T) {
	p := map[string]any{"id": "p1", "phase_states": map[string]any{"render": "complete"}, "mutation_manifest_asset_id": "private-key", "mutated_asset_id": "private-text"}
	summary := speechSummary(p)
	for k := range summary {
		if strings.Contains(k, "key") || strings.Contains(k, "mutat") {
			t.Fatal(summary)
		}
	}
}
func TestSpeechSummaryIncompleteNegative(t *testing.T) {
	p := map[string]any{"id": "p1", "phase_states": map[string]any{"render": "failed"}, "audio_asset_id": "partial"}
	if speechSummary(p)["audio_available"] != false {
		t.Fatal("partial audio exposed")
	}
}

func speechKeyFixture(t *testing.T) (map[string]any, map[string]any, map[string]any, map[string]any) {
	s, c, _ := speechFixture(t)
	s["configuration"] = map[string]any{"intended_uses": []any{"derivative_exercises"}}
	s["blueprint"].(map[string]any)["public_context"] = "Café opening"
	f := map[string]any{"plan": map[string]any{"case_version_id": "case1"}, "pieces": []any{map[string]any{"gap_after_ms": float64(250)}}}
	progress := map[string]any{"pieces": []any{map[string]any{"utterance_id": "u1", "sample_count": float64(500), "receipt_ids": []any{"actual-receipt"}}}}
	return s, c, f, progress
}
func TestSpeechKeyPositive(t *testing.T) {
	s, c, f, p := speechKeyFixture(t)
	key := projectSpeechKey(s, c, f, p, "audio1", strings.Repeat("a", 64), "1.1.0")
	unit := key["units"].([]any)[0].(map[string]any)
	if key["taxonomy_version"] != "1.1.0" || key["audio"].(map[string]any)["duration_ms"] != 271 || unit["weight"] != float64(2) || unit["corrections"].([]any)[0].(map[string]any)["text"] != "opens" || unit["audio_intervals"].([]any)[0].(map[string]any)["end_ms"] != 21 {
		t.Fatal(key)
	}
}
func TestSpeechEmptyKeyPositive(t *testing.T) {
	s, c, f, p := speechKeyFixture(t)
	c["planned_units"] = []any{}
	key := projectSpeechKey(s, c, f, p, "audio1", strings.Repeat("a", 64), "1.1.0")
	if len(key["units"].([]any)) != 0 || key["status"] != "rendered" {
		t.Fatal(key)
	}
}
func TestSpeechNoInventedAccentNegative(t *testing.T) {
	s, c, f, p := speechKeyFixture(t)
	s["blueprint"].(map[string]any)["speakers"].([]any)[0].(map[string]any)["requested_accent"] = "Scottish"
	key := projectSpeechKey(s, c, f, p, "audio1", strings.Repeat("a", 64), "1.1.0")
	sp := key["speakers"].([]any)[0].(map[string]any)
	if sp["accent_evidence"] != "not_verified" || sp["observed_accent_notes"] != nil {
		t.Fatal(sp)
	}
}
func TestSpeechNoInventedTimingNegative(t *testing.T) {
	s, c, f, p := speechKeyFixture(t)
	c["utterances"].([]any)[0].(map[string]any)["surface_text"] = strings.Repeat("long text ", 1000)
	key := projectSpeechKey(s, c, f, p, "audio1", strings.Repeat("a", 64), "1.1.0")
	interval := key["utterances"].([]any)[0].(map[string]any)["audio_interval"].(map[string]any)
	if interval["start_ms"] != 0 || interval["end_ms"] != 21 {
		t.Fatal(interval)
	}
}
