// Package recovery owns the portable snapshot encoding and one-time intake.
// Accepted files are passed directly to restore; saved state is never re-audited.
package recovery

import (
	"archive/tar"
	"compress/gzip"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path"
	"path/filepath"
	"strings"
	"time"
)

type File struct {
	Path  string `json:"path"`
	SHA   string `json:"sha256"`
	Bytes int64  `json:"bytes"`
}
type Manifest struct {
	Format     int      `json:"format"`
	ID         string   `json:"id"`
	Created    string   `json:"created_at"`
	Migrations []string `json:"migrations"`
	Files      []File   `json:"files"`
	Secrets    bool     `json:"secrets_included"`
	Models     bool     `json:"models_included"`
	Lab        bool     `json:"lab_included"`
}
type Writer struct {
	gzip     *gzip.Writer
	tar      *tar.Writer
	Manifest Manifest
	paths    map[string]bool
}

func New(w io.Writer, id string, migrations []string) *Writer {
	g := gzip.NewWriter(w)
	return &Writer{gzip: g, tar: tar.NewWriter(g), paths: map[string]bool{}, Manifest: Manifest{Format: 2, ID: id, Created: time.Now().UTC().Format(time.RFC3339Nano), Migrations: migrations, Files: []File{}}}
}
func safe(name string) bool {
	return name != "" && name == path.Clean(name) && !strings.Contains(name, "\\") && !strings.HasPrefix(name, "/") && name != ".." && !strings.HasPrefix(name, "../") && !strings.ContainsRune(name, 0)
}
func allowed(name string) bool {
	return name == "database.dump" || strings.HasPrefix(name, "media/") || strings.HasPrefix(name, "models/") || strings.HasPrefix(name, "lab/")
}
func (w *Writer) Add(name string, size int64, r io.Reader) error {
	if !safe(name) || !allowed(name) || size < 0 || w.paths[name] {
		return errors.New("SNAPSHOT_INVALID: file path or duplicate")
	}
	w.paths[name] = true
	if err := w.tar.WriteHeader(&tar.Header{Name: name, Mode: 0600, Size: size, Typeflag: tar.TypeReg}); err != nil {
		return err
	}
	h := sha256.New()
	n, err := io.CopyN(io.MultiWriter(w.tar, h), r, size)
	if err != nil {
		return err
	}
	w.Manifest.Files = append(w.Manifest.Files, File{name, hex.EncodeToString(h.Sum(nil)), n})
	return nil
}
func (w *Writer) Close() error {
	b, err := json.Marshal(w.Manifest)
	if err != nil {
		return err
	}
	if !w.paths["database.dump"] {
		return errors.New("SNAPSHOT_INVALID: database absent")
	}
	if err = w.tar.WriteHeader(&tar.Header{Name: "manifest.json", Mode: 0600, Size: int64(len(b)), Typeflag: tar.TypeReg}); err != nil {
		return err
	}
	if _, err = w.tar.Write(b); err != nil {
		return err
	}
	if err = w.tar.Close(); err != nil {
		return err
	}
	return w.gzip.Close()
}

// Admit consumes an external archive once into a new private staging directory.
// No old workspace or destination volume is accessed by this codec.
func Admit(r io.Reader, directory string, supported []string) (Manifest, error) {
	var m Manifest
	g, err := gzip.NewReader(r)
	if err != nil {
		return m, fmt.Errorf("BACKUP_INVALID: %w", err)
	}
	defer g.Close()
	tr := tar.NewReader(g)
	seen := map[string]File{}
	found := false
	for {
		h, e := tr.Next()
		if e == io.EOF {
			break
		}
		if e != nil {
			return m, fmt.Errorf("BACKUP_INVALID: %w", e)
		}
		if h.Typeflag != tar.TypeReg || !safe(h.Name) || (h.Name != "manifest.json" && !allowed(h.Name)) || h.Size < 0 || found {
			return m, errors.New("BACKUP_INVALID: unsafe or trailing archive entry")
		}
		if h.Name == "manifest.json" {
			b, e := io.ReadAll(tr)
			if e != nil {
				return m, e
			}
			if e = json.Unmarshal(b, &m); e != nil {
				return m, e
			}
			found = true
			continue
		}
		if _, ok := seen[h.Name]; ok {
			return m, errors.New("BACKUP_INVALID: duplicate entry")
		}
		target := filepath.Join(directory, filepath.FromSlash(h.Name))
		if e = os.MkdirAll(filepath.Dir(target), 0700); e != nil {
			return m, e
		}
		f, e := os.OpenFile(target, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
		if e != nil {
			return m, e
		}
		digest := sha256.New()
		n, e := io.Copy(io.MultiWriter(f, digest), tr)
		ce := f.Close()
		if e != nil {
			return m, e
		}
		if ce != nil {
			return m, ce
		}
		seen[h.Name] = File{h.Name, hex.EncodeToString(digest.Sum(nil)), n}
	}
	// Consume the gzip trailer as part of this single external-input admission.
	if _, err = io.Copy(io.Discard, g); err != nil {
		return m, fmt.Errorf("BACKUP_INVALID: %w", err)
	}
	if !found || m.Format != 2 || m.Secrets || len(m.Files) != len(seen) || len(m.Migrations) == 0 || len(m.Migrations) > len(supported) {
		return m, errors.New("BACKUP_INCOMPATIBLE: incomplete or unsupported snapshot")
	}
	if _, ok := seen["database.dump"]; !ok {
		return m, errors.New("BACKUP_INVALID: database absent")
	}
	for i, v := range m.Migrations {
		if v != supported[i] {
			return m, errors.New("BACKUP_INCOMPATIBLE: unsupported migration sequence")
		}
	}
	declared := map[string]bool{}
	for _, f := range m.Files {
		if declared[f.Path] || seen[f.Path] != f {
			return m, errors.New("BACKUP_INVALID: file hash or inventory mismatch")
		}
		declared[f.Path] = true
	}
	return m, nil
}
