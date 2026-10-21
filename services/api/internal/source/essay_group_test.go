package source

import "testing"

func sourceEssayGroup(sourceID, release string) string {
	m := NativeRecord(sourceID, release, "train.json", "essays", 0, Row{"value": map[string]any{"id": "same-native-id", "text": "An independently authored essay."}})
	return m.Value["corpus_record"].(map[string]any)["group_ids"].([]string)[0]
}
func TestSourcePublicEssayGroupPositive(t *testing.T) {
	equal(t, sourceEssayGroup("FCE-2.1", "release-one"), sourceEssayGroup("FCE-2.1", "release-two"))
}
func TestSourcePublicEssayGroupNegative(t *testing.T) {
	if sourceEssayGroup("FCE-2.1", "release-one") == sourceEssayGroup("WILOCNESS-2.1", "release-one") {
		t.Fatal("unrelated dataset-local essay IDs merged into one genuine source group")
	}
}
