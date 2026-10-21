package app

import "testing"

func TestReleaseAcousticKeyScopesPositive(t *testing.T) {
	s, c, f, p := speechKeyFixture(t)
	id := c["planned_units"].([]any)[0].(map[string]any)["id"].(string)
	f["pieces"].([]any)[0].(map[string]any)["acoustic_edits"] = []any{map[string]any{"unit_id": id}, map[string]any{"unit_id": id}}
	piece := p["pieces"].([]any)[0].(map[string]any)
	piece["sample_count"] = float64(2400)
	piece["unit_intervals"] = map[string]any{id: []any{map[string]any{"start": float64(0), "end": float64(600)}, map[string]any{"start": float64(1200), "end": float64(2400)}}}
	key := projectSpeechKey(s, c, f, p, "audio", "hash", "1.1.0")
	rows := key["units"].([]any)[0].(map[string]any)["audio_intervals"].([]any)
	if len(rows) != 2 {
		t.Fatal("multiple target intervals collapsed", rows)
	}
	for i, want := range [][2]int{{0, 25}, {50, 100}} {
		r := rows[i].(map[string]any)
		if r["start_ms"] != want[0] || r["end_ms"] != want[1] {
			t.Fatal("wrong exact scoped interval", rows)
		}
	}
}
func TestReleaseAcousticLegacyKeyNegative(t *testing.T) {
	s, c, f, p := speechKeyFixture(t)
	id := c["planned_units"].([]any)[0].(map[string]any)["id"].(string)
	f["pieces"].([]any)[0].(map[string]any)["acoustic_edits"] = []any{map[string]any{"unit_id": id}}
	p["pieces"].([]any)[0].(map[string]any)["unit_intervals"] = map[string]any{id: map[string]any{"start": float64(24), "end": float64(240)}}
	key := projectSpeechKey(s, c, f, p, "audio", "hash", "1.1.0")
	rows := key["units"].([]any)[0].(map[string]any)["audio_intervals"].([]any)
	r := rows[0].(map[string]any)
	if len(rows) != 1 || r["start_ms"] != 1 || r["end_ms"] != 10 {
		t.Fatal("accepted legacy timing replaced", rows)
	}
}

func TestReleaseUnrecordedWordCountsNegative(t *testing.T) {
	summary := speechSummary(map[string]any{"id": "old", "phase_states": map[string]any{"render": "not_started"}})
	if _, ok := summary["canonical_word_count"]; ok {
		t.Fatal("unrecorded count invented", summary)
	}
	if _, ok := summary["surface_word_count"]; ok {
		t.Fatal("unrecorded mutated count invented", summary)
	}
}
