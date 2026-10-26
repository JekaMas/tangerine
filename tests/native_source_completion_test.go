package app

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"strings"
	"tangerine.local/api/internal/source"
	"testing"
)

// Constructed records exercise the actual storage/import/status owners. They
// never stand for the unavailable Cambridge, study or vendor populations.
func completionSourceStatus(t *testing.T, f *sourceNative, id string) map[string]any {
	t.Helper()
	statuses, e := f.s.Store.SourceStatuses(context.Background())
	sourceRequire(t, e)
	sourceAssert(t, 11, len(statuses))
	for _, item := range statuses {
		if item["source_id"] == id {
			return item
		}
	}
	t.Fatal("source identity omitted")
	return nil
}

func TestNativeSourceReleaseLineagePositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	first := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), first.Report.ID))
	older := f.release.ID
	second := &sourceNative{s: f.s}
	second.upload(t, "new/train.m2", "S We made a decision .\n\n")
	second.register(t, "FCE-2.1", "partial_export")
	last := second.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), last.Report.ID))
	item := completionSourceStatus(t, f, "FCE-2.1")
	encoded := sourceBytes(item)
	var actual struct {
		ByRelease map[string][]string `json:"release_import_report_ids"`
	}
	sourceRequire(t, json.Unmarshal(encoded, &actual))
	sourceAssert(t, []string{first.Report.ID}, actual.ByRelease[older])
	sourceAssert(t, []string{last.Report.ID}, actual.ByRelease[second.release.ID])
	sourceAssert(t, "not_acquired", completionSourceStatus(t, f, "NIR-DATA")["status"])
}

func TestNativeSourceStoredAssessmentPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	var report map[string]any
	sourceRequire(t, json.Unmarshal(sourceBytes(run.Report), &report))
	missing, ok := report["full_release_missing_components"].([]any)
	if !ok || len(missing) == 0 {
		t.Fatal("import completion did not persist the actual named-release assessment")
	}
	var expected []string
	for _, entry := range missing {
		expected = append(expected, entry.(string))
	}
	item := completionSourceStatus(t, f, "FCE-2.1")
	sourceAssert(t, expected, item["missing_component_names"])
	sourceAssert(t, "incomplete", item["status"])
	sourceAssert(t, true, item["raw_complete"])
}

func TestNativeSourceStoredAssessmentNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	before := completionSourceStatus(t, f, "FCE-2.1")
	// A test-owned unavailable row table must not make a metadata read recount
	// accepted rows or lose the saved assessment. No user data are changed.
	_, e := f.s.Store.DB.Exec(context.Background(), "ALTER TABLE source_row RENAME TO test_unavailable_source_row")
	sourceRequire(t, e)
	after := completionSourceStatus(t, f, "FCE-2.1")
	sourceAssert(t, before, after)
}

func TestNativeSourceMissingComponentNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	count := "1"
	f.release.Components = []SourceComponent{{Name: "instruments", Globs: []string{"instruments/*.csv"}, Expected: &count, Reason: "Constructed documented count drift; it does not create the missing file."}}
	var input map[string]any
	sourceRequire(t, json.Unmarshal(sourceBytes(f.release), &input))
	for _, key := range []string{"id", "observed_counts", "manifest_sha256"} {
		delete(input, key)
	}
	release, e := f.s.Store.RegisterSource(context.Background(), sourceBytes(input), uuid.NewString())
	sourceRequire(t, e)
	f.release = release
	run := f.run(t, "native", nil)
	sourceAssert(t, true, run.Report.RawComplete)
	sourceAssert(t, false, run.Report.Normalized)
	for _, c := range run.Report.Components {
		if c.Component == "instruments" {
			sourceAssert(t, "0", c.Observed)
			sourceAssert(t, false, c.Complete)
			return
		}
	}
	t.Fatal("required absent component omitted from report")
}

func TestNativeSourceLegacyAssessmentNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE source_import SET payload=payload-'full_release_missing_components' WHERE id=$1", run.Report.ID)
	sourceRequire(t, e)
	item := completionSourceStatus(t, f, "FCE-2.1")
	sourceAssert(t, "incomplete", item["status"])
	sourceAssert(t, true, item["raw_complete"])
	if !strings.Contains(strings.Join(item["missing_component_names"].([]string), " "), "not saved") {
		t.Fatal("legacy assessment was silently invented or recomputed")
	}
}

