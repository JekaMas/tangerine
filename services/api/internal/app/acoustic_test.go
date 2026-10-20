package app

import (
	"encoding/json"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"testing"
)

func TestAcousticSelectionPositive(t *testing.T) {
	b, e := ExpandBlueprint([]byte(`{"exercise_request":{"topic":"Travel","speaker_count":1,"text_length_words":30,"category_families":["pronunciation"]}}`), DefaultConfiguration())
	if e != nil {
		t.Fatal(e)
	}
	if b["provider_profile_id"] != "kokoro-controlled-v1" {
		t.Fatal(b)
	}
	c := DefaultConfiguration()
	before := lab.Hash(c)
	p, e := resolvedPreparationSpeechProfile(b, c)
	if e != nil {
		t.Fatal(e)
	}
	if p["provider"] != "local_kokoro" || p["adapter_version"] != "kokoro-controlled-v1" || lab.Hash(c) != before {
		t.Fatal(p, "accepted configuration mutated")
	}
}
func TestAcousticUnfilteredPositive(t *testing.T) {
	b, e := ExpandBlueprint([]byte(`{"exercise_request":{"topic":"Travel","speaker_count":1,"text_length_words":30}}`), DefaultConfiguration())
	if e != nil || b["provider_profile_id"] != "kokoro-controlled-v1" {
		t.Fatal(b, e)
	}
}
func TestAcousticExplicitNegative(t *testing.T) {
	b, e := ExpandBlueprint([]byte(`{"provider_profile_id":"kokoro-local-en-v1","exercise_request":{"topic":"Travel","speaker_count":1,"text_length_words":30,"category_families":["pronunciation"]}}`), DefaultConfiguration())
	if e != nil {
		t.Fatal(e)
	}
	if b["provider_profile_id"] != "kokoro-local-en-v1" {
		t.Fatal("explicit binding silently switched")
	}
	p, e := resolvedPreparationSpeechProfile(b, DefaultConfiguration())
	if e != nil {
		t.Fatal(e)
	}
	if requireAcousticProfile(p) == nil {
		t.Fatal("plain adapter falsely accepted controlled operation")
	}
}
func TestAcousticTextOnlyNegative(t *testing.T) {
	for _, r := range []string{`{"category_families":["grammar"]}`, `{"mutation_count":0}`} {
		var req map[string]any
		_ = json.Unmarshal([]byte(r), &req)
		req["topic"] = "Travel"
		req["speaker_count"] = 1
		req["text_length_words"] = 30
		raw, _ := json.Marshal(map[string]any{"exercise_request": req})
		b, e := ExpandBlueprint(raw, DefaultConfiguration())
		if e != nil || b["provider_profile_id"] != "kokoro-local-en-v1" {
			t.Fatal(b, e)
		}
	}
}
func TestAcousticPlanPositive(t *testing.T) {
	s, c, p := speechFixture(t)
	_, _, acoustic, _ := acousticMutationFixture()
	c = acoustic
	p["adapter_version"] = "kokoro-controlled-v1"
	plan, e := compileSpeechPlan("p1", s, c, p)
	if e != nil {
		t.Fatal(e)
	}
	turn := plan["turns"].([]any)[0].(map[string]any)
	ops := turn["acoustic_edits"].([]any)
	if len(plan["required_capabilities"].([]any)) != 3 || plan["required_capabilities"].([]any)[2] != "ipa" {
		t.Fatal("missing actual operator capability", plan)
	}
	if len(ops) != 1 || ops[0].(map[string]any)["taxonomy_id"] != "pronunciation.segmental.consonant_voicing" {
		t.Fatal(turn)
	}
}
func TestAcousticCoreHashPositive(t *testing.T) {
	s, c, p := speechFixture(t)
	plan, e := compileSpeechPlan("p1", s, c, p)
	if e != nil {
		t.Fatal(e)
	}
	before := speechPlanHash(plan)
	plan["production_plan_asset_id"] = "resolved-child"
	if speechPlanHash(plan) != before {
		t.Fatal("circular child hash")
	}
	raw, _ := json.Marshal(plan)
	if _, _, e := contracts.Validate("render-plan", "2.0.0", raw); e != nil {
		t.Fatal("native admission disagrees with the core hash definition", e)
	}
}
func TestAcousticWrongProviderNegative(t *testing.T) {
	if requireAcousticProfile(map[string]any{"provider": "azure_speech", "adapter_version": "kokoro-controlled-v1"}) == nil {
		t.Fatal("incompatible explicit engine accepted")
	}
}
func TestAcousticProfileUnknownNegative(t *testing.T) {
	if _, e := resolvedPreparationSpeechProfile(map[string]any{"provider_profile_id": "missing"}, DefaultConfiguration()); e == nil {
		t.Fatal("invented profile")
	}
}
func TestAcousticGapPositive(t *testing.T) {
	r := sampleGap("piece", 1200, 96000)
	if r["final_end"] != 97200 || r["source_start"] != r["source_end"] || r["source_audio_sha256"] != nil {
		t.Fatal(r)
	}
}
func TestAcousticSampleMapPositive(t *testing.T) {
	r := actualSampleMap("core", "output", 100, []any{sampleGap("p", 0, 100)})
	if r["sample_rate_hz"] != 24000 || r["sample_count"] != 100 || r["output_audio_sha256"] != "output" {
		t.Fatal(r)
	}
}
func TestAcousticSummaryPrivateNegative(t *testing.T) {
	p := map[string]any{"id": "p", "revision": 1, "phase_states": map[string]any{"render": "failed"}, "last_failure": nil, "settings_asset_id": "private", "source_asset_id": "private", "key_id": "private"}
	s := speechSummary(p)
	for _, k := range []string{"key_id", "settings_asset_id", "source_asset_id"} {
		if s[k] != nil {
			t.Fatal(s)
		}
	}
}
func TestAcousticDistinctStageNegative(t *testing.T) {
	p := map[string]any{"id": "piece"}
	if acousticChild(p, "step-0:resolve")["id"] == acousticChild(p, "step-0:transform")["id"] || acousticChild(p, "step-0:transform")["id"] == acousticChild(p, "step-1:transform")["id"] {
		t.Fatal("different native stages alias")
	}
}
func TestAcousticPreflightLocalPositive(t *testing.T) {
	b := map[string]any{"exercise_request": map[string]any{"category_families": []any{"pronunciation"}}, "targets": []any{}}
	if e := requestedAcousticCapability(b, map[string]any{"provider": "local_kokoro", "adapter_version": "kokoro-controlled-v1"}); e != nil {
		t.Fatal(e)
	}
}
func TestAcousticPreflightAzurePositive(t *testing.T) {
	b := map[string]any{"targets": []any{map[string]any{"taxonomy_id": "pronunciation.segmental.consonant_voicing"}}}
	if e := requestedAcousticCapability(b, map[string]any{"provider": "azure_speech", "capabilities": []any{"plain_text", "ipa"}}); e != nil {
		t.Fatal(e)
	}
}
func TestAcousticPreflightPlainNegative(t *testing.T) {
	b := map[string]any{"exercise_request": map[string]any{"category_families": []any{"pronunciation"}}, "targets": []any{}}
	if requestedAcousticCapability(b, map[string]any{"provider": "local_kokoro", "adapter_version": "kokoro-local-en-v1"}) == nil {
		t.Fatal("explicit incompatible profile reached generation")
	}
}
func TestAcousticPreflightTimingNegative(t *testing.T) {
	b := map[string]any{"targets": []any{map[string]any{"taxonomy_id": "pronunciation.segmental.vowel_length"}}}
	if requestedAcousticCapability(b, map[string]any{"provider": "azure_speech", "capabilities": []any{"plain_text", "ipa"}}) == nil {
		t.Fatal("unavailable fine-phone timing reached generation")
	}
}

