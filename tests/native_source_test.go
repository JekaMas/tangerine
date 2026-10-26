package app

import (
	"archive/zip"
	"bytes"
	"context"
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"io"
	"math/rand"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"strings"
	"sync/atomic"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
	"testing"
	"time"
)

type sourceNative struct {
	s       *Server
	release SourceRelease
	files   []source.Member
}

func sourceStore(t *testing.T) *Storage { return sourceStoreVersion(t, 7) }
func sourceStoreVersion(t *testing.T, version int) *Storage {
	t.Helper()
	ctx := context.Background()
	admin, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	if e != nil {
		t.Fatal(e)
	}
	schema := "i13_" + strings.ReplaceAll(uuid.NewString(), "-", "")
	if _, e = admin.DB.Exec(ctx, "CREATE SCHEMA "+schema); e != nil {
		t.Fatal(e)
	}
	u, _ := url.Parse(os.Getenv("DATABASE_URL"))
	q := u.Query()
	q.Set("search_path", schema)
	u.RawQuery = q.Encode()
	store, e := OpenStorage(ctx, u.String(), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(func() {
		store.DB.Close()
		_, _ = admin.DB.Exec(context.Background(), "DROP SCHEMA "+schema+" CASCADE")
		admin.DB.Close()
	})
	if version == 7 {
		if e = store.Migrate(ctx); e != nil {
			t.Fatal(e)
		}
	} else {
		tx, e := store.DB.Begin(ctx)
		sourceRequire(t, e)
		defer tx.Rollback(ctx)
		_, e = tx.Exec(ctx, "CREATE TABLE schema_migrations(version text PRIMARY KEY,sha256 char(64) NOT NULL,applied_at timestamptz NOT NULL DEFAULT now())")
		sourceRequire(t, e)
		entries, _ := migrations.ReadDir("migrations")
		for _, entry := range entries[:version] {
			b, _ := migrations.ReadFile("migrations/" + entry.Name())
			_, e = tx.Exec(ctx, string(b))
			sourceRequire(t, e)
			_, e = tx.Exec(ctx, "INSERT INTO schema_migrations(version,sha256) VALUES($1,$2)", entry.Name(), contracts.Digest(b))
			sourceRequire(t, e)
		}
		sourceRequire(t, tx.Commit(ctx))
	}
	if e = store.InitMedia(ctx); e != nil {
		t.Fatal(e)
	}
	return store
}
func sourceRequire(t *testing.T, e error) {
	t.Helper()
	if e != nil {
		t.Fatal(e)
	}
}
func sourceAssert(t *testing.T, want, got any) {
	t.Helper()
	a, _ := json.Marshal(want)
	b, _ := json.Marshal(got)
	if string(a) != string(b) {
		t.Fatalf("want %s; got %s", a, b)
	}
}
func sourceFixture(t *testing.T) *sourceNative {
	t.Helper()
	store := sourceStore(t)
	s := NewServer(store, "http://localhost:3000", "http://unused.invalid")
	s.token = "source-owned-token"
	return &sourceNative{s: s}
}
func (f *sourceNative) upload(t *testing.T, name, body string) source.Member {
	t.Helper()
	m, e := f.s.Store.saveSourceStream(context.Background(), name, strings.NewReader(body))
	sourceRequire(t, e)
	f.files = append(f.files, m)
	return m
}
func (f *sourceNative) register(t *testing.T, id, scope string) {
	t.Helper()
	files := []SourceReleaseFile{}
	docs := []string{}
	for _, m := range f.files {
		files = append(files, SourceReleaseFile{m.Path, m.SHA, sourceNumber(m.Bytes), m.Component, m.Partition, true})
		if m.Component == "documentation" {
			docs = append(docs, m.AssetID)
		}
	}
	b := sourceBytes(map[string]any{"schema_version": "2.0.0", "source_id": id, "source_version": "constructed-i13-v1", "origin_uri": "constructed://independent-native-fixture", "documentation_asset_ids": docs, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": files, "expected_counts": []any{}, "scope_kind": scope, "component_expectations": []any{}})
	r, e := f.s.Store.RegisterSource(context.Background(), b, uuid.NewString())
	sourceRequire(t, e)
	f.release = r
}
func (f *sourceNative) bea(t *testing.T) {
	f.upload(t, "fce/readme.txt", "Constructed parser fixture. Not an acquired full native release.")
	f.upload(t, "fce/licence.txt", "Constructed notice: local analysis only.")
	for _, part := range []string{"train", "dev", "test"} {
		f.upload(t, "fce/"+part+".m2", "S café go home\nA 1 2|||R:VERB:SVA|||goes|||REQUIRED|||-NONE-|||0\n\n")
	}
	f.register(t, "FCE-2.1", "full_named_release")
}
func (f *sourceNative) run(t *testing.T, binding string, permissions []string) SourceRun {
	t.Helper()
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, binding, permissions)
	sourceRequire(t, e)
	r, e = f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), r.Revision)
	sourceRequire(t, e)
	return r
}
func (f *sourceNative) request(method, path string, body []byte, key, revision string) *httptest.ResponseRecorder {
	r := httptest.NewRequest(method, path, bytes.NewReader(body))
	r.Header.Set("Origin", f.s.Origin)
	r.Header.Set("Authorization", "Bearer source-owned-token")
	r.Header.Set("Content-Type", "application/json")
	if key != "" {
		r.Header.Set("Idempotency-Key", key)
	}
	if revision != "" {
		r.Header.Set("If-Match", revision)
	}
	w := httptest.NewRecorder()
	f.s.Handler().ServeHTTP(w, r)
	return w
}
func TestNativeSourceIntakePositive(t *testing.T) {
	f := sourceFixture(t)
	m := f.upload(t, "scripts/inert.sh", "touch NEVER_EXECUTED")
	sourceAssert(t, 20, m.Bytes)
	f.register(t, "MOODRICK-DATA", "partial_export")
	sourceAssert(t, 1, len(f.release.Files))
	read := f.request("GET", "/api/v1/sources/assets/"+m.AssetID+"/bytes", nil, "", "")
	sourceAssert(t, 200, read.Code)
	sourceAssert(t, "attachment", read.Header().Get("Content-Disposition"))
	sourceAssert(t, "touch NEVER_EXECUTED", read.Body.String())
	sourceAssert(t, "sandbox", read.Header().Get("Content-Security-Policy"))
}
func TestNativeSourceIntakeNegative(t *testing.T) {
	f := sourceFixture(t)
	if _, e := f.s.Store.saveSourceStream(context.Background(), "../escape", strings.NewReader("x")); e == nil {
		t.Fatal("unsafe input admitted")
	}
	f.upload(t, "file.csv", "id,text\na,hello\n")
	f.register(t, "MOODRICK-DATA", "partial_export")
	b := map[string]any{}
	_ = json.Unmarshal(sourceBytes(f.release), &b)
	delete(b, "id")
	delete(b, "observed_counts")
	delete(b, "manifest_sha256")
	b["source_id"] = "invented"
	if _, e := f.s.Store.RegisterSource(context.Background(), sourceBytes(b), uuid.NewString()); !errors.Is(e, ErrInput) {
		t.Fatalf("unknown source %v", e)
	}
	b["source_id"] = "MOODRICK-DATA"
	b["files"].([]any)[0].(map[string]any)["sha256"] = strings.Repeat("0", 64)
	if _, e := f.s.Store.RegisterSource(context.Background(), sourceBytes(b), uuid.NewString()); e == nil {
		t.Fatal("unacquired digest admitted")
	}
}
func TestNativeSourceNativeImportPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	sourceAssert(t, "6", run.Report.Observed)
	sourceAssert(t, "6", run.Report.Accepted)
	t.Logf("native issues: %+v", run.Report.Issues)
	sourceAssert(t, "0", run.Report.RawOnly)
	sourceAssert(t, true, run.Report.RawComplete)
	sourceAssert(t, true, run.Report.Normalized)
	sourceAssert(t, "complete", run.Report.State)
	_, _, e := contracts.Validate("import-report", "2.0.0", sourceBytes(run.Report))
	sourceRequire(t, e)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	items, e := f.s.Store.SourceStatuses(context.Background())
	sourceRequire(t, e)
	for _, item := range items {
		if item["source_id"] == "FCE-2.1" {
			sourceAssert(t, "incomplete", item["status"])
		}
	}
	rows, _, e := f.s.Store.SourceRows(context.Background(), run.Report.ID, "", 20)
	sourceRequire(t, e)
	count := 0
	for _, row := range rows {
		if c, ok := row["corpus_record"].(map[string]any); ok {
			count++
			sourceAssert(t, "café go home", c["text"])
			sourceAssert(t, []any{}, c["licence"].(map[string]any)["uses"])
		}
	}
	sourceAssert(t, 3, count)
}
func TestNativeSourceNativeImportNegative(t *testing.T) {
	f := sourceFixture(t)
	f.upload(t, "fce/readme.txt", "partial")
	f.upload(t, "fce/train.m2", "S a b\nA 0 9|||R:NOUN|||c|||REQUIRED|||-NONE-|||0\n")
	f.register(t, "FCE-2.1", "partial_export")
	run := f.run(t, "native", nil)
	sourceAssert(t, false, run.Report.Normalized)
	sourceAssert(t, "quarantined", run.Report.State)
	sourceAssert(t, "2", run.Report.Quarantined)
	sourceAssert(t, true, run.Report.RawComplete)
	if len(run.Report.Issues) == 0 {
		t.Fatal("missing located annotation error")
	}
}
func TestNativeSourceResumePositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	lease, e := f.s.Store.acquireSource(context.Background(), r.Report.ID, uuid.NewString(), r.Revision)
	sourceRequire(t, e)
	members, e := f.s.Store.sourceMembers(context.Background(), f.release.ID)
	sourceRequire(t, e)
	lease.Report.State = "parsing"
	lease.Phase = "parsing"
	sourceRequire(t, f.s.Store.stageSource(context.Background(), &lease, members))
	lease.Phase = "mapping"
	sourceRequire(t, f.s.Store.checkpointSource(context.Background(), &lease, false))
	_, e = f.s.Store.DB.Exec(context.Background(), "UPDATE source_import SET deadline_at=clock_timestamp()-interval '1 second' WHERE id=$1", r.Report.ID)
	sourceRequire(t, e)
	r, e = f.s.Store.SourceImport(context.Background(), r.Report.ID)
	sourceRequire(t, e)
	r, e = f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), r.Revision)
	sourceRequire(t, e)
	sourceAssert(t, "6", r.Report.Observed)
	sourceAssert(t, "complete", r.Report.State)
	var count int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_row WHERE import_id=$1", r.Report.ID).Scan(&count))
	sourceAssert(t, 6, count)
}
func TestNativeSourceResumeNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	lease, e := f.s.Store.acquireSource(context.Background(), r.Report.ID, uuid.NewString(), r.Revision)
	sourceRequire(t, e)
	if _, e = f.s.Store.acquireSource(context.Background(), r.Report.ID, uuid.NewString(), r.Revision); !errors.Is(e, ErrEvaluationActive) {
		t.Fatalf("concurrent writer accepted %v", e)
	}
	_, e = f.s.Store.DB.Exec(context.Background(), "UPDATE source_import SET deadline_at=clock_timestamp()-interval '1 second' WHERE id=$1", r.Report.ID)
	sourceRequire(t, e)
	if e = f.s.Store.checkpointSource(context.Background(), &lease, false); !errors.Is(e, ErrEvaluationLease) {
		t.Fatalf("late writer accepted %v", e)
	}
	if _, e = f.s.Store.acquireSource(context.Background(), r.Report.ID, uuid.NewString(), 999); !errors.Is(e, ErrRevision) {
		t.Fatalf("stale revision accepted %v", e)
	}
}
func TestNativeSourceHistoryPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	key := uuid.NewString()
	first, e := f.s.Store.RunSourceImport(context.Background(), r.Report.ID, key, 0)
	sourceRequire(t, e)
	second, e := f.s.Store.RunSourceImport(context.Background(), r.Report.ID, key, 0)
	sourceRequire(t, e)
	sourceAssert(t, first.Report, second.Report)
	sourceAssert(t, true, second.Replay)
	rows, next, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 2)
	sourceRequire(t, e)
	sourceAssert(t, 2, len(rows))
	if next == "" {
		t.Fatal("missing page cursor")
	}
	more, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, next, 2)
	sourceRequire(t, e)
	sourceAssert(t, 2, len(more))
	if rows[1]["member"] == more[0]["member"] && rows[1]["table"] == more[0]["table"] {
		t.Fatal("page repeated")
	}
	fresh := NewServer(f.s.Store, f.s.Origin, "http://unused.invalid")
	stored, e := fresh.Store.SourceImport(context.Background(), r.Report.ID)
	sourceRequire(t, e)
	sourceAssert(t, first.Report, stored.Report)
}
func TestNativeSourceHistoryNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "native", nil)
	if _, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "not-a-cursor", 2); !errors.Is(e, ErrInput) {
		t.Fatal("foreign cursor accepted")
	}
	sourceAssert(t, 404, f.request("GET", "/api/v1/imports/"+uuid.NewString(), nil, "", "").Code)
	var before int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM operation").Scan(&before))
	for i := 0; i < 3; i++ {
		sourceAssert(t, 200, f.request("GET", "/api/v1/imports/"+r.Report.ID, nil, "", "").Code)
	}
	var after int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM operation").Scan(&after))
	sourceAssert(t, before, after)
}
func (f *sourceNative) permission(t *testing.T) string {
	t.Helper()
	var docs []string
	for _, m := range f.files {
		if strings.Contains(m.Path, "licence") {
			docs = append(docs, m.AssetID)
		}
	}
	p := map[string]any{"schema_version": "2.0.0", "source_id": f.release.Source, "release_ids": []string{f.release.ID}, "grantee": "Constructed local operator", "grantor": "Constructed test notice", "uses": []string{"local_analysis"}, "scope_document_asset_ids": docs, "credential_ref": nil, "recipients": []any{}, "territories": []any{}, "valid_from": "2020-01-01T00:00:00Z", "valid_until": nil, "revoked_at": nil, "status": "permitted", "attester_person_id": nil}
	saved, e := f.s.Store.RegisterSourcePermission(context.Background(), sourceBytes(p))
	sourceRequire(t, e)
	return saved["id"].(string)
}
func TestNativeSourceRightsPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	id := f.permission(t)
	sourceRequire(t, f.s.Store.SourceUse(context.Background(), f.release.ID, []string{id}, "local_analysis"))
	r := f.run(t, "native", []string{id})
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	for _, row := range rows {
		if c, ok := row["corpus_record"].(map[string]any); ok {
			lic := c["licence"].(map[string]any)
			sourceAssert(t, []string{"local_analysis"}, lic["uses"])
			sourceAssert(t, "approved", lic["status"])
			sourceAssert(t, id, lic["rights_approval_id"])
		}
	}
}
func TestNativeSourceRightsNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	id := f.permission(t)
	if e := f.s.Store.SourceUse(context.Background(), f.release.ID, []string{id}, "derivative_exercises"); e == nil {
		t.Fatal("invented derivative permission")
	}
	sourceRequire(t, f.s.Store.RevokeSourcePermission(context.Background(), id, f.files[1].AssetID))
	if e := f.s.Store.SourceUse(context.Background(), f.release.ID, []string{id}, "local_analysis"); e == nil {
		t.Fatal("revoked permission retained")
	}
	r := f.run(t, "native", []string{id})
	sourceAssert(t, "complete", r.Report.State)
	sourceAssert(t, 200, f.request("GET", "/api/v1/library", nil, "", "").Code)
}
func TestNativeSourceSourcesPositive(t *testing.T) {
	f := sourceFixture(t)
	w := f.request("GET", "/api/v1/sources", nil, "", "")
	sourceAssert(t, 200, w.Code)
	var items []map[string]any
	sourceRequire(t, json.Unmarshal(w.Body.Bytes(), &items))
	sourceAssert(t, 11, len(items))
	for _, s := range items {
		_, _, e := contracts.Validate("source-status", "2.0.0", sourceBytes(s))
		sourceRequire(t, e)
		sourceAssert(t, "not_acquired", s["status"])
	}
	f.upload(t, "companion.csv", "writingID,SOC_scores\na,0.5\n")
	f.register(t, "EFCAMDAT-OKSUZ2025", "analysis_companion")
	r := f.run(t, "raw-only", nil)
	sourceAssert(t, true, r.Report.RawComplete)
	sourceAssert(t, false, r.Report.Normalized)
	sourceAssert(t, "1", r.Report.RawOnly)
}
func TestNativeSourceSourcesNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "raw-only", nil)
	sourceAssert(t, "6", r.Report.RawOnly)
	native := f.run(t, "native", nil)
	if r.Report.ID == native.Report.ID {
		t.Fatal("raw and native binding checkpoints mixed")
	}
	sourceAssert(t, "0", native.Report.RawOnly)
	if _, e := f.s.Store.createSourceImport(context.Background(), uuid.NewString(), "native", nil); e == nil {
		t.Fatal("missing release accepted")
	}
}
func TestNativeSourceCancelPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	lease, e := f.s.Store.acquireSource(context.Background(), r.Report.ID, uuid.NewString(), r.Revision)
	sourceRequire(t, e)
	r, e = f.s.Store.CancelSource(context.Background(), r.Report.ID, 0)
	sourceRequire(t, e)
	sourceAssert(t, "cancelled", r.Report.State)
	if e = f.s.Store.checkpointSource(context.Background(), &lease, false); !errors.Is(e, ErrEvaluationLease) {
		t.Fatal("cancelled writer published")
	}
	r, e = f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), r.Revision)
	sourceRequire(t, e)
	sourceAssert(t, "complete", r.Report.State)
}
func TestNativeSourceCancelNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "native", nil)
	if _, e := f.s.Store.CancelSource(context.Background(), r.Report.ID, r.Revision); !errors.Is(e, ErrConflict) {
		t.Fatal("complete import cancelled")
	}
	if _, e := f.s.Store.CancelSource(context.Background(), r.Report.ID, 0); !errors.Is(e, ErrRevision) {
		t.Fatal("stale cancellation accepted")
	}
}
func TestNativeSourceFailurePositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	_, e = f.s.Store.DB.Exec(context.Background(), `CREATE FUNCTION reject_source_row() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'test-owned source staging failure'; END $$; CREATE TRIGGER reject_source BEFORE INSERT ON source_row FOR EACH ROW EXECUTE FUNCTION reject_source_row()`)
	sourceRequire(t, e)
	failed, e := f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), 0)
	if e == nil {
		t.Fatal("test dependency failure did not occur")
	}
	sourceAssert(t, "failed", failed.Report.State)
	_, e = f.s.Store.DB.Exec(context.Background(), "DROP TRIGGER reject_source ON source_row")
	sourceRequire(t, e)
	fresh, e := f.s.Store.SourceImport(context.Background(), r.Report.ID)
	sourceRequire(t, e)
	recovered, e := f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), fresh.Revision)
	sourceRequire(t, e)
	sourceAssert(t, "complete", recovered.Report.State)
	sourceAssert(t, "6", recovered.Report.Observed)
	sourceAssert(t, true, recovered.Report.Normalized)
}
func TestNativeSourceFailureNegative(t *testing.T) {
	f := sourceFixture(t)
	f.upload(t, "bad.csv", "a,b\n\"unterminated")
	f.register(t, "NIR-DATA", "partial_export")
	r := f.run(t, "raw-only", nil)
	sourceAssert(t, false, r.Report.Normalized)
	if len(r.Report.Issues) == 0 {
		t.Fatal("bad native source silently complete")
	}
	r.Report.State = "parsing"
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_member WHERE release_id=$1", f.release.ID).Scan(new(int)))
}
func TestNativeSourceRemotePositive(t *testing.T) {
	f := sourceFixture(t)
	var calls atomic.Int32
	remote := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls.Add(1)
		if r.URL.Query().Get("cursor") == "second" {
			_, _ = io.WriteString(w, `{"items":[{"id":"b","original":"Second"}],"next":null,"done":true,"total":2}`)
		} else {
			_, _ = io.WriteString(w, `{"items":[{"id":"a","original":"First","unknown":17}],"next":"second","done":false,"total":2}`)
		}
	}))
	defer remote.Close()
	id := uuid.NewString()
	spec := source.RemoteSpec{Endpoint: remote.URL, Method: "GET", Headers: map[string]string{}, Query: map[string]string{}, Body: map[string]any{}, CursorField: "cursor", CursorLocation: "query", RecordsPointer: "/items", NextPointer: "/next", EndPointer: "/done", EndValue: true, TotalPointer: "/total", DatasetVersion: "native-fixture", CountUnit: "records", IdentityPointer: "/id"}
	config := map[string]any{"source_id": "NIR-DATA", "allowed_hosts": []string{"127.0.0.1"}, "remote_spec": spec}
	_, e := f.s.Store.DB.Exec(context.Background(), "INSERT INTO source_connector(id,source_id,payload) VALUES($1,'NIR-DATA',$2)", id, sourceBytes(config))
	sourceRequire(t, e)
	p, e := f.s.FetchSourceExport(context.Background(), id, remote.Client())
	sourceRequire(t, e)
	sourceAssert(t, true, p.Complete)
	sourceAssert(t, int64(2), p.Count)
	sourceAssert(t, 4, len(p.Files))
	_, e = f.s.FetchSourceExport(context.Background(), id, remote.Client())
	sourceRequire(t, e)
	sourceAssert(t, 2, int(calls.Load()))
}
func TestNativeSourceRemoteNegative(t *testing.T) {
	f := sourceFixture(t)
	remote := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, _ = io.WriteString(w, `{"items":[{"id":"same"}],"next":"cycle","done":false}`)
	}))
	defer remote.Close()
	id := uuid.NewString()
	spec := source.RemoteSpec{Endpoint: remote.URL, Method: "GET", Headers: map[string]string{}, Query: map[string]string{}, Body: map[string]any{}, CursorField: "cursor", CursorLocation: "query", RecordsPointer: "/items", NextPointer: "/next", EndPointer: "/done", EndValue: true, DatasetVersion: "native-fixture", CountUnit: "records", IdentityPointer: "/id"}
	config := map[string]any{"source_id": "NIR-DATA", "allowed_hosts": []string{"127.0.0.1"}, "remote_spec": spec}
	_, e := f.s.Store.DB.Exec(context.Background(), "INSERT INTO source_connector(id,source_id,payload) VALUES($1,'NIR-DATA',$2)", id, sourceBytes(config))
	sourceRequire(t, e)
	p, e := f.s.FetchSourceExport(context.Background(), id, remote.Client())
	if e == nil {
		t.Fatal("pagination cycle accepted")
	}
	sourceAssert(t, false, p.Complete)
	sourceAssert(t, 2, p.Pages)
}
func TestNativeSourceArchivePositive(t *testing.T) {
	f := sourceFixture(t)
	var b bytes.Buffer
	z := zip.NewWriter(&b)
	for _, name := range []string{"readme.txt", "nested/data.jsonl", "script.py"} {
		w, _ := z.Create(name)
		_, _ = io.WriteString(w, "inert")
	}
	sourceRequire(t, z.Close())
	files, e := f.s.Store.IntakeArchive(context.Background(), "all.zip", "zip", &b)
	sourceRequire(t, e)
	sourceAssert(t, 4, len(files))
	sourceAssert(t, "all.zip", files[3].Path)
}
func TestNativeSourceArchiveNegative(t *testing.T) {
	f := sourceFixture(t)
	var b bytes.Buffer
	z := zip.NewWriter(&b)
	w, _ := z.Create("../escape")
	_, _ = io.WriteString(w, "inert")
	sourceRequire(t, z.Close())
	if _, e := f.s.Store.IntakeArchive(context.Background(), "bad.zip", "zip", &b); e == nil {
		t.Fatal("unsafe archive accepted")
	}
	var count int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_file").Scan(&count))
	sourceAssert(t, 0, count)
}
func TestNativeSourceReviewTermsPositive(t *testing.T) {
	local := map[string]any{"source_id": "FCE-2.1", "source_record_id": nil, "rights_approval_id": nil, "uses": []any{"local_analysis"}, "status": "approved", "licence_evidence_hash": nil}
	key := map[string]any{"audio": map[string]any{"source_profile_id": "FCE-2.1"}, "units": []any{map[string]any{"utterance_ids": []any{"u1"}, "source": local}}}
	sourceAssert(t, local, reviewUnitSource(key, map[string]any{"utterance_ids": []any{"u1"}}))
}
func TestNativeSourceReviewTermsNegative(t *testing.T) {
	key := map[string]any{"audio": map[string]any{"source_profile_id": "FCE-2.1"}, "units": []any{map[string]any{"utterance_ids": []any{"u1"}, "source": map[string]any{"uses": []any{"local_analysis"}}}}}
	actual := reviewUnitSource(key, map[string]any{"utterance_ids": []any{"u2"}})
	sourceAssert(t, []any{}, actual["uses"])
	sourceAssert(t, "pending", actual["status"])
}

