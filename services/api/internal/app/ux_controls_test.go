package app

import (
	"encoding/json"
	"net/http/httptest"
	"reflect"
	"testing"
)

func TestUXCatalogPositive(t *testing.T) {
	s := &Server{Origin: "http://localhost:3000", token: "ux-owned-test"}
	r := httptest.NewRequest("GET", "/api/v1/preparation-options", nil)
	r.Header.Set("Authorization", "Bearer ux-owned-test")
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	var v struct {
		Version    string                `json:"taxonomy_version"`
		Categories []preparationCategory `json:"categories"`
	}
	if e := json.Unmarshal(w.Body.Bytes(), &v); e != nil {
		t.Fatal(e)
	}
	if len(v.Categories) != 122 || v.Version != "1.2.0" {
		t.Fatal(len(v.Categories), v.Version)
	}
	expected := linguisticReferences(t)
	ids := map[string]bool{}
	for _, c := range v.Categories {
		if c.Label == "" || c.Description == "" || ids[c.ID] {
			t.Fatal(c)
		}
		ids[c.ID] = true
	}
	for _, c := range expected {
		if !ids[c.ID] {
			t.Fatal("missing category", c.ID)
		}
	}
}

func TestUXCatalogControlsNegative(t *testing.T) {
	rows, _, e := preparationCategories()
	if e != nil {
		t.Fatal(e)
	}
	controls := 0
	for _, c := range rows {
		if c.Control {
			controls++
			if c.Family != "acceptable_variant" {
				t.Fatal(c)
			}
		} else if c.Family == "acceptable_variant" {
			t.Fatal("control presented as error", c)
		}
	}
	if controls != 8 {
		t.Fatal(controls)
	}
	s := &Server{Origin: "http://localhost:3000", token: "ux-owned-test"}
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, httptest.NewRequest("GET", "/api/v1/preparation-options", nil))
	if w.Code != 403 {
		t.Fatal("private API exposed", w.Code)
	}
}

func TestUXExactSelectionNegative(t *testing.T) {
	a, _ := generationRegistry("error-taxonomy.v1.yaml")
	r, _ := generationRegistry("mutation-recipes.v1.json")
	p, _ := generationRegistry("acoustic-production.v1.json")
	b := map[string]any{"targets": []any{}, "exercise_request": map[string]any{"category_families": []any{}, "category_ids": []any{"lexis.collocation", "pragmatics_register.formality"}}}
	tax, recipes, _, e := mutationSelection(b, a, r, p)
	if e != nil {
		t.Fatal(e)
	}
	got := []string{}
	for _, x := range tax["entries"].([]any) {
		got = append(got, x.(map[string]any)["id"].(string))
	}
	if !reflect.DeepEqual(got, []string{"lexis.collocation", "pragmatics_register.formality"}) || len(recipes) != 2 {
		t.Fatal(got, len(recipes))
	}
	b["exercise_request"].(map[string]any)["category_ids"] = []any{"invented.category"}
	if _, _, _, e = mutationSelection(b, a, r, p); e == nil {
		t.Fatal("unknown exact category accepted")
	}
	base, clean, c, _ := mutationFixture()
	if e = admitMutation(t, base, clean, c, tax); e == nil {
		t.Fatal("unselected grammar error accepted")
	}
}

func TestUXSeverityPositive(t *testing.T) {
	for severity, weight := range map[string]float64{"minor": 1, "moderate": 2, "major": 3, "communication_breakdown": 4} {
		b, clean, c, tax := mutationFixture()
		b["exercise_request"].(map[string]any)["severity_levels"] = []any{severity}
		u := c["planned_units"].([]any)[0].(map[string]any)
		u["severity"], u["weight"] = severity, weight
		if e := admitMutation(t, b, clean, c, tax); e != nil {
			t.Fatal(severity, e)
		}
	}
	input := []byte(`{"exercise_request":{"topic":"Making decisions","speaker_count":2,"text_length_words":200,"category_ids":["lexis.collocation"],"severity_levels":["minor"],"mutation_count":4}}`)
	b, e := ExpandBlueprint(input, DefaultConfiguration())
	if e != nil {
		t.Fatal(e)
	}
	r := b["exercise_request"].(map[string]any)
	if !reflect.DeepEqual(r["category_ids"], []any{"lexis.collocation"}) || !reflect.DeepEqual(r["severity_levels"], []any{"minor"}) || r["mutation_count"] != float64(4) {
		t.Fatal(r)
	}
}

