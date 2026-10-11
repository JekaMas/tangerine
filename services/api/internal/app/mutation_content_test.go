package app

import (
	"encoding/json"
	"fmt"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/provider"
	"testing"
)

func mutationFixture() (map[string]any, map[string]any, map[string]any, map[string]any) {
	blueprint := map[string]any{"id": "b1", "targets": []any{}, "exercise_request": map[string]any{"category_families": []any{"grammar"}, "mutation_count": float64(1)}}
	clean := map[string]any{"schema_version": "1.0.0", "blueprint_id": "b1", "status": "candidate", "failure_reason": nil, "utterances": []any{map[string]any{"id": "u1", "speaker_id": "s1", "canonical_text": "The café opens tomorrow.", "surface_text": "The café opens tomorrow."}}, "planned_units": []any{}, "acoustic_edits": []any{}}
	raw, _ := json.Marshal(clean)
	var candidate map[string]any
	_ = json.Unmarshal(raw, &candidate)
	candidate["utterances"].([]any)[0].(map[string]any)["surface_text"] = "The café open tomorrow."
	realization := map[string]any{"mode": "textual", "canonical_text": "opens", "surface_text": "open", "canonical_ipa": nil, "intended_ipa": nil, "observed_ipa": nil, "prosody": []any{}, "pace_target_wpm": nil, "observed_pace_wpm": nil, "planned_pause_ms": nil, "observed_pause_ms": nil}
	correction := map[string]any{"id": "r1", "kind": "replace", "text": "opens", "ipa": nil, "approved_text_alternatives": []any{}, "case_insensitive": false, "terminal_period_insensitive": false, "variety_constraints": []any{}, "required_propositions": []any{map[string]any{"id": "p1", "description": "Singular subject agrees with opens."}}, "forbidden_propositions": []any{}, "canonical": true}
	unit := map[string]any{"id": "e1", "primary_taxonomy_id": "grammar.verbs.subject_verb_agreement", "accepted_taxonomy_ids": []any{"grammar.verbs.subject_verb_agreement"}, "secondary_taxonomy_ids": []any{}, "domain": "grammar", "expected_judgment": "true_error", "status_label": "unequivocal_error", "utterance_ids": []any{"u1"}, "text_spans": []any{map[string]any{"utterance_id": "u1", "span": map[string]any{"start_cp": float64(9), "end_cp": float64(13), "exact_text": "open"}}}, "realization": realization, "severity": "moderate", "weight": float64(2), "difficulty": "unrated", "correction_eligible": true, "corrections": []any{correction}, "explanation_eligible": true, "rationale_required_propositions": []any{map[string]any{"id": "p1", "description": "A singular subject requires singular agreement."}}, "rationale_forbidden_propositions": []any{}, "rationale": "The singular café requires opens."}
	candidate["planned_units"] = []any{unit}
	taxonomy := map[string]any{"entries": []any{map[string]any{"id": unit["primary_taxonomy_id"], "domain": "grammar"}}}
	return blueprint, clean, candidate, taxonomy
}
func admitMutation(t *testing.T, b, clean, c, tax map[string]any) error {
	t.Helper()
	raw, _ := json.Marshal(c)
	if _, _, e := contracts.Validate("case-candidate", "1.0.0", raw); e != nil {
		return e
	}
	_, e := mutationContent(raw, b, clean, tax)
	return e
}
func TestMutationAdmissionPositive(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}
func TestMutationEmptyKeyPositive(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	b["exercise_request"].(map[string]any)["mutation_count"] = float64(0)
	c["utterances"] = clean["utterances"]
	c["planned_units"] = []any{}
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}
func TestMutationBaselineNegative(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	c["utterances"].([]any)[0].(map[string]any)["canonical_text"] = "A different story."
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("rewritten baseline accepted")
	}
}
func TestMutationLocationNegative(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	c["planned_units"].([]any)[0].(map[string]any)["text_spans"].([]any)[0].(map[string]any)["span"].(map[string]any)["start_cp"] = float64(10)
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("stale surface span accepted")
	}
}
func TestMutationManifestPositive(t *testing.T) {
	_, clean, c, _ := mutationFixture()
	m := mutationManifest(c, "clean", strings.Repeat("a", 64), "mutated", strings.Repeat("b", 64), strings.Repeat("c", 64), nil, nil)
	raw, _ := json.Marshal(m)
	if _, _, e := contracts.Validate("mutation-manifest", "2.0.0", raw); e != nil {
		t.Fatal(e)
	}
	edits := m["edits"].([]any)
	if len(edits) != 1 || edits[0].(map[string]any)["start_cp"] != 13 || edits[0].(map[string]any)["original_text"] != "s" || edits[0].(map[string]any)["replacement_text"] != "" {
		t.Fatal(edits)
	}
	text, e := ReplayMutation(clean["utterances"].([]any)[0].(map[string]any)["canonical_text"].(string), edits)
	if e != nil || text != "The café open tomorrow." {
		t.Fatal(text, e)
	}
	if m["canonical_word_count"] != 4 || m["surface_word_count"] != 4 {
		t.Fatal(m)
	}
}
func TestMutationUnicodeInsertPositive(t *testing.T) {
	_, _, c, _ := mutationFixture()
	c["utterances"].([]any)[0].(map[string]any)["surface_text"] = "🙂The café opens tomorrow."
	m := mutationManifest(c, "a", strings.Repeat("a", 64), "b", strings.Repeat("b", 64), strings.Repeat("c", 64), nil, float64(17))
	text, e := ReplayMutation("The café opens tomorrow.", m["edits"].([]any))
	if e != nil || text != "🙂The café opens tomorrow." || m["edits"].([]any)[0].(map[string]any)["end_cp"] != 0 {
		t.Fatal(text, m, e)
	}
}
func TestMutationUnknownCategoryNegative(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	c["planned_units"].([]any)[0].(map[string]any)["primary_taxonomy_id"] = "invented.leaf"
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("invented category accepted")
	}
}
func TestMutationCountNegative(t *testing.T) {
	{
		b, clean, c, tax := mutationFixture()
		c["planned_units"].([]any)[0].(map[string]any)["explanation_eligible"] = false
		if e := admitMutation(t, b, clean, c, tax); e == nil {
			t.Fatal("optional listener explanation cannot disable a generated error's rubric")
		}
	}

	duplicated := `{"schema_version":"1.0.0","blueprint_id":"b1","status":"candidate","failure_reason":null,"utterances":[],"planned_units":[],"schema_version":"1.0.0"}`
	if _, e := provider.ProjectVisible(duplicated, "case-candidate"); e == nil || !strings.Contains(e.(*provider.OutputValidationError).Detail, "duplicate") {
		t.Fatal("independent duplicate-root repair detail", e)
	}

	b, clean, c, tax := mutationFixture()
	b["exercise_request"].(map[string]any)["mutation_count"] = float64(2)
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("wrong requested count accepted")
	}
	b, clean, c, tax = mutationFixture()
	c["planned_units"].([]any)[0].(map[string]any)["rationale_required_propositions"] = []any{}
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("eligible explanation admitted with a zero-required rubric")
	}
	b, clean, c, tax = mutationFixture()
	c["planned_units"].([]any)[0].(map[string]any)["corrections"].([]any)[0].(map[string]any)["required_propositions"] = []any{}
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("eligible correction admitted with a zero-required rubric")
	}
	b, clean, c, tax = mutationFixture()
	c["planned_units"].([]any)[0].(map[string]any)["corrections"].([]any)[0].(map[string]any)["text"] = "open"
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("literal no-op offered as a true textual repair")
	}
	b, clean, c, tax = mutationFixture()
	unit := c["planned_units"].([]any)[0].(map[string]any)
	unit["rationale_required_propositions"] = []any{}
	delete(unit["text_spans"].([]any)[0].(map[string]any), "utterance_id")
	raw, _ := json.Marshal(c)
	_, e := provider.ProjectVisible(string(raw), "case-candidate")
	detail, ok := e.(*provider.OutputValidationError)
	if !ok || !strings.Contains(detail.Detail, "utterance_id") || !strings.Contains(detail.Detail, "rationale_required_propositions") {
		t.Fatal("single admission omitted simultaneous key defects", e)
	}
}
func TestMutationRegistryPositive(t *testing.T) {
	b, _, _, _ := mutationFixture()
	b["exercise_request"].(map[string]any)["category_families"] = []any{}
	a, _ := generationRegistry("error-taxonomy.v1.yaml")
	r, _ := generationRegistry("mutation-recipes.v1.json")
	p, _ := generationRegistry("acoustic-production.v1.json")
	tax, recipes, production, e := mutationSelection(b, a, r, p)
	if e != nil || len(tax["entries"].([]any)) != 122 || len(recipes) != 122 || len(production) != 122 {
		t.Fatal(tax, e, len(recipes), len(production))
	}
}
func TestMutationFamilyPositive(t *testing.T) {
	b, _, _, _ := mutationFixture()
	a, _ := generationRegistry("error-taxonomy.v1.yaml")
	r, _ := generationRegistry("mutation-recipes.v1.json")
	p, _ := generationRegistry("acoustic-production.v1.json")
	tax, recipes, _, e := mutationSelection(b, a, r, p)
	if e != nil || len(recipes) == 0 {
		t.Fatal(e)
	}
	for _, v := range tax["entries"].([]any) {
		if v.(map[string]any)["domain"] != "grammar" {
			t.Fatal(v)
		}
	}
}
func TestMutationFamilyNegative(t *testing.T) {
	b, _, _, _ := mutationFixture()
	b["exercise_request"].(map[string]any)["category_families"] = []any{"invented"}
	a, _ := generationRegistry("error-taxonomy.v1.yaml")
	r, _ := generationRegistry("mutation-recipes.v1.json")
	p, _ := generationRegistry("acoustic-production.v1.json")
	if _, _, _, e := mutationSelection(b, a, r, p); e == nil {
		t.Fatal("unknown family accepted")
	}
}
func TestMutationReplayNegative(t *testing.T) {
	_, _, c, _ := mutationFixture()
	m := mutationManifest(c, "a", strings.Repeat("a", 64), "b", strings.Repeat("b", 64), strings.Repeat("c", 64), nil, nil)
	m["edits"].([]any)[0].(map[string]any)["original_text"] = "x"
	if _, e := ReplayMutation("The café opens tomorrow.", m["edits"].([]any)); e == nil {
		t.Fatal("invalid new edit accepted")
	}
}

