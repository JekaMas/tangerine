package app

import (
	"encoding/json"
	"tangerine.local/api/internal/lab"
	"testing"
)

func preparationBlueprint(t *testing.T, n int) map[string]any {
	t.Helper()
	raw, _ := json.Marshal(map[string]any{"exercise_request": map[string]any{"topic": "A café visit ☕", "speaker_count": n, "text_length_words": 120}})
	b, e := ExpandBlueprint(raw, DefaultConfiguration())
	if e != nil {
		t.Fatal(e)
	}
	return b
}
func canonicalFixture(b map[string]any) map[string]any {
	return map[string]any{"schema_version": "1.0.0", "blueprint_id": b["id"], "status": "candidate", "failure_reason": nil, "utterances": []any{map[string]any{"id": "u1", "speaker_id": "s1", "canonical_text": "We’re re-opening the café today.", "surface_text": "We’re re-opening the café today."}}, "planned_units": []any{}, "acoustic_edits": []any{}}
}
func checkedCanonical(t *testing.T, c, b map[string]any, valid bool) {
	t.Helper()
	raw, _ := json.Marshal(c)
	_, _, e := ValidateCanonical(raw, b)
	if (e == nil) != valid {
		t.Fatalf("valid=%t error=%v", valid, e)
	}
}

func TestPreparationDefaultsPositive(t *testing.T) {
	b := preparationBlueprint(t, 1)
	req := b["exercise_request"].(map[string]any)
	s := b["speakers"].([]any)[0].(map[string]any)
	if req["topic"] != "A café visit ☕" || req["english_level"] != nil || b["format"] != "monologue" || b["provider_profile_id"] != "kokoro-local-en-v1" || s["voice_profile_id"] != "af_heart" || s["pace_wpm"] != float64(150) || s["l1"] != nil || b["duration_ms_max"] != nil {
		t.Fatal(b)
	}
}
func TestPreparationSharedVoicesPositive(t *testing.T) {
	b := preparationBlueprint(t, 3)
	ss := b["speakers"].([]any)
	if b["format"] != "dialogue" || ss[1].(map[string]any)["voice_profile_id"] != "am_adam" || ss[2].(map[string]any)["voice_profile_id"] != "af_heart" || ss[2].(map[string]any)["id"] != "s3" {
		t.Fatal(b)
	}
}
func TestPreparationSpeakerCountNegative(t *testing.T) {
	_, e := ExpandBlueprint([]byte(`{"exercise_request":{"topic":"Coffee","speaker_count":0,"text_length_words":10}}`), DefaultConfiguration())
	if e == nil {
		t.Fatal("zero speakers accepted")
	}
}
func TestPreparationWordTargetNegative(t *testing.T) {
	_, e := ExpandBlueprint([]byte(`{"exercise_request":{"topic":"Coffee","speaker_count":1,"text_length_words":0}}`), DefaultConfiguration())
	if e == nil {
		t.Fatal("zero word target accepted")
	}
}

func TestPreparationAdvancedPositive(t *testing.T) {
	b := preparationBlueprint(t, 2)
	delete(b, "id")
	delete(b, "schema_version")
	b["variety_policy"].(map[string]any)["target_locale"] = "en-GB"
	b["speakers"].([]any)[0].(map[string]any)["voice_profile_id"] = "bf_emma"
	raw, _ := json.Marshal(b)
	got, e := ExpandBlueprint(raw, DefaultConfiguration())
	if e != nil || got["variety_policy"].(map[string]any)["target_locale"] != "en-GB" || got["speakers"].([]any)[0].(map[string]any)["voice_profile_id"] != "bf_emma" {
		t.Fatal(e, got)
	}
}
func TestPreparationControlsPositive(t *testing.T) {
	raw := []byte(`{"exercise_request":{"topic":"Travel","speaker_count":1,"text_length_words":10,"mutation_count":0,"category_families":["grammar"],"english_level":"A2","audio_backend":"service"}}`)
	b, e := ExpandBlueprint(raw, DefaultConfiguration())
	if e != nil {
		t.Fatal(e)
	}
	if b["provider_profile_id"] != "azure-standard-en-v1" || b["exercise_request"].(map[string]any)["mutation_count"] != float64(0) || b["speakers"].([]any)[0].(map[string]any)["learner_cefr"] != "A2" {
		t.Fatal(b)
	}
}
func TestPreparationBackendConflictNegative(t *testing.T) {
	_, e := ExpandBlueprint([]byte(`{"exercise_request":{"topic":"Travel","speaker_count":1,"text_length_words":10,"audio_backend":"local"},"provider_profile_id":"azure-standard-en-v1"}`), DefaultConfiguration())
	if e == nil {
		t.Fatal("conflicting backend accepted")
	}
}
func TestPreparationDuplicateSpeakerNegative(t *testing.T) {
	b := preparationBlueprint(t, 2)
	delete(b, "id")
	delete(b, "schema_version")
	b["speakers"].([]any)[1].(map[string]any)["id"] = "s1"
	raw, _ := json.Marshal(b)
	if _, e := ExpandBlueprint(raw, DefaultConfiguration()); e == nil {
		t.Fatal("duplicate speaker accepted")
	}
}

