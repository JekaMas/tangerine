package app

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"tangerine.local/api/internal/recovery"
)

func SupportedMigrations() []string {
	entries, _ := migrations.ReadDir("migrations")
	out := []string{}
	for _, e := range entries {
		out = append(out, e.Name())
	}
	sort.Strings(out)
	return out
}
func (s *Storage) postgresEnvironment() []string {
	c := s.DB.Config().ConnConfig
	return append(os.Environ(), "PGHOST="+c.Host, "PGPORT="+itoa(int(c.Port)), "PGUSER="+c.User, "PGDATABASE="+c.Database, "PGPASSWORD="+c.Password, "PGSSLMODE=disable")
}

// Snapshot is invoked only by the local helper after stopping application writers.
// It reads every actual private object, not just the currently selected heads.
func (s *Storage) Snapshot(ctx context.Context, out io.Writer) error {
	conn, e := s.DB.Acquire(ctx)
	if e != nil {
		return e
	}
	defer conn.Release()
	if _, e = conn.Exec(ctx, "SELECT pg_advisory_lock(79004731)"); e != nil {
		return e
	}
	defer func() {
		end, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if _, err := conn.Exec(end, "SELECT pg_advisory_unlock(79004731)"); err != nil {
			_ = conn.Hijack().Close(end)
		}
	}()
	dir, e := os.MkdirTemp("", "tangerine-snapshot-")
	if e != nil {
		return e
	}
	defer os.RemoveAll(dir)
	rows, e := s.DB.Query(ctx, "SELECT version FROM schema_migrations ORDER BY version")
	if e != nil {
		return e
	}
	versions := []string{}
	for rows.Next() {
		var v string
		if e = rows.Scan(&v); e != nil {
			rows.Close()
			return e
		}
		versions = append(versions, v)
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return e
	}
	cmd := exec.CommandContext(ctx, "pg_dump", "--format=custom", "--no-owner", "--no-privileges", "--exclude-table-data=legacy_accounts", "--exclude-table-data=legacy_sessions", "--file="+dir+"/database.dump")
	cmd.Env = s.postgresEnvironment()
	if e = cmd.Run(); e != nil {
		return errors.New("BACKUP_FAILED: database export failed")
	}
	w := recovery.New(out, uuid.NewString(), versions)
	f, e := os.Open(dir + "/database.dump")
	if e != nil {
		return e
	}
	info, e := f.Stat()
	if e == nil {
		e = w.Add("database.dump", info.Size(), f)
	}
	f.Close()
	if e != nil {
		return e
	}
	for obj := range s.Media.ListObjects(ctx, s.Bucket, minio.ListObjectsOptions{Recursive: true}) {
		if obj.Err != nil {
			return obj.Err
		}
		stream, e := s.Media.GetObject(ctx, s.Bucket, obj.Key, minio.GetObjectOptions{})
		if e != nil {
			return e
		}
		e = w.Add("media/"+obj.Key, obj.Size, stream)
		stream.Close()
		if e != nil {
			return e
		}
	}
	for _, kind := range []string{"models", "lab"} {
		root := "/snapshot-" + kind
		if _, e = os.Stat(root); os.IsNotExist(e) {
			continue
		}
		if e != nil {
			return e
		}
		included := false
		e = filepath.WalkDir(root, func(p string, d os.DirEntry, err error) error {
			if err != nil {
				return err
			}
			if d.IsDir() {
				return nil
			}
			actual, err := filepath.EvalSymlinks(p)
			if err != nil {
				return err
			}
			rel, err := filepath.Rel(root, actual)
			if err != nil || rel == ".." || strings.HasPrefix(rel, "../") {
				return errors.New("BACKUP_FAILED: external cache symlink")
			}
			file, err := os.Open(actual)
			if err != nil {
				return err
			}
			defer file.Close()
			st, err := file.Stat()
			if err != nil {
				return err
			}
			if !st.Mode().IsRegular() {
				return errors.New("BACKUP_FAILED: non-file cache entry")
			}
			rel, err = filepath.Rel(root, p)
			if err != nil {
				return err
			}
			included = true
			return w.Add(kind+"/"+filepath.ToSlash(rel), st.Size(), file)
		})
		if e != nil {
			return e
		}
		if kind == "models" {
			w.Manifest.Models = included
		} else {
			w.Manifest.Lab = included
		}
	}
	return w.Close()
}

// RestoreSnapshot admits the supplied new archive once, then uses the accepted
// staged bytes. It is called only against a fresh project, never a live workspace.
func (s *Storage) RestoreSnapshot(ctx context.Context, input io.Reader, out io.Writer) error {
	dir, e := os.MkdirTemp("", "tangerine-restore-")
	if e != nil {
		return e
	}
	defer os.RemoveAll(dir)
	m, e := recovery.Admit(input, dir, SupportedMigrations())
	if e != nil {
		return e
	}
	var occupied bool
	if e = s.DB.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema='public')").Scan(&occupied); e != nil {
		return e
	}
	if occupied {
		return errors.New("RESTORE_TARGET_EXISTS: fresh database required")
	}
	cmd := exec.CommandContext(ctx, "pg_restore", "--no-owner", "--no-privileges", "--exit-on-error", "--dbname="+s.DB.Config().ConnConfig.Database, dir+"/database.dump")
	cmd.Env = s.postgresEnvironment()
	if e = cmd.Run(); e != nil {
		return errors.New("RESTORE_FAILED: database import failed; previous workspace retained")
	}
	if e = s.InitMedia(ctx); e != nil {
		return e
	}
	for _, entry := range m.Files {
		if entry.Path == "database.dump" {
			continue
		}
		file, e := os.Open(filepath.Join(dir, filepath.FromSlash(entry.Path)))
		if e != nil {
			return e
		}
		switch {
		case strings.HasPrefix(entry.Path, "media/"):
			_, e = s.Media.PutObject(ctx, s.Bucket, strings.TrimPrefix(entry.Path, "media/"), file, entry.Bytes, minio.PutObjectOptions{})
		default:
			kind, rel, _ := strings.Cut(entry.Path, "/")
			target := filepath.Join("/restore-"+kind, filepath.FromSlash(rel))
			e = os.MkdirAll(filepath.Dir(target), 0700)
			if e == nil {
				var dest *os.File
				dest, e = os.OpenFile(target, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
				if e == nil {
					_, e = io.Copy(dest, file)
					ce := dest.Close()
					if e == nil {
						e = ce
					}
				}
			}
		}
		file.Close()
		if e != nil {
			return e
		}
	}
	if m.Models {
		if e = filepath.WalkDir("/restore-models", func(p string, d os.DirEntry, err error) error {
			if err != nil {
				return err
			}
			return os.Chown(p, 65532, 65532)
		}); e != nil {
			return e
		}
	}
	// Credentials live only outside the archive; report reconnect rather than
	// inventing a restored authentication grant or contacting a provider.
	return json.NewEncoder(out).Encode(map[string]any{"status": "restored", "backup_id": m.ID, "files": len(m.Files), "models_restored": m.Models, "lab_restored": m.Lab, "provider_credentials": "not_restored_reconnect_or_supply_keys", "migrations": m.Migrations, "inference_calls": 0})
}
