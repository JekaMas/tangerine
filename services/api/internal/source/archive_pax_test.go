package source

import (
	"archive/tar"
	"context"
	"io"
	"os"
	"testing"
)

func paxFixture(t *testing.T, link bool) *os.File {
	t.Helper()
	f, err := os.CreateTemp(t.TempDir(), "pax-*.tar")
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = f.Close() })
	w := tar.NewWriter(f)
	if err = w.WriteHeader(&tar.Header{Name: "pax_global_header", Typeflag: tar.TypeXGlobalHeader, Format: tar.FormatPAX, PAXRecords: map[string]string{"comment": "source commit metadata, retained in the original archive"}}); err != nil {
		t.Fatal(err)
	}
	if err = w.WriteHeader(&tar.Header{Name: "source/text", Mode: 0600, Typeflag: tar.TypeReg, Size: 12}); err != nil {
		t.Fatal(err)
	}
	if _, err = io.WriteString(w, "native text\n"); err != nil {
		t.Fatal(err)
	}
	if link {
		if err = w.WriteHeader(&tar.Header{Name: "source/link", Typeflag: tar.TypeSymlink, Linkname: "../outside"}); err != nil {
			t.Fatal(err)
		}
	}
	if err = w.Close(); err != nil {
		t.Fatal(err)
	}
	return f
}

func TestSourceArchivePAXPositive(t *testing.T) {
	names := []string{}
	err := InspectArchive(context.Background(), paxFixture(t, false), "tar", DefaultLimits, func(entry Entry) error {
		reader, err := entry.Open()
		if err != nil {
			return err
		}
		defer reader.Close()
		value, err := io.ReadAll(reader)
		if err != nil {
			return err
		}
		equal(t, "native text\n", string(value))
		names = append(names, entry.Name)
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	equal(t, []string{"source/text"}, names)
}

func TestSourceArchivePAXNegative(t *testing.T) {
	accepted := 0
	err := InspectArchive(context.Background(), paxFixture(t, true), "tar", DefaultLimits, func(Entry) error { accepted++; return nil })
	if err == nil || accepted != 0 {
		t.Fatal("PAX metadata allowed a link or partially accepted an unsafe archive", err, accepted)
	}
}
