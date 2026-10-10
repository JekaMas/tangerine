package app

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/minio/minio-go/v7"
	"io"
)

// startMultipart saves the exact native upload ID before sending any parts.
func (s *Storage) startMultipart(ctx context.Context, conn *pgxpool.Conn, a Asset) (string, error) {
	core := minio.Core{Client: s.Media}
	id, err := core.NewMultipartUpload(ctx, s.Bucket, a.Key, minio.PutObjectOptions{ContentType: "application/octet-stream"})
	if err != nil {
		return "", err
	}
	tx, err := beginWriteOn(ctx, conn)
	if err != nil {
		_ = core.AbortMultipartUpload(ctx, s.Bucket, a.Key, id)
		return "", err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	locked, err := readAsset(ctx, tx, "asset_id", a.ID, true)
	if err != nil || locked.State != "reserved" {
		_ = core.AbortMultipartUpload(ctx, s.Bucket, a.Key, id)
		return "", ErrUnavailable
	}
	if err = setAssetState(ctx, tx, a, "uploading"); err != nil {
		_ = core.AbortMultipartUpload(ctx, s.Bucket, a.Key, id)
		return "", err
	}
	if _, err = tx.Exec(ctx, "UPDATE asset_location SET multipart_upload_id=$2 WHERE asset_id=$1", a.ID, id); err != nil {
		_ = core.AbortMultipartUpload(ctx, s.Bucket, a.Key, id)
		return "", err
	}
	if err = tx.Commit(ctx); err != nil {
		_ = core.AbortMultipartUpload(ctx, s.Bucket, a.Key, id)
		return "", err
	}
	return id, nil
}
func (s *Storage) writeAssetObject(ctx context.Context, conn *pgxpool.Conn, a Asset, reader io.Reader) error {
	if a.Size <= 5*1024*1024 {
		_, err := s.Media.PutObject(ctx, s.Bucket, a.Key, reader, a.Size, minio.PutObjectOptions{DisableMultipart: true, ContentType: "application/octet-stream"})
		return err
	}
	upload, err := s.startMultipart(ctx, conn, a)
	if err != nil {
		return err
	}
	core := minio.Core{Client: s.Media}
	parts := []minio.CompletePart{}
	remaining := a.Size
	// MinIO's 10,000-part ceiling permits files up to its five-terabyte limit.
	partSize := int64(64 * 1024 * 1024)
	if needed := (a.Size + 9998) / 9999; needed > partSize {
		partSize = needed
	}
	for number := 1; remaining > 0; number++ {
		size := partSize
		if remaining < size {
			size = remaining
		}
		part, err := core.PutObjectPart(ctx, s.Bucket, a.Key, upload, number, io.LimitReader(reader, size), size, minio.PutObjectPartOptions{})
		if err != nil {
			return err
		}
		parts = append(parts, minio.CompletePart{PartNumber: number, ETag: part.ETag})
		remaining -= size
	}
	var extra [1]byte
	if n, err := reader.Read(extra[:]); n != 0 || err != io.EOF {
		return errors.New("unexpected asset stream length")
	}
	_, err = core.CompleteMultipartUpload(ctx, s.Bucket, a.Key, upload, parts, minio.PutObjectOptions{})
	return err
}

// RecoverAsset never invents bytes or marks an incomplete upload verified. It
// aborts only this reservation's exact multipart ID and reuses a completed object.
func (s *Storage) RecoverAsset(ctx context.Context, id string) (Asset, error) {
	conn, release, err := s.lockAsset(ctx, id)
	if err != nil {
		return Asset{}, err
	}
	defer release()
	return s.recoverAssetUnlocked(ctx, conn, id)
}
func (s *Storage) recoverAssetUnlocked(ctx context.Context, conn *pgxpool.Conn, id string) (Asset, error) {
	a, err := readAsset(ctx, conn, "asset_id", id, false)
	if err != nil {
		return a, err
	}
	if a.State == "linked" || a.State == "orphaned" || a.State == "bytes_verified" {
		return a, nil
	}
	_, err = s.Media.StatObject(ctx, s.Bucket, a.Key, minio.StatObjectOptions{})
	if err == nil {
		return s.verifyAssetUnlocked(ctx, conn, id)
	}
	code := minio.ToErrorResponse(err).Code
	if code != "NoSuchKey" && code != "NoSuchObject" {
		return a, err
	}
	var upload *string
	if err = conn.QueryRow(ctx, "SELECT multipart_upload_id FROM asset_location WHERE asset_id=$1", id).Scan(&upload); err != nil {
		return a, err
	}
	if upload == nil {
		return a, nil
	}
	core := minio.Core{Client: s.Media}
	if err = core.AbortMultipartUpload(ctx, s.Bucket, a.Key, *upload); err != nil && minio.ToErrorResponse(err).Code != "NoSuchUpload" {
		return a, err
	}
	tx, err := beginWriteOn(ctx, conn)
	if err != nil {
		return a, err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	a, err = readAsset(ctx, tx, "asset_id", id, true)
	if err != nil {
		return a, err
	}
	if a.State != "uploading" {
		return a, ErrUnavailable
	}
	if err = setAssetState(ctx, tx, a, "orphaned"); err != nil {
		return a, err
	}
	if _, err = tx.Exec(ctx, "UPDATE asset_location SET multipart_upload_id=NULL WHERE asset_id=$1 AND multipart_upload_id=$2", id, *upload); err != nil {
		return a, err
	}
	if err = failAssetOperation(ctx, tx, a, "INFRASTRUCTURE_UNAVAILABLE", "interrupted multipart upload aborted"); err != nil {
		return a, err
	}
	a.State = "orphaned"
	return a, tx.Commit(ctx)
}

// UploadReader supports future full-source consumers without buffering files.
func (s *Storage) UploadReader(ctx context.Context, id string, r io.Reader) (Asset, error) {
	a, err := readAsset(ctx, s.DB, "asset_id", id, false)
	if err != nil {
		return a, err
	}
	if a.State != "reserved" {
		return a, ErrUnavailable
	}
	conn, release, err := s.lockAsset(ctx, id)
	if err != nil {
		return a, err
	}
	defer release()
	a, err = s.recoverAssetUnlocked(ctx, conn, id)
	if err != nil {
		return a, err
	}
	if a.State == "bytes_verified" || a.State == "linked" {
		return a, nil
	}
	if a.State != "reserved" {
		return a, ErrUnavailable
	}
	if err = s.writeAssetObject(ctx, conn, a, r); err != nil {
		return a, err
	}
	return s.verifyAssetUnlocked(ctx, conn, id)
}

// Native maintenance primitive used to inspect an interrupted multipart upload.
func (s *Storage) BeginAssetUpload(ctx context.Context, id string) (string, error) {
	conn, release, err := s.lockAsset(ctx, id)
	if err != nil {
		return "", err
	}
	defer release()
	a, err := readAsset(ctx, conn, "asset_id", id, false)
	if err != nil {
		return "", err
	}
	return s.startMultipart(ctx, conn, a)
}