var _ = time.Second
var _ = fmt.Sprint

func (f *sourceNative) mapping(t *testing.T, bad bool) string {
	t.Helper()
	f.upload(t, "records.jsonl", "{\"id\":\"r1\",\"response\":\"A café opens.\",\"scale\":\"0.12500\",\"unknown\":{\"retained\":true}}\n")
	f.upload(t, "labels.jsonl", "{\"record\":\"r1\",\"label\":\"native-one\"}\n{\"record\":\"r1\",\"label\":\"native-two\"}\n")
	f.upload(t, "dictionary.txt", "Constructed dictionary declares response text, native decimal scale and multiple source annotations. Not an unseen vendor export.")
	f.upload(t, "terms.txt", "Constructed terms retain source-specific metadata; no inferred rights.")
	f.register(t, "MOODRICK-DATA", "full_named_release")
	cardinality := "many"
	if bad {
		cardinality = "one"
	}
	program := map[string]any{"schema_version": "2.0.0", "id": "documented-fixture-v1", "source_id": f.release.Source, "release_id": f.release.ID, "raw_manifest_sha256": f.release.Manifest, "dictionary_asset_ids": []string{f.files[2].AssetID}, "tables": []any{map[string]any{"name": "records", "member_glob": "records.jsonl", "format": "jsonl", "selector": "records", "encoding": "utf-8", "delimiter": nil, "has_header": false}, map[string]any{"name": "annotations", "member_glob": "labels.jsonl", "format": "jsonl", "selector": "records", "encoding": "utf-8", "delimiter": nil, "has_header": false}}, "record_table": "records", "identity": map[string]any{"table": "records", "pointer": "/value/id"}, "joins": []any{map[string]any{"left_table": "records", "left_pointer": "/value/id", "right_table": "annotations", "right_pointer": "/value/record", "cardinality": cardinality, "required": true}}, "projections": []any{map[string]any{"from": map[string]any{"table": "records", "pointer": "/value/response"}, "to": "/corpus_record/text", "conversion": "identity", "null_values": []any{}, "required": true}, map[string]any{"from": map[string]any{"table": "records", "pointer": "/value/scale"}, "to": "/raw_metadata/scale", "conversion": "decimal", "null_values": []any{}, "required": true}}, "span_origin": "zero_based_half_open", "sample_rate_hz": 16000, "unmapped_fields": "retain_raw", "repeated_projections": []any{map[string]any{"table": "annotations", "to": "/raw_metadata/annotations", "fields": []any{map[string]any{"from": map[string]any{"table": "annotations", "pointer": "/value/label"}, "to": "/label", "conversion": "identity", "null_values": []any{}, "required": true}}}}}
	input := map[string]any{"schema_version": "2.0.0", "source_id": f.release.Source, "release_version": f.release.Release, "documentation_asset_ids": []string{f.files[2].AssetID}, "input_format": "vendor_export", "record_selector": "records", "fields": []any{map[string]any{"source_path": "/value/response", "target_field": "text", "required": true, "conversion": "identity", "null_values": []any{}}}, "label_map_asset_id": nil, "review_person_id": nil, "reviewed_at": "2026-10-21T00:00:00Z", "origin": "source_import", "provider_receipt_ids": []any{}, "input_modality": "native_annotation", "mapping_program": program}
	binding, e := f.s.Store.RegisterFormat(context.Background(), sourceBytes(input))
	sourceRequire(t, e)
	return binding["id"].(string)
}
func TestNativeSourceMappingPositive(t *testing.T) {
	f := sourceFixture(t)
	binding := f.mapping(t, false)
	r := f.run(t, binding, nil)
	sourceAssert(t, "3", r.Report.Observed)
	sourceAssert(t, "0", r.Report.RawOnly)
	sourceAssert(t, true, r.Report.Normalized)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	for _, row := range rows {
		if row["table"] == "records" {
			projection := row["projection"].(map[string]any)
			scale, _ := source.Pointer(projection, "/raw_metadata/scale")
			sourceAssert(t, json.Number("0.12500"), scale)
			annotations, _ := source.Pointer(projection, "/raw_metadata/annotations")
			sourceAssert(t, 2, len(annotations.([]any)))
			corpus := row["corpus_record"].(map[string]any)
			sourceAssert(t, "A café opens.", corpus["text"])
			raw := row["raw_record"].(map[string]any)
			if !strings.Contains(string(sourceBytes(raw)), "retained") {
				t.Fatal("unknown native data lost")
			}
		}
	}
}
func TestNativeSourceMappingNegative(t *testing.T) {
	f := sourceFixture(t)
	binding := f.mapping(t, true)
	r := f.run(t, binding, nil)
	sourceAssert(t, "1", r.Report.RawOnly)
	sourceAssert(t, false, r.Report.Normalized)
	sourceAssert(t, "3", r.Report.Accepted)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	for _, row := range rows {
		if row["table"] == "records" {
			sourceAssert(t, nil, row["corpus_record"])
			if len(row["issues"].([]any)) == 0 {
				t.Fatal("ambiguous native join silently accepted")
			}
		}
	}
	p, _, e := f.s.Store.sourceBinding(context.Background(), binding)
	sourceRequire(t, e)
	p["source_id"] = "NIR-DATA"
	delete(p, "id")

	if _, e = f.s.Store.RegisterFormat(context.Background(), sourceBytes(p)); e == nil {
		t.Fatal("foreign binding without valid source evidence accepted")
	}
}

