package app

import (
	"context"
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"errors"
	"fmt"
	"net/mail"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
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

func (s *Storage) Migrate(ctx context.Context) error {
	tx, err := s.DB.Begin(ctx)
	if err != nil {
		return err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	if _, err = tx.Exec(ctx, "SET LOCAL lock_timeout='5s'; SELECT pg_advisory_xact_lock(79004731); CREATE TABLE IF NOT EXISTS schema_migrations (version text PRIMARY KEY, sha256 char(64) NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())"); err != nil {
		return err
	}
	entries, err := migrations.ReadDir("migrations")
	if err != nil {
		return err
	}
	for _, entry := range entries {
		body, err := migrations.ReadFile("migrations/" + entry.Name())
		if err != nil {
			return err
		}
		h := sha256.Sum256(body)
		digest := hex.EncodeToString(h[:])
		var stored string
		err = tx.QueryRow(ctx, "SELECT sha256 FROM schema_migrations WHERE version=$1", entry.Name()).Scan(&stored)
		if err == nil {
			if stored != digest {
				return errors.New("applied migration checksum mismatch")
			}
			continue
		}
		if !errors.Is(err, pgx.ErrNoRows) {
			return err
		}
		if _, err = tx.Exec(ctx, string(body)); err != nil {
			return err
		}
		if _, err = tx.Exec(ctx, "INSERT INTO schema_migrations(version,sha256) VALUES ($1,$2)", entry.Name(), digest); err != nil {
			return err
		}
	}
	return tx.Commit(ctx)
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
	return s.CheckPrivateMedia(ctx)
}

func (s *Storage) CheckPrivateMedia(ctx context.Context) error {
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

func (s *Storage) InitializeAccount(ctx context.Context, email, password string) error {
	parsed, err := mail.ParseAddress(email)
	if err != nil || parsed.Address != email || len(email) > 254 {
		return errors.New("invalid INITIAL_EMAIL")
	}
	if len(password) < 16 || len(password) > 1024 {
		return errors.New("INITIAL_PASSWORD must contain 16 to 1024 bytes")
	}
	// Existing credentials are never rotated by a restart or configuration change.
	var exists bool
	if err = s.DB.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM accounts WHERE email=$1)", email).Scan(&exists); err != nil {
		return err
	}
	if exists {
		return nil
	}
	hash, err := HashPassword(password)
	if err != nil {
		return err
	}
	_, err = s.DB.Exec(ctx, "INSERT INTO accounts(email,password_hash) VALUES($1,$2) ON CONFLICT(email) DO NOTHING", email, hash)
	return err
}

func (s *Storage) CheckDatabase(ctx context.Context) error {
	var accounts, catalog, sessions bool
	err := s.DB.QueryRow(ctx, "SELECT to_regclass('accounts') IS NOT NULL, to_regclass('exercise_catalog') IS NOT NULL, to_regclass('sessions') IS NOT NULL").Scan(&accounts, &catalog, &sessions)
	if err != nil {
		return err
	}
	if !accounts || !catalog || !sessions {
		return fmt.Errorf("database migration incomplete")
	}
	var n int
	if err = s.DB.QueryRow(ctx, "SELECT count(*) FROM accounts").Scan(&n); err != nil {
		return err
	}
	if n == 0 {
		return errors.New("local account initialization incomplete")
	}
	return nil
}
