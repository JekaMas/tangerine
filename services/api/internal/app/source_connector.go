package app

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
)

type sourceExportProgress struct {
	Frozen     map[string]any    `json:"frozen"`
	Cursor     *string           `json:"cursor"`
	Seen       []string          `json:"seen"`
	Files      []source.Member   `json:"files"`
	Pages      int               `json:"pages"`
	Count      int64             `json:"observed_records"`
	Expected   *string           `json:"expected_records"`
	Complete   bool              `json:"complete"`
	Failure    string            `json:"failure"`
	Identities map[string]string `json:"identities"`
	Conflicts  []source.Issue    `json:"conflicts"`
}

func (s *Server) FetchSourceExport(ctx context.Context, id string, client *http.Client) (sourceExportProgress, error) {
	conn, e := s.Store.DB.Acquire(ctx)
	if e != nil {
		return sourceExportProgress{}, e
	}
	defer conn.Release()
	var locked bool
	if e = conn.QueryRow(ctx, "SELECT pg_try_advisory_lock(hashtextextended($1,79004771))", id).Scan(&locked); e != nil {
		return sourceExportProgress{}, e
	}
	if !locked {
		return sourceExportProgress{}, ErrEvaluationActive
	}
	defer func() {
		if _, e := conn.Exec(context.Background(), "SELECT pg_advisory_unlock(hashtextextended($1,79004771))", id); e != nil {
			_ = conn.Hijack().Close(context.Background())
		}
	}()
	var raw, progress []byte
	if e = conn.QueryRow(ctx, "SELECT payload,export_progress FROM source_connector WHERE id=$1", id).Scan(&raw, &progress); e != nil {
		return sourceExportProgress{}, e
	}
	var config map[string]any
	_ = json.Unmarshal(raw, &config)
	p := sourceExportProgress{Frozen: config, Seen: []string{}, Files: []source.Member{}}
	if len(progress) > 0 {
		if e = json.Unmarshal(progress, &p); e != nil {
			return p, e
		}
		if p.Failure != "" {
			return p, source.Failure(id, p.Failure, "Saved export requires corrected documented configuration; all native pages remain retained")
		}
		if p.Complete {
			return p, nil
		}
		config = p.Frozen
	}
	if config["remote_spec"] == nil {
		return p, source.Failure(id, "interface_missing", "No documented remote adapter supplied; use the complete local-export route")
	}
	var spec source.RemoteSpec
	if e = json.Unmarshal(sourceBytes(config["remote_spec"]), &spec); e != nil {
		return p, e
	}
	if len(progress) == 0 {
		p.Cursor = spec.InitialCursor
	}
	hosts := []string{}
	for _, v := range config["allowed_hosts"].([]any) {
		hosts = append(hosts, v.(string))
	}
	secret := ""
	if ref, ok := config["credential_ref"].(string); ok {
		name, e := sourceCredentialName(id, ref)
		if e != nil {
			return p, e
		}
		b, e := os.ReadFile(filepath.Join(s.Providers.Dir, name))
		if e != nil {
			return p, source.Failure(id, "credentials_missing", "Selected export credential unavailable")
		}
		secret = string(b)
	}
	save := func() error {
		_, e := conn.Exec(ctx, "UPDATE source_connector SET export_progress=$2 WHERE id=$1", id, sourceBytes(p))
		return e
	}
	if p.Identities == nil {
		p.Identities = map[string]string{}
	}
	for !p.Complete {
		if e = ctx.Err(); e != nil {
			return p, e
		}
		key := source.CursorKey(p.Cursor)
		for _, seen := range p.Seen {
			if key == seen {
				return p, source.Failure(id, "pagination_cycle", "A documented continuation cursor repeated")
			}
		}
		page, e := source.FetchPage(ctx, client, spec, hosts, p.Cursor, secret)
		if e != nil {
			return p, e
		}
		name := source.RemotePageName(id, p.Pages)
		file, e := s.Store.saveSourceStream(ctx, name, strings.NewReader(string(page.Bytes)))
		if e != nil {
			return p, e
		}
		p.Files = append(p.Files, file)
		// Retain both original envelope and the lossless explicitly located record view.
		var records strings.Builder
		for _, record := range page.Records {
			records.Write(sourceBytes(record))
			records.WriteByte('\n')
		}
		view, e := s.Store.saveSourceStream(ctx, name+".records.jsonl", strings.NewReader(records.String()))
		if e != nil {
			return p, e
		}
		p.Files = append(p.Files, view)
		if spec.IdentityPointer != "" {
			for index, record := range page.Records {
				identity, ok := source.Pointer(record, spec.IdentityPointer)
				if !ok || identity == nil {
					p.Conflicts = append(p.Conflicts, source.Issue{Locator: name + fmt.Sprint(index), Code: "identity_missing", Detail: "Documented remote identity is absent"})
					continue
				}
				key := source.IdentityKey(identity)
				if key == "" {
					p.Conflicts = append(p.Conflicts, source.Issue{Locator: name + fmt.Sprint(index), Code: "identity_unbound", Detail: "Documented identity must be an exact scalar"})
					continue
				}
				recordBytes := sourceBytes(source.RawValue(record))
				digest := contracts.Digest(recordBytes)
				if old, ok := p.Identities[key]; ok {
					detail := "Repeated source identity (identical payload)"
					if old != digest {
						detail = "Repeated source identity with conflicting payload"
					}
					p.Conflicts = append(p.Conflicts, source.Issue{Locator: name + fmt.Sprint(index), Code: "identity_conflict", Detail: detail})
				} else {
					p.Identities[key] = digest
				}
			}
		}
		p.Pages++
		p.Count += int64(len(page.Records))
		if page.Total != nil {
			n := string(*page.Total)
			if p.Expected != nil && *p.Expected != n {
				return p, source.Failure(id, "count_drift", "Source total changed within the frozen export")
			}
			p.Expected = &n
		}
		p.Seen = append(p.Seen, key)
		p.Cursor = page.Next
		p.Complete = page.End
		if p.Complete && len(p.Conflicts) > 0 {
			p.Complete = false
			p.Failure = "identity_conflict"
			if e = save(); e != nil {
				return p, e
			}
			return p, source.Failure(id, p.Failure, "Native duplicate/conflicting identities retained; no records dropped")
		}
		if p.Complete && p.Expected != nil && *p.Expected != sourceNumber(p.Count) {
			p.Complete = false
			p.Failure = "count_mismatch"
			if e = save(); e != nil {
				return p, e
			}
			return p, source.Failure(id, "count_mismatch", "Actual retained records differ from declared source total")
		}
		if e = save(); e != nil {
			return p, e
		}
	}
	return p, nil
}
