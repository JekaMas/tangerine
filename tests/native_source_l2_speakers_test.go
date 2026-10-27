package app

import (
	"context"
	"tangerine.local/api/internal/source"
	"testing"
)

func nativeL2SpeakerFixture(t *testing.T, table string) *sourceNative {
	t.Helper()
	f := sourceFixture(t)
	f.upload(t, "README.md", "|Speaker|Gender|Native Language|# Wav Files|# Annotations|\n|---|---|---|---|---|\n"+table+"\n\n")
	f.upload(t, "LICENSE", "Constructed local metadata fixture; no actual source rights grant.")
	f.upload(t, "ABA/transcript/a.txt", "Native test sentence.")
	f.upload(t, "ABA/wav/a.wav", string(sourceWave(44100, 22050)))
	f.register(t, "L2-ARCTIC", "partial_export")
	return f
}
func TestNativeSourceL2SpeakerMetadataPositive(t *testing.T) {
	f := nativeL2SpeakerFixture(t, "|ABA|M|Arabic|1|0|")
	r := f.run(t, "native", nil)
	sourceAssert(t, source.L2ParserVersion, r.Report.ParserVersion)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	var found bool
	for _, row := range rows {
		if row["table"] == "transcripts" {
			cp := row["corpus_record"].(map[string]any)
			sourceAssert(t, r.Report.ParserVersion, cp["parser_version"])
			sourceAssert(t, "Arabic", cp["l1"])
			sourceAssert(t, "ABA", cp["speaker_id"])
			raw := row["projection"].(map[string]any)["raw_metadata"].(map[string]any)
			sourceAssert(t, "M", raw["speaker_metadata"].(map[string]any)["gender"])
			sourceAssert(t, f.files[0].AssetID, raw["speaker_metadata_asset_id"])
			found = true
		}
	}
	if !found {
		t.Fatal("native transcript join missing")
	}
}
func TestNativeSourceL2SpeakerMetadataNegative(t *testing.T) {
	f := nativeL2SpeakerFixture(t, "|ABA|M|Arabic|1|0|\n|ABA|F|Hindi|1|0|")
	r := f.run(t, "native", nil)
	sourceAssert(t, "complete", r.Report.State)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	var declarations int
	for _, row := range rows {
		if row["table"] == "transcripts" {
			cp := row["corpus_record"].(map[string]any)
			sourceAssert(t, nil, cp["l1"])
			raw := row["projection"].(map[string]any)["raw_metadata"].(map[string]any)
			sourceAssert(t, nil, raw["speaker_metadata"])
		}
		if row["table"] == "speakers" {
			declarations++
		}
	}
	sourceAssert(t, 2, declarations)
}