func acousticMutationFixture() (map[string]any, map[string]any, map[string]any, map[string]any) {
	b, clean, c, tax := mutationFixture()
	c["utterances"] = clean["utterances"]
	u := c["planned_units"].([]any)[0].(map[string]any)
	u["primary_taxonomy_id"] = "pronunciation.segmental.consonant_voicing"
	u["accepted_taxonomy_ids"] = []any{u["primary_taxonomy_id"]}
	u["domain"] = "pronunciation.segmental"
	u["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(9), "end_cp": float64(14), "exact_text": "opens"}
	r := u["realization"].(map[string]any)
	r["mode"] = "acoustic_segmental"
	r["canonical_text"] = "opens"
	r["surface_text"] = "opens"
	r["canonical_ipa"] = "oʊpənz"
	r["intended_ipa"] = "oʊpəns"
	tax["entries"] = []any{map[string]any{"id": u["primary_taxonomy_id"], "domain": u["domain"]}}
	c["acoustic_edits"] = []any{map[string]any{"unit_id": "e1", "utterance_id": "u1", "scope": map[string]any{"start": float64(9), "end": float64(14)}, "controller": "phone_pair", "parameters": map[string]any{"duration_ratio": nil, "gain_db": nil, "pitch_points": []any{}, "pause_ms": nil, "vot_ms": nil, "reference_ipa": "oʊpənz", "mutated_ipa": "oʊpəns", "phone_start": float64(4), "phone_end": float64(5), "expected_feature": "final z to s", "accepted_reference": "final z"}}}
	return b, clean, c, tax
}
func TestMutationAcousticPositive(t *testing.T) {
	b, clean, c, tax := acousticMutationFixture()
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
	m := mutationManifest(c, "a", strings.Repeat("a", 64), "b", strings.Repeat("b", 64), strings.Repeat("c", 64), nil, nil)
	if len(m["edits"].([]any)) != 0 || len(m["acoustic_intents"].([]any)) != 1 || len(m["acoustic_edits"].([]any)) != 1 {
		t.Fatal(m)
	}
	if m["acoustic_intents"].([]any)[0].(map[string]any)["realization"].(map[string]any)["observed_ipa"] != nil {
		t.Fatal(m)
	}
}
func TestMutationControlPositive(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	c["utterances"] = clean["utterances"]
	b["exercise_request"].(map[string]any)["mutation_count"] = float64(0)
	u := c["planned_units"].([]any)[0].(map[string]any)
	u["expected_judgment"] = "acceptable"
	u["status_label"] = "decoy_non_error"
	u["correction_eligible"] = false
	u["corrections"] = []any{}
	u["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(9), "end_cp": float64(14), "exact_text": "opens"}
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}
func TestMutationAcousticMissingNegative(t *testing.T) {
	b, clean, c, tax := acousticMutationFixture()
	c["acoustic_edits"] = []any{}
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("unsupported acoustic intent accepted without operation")
	}
}
func TestMutationObservedSoundNegative(t *testing.T) {
	b, clean, c, tax := acousticMutationFixture()
	c["planned_units"].([]any)[0].(map[string]any)["realization"].(map[string]any)["observed_ipa"] = "fabricated"
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("unmeasured sound accepted")
	}
}