func TestNativeSourceNestedArchivePositive(t *testing.T) {
	f := sourceFixture(t)
	var inner bytes.Buffer
	z := zip.NewWriter(&inner)
	w, _ := z.Create("ABA/transcript/a.txt")
	_, _ = io.WriteString(w, "Native text")
	sourceRequire(t, z.Close())
	var outer bytes.Buffer
	z = zip.NewWriter(&outer)
	w, _ = z.Create("ABA.zip")
	_, _ = w.Write(inner.Bytes())
	sourceRequire(t, z.Close())
	members, e := f.s.Store.IntakeArchive(context.Background(), "all.zip", "zip", &outer)
	sourceRequire(t, e)
	sourceAssert(t, 3, len(members))
	sourceAssert(t, "ABA.zip/ABA/transcript/a.txt", members[0].Path)
	sourceAssert(t, "ABA.zip", members[1].Path)
	sourceAssert(t, "all.zip", members[2].Path)
}
func TestNativeSourceNestedArchiveNegative(t *testing.T) {
	f := sourceFixture(t)
	var inner bytes.Buffer
	z := zip.NewWriter(&inner)
	w, _ := z.Create("../escape")
	_, _ = io.WriteString(w, "inert")
	sourceRequire(t, z.Close())
	var outer bytes.Buffer
	z = zip.NewWriter(&outer)
	w, _ = z.Create("unsafe.zip")
	_, _ = w.Write(inner.Bytes())
	sourceRequire(t, z.Close())
	if _, e := f.s.Store.IntakeArchive(context.Background(), "all.zip", "zip", &outer); e == nil {
		t.Fatal("unsafe nested archive admitted")
	}
}

func TestNativeSourceFullScopeNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), r.Report.ID))
	statuses, e := f.s.Store.SourceStatuses(context.Background())
	sourceRequire(t, e)
	for _, status := range statuses {
		if status["source_id"] == "FCE-2.1" {
			sourceAssert(t, "incomplete", status["status"])
			if len(status["missing_component_names"].([]string)) == 0 {
				t.Fatal("constructed three-sentence bank certified as full source")
			}
		}
	}

}

func sourceRemoteInput(spec source.RemoteSpec) map[string]any {
	return map[string]any{"schema_version": "2.0.0", "source_id": "NIR-DATA", "mode": "authorized_https_export", "account_label": "Owned fixture", "credential_ref": nil, "contract_asset_ids": []string{}, "adapter_id": nil, "adapter_sha256": nil, "allowed_hosts": []string{"127.0.0.1"}, "selected_use": []string{"local_analysis"}, "remote_spec": spec}
}
func TestNativeSourceConnectorPositive(t *testing.T) {
	f := sourceFixture(t)
	f.s.Providers.Dir = t.TempDir()
	var observed string
	remote := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		observed = r.Header.Get("Authorization")
		_, _ = io.WriteString(w, `{"items":[{"id":"one"}],"next":null,"done":true,"total":1}`)
	}))
	defer remote.Close()
	id := uuid.NewString()
	spec := source.RemoteSpec{Endpoint: remote.URL, Method: "GET", Headers: map[string]string{}, Query: map[string]string{}, Body: map[string]any{}, CursorField: "cursor", CursorLocation: "query", RecordsPointer: "/items", NextPointer: "/next", EndPointer: "/done", EndValue: true, TotalPointer: "/total", DatasetVersion: "fixture-v1", CountUnit: "records", AuthHeader: "Authorization", AuthPrefix: "Bearer "}
	input := sourceRemoteInput(spec)
	input["credential_value"] = "owned-source-secret"
	w := f.request("PUT", "/api/v1/connectors/"+id, sourceBytes(input), "", "")
	sourceAssert(t, 200, w.Code)
	sourceAssert(t, "0", w.Header().Get("ETag"))
	_, _, validation := contracts.Validate("source-status", "2.0.0", w.Body.Bytes())
	sourceRequire(t, validation)
	if strings.Contains(w.Body.String(), "secret") {
		t.Fatal("secret in response")
	}
	p, e := f.s.FetchSourceExport(context.Background(), id, remote.Client())
	sourceRequire(t, e)
	sourceAssert(t, true, p.Complete)
	sourceAssert(t, "Bearer owned-source-secret", observed)
}
func TestNativeSourceConnectorNegative(t *testing.T) {
	f := sourceFixture(t)
	f.s.Providers.Dir = t.TempDir()
	id := uuid.NewString()
	spec := source.RemoteSpec{Endpoint: "https://127.0.0.1/export", Method: "GET", Headers: map[string]string{}, Query: map[string]string{}, Body: map[string]any{}, CursorField: "cursor", CursorLocation: "query", RecordsPointer: "/items", NextPointer: "/next", EndPointer: "/done", EndValue: true, DatasetVersion: "fixture-v1", CountUnit: "records", IdentityPointer: "/id"}
	input := sourceRemoteInput(spec)
	input["credential_value"] = "initial-secret"
	sourceAssert(t, 200, f.request("PUT", "/api/v1/connectors/"+id, sourceBytes(input), "", "").Code)
	input["credential_value"] = "current-secret"
	sourceAssert(t, 200, f.request("PUT", "/api/v1/connectors/"+id, sourceBytes(input), "", "0").Code)
	input["credential_value"] = "stale-secret"
	sourceAssert(t, 409, f.request("PUT", "/api/v1/connectors/"+id, sourceBytes(input), "", "0").Code)
	var payload []byte
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT payload FROM source_connector WHERE id=$1", id).Scan(&payload))
	var saved map[string]any
	sourceRequire(t, source.Decode(payload, &saved))
	name, e := sourceCredentialName(id, saved["credential_ref"].(string))
	sourceRequire(t, e)
	bytes, e := os.ReadFile(f.s.Providers.Dir + "/" + name)
	sourceRequire(t, e)
	sourceAssert(t, "current-secret", string(bytes))
	other := uuid.NewString()
	if _, e = sourceCredentialName(other, saved["credential_ref"].(string)); e == nil {
		t.Fatal("foreign connector credential admitted")
	}
}
func TestNativeSourceRemoteResumePositive(t *testing.T) {
	f := sourceFixture(t)
	var stage atomic.Int32
	var first atomic.Int32
	var second atomic.Int32
	remote := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Query().Get("cursor") == "second" {
			second.Add(1)
			if stage.Load() == 0 {
				w.WriteHeader(503)
				return
			}
			_, _ = io.WriteString(w, `{"items":[{"id":"b"}],"next":null,"done":true,"total":2}`)
		} else {
			first.Add(1)
			_, _ = io.WriteString(w, `{"items":[{"id":"a"}],"next":"second","done":false,"total":2}`)
		}
	}))
	defer remote.Close()
	id := uuid.NewString()
	spec := source.RemoteSpec{Endpoint: remote.URL, Method: "GET", Query: map[string]string{}, Headers: map[string]string{}, Body: map[string]any{}, CursorField: "cursor", CursorLocation: "query", RecordsPointer: "/items", NextPointer: "/next", EndPointer: "/done", EndValue: true, TotalPointer: "/total", DatasetVersion: "fixture-v1", CountUnit: "records", IdentityPointer: "/id"}
	_, e := f.s.Store.DB.Exec(context.Background(), "INSERT INTO source_connector(id,source_id,payload) VALUES($1,'NIR-DATA',$2)", id, sourceBytes(sourceRemoteInput(spec)))
	sourceRequire(t, e)
	partial, e := f.s.FetchSourceExport(context.Background(), id, remote.Client())
	if e == nil {
		t.Fatal("remote failure missing")
	}
	sourceAssert(t, 1, partial.Pages)
	sourceAssert(t, 2, int(second.Load()))
	stage.Store(1)
	done, e := f.s.FetchSourceExport(context.Background(), id, remote.Client())
	sourceRequire(t, e)
	sourceAssert(t, true, done.Complete)
	sourceAssert(t, 1, int(first.Load()))
	sourceAssert(t, int64(2), done.Count)
	sourceAssert(t, 4, len(done.Files))
}
func TestNativeSourceRemoteConflictNegative(t *testing.T) {
	f := sourceFixture(t)
	remote := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Query().Get("cursor") == "next" {
			_, _ = io.WriteString(w, `{"items":[{"id":"a","text":"conflict"}],"next":null,"done":true,"total":2}`)
		} else {
			_, _ = io.WriteString(w, `{"items":[{"id":"a","text":"original"}],"next":"next","done":false,"total":2}`)
		}
	}))
	defer remote.Close()
	id := uuid.NewString()
	spec := source.RemoteSpec{Endpoint: remote.URL, Method: "GET", CursorField: "cursor", CursorLocation: "query", RecordsPointer: "/items", NextPointer: "/next", EndPointer: "/done", EndValue: true, TotalPointer: "/total", DatasetVersion: "fixture", CountUnit: "records", IdentityPointer: "/id"}
	_, e := f.s.Store.DB.Exec(context.Background(), "INSERT INTO source_connector(id,source_id,payload) VALUES($1,'NIR-DATA',$2)", id, sourceBytes(sourceRemoteInput(spec)))
	sourceRequire(t, e)
	p, e := f.s.FetchSourceExport(context.Background(), id, remote.Client())
	if e == nil {
		t.Fatal("conflicting native identity silently complete")
	}
	sourceAssert(t, 4, len(p.Files))
	sourceAssert(t, "identity_conflict", p.Failure)
	sourceAssert(t, 1, len(p.Conflicts))
	sourceAssert(t, int64(2), p.Count)
}
func TestNativeSourceIssuesPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "native", nil)
	for i := 0; i < 1003; i++ {
		loc := fmt.Sprintf("row/%04d", i)
		if i%2 == 0 {
			loc = "row/" + loc
		}
		sourceRequire(t, f.s.Store.sourceIssue(context.Background(), r, source.Issue{loc, "native_notice", "Independent located issue"}))
	}
	all := []source.Issue{}
	cursor := ""
	for {
		items, next, e := f.s.Store.SourceIssues(context.Background(), r.Report.ID, cursor)
		sourceRequire(t, e)
		all = append(all, items...)
		if next == "" {
			break
		}
		cursor = next
	}
	sourceAssert(t, 1003, len(all))
	seen := map[string]bool{}
	for _, i := range all {
		if seen[i.Locator] {
			t.Fatal("issue page duplicated")
		}
		seen[i.Locator] = true
	}
	sourceRequire(t, f.s.Store.sourceSummary(context.Background(), &r))
	sourceRequire(t, f.s.Store.sourceIssueAsset(context.Background(), &r))
	if r.Report.FullIssues == nil {
		t.Fatal("full issue asset missing")
	}
}
func TestNativeSourceIssuesNegative(t *testing.T) {
	f := sourceFixture(t)
	if _, _, e := f.s.Store.SourceIssues(context.Background(), uuid.NewString(), `["broken"]`); e == nil {
		t.Fatal("invalid issue cursor accepted")
	}
}

