package app

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"io"
	"os"
	"sync"
	"testing"
	"time"
)

// Native disposable PostgreSQL/MinIO, real shared production pool. Expectations
// use literal bytes and independent SHA256; no provider/storage/HTTP doubles.
func nativeStore(t *testing.T) *Storage {
	t.Helper()
	s, e := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(s.DB.Close)
	return s
}
func nativeSHA(b []byte) string { h := sha256.Sum256(b); return hex.EncodeToString(h[:]) }
func nativeRequest() AssetRequest {
	return AssetRequest{Operation: OperationRequest{Name: "native-upload", Key: uuid.NewString(), Path: "/native/" + uuid.NewString(), Body: json.RawMessage(`{"intent":"frozen"}`)}, SHA: nativeSHA([]byte("review")), Size: 6, Purpose: "provider_input", MIME: "text/plain"}
}
func nativeReserve(t *testing.T, s *Storage, r AssetRequest) Asset {
	t.Helper()
	a, e := s.ReserveAsset(context.Background(), r)
	if e != nil {
		t.Fatal(e)
	}
	return a
}
func nativeAnswer(t *testing.T, s *Storage) Reference {
	t.Helper()
	id := uuid.NewString()
	b := json.RawMessage(`{"answer_text":"Literal target","requested_language":"en"}`)
	if _, e := s.WriteDocuments(context.Background(), []DocumentWrite{{ID: id, Kind: "answer-write", Version: "2.0.0", Scope: id, Payload: b}}); e != nil {
		t.Fatal(e)
	}
	return Reference{Pointer: "/candidate_id", ID: id, Scope: id, Kind: "answer-write", SHA: nativeSHA(b), Relation: "candidate"}
}
func nativeCase(id, candidate, parent string) []byte {
	p := "null"
	if parent != "" {
		p = fmt.Sprintf("%q", parent)
	}
	return []byte(fmt.Sprintf(`{"candidate_id":%q,"created_at":"2026-10-10T10:00:00Z","delivery_asset_id":null,"ground_truth_id":null,"id":%q,"parent_case_version_id":%s,"quarantine_open":false,"revision":0,"status":"draft"}`, candidate, id, p))
}
func nativeHead(t *testing.T, s *Storage) (string, string, Reference) {
	t.Helper()
	ref := nativeAnswer(t, s)
	head, id := uuid.NewString(), uuid.NewString()
	b := nativeCase(id, ref.ID, "")
	if _, e := s.WriteDocuments(context.Background(), []DocumentWrite{{ID: id, Kind: "case-head", Version: "2.0.0", Scope: id, Payload: b, References: []Reference{ref}, Head: &HeadWrite{ID: head, State: "draft"}}}); e != nil {
		t.Fatal(e)
	}
	ref = Reference{Pointer: "/case_version_id", ID: id, Scope: id, Kind: "case-head", SHA: nativeSHA(b), Relation: "case-version"}
	return head, id, ref
}
func nativeEvidence(id string, c Reference, parents []string) DocumentWrite {
	p, _ := json.Marshal(parents)
	if parents == nil {
		p = []byte("[]")
	}
	b := []byte(fmt.Sprintf(`{"asset_sha256":null,"case_version_id":%q,"created_at":"2026-10-10T10:00:00Z","epistemic_status":"requested","id":%q,"method_version":"native-fixture-v1","numeric_measure":null,"observed":null,"parent_evidence_ids":%s,"provider_profile_id":null,"raw_private_asset_id":null,"schema_version":"2.0.0","source_refs":[],"subject_audio_sha256":null,"subject_ids":[%q],"type":"source","unit":null}`, c.ID, id, p, c.ID))
	subject := c
	subject.Pointer = "/subject_ids/0"
	subject.Relation = "subject"
	return DocumentWrite{ID: id, Kind: "evidence", Version: "2.0.0", Scope: c.ID, Payload: b, References: []Reference{c, subject}}
}
func nativePart(t *testing.T, s *Storage, a Asset) string {
	t.Helper()
	ctx := context.Background()
	id, e := s.BeginAssetUpload(ctx, a.ID)
	if e != nil {
		t.Fatal(e)
	}
	core := minio.Core{Client: s.Media}
	if _, e = core.PutObjectPart(ctx, s.Bucket, a.Key, id, 1, bytes.NewReader([]byte("rev")), 3, minio.PutObjectPartOptions{}); e != nil {
		t.Fatal(e)
	}
	return id
}
func nativeFailed(t *testing.T, s *Storage, a Asset) (string, string) {
	t.Helper()
	var state, errorID, result, subject string
	if e := s.DB.QueryRow(context.Background(), "SELECT state,error_document_id,result_document_id,subject_id FROM operation WHERE id=$1", a.OperationID).Scan(&state, &errorID, &result, &subject); e != nil {
		t.Fatal(e)
	}
	if state != "failed" || subject != a.ID {
		t.Fatalf("failure lineage: %s %s", state, subject)
	}
	d, e := s.ReadDocument(context.Background(), errorID)
	if e != nil {
		t.Fatal(e)
	}
	var p map[string]any
	_ = json.Unmarshal(d.Payload, &p)
	if d.Kind != "error-response" || p["request_id"] != a.OperationID || p["retryable"] != true {
		t.Fatalf("error receipt: %s", d.Payload)
	}
	d, e = s.ReadDocument(context.Background(), result)
	if e != nil {
		t.Fatal(e)
	}
	_ = json.Unmarshal(d.Payload, &p)
	if p["state"] != "orphaned" || p["id"] != a.ID {
		t.Fatal("frozen failure result differs")
	}
	return errorID, result
}

