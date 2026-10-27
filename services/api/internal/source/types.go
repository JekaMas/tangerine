// Package source owns deterministic, inert source intake and native conversion.
// It neither executes source content nor grants rights or invokes models.
package source

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"path"
	"strings"
)

const ParserVersion = "source-native-v1"

var IDs = []string{"TET-GOLD-1", "SPEECHOCEAN762", "L2-ARCTIC", "WILOCNESS-2.1", "FCE-2.1", "EFCAMDAT-R2", "EFCAMDAT-SHATZ2020", "EFCAMDAT-OKSUZ2025", "DOUBAO-STUDY-RECORDS", "MOODRICK-DATA", "NIR-DATA"}

// Supplemental sources never replace or inflate the original eleven scopes.
var SupplementalIDs = []string{"JFLEG", "EDACC", "ELRD", "DIPLOMAT", "DRAL"}

func AllIDs() []string { return append(append([]string{}, IDs...), SupplementalIDs...) }

func Known(id string) bool {
	for _, v := range AllIDs() {
		if id == v {
			return true
		}
	}
	return false
}

type Issue struct {
	Locator string `json:"source_locator"`
	Code    string `json:"code"`
	Detail  string `json:"detail"`
}

func (i Issue) Error() string                   { return i.Code + ": " + i.Locator + ": " + i.Detail }
func Failure(member, code, detail string) error { return Issue{member, code, detail} }

type Row map[string]any
type Table struct {
	Name   string `json:"name"`
	Member string `json:"member"`
	Rows   []Row  `json:"rows"`
}
type Native struct {
	Tables []Table `json:"tables"`
	Issues []Issue `json:"issues"`
}
type Options struct {
	Format    string  `json:"format"`
	Selector  string  `json:"selector"`
	Encoding  string  `json:"encoding"`
	Delimiter *string `json:"delimiter"`
	Header    bool    `json:"has_header"`
}
type Open func(context.Context, string) (io.ReadCloser, error)
type Member struct {
	Path      string         `json:"relative_path"`
	SHA       string         `json:"sha256"`
	Bytes     int64          `json:"byte_count"`
	Component string         `json:"component"`
	Partition *string        `json:"partition"`
	AssetID   string         `json:"asset_id,omitempty"`
	Media     map[string]any `json:"media_metadata,omitempty"`
}

func SafePath(s string) (string, error) {
	if s == "" || strings.ContainsAny(s, "\\\x00") || strings.HasPrefix(s, "/") || strings.Contains(strings.Split(s, "/")[0], ":") {
		return "", Failure(s, "unsafe_path", "Expected a relative POSIX member")
	}
	for _, p := range strings.Split(s, "/") {
		if p == ".." {
			return "", Failure(s, "unsafe_path", "Parent traversal is not allowed")
		}
	}
	s = path.Clean(s)
	if s == "." || strings.HasPrefix(s, "../") {
		return "", Failure(s, "unsafe_path", "Expected an ordinary file")
	}
	return s, nil
}
func Decode(data []byte, dst any) error {
	d := json.NewDecoder(strings.NewReader(string(data)))
	d.UseNumber()
	if e := d.Decode(dst); e != nil {
		return e
	}
	if d.Decode(new(any)) != io.EOF {
		return fmt.Errorf("trailing JSON content")
	}
	return nil
}
func component(name string) string {
	n := strings.ToLower(name)
	switch {
	case strings.HasSuffix(n, ".wav"), strings.HasSuffix(n, ".mp3"), strings.HasSuffix(n, ".mp4"):
		return "media"
	case strings.Contains(n, "license"), strings.Contains(n, "readme"), strings.Contains(n, "agreement"), strings.Contains(n, "prompt"):
		return "documentation"
	case strings.HasSuffix(n, ".textgrid"), strings.HasSuffix(n, ".m2"), strings.Contains(n, "score"):
		return "annotations"
	}
	return "data"
}
func Partition(name string) *string {
	n := strings.ToLower(name)
	for _, p := range []string{"train", "dev", "test", "calibration", "holdout"} {
		for _, s := range strings.FieldsFunc(n, func(r rune) bool { return r == '/' || r == '.' || r == '_' || r == '-' }) {
			if s == p {
				return &p
			}
		}
	}
	return nil
}
func NewMember(name string) Member {
	return Member{Path: name, Component: component(name), Partition: Partition(name)}
}
