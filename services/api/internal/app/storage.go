package app

import (
	"context"
	"embed"
	"encoding/json"
	"errors"
	"strings"
	"tangerine.local/api/internal/contracts"
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
	return s.CheckPrivateMedia(ctx)
}

func (s *Storage) CheckPrivateMedia(ctx context.Context) error {
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

var ErrMigrationRequired = errors.New("database migration required")

//go:embed required_columns.json
var requiredColumns []byte

func (s *Storage) CheckDatabase(ctx context.Context) error {
	history, err := validateHistory(ctx, s.DB)
	if err != nil {
		return ErrMigrationRequired
	}
	entries, _ := migrations.ReadDir("migrations")
	if len(history) != len(entries) {
		return ErrMigrationRequired
	}
	var expected map[string][]string
	if err = json.Unmarshal(requiredColumns, &expected); err != nil {
		return err
	}
	rows, err := s.DB.Query(ctx, "SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public'")
	if err != nil {
		return err
	}
	actual := map[string]map[string]bool{}
	for rows.Next() {
		var table, column string
		if err = rows.Scan(&table, &column); err != nil {
			rows.Close()
			return err
		}
		if actual[table] == nil {
			actual[table] = map[string]bool{}
		}
		actual[table][column] = true
	}
	rows.Close()
	if err = rows.Err(); err != nil {
		return err
	}
	for table, columns := range expected {
		for _, column := range columns {
			if !actual[table][column] {
				return ErrMigrationRequired
			}
		}
	}
	var count int
	if err = s.DB.QueryRow(ctx, "SELECT count(*) FROM workspace w JOIN workspaces f ON f.id=w.foundation_workspace_id WHERE w.id='local' AND f.singleton").Scan(&count); err != nil || count != 1 {
		return ErrMigrationRequired
	}
	// Check each actual guard, not merely a reusable trigger name.
	guardSQL, err := migrations.ReadFile("migrations/003_domain_storage.sql")
	if err != nil {
		return err
	}
	body := strings.SplitN(string(guardSQL), "CREATE FUNCTION reject_document_mutation() RETURNS trigger LANGUAGE plpgsql AS $$", 2)
	if len(body) != 2 {
		return ErrMigrationRequired
	}
	expectedBody := strings.TrimSpace(strings.SplitN(body[1], "$$;", 2)[0])
	for name, table := range map[string]string{"document_immutable": "document", "audit_immutable": "audit_event", "schema_immutable": "schema_registry", "migration_backup_immutable": "migration_backup"} {
		var valid bool
		var actualBody string
		err = s.DB.QueryRow(ctx, `SELECT t.tgenabled IN ('O','A') AND t.tgtype=27 AND t.tgqual IS NULL AND t.tgnargs=0 AND p.proname='reject_document_mutation' AND pn.nspname='public' AND p.pronargs=0 AND p.prorettype='trigger'::regtype AND l.lanname='plpgsql',p.prosrc
   FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid JOIN pg_namespace pn ON pn.oid=p.pronamespace JOIN pg_language l ON l.oid=p.prolang
   WHERE NOT t.tgisinternal AND t.tgname=$1 AND n.nspname='public' AND c.relname=$2`, name, table).Scan(&valid, &actualBody)
		if err != nil || !valid || strings.TrimSpace(actualBody) != expectedBody {
			return ErrMigrationRequired
		}
	}
	registry, err := contracts.Registry()
	if err != nil {
		return err
	}
	for _, c := range registry {
		var sha string
		var raw []byte
		if err = s.DB.QueryRow(ctx, "SELECT sha256,schema_json FROM schema_registry WHERE kind=$1 AND version=$2 AND sha256=$3", c.Kind, c.Version, c.SHA).Scan(&sha, &raw); err != nil {
			return ErrMigrationRequired
		}
		a, _ := contracts.Canonical(c.Bytes)
		b, _ := contracts.Canonical(raw)
		if string(a) != string(b) {
			return ErrMigrationRequired
		}
	}
	return nil
}
