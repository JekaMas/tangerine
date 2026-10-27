package app

import (
	"context"
	"encoding/json"
	"os"
	"testing"
)

// These small explicitly constructed releases use the same real durable source
// owners as the full retained import. No corpus row or successful API is mocked.
func TestNativeJFLEGVerifyUIFixtures(t *testing.T) {
	s := jflegOpen(t)
	t.Cleanup(func() { s.DB.Close() })
	server := NewServer(s, "http://localhost:3000", "http://no-model.invalid")
	server.token = "source-owned-token"
	fixtures := map[string]any{}
	for _, kind := range []string{"partial", "empty"} {
		f := &sourceNative{s: server}
		f.upload(t, kind+"/README.md", "Constructed verification fixture; no full acquired release or linguistic gold claim.")
		if kind == "partial" {
			f.upload(t, kind+"/dev/dev.src", "They goes . \nSecond .\n")
		}
		f.upload(t, kind+"/dev/dev.ref0", "They go . \nSecond .\n")
		f.register(t, "JFLEG", "partial_export")
		run := f.run(t, "native", nil)
		sourceAssert(t, "complete", run.Report.State)
		sourceAssert(t, false, run.Report.Normalized)
		items, _, e := s.SourceCorrectionExamples(context.Background(), run.Report.ID, "", "", 20)
		sourceRequire(t, e)
		want := 0
		if kind == "partial" {
			want = 2
			for _, item := range items {
				sourceAssert(t, "partial", item.ReferenceCompleteness)
				sourceAssert(t, 1, len(item.References))
			}
		}
		sourceAssert(t, want, len(items))
		dataset, e := s.SourceCorrectionDataset(context.Background(), run.Report.ID, "dev")
		sourceRequire(t, e)
		sourceAssert(t, want, len(dataset.Examples))
		fixtures[kind] = map[string]any{"release_id": f.release.ID, "import_id": run.Report.ID, "expected_examples": want, "examples": items, "constructed": true, "expected_origin": "constructed://independent-native-fixture"}
	}
	jflegSave(t, "verify-ui-fixtures.json", fixtures)
}

func TestNativeJFLEGVerifyCommitFixtures(t *testing.T) {
	s := jflegOpen(t)
	t.Cleanup(func() { s.DB.Close() })
	raw, e := os.ReadFile("/evidence/verify-ui-fixtures.json")
	sourceRequire(t, e)
	var fixtures map[string]map[string]any
	sourceRequire(t, json.Unmarshal(raw, &fixtures))
	for _, kind := range []string{"partial", "empty"} {
		id := fixtures[kind]["import_id"].(string)
		sourceRequire(t, s.CommitSourceImport(context.Background(), id))
		var published bool
		sourceRequire(t, s.DB.QueryRow(context.Background(), "SELECT published FROM source_import WHERE id=$1", id).Scan(&published))
		sourceAssert(t, true, published)
	}
	jflegSave(t, "verify-fixtures-commit.json", map[string]any{"constructed": true, "existing_imports": fixtures, "published": true, "new_imports": 0})
}
