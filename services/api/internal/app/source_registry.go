package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"strconv"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
	"time"
)

func (s *Storage) SourceRelease(ctx context.Context, id string) (SourceRelease, error) {
	var b []byte
	var r SourceRelease
	e := s.DB.QueryRow(ctx, "SELECT payload FROM source_release WHERE id=$1", id).Scan(&b)
	if e == nil {
		e = json.Unmarshal(b, &r)
	}
	return r, e
}
func (s *Storage) sourceAssetsExist(ctx context.Context, ids []string) error {
	for _, id := range ids {
		var exists bool
		if e := s.DB.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM asset_location WHERE asset_id=$1 AND state='linked')", id).Scan(&exists); e != nil {
			return e
		}
		if !exists {
			return ErrReference
		}
	}
	return nil
}
func (s *Storage) RegisterSource(ctx context.Context, body []byte, key string) (SourceRelease, error) {
	var r SourceRelease
	_, b, e := contracts.Validate("source-release-request", "2.0.0", body)
	if e != nil {
		return r, ErrInput
	}
	if e = json.Unmarshal(b, &r); e != nil {
		return r, e
	}
	if !source.Known(r.Source) {
		return r, ErrInput
	}
	if r.Scope == "" {
		r.Scope = "partial_export"
	}
	if !sourceScope(r.Scope) {
		return r, ErrInput
	}
	if e = s.sourceAssetsExist(ctx, r.Docs); e != nil {
		return r, e
	}
	files := map[string]bool{}
	for _, f := range r.Files {
		n, e := source.SafePath(f.Path)
		if e != nil || n != f.Path || files[n] {
			return r, ErrInput
		}
		files[n] = true
		if _, e = strconv.ParseInt(f.Bytes, 10, 64); e != nil {
			return r, ErrInput
		}
	}
	req := OperationRequest{Name: "source_release", Key: key, Path: "/api/v1/source-releases", Body: b}
	digest, e := operationDigest(req)
	if e != nil {
		return r, ErrInput
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return r, e
	}
	defer tx.Rollback(context.Background())
	op, fresh, e := reserveOperation(ctx, tx, req, digest)
	if e != nil {
		return r, e
	}
	if !fresh {
		var id string
		if e = tx.QueryRow(ctx, "SELECT subject_id FROM operation WHERE id=$1", op.ID).Scan(&id); e != nil {
			return r, e
		}
		if e = tx.Commit(ctx); e != nil {
			return r, e
		}
		return s.SourceRelease(ctx, id)
	}
	r.ID = uuid.NewString()
	r.Observed = []SourceCount{}
	canonical, _ := contracts.Canonical(sourceBytes(r.Files))
	r.Manifest = contracts.Digest(canonical)
	if r.Profile != nil {
		var src string
		if e = tx.QueryRow(ctx, "SELECT source_id FROM source_format WHERE id=$1", *r.Profile).Scan(&src); e != nil || src != r.Source {
			return r, ErrReference
		}
	}
	if _, e = tx.Exec(ctx, "INSERT INTO source_release(id,source_id,payload,scope_kind) VALUES($1,$2,$3,$4)", r.ID, r.Source, sourceBytes(r), r.Scope); e != nil {
		return r, e
	}
	for _, f := range r.Files {
		var file string
		e = tx.QueryRow(ctx, "SELECT id FROM source_file WHERE relative_path=$1 AND sha256=$2 AND byte_count=$3::bigint", f.Path, f.SHA, f.Bytes).Scan(&file)
		if e != nil {
			return r, fmt.Errorf("%w: unacquired member %s", ErrReference, f.Path)
		}
		if _, e = tx.Exec(ctx, "INSERT INTO source_member(release_id,relative_path,file_id,component,partition) VALUES($1,$2,$3,$4,$5)", r.ID, f.Path, file, f.Component, f.Partition); e != nil {
			return r, e
		}
	}
	if _, e = tx.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2,finished_at=clock_timestamp() WHERE id=$1", op.ID, r.ID); e != nil {
		return r, e
	}
	return r, tx.Commit(ctx)
}
func sourceTime() string          { return time.Now().UTC().Format(time.RFC3339Nano) }
func sourceNotFound(e error) bool { return errors.Is(e, pgx.ErrNoRows) }