func TestNativeSourceUpgradePositive(t *testing.T) {
	s := sourceStoreVersion(t, 6)
	ctx := context.Background()
	id := uuid.NewString()
	_, e := s.DB.Exec(ctx, "INSERT INTO exercise_catalog(id,title,published_at,source_revision,audio_sha256) VALUES($1,'Preserved baseline library',now(),'pre-imports',$2)", id, strings.Repeat("a", 64))
	sourceRequire(t, e)
	sourceRequire(t, s.Migrate(ctx))
	sourceRequire(t, s.Migrate(ctx))
	var title string
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT title FROM exercise_catalog WHERE id=$1", id).Scan(&title))
	sourceAssert(t, "Preserved baseline library", title)
	var count int
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM schema_migrations").Scan(&count))
	sourceAssert(t, 7, count)
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row").Scan(&count))
	sourceAssert(t, 0, count)
}
func TestNativeSourceUpgradeNegative(t *testing.T) {
	s := sourceStoreVersion(t, 6)
	ctx := context.Background()
	_, e := s.DB.Exec(ctx, "CREATE TABLE source_file(test_owned_conflict text)")
	sourceRequire(t, e)
	if s.Migrate(ctx) == nil {
		t.Fatal("conflicting upgrade did not fail")
	}
	var n int
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM schema_migrations").Scan(&n))
	sourceAssert(t, 6, n)
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM workspaces").Scan(&n))
	sourceAssert(t, 1, n)
	_, e = s.DB.Exec(ctx, "DROP TABLE source_file")
	sourceRequire(t, e)
	sourceRequire(t, s.Migrate(ctx))
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM schema_migrations").Scan(&n))
	sourceAssert(t, 7, n)
}

