package app

import (
	"bytes"
	"context"
	"errors"
	"io"
	"strings"
	"tangerine.local/api/internal/source"
	"testing"
)

type sourceNoRead struct{}

func (sourceNoRead) Read([]byte) (int, error) {
	return 0, errors.New("accepted bytes must not be read again")
}

func TestNativeSourceAdmittedReusePositive(t *testing.T) {
	f := sourceFixture(t)
	first := f.upload(t, "original/README.md", "official inert document")
	again, e := f.s.Store.saveAdmittedSource(context.Background(), first, sourceNoRead{})
	sourceRequire(t, e)
	sourceAssert(t, first.AssetID, again.AssetID)
	sourceAssert(t, first.SHA, again.SHA)
	var count int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_file WHERE relative_path=$1", first.Path).Scan(&count))
	sourceAssert(t, 1, count)
	// Ordinary untrusted admission remains the one hashing owner.
	untrusted, e := f.s.Store.saveSourceStream(context.Background(), "original/second.txt", strings.NewReader("new input"))
	sourceRequire(t, e)
	sourceAssert(t, "3e7ef6bcdf24c03ba46c0e0511c2bcbacaddfd2ff4b843cf23e5af119a8a5981", untrusted.SHA)
}
func TestNativeSourceAdmittedFailureNegative(t *testing.T) {
	f := sourceFixture(t)
	m := source.NewMember("original/interrupted.txt")
	m.SHA = strings.Repeat("a", 64)
	m.Bytes = 100
	if _, e := f.s.Store.saveAdmittedSource(context.Background(), m, bytes.NewReader([]byte("short"))); e == nil {
		t.Fatal("incomplete storage write linked")
	}
	var count int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_file WHERE relative_path=$1", m.Path).Scan(&count))
	sourceAssert(t, 0, count)
	if _, e := f.s.Store.saveSourceStream(context.Background(), "../outside", io.LimitReader(strings.NewReader("x"), 1)); e == nil {
		t.Fatal("unsafe ordinary path admitted")
	}
}
