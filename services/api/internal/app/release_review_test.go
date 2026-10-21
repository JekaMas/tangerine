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
