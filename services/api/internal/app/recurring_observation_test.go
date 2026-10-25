package app

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"tangerine.local/api/internal/contracts"
)

// This read-only replay needs the explicitly captured synthetic observation.
// The ordinary suite does not connect a provider or create an exercise.
func TestRecurringSavedProjectionObservation(t *testing.T) {
	root := os.Getenv("TANGERINE_RECURRING_OBSERVATION")
	if root == "" {
		t.Skip("explicit saved synthetic observation only")
	}
	read := func(name string) map[string]any {
		t.Helper()
		raw, err := os.ReadFile(filepath.Join(root, name))
		if err != nil {
			t.Fatal(err)
		}
		var value map[string]any
		if err = json.Unmarshal(raw, &value); err != nil {
			t.Fatal(err)
		}
		return value
	}
	settings := read("demo-settings_asset_id.json")
	frozen := read("demo-render_plan_asset_id.json")
	progress := read("demo-render_progress_asset_id.json")
	candidate := read("demo-candidate.json")
	key := projectSpeechKey(settings, candidate, frozen, progress, progress["assembled_asset_id"].(string), progress["assembled_sha256"].(string), "1.0.0")
	raw, _ := json.Marshal(key)
	if err := os.WriteFile(filepath.Join(root, "projected-key.json"), raw, 0600); err != nil {
		t.Fatal(err)
	}
	if _, _, err := contracts.Validate("ground-truth", "2.0.0", raw); err != nil {
		t.Fatal(err)
	}
	evaluation := map[string]any{}
	for _, field := range []string{"schema_version", "case_version_id", "taxonomy_version", "public_context", "variety_policy", "audio", "speakers", "utterances", "units", "verification_policy_version", "case_sha256"} {
		evaluation[field] = key[field]
	}
	raw, _ = json.Marshal(evaluation)
	if _, _, err := contracts.Validate("evaluation-key", "2.0.0", raw); err != nil {
		t.Fatal(err)
	}
	for _, label := range []string{"positive", "negative"} {
		score := read(label + "-results.json")["score"].(map[string]any)
		summary := map[string]any{}
		for _, field := range []string{"schema_version", "attempt_id", "case_version_id", "decision_set_sha256", "scoring_policy_version", "status", "counts", "composite", "optional_explanation", "items"} {
			summary[field] = score[field]
		}
		raw, _ = json.Marshal(summary)
		if _, _, err := contracts.Validate("feedback-score", "2.0.0", raw); err != nil {
			t.Fatal(label, err)
		}
	}
}