func measuredRangeFixture() (map[string]any, map[string]any, map[string]any, map[string]any) {
	b, clean, c, tax := acousticMutationFixture()
	unit := c["planned_units"].([]any)[0].(map[string]any)
	unit["primary_taxonomy_id"] = "pronunciation.suprasegmental.pitch_range"
	unit["accepted_taxonomy_ids"] = []any{unit["primary_taxonomy_id"]}
	unit["domain"] = "pronunciation.suprasegmental"
	unit["realization"].(map[string]any)["mode"] = "acoustic_suprasegmental"
	tax["entries"] = []any{map[string]any{"id": unit["primary_taxonomy_id"], "domain": unit["domain"]}}
	op := c["acoustic_edits"].([]any)[0].(map[string]any)
	op["controller"] = "pitch_duration"
	p := op["parameters"].(map[string]any)
	for _, k := range []string{"reference_ipa", "mutated_ipa", "phone_start", "phone_end"} {
		p[k] = nil
	}
	return b, clean, c, tax
}
func TestAcousticMeasuredRangeAdmissionPositive(t *testing.T) {
	b, clean, c, tax := measuredRangeFixture()
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal("source-derived pitch range rejected before audio exists", e)
	}
}
func TestAcousticMeasuredRangePlanPositive(t *testing.T) {
	settings, _, profile := speechFixture(t)
	_, _, c, _ := measuredRangeFixture()
	profile["adapter_version"] = "kokoro-controlled-v1"
	plan, e := compileSpeechPlan("p1", settings, c, profile)
	if e != nil {
		t.Fatal(e)
	}
	edit := plan["turns"].([]any)[0].(map[string]any)["acoustic_edits"].([]any)[0].(map[string]any)
	if edit["taxonomy_id"] != "pronunciation.suprasegmental.pitch_range" || len(edit["parameters"].(map[string]any)["pitch_points"].([]any)) != 0 {
		t.Fatal("invented pitch before source generation", edit)
	}
}
func TestAcousticMeasuredRangeWrongLeafNegative(t *testing.T) {
	b, clean, c, tax := acousticMutationFixture()
	op := c["acoustic_edits"].([]any)[0].(map[string]any)
	op["controller"] = "pitch_duration"
	p := op["parameters"].(map[string]any)
	for _, k := range []string{"reference_ipa", "mutated_ipa", "phone_start", "phone_end"} {
		p[k] = nil
	}
	if admitMutation(t, b, clean, c, tax) == nil {
		t.Fatal("empty control on an unrelated leaf was accepted")
	}
}
func TestAcousticMeasuredRangeTextUnitNegative(t *testing.T) {
	b, clean, c, tax := measuredRangeFixture()
	c["planned_units"].([]any)[0].(map[string]any)["realization"].(map[string]any)["mode"] = "textual"
	if admitMutation(t, b, clean, c, tax) == nil {
		t.Fatal("text-only unit acquired an acoustic control")
	}
}