func TestNativeSourceCompanionNegative(t *testing.T) {
	f := sourceFixture(t)
	f.upload(t, "definite.csv", "writingID,Noof_obl_context,SOC_scores\nw1,2,0.5\n")
	f.upload(t, "indefinite.csv", "writingID,Noof_obl_context,SOC_scores\nw1,1,1\n")
	f.register(t, "EFCAMDAT-OKSUZ2025", "analysis_companion")
	run := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	sourceAssert(t, true, run.Report.RawComplete)
	sourceAssert(t, false, run.Report.Normalized)
	sourceAssert(t, "2", run.Report.RawOnly)
	if completionSourceStatus(t, f, "EFCAMDAT-OKSUZ2025")["status"] == "complete" {
		t.Fatal("article companion certified the full derivative")
	}
	for _, id := range []string{"EFCAMDAT-R2", "EFCAMDAT-SHATZ2020"} {
		sourceAssert(t, "not_acquired", completionSourceStatus(t, f, id)["status"])
	}
}

func TestNativeSourceMirrorNegative(t *testing.T) {
	f := sourceFixture(t)
	f.upload(t, "ABA/transcript/arctic_a0001.txt", "A constructed mirror transcript.")
	f.upload(t, "README.md", "Constructed pinned mirror; official archive equivalence unknown.")
	f.register(t, "L2-ARCTIC", "mirror")
	run := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	loaded, e := f.s.Store.SourceRelease(context.Background(), f.release.ID)
	sourceRequire(t, e)
	sourceAssert(t, "mirror", loaded.Scope)
	sourceAssert(t, f.release.Origin, loaded.Origin)
	sourceAssert(t, true, run.Report.RawComplete)
	if completionSourceStatus(t, f, "L2-ARCTIC")["status"] == "complete" {
		t.Fatal("mirror intake certified an official full source")
	}
}

func TestNativeSourceSavedPermissionsPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	permission := f.permission(t)
	run := f.run(t, "native", []string{permission})
	loaded, e := f.s.Store.SourceImport(context.Background(), run.Report.ID)
	sourceRequire(t, e)
	var projected struct {
		Binding     string   `json:"format_binding_id"`
		Permissions []string `json:"permission_grant_ids"`
	}
	sourceRequire(t, json.Unmarshal(sourceBytes(loaded), &projected))
	sourceAssert(t, "native", projected.Binding)
	sourceAssert(t, []string{permission}, projected.Permissions)
	// The returned saved selection resumes the original import rather than
	// inheriting notices from another selected source or causing a conflict.
	reopened, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, projected.Binding, projected.Permissions)
	sourceRequire(t, e)
	sourceAssert(t, run.Report.ID, reopened.Report.ID)
}

func TestNativeSourceComponentReconciliationPositive(t *testing.T) {
	for _, entry := range []struct{ name, glob, expected, observed string }{
		{"documented empty optional component", "optional/*.csv", "0", "0"},
		{"documented nonzero drift", "fce/train.m2", "2", "1"},
	} {
		t.Run(entry.name, func(t *testing.T) {
			f := sourceFixture(t)
			f.bea(t)
			f.release.Components = []SourceComponent{{Name: "documented", Globs: []string{entry.glob}, Expected: &entry.expected, Reason: "Constructed owner-documented reconciliation"}}
			var input map[string]any
			sourceRequire(t, json.Unmarshal(sourceBytes(f.release), &input))
			for _, key := range []string{"id", "observed_counts", "manifest_sha256"} {
				delete(input, key)
			}
			release, e := f.s.Store.RegisterSource(context.Background(), sourceBytes(input), uuid.NewString())
			sourceRequire(t, e)
			f.release = release
			run := f.run(t, "native", nil)
			sourceAssert(t, true, run.Report.Normalized)
			for _, count := range run.Report.Components {
				if count.Component == "documented" {
					sourceAssert(t, entry.observed, count.Observed)
					sourceAssert(t, true, count.Complete)
					return
				}
			}
			t.Fatal("documented component omitted")
		})
	}
}

func TestNativeSourceSpeechMediaScopeNegative(t *testing.T) {
	f := sourceSpeechFixture(t, false)
	run := f.run(t, "native", nil)
	// Synthetic member metadata isolates the native media-count rule. It is
	// not an acquired5,000recording population or a complete import claim.
	members := []source.Member{}
	for i := 0; i < 5245; i++ {
		members = append(members, source.Member{Path: fmt.Sprintf("WAVE/%d.WAV", i)})
	}
	for _, count := range []int{5000, 5245} {
		missing, e := f.s.Store.sourceFullMissing(context.Background(), f.release, run.Report.ID, members[:count])
		sourceRequire(t, e)
		found := false
		for _, message := range missing {
			found = found || strings.HasPrefix(message, "Complete native WAVE files:")
		}
		sourceAssert(t, count != 5245, found)
	}
}
