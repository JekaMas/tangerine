package app

import "testing"

func TestReleaseMutationShapePositive(t *testing.T) {
	v := projectionCandidate(t, "The café open tomorrow.", "open", 10, 14, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["corrections"] = []any{map[string]any{"text": "opens"}}
	normalizeMutationOutput(v)
	if len(u["rationale_forbidden_propositions"].([]any)) != 0 || u["corrections"].([]any)[0].(map[string]any)["canonical"] != true || projectedSpan(v)["start_cp"] != float64(9) {
		t.Fatal(v)
	}
}
func TestReleaseMutationShapeExplicitNegative(t *testing.T) {
	v := projectionCandidate(t, "open", "open", 0, 4, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["rationale_forbidden_propositions"] = []any{"retained"}
	u["corrections"] = []any{map[string]any{"canonical": false}}
	normalizeMutationOutput(v)
	if u["rationale_forbidden_propositions"].([]any)[0] != "retained" || u["corrections"].([]any)[0].(map[string]any)["canonical"] != false {
		t.Fatal(v)
	}
}
func TestReleaseMutationShapeAlternativesNegative(t *testing.T) {
	v := projectionCandidate(t, "open", "open", 0, 4, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["corrections"] = []any{map[string]any{"text": "opens"}, map[string]any{"text": "will open"}}
	normalizeMutationOutput(v)
	for _, r := range u["corrections"].([]any) {
		if _, ok := r.(map[string]any)["canonical"]; ok {
			t.Fatal("preferred alternative invented", v)
		}
	}
}
func TestReleaseMutationShapeMalformedNegative(t *testing.T) {
	v := projectionCandidate(t, "open", "open", 0, 4, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["rationale_forbidden_propositions"] = nil
	u["corrections"] = []any{map[string]any{"canonical": "yes"}}
	normalizeMutationOutput(v)
	if u["rationale_forbidden_propositions"] != nil || u["corrections"].([]any)[0].(map[string]any)["canonical"] != "yes" {
		t.Fatal(v)
	}
}

func TestReleaseMutationDisplayRationalePositive(t *testing.T) {
	v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["rationale_required_propositions"] = []any{map[string]any{"id": "r1", "description": "The singular subject requires opens."}, map[string]any{"id": "r2", "description": "The heard open lacks agreement."}}
	normalizeMutationOutput(v)
	if u["rationale"] != "The singular subject requires opens.\nThe heard open lacks agreement." {
		t.Fatal(u)
	}
}
func TestReleaseMutationDisplayRationaleNegative(t *testing.T) {
	for _, propositions := range []any{nil, []any{}, []any{map[string]any{"description": 17}}, []any{map[string]any{"description": ""}}, []any{map[string]any{"description": "Supported."}, map[string]any{}}} {
		v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["rationale_required_propositions"] = propositions
		normalizeMutationOutput(v)
		if _, exists := u["rationale"]; exists {
			t.Fatal("Invented rationale", u)
		}
	}
	for _, explicit := range []any{nil, "Already authored."} {
		v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["rationale"] = explicit
		u["rationale_required_propositions"] = []any{map[string]any{"description": "Supplied."}}
		normalizeMutationOutput(v)
		if u["rationale"] != explicit {
			t.Fatal("Changed explicit field", u)
		}
	}
}

func TestReleaseMutationUtteranceProjectionPositive(t *testing.T) {
	v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["text_spans"] = []any{map[string]any{"utterance_id": "u2"}, map[string]any{"utterance_id": "u1"}, map[string]any{"utterance_id": "u2"}}
	normalizeMutationOutput(v)
	ids := u["utterance_ids"].([]any)
	if len(ids) != 2 || ids[0] != "u2" || ids[1] != "u1" {
		t.Fatal(u)
	}
}
func TestReleaseMutationUtteranceProjectionNegative(t *testing.T) {
	for _, spans := range []any{nil, []any{}, []any{map[string]any{}}, []any{map[string]any{"utterance_id": "u1"}, nil}} {
		v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["text_spans"] = spans
		normalizeMutationOutput(v)
		if _, ok := u["utterance_ids"]; ok {
			t.Fatal("Invented turn association", u)
		}
	}
	v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["utterance_ids"] = nil
	normalizeMutationOutput(v)
	if u["utterance_ids"] != nil {
		t.Fatal(u)
	}
}
