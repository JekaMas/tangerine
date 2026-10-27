package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"os"
	"strings"
	"tangerine.local/api/internal/source"
	"testing"
	"time"
)

type supplementInput struct {
	Name, Version, Origin string
	Source                string `json:"source_id"`
	Files                 []struct {
		Path, Local string
		Bytes       int64
		SHA         string `json:"sha256"`
	}
}

func supplementSave(t *testing.T, name string, value any) {
	t.Helper()
	sourceRequire(t, os.WriteFile("/evidence/"+name, sourceBytes(value), 0600))
}
func supplementRead(t *testing.T, name string, value any) {
	t.Helper()
	b, e := os.ReadFile("/evidence/" + name)
	sourceRequire(t, e)
	sourceRequire(t, json.Unmarshal(b, value))
}
func supplementOpen(t *testing.T) *Storage {
	t.Helper()
	s, e := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	sourceRequire(t, e)
	return s
}
func supplementScalar(t *testing.T, s *Storage, query string, args ...any) int64 {
	t.Helper()
	var n int64
	sourceRequire(t, s.DB.QueryRow(context.Background(), query, args...).Scan(&n))
	return n
}
func supplementInterrupt(t *testing.T, s *Storage, run SourceRun, condition string, threshold int64) SourceRun {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	done := make(chan struct{})
	go func() {
		defer close(done)
		ticker := time.NewTicker(10 * time.Millisecond)
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				var n int64
				if s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND "+condition, run.Report.ID).Scan(&n) == nil && n >= threshold {
					cancel()
					return
				}
			}
		}
	}()
	_, err := s.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision)
	cancel()
	<-done
	if err == nil {
		t.Fatal("Actual interruption was not exercised")
	}
	saved, e := s.SourceImport(context.Background(), run.Report.ID)
	sourceRequire(t, e)
	sourceAssert(t, "failed", saved.Report.State)
	return saved
}
func supplementFull(t *testing.T, name string) {
	ctx := context.Background()
	s := supplementOpen(t)
	defer func() { s.DB.Close() }()
	sourceRequire(t, s.Migrate(ctx))
	sourceRequire(t, s.InitMedia(ctx))
	var inputs []supplementInput
	supplementRead(t, "admission-inputs.json", &inputs)
	var input supplementInput
	for _, candidate := range inputs {
		if candidate.Name == name {
			input = candidate
		}
	}
	if input.Name == "" {
		t.Fatal("Scope input missing")
	}
	fixture := map[string]string{}
	retained, err := os.ReadFile("/evidence/" + name + "-fixture.json")
	var release SourceRelease
	if err == nil {
		sourceRequire(t, json.Unmarshal(retained, &fixture))
		release, err = s.SourceRelease(ctx, fixture["release_id"])
		sourceRequire(t, err)
	} else {
		files := []SourceReleaseFile{}
		docs := []string{}
		admitted := 0
		for i, file := range input.Files {
			m := source.NewMember(file.Path)
			m.SHA = file.SHA
			m.Bytes = file.Bytes
			var previous string
			e := s.DB.QueryRow(ctx, "SELECT asset_id FROM source_file WHERE relative_path=$1 AND sha256=$2 AND byte_count=$3", m.Path, m.SHA, m.Bytes).Scan(&previous)
			if e == nil {
				m.AssetID = previous
			} else {
				if !errors.Is(e, pgx.ErrNoRows) {
					t.Fatal(e)
				}
				f, e := os.Open(file.Local)
				sourceRequire(t, e)
				if file.SHA == "" {
					m, e = s.saveSourceStream(ctx, file.Path, f)
				} else {
					if strings.HasSuffix(strings.ToLower(file.Path), ".wav") {
						m.Media, e = source.WaveInfo(f)
						sourceRequire(t, e)
						_, e = f.Seek(0, 0)
						sourceRequire(t, e)
					}
					m, e = s.saveAdmittedSource(ctx, m, f)
				}
				f.Close()
				sourceRequire(t, e)
				admitted++
			}
			files = append(files, SourceReleaseFile{m.Path, m.SHA, sourceNumber(m.Bytes), m.Component, m.Partition, true})
			if m.Component == "documentation" {
				docs = append(docs, m.AssetID)
			}
			if i%250 == 0 {
				supplementSave(t, name+"-admission-progress.json", map[string]any{"members": i + 1, "new_admissions": admitted, "selected_files": len(input.Files)})
				t.Log(name, "admitted", i+1, "/", len(input.Files))
			}
		}
		count := sourceNumber(int64(len(files)))
		body := map[string]any{"schema_version": "2.0.0", "source_id": input.Source, "source_version": input.Version, "origin_uri": input.Origin, "documentation_asset_ids": docs, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": files, "expected_counts": []SourceCount{{Unit: "files", Value: &count}}, "scope_kind": "full_named_release", "component_expectations": []any{}}
		release, err = s.RegisterSource(ctx, sourceBytes(body), uuid.NewString())
		sourceRequire(t, err)
		fixture = map[string]string{"release_id": release.ID, "source_id": input.Source, "source_version": input.Version}
		supplementSave(t, name+"-fixture.json", fixture)
	}
	run, e := s.createSourceImport(ctx, release.ID, "native", []string{})
	sourceRequire(t, e)
	sourceAssert(t, source.SupplementParserVersion, run.Report.ParserVersion)
	observed := map[string]any{}
	if run.Report.State == "inventory" && name == "edacc" {
		run = supplementInterrupt(t, s, run, "true", 128)
		observed["staging_interrupted"] = true
		before := supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID)
		if s.CommitSourceImport(ctx, run.Report.ID) == nil {
			t.Fatal("Incomplete import published")
		}
		observed["incomplete_commit_rejected"] = true
		if _, e = s.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision-1); e == nil {
			t.Fatal("Stale resume accepted")
		}
		sourceAssert(t, before, supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID))
		observed["stale_revision_rejected"] = true
		oldMember, oldRow, oldRevision := run.Member, run.Row, run.Revision
		s.DB.Close()
		s = supplementOpen(t)
		run, e = s.SourceImport(ctx, run.Report.ID)
		sourceRequire(t, e)
		sourceAssert(t, oldMember, run.Member)
		sourceAssert(t, oldRow, run.Row)
		sourceAssert(t, oldRevision, run.Revision)
		observed["reopen_same_cursor"] = true
		run = supplementInterrupt(t, s, run, "state<>'staged'", 64)
		observed["mapping_interrupted"] = true
		supplementSave(t, name+"-recovery.json", observed)
	}
	// Each foreground resume respects the product's existing 270-second budget.
	for attempt := 0; run.Report.State != "complete" && attempt < 12; attempt++ {
		c, cancel := context.WithTimeout(ctx, 270*time.Second)
		_, err = s.RunSourceImport(c, run.Report.ID, uuid.NewString(), run.Revision)
		cancel()
		run, e = s.SourceImport(ctx, run.Report.ID)
		sourceRequire(t, e)
		supplementSave(t, name+"-last-run.json", run)
		if err != nil && !errors.Is(err, context.DeadlineExceeded) && !errors.Is(err, context.Canceled) {
			t.Fatal(err)
		}
	}
	sourceAssert(t, "complete", run.Report.State)
	sourceAssert(t, true, run.Report.Normalized)
	sourceAssert(t, true, run.Report.RawComplete)
	sourceAssert(t, "0", run.Report.RawOnly)
	sourceAssert(t, "0", run.Report.Quarantined)
	sourceAssert(t, 0, len(run.Report.FullMissing))
	sourceRequire(t, s.CommitSourceImport(ctx, run.Report.ID))
	fixture["import_id"] = run.Report.ID
	supplementSave(t, name+"-fixture.json", fixture)
	var native map[string]struct{ Rows map[string]int64 }
	supplementRead(t, "native-expected.json", &native)
	for member, want := range native[name].Rows {
		got := supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND member=$2", run.Report.ID, member)
		sourceAssert(t, want, got)
	}
	wanted := map[string]int64{"edacc": 19137, "elrd": 589, "diplomat": 35255, "dral-base": 10490, "dral-8": 13596}[name]
	sourceAssert(t, wanted, supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection ? 'source_example'", run.Report.ID))
	if name != "diplomat" {
		sourceAssert(t, wanted, supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND projection->'source_example'->'media'->>'asset_id' IS NOT NULL", run.Report.ID))
	}
	if strings.HasPrefix(name, "dral-") {
		sourceAssert(t, int64(0), supplementScalar(t, s, "SELECT count(*) FROM source_row WHERE import_id=$1 AND corpus_record IS NOT NULL", run.Report.ID))
	}
	assets := supplementScalar(t, s, "SELECT count(*) FROM source_member WHERE release_id=$1", release.ID)
	sourceAssert(t, int64(len(input.Files)), assets)
	sourceAssert(t, int64(0), supplementScalar(t, s, "SELECT count(*) FROM usage_ledger"))
	supplementSave(t, name+"-observations.json", map[string]any{"scope": name, "release_id": release.ID, "import_id": run.Report.ID, "report": run.Report, "retained_files": assets, "normalized_examples": wanted, "native_file_counts_checked": len(native[name].Rows), "model_usage_rows": 0, "source_version": input.Version})
	fmt.Println("Complete actual supplement import", name, "examples", wanted, "files", assets)
}
func TestNativeSupplementFullEDACC(t *testing.T)    { supplementFull(t, "edacc") }
func TestNativeSupplementFullELRD(t *testing.T)     { supplementFull(t, "elrd") }
func TestNativeSupplementFullDIPLOMAT(t *testing.T) { supplementFull(t, "diplomat") }
func TestNativeSupplementFullDRALBASE(t *testing.T) { supplementFull(t, "dral-base") }
func TestNativeSupplementFullDRAL8(t *testing.T)    { supplementFull(t, "dral-8") }