func TestPreparationCanonicalPositive(t *testing.T) {
	b := preparationBlueprint(t, 1)
	c := canonicalFixture(b)
	checkedCanonical(t, c, b, true)
	raw, _ := json.Marshal(c)
	_, n, e := ValidateCanonical(raw, b)
	if e != nil || n != 5 {
		t.Fatal(n, e)
	}
}
func TestPreparationApproximateLengthPositive(t *testing.T) {
	b := preparationBlueprint(t, 1)
	c := canonicalFixture(b)
	checkedCanonical(t, c, b, true)
	if b["exercise_request"].(map[string]any)["text_length_words"] != float64(120) {
		t.Fatal("target altered")
	}
}
func TestPreparationInjectedTextNegative(t *testing.T) {
	b := preparationBlueprint(t, 1)
	c := canonicalFixture(b)
	c["utterances"].([]any)[0].(map[string]any)["surface_text"] = "We re-open café today."
	checkedCanonical(t, c, b, false)
}
func TestPreparationMissingRoleNegative(t *testing.T) {
	b := preparationBlueprint(t, 2)
	checkedCanonical(t, canonicalFixture(b), b, false)
}

func TestPreparationFrozenBindingsPositive(t *testing.T) {
	c := DefaultConfiguration()
	c["llm_profiles"].([]any)[0].(map[string]any)["model"] = "fixture-original"
	bs, e := preparationBindings(c, lab.Shipped())
	if e != nil || len(bs) != 2 {
		t.Fatal(e)
	}
	c["llm_profiles"].([]any)[0].(map[string]any)["model"] = "fixture-changed"
	if bs[0].(map[string]any)["model"] != "fixture-original" || bs[0].(map[string]any)["timeout_seconds"] != float64(90) || bs[1].(map[string]any)["timeout_seconds"] != float64(150) {
		t.Fatal(bs)
	}
}
func TestPreparationExactPromptPositive(t *testing.T) {
	c := DefaultConfiguration()
	c["llm_profiles"].([]any)[0].(map[string]any)["model"] = "fixture-original"
	b := lab.Shipped()
	bs, e := preparationBindings(c, b)
	if e != nil {
		t.Fatal(e)
	}
	if bs[0].(map[string]any)["prompt_bundle_sha256"] != b.SHA || bs[0].(map[string]any)["phase"] != "canonical_text" || bs[1].(map[string]any)["phase"] != "mutation" {
		t.Fatal(bs)
	}
}
func TestPreparationUnselectedModelNegative(t *testing.T) {
	if _, e := preparationBindings(DefaultConfiguration(), lab.Shipped()); e == nil {
		t.Fatal("unselected model accepted")
	}
}
func TestPreparationPaidModelNegative(t *testing.T) {
	c := DefaultConfiguration()
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	p["model"] = "fixture"
	p["billing_mode"] = "metered"
	if _, e := preparationBindings(c, lab.Shipped()); e == nil {
		t.Fatal("billed model accepted")
	}
}
