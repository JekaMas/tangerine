package app

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"os"
	"path/filepath"
	"tangerine.local/api/internal/source"
	"testing"
	"time"
)

const jflegCommit = "ee06ff806a208aba815ac45313f4e750a48330a5"
const jflegOwner = "jfleg-" + jflegCommit

func jflegSave(t *testing.T, name string, value any) {
	t.Helper()
	sourceRequire(t, os.WriteFile("/evidence/"+name, sourceBytes(value), 0600))
}
func jflegOpen(t *testing.T) *Storage {
	t.Helper()
	s, e := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	sourceRequire(t, e)
	return s
}

type jflegBaseline struct {
	Files []struct {
		Path  string `json:"path"`
		Bytes int64  `json:"bytes"`
	} `json:"files"`
	Lines map[string][]string `json:"lines"`
}

func jflegBaselineRead(t *testing.T) jflegBaseline {
	t.Helper()
	raw, e := os.ReadFile("/evidence/native-expected.json")
	sourceRequire(t, e)
	var out jflegBaseline
	sourceRequire(t, json.Unmarshal(raw, &out))
	return out
}
func jflegScalar(t *testing.T, s *Storage, query string, args ...any) int64 {
	t.Helper()
	var n int64
	sourceRequire(t, s.DB.QueryRow(context.Background(), query, args...).Scan(&n))
	return n
}
func jflegInterrupt(t *testing.T, s *Storage, run SourceRun, condition string, threshold int64) SourceRun {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	stopped := make(chan struct{})
	go func() {
		defer close(stopped)
		tick := time.NewTicker(10 * time.Millisecond)
		defer tick.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-tick.C:
				var n int64
				e := s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND "+condition, run.Report.ID).Scan(&n)
				if e == nil && n >= threshold {
					cancel()
					return
				}
			}
		}
	}()
	_, e := s.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision)
	cancel()
	<-stopped
	if e == nil {
		t.Fatal("required actual interruption did not occur")
	}
	saved, err := s.SourceImport(context.Background(), run.Report.ID)
	sourceRequire(t, err)
	sourceAssert(t, "failed", saved.Report.State)
	return saved
}
func TestNativeJFLEGFull(t *testing.T) {
	ctx := context.Background()
	s := jflegOpen(t)
	defer func() { s.DB.Close() }()
	sourceRequire(t, s.Migrate(ctx))
	sourceRequire(t, s.InitMedia(ctx))
	var release SourceRelease
	if retained, err := os.ReadFile("/evidence/fixture.json"); err == nil {
		var saved map[string]string
		sourceRequire(t, json.Unmarshal(retained, &saved))
		var e error
		release, e = s.SourceRelease(ctx, saved["release_id"])
		sourceRequire(t, e)
		// A repaired candidate gets a new import using the already admitted members.
		// The previous failed projection remains untouched as a retained witness.
		count, records := "30", "34789"
		body := map[string]any{"schema_version": "2.0.0", "source_id": "JFLEG", "source_version": jflegCommit, "origin_uri": release.Origin, "documentation_asset_ids": release.Docs, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": release.Files, "expected_counts": []SourceCount{{Unit: "files", Value: &count}, {Unit: "records", Value: &records}}, "scope_kind": "full_named_release", "component_expectations": []any{}}
		release, e = s.RegisterSource(ctx, sourceBytes(body), uuid.NewString())
		sourceRequire(t, e)
		jflegSave(t, "fixture.json", map[string]any{"release_id": release.ID, "source_version": jflegCommit})
	} else {
		archive, e := os.Open("/corpus/owner-" + jflegCommit + ".tar.gz")
		sourceRequire(t, e)
		defer archive.Close()
		files, e := s.IntakeArchive(ctx, "owner-"+jflegCommit+".tar.gz", "tar.gz", archive)
		sourceRequire(t, e)
		sourceAssert(t, 30, len(files))
		nativeFiles := []SourceReleaseFile{}
		docs := []string{}
		for _, m := range files {
			nativeFiles = append(nativeFiles, SourceReleaseFile{m.Path, m.SHA, sourceNumber(m.Bytes), m.Component, m.Partition, true})
			if m.Component == "documentation" {
				docs = append(docs, m.AssetID)
			}
		}
		count, records := "30", "34789"
		body := map[string]any{"schema_version": "2.0.0", "source_id": "JFLEG", "source_version": jflegCommit, "origin_uri": "https://github.com/keisks/jfleg/tree/" + jflegCommit, "documentation_asset_ids": docs, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": nativeFiles, "expected_counts": []SourceCount{{Unit: "files", Value: &count}, {Unit: "records", Value: &records}}, "scope_kind": "full_named_release", "component_expectations": []any{}}
		release, e = s.RegisterSource(ctx, sourceBytes(body), uuid.NewString())
		sourceRequire(t, e)
		jflegSave(t, "fixture.json", map[string]any{"release_id": release.ID, "source_version": jflegCommit})
	}
	run, e := s.createSourceImport(ctx, release.ID, "native", []string{})
	sourceRequire(t, e)
	sourceAssert(t, source.JFLEGParserVersion, run.Report.ParserVersion)
	run = jflegInterrupt(t, s, run, "true", 128)
	stageCount := jflegScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID)
	if stageCount < 128 {
		t.Fatal("no real staging checkpoint")
	}
	if s.CommitSourceImport(ctx, run.Report.ID) == nil {
		t.Fatal("failed import published")
	}
	before := stageCount
	if _, e = s.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision-1); e == nil {
		t.Fatal("stale revision accepted")
	}
	sourceAssert(t, before, jflegScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID))
	s.DB.Close()
	s = jflegOpen(t)
	saved, e := s.SourceImport(ctx, run.Report.ID)
	sourceRequire(t, e)
	sourceAssert(t, run.Member, saved.Member)
	sourceAssert(t, run.Revision, saved.Revision)
	run = jflegInterrupt(t, s, saved, "state<>'staged'", 64)
	acceptedBefore := jflegScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND state<>'staged'", run.Report.ID)
	var anchorMember, anchorTable, anchorBefore string
	var ordinal int64
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT member,table_name,ordinal,projection::text FROM source_row WHERE import_id=$1 AND state<>'staged' ORDER BY member,table_name,ordinal LIMIT 1", run.Report.ID).Scan(&anchorMember, &anchorTable, &ordinal, &anchorBefore))
	s.DB.Close()
	s = jflegOpen(t)
	run, e = s.SourceImport(ctx, run.Report.ID)
	sourceRequire(t, e)
	run, e = s.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision)
	sourceRequire(t, e)
	jflegSave(t, "import-report-before-assertions.json", run)
	sourceAssert(t, "complete", run.Report.State)
	sourceAssert(t, true, run.Report.Normalized)
	sourceAssert(t, true, run.Report.RawComplete)
	sourceAssert(t, "34789", run.Report.Accepted)
	sourceAssert(t, "0", run.Report.RawOnly)
	sourceAssert(t, "0", run.Report.Quarantined)
	sourceRequire(t, s.CommitSourceImport(ctx, run.Report.ID))
	var anchorAfter string
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT projection::text FROM source_row WHERE import_id=$1 AND member=$2 AND table_name=$3 AND ordinal=$4", run.Report.ID, anchorMember, anchorTable, ordinal).Scan(&anchorAfter))
	sourceAssert(t, anchorBefore, anchorAfter)
	sourceAssert(t, int64(30), jflegScalar(t, s, "SELECT count(*) FROM source_member WHERE release_id=$1", release.ID))
	sourceAssert(t, int64(1501), jflegScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND corpus_record IS NOT NULL", run.Report.ID))
	baseline := jflegBaselineRead(t)
	datasets := map[string]int{}
	allGroups := map[string]bool{}
	allRefs := 0
	replays := 0
	unchanged := 0
	for part, want := range map[string]int{"dev": 754, "test": 747} {
		dataset, e := s.SourceCorrectionDataset(ctx, run.Report.ID, part)
		sourceRequire(t, e)
		sourceAssert(t, want, len(dataset.Examples))
		datasets[part] = len(dataset.Examples)
		sourceAssert(t, release.ID, dataset.Release)
		sourceAssert(t, jflegCommit, dataset.SourceVersion)
		for i, example := range dataset.Examples {
			sourceAssert(t, fmt.Sprintf("%s:%d", part, i), example.ID)
			sourceAssert(t, baseline.Lines[part+"/"+part+".src"][i], example.Original.Text)
			sourceAssert(t, 4, len(example.References))
			sourceAssert(t, 4, len(example.Differences))
			sourceAssert(t, "complete", example.ReferenceCompleteness)
			if allGroups[example.Group] {
				t.Fatal("source family duplicated across examples")
			}
			allGroups[example.Group] = true
			sourceAssert(t, baseline.Lines[part+"/"+part+".spellchecked.src"][i], example.Spellchecked.Text)
			for j, reference := range example.References {
				sourceAssert(t, fmt.Sprintf("ref%d", j), reference.ID)
				sourceAssert(t, baseline.Lines[fmt.Sprintf("%s/%s.ref%d", part, part, j)][i], reference.Text)
				sourceAssert(t, "source_annotation", reference.Origin)
				sourceAssert(t, int64(i), reference.LineIndex)
				d := example.Differences[j]
				a := []rune(example.Original.Text)
				actual := string(a[:d.OriginalSpan[0]]) + d.Replacement + string(a[d.OriginalSpan[1]:])
				sourceAssert(t, reference.Text, actual)
				sourceAssert(t, "not_computed", d.LinguisticAlignment)
				sourceAssert(t, "not_supplied", d.CategoryMapping)
				replays++
				if d.Kind == "unchanged" {
					unchanged++
				}
				allRefs++
			}
		}
		jflegSave(t, "dataset-"+part+".json", dataset)
	}
	tableCounts := map[string]int64{}
	rows, e := s.DB.Query(ctx, "SELECT table_name,count(*) FROM source_row WHERE import_id=$1 GROUP BY table_name ORDER BY table_name", run.Report.ID)
	sourceRequire(t, e)
	for rows.Next() {
		var table string
		var n int64
		sourceRequire(t, rows.Scan(&table, &n))
		tableCounts[table] = n
	}
	sourceRequire(t, rows.Err())
	rows.Close()
	sourceAssert(t, int64(1501), tableCounts["jfleg_source"])
	sourceAssert(t, int64(1501), tableCounts["jfleg_spellchecked"])
	sourceAssert(t, int64(22549), tableCounts["edits"])
	sourceAssert(t, int64(1501), tableCounts["sentences"])
	sourceAssert(t, int64(1733), tableCounts["records"])
	sourceAssert(t, int64(24), jflegScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND native_row->>'invalid'='true' AND state='metadata'", run.Report.ID))
	sourceAssert(t, int64(19), jflegScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND native_row->>'invalid'='true' AND table_name='edits'", run.Report.ID))
	sourceAssert(t, int64(5), jflegScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND native_row->>'invalid'='true' AND table_name='sentences'", run.Report.ID))
	sourceAssert(t, 6004, allRefs)
	sourceAssert(t, 6004, replays)
	jflegSave(t, "fixture.json", map[string]any{"release_id": release.ID, "import_id": run.Report.ID, "source_version": jflegCommit})
	jflegSave(t, "observations.json", map[string]any{"release_id": release.ID, "import_id": run.Report.ID, "report": run.Report, "assets": 30, "tables": tableCounts, "datasets": datasets, "reference_positions": allRefs, "coarse_replays": replays, "unchanged_references": unchanged, "groups": len(allGroups), "staging_interruption_rows": stageCount, "mapping_interruption_accepted": acceptedBefore, "accepted_anchor_unchanged": anchorBefore == anchorAfter, "stale_revision_rejected": true, "incomplete_commit_rejected": true, "reopened_same_cursor": true, "corpus_records": 1501, "tool_invalid_annotations": 19, "tool_affected_sentences": 5, "tool_findings_retained": 24, "native_expected_file": filepath.Base("/evidence/native-expected.json")})
}