func TestUXSeverityRejectedNegative(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	b["exercise_request"].(map[string]any)["severity_levels"] = []any{"minor", "moderate"}
	u := c["planned_units"].([]any)[0].(map[string]any)
	u["severity"], u["weight"] = "major", float64(3)
	if e := admitMutation(t, b, clean, c, tax); e == nil {
		t.Fatal("unrequested major severity accepted")
	}
	if clean["utterances"].([]any)[0].(map[string]any)["surface_text"] != "The café opens tomorrow." {
		t.Fatal("clean checkpoint changed")
	}
	if _, e := ExpandBlueprint([]byte(`{"exercise_request":{"topic":"Travel","speaker_count":1,"text_length_words":100,"severity_levels":["extreme"]}}`), DefaultConfiguration()); e == nil {
		t.Fatal("invented severity accepted")
	}
}

func TestUXSeverityLegacyPositive(t *testing.T) {
	for _, empty := range []bool{false, true} {
		b, clean, c, tax := mutationFixture()
		if empty {
			b["exercise_request"].(map[string]any)["severity_levels"] = []any{}
		}
		if e := admitMutation(t, b, clean, c, tax); e != nil {
			t.Fatal(e)
		}
	}
}

func TestUXSeverityZeroPositive(t *testing.T) {
	b, clean, c, tax := mutationFixture()
	r := b["exercise_request"].(map[string]any)
	r["mutation_count"] = float64(0)
	r["severity_levels"] = []any{"minor"}
	r["category_ids"] = []any{"grammar.verbs.subject_verb_agreement"}
	c["utterances"], c["planned_units"] = clean["utterances"], []any{}
	if e := admitMutation(t, b, clean, c, tax); e != nil {
		t.Fatal(e)
	}
}

func TestUXAcousticSelectionPositive(t *testing.T) {
	b := map[string]any{"targets": []any{}, "exercise_request": map[string]any{"category_families": []any{}, "category_ids": []any{"pronunciation.segmental.consonant_substitution"}}}
	if !acousticRequested(b) {
		t.Fatal("exact pronunciation request lost")
	}
	if e := requestedAcousticCapability(b, map[string]any{"provider": "local_kokoro", "adapter_version": "kokoro-controlled-v1"}); e != nil {
		t.Fatal(e)
	}
}

func TestUXAcousticSelectionNegative(t *testing.T) {
	b := map[string]any{"targets": []any{}, "exercise_request": map[string]any{"category_families": []any{}, "category_ids": []any{"lexis.collocation", "pragmatics_register.formality"}}}
	if acousticRequested(b) {
		t.Fatal("text-only categories became an acoustic request")
	}
	b["exercise_request"].(map[string]any)["category_ids"] = []any{"pronunciation.segmental.consonant_substitution"}
	if e := requestedAcousticCapability(b, map[string]any{"provider": "local_kokoro", "adapter_version": "kokoro-local-en-v1"}); e == nil {
		t.Fatal("plain adapter accepted explicit acoustic requirement")
	}
}

func TestUXCheckpointProjectionPositive(t *testing.T) {
	raw := []byte(`{"exercise_request":{"category_ids":["lexis.collocation"],"severity_levels":["minor"]}}`)
	if e := validateProjection(DocumentWrite{ID: "checkpoint", Kind: "preparation-state"}, raw); e != nil {
		t.Fatal("registry category label became a document reference", e)
	}
}

func TestUXCheckpointProjectionNegative(t *testing.T) {
	raw := []byte(`{"exercise_request":{"category_ids":["lexis.collocation"]},"settings_asset_id":"missing-settings"}`)
	if e := validateProjection(DocumentWrite{ID: "checkpoint", Kind: "preparation-state"}, raw); e == nil {
		t.Fatal("actual settings association was dropped with the taxonomy-label exemption")
	}
}
