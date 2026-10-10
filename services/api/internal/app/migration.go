package app

import (
	"archive/tar"
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"os"
	"os/exec"
	"sort"
	"strings"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/minio/minio-go/v7"
	"tangerine.local/api/internal/contracts"
)

// readMigrationHistory trusts the saved applied-version list. New migration
// statements are applied only when their version is absent.
func readMigrationHistory(ctx context.Context, q interface {
	Query(context.Context, string, ...any) (pgx.Rows, error)
	QueryRow(context.Context, string, ...any) pgx.Row
}) (map[string]string, error) {
	var exists bool
	if err := q.QueryRow(ctx, "SELECT to_regclass('schema_migrations') IS NOT NULL").Scan(&exists); err != nil {
		return nil, err
	}
	history := map[string]string{}
	if !exists {
		return history, nil
	}
	rows, err := q.Query(ctx, "SELECT version,sha256 FROM schema_migrations ORDER BY version")
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	for rows.Next() {
		var name, sha string
		if err = rows.Scan(&name, &sha); err != nil {
			return nil, err
		}
		history[name] = sha
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return history, nil
}

type upgradeBackup struct {
	ID, Key, SHA                string
	Size                        int64
	Vector, Inventory, Manifest []byte
}

// upgradeBackup freezes application writers with the migration's session lock.
// pg_dump is native, passwords stay in process environment, and all existing
// private object bytes are archived with a provenance manifest before change.
func (s *Storage) backupUpgrade(ctx context.Context, history map[string]string) (upgradeBackup, error) {
	var receipt upgradeBackup
	dir, err := os.MkdirTemp("", "tangerine-upgrade-")
	if err != nil {
		return receipt, err
	}
	defer os.RemoveAll(dir)
	config := s.DB.Config().ConnConfig
	env := append(os.Environ(), "PGHOST="+config.Host, "PGPORT="+itoa(int(config.Port)), "PGUSER="+config.User, "PGDATABASE="+config.Database, "PGPASSWORD="+config.Password, "PGSSLMODE=disable")
	cmd := exec.CommandContext(ctx, "pg_dump", "--format=custom", "--no-owner", "--no-privileges", "--file="+dir+"/database.dump")
	cmd.Env = env
	if err = cmd.Run(); err != nil {
		return receipt, errors.New("upgrade database backup failed")
	}
	inventory := []map[string]any{}
	rows, err := s.DB.Query(ctx, "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")
	if err != nil {
		return receipt, err
	}
	tables := []string{}
	for rows.Next() {
		var t string
		if err = rows.Scan(&t); err != nil {
			rows.Close()
			return receipt, err
		}
		tables = append(tables, t)
	}
	rows.Close()
	if err = rows.Err(); err != nil {
		return receipt, err
	}
	for _, t := range tables {
		var count int64
		if err = s.DB.QueryRow(ctx, "SELECT count(*) FROM "+pgx.Identifier{t}.Sanitize()).Scan(&count); err != nil {
			return receipt, err
		}
		inventory = append(inventory, map[string]any{"table": t, "rows": count})
	}
	archive, err := os.Create(dir + "/backup.tar")
	if err != nil {
		return receipt, err
	}
	defer archive.Close()
	tw := tar.NewWriter(archive)
	manifest := []map[string]any{}
	appendFile := func(name string, r io.Reader, size int64) error {
		if err := tw.WriteHeader(&tar.Header{Name: name, Mode: 0600, Size: size}); err != nil {
			return err
		}
		h := sha256.New()
		n, err := io.CopyN(io.MultiWriter(tw, h), r, size)
		if err != nil || n != size {
			return errors.New("backup input incomplete")
		}
		manifest = append(manifest, map[string]any{"path": name, "sha256": hex.EncodeToString(h.Sum(nil)), "byte_count": size})
		return nil
	}
	dump, err := os.Open(dir + "/database.dump")
	if err != nil {
		return receipt, err
	}
	defer dump.Close()
	stat, err := dump.Stat()
	if err != nil {
		return receipt, err
	}
	if err = appendFile("database.dump", dump, stat.Size()); err != nil {
		return receipt, err
	}
	exists, err := s.Media.BucketExists(ctx, s.Bucket)
	if err != nil {
		return receipt, err
	}
	if exists {
		for object := range s.Media.ListObjects(ctx, s.Bucket, minio.ListObjectsOptions{Recursive: true}) {
			if object.Err != nil {
				return receipt, object.Err
			}
			reader, err := s.Media.GetObject(ctx, s.Bucket, object.Key, minio.GetObjectOptions{})
			if err != nil {
				return receipt, err
			}
			info, err := reader.Stat()
			if err != nil {
				_ = reader.Close()
				return receipt, err
			}
			err = appendFile("objects/"+object.Key, reader, info.Size)
			_ = reader.Close()
			if err != nil {
				return receipt, err
			}

		}
	}
	receipt.Vector, _ = json.Marshal(history)
	receipt.Inventory, _ = json.Marshal(inventory)
	receipt.Manifest, _ = json.Marshal(manifest)
	meta, _ := json.Marshal(map[string]any{"source_vector": history, "table_inventory": inventory, "files": manifest})
	if err = appendFile("manifest.json", bytes.NewReader(meta), int64(len(meta))); err != nil {
		return receipt, err
	}
	if err = tw.Close(); err != nil {
		return receipt, err
	}
	if err = archive.Sync(); err != nil {
		return receipt, err
	}
	if _, err = archive.Seek(0, 0); err != nil {
		return receipt, err
	}
	stat, err = archive.Stat()
	if err != nil {
		return receipt, err
	}
	hash := sha256.New()
	count, err := io.Copy(hash, archive)
	if err != nil || count != stat.Size() {
		return receipt, errors.New("backup digest failed")
	}
	receipt.SHA = hex.EncodeToString(hash.Sum(nil))
	receipt.Size = count
	if _, err = archive.Seek(0, 0); err != nil {
		return receipt, err
	}
	if !exists {
		if err = s.Media.MakeBucket(ctx, s.Bucket, minio.MakeBucketOptions{}); err != nil {
			return receipt, err
		}
	}
	receipt.ID = uuid.NewString()
	receipt.Key = uuid.NewString()
	if _, err = archive.Seek(0, 0); err != nil {
		return receipt, err
	}
	if _, err = s.Media.PutObject(ctx, s.Bucket, receipt.Key, archive, receipt.Size, minio.PutObjectOptions{ContentType: "application/x-tar"}); err != nil {
		return receipt, err
	}
	return receipt, nil
}
func itoa(n int) string { b, _ := json.Marshal(n); return string(b) }
func (s *Storage) Migrate(ctx context.Context) error {
	conn, err := s.DB.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()
	if _, err = conn.Exec(ctx, "SET lock_timeout='5s'; SELECT pg_advisory_lock(79004731)"); err != nil {
		return err
	}
	defer func() { _, _ = conn.Exec(context.Background(), "SELECT pg_advisory_unlock(79004731)") }()
	history, err := readMigrationHistory(ctx, conn)
	if err != nil {
		return err
	}
	var backup *upgradeBackup
	_, domainApplied := history["003_domain_storage.sql"]
	if len(history) > 0 && !domainApplied {
		b, err := s.backupUpgrade(ctx, history)
		if err != nil {
			return err
		}
		backup = &b
	}
	tx, err := conn.Begin(ctx)
	if err != nil {
		return err
	}
	defer func() { _ = tx.Rollback(context.Background()) }()
	if _, err = tx.Exec(ctx, "CREATE TABLE IF NOT EXISTS schema_migrations(version text PRIMARY KEY,sha256 char(64) NOT NULL,applied_at timestamptz NOT NULL DEFAULT now())"); err != nil {
		return err
	}
	entries, _ := migrations.ReadDir("migrations")
	for _, e := range entries {
		if _, applied := history[e.Name()]; applied {
			continue
		}
		b, _ := migrations.ReadFile("migrations/" + e.Name())
		if _, err = tx.Exec(ctx, string(b)); err != nil {
			return err
		}
		if _, err = tx.Exec(ctx, "INSERT INTO schema_migrations(version,sha256) VALUES($1,$2)", e.Name(), contracts.Digest(b)); err != nil {
			return err
		}
	}
	registry, err := contracts.Registry()
	if err != nil {
		return err
	}
	kinds := []string{}
	for k := range registry {
		kinds = append(kinds, k)
	}
	sort.Strings(kinds)
	vector := []string{}
	for _, k := range kinds {
		c := registry[k]
		if _, err = tx.Exec(ctx, "INSERT INTO schema_registry(kind,version,sha256,schema_json) VALUES($1,$2,$3,$4) ON CONFLICT DO NOTHING", c.Kind, c.Version, c.SHA, c.Bytes); err != nil {
			return err
		}
		vector = append(vector, c.Kind+":"+c.Version+":"+c.SHA)
	}
	if _, err = tx.Exec(ctx, "INSERT INTO migration_receipt(migration_id,source_sha256,contract_vector_sha256) VALUES('003_domain_storage.sql',$1,$2) ON CONFLICT DO NOTHING", contracts.Digest(mustMigration("003_domain_storage.sql")), contracts.Digest([]byte(strings.Join(vector, "\n")))); err != nil {
		return err
	}
	if backup != nil {
		if _, err = tx.Exec(ctx, "INSERT INTO migration_backup(id,source_vector,table_inventory,storage_key,sha256,byte_count,verified_at,manifest) VALUES($1,$2,$3,$4,$5,$6,clock_timestamp(),$7)", backup.ID, backup.Vector, backup.Inventory, backup.Key, backup.SHA, backup.Size, backup.Manifest); err != nil {
			return err
		}
	}
	return tx.Commit(ctx)
}
func mustMigration(name string) []byte { b, _ := migrations.ReadFile("migrations/" + name); return b }
