package app

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/url"
	"os"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
	"testing"
)

func jflegFixtureRead(t *testing.T) map[string]string {
	t.Helper()
	b, e := os.ReadFile("/evidence/fixture.json")
	sourceRequire(t, e)
	var fixture map[string]string
	sourceRequire(t, json.Unmarshal(b, &fixture))
	if fixture["import_id"] == "" {
		t.Fatal("complete actual full import fixture absent")
	}
	return fixture
}
func jflegServer(t *testing.T) (*sourceNative, map[string]string) {
	t.Helper()
	s := jflegOpen(t)
	t.Cleanup(func() { s.DB.Close() })
	server := NewServer(s, "http://localhost:3000", "http://no-model.invalid")
	server.token = "source-owned-token"
	return &sourceNative{s: server}, jflegFixtureRead(t)
}
func TestNativeJFLEGConsumerPositive(t *testing.T) {
	f, fixture := jflegServer(t)
	ctx := context.Background()
	id := fixture["import_id"]
	before := jflegScalar(t, f.s.Store, "SELECT count(*) FROM source_import")
	statuses := f.request("GET", "/api/v1/sources", nil, "", "")
	sourceAssert(t, 200, statuses.Code)
	var items []map[string]any
	sourceRequire(t, json.Unmarshal(statuses.Body.Bytes(), &items))
	sourceAssert(t, 12, len(items))
	found := false
	for _, item := range items {
		_, _, e := contracts.Validate("source-status", "2.0.0", sourceBytes(item))
		sourceRequire(t, e)
		if item["source_id"] == "JFLEG" {
			found = true
			sourceAssert(t, "complete", item["status"])
			sourceAssert(t, true, item["normalized_complete"])
			sourceAssert(t, []any{}, item["missing_component_names"])
		}
	}
	if !found {
		t.Fatal("supplemental status missing")
	}
	// Saved source examples require no object-store read or integrity re-admission.
	media := f.s.Store.Media
	f.s.Store.Media = nil
	all, e := f.s.Store.SourceCorrectionDataset(ctx, id, "")
	sourceRequire(t, e)
	sourceAssert(t, 1501, len(all.Examples))
	f.s.Store.Media = media
	baseline := jflegBaselineRead(t)
	counts := map[string]int{}
	for part, want := range map[string]int{"dev": 754, "test": 747} {
		response := f.request("GET", "/api/v1/imports/"+id+"/corrections?format=dataset&partition="+part, nil, "", "")
		sourceAssert(t, 200, response.Code)
		if !strings.Contains(response.Header().Get("Content-Disposition"), "attachment") {
			t.Fatal("dataset did not download")
		}
		var dataset source.CorrectionDataset
		sourceRequire(t, json.Unmarshal(response.Body.Bytes(), &dataset))
		_, _, e := contracts.Validate("source-correction-dataset", "2.0.0", response.Body.Bytes())
		sourceRequire(t, e)
		sourceAssert(t, want, len(dataset.Examples))
		sourceAssert(t, "CC-BY-NC-SA-4.0", dataset.Licence)
		if !strings.Contains(dataset.Attribution, "Napoles") || !strings.Contains(dataset.Attribution, "Heilman") {
			t.Fatal("source-requested attribution missing", dataset.Attribution)
		}
		sourceAssert(t, jflegCommit, dataset.SourceVersion)
		counts[part] = len(dataset.Examples)
		for i, example := range dataset.Examples {
			sourceAssert(t, baseline.Lines[part+"/"+part+".src"][i], example.Original.Text)
			sourceAssert(t, 4, len(example.References))
			for j, reference := range example.References {
				sourceAssert(t, baseline.Lines[fmt.Sprintf("%s/%s.ref%d", part, part, j)][i], reference.Text)
			}
		}
	}
	rows, e := f.s.Store.DB.Query(ctx, "SELECT table_name,projection->'raw_metadata'->>'annotation_origin',count(*) FROM source_row WHERE import_id=$1 GROUP BY table_name,projection->'raw_metadata'->>'annotation_origin'", id)
	sourceRequire(t, e)
	origins := map[string]string{}
	for rows.Next() {
		var table, origin string
		var n int64
		sourceRequire(t, rows.Scan(&table, &origin, &n))
		origins[table] = origin
	}
	sourceRequire(t, rows.Err())
	rows.Close()
	sourceAssert(t, "source_tool_derivation", origins["edits"])
	sourceAssert(t, "source_annotation", origins["jfleg_ref0"])
	sourceAssert(t, "source_tool_derivation", origins["jfleg_spellchecked"])
	sourceAssert(t, "source_experimental_annotation", origins["records"])
	sourceAssert(t, int64(24), jflegScalar(t, f.s.Store, "SELECT count(*) FROM source_row WHERE import_id=$1 AND native_row->>'invalid'='true' AND projection->'raw_metadata'->>'tool_annotation_usable_as_gold'='false' AND state='metadata'", id))
	// Real corpus projection retains supplied text and has no invented audio/taxonomy.
	var corpus []byte
	sourceRequire(t, f.s.Store.DB.QueryRow(ctx, "SELECT corpus_record FROM source_row WHERE import_id=$1 AND table_name='jfleg_source' ORDER BY member,ordinal LIMIT 1", id).Scan(&corpus))
	var record map[string]any
	sourceRequire(t, json.Unmarshal(corpus, &record))
	sourceAssert(t, baseline.Lines["dev/dev.src"][0], record["text"])
	sourceAssert(t, "external_written", record["origin"])
	sourceAssert(t, nil, record["normalized_case_version_id"])
	sourceAssert(t, before, jflegScalar(t, f.s.Store, "SELECT count(*) FROM source_import"))
	jflegSave(t, "consumer-observations.json", map[string]any{"source_cards": 12, "jfleg_status": "complete", "download_counts": counts, "all_examples": 1501, "originals_checked": 1501, "reference_positions_checked": 6004, "origins": origins, "tool_findings_retained": 24, "readback_without_media": true, "readback_import_count_unchanged": true, "corpus_origin": record["origin"]})
}
func TestNativeJFLEGCursorPositive(t *testing.T) {
	f, fixture := jflegServer(t)
	id := fixture["import_id"]
	cursor := ""
	ids := map[string]bool{}
	pages := 0
	for {
		response := f.request("GET", "/api/v1/imports/"+id+"/corrections?limit=200&cursor="+url.QueryEscape(cursor), nil, "", "")
		sourceAssert(t, 200, response.Code)
		var page struct {
			Items []source.CorrectionExample `json:"items"`
			Next  string                     `json:"next_cursor"`
		}
		sourceRequire(t, json.Unmarshal(response.Body.Bytes(), &page))
		pages++
		for _, item := range page.Items {
			if ids[item.ID] {
				t.Fatal("duplicate paginated family", item.ID)
			}
			ids[item.ID] = true
		}
		if page.Next == "" {
			break
		}
		cursor = page.Next
	}
	sourceAssert(t, 1501, len(ids))
	sourceAssert(t, 8, pages)
	jflegSave(t, "cursor-observations.json", map[string]any{"pages": pages, "distinct_examples": len(ids), "includes_dev_0": ids["dev:0"], "includes_test_746": ids["test:746"]})
}
func TestNativeJFLEGConsumerNegative(t *testing.T) {
	f, fixture := jflegServer(t)
	id := fixture["import_id"]
	codes := map[string]int{}
	for name, suffix := range map[string]string{"cursor": "?cursor=not-json", "partition": "?partition=train"} {
		w := f.request("GET", "/api/v1/imports/"+id+"/corrections"+suffix, nil, "", "")
		sourceAssert(t, 400, w.Code)
		sourceAssert(t, "{\"error\":\"source_input_invalid\"}\n", w.Body.String())
		codes[name] = w.Code
	}
	w := f.request("GET", "/api/v1/imports/00000000-0000-4000-8000-000000000000/corrections", nil, "", "")
	sourceAssert(t, 404, w.Code)
	sourceAssert(t, "{\"error\":\"source_not_found\"}\n", w.Body.String())
	codes["missing"] = w.Code
	jflegSave(t, "consumer-negative.json", map[string]any{"statuses": codes, "safe_errors": true})
}
func TestNativeJFLEGPartialNegative(t *testing.T) {
	f := sourceFixture(t)
	f.upload(t, "owner/README.md", "Constructed incomplete JFLEG fixture; no acquired corpus claim.")
	f.upload(t, "owner/dev/dev.src", "They goes . \nSecond .\n")
	f.upload(t, "owner/dev/dev.ref0", "They go . \nSecond .\n")
	f.upload(t, "foreign/test/test.ref1", "Foreign .\n")
	f.upload(t, "owner/dev/dev.spellchecked.src", "They goes . \nSecond .\n")
	f.register(t, "JFLEG", "full_named_release")
	run := f.run(t, "native", nil)
	sourceAssert(t, false, run.Report.Normalized)
	if len(run.Report.FullMissing) == 0 {
		t.Fatal("partial example release claimed complete")
	}
	examples, _, e := f.s.Store.SourceCorrectionExamples(context.Background(), run.Report.ID, "", "dev", 20)
	sourceRequire(t, e)
	sourceAssert(t, 2, len(examples))
	sourceAssert(t, 1, len(examples[0].References))
	sourceAssert(t, "ref0", examples[0].References[0].ID)
	sourceAssert(t, "partial", examples[0].ReferenceCompleteness)
	sourceAssert(t, "They goes . ", examples[0].Original.Text)
	sourceAssert(t, "They goes . ", examples[0].Spellchecked.Text)
	// The foreign directory/partition does not supply a missing reference.
	sourceAssert(t, "Second .", examples[1].References[0].Text)
	jflegSave(t, "partial-observations.json", map[string]any{"normalized_complete": false, "full_missing": run.Report.FullMissing, "examples": examples, "constructed": true})
}
func TestNativeJFLEGLabPositive(t *testing.T) {
	f, fixture := jflegServer(t)
	ctx := context.Background()
	dataset, e := f.s.Store.SourceCorrectionDataset(ctx, fixture["import_id"], "")
	sourceRequire(t, e)
	baseline := jflegBaselineRead(t)
	outputs := []source.CorrectionOutput{}
	// Inputs and expectations come from the separately frozen native files, not
	// from the candidate-produced dataset or candidate difference algorithm.
	for _, part := range []string{"dev", "test"} {
		for i := range baseline.Lines[part+"/"+part+".src"] {
			for j := 0; j < 4; j++ {
				outputs = append(outputs, source.CorrectionOutput{Example: fmt.Sprintf("%s:%d", part, i), Text: baseline.Lines[fmt.Sprintf("%s/%s.ref%d", part, part, j)][i]})
			}
		}
	}
	command := map[string]any{"action": "source-correction-evaluate", "payload": source.CorrectionEvaluationRequest{Dataset: dataset, Outputs: outputs}}
	var result bytes.Buffer
	sourceRequire(t, f.s.Store.LabCommand(ctx, bytes.NewReader(sourceBytes(command)), &result))
	var saved struct {
		Report source.CorrectionEvaluation `json:"report"`
		Asset  string                      `json:"asset_id"`
		Input  string                      `json:"input_asset_id"`
		Calls  int                         `json:"provider_calls"`
	}
	sourceRequire(t, json.Unmarshal(result.Bytes(), &saved))
	sourceAssert(t, 0, saved.Calls)
	sourceAssert(t, 6004, saved.Report.Totals["reference_matches"])
	sourceAssert(t, 1501, saved.Report.Totals["logical_examples"])
	sourceAssert(t, 0, saved.Report.Totals["unsubmitted_examples"])
	sourceAssert(t, 6004, len(saved.Report.Rows))
	sourceAssert(t, "exact_native_text_v1", saved.Report.MatchPolicy)
	if saved.Input == "" {
		t.Fatal("evaluation input not retained")
	}
	sourceAssert(t, saved.Input, saved.Report.InputAsset)
	sourceAssert(t, jflegCommit, saved.Report.SourceVersion)
	sourceAssert(t, dataset.SourceManifest, saved.Report.SourceManifest)
	input, e := f.s.Store.ReadAsset(ctx, saved.Input)
	sourceRequire(t, e)
	var retained source.CorrectionEvaluationRequest
	sourceRequire(t, json.Unmarshal(input, &retained))
	sourceAssert(t, outputs, retained.Outputs)
	sourceAssert(t, dataset, retained.Dataset)
	for i, row := range saved.Report.Rows {
		native := outputs[i]
		parts := strings.Split(native.Example, ":")
		var ordinal int
		_, e := fmt.Sscanf(parts[1], "%d", &ordinal)
		sourceRequire(t, e)
		want := []string{}
		for j := 0; j < 4; j++ {
			if baseline.Lines[fmt.Sprintf("%s/%s.ref%d", parts[0], parts[0], j)][ordinal] == native.Text {
				want = append(want, fmt.Sprintf("ref%d", j))
			}
		}
		sourceAssert(t, want, row.Matched)
		sourceAssert(t, "reference_match", row.Status)
		sourceAssert(t, "not_run", row.SemanticJudgment)
	}
	raw, e := f.s.Store.ReadAsset(ctx, saved.Asset)
	sourceRequire(t, e)
	var readback source.CorrectionEvaluation
	sourceRequire(t, json.Unmarshal(raw, &readback))
	sourceAssert(t, saved.Report, readback)
	jflegSave(t, "evaluation-positive.json", map[string]any{"totals": saved.Report.Totals, "rows_checked": len(saved.Report.Rows), "asset_id": saved.Asset, "input_asset_id": saved.Input, "input_dataset_and_outputs_equal": true, "saved_report_readback_equal": true, "provider_calls": saved.Calls, "match_policy": saved.Report.MatchPolicy})
}
func TestNativeJFLEGLabNegative(t *testing.T) {
	f, fixture := jflegServer(t)
	ctx := context.Background()
	dataset, e := f.s.Store.SourceCorrectionDataset(ctx, fixture["import_id"], "dev")
	sourceRequire(t, e)
	dataset.Examples = dataset.Examples[:1]
	// A deliberately outside-reference alternative is unjudged, not incorrect.
	request := source.CorrectionEvaluationRequest{Dataset: dataset, Outputs: []source.CorrectionOutput{{Example: "dev:0", Text: "A different repair not supplied by this source."}, {Example: "unknown", Text: dataset.Examples[0].References[0].Text}}}
	var result bytes.Buffer
	sourceRequire(t, f.s.Store.LabCommand(ctx, bytes.NewReader(sourceBytes(map[string]any{"action": "source-correction-evaluate", "payload": request})), &result))
	var saved struct {
		Report source.CorrectionEvaluation `json:"report"`
		Calls  int                         `json:"provider_calls"`
	}
	sourceRequire(t, json.Unmarshal(result.Bytes(), &saved))
	sourceAssert(t, 0, saved.Calls)
	sourceAssert(t, 1, saved.Report.Totals["not_in_reference_set"])
	sourceAssert(t, 1, saved.Report.Totals["unknown_examples"])
	sourceAssert(t, "not_in_reference_set", saved.Report.Rows[0].Status)
	sourceAssert(t, "unknown_example", saved.Report.Rows[1].Status)
	for _, row := range saved.Report.Rows {
		sourceAssert(t, "not_run", row.SemanticJudgment)
		sourceAssert(t, []string{}, row.Matched)
	}
	if strings.Contains(result.String(), "incorrect") || strings.Contains(result.String(), "learner_score") {
		t.Fatal("reference membership presented as correctness grade")
	}
	// Fresh malformed external input is rejected once without creating a report.
	before := jflegScalar(t, f.s.Store, "SELECT count(*) FROM asset_location")
	if f.s.Store.LabCommand(ctx, strings.NewReader(`{"action":"source-correction-evaluate","payload":{"dataset":{},"outputs":[]}}`), &bytes.Buffer{}) == nil {
		t.Fatal("undocumented external payload admitted")
	}
	sourceAssert(t, before, jflegScalar(t, f.s.Store, "SELECT count(*) FROM asset_location"))
	jflegSave(t, "evaluation-negative.json", map[string]any{"report": saved.Report, "provider_calls": saved.Calls, "invalid_payload_no_asset": true, "incorrect_grade_absent": true})
}

