package app

import (
	"encoding/json"
	"strings"
	"testing"
)

func TestReleaseLibraryAudioPositive(t *testing.T) {
	sha := strings.Repeat("a", 64)
	b, err := json.Marshal(LibraryItem{ID: "case", AudioSHA256: &sha})
	if err != nil {
		t.Fatal(err)
	}
	var row map[string]any
	if err = json.Unmarshal(b, &row); err != nil {
		t.Fatal(err)
	}
	if row["audio_sha256"] != sha {
		t.Fatal(row)
	}
	for _, name := range []string{"units", "utterances", "transcript", "mutation_manifest", "category", "target_count"} {
		if _, ok := row[name]; ok {
			t.Fatal("Private key data in Library", row)
		}
	}
}
func TestReleaseLibraryMissingAudioNegative(t *testing.T) {
	b, err := json.Marshal(LibraryItem{ID: "legacy"})
	if err != nil {
		t.Fatal(err)
	}
	var row map[string]any
	if err = json.Unmarshal(b, &row); err != nil {
		t.Fatal(err)
	}
	if _, ok := row["audio_sha256"]; ok {
		t.Fatal("Absent media advertised", row)
	}
}
