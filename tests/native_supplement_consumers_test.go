package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"
)

func supplementFixtureRead(t *testing.T, name string) map[string]string {
	t.Helper()
	v := map[string]string{}
	supplementRead(t, name+"-fixture.json", &v)
	if v["import_id"] == "" {
		t.Fatal("Complete actual fixture missing", name)
	}
	return v
}
func supplementServer(t *testing.T) *sourceNative {
	t.Helper()
	s := supplementOpen(t)
	t.Cleanup(func() { s.DB.Close() })
	server := NewServer(s, "http://localhost:3000", "http://no-model.invalid")
	server.token = "source-owned-token"
	return &sourceNative{s: server}
}
func supplementPage(t *testing.T, f *sourceNative, id, cursor string) map[string]any {
	t.Helper()
	response := f.request("GET", "/api/v1/imports/"+id+"/examples?limit=20&cursor="+url.QueryEscape(cursor), nil, "", "")
	sourceAssert(t, 200, response.Code)
	var page map[string]any
	sourceRequire(t, json.Unmarshal(response.Body.Bytes(), &page))
	return page
}
func supplementFirst(t *testing.T, f *sourceNative, id string) map[string]any {
	t.Helper()
	page := supplementPage(t, f, id, "")
	items := page["items"].([]any)
	if len(items) == 0 {
		t.Fatal("Actual saved examples missing")
	}
	return items[0].(map[string]any)["projection"].(map[string]any)["source_example"].(map[string]any)
}
func TestNativeSupplementConsumerPositive(t *testing.T) {
	f := supplementServer(t)
	s := f.s.Store
	ctx := context.Background()
	out := map[string]any{}
	before := supplementScalar(t, s, "SELECT count(*) FROM source_import")
	statuses := f.request("GET", "/api/v1/sources", nil, "", "")
	sourceAssert(t, 200, statuses.Code)
	var cards []map[string]any
	sourceRequire(t, json.Unmarshal(statuses.Body.Bytes(), &cards))
	sourceAssert(t, 16, len(cards))
	for _, name := range []string{"edacc", "elrd", "diplomat", "dral-base", "dral-8"} {
		fixture := supplementFixtureRead(t, name)
		id := fixture["import_id"]
		run, e := s.SourceImport(ctx, id)
		sourceRequire(t, e)
		sourceAssert(t, "complete", run.Report.State)
		// The saved read owner works with no object-store client. It trusts DB projections.
		media := s.Media
		s.Media = nil
		page := supplementPage(t, f, id, "")
		s.Media = media
		items := page["items"].([]any)
		sourceAssert(t, 20, len(items))
		example := items[0].(map[string]any)["projection"].(map[string]any)["source_example"].(map[string]any)
		sourceAssert(t, fixture["source_id"], example["source_id"])
		sourceAssert(t, fixture["source_version"], example["source_version"])
		rangeObserved := false
		if name != "diplomat" {
			asset := example["media"].(map[string]any)["asset_id"].(string)
			request := httptest.NewRequest("GET", "/api/v1/sources/assets/"+asset+"/bytes", nil)
			request.Header.Set("Authorization", "Bearer source-owned-token")
			request.Header.Set("Range", "bytes=0-43")
			response := httptest.NewRecorder()
			f.s.Handler().ServeHTTP(response, request)
			sourceAssert(t, 206, response.Code)
			sourceAssert(t, "audio/wav", response.Header().Get("Content-Type"))
			sourceAssert(t, 44, response.Body.Len())
			sourceAssert(t, "RIFF", response.Body.String()[:4])
			if !strings.HasPrefix(response.Header().Get("Content-Range"), "bytes 0-43/") {
				t.Fatal("Actual stored WAVE range missing")
			}
			rangeObserved = true
		} else {
			sourceAssert(t, nil, example["media"])
			sourceAssert(t, nil, example["source_clock"])
		}
		out[name] = map[string]any{"page_examples": len(items), "next_cursor": page["next_cursor"], "read_without_media": true, "wave_range": rangeObserved, "first_example": example}
	}
	for _, card := range cards {
		switch card["source_id"] {
		case "EDACC", "ELRD", "DIPLOMAT", "DRAL":
			sourceAssert(t, "complete", card["status"])
			sourceAssert(t, true, card["normalized_complete"])
			sourceAssert(t, []any{}, card["missing_component_names"])
		}
	}
	sourceAssert(t, before, supplementScalar(t, s, "SELECT count(*) FROM source_import"))
	supplementSave(t, "consumer-observations.json", map[string]any{"source_cards": 16, "readback_import_count_unchanged": true, "sources": out})
}
func TestNativeSupplementConsumerNegative(t *testing.T) {
	f := supplementServer(t)
	missing := f.request("GET", "/api/v1/imports/00000000-0000-0000-0000-000000000037/examples", nil, "", "")
	sourceAssert(t, 404, missing.Code)
	for _, name := range []string{"edacc", "elrd", "diplomat", "dral-base", "dral-8"} {
		id := supplementFixtureRead(t, name)["import_id"]
		bad := f.request("GET", "/api/v1/imports/"+id+"/examples?cursor=broken", nil, "", "")
		sourceAssert(t, 400, bad.Code)
		if strings.Contains(bad.Body.String(), "SELECT") {
			t.Fatal("SQL exposed")
		}
	}
	supplementSave(t, "consumer-negative.json", map[string]any{"missing_import_status": 404, "invalid_cursor_status": 400, "sources_checked": 5, "raw_backend_detail": false})
}
func TestNativeSupplementCursorPositive(t *testing.T) {
	f := supplementServer(t)
	counts := map[string]any{}
	for _, name := range []string{"edacc", "elrd", "diplomat", "dral-base", "dral-8"} {
		id := supplementFixtureRead(t, name)["import_id"]
		first := supplementPage(t, f, id, "")
		second := supplementPage(t, f, id, first["next_cursor"].(string))
		seen := map[string]bool{}
		for _, page := range []map[string]any{first, second} {
			for _, raw := range page["items"].([]any) {
				v := raw.(map[string]any)
				key := fmt.Sprint(v["member"], v["table"], v["ordinal"])
				if seen[key] {
					t.Fatal("Cursor repeated an accepted native row")
				}
				seen[key] = true
			}
		}
		sourceAssert(t, 40, len(seen))
		counts[name] = len(seen)
	}
	supplementSave(t, "cursor-observations.json", counts)
}
func TestNativeSupplementFilesPositive(t *testing.T) {
	f := supplementServer(t)
	counts := map[string]int{}
	for name, want := range map[string]int{"edacc": 96, "elrd": 36, "diplomat": 19, "dral-base": 10498, "dral-8": 3086} {
		fixture := supplementFixtureRead(t, name)
		response := f.request("GET", "/api/v1/source-releases/"+fixture["release_id"]+"/files", nil, "", "")
		sourceAssert(t, 200, response.Code)
		var members []map[string]any
		sourceRequire(t, json.Unmarshal(response.Body.Bytes(), &members))
		sourceAssert(t, want, len(members))
		counts[name] = len(members)
		for _, member := range members {
			if id, ok := member["asset_id"].(string); !ok || id == "" {
				t.Fatal("Retained member is not accessible", member)
			}
		}
	}
	supplementSave(t, "file-observations.json", counts)
}
func TestNativeSupplementFilesNegative(t *testing.T) {
	f := supplementServer(t)
	response := f.request("GET", "/api/v1/source-releases/00000000-0000-0000-0000-000000000037/files", nil, "", "")
	sourceAssert(t, 404, response.Code)
	id := supplementFixtureRead(t, "edacc")["release_id"]
	response = f.request("GET", "/api/v1/source-releases/"+id+"/files", nil, "", "")
	var files []map[string]any
	sourceRequire(t, json.Unmarshal(response.Body.Bytes(), &files))
	found := false
	for _, file := range files {
		if strings.HasSuffix(file["relative_path"].(string), "evaluate.sh") {
			found = true
			download := f.request("GET", "/api/v1/sources/assets/"+file["asset_id"].(string)+"/bytes", nil, "", "")
			sourceAssert(t, 200, download.Code)
			sourceAssert(t, "attachment", download.Header().Get("Content-Disposition"))
			sourceAssert(t, "sandbox", download.Header().Get("Content-Security-Policy"))
			if download.Body.Len() == 0 {
				t.Fatal("Original inert script missing")
			}
		}
	}
	sourceAssert(t, true, found)
	supplementSave(t, "file-negative.json", map[string]any{"missing_release_status": 404, "script_download": "inert_attachment", "script_sandbox": true})
}
func TestNativeSupplementViewsPositive(t *testing.T) {
	f := supplementServer(t)
	counts := map[string]any{}
	for _, item := range []struct {
		name, view string
		want       int
	}{{"diplomat", "PIR_second_subtask_dataset", 20}, {"diplomat", "NLI_task_dataset", 20}, {"dral-8", "fragments-short", 20}, {"dral-8", "recordings", 20}} {
		id := supplementFixtureRead(t, item.name)["import_id"]
		response := f.request("GET", "/api/v1/imports/"+id+"/examples?limit=20&view="+item.view, nil, "", "")
		sourceAssert(t, 200, response.Code)
		var page struct {
			Items []map[string]any `json:"items"`
		}
		sourceRequire(t, json.Unmarshal(response.Body.Bytes(), &page))
		sourceAssert(t, item.want, len(page.Items))
		for _, row := range page.Items {
			e := row["projection"].(map[string]any)["source_example"].(map[string]any)
			v := e["task"]
			if v == nil {
				v = e["kind"]
			}
			sourceAssert(t, item.view, v)
		}
		counts[item.name+"/"+item.view] = len(page.Items)
	}
	supplementSave(t, "view-observations.json", counts)
}
func TestNativeSupplementViewsNegative(t *testing.T) {
	f := supplementServer(t)
	id := supplementFixtureRead(t, "diplomat")["import_id"]
	response := f.request("GET", "/api/v1/imports/"+id+"/examples?view=not-supplied", nil, "", "")
	sourceAssert(t, 200, response.Code)
	var page struct {
		Items []any  `json:"items"`
		Next  string `json:"next_cursor"`
	}
	sourceRequire(t, json.Unmarshal(response.Body.Bytes(), &page))
	sourceAssert(t, 0, len(page.Items))
	sourceAssert(t, "", page.Next)
	supplementSave(t, "view-negative.json", map[string]any{"unknown_view_examples": 0, "unknown_view_next_cursor": ""})
}

