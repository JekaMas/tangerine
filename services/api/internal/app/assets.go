package app

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"strconv"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/minio/minio-go/v7"
	"tangerine.local/api/internal/contracts"
)

type AssetRequest struct {
	Operation OperationRequest `json:"operation"`
	SHA       string           `json:"sha256"`
	Size      int64            `json:"byte_count"`
	Purpose   string           `json:"purpose"`
	MIME      string           `json:"mime_type"`
	Owner     *HeadWrite       `json:"owner,omitempty"`
}
type Asset struct {
	ID          string  `json:"id"`
	Key         string  `json:"storage_key"`
	State       string  `json:"state"`
	SHA         string  `json:"sha256"`
	Size        int64   `json:"byte_count"`
	OperationID string  `json:"operation_id"`
	Owner       *string `json:"owner_head_id,omitempty"`
	Revision    *int64  `json:"owner_revision,omitempty"`
}

func (s *Storage) ReserveAsset(ctx context.Context, r AssetRequest) (Asset, error) {
	return s.reserveAsset(ctx, r, "")
}

func (s *Storage) reserveAsset(ctx context.Context, r AssetRequest, retryID string) (Asset, error) {
	if !validDigest(r.SHA) || r.Size < 0 || (r.Owner != nil && r.Owner.Expected == nil) {
		return Asset{}, errors.New("invalid asset reservation")
	}
	digest, err := assetRequestDigest(r)
	if err != nil {
		return Asset{}, err
	}
	tx, err := beginWrite(ctx, s)
	if err != nil {
		return Asset{}, err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	var retryResult *string
	if retryID != "" {
		old, err := readAsset(ctx, tx, "asset_id", retryID, false)
		if err != nil {
			return Asset{}, err
		}
		var state, key, originalDigest string
		var receipt *string
		if err = tx.QueryRow(ctx, "SELECT state,idempotency_key,request_sha256,error_document_id,result_document_id FROM operation WHERE id=$1 FOR SHARE", old.OperationID).Scan(&state, &key, &originalDigest, &receipt, &retryResult); err != nil {
			return Asset{}, err
		}
		parsed, _ := uuid.Parse(r.Operation.Key)
		if state != "failed" || receipt == nil || retryResult == nil || parsed.String() == key || digest != originalDigest {
			return Asset{}, ErrConflict
		}
	}
	o, created, err := reserveOperation(ctx, tx, r.Operation, digest)
	if err != nil {
		return Asset{}, err
	}
	if retryResult != nil {
		if created {
			if _, err = tx.Exec(ctx, "UPDATE operation SET input_document_id=$2 WHERE id=$1", o.ID, *retryResult); err != nil {
				return Asset{}, err
			}
		} else {
			var originalInput *string
			if err = tx.QueryRow(ctx, "SELECT input_document_id FROM operation WHERE id=$1", o.ID).Scan(&originalInput); err != nil {
				return Asset{}, err
			}
			if originalInput == nil || *originalInput != *retryResult {
				return Asset{}, ErrConflict
			}
		}
	}
	// Lock the durable operation before any object reservation; repeated calls reuse it.
	var state string
	if err = tx.QueryRow(ctx, "SELECT state FROM operation WHERE id=$1 FOR UPDATE", o.ID).Scan(&state); err != nil {
		return Asset{}, err
	}
	a, err := readAsset(ctx, tx, "operation_id", o.ID, false)
	if err == nil {
		return a, tx.Commit(ctx)
	}
	if !errors.Is(err, pgx.ErrNoRows) {
		return a, err
	}
	if state != "reserved" {
		return a, ErrConflict
	}
	a = Asset{ID: uuid.NewString(), Key: uuid.NewString(), State: "reserved", SHA: r.SHA, Size: r.Size, OperationID: o.ID}
	if r.Owner != nil {
		a.Owner = &r.Owner.ID
		a.Revision = r.Owner.Expected
		var revision int64
		if err = tx.QueryRow(ctx, "SELECT revision FROM entity_head WHERE id=$1 FOR UPDATE", *a.Owner).Scan(&revision); err != nil {
			return a, err
		}
		if revision != *a.Revision {
			return a, ErrRevision
		}
	}
	payload := map[string]any{"schema_version": "2.0.0", "id": a.ID, "purpose": r.Purpose, "owner": map[string]any{"kind": "asset", "id": a.ID, "version_id": nil}, "state": "reserved", "sha256": nil, "byte_count": nil, "mime_type": r.MIME, "storage_key": a.Key, "created_at": time.Now().UTC().Format(time.RFC3339Nano), "verified_at": nil, "linked_at": nil, "source_request_id": o.ID}
	if a.Owner != nil {
		var kind, version string
		if err = tx.QueryRow(ctx, "SELECT kind,document_id FROM entity_head WHERE id=$1", *a.Owner).Scan(&kind, &version); err != nil {
			return a, err
		}
		ownerKind := map[string]string{"case-head": "case", "candidate-envelope": "case", "ground-truth": "case", "answer-write": "attempt", "attempt": "attempt", "configuration": "configuration", "source-release": "release", "raw-record": "record"}[kind]
		if ownerKind == "" {
			ownerKind = "configuration"
		}
		payload["owner"] = map[string]any{"kind": ownerKind, "id": *a.Owner, "version_id": version}
	}
	b, _ := json.Marshal(payload)
	if err = assetDocument(ctx, tx, a, b, nil); err != nil {
		return a, err
	}
	_, err = tx.Exec(ctx, "INSERT INTO asset_location(asset_id,storage_key,state,operation_id,owner_head_id,owner_revision,intended_sha256,intended_byte_count) VALUES($1,$2,'reserved',$3,$4,$5,$6,$7)", a.ID, a.Key, o.ID, a.Owner, a.Revision, a.SHA, a.Size)
	if err != nil {
		return a, err
	}
	return a, tx.Commit(ctx)
}

type rowQuerier interface {
	QueryRow(context.Context, string, ...any) pgx.Row
}

func readAsset(ctx context.Context, q rowQuerier, column, id string, lock bool) (Asset, error) {
	var a Asset
	if column != "asset_id" && column != "operation_id" {
		return a, errors.New("invalid lookup")
	}
	suffix := ""
	if lock {
		suffix = " FOR UPDATE"
	}
	err := q.QueryRow(ctx, "SELECT asset_id,storage_key,state,intended_sha256,intended_byte_count::bigint,operation_id,owner_head_id,owner_revision FROM asset_location WHERE "+column+"=$1"+suffix, id).Scan(&a.ID, &a.Key, &a.State, &a.SHA, &a.Size, &a.OperationID, &a.Owner, &a.Revision)
	return a, err
}
func assetDocument(ctx context.Context, tx pgx.Tx, a Asset, payload []byte, expected *int64) error {
	c, b, err := contracts.Validate("asset", "2.0.0", payload)
	if err != nil {
		return err
	}
	id := uuid.NewString()
	w := DocumentWrite{ID: id, Kind: "asset", Version: "2.0.0", Scope: id, Head: &HeadWrite{a.ID, expected, a.State}}
	var value map[string]any
	_ = json.Unmarshal(b, &value)
	if owner, ok := value["owner"].(map[string]any); ok {
		if version, ok := owner["version_id"].(string); ok {
			var ref Reference
			ref.Pointer = "/owner/version_id"
			ref.Relation = "frozen-owner"
			if err = tx.QueryRow(ctx, "SELECT node_id,scope_id,kind,content_sha256 FROM object_node WHERE document_id=$1 AND json_pointer=''", version).Scan(&ref.ID, &ref.Scope, &ref.Kind, &ref.SHA); err != nil {
				return err
			}
			w.References = []Reference{ref}
		}
	}
	return insertDocument(ctx, tx, w, SavedDocument{id, "asset", "2.0.0", c.SHA, contracts.Digest(b), b})
}
func setAssetState(ctx context.Context, tx pgx.Tx, a Asset, state string) error {
	var b []byte
	var revision int64
	err := tx.QueryRow(ctx, "SELECT d.payload,h.revision FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id=$1", a.ID).Scan(&b, &revision)
	if err != nil {
		return err
	}
	var p map[string]any
	if err = json.Unmarshal(b, &p); err != nil {
		return err
	}
	p["state"] = state
	if state == "bytes_verified" || state == "linked" {
		p["sha256"] = a.SHA
		p["byte_count"] = strconv.FormatInt(a.Size, 10)
		if p["verified_at"] == nil {
			p["verified_at"] = time.Now().UTC().Format(time.RFC3339Nano)
		}
	}
	if state == "linked" {
		p["linked_at"] = time.Now().UTC().Format(time.RFC3339Nano)
	}
	b, _ = json.Marshal(p)
	a.State = state
	if err = assetDocument(ctx, tx, a, b, &revision); err != nil {
		return err
	}
	_, err = tx.Exec(ctx, "UPDATE asset_location SET state=$2,sha256=CASE WHEN $2 IN('bytes_verified','linked') THEN intended_sha256 ELSE sha256 END,byte_count=CASE WHEN $2 IN('bytes_verified','linked') THEN intended_byte_count ELSE byte_count END,verified_at=CASE WHEN $2 IN('bytes_verified','linked') THEN coalesce(verified_at,clock_timestamp()) ELSE verified_at END,linked_at=CASE WHEN $2='linked' THEN clock_timestamp() ELSE linked_at END WHERE asset_id=$1", a.ID, state)
	return err
}

// UploadAsset only writes a still-reserved object. Recovery reuses already present
// bytes and never silently overwrites them with a later candidate.
func (s *Storage) UploadAsset(ctx context.Context, id string, data []byte) (Asset, error) {
	a, err := readAsset(ctx, s.DB, "asset_id", id, false)
	if err != nil {
		return a, err
	}
	if a.State == "linked" || a.State == "bytes_verified" {
		return a, nil
	}
	if a.State != "reserved" && a.State != "uploading" && a.State != "bytes_verified" {
		return a, ErrUnavailable
	}
	conn, release, err := s.lockAsset(ctx, id)
	if err != nil {
		return a, err
	}
	defer release()
	a, err = readAsset(ctx, conn, "asset_id", id, false)
	if err != nil {
		return a, err
	}
	if a.State == "linked" || a.State == "bytes_verified" {
		return a, nil
	}
	if a.State == "uploading" {
		a, err = s.recoverAssetUnlocked(ctx, conn, id)
		if err != nil {
			return a, err
		}
	}
	if a.State == "orphaned" {
		return a, ErrUnavailable
	}
	if a.State == "linked" || a.State == "bytes_verified" {
		return a, nil
	}
	_, err = s.Media.StatObject(ctx, s.Bucket, a.Key, minio.StatObjectOptions{})
	if err != nil {
		if code := minio.ToErrorResponse(err).Code; code != "NoSuchKey" && code != "NoSuchObject" {
			return a, err
		}
		if int64(len(data)) != a.Size || contracts.Digest(data) != a.SHA {
			return a, errors.New("asset input digest mismatch")
		}
		if err = s.writeAssetObject(ctx, conn, a, bytes.NewReader(data)); err != nil {
			return a, err
		}
	} else {
		// Staged bytes have not entered the accepted store yet: check them once.
		return s.verifyAssetUnlocked(ctx, conn, id)
	}

	tx, err := beginWriteOn(ctx, conn)
	if err != nil {
		return a, err
	}
	defer tx.Rollback(context.Background())
	a, err = readAsset(ctx, tx, "asset_id", id, true)
	if err != nil {
		return a, err
	}
	if err = setAssetState(ctx, tx, a, "bytes_verified"); err != nil {
		return a, err
	}
	if err = tx.Commit(ctx); err != nil {
		return a, err
	}
	a.State = "bytes_verified"
	return a, nil
}
func (s *Storage) VerifyAsset(ctx context.Context, id string) (Asset, error) {
	conn, release, err := s.lockAsset(ctx, id)
	if err != nil {
		return Asset{}, err
	}
	defer release()
	return s.verifyAssetUnlocked(ctx, conn, id)
}
func (s *Storage) verifyAssetUnlocked(ctx context.Context, conn *pgxpool.Conn, id string) (Asset, error) {
	a, err := readAsset(ctx, conn, "asset_id", id, false)
	if err != nil {
		return a, err
	}
	if a.State == "linked" || a.State == "bytes_verified" {
		return a, nil
	}
	if a.State != "reserved" && a.State != "uploading" && a.State != "bytes_verified" {
		return a, ErrUnavailable
	}
	object, err := s.Media.GetObject(ctx, s.Bucket, a.Key, minio.GetObjectOptions{})
	if err != nil {
		return a, err
	}
	hash := sha256.New()
	count, err := io.Copy(hash, io.LimitReader(object, a.Size+1))
	closeErr := object.Close()
	if err != nil {
		return a, err
	}
	if closeErr != nil {
		return a, closeErr
	}
	valid := count == a.Size && hex.EncodeToString(hash.Sum(nil)) == a.SHA
	tx, err := beginWriteOn(ctx, conn)
	if err != nil {
		return a, err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	a, err = readAsset(ctx, tx, "asset_id", id, true)
	if err != nil {
		return a, err
	}
	if a.State == "linked" || a.State == "bytes_verified" {
		return a, nil
	}
	if a.State == "orphaned" {
		return a, ErrUnavailable
	}
	state := "bytes_verified"
	if !valid {
		state = "orphaned"
	}
	if err = setAssetState(ctx, tx, a, state); err != nil {
		return a, err
	}
	if !valid {
		if err = failAssetOperation(ctx, tx, a, "DIGEST_MISMATCH", "asset readback digest mismatch"); err != nil {
			return a, err
		}
	}
	if err = tx.Commit(ctx); err != nil {
		return a, err
	}
	a.State = state
	if !valid {
		return a, errors.New("asset readback digest mismatch")
	}
	return a, nil
}

// LinkAsset commits the verified asset, new owner version, exact reference and
// completed operation in one transaction. A stale owner keeps an orphan for recovery.
func (s *Storage) LinkAsset(ctx context.Context, id string, owner *DocumentWrite) (Asset, error) {
	tx, err := beginWrite(ctx, s)
	if err != nil {
		return Asset{}, err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	a, err := readAsset(ctx, tx, "asset_id", id, true)
	if err != nil {
		return a, err
	}
	var opState string
	if err = tx.QueryRow(ctx, "SELECT state FROM operation WHERE id=$1 FOR UPDATE", a.OperationID).Scan(&opState); err != nil {
		return a, err
	}
	if a.State == "linked" && opState == "complete" {
		return a, nil
	}
	if a.State != "bytes_verified" || opState != "reserved" {
		return a, ErrUnavailable
	}
	if a.Owner == nil && owner != nil {
		return a, ErrReference
	}
	if a.Owner != nil {
		if owner == nil || owner.Head == nil || owner.Head.ID != *a.Owner || owner.Head.Expected == nil || *owner.Head.Expected != *a.Revision {
			return a, ErrReference
		}
		var revision int64
		if err = tx.QueryRow(ctx, "SELECT revision FROM entity_head WHERE id=$1 FOR UPDATE", *a.Owner).Scan(&revision); err != nil {
			return a, err
		}
		if revision != *a.Revision {
			if err = setAssetState(ctx, tx, a, "orphaned"); err != nil {
				return a, err
			}
			_, err = tx.Exec(ctx, "UPDATE operation SET state='interrupted',finished_at=clock_timestamp() WHERE id=$1", a.OperationID)
			if err != nil {
				return a, err
			}
			if err = tx.Commit(ctx); err != nil {
				return a, err
			}
			a.State = "orphaned"
			return a, ErrRevision
		}
	}
	if err = setAssetState(ctx, tx, a, "linked"); err != nil {
		return a, err
	}
	a.State = "linked"
	var result string
	if err = tx.QueryRow(ctx, "SELECT document_id FROM entity_head WHERE id=$1", a.ID).Scan(&result); err != nil {
		return a, err
	}
	// Asset byte identity has its own version scope, independent of later lifecycle documents.
	if _, err = tx.Exec(ctx, "INSERT INTO object_node(node_id,scope_id,kind,document_id,json_pointer,content_sha256) VALUES($1,$1,'asset-bytes',$2,'/sha256',$3)", a.ID, result, a.SHA); err != nil {
		return a, err
	}
	if owner != nil {
		saved, err := validateDocument(*owner)
		if err != nil {
			return a, err
		}
		hasRef := false
		for _, r := range owner.References {
			if r.ID == a.ID && r.Scope == a.ID && r.Kind == "asset-bytes" && r.SHA == a.SHA {
				hasRef = true
			}
		}
		if !hasRef {
			return a, ErrReference
		}
		if err = insertDocument(ctx, tx, *owner, saved); err != nil {
			return a, err
		}
		result = owner.ID
	} else if a.Owner != nil {
		return a, ErrReference
	}
	if _, err = tx.Exec(ctx, "UPDATE operation SET state='complete',result_document_id=$2,finished_at=clock_timestamp() WHERE id=$1", a.OperationID, result); err != nil {
		return a, err
	}
	if owner != nil {
		if err = validateGraph(ctx, tx, owner.ID); err != nil {
			return a, err
		}
	}
	return a, tx.Commit(ctx)
}
func (s *Storage) ReadAsset(ctx context.Context, id string) ([]byte, error) {
	a, err := readAsset(ctx, s.DB, "asset_id", id, false)
	if err != nil {
		return nil, err
	}
	if a.State != "linked" {
		return nil, ErrUnavailable
	}
	o, err := s.Media.GetObject(ctx, s.Bucket, a.Key, minio.GetObjectOptions{})
	if err != nil {
		return nil, err
	}
	defer o.Close()
	b, err := io.ReadAll(o)
	if err != nil {
		return nil, err
	}
	return b, nil
}
func (s *Storage) OrphanPreview(ctx context.Context) ([]string, error) {
	rows, err := s.DB.Query(ctx, "SELECT a.asset_id FROM asset_location a WHERE a.state='orphaned' AND a.reserved_at <= clock_timestamp()-interval '30 days' AND NOT EXISTS(SELECT 1 FROM object_reference r WHERE r.target_id=a.asset_id) AND NOT EXISTS(SELECT 1 FROM document d WHERE d.kind='backup-manifest' AND d.payload::text LIKE '%'||a.asset_id||'%') ORDER BY a.asset_id")
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	ids := []string{}
	for rows.Next() {
		var id string
		if err = rows.Scan(&id); err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}
	return ids, rows.Err()
}
func assetError(err error) string {
	switch {
	case errors.Is(err, ErrConflict):
		return "conflict"
	case errors.Is(err, ErrRevision):
		return "revision_conflict"
	case errors.Is(err, ErrReference):
		return "reference_error"
	case errors.Is(err, ErrUnavailable):
		return "asset_unavailable"
	default:
		return fmt.Sprintf("storage_error")
	}
}

func validDigest(value string) bool {
	if len(value) != 64 {
		return false
	}
	decoded, err := hex.DecodeString(value)
	return err == nil && hex.EncodeToString(decoded) == value
}

func assetRequestDigest(r AssetRequest) (string, error) {
	// The exact intended bytes and ownership are part of idempotency identity.
	var err error
	r.Operation.Body, err = json.Marshal(struct {
		SHA     string          `json:"sha256"`
		Size    int64           `json:"byte_count"`
		Purpose string          `json:"purpose"`
		MIME    string          `json:"mime_type"`
		Owner   *HeadWrite      `json:"owner"`
		Context json.RawMessage `json:"context"`
	}{r.SHA, r.Size, r.Purpose, r.MIME, r.Owner, r.Operation.Body})
	if err != nil {
		return "", err
	}
	digest, err := operationDigest(r.Operation)
	if err != nil {
		return "", err
	}
	return digest, nil
}

// Keep the same acquired connection for every guarded read and short write.
// Duplicate waiters therefore cannot consume the winner's next connection.
func (s *Storage) lockAsset(ctx context.Context, id string) (*pgxpool.Conn, func(), error) {
	conn, err := s.DB.Acquire(ctx)
	if err != nil {
		return nil, nil, err
	}
	release := func() {
		cleanup, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if _, err := conn.Exec(cleanup, "SELECT pg_advisory_unlock(hashtextextended($1,0))", id); err != nil {
			// A connection with uncertain session-lock ownership must not return to the pool.
			_ = conn.Hijack().Close(cleanup)
			return
		}
		conn.Release()
	}
	if _, err = conn.Exec(ctx, "SELECT pg_advisory_lock(hashtextextended($1,0))", id); err != nil {
		release()
		return nil, nil, err
	}
	return conn, release, nil
}

// Failure, frozen asset result and typed error are durable in the same transaction.
func failAssetOperation(ctx context.Context, tx pgx.Tx, a Asset, code, message string) error {
	id := uuid.NewString()
	payload, err := json.Marshal(map[string]any{"code": code, "message": message, "request_id": a.OperationID, "retryable": true, "object_id": nil, "details": []any{}})
	if err != nil {
		return err
	}
	w := DocumentWrite{ID: id, Kind: "error-response", Version: "2.0.0", Scope: id, Payload: payload}
	saved, err := validateDocument(w)
	if err != nil {
		return err
	}
	if err = insertDocument(ctx, tx, w, saved); err != nil {
		return err
	}
	_, err = tx.Exec(ctx, "UPDATE operation SET state='failed',subject_id=$2::text,result_document_id=(SELECT document_id FROM entity_head WHERE id=$2::text),error_document_id=$3,finished_at=clock_timestamp() WHERE id=$1", a.OperationID, a.ID, id)
	return err
}

// Retry is a new reservation bound to precisely the original frozen intent.
func (s *Storage) RetryAsset(ctx context.Context, id string, r AssetRequest) (Asset, error) {
	return s.reserveAsset(ctx, r, id)
}
