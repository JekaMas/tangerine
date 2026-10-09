package app

import (
	"bufio"
	"crypto/rand"
	"encoding/hex"
	"errors"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

var operatorKeys = map[string]bool{"DEEPSEEK_API_KEY": true, "OPENAI_API_KEY": true, "AZURE_SPEECH_KEY": true, "AZURE_SPEECH_REGION": true, "ELEVENLABS_API_KEY": true}
var runtimeKeys = []string{"POSTGRES_PASSWORD", "MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD", "API_INTERNAL_TOKEN", "SPEECH_INTERNAL_TOKEN"}

// ConfigureLocal validates operator input, then creates durable internal credentials.
// Existing credentials are never regenerated: losing the file is a restore problem.
func ConfigureLocal(operatorFile, directory string) error {
	input, err := os.Open(operatorFile)
	if err != nil {
		return errors.New("CONFIG_INVALID: cannot read .env")
	}
	defer input.Close()
	seen := map[string]bool{}
	scanner := bufio.NewScanner(input)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		key, value, ok := strings.Cut(line, "=")
		if !ok || !operatorKeys[key] || seen[key] || strings.ContainsAny(value, "\r\x00$`\\\"' ") {
			return errors.New("CONFIG_INVALID: use unique supported KEY=value entries without shell expansion or quoting")
		}
		seen[key] = true
	}
	if scanner.Err() != nil {
		return errors.New("CONFIG_INVALID: unreadable .env")
	}
	if directory == "" {
		return errors.New("CONFIG_INVALID: runtime directory missing")
	}
	if err = os.MkdirAll(directory, 0700); err != nil {
		return errors.New("CONFIG_WRITE_FAILED: cannot create runtime directory")
	}
	if err = os.Chmod(directory, 0700); err != nil {
		return errors.New("CONFIG_WRITE_FAILED: cannot protect runtime directory")
	}
	destination := filepath.Join(directory, "runtime.env")
	if existing, err := os.ReadFile(destination); err == nil {
		values := map[string]string{}
		for _, line := range strings.Split(string(existing), "\n") {
			key, value, ok := strings.Cut(line, "=")
			if ok {
				values[key] = value
			}
		}
		for _, key := range runtimeKeys {
			value := values[key]
			decoded, e := hex.DecodeString(value)
			if e != nil || len(decoded) != 32 {
				return errors.New("CONFIG_DAMAGED: restore data/config/runtime.env; do not regenerate credentials for existing volumes")
			}
		}
		return os.Chmod(destination, 0600)
	} else if !os.IsNotExist(err) {
		return errors.New("CONFIG_READ_FAILED: cannot read durable credentials")
	}
	keys := append([]string(nil), runtimeKeys...)
	sort.Strings(keys)
	var content strings.Builder
	for _, key := range keys {
		var bytes [32]byte
		if _, err := rand.Read(bytes[:]); err != nil {
			return errors.New("CONFIG_WRITE_FAILED: random source unavailable")
		}
		content.WriteString(key + "=" + hex.EncodeToString(bytes[:]) + "\n")
	}
	temporary, err := os.CreateTemp(directory, ".runtime-*")
	if err != nil {
		return errors.New("CONFIG_WRITE_FAILED: cannot create credentials")
	}
	name := temporary.Name()
	defer os.Remove(name)
	if _, err = temporary.WriteString(content.String()); err == nil {
		err = temporary.Sync()
	}
	closeErr := temporary.Close()
	if err != nil || closeErr != nil {
		return errors.New("CONFIG_WRITE_FAILED: cannot save credentials")
	}
	// Link is exclusive and atomic even if two launchers configure concurrently.
	if err = os.Link(name, destination); os.IsExist(err) {
		return ConfigureLocal(operatorFile, directory)
	}
	if err != nil {
		return errors.New("CONFIG_WRITE_FAILED: cannot publish credentials")
	}
	return nil
}

func Redact(input io.Reader, output io.Writer) error {
	var secrets []string
	for _, entry := range os.Environ() {
		key, value, _ := strings.Cut(entry, "=")
		if len(value) > 3 && (strings.Contains(key, "KEY") || strings.Contains(key, "TOKEN") || strings.Contains(key, "PASSWORD") || key == "DATABASE_URL" || key == "MINIO_ROOT_USER") {
			secrets = append(secrets, value)
		}
	}
	sort.Slice(secrets, func(i, j int) bool { return len(secrets[i]) > len(secrets[j]) })
	scanner := bufio.NewScanner(input)
	scanner.Buffer(make([]byte, 4096), 1024*1024)
	for scanner.Scan() {
		line := scanner.Text()
		for _, secret := range secrets {
			line = strings.ReplaceAll(line, secret, "[redacted]")
		}
		if _, err := io.WriteString(output, line+"\n"); err != nil {
			return err
		}
	}
	return scanner.Err()
}
