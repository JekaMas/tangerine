package app

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"
)

func TestConfigureCreatesAndPreservesDurableCredentials(t *testing.T) {
	dir := t.TempDir()
	operator := filepath.Join(dir, ".env")
	runtime := filepath.Join(dir, "config")
	if err := os.WriteFile(operator, []byte("OPENAI_API_KEY=\n"), 0600); err != nil {
		t.Fatal(err)
	}
	if err := ConfigureLocal(operator, runtime); err != nil {
		t.Fatal(err)
	}
	first, err := os.ReadFile(filepath.Join(runtime, "runtime.env"))
	if err != nil {
		t.Fatal(err)
	}
	if err := ConfigureLocal(operator, runtime); err != nil {
		t.Fatal(err)
	}
	second, _ := os.ReadFile(filepath.Join(runtime, "runtime.env"))
	if !bytes.Equal(first, second) {
		t.Fatal("credentials rotated")
	}
	info, _ := os.Stat(filepath.Join(runtime, "runtime.env"))
	if info.Mode().Perm() != 0600 {
		t.Fatal("credentials permissions")
	}
}
func TestConfigureRejectsBadInputAndDamagedCredentials(t *testing.T) {
	dir := t.TempDir()
	operator := filepath.Join(dir, ".env")
	runtime := filepath.Join(dir, "config")
	for _, input := range []string{"UNKNOWN=value", "OPENAI_API_KEY=x\nOPENAI_API_KEY=y", "OPENAI_API_KEY=$TOKEN"} {
		os.WriteFile(operator, []byte(input), 0600)
		if ConfigureLocal(operator, runtime) == nil {
			t.Fatal("invalid config accepted")
		}
	}
	os.WriteFile(operator, []byte(""), 0600)
	os.MkdirAll(runtime, 0700)
	os.WriteFile(filepath.Join(runtime, "runtime.env"), []byte("damaged"), 0600)
	if ConfigureLocal(operator, runtime) == nil {
		t.Fatal("damaged credentials regenerated")
	}
}
func TestRedactionUsesActualSecrets(t *testing.T) {
	t.Setenv("OPENAI_API_KEY", "controlled-secret-never-print")
	t.Setenv("MINIO_ROOT_USER", "controlled-private-media-user")
	var out bytes.Buffer
	if err := Redact(bytes.NewBufferString("safe controlled-secret-never-print controlled-private-media-user line\n"), &out); err != nil {
		t.Fatal(err)
	}
	if out.String() != "safe [redacted] [redacted] line\n" {
		t.Fatal("redaction failed")
	}
}
