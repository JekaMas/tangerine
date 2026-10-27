package app

import (
	"bytes"
	"context"
	"encoding/binary"
	"encoding/json"
	"net/http/httptest"
	"strings"
	"tangerine.local/api/internal/contracts"
	"testing"
)

func overlapFixture(t *testing.T, kind string) (map[string]any, map[string]any, map[string]any, map[string]any) {
	t.Helper()
	b, clean, c, tax := mutationFixture()
	b["exercise_request"] = map[string]any{"mutation_count": float64(1), "category_families": []any{"discourse"}}
	text := "Please wait until I finish. Do not touch the wire."
	turns := []any{map[string]any{"id": "u1", "speaker_id": "s1", "canonical_text": text, "surface_text": text}, map[string]any{"id": "u2", "speaker_id": "s2", "canonical_text": "I want to speak now.", "surface_text": "I want to speak now."}}
	c["utterances"] = turns
	clean["utterances"] = turns
	u := c["planned_units"].([]any)[0].(map[string]any)
	u["primary_taxonomy_id"] = "discourse.turn_taking"
	u["accepted_taxonomy_ids"] = []any{"discourse.turn_taking"}
	u["domain"] = "discourse"
	u["utterance_ids"] = []any{"u1", "u2"}
	u["realization"].(map[string]any)["mode"] = "discourse_context"
	start := strings.Index(text, "Do not touch")
	scope := map[string]any{"start_cp": float64(start), "end_cp": float64(start + 12), "exact_text": "Do not touch"}
	u["text_spans"] = []any{map[string]any{"utterance_id": "u1", "span": scope}}
	u["realization"].(map[string]any)["canonical_text"] = "Wait for the safety instruction."
	u["realization"].(map[string]any)["surface_text"] = "Interrupt the safety instruction."
	u["rationale"] = "B takes the floor during the explicitly protected safety instruction."
	u["rationale_required_propositions"].([]any)[0].(map[string]any)["description"] = u["rationale"]
	correction := u["corrections"].([]any)[0].(map[string]any)
	correction["text"] = "Wait until A finishes the safety instruction."
	correction["required_propositions"].([]any)[0].(map[string]any)["description"] = "Let the complete safety instruction be heard before taking the floor."
	c["overlap_intents"] = []any{map[string]any{"unit_id": "e1", "kind": kind, "target_utterance_id": "u1", "overlapping_utterance_id": "u2", "target_scope": scope, "target_gain": .08, "overlapping_gain": .8}}
	tax["entries"] = []any{map[string]any{"id": "discourse.turn_taking", "domain": "discourse"}}
	if kind == "cooperative_backchannel" {
		u["expected_judgment"] = "acceptable"
		u["status_label"] = "acceptable_variant"
		b["exercise_request"] = map[string]any{"mutation_count": float64(0)}
		c["overlap_intents"].([]any)[0].(map[string]any)["target_gain"] = 1.0
		c["overlap_intents"].([]any)[0].(map[string]any)["overlapping_gain"] = .08
	}
	return b, clean, c, tax
}
func TestOverlapAdmissionPositive(t *testing.T) {
	b, clean, c, tax := overlapFixture(t, "obstructive")
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}
func TestOverlapCooperativePositive(t *testing.T) {
	b, clean, c, tax := overlapFixture(t, "cooperative_backchannel")
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}
func TestOverlapAdmissionNegative(t *testing.T) {
	for _, kind := range []string{"same-speaker", "wrong-unit", "forward-target", "false-error", "bad-scope", "missing-intent"} {
		t.Run(kind, func(t *testing.T) {
			b, clean, c, tax := overlapFixture(t, "obstructive")
			x := c["overlap_intents"].([]any)[0].(map[string]any)
			switch kind {
			case "same-speaker":
				c["utterances"].([]any)[1].(map[string]any)["speaker_id"] = "s1"
			case "wrong-unit":
				x["unit_id"] = "absent"
			case "forward-target":
				x["target_utterance_id"] = "u2"
			case "false-error":
				x["kind"] = "cooperative_backchannel"
			case "bad-scope":
				x["target_scope"].(map[string]any)["exact_text"] = "imaginary masking"
			case "missing-intent":
				delete(c, "overlap_intents")
			}
			if e := admitMutation(t, b, clean, c, tax); e == nil {
				t.Fatal("invalid overlap admitted")
			}
		})
	}
}
func TestOverlapManifestPositive(t *testing.T) {
	_, _, c, _ := overlapFixture(t, "obstructive")
	m := mutationManifest(c, "clean", strings.Repeat("a", 64), "mutated", strings.Repeat("b", 64), strings.Repeat("c", 64), nil, nil)
	raw, _ := json.Marshal(m)
	if _, _, e := contracts.Validate("mutation-manifest", "2.0.0", raw); e != nil {
		t.Fatal(e)
	}
	if len(m["edits"].([]any)) != 0 || len(overlapIntents(m)) != 1 {
		t.Fatal(m)
	}
}
func mixFixture() ([]speechSource, []any, map[string][]byte) {
	sources := []speechSource{{"a", "u1", "one two", 0, 24000, 0, []speechWord{{0, 3, 0, 12000}, {4, 7, 12000, 24000}}}, {"b", "u2", "other", 0, 24000, 0, nil}}
	intent := []any{map[string]any{"unit_id": "e1", "kind": "obstructive", "target_utterance_id": "u1", "overlapping_utterance_id": "u2", "target_scope": map[string]any{"start_cp": float64(4), "end_cp": float64(7)}, "target_gain": .5, "overlapping_gain": .5}}
	return sources, intent, map[string][]byte{"a": constantPCM(24000, 1000), "b": constantPCM(24000, -2000)}
}
func constantPCM(n int, value int16) []byte {
	raw := make([]byte, n*2)
	for i := 0; i < n; i++ {
		binary.LittleEndian.PutUint16(raw[i*2:], uint16(value))
	}
	return raw
}
func TestOverlapArithmeticPositive(t *testing.T) {
	sources, intent, audio := mixFixture()
	c, e := planSpeechComposition(sources, intent)
	if e != nil {
		t.Fatal(e)
	}
	pcm, e := composeSpeechPCM(context.Background(), c, audio)
	if e != nil {
		t.Fatal(e)
	}
	if len(pcm) != 72000 || c.Pieces[1].Start != 12000 || c.Overlaps[0].Start != 12000 || c.Overlaps[0].End != 24000 {
		t.Fatal(c, len(pcm))
	}
	for i := 0; i < 36000; i++ {
		want := int16(1000)
		if i >= 12000 && i < 24000 {
			want = -500
		}
		if i >= 24000 {
			want = -1000
		}
		if got := int16(binary.LittleEndian.Uint16(pcm[i*2:])); got != want {
			t.Fatalf("sample %d got %d want %d", i, got, want)
		}
	}
	if !bytes.Equal(pcm[:24000], audio["a"][:24000]) {
		t.Fatal("unselected speech changed")
	}
}
func TestOverlapClippingNegative(t *testing.T) {
	sources, intent, audio := mixFixture()
	x := intent[0].(map[string]any)
	x["target_gain"], x["overlapping_gain"] = 1.0, 1.0
	audio["a"], audio["b"] = constantPCM(24000, 30000), constantPCM(24000, 30000)
	c, _ := planSpeechComposition(sources, intent)
	if _, e := composeSpeechPCM(context.Background(), c, audio); e == nil || e.Error() != "AUDIO_CLIPPING" {
		t.Fatal("clipped or normalized instead", e)
	}
}
func TestOverlapCancellationNegative(t *testing.T) {
	sources, intent, audio := mixFixture()
	c, _ := planSpeechComposition(sources, intent)
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, e := composeSpeechPCM(ctx, c, audio); e != context.Canceled {
		t.Fatal(e)
	}
}
func TestOverlapSequentialPositive(t *testing.T) {
	sources, _, audio := mixFixture()
	c, e := planSpeechComposition(sources, nil)
	if e != nil {
		t.Fatal(e)
	}
	pcm, e := composeSpeechPCM(context.Background(), c, audio)
	if e != nil || !bytes.Equal(pcm, append(append([]byte{}, audio["a"]...), audio["b"]...)) {
		t.Fatal("sequential default changed", e)
	}
}
func TestOverlapTimingNegative(t *testing.T) {
	sources, intent, _ := mixFixture()
	sources[0].Words = nil
	if _, e := planSpeechComposition(sources, intent); e == nil || e.Error() != "ALIGNMENT_UNAVAILABLE" {
		t.Fatal("invented word timing", e)
	}
}
func TestOverlapLaterTurnPositive(t *testing.T) {
	sources, intent, _ := mixFixture()
	sources[1].Count = 2400
	sources[1].Gap = 2400
	sources = append(sources, speechSource{"c", "u3", "next", 0, 1200, 0, nil})
	c, e := planSpeechComposition(sources, intent)
	if e != nil || c.Pieces[2].Start != 24000 || c.SampleCount != 25200 || c.Overlaps[0].End != 14400 {
		t.Fatal("short backchannel cut off foreground speaker", c, e)
	}
}
func TestOverlapSourceMapPositive(t *testing.T) {
	sources, intent, _ := mixFixture()
	c, _ := planSpeechComposition(sources, intent)
	rows := []any{map[string]any{"piece_id": "b", "source_start": 1000, "source_end": 25000, "final_start": 0, "final_end": 24000, "source_audio_sha256": "source", "kind": "copy"}}
	out := compositionRows(rows, c.Pieces[1], c.Tracks)
	r := out[0].(map[string]any)
	if r["source_start"] != 1000 || r["source_end"] != 25000 || r["final_start"] != 12000 || r["final_end"] != 36000 || r["mix_gain"] != .5 || r["source_audio_sha256"] != "source" {
		t.Fatal(out)
	}
}
func TestOverlapKeyPositive(t *testing.T) {
	s, c, f, p := speechKeyFixture(t)
	_, _, candidate, _ := overlapFixture(t, "obstructive")
	c = candidate
	sources, intent, _ := mixFixture()
	composition, _ := planSpeechComposition(sources, intent)
	p["composition"] = compositionValue(composition)
	p["pieces"] = []any{map[string]any{"utterance_id": "u1", "sample_count": float64(24000), "receipt_ids": []any{"ra"}}, map[string]any{"utterance_id": "u2", "sample_count": float64(24000), "receipt_ids": []any{"rb"}}}
	f["pieces"] = []any{map[string]any{"gap_after_ms": float64(0)}, map[string]any{"gap_after_ms": float64(0)}}
	key := projectSpeechKey(s, c, f, p, "audio", strings.Repeat("a", 64), "1.1.0")
	u := key["utterances"].([]any)[1].(map[string]any)
	interval := u["audio_interval"].(map[string]any)
	unit := key["units"].([]any)[0].(map[string]any)["audio_intervals"].([]any)[0].(map[string]any)
	if interval["start_ms"] != 500 || interval["end_ms"] != 1500 || unit["start_ms"] != 500 || unit["end_ms"] != 1000 || key["audio"].(map[string]any)["duration_ms"] != 1500 {
		t.Fatal(key)
	}
}

