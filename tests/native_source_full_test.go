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
	file, e := os.Open(filepath.Join(root, "bea", name))
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
	r, e := f.s.Store.RegisterSource(context.Background(), sourceBytes(map[string]any{"schema_version": "2.0.0", "source_id": id, "source_version": "BEA-v2.1", "origin_uri": origin, "documentation_asset_ids": docs, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": files, "expected_counts": []any{}, "scope_kind": "full_named_release", "component_expectations": []any{}}), uuid.NewString())
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
