package app

import (
	"encoding/json"
	"tangerine.local/api/internal/source"
	"testing"
)

func TestSourceL2SpeakerProjectionPositive(t *testing.T) {
	m := source.NativeRecord("L2-ARCTIC", "r", "ABA.zip/ABA/transcript/arctic_a0003.txt", "transcripts", 0, source.Row{"text": "This is native text."})
	info := source.Row{"member": "README.md", "row": 42, "speaker": "ABA", "gender": "M", "native_language": "Arabic", "read_wav_files": "1129"}
	sourceL2SpeakerProjection(&m, map[string]source.Row{"ABA": info}, map[string]source.Member{"README.md": {AssetID: "official-readme"}})
	l2Assert(t, "Arabic", m.Value["corpus_record"].(map[string]any)["l1"])
	l2Assert(t, "official-readme", m.Value["raw_metadata"].(map[string]any)["speaker_metadata_asset_id"])
	l2Assert(t, "M", m.Value["raw_metadata"].(map[string]any)["speaker_metadata"].(source.Row)["gender"])
	l2Assert(t, map[string]any{"member": "README.md", "line_index": 42}, m.Value["raw_metadata"].(map[string]any)["speaker_metadata_locator"])
	l2Assert(t, nil, m.Raw["native_language"])
}
func TestSourceL2SpeakerProjectionNegative(t *testing.T) {
	m := source.NativeRecord("L2-ARCTIC", "r", "UNKNOWN/transcript/a.txt", "transcripts", 0, source.Row{"text": "Native partial source."})
	sourceL2SpeakerProjection(&m, map[string]source.Row{"ABA": {"native_language": "Arabic"}}, nil)
	l2Assert(t, nil, m.Value["corpus_record"].(map[string]any)["l1"])
	l2Assert(t, "mapped", m.Status)
	l2Assert(t, nil, m.Value["raw_metadata"].(map[string]any)["speaker_metadata"])
}

// These unit cases compile in the ordinary Go package without the disposable
// native harness helpers. Expectations are literal JSON values.
func l2Assert(t *testing.T, want, got any) {
	t.Helper()
	a, _ := json.Marshal(want)
	b, _ := json.Marshal(got)
	if string(a) != string(b) {
		t.Fatalf("want %s; got %s", a, b)
	}
}
func l2Require(t *testing.T, e error) {
	t.Helper()
	if e != nil {
		t.Fatal(e)
	}
}
