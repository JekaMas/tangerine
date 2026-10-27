package app

import "testing"

func TestLocalMutationDerivedWeightPositive(t *testing.T) {
	for severity, want := range map[string]float64{"minor": 1, "moderate": 2, "major": 3, "communication_breakdown": 4} {
		v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["severity"] = severity
		normalizeMutationOutput(v)
		if u["weight"] != want {
			t.Fatal(severity, u)
		}
	}
}

func TestLocalMutationWeightExplicitNegative(t *testing.T) {
	for _, explicit := range []any{nil, float64(9), "1"} {
		v := projectionCandidate(t, "open", "open", 0, 4, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["severity"], u["weight"] = "minor", explicit
		normalizeMutationOutput(v)
		if u["weight"] != explicit {
			t.Fatal("explicit invalid weight concealed", u)
		}
	}
	v := projectionCandidate(t, "open", "open", 0, 4, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["severity"] = "invented"
	normalizeMutationOutput(v)
	if _, ok := u["weight"]; ok {
		t.Fatal("unknown severity guessed", u)
	}
}

func TestLocalMutationSuppliedRationalePositive(t *testing.T) {
	v := projectionCandidate(t, "The café open tomorrow.", "open", 9, 13, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["expected_judgment"], u["explanation_eligible"] = "true_error", false
	u["rationale"] = "The singular subject requires opens."
	u["rationale_required_propositions"] = []any{}
	normalizeMutationOutput(v)
	ps := u["rationale_required_propositions"].([]any)
	if u["explanation_eligible"] != true || len(ps) != 1 || ps[0].(map[string]any)["description"] != u["rationale"] {
		t.Fatal("supplied explanation was not projected verbatim", u)
	}
}

func TestLocalMutationRationaleUnknownNegative(t *testing.T) {
	for _, rationale := range []any{nil, "", 17} {
		v := projectionCandidate(t, "open", "open", 0, 4, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["expected_judgment"], u["explanation_eligible"], u["rationale"] = "true_error", false, rationale
		u["rationale_required_propositions"] = []any{}
		normalizeMutationOutput(v)
		if u["explanation_eligible"] != false || len(u["rationale_required_propositions"].([]any)) != 0 {
			t.Fatal("missing explanation invented", u)
		}
	}
	for _, judgment := range []string{"acceptable", "unknown"} {
		v := projectionCandidate(t, "open", "open", 0, 4, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["expected_judgment"], u["explanation_eligible"], u["rationale"] = judgment, false, "A supplied control explanation."
		u["rationale_required_propositions"] = []any{}
		normalizeMutationOutput(v)
		if u["explanation_eligible"] != false || len(u["rationale_required_propositions"].([]any)) != 0 {
			t.Fatal("non-error relabelled", u)
		}
	}
}

func TestLocalMutationExistingPropositionsPositive(t *testing.T) {
	v := projectionCandidate(t, "open", "open", 0, 4, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	u["expected_judgment"], u["explanation_eligible"] = "true_error", false
	u["rationale_required_propositions"] = []any{map[string]any{"id": "p1", "description": "The supplied explanation."}}
	normalizeMutationOutput(v)
	if u["explanation_eligible"] != true || u["rationale_required_propositions"].([]any)[0].(map[string]any)["id"] != "p1" {
		t.Fatal(u)
	}
}

func TestLocalMutationMalformedRationaleNegative(t *testing.T) {
	for _, explicit := range []any{nil, "unsupported"} {
		v := projectionCandidate(t, "open", "open", 0, 4, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		u["expected_judgment"], u["explanation_eligible"], u["rationale"] = "true_error", explicit, "Supplied explanation."
		u["rationale_required_propositions"] = nil
		normalizeMutationOutput(v)
		if u["explanation_eligible"] != explicit || u["rationale_required_propositions"] != nil {
			t.Fatal("malformed explicit fields coerced", u)
		}
	}
}

func TestLocalMutationExplicitSurfaceSpanPositive(t *testing.T) {
	v := projectionCandidate(t, "We have two book.", "two books", 8, 17, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	s := u["text_spans"].([]any)[0].(map[string]any)
	s["surface_span"] = map[string]any{"start_cp": float64(8), "end_cp": float64(16), "exact_text": "two book"}
	normalizeMutationOutput(v)
	if projectedSpan(v)["exact_text"] != "two book" || projectedSpan(v)["start_cp"] != float64(8) || projectedSpan(v)["end_cp"] != float64(16) {
		t.Fatal(v)
	}
}

func TestLocalMutationSurfaceSpanAmbiguityNegative(t *testing.T) {
	for _, surface := range []string{"two book and two book", "No matching wording."} {
		v := projectionCandidate(t, surface, "two books", 0, 9, "textual")
		u := v["planned_units"].([]any)[0].(map[string]any)
		s := u["text_spans"].([]any)[0].(map[string]any)
		s["surface_span"] = map[string]any{"start_cp": float64(0), "end_cp": float64(8), "exact_text": "two book"}
		normalizeMutationOutput(v)
		if projectedSpan(v)["exact_text"] != "two books" {
			t.Fatal("unknown final scope guessed", v)
		}
	}
	v := projectionCandidate(t, "We have two book.", "book", 12, 16, "textual")
	u := v["planned_units"].([]any)[0].(map[string]any)
	s := u["text_spans"].([]any)[0].(map[string]any)
	s["surface_span"] = map[string]any{"start_cp": float64(8), "end_cp": float64(16), "exact_text": "two book"}
	normalizeMutationOutput(v)
	if projectedSpan(v)["exact_text"] != "book" {
		t.Fatal("valid original scope changed", v)
	}
}
