package app

import (
	"fmt"
	"github.com/google/uuid"
	"os"
	"path/filepath"
	"strings"
)

func (s *Server) saveSourceCredential(id, value string) (string, error) {
	dir := s.Providers.Dir
	if dir == "" {
		return "", fmt.Errorf("source secret store unavailable")
	}
	if e := os.MkdirAll(dir, 0700); e != nil {
		return "", e
	}
	f, e := os.CreateTemp(dir, ".source-")
	if e != nil {
		return "", e
	}
	defer os.Remove(f.Name())
	if e = f.Chmod(0600); e != nil {
		f.Close()
		return "", e
	}
	if _, e = f.WriteString(value); e != nil {
		f.Close()
		return "", e
	}
	if e = f.Close(); e != nil {
		return "", e
	}
	version := uuid.NewString()
	ref := "source:" + id + ":" + version
	if e = os.Rename(f.Name(), filepath.Join(dir, "source-"+id+"-"+version)); e != nil {
		return "", e
	}
	return ref, nil
}

func sourceCredentialName(id, ref string) (string, error) {
	if ref == "source:"+id {
		return "source-" + id, nil
	}
	v, ok := strings.CutPrefix(ref, "source:"+id+":")
	if !ok {
		return "", ErrReference
	}
	if _, e := uuid.Parse(v); e != nil {
		return "", ErrReference
	}
	return "source-" + id + "-" + v, nil
}