// Replayable event order, real storage and API owners. The model only knows
// literal six native rows and whether explicit publication happened. Native I/O
// scheduling is outside the deterministic shuffle; no shrinking is claimed.
func sourceSequence(t *testing.T, seed int64) {
	f := sourceFixture(t)
	f.bea(t)
	run, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	key := uuid.NewString()
	run, e = f.s.Store.RunSourceImport(context.Background(), run.Report.ID, key, 0)
	sourceRequire(t, e)
	events := []string{"publish", "read", "replay", "stale", "publish", "read", "replay", "stale"}
	rand.New(rand.NewSource(seed)).Shuffle(len(events), func(i, j int) { events[i], events[j] = events[j], events[i] })
	published := false
	seen := map[string]int{}
	for index, event := range events {
		t.Logf("seed=%d event=%d trace=%v", seed, index, events)
		switch event {
		case "publish":
			sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
			published = true
			seen["publish/applied"]++
		case "read":
			rows, _, e := f.s.Store.SourceRows(context.Background(), run.Report.ID, "", 20)
			sourceRequire(t, e)
			sourceAssert(t, 6, len(rows))
			seen["read/observed_no_mutation"]++
		case "replay":
			again, e := f.s.Store.RunSourceImport(context.Background(), run.Report.ID, key, 0)
			sourceRequire(t, e)
			sourceAssert(t, true, again.Replay)
			sourceAssert(t, "6", again.Report.Observed)
			seen["replay/observed_no_mutation"]++
		case "stale":
			_, e := f.s.Store.RunSourceImport(context.Background(), run.Report.ID, uuid.NewString(), 0)
			if !errors.Is(e, ErrRevision) {
				t.Fatalf("stale event:%v", e)
			}
			seen["stale/observed_no_mutation"]++
		}
		var actual bool
		sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT published FROM source_import WHERE id=$1", run.Report.ID).Scan(&actual))
		sourceAssert(t, published, actual)
		var n int
		sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID).Scan(&n))
		sourceAssert(t, 6, n)
	}
	for _, required := range []string{"publish/applied", "read/observed_no_mutation", "replay/observed_no_mutation", "stale/observed_no_mutation"} {
		if seen[required] != 2 {
			t.Fatalf("required event disposition absent%s", required)
		}
	}
}
func TestNativeSourceSequencePositive(t *testing.T) {
	for seed := int64(1); seed <= 8; seed++ {
		t.Run(fmt.Sprint(seed), func(t *testing.T) { sourceSequence(t, seed) })
	}
}
func TestNativeSourceSequenceNegative(t *testing.T) {
	for seed := int64(101); seed <= 108; seed++ {
		t.Run(fmt.Sprint(seed), func(t *testing.T) { sourceSequence(t, seed) })
	}
}
func TestNativeSourceCountsPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "native", nil)
	three := "3"
	r.Frozen.Release.Expected = []SourceCount{{Unit: "sentences", Value: &three}}
	complete, e := f.s.Store.sourceExpectedCounts(context.Background(), &r, f.files)
	sourceRequire(t, e)
	sourceAssert(t, true, complete)
	sourceAssert(t, "3", r.Report.Components[len(r.Report.Components)-1].Observed)
}
func TestNativeSourceCountsNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "native", nil)
	four := "4"
	r.Frozen.Release.Expected = []SourceCount{{Unit: "sentences", Value: &four}, {Unit: "guessed-population", Value: nil}}
	complete, e := f.s.Store.sourceExpectedCounts(context.Background(), &r, f.files)
	sourceRequire(t, e)
	sourceAssert(t, false, complete)
	items, _, e := f.s.Store.SourceIssues(context.Background(), r.Report.ID, "")
	sourceRequire(t, e)
	codes := map[string]bool{}
	for _, i := range items {
		codes[i.Code] = true
	}
	sourceAssert(t, true, codes["count_mismatch"])
	sourceAssert(t, true, codes["count_unbound"])
}
func TestNativeSourceTransformationPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "native", nil)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	for _, row := range rows {
		transform := row["transformation"].(map[string]any)
		_, _, e := contracts.Validate("transformation", "2.0.0", sourceBytes(transform))
		sourceRequire(t, e)
		sourceAssert(t, []any{}, transform["output_sha256s"])
		sourceAssert(t, []any{}, transform["output_asset_ids"])
		sourceAssert(t, r.Frozen.MethodSHA, transform["method_sha256"])
		sourceAssert(t, 1, len(transform["input_sha256s"].([]any)))
	}
}
func TestNativeSourceTransformationNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r := f.run(t, "raw-only", nil)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	for _, row := range rows {
		sourceAssert(t, nil, row["corpus_record"])
		raw := row["raw_record"].(map[string]any)
		sourceAssert(t, "unmapped", raw["interpretation_status"])
		if row["transformation"] == nil {
			t.Fatal("unmapped original lost parse provenance")
		}
	}
}

func sourceGoldBank(t *testing.T) (*sourceNative, SourceRun, []source.Member) {
	t.Helper()
	f := sourceFixture(t)
	f.upload(t, "gold/dictionary.txt", "Constructed accounting fixture only:122x6conditions. It does not establish semantic gold quality.")
	f.register(t, "TET-GOLD-1", "full_named_release")
	run, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "raw-only", nil)
	sourceRequire(t, e)
	key, _, _ := reviewKeyFixture(t)
	key["variety_policy"] = map[string]any{"target_locale": "en-US", "accepted_varieties": []any{"en-US"}, "register": "neutral", "assessment_basis": "explicit_target_form", "public_constraints": "Judge the supplied public language context."}

	raw, _ := generationRegistry("mutation-recipes.v1.json")
	var registry map[string]any
	sourceRequire(t, source.Decode(raw, &registry))
	recipes := registry["recipes"].([]any)
	sourceAssert(t, 122, len(recipes))
	hash := strings.Repeat("a", 64)
	for leaf, v := range recipes {
		recipe := v.(map[string]any)
		for i := 0; i < 6; i++ {
			current := reviewClone(key)
			current["public_context"] = fmt.Sprintf("Constructed accounting %d %d", leaf, i)
			unit := current["units"].([]any)[0].(map[string]any)
			unit["primary_taxonomy_id"] = recipe["taxonomy_id"]
			unit["domain"] = recipe["reporting_domain"]
			role := "positive"
			if i%2 == 1 {
				role = "control"
			}
			split := fmt.Sprintf("split%d", i/2)
			gold := map[string]any{"ground_truth": current, "pair_id": fmt.Sprintf("pair%d", leaf), "pair_role": role, "split": split, "group_ids": []any{fmt.Sprintf("g%d-%s", leaf, split)}, "label_origin": "source_import"}
			if _, e := sourceGoldAdmission(gold); e != nil {
				t.Fatal(e)
			}
			_, e = f.s.Store.DB.Exec(context.Background(), "INSERT INTO source_row(import_id,member,table_name,ordinal,native_row,projection,state) VALUES($1,'gold.jsonl','records',$2,'{}',$3,'mapped')", run.Report.ID, leaf*6+i, sourceBytes(map[string]any{"raw_metadata": map[string]any{"gold": gold}}))
			sourceRequire(t, e)
		}
	}
	// Media metadata has its own WAVE intake proof. Here a declared accepted media
	// receipt is the dependency of the gold-population accounting owner.
	members := []source.Member{{Path: "actual.wav", SHA: hash, Media: map[string]any{"sample_rate_hz": 24000}}}
	return f, run, members
}
func TestNativeSourceGoldPositive(t *testing.T) {
	f, run, members := sourceGoldBank(t)
	missing, e := f.s.Store.sourceGoldMissing(context.Background(), run.Report.ID, members)
	sourceRequire(t, e)
	sourceAssert(t, []string{}, missing)
}
func TestNativeSourceGoldNegative(t *testing.T) {
	f, run, members := sourceGoldBank(t)
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE source_row SET projection=jsonb_set(projection,'{raw_metadata,gold,group_ids}', '[\"cross-split-shared\"]') WHERE import_id=$1", run.Report.ID)
	sourceRequire(t, e)
	missing, e := f.s.Store.sourceGoldMissing(context.Background(), run.Report.ID, members)
	sourceRequire(t, e)
	found := false
	for _, m := range missing {
		found = found || strings.Contains(m, "overlap")
	}
	sourceAssert(t, true, found)
	members = nil
	missing, e = f.s.Store.sourceGoldMissing(context.Background(), run.Report.ID, members)
	sourceRequire(t, e)
	if len(missing) == 0 {
		t.Fatal("unavailable recordings counted as playable gold")
	}
}

