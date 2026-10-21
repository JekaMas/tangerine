package app

import (
	"encoding/json"
	"tangerine.local/api/internal/contracts"
	"testing"
)

func TestAudioDiagnosticLocalProfilePositive(t *testing.T) {
	p := audioDiagnosticDefaults()["profiles"].([]any)[1].(map[string]any)
	selected, err := diagnosticProfile(map[string]any{"audio_diagnostic_profile": p}, "qwen25-omni-audio-v1")
	if err != nil || selected["model"] != "Qwen/Qwen2.5-Omni-3B" || selected["billing_mode"] != "local" {
		t.Fatal(selected, err)
	}
}
func TestAudioDiagnosticUnselectedNegative(t *testing.T) {
	if _, err := diagnosticProfile(DefaultConfiguration(), "qwen25-omni-audio-v1"); err == nil {
		t.Fatal("missing auditory model silently selected")
	}
}
func TestAudioDiagnosticMeteredNegative(t *testing.T) {
	p := audioDiagnosticDefaults()["profiles"].([]any)[2].(map[string]any)
	p["billing_mode"] = "metered"
	if _, err := diagnosticProfile(map[string]any{"audio_diagnostic_profile": p}, "gemini-audio-v1"); err == nil {
		t.Fatal("metered auditory profile accepted")
	}
}
func TestAudioDiagnosticNativeProfilePositive(t *testing.T) {
	p, err := diagnosticProfile(DefaultConfiguration(), "faster-whisper-local-en-v1")
	if err != nil || p["billing_mode"] != "local" {
		t.Fatal(p, err)
	}
	for _, id := range []string{"ffmpeg-ebur128-v1", "praat-ac-v1", "faster-whisper-local-en-v1", "qwen25-omni-audio-v1", "gemini-audio-v1"} {
		if !diagnosticMethod(id) {
			t.Fatal(id)
		}
	}
}
func diagnosticIntentFixture(t *testing.T) diagnosticFrozen {
	t.Helper()
	s, c, p, progress := speechKeyFixture(t)
	key := projectSpeechKey(s, c, p, progress, "audio", "hash", "2.0.0")
	raw, _ := json.Marshal(key)
	if err := json.Unmarshal(raw, &key); err != nil {
		t.Fatal(err)
	}
	return diagnosticFrozen{Key: key, Canonical: "The café opens tomorrow.", Surface: "The café open tomorrow."}
}
func TestAudioDiagnosticIntentPositive(t *testing.T) {
	f := diagnosticIntentFixture(t)
	u := f.Key["units"].([]any)[0].(map[string]any)
	u["audio_intervals"] = []any{map[string]any{"start_ms": float64(0), "end_ms": float64(100)}}
	result := diagnosticIntent(f, map[string]any{"start": float64(0), "end": float64(2400)})
	if len(result["units"].([]any)) != 1 || result["canonical_text"] != "The café opens tomorrow." || result["surface_text"] != "The café open tomorrow." {
		t.Fatal(result)
	}
	if _, present := result["answer"]; present {
		t.Fatal("listener answer leaked to audio judge")
	}
}
func TestAudioDiagnosticPriorObservationNegative(t *testing.T) {
	f := diagnosticIntentFixture(t)
	u := f.Key["units"].([]any)[0].(map[string]any)
	u["audio_intervals"] = []any{map[string]any{"start_ms": float64(0), "end_ms": float64(100)}}
	r := u["realization"].(map[string]any)
	r["observed_ipa"] = "pæn"
	r["observed_pace_wpm"] = float64(120)
	r["observed_pause_ms"] = float64(300)
	out := diagnosticIntent(f, map[string]any{"start": float64(0), "end": float64(2400)})
	r = out["planned_units"].([]any)[0].(map[string]any)["realization"].(map[string]any)
	if r["observed_ipa"] != nil || r["observed_pace_wpm"] != nil || r["observed_pause_ms"] != nil {
		t.Fatal("prior acoustic observations conditioned the judge", r)
	}
	if u["realization"].(map[string]any)["observed_ipa"] != "pæn" {
		t.Fatal("saved key mutated")
	}
}
func TestAudioDiagnosticOutsideClipNegative(t *testing.T) {
	f := diagnosticIntentFixture(t)
	u := f.Key["units"].([]any)[0].(map[string]any)
	u["audio_intervals"] = []any{map[string]any{"start_ms": float64(0), "end_ms": float64(100)}}
	out := diagnosticIntent(f, map[string]any{"start": float64(4800), "end": float64(7200)})
	if len(out["units"].([]any)) != 0 || len(out["planned_units"].([]any)) != 0 {
		t.Fatal("out-of-clip unit included", out)
	}
}

