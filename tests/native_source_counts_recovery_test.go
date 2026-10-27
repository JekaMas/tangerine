package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"strings"
	"testing"
)

func nativeSourceCountRecovery(t *testing.T, want string) (SourceRun, *sourceNative) {
	t.Helper()
	ctx := context.Background()
	f := sourceFixture(t)
	f.bea(t)
	f.release.Expected = []SourceCount{{Unit: "records", Value: &want}}
	body := map[string]any{}
	sourceRequire(t, json.Unmarshal(sourceBytes(f.release), &body))
	delete(body, "id")
	delete(body, "observed_counts")
	delete(body, "manifest_sha256")
	r, e := f.s.Store.RegisterSource(ctx, sourceBytes(body), uuid.NewString())
	sourceRequire(t, e)
	f.release = r
	run, e := f.s.Store.createSourceImport(ctx, r.ID, "native", nil)
	sourceRequire(t, e)
	run, e = f.s.Store.acquireSource(ctx, run.Report.ID, uuid.NewString(), run.Revision)
	sourceRequire(t, e)
	run.Report.State = "failed"
	sourceRequire(t, f.s.Store.sourceSummary(ctx, &run))
	sourceRequire(t, f.s.Store.checkpointSource(ctx, &run, true))
	var initial bool
	for _, issue := range run.Report.Issues {
		if issue.Code == "count_mismatch" && strings.Contains(issue.Detail, "actual 0") {
			initial = true
		}
	}
	sourceAssert(t, true, initial)
	run, e = f.s.Store.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision)
	sourceRequire(t, e)
	return run, f
}
func TestNativeSourceCountRecoveryPositive(t *testing.T) {
	run, f := nativeSourceCountRecovery(t, "6")
	for _, issue := range run.Report.Issues {
		if issue.Code == "count_mismatch" || issue.Code == "count_unbound" {
			t.Fatalf("resolved count still shown as active: %+v", issue)
		}
	}
	var history int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_issue WHERE import_id=$1 AND code='count_mismatch'", run.Report.ID).Scan(&history))
	sourceAssert(t, 1, history)
	sourceAssert(t, "6", run.Report.Observed)
}
func TestNativeSourceCountRecoveryNegative(t *testing.T) {
	run, _ := nativeSourceCountRecovery(t, "7")
	var found bool
	for _, issue := range run.Report.Issues {
		if issue.Code == "count_mismatch" {
			sourceAssert(t, "records expected 7; actual 6 in its stated native counting unit", issue.Detail)
			found = true
		}
	}
	sourceAssert(t, true, found)
	sourceAssert(t, false, run.Report.Normalized)
}
