package app

import (
	"encoding/json"
	"testing"
)

func TestReleaseReviewAttachedTextEvidencePositive(t *testing.T) {
	r, f, out := reviewOutputFixture(t)
	u := f.Key["units"].([]any)[0].(map[string]any)
	u["evidence_ids"] = []any{"bound-text-attachment"}
	f.Resources.Evidence = []any{}
	out["unit_judgments"].([]any)[0].(map[string]any)["evidence_ids"] = []any{"bound-text-attachment"}
	raw, _ := json.Marshal(out)
	if _, err := admitReview(raw, r, f); err != nil {
		t.Fatal(err)
	}
}
func TestReleaseReviewUnknownEvidenceNegative(t *testing.T) {
	for _, mode := range []string{"textual", "acoustic_segmental"} {
		r, f, out := reviewOutputFixture(t)
		u := f.Key["units"].([]any)[0].(map[string]any)
		u["realization"].(map[string]any)["mode"] = mode
		u["evidence_ids"] = []any{"bound-text-attachment"}
		f.Resources.Evidence = []any{}
		id := "invented"
		if mode == "acoustic_segmental" {
			id = "bound-text-attachment"
		}
		out["unit_judgments"].([]any)[0].(map[string]any)["evidence_ids"] = []any{id}
		raw, _ := json.Marshal(out)
		if _, err := admitReview(raw, r, f); err == nil {
			t.Fatal("Unseen or acoustic attachment accepted", mode)
		}
	}
}

func TestReleaseReviewGeneratedTurnPositive(t *testing.T) {
	source := map[string]any{"source_id": "GENERATED-EXERCISE", "source_record_id": nil, "rights_approval_id": nil, "uses": []any{"local_analysis", "derivative_exercises"}, "status": "approved", "licence_evidence_hash": nil}
	key := map[string]any{"audio": map[string]any{"source_profile_id": "GENERATED-EXERCISE"}, "units": []any{map[string]any{"utterance_ids": []any{"t1"}, "source": source}}}
	got := reviewUnitSource(key, map[string]any{"utterance_ids": []any{"t2"}})
	if got["status"] != "approved" || len(got["uses"].([]any)) != 2 {
		t.Fatal("Known generated recording wrongly became pending for another utterance", got)
	}
	got["status"] = "changed"
	if source["status"] != "approved" {
		t.Fatal("Saved source was mutated")
	}
}
func TestReleaseReviewGeneratedEmptyKeyPositive(t *testing.T) {
	key := map[string]any{"audio": map[string]any{"source_profile_id": "GENERATED-EXERCISE"}, "units": []any{}}
	got := reviewUnitSource(key, map[string]any{"utterance_ids": []any{"t2"}})
	if got["source_id"] != "GENERATED-EXERCISE" || got["status"] != "approved" || len(got["uses"].([]any)) != 2 {
		t.Fatal(got)
	}
}
func TestReleaseReviewUnknownTurnSourceNegative(t *testing.T) {
	for _, root := range []string{"PRIVATE-CORPUS", "GENERATED-EXERCISE"} {
		key := map[string]any{"audio": map[string]any{"source_profile_id": root}, "units": []any{map[string]any{"utterance_ids": []any{"t1"}, "source": map[string]any{"source_id": "PRIVATE-CORPUS", "status": "pending", "uses": []any{}}}}}
		got := reviewUnitSource(key, map[string]any{"utterance_ids": []any{"t2"}})
		if got["status"] != "pending" || len(got["uses"].([]any)) != 0 {
			t.Fatal("Unknown/mixed corpus got invented rights", got)
		}
	}
}