func TestReviewMeasurementsContextPositive(t *testing.T) {
	r, f, _ := reviewOutputFixture(t)
	entry := map[string]any{"id": "grammar.verbs.subject_verb_agreement", "label": "Agreement", "definition": "Agreement"}
	f.Taxonomy = map[string]any{"entries": []any{entry}}
	f.Resources.Taxonomy = []any{entry}
	f.Measurements = []any{map[string]any{"id": "measurement", "method_id": "qwen25-omni-audio-v1", "categorical_value": "model_supported"}}
	input, parts := reviewInput(r, f)
	if len(input["measurements"].([]any)) != 1 || parts["evidence"].(map[string]any)["audio_measurements"] == nil {
		t.Fatal(input, parts)
	}
	if input["input_modality"] != "text" || len(f.Resources.Evidence) != 0 {
		t.Fatal("reports promoted to hearing/native evidence", input, f.Resources)
	}
}
func TestReviewMeasurementsAbsentNegative(t *testing.T) {
	r, f, _ := reviewOutputFixture(t)
	f.Taxonomy = map[string]any{"entries": []any{}}
	input, _ := reviewInput(r, f)
	if len(input["measurements"].([]any)) != 0 || input["input_modality"] != "text" {
		t.Fatal(input)
	}
}

func TestAudioDiagnosticMixedTargetsPositive(t *testing.T) {
	f := diagnosticIntentFixture(t)
	u := f.Key["units"].([]any)[0].(map[string]any)
	u["audio_intervals"] = []any{map[string]any{"start_ms": float64(0), "end_ms": float64(100)}}
	raw, _ := json.Marshal(u)
	var second map[string]any
	_ = json.Unmarshal(raw, &second)
	second["id"] = "stress2"
	second["realization"].(map[string]any)["prosody"] = []any{map[string]any{"feature": "lexical_stress", "observation": "prior", "evidence_ids": []any{"prior"}}}
	f.Key["units"] = []any{u, second}
	out := diagnosticIntent(f, map[string]any{"start": float64(0), "end": float64(2400)})
	features := out["features"].([]any)
	if len(features) != 2 || features[0] != "speech_realization" || features[1] != "lexical_stress" {
		t.Fatal(out)
	}
	if len(out["units"].([]any)) != 2 {
		t.Fatal(out)
	}
}

func TestAudioDiagnosticScopedIdentifierPositive(t *testing.T) {
	for _, field := range []string{"method_id", "target_unit_id", "unit_id"} {
		if !externalID("audio-measurement", field) {
			t.Fatal(field)
		}
	}
}
func TestAudioDiagnosticForeignIdentifierNegative(t *testing.T) {
	for _, field := range []string{"case_version_id", "evidence_asset_ids"} {
		if externalID("audio-measurement", field) {
			t.Fatal("Foreign lineage was waived", field)
		}
	}
	if externalID("candidate-envelope", "unit_id") {
		t.Fatal("Unrelated owner exemption")
	}
}

func TestAudioDiagnosticComputeBindingsPositive(t *testing.T) {
	p := audioDiagnosticDefaults()["profiles"].([]any)[1].(map[string]any)
	if p["compute_type"] != "int8_dynamic" || p["device"] != "cpu" || p["quantization_engine"] != "qnnpack" || p["repetition_penalty"] != 1.1 {
		t.Fatal(p)
	}
	if _, _, err := contracts.Validate("audio-judge-profile", "2.0.0", sourceBytes(p)); err != nil {
		t.Fatal(err)
	}
	delete(p, "compute_type") // legacy omission still means float32, never a silent quantization switch.
	delete(p, "quantization_engine")
	delete(p, "repetition_penalty")
	if _, _, err := contracts.Validate("audio-judge-profile", "2.0.0", sourceBytes(p)); err != nil {
		t.Fatal(err)
	}
}
func TestAudioDiagnosticComputeBindingNegative(t *testing.T) {
	for _, mode := range []string{"invented", "cuda", "unknown-engine", "penalty"} {
		p := audioDiagnosticDefaults()["profiles"].([]any)[1].(map[string]any)
		if mode == "penalty" {
			p["repetition_penalty"] = 0
		} else if mode == "unknown-engine" {
			p["quantization_engine"] = "invented"
		} else if mode == "cuda" {
			p["device"] = "cuda"
		} else {
			p["compute_type"] = mode
		}
		if _, _, err := contracts.Validate("audio-judge-profile", "2.0.0", sourceBytes(p)); err == nil {
			t.Fatal("Unsupported new binding admitted", p)
		}
	}
}

func TestAudioDiagnosticControlledTargetPositive(t *testing.T) {
	f := diagnosticIntentFixture(t)
	unit := f.Key["units"].([]any)[0].(map[string]any)
	f.Manifest = map[string]any{"acoustic_edits": []any{map[string]any{"unit_id": unit["id"], "controller": "pause_insert"}}}
	out := diagnosticIntent(f, map[string]any{"start": float64(0), "end": float64(2400)})
	features := out["features"].([]any)
	if len(features) != 1 || features[0] != "pause_insert" {
		t.Fatal(out)
	}
	if len(out["acoustic_edits"].([]any)) != 1 {
		t.Fatal(out)
	}
}
func TestAudioDiagnosticForeignControlNegative(t *testing.T) {
	f := diagnosticIntentFixture(t)
	f.Manifest = map[string]any{"acoustic_edits": []any{map[string]any{"unit_id": "foreign", "controller": "pause_insert"}}}
	out := diagnosticIntent(f, map[string]any{"start": float64(0), "end": float64(2400)})
	features := out["features"].([]any)
	if len(features) != 1 || features[0] != "speech_realization" || len(out["acoustic_edits"].([]any)) != 0 {
		t.Fatal(out)
	}
}
