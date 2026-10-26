package app

import (
	"encoding/json"
	"tangerine.local/api/internal/source"
)

type SourceRelease struct {
	Version     string              `json:"schema_version"`
	ID          string              `json:"id"`
	Source      string              `json:"source_id"`
	Release     string              `json:"source_version"`
	Origin      string              `json:"origin_uri"`
	Docs        []string            `json:"documentation_asset_ids"`
	Permissions []string            `json:"permission_grant_ids"`
	Profile     *string             `json:"format_profile_id"`
	ProfileSHA  *string             `json:"format_profile_sha256"`
	Files       []SourceReleaseFile `json:"files"`
	Expected    []SourceCount       `json:"expected_counts"`
	Observed    []SourceCount       `json:"observed_counts"`
	Manifest    string              `json:"manifest_sha256"`
	Scope       string              `json:"scope_kind,omitempty"`
	Components  []SourceComponent   `json:"component_expectations,omitempty"`
}
type SourceReleaseFile struct {
	Path      string  `json:"relative_path"`
	SHA       string  `json:"sha256"`
	Bytes     string  `json:"bytes"`
	Component string  `json:"component"`
	Partition *string `json:"partition"`
	Required  bool    `json:"required"`
}
type SourceCount struct {
	Unit      string  `json:"unit"`
	Partition *string `json:"partition"`
	Value     *string `json:"value"`
	Basis     *string `json:"basis_asset_id"`
}
type SourceComponent struct {
	Name     string   `json:"component"`
	Globs    []string `json:"member_globs"`
	Expected *string  `json:"expected"`
	Reason   string   `json:"reconciliation_reason"`
}
type SourceReport struct {
	Version       string                 `json:"schema_version"`
	ID            string                 `json:"id"`
	Release       string                 `json:"release_id"`
	Parser        string                 `json:"parser_id"`
	ParserVersion string                 `json:"parser_version"`
	State         string                 `json:"state"`
	Observed      string                 `json:"observed_records"`
	Accepted      string                 `json:"accepted_records"`
	Quarantined   string                 `json:"quarantined_records"`
	Rejected      string                 `json:"rejected_records"`
	Components    []SourceComponentCount `json:"component_counts"`
	Issues        []source.Issue         `json:"issues"`
	FullIssues    *string                `json:"full_issue_asset_id"`
	Manifest      string                 `json:"source_manifest_sha256"`
	Started       string                 `json:"started_at"`
	Finished      *string                `json:"finished_at"`
	RawComplete   bool                   `json:"raw_complete"`
	Normalized    bool                   `json:"normalized_complete"`
	RawOnly       string                 `json:"raw_only_records"`
	FullMissing   []string               `json:"full_release_missing_components"`
}
type SourceComponentCount struct {
	Component string  `json:"component"`
	Expected  *string `json:"expected"`
	Observed  string  `json:"observed"`
	Complete  bool    `json:"complete"`
}
type SourceRun struct {
	Report      SourceReport `json:"report"`
	Revision    int64        `json:"revision"`
	Epoch       int64        `json:"-"`
	Operation   string       `json:"-"`
	Phase       string       `json:"phase"`
	Member      string       `json:"member_cursor"`
	Row         int64        `json:"row_cursor"`
	Binding     string       `json:"format_binding_id"`
	Permissions []string     `json:"permission_grant_ids"`
	Frozen      SourceFrozen `json:"-"`
	Replay      bool         `json:"-"`
}
type SourceFrozen struct {
	MethodSHA   string          `json:"method_sha256"`
	Release     SourceRelease   `json:"release"`
	Binding     map[string]any  `json:"binding"`
	Program     *source.Program `json:"program"`
	Permissions []string        `json:"permission_ids"`
	Native      bool            `json:"native"`
}

func sourceBytes(v any) []byte { b, _ := json.Marshal(v); return b }
