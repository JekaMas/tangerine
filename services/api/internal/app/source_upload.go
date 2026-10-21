package app

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"io"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"tangerine.local/api/internal/source"
)

// saveSourceStream computes actual new-input identity once. The accepted spool is
// handed to the existing private multipart owner without a second hash/readback.
func (s *Storage) saveSourceStream(ctx context.Context, name string, r io.Reader) (source.Member, error) {
	name, e := source.SafePath(name)
	if e != nil {
		return source.Member{}, e
	}
	f, e := os.CreateTemp("", "tangerine-source-")
	if e != nil {
		return source.Member{}, e
	}
	defer os.Remove(f.Name())
	defer f.Close()
	h := sha256.New()
	n, e := io.Copy(io.MultiWriter(f, h), io.LimitReader(r, source.DefaultLimits.MemberBytes+1))
	if e != nil {
		return source.Member{}, e
	}
	if n > source.DefaultLimits.MemberBytes {
		return source.Member{}, source.Failure(name, "intake_limit", "Operator member limit exceeded")
	}
	digest := hex.EncodeToString(h.Sum(nil))
	m := source.NewMember(name)
	m.SHA = digest
	m.Bytes = n
	if strings.EqualFold(filepath.Ext(name), ".wav") {
		metadata, err := source.WaveInfo(f)
		if err != nil {
			m.Media = map[string]any{"error": "invalid_source_wave"}
		} else {
			m.Media = metadata
		}
	}
	var saved string
	e = s.DB.QueryRow(ctx, "SELECT asset_id FROM source_file WHERE relative_path=$1 AND sha256=$2 AND byte_count=$3", name, digest, n).Scan(&saved)
	if e == nil {
		m.AssetID = saved
		return m, nil
	}
	a, e := s.ReserveAsset(ctx, AssetRequest{Operation: OperationRequest{Name: "source-upload", Key: uuid.NewString(), Path: "/sources/upload", Body: sourceBytes(map[string]any{"name": name, "sha": digest, "size": n})}, SHA: digest, Size: n, Purpose: "source_component", MIME: "application/octet-stream"})
	if e != nil {
		return m, e
	}
	if _, e = f.Seek(0, 0); e != nil {
		return m, e
	}
	conn, release, e := s.lockAsset(ctx, a.ID)
	if e != nil {
		return m, e
	}
	defer func() { release() }()
	if e = s.writeAssetObject(ctx, conn, a, f); e != nil {
		return m, e
	}
	tx, e := beginWriteOn(ctx, conn)
	if e != nil {
		return m, e
	}
	defer tx.Rollback(context.Background())
	if e = setAssetState(ctx, tx, a, "bytes_verified"); e != nil {
		return m, e
	}
	if e = tx.Commit(ctx); e != nil {
		return m, e
	}
	release()
	release = func() {}
	a, e = s.LinkAsset(ctx, a.ID, nil)
	if e != nil {
		return m, e
	}
	m.AssetID = a.ID
	_, e = s.DB.Exec(ctx, "INSERT INTO source_file(id,relative_path,sha256,byte_count,asset_id,media_metadata) VALUES($1,$2,$3,$4,$5,$6) ON CONFLICT(relative_path,sha256,byte_count) DO NOTHING", uuid.NewString(), name, digest, n, a.ID, nullableJSON(m.Media))
	return m, e
}
func (s *Storage) IntakeArchive(ctx context.Context, name, kind string, r io.Reader) ([]source.Member, error) {
	files := []source.Member{}
	var total int64
	var scan func(string, string, string, io.Reader, int) error
	scan = func(name, kind, prefix string, reader io.Reader, depth int) error {
		if depth > 8 {
			return source.Failure(name, "intake_limit", "Nested archive depth exceeds8; no truncation")
		}
		f, e := os.CreateTemp("", "tangerine-intake-")
		if e != nil {
			return e
		}
		defer os.Remove(f.Name())
		defer f.Close()
		if n, e := io.Copy(f, io.LimitReader(reader, source.DefaultLimits.Bytes-total+1)); e != nil || n > source.DefaultLimits.Bytes-total {
			if e != nil {
				return e
			}
			return source.Failure(name, "intake_limit", "Complete archive expansion exceeds configured capacity")
		}
		e = source.InspectArchive(ctx, f, kind, source.DefaultLimits, func(entry source.Entry) error {
			if len(files) >= source.DefaultLimits.Files || entry.Size > source.DefaultLimits.Bytes-total {
				return source.Failure(entry.Name, "intake_limit", "Complete expansion exceeds configured capacity")
			}
			logical := path.Join(prefix, entry.Name)
			r, e := entry.Open()
			if e != nil {
				return e
			}
			defer r.Close()
			if childKind := sourceKind(logical); childKind != "" {
				return scan(logical, childKind, logical, r, depth+1)
			}
			m, e := s.saveSourceStream(ctx, logical, r)
			if e != nil {
				return e
			}
			files = append(files, m)
			total += m.Bytes
			return nil
		})
		if e != nil {
			return e
		}
		if _, e = f.Seek(0, 0); e != nil {
			return e
		}
		raw, e := s.saveSourceStream(ctx, name, f)
		if e != nil {
			return e
		}
		raw.Component = "archive"
		files = append(files, raw)
		total += raw.Bytes
		return nil
	}
	e := scan(name, kind, "", r, 0)
	return files, e
}

func (s *Storage) sourceFileReader(ctx context.Context, releaseID, name string) (io.ReadCloser, error) {
	var key string
	e := s.DB.QueryRow(ctx, "SELECT a.storage_key FROM source_member m JOIN source_file f ON f.id=m.file_id JOIN asset_location a ON a.asset_id=f.asset_id WHERE m.release_id=$1 AND m.relative_path=$2", releaseID, name).Scan(&key)
	if e != nil {
		return nil, e
	}
	return s.Media.GetObject(ctx, s.Bucket, key, minio.GetObjectOptions{})
}
func (s *Storage) sourceMembers(ctx context.Context, release string) ([]source.Member, error) {
	rows, e := s.DB.Query(ctx, "SELECT m.relative_path,f.sha256,f.byte_count,m.component,m.partition,f.asset_id,f.media_metadata FROM source_member m JOIN source_file f ON f.id=m.file_id WHERE m.release_id=$1 ORDER BY m.relative_path COLLATE \"C\"", release)
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	out := []source.Member{}
	for rows.Next() {
		var m source.Member
		var media []byte
		if e = rows.Scan(&m.Path, &m.SHA, &m.Bytes, &m.Component, &m.Partition, &m.AssetID, &media); e != nil {
			return nil, e
		}
		if len(media) > 0 {
			_ = json.Unmarshal(media, &m.Media)
		}
		out = append(out, m)
	}
	return out, rows.Err()
}
func sourceNumber(n int64) string { return strconv.FormatInt(n, 10) }
func sourceScope(s string) bool {
	return s == "full_named_release" || s == "partial_export" || s == "analysis_companion" || s == "mirror"
}
func sourceKind(name string) string {
	n := strings.ToLower(name)
	switch {
	case strings.HasSuffix(n, ".tar.gz"), strings.HasSuffix(n, ".tgz"):
		return "tar.gz"
	case strings.HasSuffix(n, ".tar"):
		return "tar"
	case strings.HasSuffix(n, ".zip"):
		return "zip"
	}
	return ""
}
func sourceError(e error) string {
	if e == nil {
		return ""
	}
	if i, ok := e.(source.Issue); ok {
		return i.Code
	}
	return fmt.Sprintf("source_unavailable")
}
