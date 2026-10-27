package app

import (
	"tangerine.local/api/internal/source"
	"testing"
)

func supplementFixture(id, member, table string, row source.Row) (source.Mapped, SourceRun, supplementContext) {
	m := source.NativeRecord(id, "release", member, table, 0, row)
	run := SourceRun{Report: SourceReport{Release: "release"}, Frozen: SourceFrozen{Release: SourceRelease{Source: id, Release: "native-v1"}}}
	c := supplementContext{lines: map[string]source.Row{}, metadata: map[string][]source.Row{}, media: map[string]supplementMedia{}, nli: map[int64]source.Row{}, csv: map[string]map[string][]source.Row{}, background: map[string][]map[string]any{}}
	return m, run, c
}
func supplementExample(t *testing.T, m source.Mapped) map[string]any {
	t.Helper()
	e, ok := m.Value["source_example"].(map[string]any)
	if !ok {
		t.Fatal("Normalized example missing", m)
	}
	return e
}
func TestSupplementEdAccPositive(t *testing.T) {
	m, r, c := supplementFixture("EDACC", "owner/dev/segments", "sp_edacc_segments", source.Row{"text": "utt2 EDACC-C01 5.22 6.25"})
	c.lines["owner/dev/sp_edacc_text/utt2"] = source.Row{"text": "utt2 uh <breath> yeah "}
	c.lines["owner/dev/sp_edacc_utt2spk/utt2"] = source.Row{"text": "utt2 EDACC-C01-B"}
	c.media["owner/data/EDACC-C01.wav"] = supplementMedia{Member: source.Member{AssetID: "real-wave", Path: "owner/data/EDACC-C01.wav"}, Release: "release"}
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["text"] != "uh <breath> yeah " || e["accent_is_error"] != false || e["source_clock"].(map[string]any)["start"] != "261/50" || e["media"].(map[string]any)["asset_id"] != "real-wave" {
		t.Fatal("Source reference fields lost", e)
	}
}
func TestSupplementEdAccNegative(t *testing.T) {
	m, r, c := supplementFixture("EDACC", "owner/dev/segments", "sp_edacc_segments", source.Row{"text": "utt2 EDACC-C01 5.22 6.25"})
	c.lines["owner/test/sp_edacc_text/utt2"] = source.Row{"text": "utt2 foreign"}
	c.media["foreign/data/EDACC-C01.wav"] = supplementMedia{Member: source.Member{AssetID: "foreign"}}
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["text"] == "foreign" || e["media"] != nil {
		t.Fatal("Cross-partition/foreign-root association", e)
	}
	m, r, c = supplementFixture("EDACC", "owner/dev/company.ctm", "sp_edacc_company_ctm", source.Row{"text": "record 1 1.0 0.2 word"})
	sourceSupplementProjection(&m, r, c)
	if m.Value["source_example"] != nil || m.Value["raw_metadata"].(map[string]any)["annotation_origin"] != "source_asr_output" {
		t.Fatal("ASR became reference/error gold", m)
	}
}
func TestSupplementELRDPositive(t *testing.T) {
	m, r, c := supplementFixture("ELRD", "owner/diarized_transcripts/meeting-camping-dm01-dm02.jsonl", "sp_elrd_turns", source.Row{"value": map[string]any{"start": "0:00:13.703000", "end": "0:01:00.430000", "speaker": "dm01", "transcript": "well well i think"}})
	c.media["owner/audios/meeting-camping-dm01-dm02.wav"] = supplementMedia{Member: source.Member{AssetID: "audio"}, Release: "release"}
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["text"] != "well well i think" || e["text_origin"] != "source_asr_transcription" || e["source_clock"].(map[string]any)["start"] != "13703/1000" || e["media"] == nil {
		t.Fatal("ELRD native turn lost", e)
	}
}
func TestSupplementELRDNegative(t *testing.T) {
	m, r, c := supplementFixture("ELRD", "owner/diarized_transcripts/meeting.jsonl", "sp_elrd_turns", source.Row{"ambiguous_keys": true, "value": map[string]any{"transcript": "do not trust duplicate fields"}})
	sourceSupplementProjection(&m, r, c)
	if m.Value["source_example"] != nil {
		t.Fatal("Ambiguous native fields became semantic evidence", m)
	}
	clock := source.SourceClock("invalid", "0:00:01")
	if clock["start"] != nil || clock["end"] != nil {
		t.Fatal("Invalid native time guessed", clock)
	}
}
func TestSupplementDiPlomatPositive(t *testing.T) {
	row := source.Row{"value": map[string]any{"text": []any{"Hello.", "Are you sure?"}, "speaker": []any{"A", "B"}, "label": 4, "choice": []any{"a", "b", "c", "d", "e"}, "correct_turn_number": 1}}
	m, r, c := supplementFixture("DIPLOMAT", "PIR_second_subtask_dataset/val.jsonl", "sp_diplomat", row)
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["text"] != "Hello.\nAre you sure?" || e["label_namespace"] != "DiPlomat_native_not_Tangerine" || e["native_partition"] != "val" || e["source_selected_choice"] != "e" || e["label_meaning"] != "zero_based_correct_choice_index" || e["independent_population_count"] != nil {
		t.Fatal("Native context/label/split meaning changed", e)
	}
	n, r, c := supplementFixture("DIPLOMAT", "CQA_task_dataset/train.jsonl", "sp_diplomat", row)
	sourceSupplementProjection(&n, r, c)
	if e["group_ids"].([]string)[0] != supplementExample(t, n)["group_ids"].([]string)[0] {
		t.Fatal("Overlapping task context was independent")
	}
}
func TestSupplementDiPlomatNegative(t *testing.T) {
	m, r, c := supplementFixture("DIPLOMAT", "NLI_dataset_without_context/dataset.json", "sp_diplomat", source.Row{"value": map[string]any{"text": "An assertion.", "hypothesis": "A valid alternative."}})
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["media"] != nil || e["source_clock"] != nil || e["derived_view_relation"] != nil || e["error_labels"] != "not_supplied" {
		t.Fatal("Missing context/audio/labels invented", e)
	}
}
func dralFixture() (source.Mapped, SourceRun, supplementContext) {
	row := source.Row{"header": []string{"id", "conv_id", "participant_id", "time_start", "time_end", "trans_id", "lang_code", "original_or_reenacted"}, "cells": []string{"ES_001_2", "ES_001", "1", "0 days 00:00:06.310000", "0 days 00:00:07.020000", "EN_001_2", "ES", "OG"}}
	return supplementFixture("DRAL", "DRAL-8.0/fragments-short.csv", "sp_dral_fragments_short", row)
}
func TestSupplementDRALPositive(t *testing.T) {
	m, r, c := dralFixture()
	c.media["fragments-short/ES_001_2.wav"] = supplementMedia{Member: source.Member{AssetID: "base-audio", Media: map[string]any{"sample_count": 11360, "sample_rate_hz": 16000}}, Release: "base"}
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["text"] != nil || e["source_clock"].(map[string]any)["start"] != "631/100" || e["local_clock"].(map[string]any)["start"] != "0" || e["local_clock"].(map[string]any)["end"] != "71/100" || e["base_release_dependency"] != "base" {
		t.Fatal("Fragment/base clocks or absent text conflated", e)
	}
	if m.Value["corpus_record"] != nil {
		t.Fatal("Audio invented a text corpus record")
	}
}
func TestSupplementDRALNegative(t *testing.T) {
	m, r, c := dralFixture()
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["media"] != nil || e["independent_population_count"] != nil || e["media_state"] != "not_present_in_selected_release_or_compatible_base" {
		t.Fatal("Unavailable base invented", e)
	}
	groups := e["group_ids"].([]string)
	r.Frozen.Release.Release = "another-compatible-release"
	n, _, _ := dralFixture()
	sourceSupplementProjection(&n, r, c)
	if groups[0] != supplementExample(t, n)["group_ids"].([]string)[0] {
		t.Fatal("A repeated native view became another population")
	}
}
func TestSupplementDRALWindowPositive(t *testing.T) {
	m, r, c := dralFixture()
	c.media["recordings/ES_001.wav"] = supplementMedia{Member: source.Member{AssetID: "actual-conversation", Media: map[string]any{"sample_count": 320000, "sample_rate_hz": 16000}}, Release: "base"}
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["media_representation"] != "native_recording_window" || e["native_fragment_file"] != "not_supplied_in_selected_assets" || e["local_clock"].(map[string]any)["start"] != "631/100" || e["media"].(map[string]any)["asset_id"] != "actual-conversation" {
		t.Fatal("Available conversation window lost or called a separate zero-clock clip", e)
	}
}
func TestSupplementDRALWindowNegative(t *testing.T) {
	m, r, c := dralFixture()
	c.media["recordings/ES_001.wav"] = supplementMedia{Member: source.Member{AssetID: "too-short", Media: map[string]any{"sample_count": 32000, "sample_rate_hz": 16000}}, Release: "base"}
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["media"] != nil || e["local_clock"] != nil {
		t.Fatal("Unplayable out-of-recording window invented", e)
	}
}
func TestSupplementDiPlomatPartitionPositive(t *testing.T) {
	for _, folder := range []string{"NLI_task_dataset", "NLI_dataset_without_context"} {
		m, r, c := supplementFixture("DIPLOMAT", folder+"/dataset.json", "sp_diplomat", source.Row{"value": map[string]any{"text": "An assertion.", "hypothesis": "A consequence."}})
		sourceSupplementProjection(&m, r, c)
		e := supplementExample(t, m)
		if e["native_partition"] != "train" || m.Value["corpus_record"].(map[string]any)["native_partition"] != "train" {
			t.Fatal("Owner-declared training split lost", e)
		}
	}
}
func TestSupplementDiPlomatPartitionNegative(t *testing.T) {
	m, r, c := supplementFixture("DIPLOMAT", "unknown_task/dataset.json", "sp_diplomat", source.Row{"value": map[string]any{"text": "An assertion."}})
	sourceSupplementProjection(&m, r, c)
	e := supplementExample(t, m)
	if e["native_partition"] == "train" || e["partition_origin"] != nil {
		t.Fatal("Unknown task received an invented owner split", e)
	}
}