func TestNativeSourcePrivateScopePositive(t *testing.T) {
	for _, id := range []string{"DOUBAO-STUDY-RECORDS", "MOODRICK-DATA", "NIR-DATA", "EFCAMDAT-SHATZ2020", "EFCAMDAT-OKSUZ2025"} {
		t.Run(id, func(t *testing.T) {
			f := sourceFixture(t)
			filename := "export.jsonl"
			sourcePath := "/value/response"
			inputFormat := "vendor_export"
			selector := "records"
			if strings.HasPrefix(id, "EFCAMDAT-") {
				filename = "original.xlsx"
				sourcePath = "/cells/0/value"
				inputFormat = "xlsx"
				selector = "Native"
				var b bytes.Buffer
				z := zip.NewWriter(&b)
				for name, value := range map[string]string{"xl/workbook.xml": `<workbook xmlns:r="urn:r"><sheets><sheet name="Native" r:id="r1" state="hidden"/></sheets></workbook>`, "xl/_rels/workbook.xml.rels": `<Relationships><Relationship Id="r1" Target="worksheets/sheet1.xml"/></Relationships>`, "xl/worksheets/sheet1.xml": `<worksheet><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>Exact private export</t></is></c><c r="B1"><f>1+2</f><v>3</v></c></row></sheetData></worksheet>`} {
					w, _ := z.Create(name)
					_, _ = io.WriteString(w, value)
				}
				sourceRequire(t, z.Close())
				m, e := f.s.Store.saveSourceStream(context.Background(), filename, &b)
				sourceRequire(t, e)
				f.files = append(f.files, m)
			} else {
				f.upload(t, filename, "{\"response\":\"Exact private export\",\"unknown\":\"retained\"}\n")
			}
			f.upload(t, "dictionary.txt", "Constructed explicit field dictionary for interpreter qualification. Not actual private-source conformance.")
			f.upload(t, "terms.txt", "Constructed no-transfer metadata")
			f.register(t, id, "partial_export")
			binding, e := f.s.Store.RegisterFormat(context.Background(), sourceBytes(map[string]any{"schema_version": "2.0.0", "source_id": id, "release_version": f.release.Release, "documentation_asset_ids": []string{f.files[1].AssetID}, "input_format": inputFormat, "record_selector": selector, "fields": []any{map[string]any{"source_path": sourcePath, "target_field": "text", "required": true, "conversion": "identity", "null_values": []any{}}}, "label_map_asset_id": nil}))
			sourceRequire(t, e)
			r := f.run(t, binding["id"].(string), nil)
			rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
			sourceRequire(t, e)
			sourceAssert(t, 1, len(rows))
			c := rows[0]["corpus_record"].(map[string]any)
			sourceAssert(t, id, c["source_id"])
			sourceAssert(t, "Exact private export", c["text"])
			sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), r.Report.ID))
			statuses, e := f.s.Store.SourceStatuses(context.Background())
			sourceRequire(t, e)
			for _, v := range statuses {
				if v["source_id"] == id && v["status"] == "complete" {
					t.Fatal("constructed private export certified full original")
				}
			}
		})
	}
}
func TestNativeSourcePrivateScopeNegative(t *testing.T) {
	for _, id := range []string{"DOUBAO-STUDY-RECORDS", "MOODRICK-DATA", "NIR-DATA", "EFCAMDAT-SHATZ2020", "EFCAMDAT-OKSUZ2025"} {
		t.Run(id, func(t *testing.T) {
			f := sourceFixture(t)
			f.upload(t, "export.jsonl", "{\"response\":\"Exact private export\"}\n")
			f.register(t, id, "partial_export")
			r := f.run(t, "native", nil)
			sourceAssert(t, false, r.Report.Normalized)
			sourceAssert(t, "1", r.Report.RawOnly)
			rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
			sourceRequire(t, e)
			sourceAssert(t, nil, rows[0]["corpus_record"])
		})
	}
}
func TestNativeSourceEfcamdatPositive(t *testing.T) {
	f := sourceFixture(t)
	f.upload(t, "release.xml", `<selection><writings><writing id="one"><learner id="genuine-one" nationality="unknown"/><text>A café <change><selection>opens.</selection><tag>R:VERB</tag><correct>suggestion</correct></change></text></writing></writings></selection>`)
	f.upload(t, "dictionary.txt", "Constructed native R2 XML structure; suggestions are excluded from original.")
	f.register(t, "EFCAMDAT-R2", "partial_export")
	r := f.run(t, "native", nil)
	sourceAssert(t, "1", r.Report.Accepted)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	c := rows[0]["corpus_record"].(map[string]any)
	sourceAssert(t, "A café opens.", c["text"])
	if c["l1"] != nil {
		t.Fatal("nationality invented as L1")
	}
}
func TestNativeSourceEfcamdatNegative(t *testing.T) {
	f := sourceFixture(t)
	f.upload(t, "release.xml", `<!DOCTYPE selection [<!ENTITY x SYSTEM "https://no-request.invalid/secret">]><selection><writings><writing><text>&x;</text></writing></writings></selection>`)
	f.upload(t, "dictionary.txt", "Constructed native fixture")
	f.register(t, "EFCAMDAT-R2", "partial_export")
	r := f.run(t, "native", nil)
	sourceAssert(t, false, r.Report.Normalized)
	if len(r.Report.Issues) == 0 {
		t.Fatal("external entity silently accepted")
	}
}

func sourceOrderingFixture(t *testing.T) *sourceNative {
	f := sourceFixture(t)
	for _, name := range []string{"A.dev.gold.bea19.m2", "ABCN.dev.gold.bea19.m2", "A.train.gold.bea19.m2", "ABC.train.gold.bea19.m2", "N.dev.gold.bea19.m2"} {
		f.upload(t, "wi/m2/"+name, "S Native sentence\nA -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n\n")
	}
	f.upload(t, "licence.txt", "Constructed counting fixture")
	f.register(t, "WILOCNESS-2.1", "partial_export")
	return f
}
func TestNativeSourceOrderingPositive(t *testing.T) {
	f := sourceOrderingFixture(t)
	run := f.run(t, "native", nil)
	sourceAssert(t, "10", run.Report.Observed)
	var n int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(DISTINCT member) FROM source_row WHERE import_id=$1", run.Report.ID).Scan(&n))
	sourceAssert(t, 5, n)
}
func TestNativeSourceScopeCountNegative(t *testing.T) {
	f := sourceOrderingFixture(t)
	run := f.run(t, "native", nil)
	missing, e := f.s.Store.sourceFullMissing(context.Background(), f.release, run.Report.ID, f.files)
	sourceRequire(t, e)
	want := []string{"N.dev.gold.bea19.m2: expected988, observed1", "A.train.gold.bea19.m2: expected10493, observed1", "ABC.train.gold.bea19.m2: expected34308, observed1"}
	for _, literal := range want {
		found := false
		for _, actual := range missing {
			found = found || actual == literal
		}
		if !found {
			t.Fatalf("missing independent full native count%s: %v", literal, missing)
		}
	}
}

