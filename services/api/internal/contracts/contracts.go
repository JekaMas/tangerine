// Package contracts owns the exact saved contract registry and RFC 8785 encoding.
package contracts

import (
	"bytes"
	"crypto/sha256"
	"embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math"
	"strconv"
	"strings"
	"sync"
	"unicode/utf8"

	"github.com/cyberphone/json-canonicalization/go/src/webpki.org/jsoncanonicalizer"
	"github.com/santhosh-tekuri/jsonschema/v6"
)

//go:embed schemas/*.json
var Files embed.FS

type Contract struct {
	Kind, Version, SHA string
	Bytes              []byte
	Schema             *jsonschema.Schema
}

var once sync.Once
var registry map[string]Contract
var registryErr error

func Registry() (map[string]Contract, error) {
	once.Do(func() {
		registry = map[string]Contract{}
		compiler := jsonschema.NewCompiler()
		compiler.AssertFormat()
		entries, err := Files.ReadDir("schemas")
		if err != nil {
			registryErr = err
			return
		}
		for _, e := range entries {
			b, err := Files.ReadFile("schemas/" + e.Name())
			if err != nil {
				registryErr = err
				return
			}
			v, err := jsonschema.UnmarshalJSON(bytes.NewReader(b))
			if err != nil {
				registryErr = err
				return
			}
			if err = compiler.AddResource("https://tangerine.invalid/schemas/"+e.Name(), v); err != nil {
				registryErr = err
				return
			}
		}
		for _, e := range entries {
			b, _ := Files.ReadFile("schemas/" + e.Name())
			var v map[string]any
			_ = json.Unmarshal(b, &v)
			version := "2.0.0"
			if p, ok := v["properties"].(map[string]any); ok {
				if s, ok := p["schema_version"].(map[string]any); ok {
					if c, ok := s["const"].(string); ok {
						version = c
					}
				}
			}
			s, err := compiler.Compile("https://tangerine.invalid/schemas/" + e.Name())
			if err != nil {
				registryErr = fmt.Errorf("compile %s: %w", e.Name(), err)
				return
			}
			kind := strings.TrimSuffix(e.Name(), ".schema.json")
			registry[kind] = Contract{kind, version, Digest(b), b, s}
		}
	})
	return registry, registryErr
}
func Digest(b []byte) string { h := sha256.Sum256(b); return hex.EncodeToString(h[:]) }
func Validate(kind, version string, raw []byte) (Contract, []byte, error) {
	r, err := Registry()
	if err != nil {
		return Contract{}, nil, err
	}
	c, ok := r[kind]
	if !ok || c.Version != version {
		return c, nil, errors.New("unknown contract version")
	}
	b, err := Canonical(raw)
	if err != nil {
		return c, nil, err
	}
	v, err := jsonschema.UnmarshalJSON(bytes.NewReader(b))
	if err != nil {
		return c, nil, err
	}
	if err = c.Schema.Validate(v); err != nil {
		return c, nil, fmt.Errorf("invalid %s document: %w", kind, err)
	}
	if err = verifyOwnedDigest(kind, b); err != nil {
		return c, nil, err
	}
	return c, b, nil
}

// Canonical rejects ambiguous JSON before JCS. It preserves all Unicode code points.
func Canonical(raw []byte) ([]byte, error) {
	if !utf8.Valid(raw) {
		return nil, errors.New("invalid UTF-8")
	}
	if err := checkSurrogates(raw); err != nil {
		return nil, err
	}
	d := json.NewDecoder(bytes.NewReader(raw))
	d.UseNumber()
	if err := readValue(d); err != nil {
		return nil, err
	}
	if _, err := d.Token(); err != io.EOF {
		return nil, errors.New("trailing JSON")
	}
	return jsoncanonicalizer.Transform(raw)
}
func readValue(d *json.Decoder) error {
	t, err := d.Token()
	if err != nil {
		return err
	}
	if n, ok := t.(json.Number); ok {
		f, err := strconv.ParseFloat(string(n), 64)
		if err != nil || math.IsNaN(f) || math.IsInf(f, 0) || (math.Trunc(f) == f && math.Abs(f) > 9007199254740991) {
			return errors.New("nonfinite or unsafe JSON number")
		}
		return nil
	}
	if delim, ok := t.(json.Delim); ok {
		switch delim {
		case '{':
			seen := map[string]bool{}
			for d.More() {
				k, err := d.Token()
				if err != nil {
					return err
				}
				s, ok := k.(string)
				if !ok || seen[s] {
					return errors.New("duplicate object key")
				}
				seen[s] = true
				if err = readValue(d); err != nil {
					return err
				}
			}
			end, err := d.Token()
			if err != nil || end != json.Delim('}') {
				return errors.New("invalid object")
			}
		case '[':
			for d.More() {
				if err = readValue(d); err != nil {
					return err
				}
			}
			end, err := d.Token()
			if err != nil || end != json.Delim(']') {
				return errors.New("invalid array")
			}
		default:
			return errors.New("invalid delimiter")
		}
	}
	return nil
}
func checkSurrogates(b []byte) error {
	in := false
	for i := 0; i < len(b); i++ {
		if b[i] == '"' {
			in = !in
			continue
		}
		if !in || b[i] != '\\' {
			continue
		}
		i++
		if i >= len(b) {
			return errors.New("invalid escape")
		}
		if b[i] != 'u' {
			continue
		}
		if i+4 >= len(b) {
			return errors.New("invalid unicode escape")
		}
		v, err := strconv.ParseUint(string(b[i+1:i+5]), 16, 16)
		if err != nil {
			return err
		}
		i += 4
		if v >= 0xdc00 && v <= 0xdfff {
			return errors.New("unpaired low surrogate")
		}
		if v >= 0xd800 && v <= 0xdbff {
			if i+6 >= len(b) || b[i+1] != '\\' || b[i+2] != 'u' {
				return errors.New("unpaired high surrogate")
			}
			w, err := strconv.ParseUint(string(b[i+3:i+7]), 16, 16)
			if err != nil || w < 0xdc00 || w > 0xdfff {
				return errors.New("unpaired high surrogate")
			}
			i += 6
		}
	}
	return nil
}

// Pointer reads an RFC 6901 path; IDs and digests are validated against actual values.
func Pointer(raw []byte, path string) (any, error) {
	var v any
	d := json.NewDecoder(bytes.NewReader(raw))
	d.UseNumber()
	if err := d.Decode(&v); err != nil {
		return nil, err
	}
	if path == "" {
		return v, nil
	}
	if !strings.HasPrefix(path, "/") {
		return nil, errors.New("invalid pointer")
	}
	for _, part := range strings.Split(path[1:], "/") {
		part = strings.ReplaceAll(strings.ReplaceAll(part, "~1", "/"), "~0", "~")
		switch x := v.(type) {
		case map[string]any:
			var ok bool
			v, ok = x[part]
			if !ok {
				return nil, errors.New("missing pointer")
			}
		case []any:
			i, err := strconv.Atoi(part)
			if err != nil || i < 0 || i >= len(x) {
				return nil, errors.New("invalid array pointer")
			}
			v = x[i]
		default:
			return nil, errors.New("noncontainer pointer")
		}
	}
	return v, nil
}
