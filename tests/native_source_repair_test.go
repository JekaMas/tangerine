package app

import (
	"bytes"
	"context"
	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"testing"
)

func TestNativeSourceReadFailureNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	var key string
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT storage_key FROM asset_location WHERE asset_id=$1", f.files[2].AssetID).Scan(&key))
	original := []byte("S café go home\nA 1 2|||R:VERB:SVA|||goes|||REQUIRED|||-NONE-|||0\n\n")
	defer func() {
		_, e := f.s.Store.Media.PutObject(context.Background(), f.s.Store.Bucket, key, bytes.NewReader(original), int64(len(original)), minio.PutObjectOptions{})
		if e != nil {
			t.Error(e)
		}
	}()
	sourceRequire(t, f.s.Store.Media.RemoveObject(context.Background(), f.s.Store.Bucket, key, minio.RemoveObjectOptions{}))
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	failed, e := f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), 0)
	if e == nil {
		t.Fatalf("missing stored bytes became native parsing success/state%s: %+v", failed.Report.State, failed.Report.Issues)
	}
	sourceAssert(t, "failed", failed.Report.State)
	for _, issue := range failed.Report.Issues {
		if issue.Code == "parse_failed" {
			t.Fatal("storage failure permanently classified as malformed native input")
		}
	}
}

func TestNativeSourceReadFailurePositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	var key string
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT storage_key FROM asset_location WHERE asset_id=$1", f.files[2].AssetID).Scan(&key))
	original := []byte("S café go home\nA 1 2|||R:VERB:SVA|||goes|||REQUIRED|||-NONE-|||0\n\n")
	sourceRequire(t, f.s.Store.Media.RemoveObject(context.Background(), f.s.Store.Bucket, key, minio.RemoveObjectOptions{}))
	r, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	_, e = f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), 0)
	if e == nil {
		t.Fatal("expected actual missing-byte failure")
	}
	_, e = f.s.Store.Media.PutObject(context.Background(), f.s.Store.Bucket, key, bytes.NewReader(original), int64(len(original)), minio.PutObjectOptions{})
	sourceRequire(t, e)
	fresh, e := f.s.Store.SourceImport(context.Background(), r.Report.ID)
	sourceRequire(t, e)
	recovered, e := f.s.Store.RunSourceImport(context.Background(), r.Report.ID, uuid.NewString(), fresh.Revision)
	sourceRequire(t, e)
	sourceAssert(t, "complete", recovered.Report.State)
	sourceAssert(t, true, recovered.Report.Normalized)
	sourceAssert(t, "6", recovered.Report.Observed)
}
func sourceStoredEssayGroup(t *testing.T, id string) string {
	t.Helper()
	f := sourceFixture(t)
	for _, part := range []string{"train", "dev", "test"} {
		f.upload(t, part+".m2", "S Original sentence\nA -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n\n")
	}
	f.upload(t, "licence.txt", "Constructed grouping fixture")
	f.upload(t, "train.json", `{"id":"same-native-id","text":"An independently authored essay."}`)
	f.register(t, id, "partial_export")
	r := f.run(t, "native", nil)
	sourceAssert(t, "7", r.Report.Observed)
	rows, _, e := f.s.Store.SourceRows(context.Background(), r.Report.ID, "", 20)
	sourceRequire(t, e)
	for _, row := range rows {
		if row["table"] == "essays" {
			c := row["corpus_record"].(map[string]any)
			return c["group_ids"].([]any)[1].(string)
		}
	}
	t.Fatal("stored native essay absent")
	return ""
}
func TestNativeSourceEssayGroupPositive(t *testing.T) {
	sourceAssert(t, sourceStoredEssayGroup(t, "FCE-2.1"), sourceStoredEssayGroup(t, "FCE-2.1"))
}
func TestNativeSourceEssayGroupNegative(t *testing.T) {
	if sourceStoredEssayGroup(t, "FCE-2.1") == sourceStoredEssayGroup(t, "WILOCNESS-2.1") {
		t.Fatal("persisted unrelated source groups merged")
	}
}