type nativeBlockedReader struct {
	once             sync.Once
	entered, release chan struct{}
	r                io.Reader
}

func (r *nativeBlockedReader) Read(b []byte) (int, error) {
	r.once.Do(func() { close(r.entered); <-r.release })
	return r.r.Read(b)
}
func nativeOccupied(t *testing.T, s *Storage) {
	t.Helper()
	deadline := time.Now().Add(5 * time.Second)
	for s.DB.Stat().AcquiredConns() != 10 && time.Now().Before(deadline) {
		time.Sleep(10 * time.Millisecond)
	}
	if n := s.DB.Stat().AcquiredConns(); n != 10 {
		t.Fatalf("setup occupancy: %d", n)
	}
}
func TestNativePoolSameAssetPositive(t *testing.T) {
	s := nativeStore(t)
	a := nativeReserve(t, s, nativeRequest())
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	reader := &nativeBlockedReader{entered: make(chan struct{}), release: make(chan struct{}), r: bytes.NewReader([]byte("review"))}
	winner := make(chan error, 1)
	go func() { _, e := s.UploadReader(ctx, a.ID, reader); winner <- e }()
	<-reader.entered
	results := make(chan error, 9)
	for i := 0; i < 9; i++ {
		go func() { _, e := s.UploadAsset(ctx, a.ID, []byte("review")); results <- e }()
	}
	nativeOccupied(t, s)
	close(reader.release)
	if e := <-winner; e != nil {
		t.Fatal(e)
	}
	for i := 0; i < 9; i++ {
		if e := <-results; e != nil {
			t.Fatal(e)
		}
	}
	if _, e := s.LinkAsset(ctx, a.ID, nil); e != nil {
		t.Fatal(e)
	}
	b, e := s.ReadAsset(ctx, a.ID)
	if e != nil || !bytes.Equal(b, []byte("review")) {
		t.Fatal("wrong byte result", e)
	}
}
func TestNativePoolDistinctAssetsPositive(t *testing.T) {
	s := nativeStore(t)
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	as := make([]Asset, 20)
	for i := range as {
		as[i] = nativeReserve(t, s, nativeRequest())
	}
	results := make(chan error, len(as))
	for _, a := range as {
		go func(a Asset) { _, e := s.UploadAsset(ctx, a.ID, []byte("review")); results <- e }(a)
	}
	for range as {
		if e := <-results; e != nil {
			t.Fatal(e)
		}
	}
	for _, a := range as {
		if _, e := s.LinkAsset(ctx, a.ID, nil); e != nil {
			t.Fatal(e)
		}
		b, e := s.ReadAsset(ctx, a.ID)
		if e != nil || string(b) != "review" {
			t.Fatal("distinct bytes", e)
		}
	}
}
func TestNativePoolCancelledWaiterNegative(t *testing.T) {
	s := nativeStore(t)
	a := nativeReserve(t, s, nativeRequest())
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	r := &nativeBlockedReader{entered: make(chan struct{}), release: make(chan struct{}), r: bytes.NewReader([]byte("review"))}
	done := make(chan error, 1)
	go func() { _, e := s.UploadReader(ctx, a.ID, r); done <- e }()
	<-r.entered
	waiter, stop := context.WithTimeout(ctx, 100*time.Millisecond)
	defer stop()
	_, e := s.UploadAsset(waiter, a.ID, []byte("review"))
	if e == nil {
		t.Fatal("cancelled waiter succeeded")
	}
	close(r.release)
	if e = <-done; e != nil {
		t.Fatal(e)
	}
	if _, e = s.UploadAsset(ctx, a.ID, []byte("review")); e != nil {
		t.Fatal("lock leaked", e)
	}
}
func TestNativePoolWrongBytesNegative(t *testing.T) {
	s := nativeStore(t)
	a := nativeReserve(t, s, nativeRequest())
	ctx := context.Background()
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if _, e := s.UploadAsset(ctx, a.ID, []byte("wrong!")); e == nil {
				t.Error("wrong bytes accepted")
			}
		}()
	}
	wg.Wait()
	if _, e := s.Media.StatObject(ctx, s.Bucket, a.Key, minio.StatObjectOptions{}); minio.ToErrorResponse(e).Code != "NoSuchKey" {
		t.Fatal("rejected upload created bytes", e)
	}
	if _, e := s.UploadAsset(ctx, a.ID, []byte("review")); e != nil {
		t.Fatal(e)
	}
}
func TestNativeGraphEvidenceAcyclicPositive(t *testing.T) {
	s := nativeStore(t)
	_, _, c := nativeHead(t, s)
	parent := nativeEvidence(uuid.NewString(), c, nil)
	child := nativeEvidence(uuid.NewString(), c, []string{parent.ID})
	child.References = append(child.References, Reference{Pointer: "/parent_evidence_ids/0", ID: parent.ID, Scope: c.ID, Kind: "evidence", SHA: nativeSHA(parent.Payload), Relation: "parent-evidence"})
	if _, e := s.WriteDocuments(context.Background(), []DocumentWrite{child, parent}); e != nil {
		t.Fatal(e)
	}
	for _, id := range []string{parent.ID, child.ID} {
		if _, e := s.ReadDocument(context.Background(), id); e != nil {
			t.Fatal(e)
		}
	}
}
func TestNativeGraphLinkAcyclicPositive(t *testing.T) {
	s := nativeStore(t)
	head, old, c := nativeHead(t, s)
	zero := int64(0)
	r := nativeRequest()
	r.Owner = &HeadWrite{ID: head, Expected: &zero, State: "draft"}
	a := nativeReserve(t, s, r)
	ctx := context.Background()
	if _, e := s.UploadAsset(ctx, a.ID, []byte("review")); e != nil {
		t.Fatal(e)
	}
	id := uuid.NewString()
	b := nativeCase(id, a.ID, old)
	c.Pointer = "/parent_case_version_id"
	c.Relation = "parent-evidence"
	w := DocumentWrite{ID: id, Kind: "case-head", Version: "2.0.0", Scope: id, Payload: b, Head: &HeadWrite{ID: head, Expected: &zero, State: "draft"}, References: []Reference{c, {Pointer: "/candidate_id", ID: a.ID, Scope: a.ID, Kind: "asset-bytes", SHA: a.SHA, Relation: "candidate"}}}
	if _, e := s.LinkAsset(ctx, a.ID, &w); e != nil {
		t.Fatal(e)
	}
	var revision int
	_ = s.DB.QueryRow(ctx, "SELECT revision FROM entity_head WHERE id=$1", head).Scan(&revision)
	if revision != 1 {
		t.Fatal(revision)
	}
}
func TestNativeGraphParentRoleNegative(t *testing.T) {
	s := nativeStore(t)
	ctx := context.Background()
	_, _, c := nativeHead(t, s)
	for _, relation := range []string{"parent", "parent-evidence"} {
		w := nativeEvidence(uuid.NewString(), c, nil)
		w = nativeEvidence(w.ID, c, []string{w.ID})
		w.References = append(w.References, Reference{Pointer: "/parent_evidence_ids/0", ID: w.ID, Scope: c.ID, Kind: "evidence", SHA: nativeSHA(w.Payload), Relation: relation})
		if _, e := s.WriteDocuments(ctx, []DocumentWrite{w}); !errors.Is(e, ErrReference) {
			t.Fatal("self parent", relation, e)
		}
	}
	aID, bID := uuid.NewString(), uuid.NewString()
	a, b := nativeEvidence(aID, c, []string{bID}), nativeEvidence(bID, c, []string{aID})
	a.References = append(a.References, Reference{Pointer: "/parent_evidence_ids/0", ID: bID, Scope: c.ID, Kind: "evidence", SHA: nativeSHA(b.Payload), Relation: "parent-evidence"})
	b.References = append(b.References, Reference{Pointer: "/parent_evidence_ids/0", ID: aID, Scope: c.ID, Kind: "evidence", SHA: nativeSHA(a.Payload), Relation: "parent-evidence"})
	if _, e := s.WriteDocuments(ctx, []DocumentWrite{a, b}); !errors.Is(e, ErrReference) {
		t.Fatal("two node cycle", e)
	}
	var count int
	_ = s.DB.QueryRow(ctx, "SELECT count(*) FROM document WHERE id IN($1,$2)", aID, bID).Scan(&count)
	if count != 0 {
		t.Fatal("partial cycle commit")
	}
}
func TestNativeGraphLinkCycleNegative(t *testing.T) {
	s := nativeStore(t)
	head, _, _ := nativeHead(t, s)
	zero := int64(0)
	r := nativeRequest()
	r.Owner = &HeadWrite{ID: head, Expected: &zero, State: "draft"}
	a := nativeReserve(t, s, r)
	ctx := context.Background()
	if _, e := s.UploadAsset(ctx, a.ID, []byte("review")); e != nil {
		t.Fatal(e)
	}
	id := uuid.NewString()
	b := nativeCase(id, a.ID, id)
	w := DocumentWrite{ID: id, Kind: "case-head", Version: "2.0.0", Scope: id, Payload: b, Head: &HeadWrite{ID: head, Expected: &zero, State: "draft"}, References: []Reference{{Pointer: "/candidate_id", ID: a.ID, Scope: a.ID, Kind: "asset-bytes", SHA: a.SHA, Relation: "candidate"}, {Pointer: "/parent_case_version_id", ID: id, Scope: id, Kind: "case-head", SHA: nativeSHA(b), Relation: "parent-evidence"}}}
	if _, e := s.LinkAsset(ctx, a.ID, &w); !errors.Is(e, ErrReference) {
		t.Fatal("cycle link", e)
	}
	var state string
	var revision, count int
	_ = s.DB.QueryRow(ctx, "SELECT state FROM asset_location WHERE asset_id=$1", a.ID).Scan(&state)
	_ = s.DB.QueryRow(ctx, "SELECT revision FROM entity_head WHERE id=$1", head).Scan(&revision)
	_ = s.DB.QueryRow(ctx, "SELECT count(*) FROM document WHERE id=$1", id).Scan(&count)
	if state != "bytes_verified" || revision != 0 || count != 0 {
		t.Fatalf("non-atomic rollback %s %d %d", state, revision, count)
	}
	w.ID = "bad-envelope"
	if _, e := s.LinkAsset(ctx, a.ID, &w); e == nil {
		t.Fatal("invalid envelope accepted")
	}
	ownerless := nativeReserve(t, s, nativeRequest())
	if _, e := s.UploadAsset(ctx, ownerless.ID, []byte("review")); e != nil {
		t.Fatal(e)
	}
	newID := uuid.NewString()
	validOwner := DocumentWrite{ID: newID, Kind: "case-head", Version: "2.0.0", Scope: newID, Payload: nativeCase(newID, ownerless.ID, ""), Head: &HeadWrite{ID: head, Expected: &zero, State: "draft"}, References: []Reference{{Pointer: "/candidate_id", ID: ownerless.ID, Scope: ownerless.ID, Kind: "asset-bytes", SHA: ownerless.SHA, Relation: "candidate"}}}
	if _, e := s.LinkAsset(ctx, ownerless.ID, &validOwner); !errors.Is(e, ErrReference) {
		t.Fatal("owner acquired after reservation", e)
	}
	var ownerlessState, operationState string
	if e := s.DB.QueryRow(ctx, "SELECT a.state,o.state FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE a.asset_id=$1", ownerless.ID).Scan(&ownerlessState, &operationState); e != nil {
		t.Fatal(e)
	}
	if ownerlessState != "bytes_verified" || operationState != "reserved" {
		t.Fatal("ownerless rejection partially committed", ownerlessState, operationState)
	}

}
func TestNativeRecoveryCompletedPositive(t *testing.T) {
	s := nativeStore(t)
	ctx := context.Background()
	a := nativeReserve(t, s, nativeRequest())
	if _, e := s.Media.PutObject(ctx, s.Bucket, a.Key, bytes.NewReader([]byte("review")), 6, minio.PutObjectOptions{DisableMultipart: true}); e != nil {
		t.Fatal(e)
	}
	a, e := s.RecoverAsset(ctx, a.ID)
	if e != nil || a.State != "bytes_verified" {
		t.Fatal(a, e)
	}
	if _, e = s.LinkAsset(ctx, a.ID, nil); e != nil {
		t.Fatal(e)
	}
	b, e := s.ReadAsset(ctx, a.ID)
	if e != nil || string(b) != "review" {
		t.Fatal(e)
	}
}
func TestNativeRecoveryRetryPositive(t *testing.T) {
	s := nativeStore(t)
	ctx := context.Background()
	r := nativeRequest()
	a := nativeReserve(t, s, r)
	upload := nativePart(t, s, a)
	if _, e := s.RecoverAsset(ctx, a.ID); e != nil {
		t.Fatal(e)
	}
	errorID, result := nativeFailed(t, s, a)
	// Reopen storage to demonstrate durable restart/readback rather than cached state.
	again := nativeStore(t)
	if _, e := again.RecoverAsset(ctx, a.ID); e != nil {
		t.Fatal(e)
	}
	error2, result2 := nativeFailed(t, again, a)
	if errorID != error2 || result != result2 {
		t.Fatal("rotated failure receipt")
	}
	core := minio.Core{Client: s.Media}
	if _, e := core.ListObjectParts(ctx, s.Bucket, a.Key, upload, 0, 10); minio.ToErrorResponse(e).Code != "NoSuchUpload" {
		t.Fatal("partial upload survived exact abort", e)
	}
	r.Operation.Key = uuid.NewString()
	next, e := again.RetryAsset(ctx, a.ID, r)
	if e != nil {
		t.Fatal(e)
	}
	repeated, e := again.RetryAsset(ctx, a.ID, r)
	if e != nil || repeated.ID != next.ID {
		t.Fatal("retry idempotency", e)
	}
	if next.ID == a.ID || next.OperationID == a.OperationID {
		t.Fatal("reused failed operation")
	}
	var input string
	if e = again.DB.QueryRow(ctx, "SELECT input_document_id FROM operation WHERE id=$1", next.OperationID).Scan(&input); e != nil || input != result {
		t.Fatal("retry lost frozen failure lineage", e)
	}
	if _, e = again.UploadAsset(ctx, next.ID, []byte("review")); e != nil {
		t.Fatal(e)
	}
	if _, e = again.LinkAsset(ctx, next.ID, nil); e != nil {
		t.Fatal(e)
	}
	nativeFailed(t, again, a)
}
func TestNativeRecoveryOldKeyNegative(t *testing.T) {
	s := nativeStore(t)
	ctx := context.Background()
	r := nativeRequest()
	a := nativeReserve(t, s, r)
	nativePart(t, s, a)
	if _, e := s.RecoverAsset(ctx, a.ID); e != nil {
		t.Fatal(e)
	}
	nativeFailed(t, s, a)
	old, e := s.ReserveAsset(ctx, r)
	if e != nil || old.ID != a.ID || old.State != "orphaned" {
		t.Fatal("original idempotent failure", e)
	}
	if _, e = s.UploadAsset(ctx, a.ID, []byte("review")); !errors.Is(e, ErrUnavailable) {
		t.Fatal(e)
	}
	if _, e = s.LinkAsset(ctx, a.ID, nil); !errors.Is(e, ErrUnavailable) {
		t.Fatal(e)
	}
	if _, e = s.RetryAsset(ctx, a.ID, r); !errors.Is(e, ErrConflict) {
		t.Fatal(e)
	}
	nativeFailed(t, s, a)
}
func TestNativeRecoveryChangedIntentNegative(t *testing.T) {
	s := nativeStore(t)
	ctx := context.Background()
	r := nativeRequest()
	a := nativeReserve(t, s, r)
	nativePart(t, s, a)
	if _, e := s.RecoverAsset(ctx, a.ID); e != nil {
		t.Fatal(e)
	}
	for _, field := range []string{"path", "body", "query", "sha", "size", "mime", "purpose", "revision"} {
		x := r
		x.Operation.Key = uuid.NewString()
		switch field {
		case "path":
			x.Operation.Path = "/other"
		case "body":
			x.Operation.Body = json.RawMessage(`{"intent":"changed"}`)
		case "query":
			x.Operation.Query = json.RawMessage(`{"q":1}`)
		case "sha":
			x.SHA = nativeSHA([]byte("other!"))
		case "size":
			x.Size = 7
		case "mime":
			x.MIME = "audio/wav"
		case "purpose":
			x.Purpose = "provider_output"
		case "revision":
			v := int64(1)
			x.Operation.Revision = &v
		}
		if _, e := s.RetryAsset(ctx, a.ID, x); !errors.Is(e, ErrConflict) {
			t.Fatal(field, e)
		}
		var count int
		_ = s.DB.QueryRow(ctx, "SELECT count(*) FROM operation WHERE idempotency_key=$1", x.Operation.Key).Scan(&count)
		if count != 0 {
			t.Fatal("invalid retry side effect")
		}
	}
	// A retry key identifies one original immutable failure, even for equal intent.
	other := r
	other.Operation.Key = uuid.NewString()
	originalB := nativeReserve(t, s, other)
	nativePart(t, s, originalB)
	if _, e := s.RecoverAsset(ctx, originalB.ID); e != nil {
		t.Fatal(e)
	}
	retry := r
	retry.Operation.Key = uuid.NewString()
	retryA, e := s.RetryAsset(ctx, a.ID, retry)
	if e != nil {
		t.Fatal(e)
	}
	if _, e = s.RetryAsset(ctx, originalB.ID, retry); !errors.Is(e, ErrConflict) {
		t.Fatal("retry key accepted for another failure", e)
	}
	independent := r
	independent.Operation.Key = uuid.NewString()
	normal := nativeReserve(t, s, independent)
	if _, e = s.RetryAsset(ctx, a.ID, independent); !errors.Is(e, ErrConflict) {
		t.Fatal("independent reservation relabelled as retry", e)
	}
	var input string
	_, originalResult := nativeFailed(t, s, a)
	if e = s.DB.QueryRow(ctx, "SELECT input_document_id FROM operation WHERE id=$1", retryA.OperationID).Scan(&input); e != nil || input != originalResult {
		t.Fatal("changed retry lineage", e)
	}
	var independentInput *string
	if e = s.DB.QueryRow(ctx, "SELECT input_document_id FROM operation WHERE id=$1", normal.OperationID).Scan(&independentInput); e != nil || independentInput != nil {
		t.Fatal("independent operation changed", e)
	}

}
func TestNativeDatabaseReachablePositive(t *testing.T) {
	s := nativeStore(t)
	if e := s.CheckDatabase(context.Background()); e != nil {
		t.Fatal(e)
	}
}
func TestNativeDatabaseReopenPositive(t *testing.T) {
	s := nativeStore(t)
	s.DB.Close()
	again := nativeStore(t)
	if e := again.CheckDatabase(context.Background()); e != nil {
		t.Fatal(e)
	}
}
func TestNativeDatabaseClosedNegative(t *testing.T) {
	s := nativeStore(t)
	s.DB.Close()
	if e := s.CheckDatabase(context.Background()); e == nil {
		t.Fatal("closed database reported reachable")
	}
}
func TestNativeDatabaseCancelledNegative(t *testing.T) {
	s := nativeStore(t)
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if e := s.CheckDatabase(ctx); e == nil {
		t.Fatal("cancelled readiness reported reachable")
	}
}