// Independent linear native-key oracles avoid a quadratic JSON join. They
// compare the same complete populations without candidate projection helpers.
func supplementNativeEdAccJoins(t *testing.T, s *Storage, id string) int64 {
	t.Helper()
	rows, err := s.DB.Query(context.Background(), "SELECT member,table_name,native_row->>'text',projection->'source_example'->>'text' FROM source_row WHERE import_id=$1 AND table_name IN ('sp_edacc_text','sp_edacc_segments')", id)
	sourceRequire(t, err)
	defer rows.Close()
	type segment struct{ key, text string }
	texts := map[string]string{}
	segments := []segment{}
	for rows.Next() {
		var member, table, line string
		var actual *string
		sourceRequire(t, rows.Scan(&member, &table, &line, &actual))
		key, tail, ok := strings.Cut(line, " ")
		sourceAssert(t, true, ok)
		prefix := member[:strings.LastIndex(member, "/")]
		if table == "sp_edacc_text" {
			texts[prefix+"/"+key] = tail
		} else {
			if actual == nil {
				t.Fatal("Saved primary text absent")
			}
			segments = append(segments, segment{prefix + "/" + key, *actual})
		}
	}
	sourceRequire(t, rows.Err())
	for _, segment := range segments {
		want, found := texts[segment.key]
		sourceAssert(t, true, found)
		sourceAssert(t, want, segment.text)
	}
	return int64(len(segments))
}
func supplementNativeRepeatedViews(t *testing.T, s *Storage, base, latest string) int64 {
	t.Helper()
	rows, err := s.DB.Query(context.Background(), "SELECT import_id,table_name,native_row->'cells'->>0,projection->'source_example'->>'native_id',projection->'source_example'->'group_ids'->>0 FROM source_row WHERE import_id=ANY($1) AND projection ? 'source_example'", []string{base, latest})
	sourceRequire(t, err)
	defer rows.Close()
	old, current := map[string]string{}, map[string]string{}
	groups := map[string]map[string]bool{base: {}, latest: {}}
	for rows.Next() {
		var importID, table, native, projected, group string
		sourceRequire(t, rows.Scan(&importID, &table, &native, &projected, &group))
		sourceAssert(t, native, projected)
		key := table + "/" + native
		if importID == base {
			old[key] = group
		} else {
			current[key] = group
		}
		if groups[importID][group] {
			t.Fatal("Different native views collapsed into one group", group)
		}
		groups[importID][group] = true
	}
	sourceRequire(t, rows.Err())
	var repeated int64
	for key, before := range old {
		if after, found := current[key]; found {
			sourceAssert(t, before, after)
			repeated++
		}
	}
	sourceAssert(t, 10490, len(old))
	sourceAssert(t, 13596, len(current))
	return repeated
}

