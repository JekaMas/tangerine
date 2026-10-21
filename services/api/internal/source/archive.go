package source

import (
	"archive/tar"
	"archive/zip"
	"compress/gzip"
	"context"
	"fmt"
	"io"
	"os"
	"sort"
	"strings"
)

// Resource limits are operator configuration, not silent truncation. Every failure
// leaves the original upload inert; no partial archive is reported complete.
type Limits struct {
	Files       int
	Bytes       int64
	MemberBytes int64
}

var DefaultLimits = Limits{Files: 1000000, Bytes: 1 << 40, MemberBytes: 1 << 39}

type Entry struct {
	Name string
	Size int64
	Open func() (io.ReadCloser, error)
}

func InspectArchive(ctx context.Context, f *os.File, kind string, limits Limits, accept func(Entry) error) error {
	info, e := f.Stat()
	if e != nil {
		return e
	}
	if limits.Files <= 0 || limits.Bytes <= 0 || limits.MemberBytes <= 0 {
		return fmt.Errorf("invalid intake limits")
	}
	entries := []Entry{}
	seen := map[string]bool{}
	var total int64
	add := func(name string, size int64, ordinary bool, open func() (io.ReadCloser, error)) error {
		if e := ctx.Err(); e != nil {
			return e
		}
		n, e := SafePath(name)
		if e != nil {
			return e
		}
		if !ordinary {
			return Failure(name, "unsafe_member", "Links, devices and special files are not accepted")
		}
		if seen[n] {
			return Failure(n, "duplicate_path", "Normalized archive path is duplicated")
		}
		seen[n] = true
		if size < 0 || size > limits.MemberBytes || size > limits.Bytes-total || len(entries) >= limits.Files {
			return Failure(n, "intake_limit", "Configured complete-intake capacity exceeded; no truncation")
		}
		total += size
		entries = append(entries, Entry{n, size, open})
		return nil
	}
	switch kind {
	case "zip":
		z, e := zip.NewReader(f, info.Size())
		if e != nil {
			return e
		}
		for _, m := range z.File {
			if m.FileInfo().IsDir() {
				if _, e := SafePath(strings.TrimSuffix(m.Name, "/")); e != nil {
					return e
				}
				continue
			}
			m := m
			if e = add(m.Name, int64(m.UncompressedSize64), m.Mode().IsRegular(), m.Open); e != nil {
				return e
			}
		}
	case "tar", "tar.gz", "tgz":
		// Tar entries are spooled privately so validation of the entire member list
		// precedes acceptance. Removing this temp tree never touches source paths.
		dir, e := os.MkdirTemp("", "tangerine-source-tar-")
		if e != nil {
			return e
		}
		defer os.RemoveAll(dir)
		var reader io.Reader = io.NewSectionReader(f, 0, info.Size())
		if kind != "tar" {
			gz, e := gzip.NewReader(reader)
			if e != nil {
				return e
			}
			defer gz.Close()
			reader = gz
		}
		t := tar.NewReader(reader)
		for {
			h, e := t.Next()
			if e == io.EOF {
				break
			}
			if e != nil {
				return e
			}
			if h.Typeflag == tar.TypeDir {
				if _, e = SafePath(strings.TrimSuffix(h.Name, "/")); e != nil {
					return e
				}
				continue
			}
			tmp := fmt.Sprintf("%s/%d", dir, len(entries))
			if e = add(h.Name, h.Size, h.Typeflag == tar.TypeReg || h.Typeflag == tar.TypeRegA, func() (io.ReadCloser, error) { return os.Open(tmp) }); e != nil {
				return e
			}
			out, e := os.OpenFile(tmp, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0600)
			if e != nil {
				return e
			}
			n, e := io.Copy(out, t)
			ce := out.Close()
			if e != nil {
				return e
			}
			if ce != nil {
				return ce
			}
			if n != h.Size {
				return io.ErrUnexpectedEOF
			}
		}
	default:
		return Failure(kind, "archive_format", "Use ZIP, TAR or TAR.GZ, or upload every directory file")
	}
	sort.Slice(entries, func(i, j int) bool { return entries[i].Name < entries[j].Name })
	for _, v := range entries {
		if e := ctx.Err(); e != nil {
			return e
		}
		if e := accept(v); e != nil {
			return e
		}
	}
	return nil
}