func TestOverlapSplitTargetPositive(t *testing.T) {
	sources, intents, audio := mixFixture()
	sources = []speechSource{{"a1", "u1", "one ", 0, 12000, 0, nil}, {"a2", "u1", "two", 4, 12000, 0, nil}, sources[1]}
	x := intents[0].(map[string]any)
	x["target_scope"] = map[string]any{"start_cp": float64(0), "end_cp": float64(7)}
	audio["a1"], audio["a2"] = audio["a"][:24000], audio["a"][24000:]
	c, e := planSpeechComposition(sources, intents)
	if e != nil {
		t.Fatal(e)
	}
	pcm, e := composeSpeechPCM(context.Background(), c, audio)
	if e != nil || c.Pieces[2].Start != 0 || c.SampleCount != 24000 || c.Overlaps[0].End != 24000 || int16(binary.LittleEndian.Uint16(pcm[30000:])) != -500 {
		t.Fatal("split target lost a source clock", c, e)
	}
}
func TestOverlapWordsPositive(t *testing.T) {
	native := map[string]any{"decoder": []any{map[string]any{"start_sample": float64(600), "word_tokens": []any{map[string]any{"text": "café", "start_sample": float64(10), "end_sample": float64(20)}, map[string]any{"text": "café", "start_sample": float64(30), "end_sample": float64(40)}}}}}
	request := map[string]any{"operations": []any{map[string]any{"text": "A café café."}}}
	words := speechWords(native, request)
	if len(words) != 2 || words[0] != (speechWord{2, 6, 610, 620}) || words[1] != (speechWord{7, 11, 630, 640}) {
		t.Fatal(words)
	}
}
func TestOverlapSchemaNegative(t *testing.T) {
	for _, field := range []string{"target_gain", "overlapping_gain"} {
		for _, gain := range []float64{0, -.1, 1.1} {
			_, _, c, _ := overlapFixture(t, "obstructive")
			c["overlap_intents"].([]any)[0].(map[string]any)[field] = gain
			raw, _ := json.Marshal(c)
			if _, _, e := contracts.Validate("case-candidate", "1.0.0", raw); e == nil {
				t.Fatal("invalid gain admitted", field, gain)
			}
		}
	}
}
func TestOverlapPublicFailureNegative(t *testing.T) {
	code, message := speechPublicFailure(compositionFailure("AUDIO_CLIPPING"))
	if code != "PROVIDER_OUTPUT_INVALID" || strings.Contains(message, "AUDIO_CLIPPING") || !strings.Contains(message, "saved") || !strings.Contains(message, "new exercise") {
		t.Fatal(code, message)
	}
}
func TestOverlapFixedFailureNegative(t *testing.T) {
	for _, code := range []string{"AUDIO_CLIPPING", "ALIGNMENT_UNAVAILABLE"} {
		if speechRetryable(compositionFailure(code)) {
			t.Fatal("repeating frozen inputs was advertised as repair", code)
		}
	}
}
func TestOverlapRecoverableFailurePositive(t *testing.T) {
	for _, code := range []string{"SPEECH_UNAVAILABLE", "SPEECH_TIMEOUT", "MODEL_SETUP_REQUIRED", "MISSING_CREDENTIALS", "CANCELLED"} {
		if !speechRetryable(compositionFailure(code)) {
			t.Fatal("recoverable saved work lost resume", code)
		}
	}
}
func TestOverlapFixedFailureResponseNegative(t *testing.T) {
	code, message := speechPublicFailure(compositionFailure("ALIGNMENT_UNAVAILABLE"))
	p := map[string]any{"id": "saved", "phase_states": map[string]any{"render": "failed"}, "last_failure": map[string]any{"code": code, "message": message, "retryable": false}}
	w := httptest.NewRecorder()
	(&Server{}).generationResponse(w, p, compositionFailure("ALIGNMENT_UNAVAILABLE"))
	var body map[string]any
	_ = json.Unmarshal(w.Body.Bytes(), &body)
	if body["retryable"] != false || body["code"] != "CAPABILITY_UNQUALIFIED" || strings.Contains(body["message"].(string), "ALIGNMENT_UNAVAILABLE") || !strings.Contains(body["message"].(string), "compatible speech voice") {
		t.Fatal("immediate response contradicted the saved recovery action", body)
	}
}
func TestOverlapFutureNativeClockNegative(t *testing.T) {
	s, intents, _ := mixFixture()
	intents[0].(map[string]any)["target_utterance_id"] = "u2"
	intents[0].(map[string]any)["overlapping_utterance_id"] = "u1"
	intents[0].(map[string]any)["target_scope"] = map[string]any{"start_cp": float64(0), "end_cp": float64(5)}
	if _, e := planSpeechComposition(s, intents); e == nil {
		t.Fatal("future source accepted before its clock exists")
	}
}

