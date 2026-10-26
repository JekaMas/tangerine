package app

import (
	"context"
	"fmt"
	"github.com/google/uuid"
	"os"
	"path/filepath"
	"testing"
)

// Full native source imports use every original supplied member and production
// PostgreSQL/MinIO conversion. Missing source terms never become invented grants.
func sourceFullFixture(t *testing.T, id, name, origin string) *sourceNative {
	t.Helper()
	root := os.Getenv("TANGERINE_CORPUS_DATA")
	if root == "" {
		t.Fatal("actual acquired corpus mount required")
	}
	f := sourceFixture(t)
	directory := "bea"
	version := "BEA-v2.1"
	if id == "SPEECHOCEAN762" {
		directory = "speechocean762"
		version = "OpenSLR101-speechocean762"
	}
	file, e := os.Open(filepath.Join(root, directory, name))
	sourceRequire(t, e)
	defer file.Close()
	members, e := f.s.Store.IntakeArchive(context.Background(), name, "tar.gz", file)
	sourceRequire(t, e)
	files := []SourceReleaseFile{}
	docs := []string{}
	for _, m := range members {
		files = append(files, SourceReleaseFile{m.Path, m.SHA, sourceNumber(m.Bytes), m.Component, m.Partition, true})
		if m.Component == "documentation" {
			docs = append(docs, m.AssetID)
		}
	}
	r, e := f.s.Store.RegisterSource(context.Background(), sourceBytes(map[string]any{"schema_version": "2.0.0", "source_id": id, "source_version": version, "origin_uri": origin, "documentation_asset_ids": docs, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": files, "expected_counts": []any{}, "scope_kind": "full_named_release", "component_expectations": []any{}}), uuid.NewString())
	sourceRequire(t, e)
	f.release = r
	f.files = members
	return f
}
func sourceFullRun(t *testing.T, f *sourceNative) SourceRun {
	t.Helper()
	run, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	for turn := 0; turn < 12; turn++ {
		ctx, cancel := context.WithTimeout(context.Background(), OverallDeadline)
		next, e := f.s.Store.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision)
		cancel()
		if e == nil {
			return next
		}
		t.Logf("Foreground%dcaptured partial progress; actual reason%v", turn, e)
		run, e = f.s.Store.SourceImport(context.Background(), run.Report.ID)
		sourceRequire(t, e)
	}
	t.Fatal("native full source did not complete through saved foreground progress")
	return run
}
func TestNativeSourceFullFCEPositive(t *testing.T) {
	f := sourceFullFixture(t, "FCE-2.1", "fce_v2.1.bea19.tar.gz", "https://www.cl.cam.ac.uk/research/nl/bea2019st/data/fce_v2.1.bea19.tar.gz")
	run := sourceFullRun(t, f)
	sourceAssert(t, "0", run.Report.Quarantined)
	sourceAssert(t, "0", run.Report.RawOnly)
	sourceAssert(t, true, run.Report.Normalized)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	members, e := f.s.Store.sourceMembers(context.Background(), f.release.ID)
	sourceRequire(t, e)
	missing, e := f.s.Store.sourceFullMissing(context.Background(), f.release, run.Report.ID, members)
	sourceRequire(t, e)
	sourceAssert(t, []string{}, missing)
	var sentences int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name='sentences'", run.Report.ID).Scan(&sentences))
	sourceAssert(t, 33236, sentences)
	t.Logf("Actual full FCE archive: %d retainedfiles, %s native rows, %d sentence representations", len(f.files), run.Report.Observed, sentences)
}
func TestNativeSourceFullWIPositive(t *testing.T) {
	f := sourceFullFixture(t, "WILOCNESS-2.1", "wi+locness_v2.1.bea19.tar.gz", "https://www.cl.cam.ac.uk/research/nl/bea2019st/data/wi+locness_v2.1.bea19.tar.gz")
	run := sourceFullRun(t, f)
	sourceAssert(t, "0", run.Report.Quarantined)
	sourceAssert(t, "0", run.Report.RawOnly)
	sourceAssert(t, true, run.Report.Normalized)
	members, e := f.s.Store.sourceMembers(context.Background(), f.release.ID)
	sourceRequire(t, e)
	missing, e := f.s.Store.sourceFullMissing(context.Background(), f.release, run.Report.ID, members)
	sourceRequire(t, e)
	sourceAssert(t, []string{}, missing)
	var heldout int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name='withheld'", run.Report.ID).Scan(&heldout))
	sourceAssert(t, 4477, heldout)
	var fabricated int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name='withheld' AND projection #>> '{raw_metadata,labels_state}'<>'labels_not_supplied'", run.Report.ID).Scan(&fabricated))
	sourceAssert(t, 0, fabricated)
	t.Log(fmt.Sprintf("Actual full W&I archive: %d members, %s native rows, withheld labels remain absent", len(f.files), run.Report.Observed))
}

func TestNativeSourceFullSpeechOceanPositive(t *testing.T) {
	f := sourceFullFixture(t, "SPEECHOCEAN762", "speechocean762.tar.gz", "https://openslr.org/resources/101/speechocean762.tar.gz")
	run := sourceFullRun(t, f)
	if dir := os.Getenv("TANGERINE_SOURCE_FULL_EVIDENCE"); dir != "" {
		sourceRequire(t, os.WriteFile(filepath.Join(dir, "speechocean-report.json"), sourceBytes(run.Report), 0600))
	}
	sourceAssert(t, "0", run.Report.Quarantined)
	sourceAssert(t, "0", run.Report.RawOnly)
	sourceAssert(t, true, run.Report.RawComplete)
	sourceAssert(t, true, run.Report.Normalized)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	var scored, raters, recordings int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FILTER(WHERE table_name='scores.json'),count(*) FILTER(WHERE table_name='scores-detail.json') FROM source_row WHERE import_id=$1", run.Report.ID).Scan(&scored, &raters))
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_member WHERE release_id=$1 AND lower(relative_path) LIKE '%.wav'", f.release.ID).Scan(&recordings))
	sourceAssert(t, 5000, scored)
	sourceAssert(t, 5000, raters)
	// The actual archive also contains245unrated recordings. Preserve those
	// native members separately from its5,000scored utterances.
	sourceAssert(t, 5245, recordings)
	sourceAssert(t, []string{}, run.Report.FullMissing)
	statuses, e := f.s.Store.SourceStatuses(context.Background())
	sourceRequire(t, e)
	for _, item := range statuses {
		if item["source_id"] == "SPEECHOCEAN762" {
			sourceAssert(t, "complete", item["status"])
		}
	}
	t.Logf("Actual full SpeechOcean: %d members, %d scored/rater utterances, %d original WAVE files; native scales and all raw scores retained", len(f.files), scored, recordings)
}
