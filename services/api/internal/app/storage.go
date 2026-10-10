package app

import (
	"context"
	"embed"
	"errors"
	"strings"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

//go:embed migrations/*.sql
var migrations embed.FS

type Storage struct {
	DB     *pgxpool.Pool
	Media  *minio.Client
	Bucket string
}

func OpenStorage(ctx context.Context, databaseURL, endpoint, accessKey, secretKey, bucket string) (*Storage, error) {
	if databaseURL == "" || endpoint == "" || accessKey == "" || secretKey == "" || bucket == "" {
		return nil, errors.New("missing local storage configuration")
	}
	config, err := pgxpool.ParseConfig(databaseURL)
	if err != nil {
		return nil, errors.New("invalid database configuration")
	}
	config.MaxConns = 10
	config.ConnConfig.ConnectTimeout = 5 * time.Second
	pool, err := pgxpool.NewWithConfig(ctx, config)
	if err != nil {
		return nil, errors.New("database configuration failed")
	}
	media, err := minio.New(endpoint, &minio.Options{Creds: credentials.NewStaticV4(accessKey, secretKey, ""), Secure: false})
	if err != nil {
		pool.Close()
		return nil, errors.New("invalid media configuration")
	}
	return &Storage{DB: pool, Media: media, Bucket: bucket}, nil
}

func (s *Storage) InitMedia(ctx context.Context) error {
	exists, err := s.Media.BucketExists(ctx, s.Bucket)
	if err != nil {
		return err
	}
	if !exists {
		if err = s.Media.MakeBucket(ctx, s.Bucket, minio.MakeBucketOptions{}); err != nil {
			return err
		}
	}
	return s.validatePrivateMedia(ctx)
}

func (s *Storage) validatePrivateMedia(ctx context.Context) error {
	exists, err := s.Media.BucketExists(ctx, s.Bucket)
	if err != nil {
		return err
	}
	if !exists {
		return errors.New("private media initialization incomplete")
	}
	policy, err := s.Media.GetBucketPolicy(ctx, s.Bucket)
	if err != nil {
		if minio.ToErrorResponse(err).Code == "NoSuchBucketPolicy" {
			return nil
		}
		return err
	}
	if strings.TrimSpace(policy) != "" {
		return errors.New("media bucket must have no public policy")
	}
	return nil
}

// Accepted bucket configuration is trusted; readiness checks availability only.
func (s *Storage) CheckPrivateMedia(ctx context.Context) error {
	exists, e := s.Media.BucketExists(ctx, s.Bucket)
	if e != nil {
		return e
	}
	if !exists {
		return errors.New("private media unavailable")
	}
	return nil
}

var ErrMigrationRequired = errors.New("database migration required")

// CheckDatabase observes current availability. Initialization owns migration
// admission; ordinary readiness trusts the accepted database.
func (s *Storage) CheckDatabase(ctx context.Context) error { return s.DB.Ping(ctx) }