func TestOverlapCanonicalNegative(t *testing.T) {
	b, clean, c, _ := overlapFixture(t, "obstructive")
	clean["overlap_intents"] = c["overlap_intents"]
	raw, _ := json.Marshal(clean)
	if _, _, e := canonicalContent(raw, b); e == nil {
		t.Fatal("clean phase admitted a timing mutation")
	}
}
func TestOverlapFrozenPlanPositive(t *testing.T) {
	s, _, profile := speechFixture(t)
	_, _, c, _ := overlapFixture(t, "obstructive")
	s["blueprint"].(map[string]any)["speakers"] = append(s["blueprint"].(map[string]any)["speakers"].([]any), map[string]any{"id": "s2", "voice_profile_id": "am_adam"})
	profile["voices"] = append(profile["voices"].([]any), map[string]any{"id": "am_adam", "locale": "en-US"})
	plan, e := compileSpeechPlan("preparation", s, c, profile)
	if e != nil {
		t.Fatal(e)
	}
	raw, _ := json.Marshal(plan)
	if _, _, e := contracts.Validate("render-plan", "2.0.0", raw); e != nil {
		t.Fatal(e)
	}
	if len(overlapIntents(plan)) != 1 || plan["turns"].([]any)[1].(map[string]any)["voice_id"] != "am_adam" {
		t.Fatal(plan)
	}
}
func TestOverlapAcousticKeySiblingPositive(t *testing.T) {
	s, c, f, p := speechKeyFixture(t)
	sources, intent, _ := mixFixture()
	composition, _ := planSpeechComposition(sources, intent)
	composition.Overlaps[0].UnitID = "overlap-other-unit"
	p["composition"] = compositionValue(composition)
	p["pieces"] = []any{map[string]any{"utterance_id": "u1", "sample_count": float64(24000), "receipt_ids": []any{}}, map[string]any{"utterance_id": "u2", "sample_count": float64(24000), "receipt_ids": []any{}, "unit_intervals": map[string]any{"e1": []any{map[string]any{"start": float64(2400), "end": float64(4800)}}}}}
	f["pieces"] = []any{map[string]any{"gap_after_ms": float64(0)}, map[string]any{"gap_after_ms": float64(0), "acoustic_edits": []any{map[string]any{"unit_id": "e1"}}}}
	key := projectSpeechKey(s, c, f, p, "audio", strings.Repeat("a", 64), "1.1.0")
	interval := key["units"].([]any)[0].(map[string]any)["audio_intervals"].([]any)[0].(map[string]any)
	if interval["start_ms"] != 600 || interval["end_ms"] != 700 {
		t.Fatal("acoustic sibling used obsolete sequential offset", interval)
	}
}
