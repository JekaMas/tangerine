package app

import (
	"context"
	"encoding/json"
	"net/http"
	"tangerine.local/api/internal/empirical"
	"testing"
)

// Independent constructed input. It needs no imported corpus, learner or LLM.
func i38HTTPInput() EmpiricalSubmission {
	three, two := int64(3), int64(2)
	leaf := "lexis.collocation"
	return EmpiricalSubmission{Title: "Constructed report recovery", Input: empirical.Input{
		Population: empirical.Population{Release: "constructed", View: "two sentences", Window: "sentence", Origin: "constructed"},
		Leaves:     []string{leaf}, Windows: []empirical.Window{
			{ID: "one", Annotated: true, Tokens: &three, Events: []empirical.Event{{ID: "one/0", Native: "authored", Leaf: &leaf}}},
			{ID: "two", Annotated: true, Tokens: &two},
		},
	}}
}

func TestImportedHTTPValidationNegative(t *testing.T) {
	f := sourceFixture(t)
	good := f.request(http.MethodPost, "/api/v1/reports/empirical", sourceBytes(i38HTTPInput()), "", "")
	sourceAssert(t, http.StatusCreated, good.Code)
	var saved map[string]any
	sourceRequire(t, json.Unmarshal(good.Body.Bytes(), &saved))
	for _, tc := range []struct {
		name string
		edit func(*EmpiricalSubmission)
	}{
		{"missing population", func(v *EmpiricalSubmission) { v.Input.Population.Release = "" }},
		{"duplicate windows", func(v *EmpiricalSubmission) { v.Input.Windows[1].ID = "one" }},
		{"unknown mapped category", func(v *EmpiricalSubmission) { id := "unknown"; v.Input.Windows[0].Events[0].Leaf = &id }},
		{"invalid opportunities", func(v *EmpiricalSubmission) {
			v.Input.Windows[0].Opportunities = map[string]int64{"lexis.collocation": -1}
		}},
		{"duplicate attempt", func(v *EmpiricalSubmission) { v.Attempts = []empirical.Attempt{{ID: "duplicate"}, {ID: "duplicate"}} }},
	} {
		t.Run(tc.name, func(t *testing.T) {
			input := i38HTTPInput()
			tc.edit(&input)
			response := f.request(http.MethodPost, "/api/v1/reports/empirical", sourceBytes(input), "", "")
			if response.Code != http.StatusBadRequest {
				t.Fatalf("invalid report input must be a correctable HTTP 400, got %d: %s", response.Code, response.Body.String())
			}
			sourceAssert(t, "{\"error\":\"source_input_invalid\"}\n", response.Body.String())
		})
	}
	sourceAssert(t, 1, len(mustI38Reports(t, f.s.Store)))
	read := f.request(http.MethodGet, "/api/v1/reports/empirical/"+saved["id"].(string), nil, "", "")
	sourceAssert(t, http.StatusOK, read.Code)
	sourceAssert(t, good.Body.String(), read.Body.String())
}

func TestImportedHTTPRecoveryPositive(t *testing.T) {
	f := sourceFixture(t)
	first := f.request(http.MethodPost, "/api/v1/reports/empirical", sourceBytes(i38HTTPInput()), "", "")
	sourceAssert(t, http.StatusCreated, first.Code)
	var saved map[string]any
	sourceRequire(t, json.Unmarshal(first.Body.Bytes(), &saved))
	ctx := context.Background()
	_, err := f.s.Store.DB.Exec(ctx, "ALTER TABLE empirical_report RENAME TO i38_temporarily_unavailable_report")
	sourceRequire(t, err)
	failed := f.request(http.MethodPost, "/api/v1/reports/empirical", sourceBytes(i38HTTPInput()), "", "")
	// An actual storage failure must remain a service error, not input blame.
	sourceAssert(t, http.StatusServiceUnavailable, failed.Code)
	_, err = f.s.Store.DB.Exec(ctx, "ALTER TABLE i38_temporarily_unavailable_report RENAME TO empirical_report")
	sourceRequire(t, err)
	read := f.request(http.MethodGet, "/api/v1/reports/empirical/"+saved["id"].(string), nil, "", "")
	sourceAssert(t, http.StatusOK, read.Code)
	sourceAssert(t, first.Body.String(), read.Body.String())
	second := f.request(http.MethodPost, "/api/v1/reports/empirical", sourceBytes(i38HTTPInput()), "", "")
	sourceAssert(t, http.StatusCreated, second.Code)
	sourceAssert(t, 2, len(mustI38Reports(t, f.s.Store)))
	var calls int
	sourceRequire(t, f.s.Store.DB.QueryRow(ctx, "SELECT count(*) FROM document WHERE kind='provider-receipt'").Scan(&calls))
	sourceAssert(t, 0, calls)
}

func TestImportedHTTPSourceSelectionNegative(t *testing.T) {
	f, run := i38Fixture(t)
	input := i38HTTPInput()
	input.Source = &EmpiricalSource{Import: run.Report.ID, Member: "fce/m2/fce.train.gold.bea19.m2", Table: "edits"}
	bad := f.request(http.MethodPost, "/api/v1/reports/empirical", sourceBytes(input), "", "")
	sourceAssert(t, http.StatusBadRequest, bad.Code)
	sourceAssert(t, "{\"error\":\"source_input_invalid\"}\n", bad.Body.String())
	// Correcting the legacy selector works without a review or another import.
	input.Source.Table = "sentences"
	good := f.request(http.MethodPost, "/api/v1/reports/empirical", sourceBytes(input), "", "")
	sourceAssert(t, http.StatusCreated, good.Code)
	sourceAssert(t, 1, len(mustI38Reports(t, f.s.Store)))
}