// ReplayMutation is an independent test-only ledger replay; it is not shipped.
func ReplayMutation(text string, edits []any) (string, error) {
	runes := []rune(text)
	position := 0
	var out strings.Builder
	for _, v := range edits {
		e := v.(map[string]any)
		start, end := mutationOffset(e["start_cp"]), mutationOffset(e["end_cp"])
		if start < position || start > end || end > len(runes) || string(runes[start:end]) != e["original_text"] {
			return "", fmt.Errorf("invalid canonical edit")
		}
		out.WriteString(string(runes[position:start]))
		out.WriteString(e["replacement_text"].(string))
		position = end
	}
	out.WriteString(string(runes[position:]))
	return out.String(), nil
}
func mutationOffset(v any) int {
	switch x := v.(type) {
	case int:
		return x
	case float64:
		return int(x)
	}
	return -1
}

func TestMutationMultipleScopesPositive(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	c["utterances"].([]any)[0].(map[string]any)["surface_text"] = "The café open tomorrows."
	u := c["planned_units"].([]any)[0].(map[string]any)
	u["text_spans"] = append(u["text_spans"].([]any), map[string]any{"utterance_id": "u1", "span": map[string]any{"start_cp": float64(14), "end_cp": float64(23), "exact_text": "tomorrows"}})
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}

