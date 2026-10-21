package recovery

import (
	"archive/tar"
	"bytes"
	"compress/gzip"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func archiveFixture(t *testing.T) []byte {
	t.Helper()
	var b bytes.Buffer
	w := New(&b, "literal-backup", []string{"001.sql", "002.sql"})
	for name, body := range map[string]string{"database.dump": "literal database bytes", "media/frozen-audio": "\x00\x01\xffexact audio", "models/voices/voice.bin": "installed voice", "lab/mlflow.db": "constructed SQLite transport bytes"} {
		if e := w.Add(name, int64(len(body)), strings.NewReader(body)); e != nil {
			t.Fatal(e)
		}
	}
	w.Manifest.Models = true
	w.Manifest.Lab = true
	if e := w.Close(); e != nil {
		t.Fatal(e)
	}
	return b.Bytes()
}
func TestRecoveryArchivePositive(t *testing.T) {
	dir := t.TempDir()
	m, e := Admit(bytes.NewReader(archiveFixture(t)), dir, []string{"001.sql", "002.sql", "003.sql"})
	if e != nil {
		t.Fatal(e)
	}
	if m.ID != "literal-backup" || len(m.Files) != 4 || m.Secrets || !m.Models || !m.Lab {
		t.Fatal(m)
	}
	b, e := os.ReadFile(filepath.Join(dir, "media/frozen-audio"))
	if e != nil || string(b) != "\x00\x01\xffexact audio" {
		t.Fatal(string(b), e)
	}
}
func TestRecoveryOlderSchemaPositive(t *testing.T) {
	_, e := Admit(bytes.NewReader(archiveFixture(t)), t.TempDir(), []string{"001.sql", "002.sql", "003.sql"})
	if e != nil {
		t.Fatal(e)
	}
}
func badArchive(t *testing.T, name string, kind byte, manifest bool) []byte {
	t.Helper()
	var b bytes.Buffer
	g := gzip.NewWriter(&b)
	w := tar.NewWriter(g)
	_ = w.WriteHeader(&tar.Header{Name: name, Typeflag: kind, Mode: 0600, Size: 1, Linkname: "/outside"})
	_, _ = w.Write([]byte("x"))
	if manifest {
		raw, _ := json.Marshal(Manifest{Format: 2, ID: "bad", Migrations: []string{"001.sql"}, Files: []File{{Path: name, SHA: strings.Repeat("0", 64), Bytes: 1}}})
		_ = w.WriteHeader(&tar.Header{Name: "manifest.json", Typeflag: tar.TypeReg, Mode: 0600, Size: int64(len(raw))})
		_, _ = w.Write(raw)
	}
	_ = w.Close()
	_ = g.Close()
	return b.Bytes()
}
func TestRecoveryUnsafePathNegative(t *testing.T) {
	for _, name := range []string{"../outside", "/outside", "media/../../outside", "models\\outside", "credentials/private.key"} {
		t.Run(strings.ReplaceAll(name, "/", "_"), func(t *testing.T) {
			if _, e := Admit(bytes.NewReader(badArchive(t, name, tar.TypeReg, true)), t.TempDir(), []string{"001.sql"}); e == nil {
				t.Fatal("unsafe archive admitted", name)
			}
		})
	}
}
func TestRecoveryLinkNegative(t *testing.T) {
	if _, e := Admit(bytes.NewReader(badArchive(t, "media/link", tar.TypeSymlink, false)), t.TempDir(), []string{"001.sql"}); e == nil {
		t.Fatal("link admitted")
	}
}
func TestRecoveryTamperNegative(t *testing.T) {
	if _, e := Admit(bytes.NewReader(badArchive(t, "database.dump", tar.TypeReg, true)), t.TempDir(), []string{"001.sql"}); e == nil || !strings.Contains(e.Error(), "hash") {
		t.Fatal(e)
	}
}
func TestRecoveryFutureSchemaNegative(t *testing.T) {
	if _, e := Admit(bytes.NewReader(archiveFixture(t)), t.TempDir(), []string{"001.sql"}); e == nil || !strings.Contains(e.Error(), "INCOMPATIBLE") {
		t.Fatal(e)
	}
}
func TestRecoveryIncompleteNegative(t *testing.T) {
	data := archiveFixture(t)
	for _, n := range []int{0, len(data) / 2, len(data) - 5} {
		if _, e := Admit(bytes.NewReader(data[:n]), t.TempDir(), []string{"001.sql", "002.sql"}); e == nil {
			t.Fatal("truncated archive admitted", n)
		}
	}
}
func TestRecoveryDuplicateNegative(t *testing.T) {
	var b bytes.Buffer
	w := New(&b, "duplicate", []string{"001.sql"})
	if e := w.Add("database.dump", 1, strings.NewReader("x")); e != nil {
		t.Fatal(e)
	}
	if e := w.Add("database.dump", 1, strings.NewReader("y")); e == nil {
		t.Fatal("duplicate overwritten")
	}
}
func TestRecoveryDestinationNegative(t *testing.T) {
	dir := t.TempDir()
	if e := os.WriteFile(filepath.Join(dir, "database.dump"), []byte("previous"), 0600); e != nil {
		t.Fatal(e)
	}
	if _, e := Admit(bytes.NewReader(archiveFixture(t)), dir, []string{"001.sql", "002.sql"}); e == nil {
		t.Fatal("existing file replaced")
	}
	b, _ := os.ReadFile(filepath.Join(dir, "database.dump"))
	if string(b) != "previous" {
		t.Fatal(string(b))
	}
}