func TestNativeSupplementReadbackPositive(t *testing.T) {
	f := supplementServer(t)
	s := f.s.Store
	ed := supplementFixtureRead(t, "edacc")["import_id"]
	el := supplementFixtureRead(t, "elrd")["import_id"]
	dp := supplementFixtureRead(t, "diplomat")["import_id"]
	base := supplementFixtureRead(t, "dral-base")
	latest := supplementFixtureRead(t, "dral-8")
	// Independent keyed native join over the full EdAcc primary population, not its row order.
	joined := supplementNativeEdAccJoins(t, s, ed)
	sourceAssert(t, int64(19137), joined)
	sourceAssert(t, int64(19137), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name='sp_edacc_segments' AND projection->'source_example'->>'accent_is_error'='false'", ed))
	sourceAssert(t, int64(282416), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name='sp_edacc_company_ctm' AND projection->'raw_metadata'->>'annotation_origin'='source_asr_output' AND NOT projection ? 'corpus_record'", ed))
	sourceAssert(t, int64(589), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection->'source_example'->>'text_origin'='source_asr_transcription' AND projection->'source_example'->'native_fields'=native_row", el))
	sourceAssert(t, int64(35255), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection->'source_example'->'native_fields'=native_row->'value' AND projection->'source_example'->'independent_population_count'='null'::jsonb", dp))
	sourceAssert(t, int64(1062), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND member='PIR_second_subtask_dataset/test.jsonl' AND projection->'source_example'->'derived_view_relation'->>'method'='owner-test-order-expanded-turn-count-supported-context-v1'", dp))
	sourceAssert(t, int64(6494), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND member LIKE 'PIR_second_subtask_dataset/%' AND projection->'source_example'->>'source_selected_choice'=(native_row->'value'->'choice'->>((native_row->'value'->>'label')::integer)) AND projection->'source_example'->>'label_meaning'='zero_based_correct_choice_index'", dp))
	// Cross-version repeated native views keep the same conservative grouping,
	// while media and corrected participant fields retain their actual release.
	repeated := supplementNativeRepeatedViews(t, s, base["import_id"], latest["import_id"])
	sourceAssert(t, int64(10490), repeated)
	fallback := supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection->'source_example'->>'base_release_dependency'=$2", latest["import_id"], base["release_id"])
	if fallback <= 0 {
		t.Fatal("No actual compatible base media used")
	}
	sourceAssert(t, int64(272), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name='sp_dral_participant'", latest["import_id"]))
	sourceAssert(t, int64(13294), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name IN ('sp_dral_fragments_short','sp_dral_fragments_long') AND projection->'source_example'->'source_clock'->>'start' IS NOT NULL AND projection->'source_example'->'local_clock'->>'start'='0'", latest["import_id"]))
	sourceAssert(t, int64(30), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection->'source_example'->>'media_representation'='native_recording_window' AND projection->'source_example'->'local_clock'=projection->'source_example'->'source_clock'", latest["import_id"]))
	supplementSave(t, "native-meaning-observations.json", map[string]any{"edacc_keyed_text_joins": joined, "edacc_reference_examples": 19137, "edacc_separate_asr_rows": 282416, "elrd_asr_turns": 589, "diplomat_exact_native_tasks": 35255, "diplomat_paired_test_answers": 1062, "diplomat_correct_choice_indices": 6494, "dral_repeated_views": repeated, "dral_base_media_dependencies": fallback, "dral_latest_participants": 272, "dral_fragments_separate_clocks": 13294, "dral_source_recording_windows": 30})
}
func TestNativeSupplementReadbackNegative(t *testing.T) {
	f := supplementServer(t)
	s := f.s.Store
	zero := map[string]int64{}
	for _, name := range []string{"edacc", "elrd", "diplomat", "dral-base", "dral-8"} {
		id := supplementFixtureRead(t, name)["import_id"]
		n := supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection->'source_example'->>'error_labels'<>'not_supplied'", id)
		sourceAssert(t, int64(0), n)
		zero[name] = n
	}
	sourceAssert(t, int64(0), supplementScalar(t, s, "SELECT count(*) FROM document WHERE kind='case-version'"))
	sourceAssert(t, int64(0), supplementScalar(t, s, "SELECT count(*) FROM usage_ledger"))
	supplementSave(t, "native-meaning-negative.json", map[string]any{"invented_error_labels": zero, "generated_cases": 0, "model_usage_rows": 0})
}
func TestNativeSupplementMissingNegative(t *testing.T) {
	f := sourceFixture(t)
	ctx := context.Background()
	results := map[string]any{}
	// Labelled partial inputs exercise the production completeness owner; they are
	// not presented as any acquired complete release.
	for _, id := range []string{"EDACC", "ELRD", "DIPLOMAT", "DRAL"} {
		member := f.upload(t, strings.ToLower(id)+"/README.md", "Constructed incomplete source notice")
		body := map[string]any{"schema_version": "2.0.0", "source_id": id, "source_version": "constructed-partial", "origin_uri": "local constructed counterexample", "documentation_asset_ids": []string{member.AssetID}, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": []SourceReleaseFile{{member.Path, member.SHA, sourceNumber(member.Bytes), member.Component, nil, true}}, "expected_counts": []any{}, "scope_kind": "partial_export", "component_expectations": []any{}}
		release, e := f.s.Store.RegisterSource(ctx, sourceBytes(body), uuid.NewString())
		sourceRequire(t, e)
		run, e := f.s.Store.createSourceImport(ctx, release.ID, "native", []string{})
		sourceRequire(t, e)
		run, e = f.s.Store.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision)
		sourceRequire(t, e)
		sourceAssert(t, false, run.Report.Normalized)
		if len(run.Report.FullMissing) == 0 {
			t.Fatal("Partial source labelled complete", id)
		}
		sourceRequire(t, f.s.Store.CommitSourceImport(ctx, run.Report.ID))
		results[id] = len(run.Report.FullMissing)
	}
	supplementSave(t, "missing-observations.json", results)
}
func TestNativeSupplementPersistencePositive(t *testing.T) {
	ctx := context.Background()
	s := supplementOpen(t)
	defer func() { s.DB.Close() }()
	fixture := supplementFixtureRead(t, "edacc")
	id := fixture["import_id"]
	var retained int64
	sourceRequire(t, s.DB.QueryRow(ctx, `SELECT count(*) FROM source_row WHERE import_id=$1 AND (transformation->>'created_at')::timestamptz < (SELECT min((payload->>'finished_at')::timestamptz) FROM source_import_event WHERE import_id=$1 AND payload->>'state'='failed' AND (payload->>'accepted_records')::bigint>=64)`, id).Scan(&retained))
	if retained < 64 {
		t.Fatal("Accepted pre-interruption rows were rewritten or recovery lineage is absent", retained)
	}
	reopened := 0
	for _, name := range []string{"edacc", "elrd", "diplomat", "dral-base", "dral-8"} {
		fixture := supplementFixtureRead(t, name)
		s.DB.Close()
		s = supplementOpen(t)
		run, e := s.SourceImport(ctx, fixture["import_id"])
		sourceRequire(t, e)
		sourceAssert(t, "complete", run.Report.State)
		sourceAssert(t, "source-native-supplements-v1", run.Report.ParserVersion)
		sourceAssert(t, fixture["source_version"], run.Frozen.Release.Release)
		sourceAssert(t, int64(0), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND state='staged'", run.Report.ID))
		reopened++
	}
	supplementSave(t, "persistence-observations.json", map[string]any{"reopened_complete_imports": reopened, "accepted_rows_predating_mapping_failure": retained, "frozen_parser": "source-native-supplements-v1", "source_versions_retained": true})
}
func TestNativeSupplementPersistenceNegative(t *testing.T) {
	s := supplementOpen(t)
	defer s.DB.Close()
	ctx := context.Background()
	for _, name := range []string{"edacc", "elrd", "diplomat", "dral-base", "dral-8"} {
		fixture := supplementFixtureRead(t, name)
		run, e := s.SourceImport(ctx, fixture["import_id"])
		sourceRequire(t, e)
		before := supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID)
		if _, e = s.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision-1); !errors.Is(e, ErrRevision) {
			t.Fatal("Stale revision did not reach the real revision owner", name, e)
		}
		saved, e := s.SourceImport(ctx, run.Report.ID)
		sourceRequire(t, e)
		sourceAssert(t, run.Revision, saved.Revision)
		sourceAssert(t, before, supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID))
	}
	supplementSave(t, "persistence-negative.json", map[string]any{"stale_completed_revisions_rejected": 5, "saved_counts_and_revisions_unchanged": true})
}
func TestNativeSupplementWindowPositive(t *testing.T) {
	f := supplementServer(t)
	s := f.s.Store
	id := supplementFixtureRead(t, "dral-8")["import_id"]
	var member, table string
	var ordinal int64
	sourceRequire(t, s.DB.QueryRow(context.Background(), "SELECT member,table_name,ordinal FROM source_row WHERE import_id=$1 AND projection->'source_example'->>'native_id'='EN_049_#1' AND table_name='sp_dral_fragments_long'", id).Scan(&member, &table, &ordinal))
	response := f.request("GET", "/api/v1/imports/"+id+"/examples?limit=1&cursor="+url.QueryEscape(sourceCursor(member, table, ordinal-1)), nil, "", "")
	sourceAssert(t, 200, response.Code)
	var page struct {
		Items []map[string]any `json:"items"`
	}
	sourceRequire(t, json.Unmarshal(response.Body.Bytes(), &page))
	sourceAssert(t, 1, len(page.Items))
	row := page.Items[0]
	e := row["projection"].(map[string]any)["source_example"].(map[string]any)
	sourceAssert(t, "EN_049_#1", e["native_id"])
	sourceAssert(t, "native_recording_window", e["media_representation"])
	sourceAssert(t, "not_supplied_in_selected_assets", e["native_fragment_file"])
	sourceAssert(t, "283/50", e["local_clock"].(map[string]any)["start"])
	sourceAssert(t, "981/100", e["local_clock"].(map[string]any)["end"])
	sourceAssert(t, "DRAL16kHz/recordings/EN_049.wav", e["media"].(map[string]any)["member"])
	supplementSave(t, "window-source-row.json", row)
	supplementSave(t, "window-positive.json", map[string]any{"source_native_id": "EN_049_#1", "media_representation": "native_recording_window", "local_start": "283/50", "local_end": "981/100", "original_recording": "DRAL16kHz/recordings/EN_049.wav"})
}
func TestNativeSupplementWindowNegative(t *testing.T) {
	s := supplementOpen(t)
	defer s.DB.Close()
	id := supplementFixtureRead(t, "dral-8")["import_id"]
	sourceAssert(t, int64(0), supplementScalar(t, s, "SELECT count(*) FROM source_file WHERE relative_path LIKE '%/fragments-long/EN_049_%' OR relative_path LIKE '%/fragments-long/BN_049_%'"))
	sourceAssert(t, int64(30), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection->'source_example'->>'native_fragment_file'='not_supplied_in_selected_assets' AND projection->'source_example'->'media'->>'member' LIKE '%/recordings/%'", id))
	supplementSave(t, "window-negative.json", map[string]any{"invented_fragment_files": 0, "actual_recording_windows": 30, "native_fragment_absence_retained": true})
}
func TestNativeSupplementPartitionPositive(t *testing.T) {
	s := supplementOpen(t)
	defer s.DB.Close()
	fixture := supplementFixtureRead(t, "diplomat")
	id := fixture["import_id"]
	counts := map[string]int64{}
	for part, want := range map[string]int64{"source_train": 29216, "dev": 1971, "source_test": 4068} {
		n := supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND corpus_record->>'split'=$2", id, part)
		sourceAssert(t, want, n)
		counts[part] = n
	}
	sourceAssert(t, int64(5102), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND member LIKE 'NLI_%/dataset.json' AND projection->'source_example'->>'native_partition'='train' AND projection->'source_example'->>'partition_origin'='owner_dataset_builder' AND corpus_record->>'split'='source_train'", id))
	sourceAssert(t, int64(35255), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection->'source_example'->'native_fields'=native_row->'value'", id))
	sourceAssert(t, int64(0), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND corpus_record->>'split'='quarantine'", id))
	supplementSave(t, "partition-observations.json", map[string]any{"counts": counts, "native_nli_train_rows": 5102, "native_fields_unchanged": 35255, "unassigned_native_splits": 0, "source_id": "DIPLOMAT", "import_id": id})
}