func sourceWave(rate, frames int) []byte {
	b := make([]byte, 44+frames*2)
	copy(b, "RIFF")
	binary.LittleEndian.PutUint32(b[4:], uint32(len(b)-8))
	copy(b[8:], "WAVEfmt ")
	binary.LittleEndian.PutUint32(b[16:], 16)
	binary.LittleEndian.PutUint16(b[20:], 1)
	binary.LittleEndian.PutUint16(b[22:], 1)
	binary.LittleEndian.PutUint32(b[24:], uint32(rate))
	binary.LittleEndian.PutUint32(b[28:], uint32(rate*2))
	binary.LittleEndian.PutUint16(b[32:], 2)
	binary.LittleEndian.PutUint16(b[34:], 16)
	copy(b[36:], "data")
	binary.LittleEndian.PutUint32(b[40:], uint32(frames*2))
	return b
}
func sourceSpeechFixture(t *testing.T, bad bool) *sourceNative {
	f := sourceFixture(t)
	scores := map[string]any{}
	details := map[string]any{}
	for i, part := range []string{"train", "test"} {
		id := fmt.Sprintf("u%d", i)
		speaker := fmt.Sprintf("s%d", i)
		f.upload(t, "speech/"+part+"/text", id+"\tA native sentence\n")
		f.upload(t, "speech/"+part+"/utt2spk", id+" "+speaker+"\n")
		f.upload(t, "speech/"+part+"/spk2utt", speaker+" "+id+"\n")
		f.upload(t, "speech/"+part+"/spk2age", speaker+" adult\n")
		f.upload(t, "speech/"+part+"/wav.scp", id+" WAVE/"+id+".WAV\n")
		if !(bad && i == 1) {
			f.upload(t, "speech/WAVE/"+id+".WAV", string(sourceWave(16000, 16000)))
		}
		scores[id] = map[string]any{"text": "A native sentence", "accuracy": 8, "fluency": 8, "prosodic": 8, "completeness": 10, "total": 8, "words": []any{}}
		details[id] = map[string]any{"accuracy": []any{8, 8, 8, 8, 8}, "fluency": []any{8, 8, 8, 8, 8}, "prosodic": []any{8, 8, 8, 8, 8}, "completeness": []any{1, 1, 1, 1, 1}, "total": []any{8, 8, 8, 8, 8}, "phones": []any{}}
	}
	f.upload(t, "speech/scores.json", string(sourceBytes(scores)))
	f.upload(t, "speech/scores-detail.json", string(sourceBytes(details)))
	f.register(t, "SPEECHOCEAN762", "partial_export")
	return f
}
func TestNativeSourceSpeechPositive(t *testing.T) {
	f := sourceSpeechFixture(t, false)
	r := f.run(t, "native", nil)
	sourceAssert(t, true, r.Report.Normalized)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 200)
	sourceRequire(t, e)
	n := 0
	for _, row := range rows {
		if c, ok := row["corpus_record"].(map[string]any); ok {
			n++
			sourceAssert(t, "external_human_speech", c["origin"])
			sourceAssert(t, "adult", c["age_group"])
			raw, _ := source.Pointer(row["projection"], "/raw_metadata")
			m := raw.(map[string]any)
			sourceAssert(t, nil, m["observed_phone_substitution"])
			sourceAssert(t, json.Number("16000"), m["source_clock_hz"])
			if m["audio_asset_id"] == nil {
				t.Fatal("missing actual accepted audio")
			}
		}
	}
	sourceAssert(t, 2, n)
}
func TestNativeSourceSpeechNegative(t *testing.T) {
	f := sourceSpeechFixture(t, true)
	r := f.run(t, "native", nil)
	sourceAssert(t, false, r.Report.Normalized)
	sourceAssert(t, "1", r.Report.Quarantined)
	codes := map[string]bool{}
	for _, i := range r.Report.Issues {
		codes[i.Code] = true
	}
	sourceAssert(t, true, codes["missing_audio"])
}

func TestNativeSourceFrozenPermissionsNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	if _, e = f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", []string{"changed-selected-permission"}); !errors.Is(e, ErrConflict) {
		t.Fatalf("silently mixed old and changed source permissions%v", e)
	}
	saved, e := f.s.Store.SourceImport(context.Background(), r.Report.ID)
	sourceRequire(t, e)
	sourceAssert(t, 0, len(saved.Frozen.Permissions))
}
func TestNativeSourceMissingBytesNegative(t *testing.T) {
	f := sourceFixture(t)
	m := f.upload(t, "original.txt", "Retained original")
	var key string
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT storage_key FROM asset_location WHERE asset_id=$1", m.AssetID).Scan(&key))
	sourceRequire(t, f.s.Store.Media.RemoveObject(context.Background(), f.s.Store.Bucket, key, minio.RemoveObjectOptions{}))
	r := f.request("GET", "/api/v1/sources/assets/"+m.AssetID+"/bytes", nil, "", "")
	sourceAssert(t, 503, r.Code)
}

func TestNativeSourceProjectionBatchPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	sourceAssert(t, "6", run.Report.Accepted)
	var n int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_row WHERE import_id=$1 AND raw_record IS NOT NULL AND transformation IS NOT NULL", run.Report.ID).Scan(&n))
	sourceAssert(t, 6, n)
}
func TestNativeSourceProjectionBatchNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	_, e = f.s.Store.DB.Exec(context.Background(), `CREATE FUNCTION fail_projection() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN IF NEW.state='mapped' THEN RAISE EXCEPTION 'test-owned projection storage unavailable'; END IF; RETURN NEW; END $$; CREATE TRIGGER reject_projection BEFORE UPDATE ON source_row FOR EACH ROW EXECUTE FUNCTION fail_projection()`)
	sourceRequire(t, e)
	_, e = f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), 0)
	if e == nil {
		t.Fatal("test-owned projection failure missing")
	}
	var n int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_row WHERE import_id=$1 AND state<>'staged'", r.Report.ID).Scan(&n))
	sourceAssert(t, 0, n)
	_, e = f.s.Store.DB.Exec(context.Background(), "DROP TRIGGER reject_projection ON source_row")
	sourceRequire(t, e)
	fresh, e := f.s.Store.SourceImport(context.Background(), r.Report.ID)
	sourceRequire(t, e)
	done, e := f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), fresh.Revision)
	sourceRequire(t, e)
	sourceAssert(t, "6", done.Report.Accepted)
	sourceAssert(t, true, done.Report.Normalized)
}

func TestNativeSourceAdmissionReplayPositive(t *testing.T) {
	f := sourceFixture(t)
	binding := f.mapping(t, false)
	first, _, e := f.s.Store.sourceBinding(context.Background(), binding)
	sourceRequire(t, e)
	request := map[string]any{}
	sourceRequire(t, source.Decode(sourceBytes(first), &request))
	delete(request, "binding_program_asset_id")
	program, _, e := f.s.Store.sourceBinding(context.Background(), binding)
	sourceRequire(t, e)
	var raw []byte
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT program FROM source_format WHERE id=$1", binding).Scan(&raw))
	var p any
	sourceRequire(t, source.Decode(raw, &p))
	request["mapping_program"] = p
	again, e := f.s.Store.RegisterFormat(context.Background(), sourceBytes(request))
	sourceRequire(t, e)
	sourceAssert(t, program["id"], again["id"])
	sourceAssert(t, program["reviewed_at"], again["reviewed_at"])
}
func TestNativeSourceAdmissionReplayNegative(t *testing.T) {
	f := sourceFixture(t)
	binding := f.mapping(t, false)
	first, _, e := f.s.Store.sourceBinding(context.Background(), binding)
	sourceRequire(t, e)
	request := map[string]any{}
	sourceRequire(t, source.Decode(sourceBytes(first), &request))
	request["record_selector"] = "different-documented-record-boundary"
	changed, e := f.s.Store.RegisterFormat(context.Background(), sourceBytes(request))
	sourceRequire(t, e)
	if changed["id"] == first["id"] {
		t.Fatal("changed conversion silently overwrote immutable binding")
	}
	saved, _, e := f.s.Store.sourceBinding(context.Background(), binding)
	sourceRequire(t, e)
	sourceAssert(t, "records", saved["record_selector"])
}