func TestNativeJFLEGCompletenessPositive(t *testing.T) {
	f, fixture := jflegServer(t)
	ctx := context.Background()
	release, e := f.s.Store.SourceRelease(ctx, fixture["release_id"])
	sourceRequire(t, e)
	members, e := f.s.Store.sourceMembers(ctx, release.ID)
	sourceRequire(t, e)
	missing, e := f.s.Store.sourceFullMissing(ctx, release, fixture["import_id"], members)
	sourceRequire(t, e)
	sourceAssert(t, []string{}, missing)
	jflegSave(t, "completeness-positive.json", map[string]any{"missing": missing, "actual_import_id": fixture["import_id"], "source_assets_read": 0})
}
func TestNativeJFLEGCompletenessNegative(t *testing.T) {
	f, fixture := jflegServer(t)
	ctx := context.Background()
	release, e := f.s.Store.SourceRelease(ctx, fixture["release_id"])
	sourceRequire(t, e)
	members, e := f.s.Store.sourceMembers(ctx, release.ID)
	sourceRequire(t, e)
	// All real member names exist, but this unpopulated import has no normalized
	// rows. A full-source claim must include experimental data, not just names.
	missing, e := f.s.Store.sourceFullMissing(ctx, release, "unpopulated-test-owned-import", members)
	sourceRequire(t, e)
	text := strings.Join(missing, "\n")
	for _, want := range []string{"dev.ref.m2 sentences: expected 754, observed 0", "dev.ref.m2 edits: expected 11611, observed 0", "test.ref.m2 edits: expected 10938, observed 0", "coded_sentences.csv: expected 100, observed 0", "pairwise.csv: expected 1629, observed 0", "sample.csv: expected 4, observed 0"} {
		if !strings.Contains(text, want) {
			t.Fatalf("missing full-source condition %q in %v", want, missing)
		}
	}
	jflegSave(t, "completeness-negative.json", map[string]any{"missing": missing, "constructed_unpopulated_import": true, "actual_members": len(members)})
}