func TestMutationDeletionBoundaryPositive(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	u := c["planned_units"].([]any)[0].(map[string]any)
	u["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(13), "end_cp": float64(13), "exact_text": ""}
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}

func TestMutationUnattributedNegative(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	c["utterances"].([]any)[0].(map[string]any)["surface_text"] = "The café open tomorrows."
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("unlisted tomorrows change accepted with only the open key")
	}
}

func TestMutationUnchangedScopeNegative(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	c["utterances"].([]any)[0].(map[string]any)["surface_text"] = "A café open tomorrow!"
	u := c["planned_units"].([]any)[0].(map[string]any)
	u["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(12), "end_cp": float64(20), "exact_text": "tomorrow"}
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("unchanged tomorrow span cannot attribute surrounding edits")
	}
}

func TestMutationAcousticSubscopePositive(t *testing.T) {
	b, clean, c, tax := acousticMutationFixture()
	c["planned_units"].([]any)[0].(map[string]any)["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(0), "end_cp": float64(24), "exact_text": "The café opens tomorrow."}
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}

func TestMutationPauseParametersPositive(t *testing.T) {
	for _, controller := range []string{"vowel_duration", "pitch_duration", "pause_insert", "vot_edit"} {
		b, clean, c, tax := acousticMutationFixture()
		edit := c["acoustic_edits"].([]any)[0].(map[string]any)
		edit["controller"] = controller
		p := edit["parameters"].(map[string]any)
		p["reference_ipa"], p["mutated_ipa"] = nil, nil
		switch controller {
		case "vowel_duration":
			p["duration_ratio"] = float64(0.45)
		case "pitch_duration":
			p["pitch_points"] = []any{map[string]any{"fraction": float64(0), "semitones": float64(1)}, map[string]any{"fraction": float64(1), "semitones": float64(3)}}
		case "pause_insert":
			p["pause_ms"] = float64(4000)
		case "vot_edit":
			p["vot_ms"] = float64(0)
		}
		if e := admitMutation(t, b, clean, c, tax); e != nil {
			t.Fatal(controller, e)
		}
	}
}

func TestMutationAcousticWrongScopeNegative(t *testing.T) {
	for _, otherTurn := range []bool{false, true} {
		b, clean, c, tax := acousticMutationFixture()
		edit := c["acoustic_edits"].([]any)[0].(map[string]any)
		if otherTurn {
			second := map[string]any{"id": "u2", "speaker_id": "s1", "canonical_text": "The café opens tomorrow.", "surface_text": "The café opens tomorrow."}
			c["utterances"] = append(c["utterances"].([]any), second)
			clean["utterances"] = c["utterances"]
			edit["utterance_id"] = "u2"
		} else {
			edit["scope"] = map[string]any{"start": float64(0), "end": float64(3)}
		}
		if e := admitMutation(t, b, clean, c, tax); e == nil {
			t.Fatal("acoustic operation outside its unit span accepted", otherTurn)
		}
	}
}

func TestMutationAcousticParametersNegative(t *testing.T) {
	for _, controller := range []string{"phone_pair", "vowel_duration", "pitch_duration", "pause_insert", "vot_edit"} {
		b, clean, c, tax := acousticMutationFixture()
		edit := c["acoustic_edits"].([]any)[0].(map[string]any)
		edit["controller"] = controller
		p := edit["parameters"].(map[string]any)
		p["reference_ipa"], p["mutated_ipa"] = nil, nil
		if e := admitMutation(t, b, clean, c, tax); e == nil {
			t.Fatal("controller accepted without its required operands", controller)
		}
	}
}
