package app

import (
	"context"
	"encoding/json"
	"tangerine.local/api/internal/source"
)

func (s *Storage) SourceStatuses(ctx context.Context) ([]map[string]any, error) {
	out := []map[string]any{}
	for _, id := range source.AllIDs() {
		item := sourceStatusBase(id)
		rows, e := s.DB.Query(ctx, "SELECT id,payload FROM source_release WHERE source_id=$1 ORDER BY created_at,id", id)
		if e != nil {
			return nil, e
		}
		releases := []SourceRelease{}
		ids := []string{}
		for rows.Next() {
			var rid string
			var b []byte
			if e = rows.Scan(&rid, &b); e != nil {
				rows.Close()
				return nil, e
			}
			var r SourceRelease
			_ = json.Unmarshal(b, &r)
			releases = append(releases, r)
			ids = append(ids, rid)
		}
		rows.Close()
		if e = rows.Err(); e != nil {
			return nil, e
		}
		item["release_ids"] = ids
		item["selected_release_ids"] = ids
		if len(releases) > 0 {
			last := releases[len(releases)-1]
			members := []source.Member{}
			for _, file := range last.Files {
				members = append(members, source.Member{Path: file.Path})
			}
			missing := source.MissingNative(id, members)
			item["missing_component_names"] = missing
			item["status"] = "ready_to_import"
			item["reasons"] = []string{"Actual intake is independent of original full-source and semantic completeness. Selected scope: " + last.Scope}
			reports, e := s.DB.Query(ctx, "SELECT id,release_id,payload,published FROM source_import WHERE release_id=ANY($1) ORDER BY created_at,id", ids)
			if e != nil {
				return nil, e
			}
			imports := []string{}
			byRelease := map[string][]string{}
			for _, rid := range ids {
				byRelease[rid] = []string{}
			}
			for reports.Next() {
				var iid, rid string
				var published bool
				var b []byte
				if e = reports.Scan(&iid, &rid, &b, &published); e != nil {
					reports.Close()
					return nil, e
				}
				byRelease[rid] = append(byRelease[rid], iid)
				if rid != last.ID {
					continue
				}
				var report SourceReport
				_ = json.Unmarshal(b, &report)
				imports = append(imports, iid)
				missing = report.FullMissing
				if missing == nil {
					missing = []string{"Full-release assessment was not saved. Existing retained data remain usable."}
				}
				item["missing_component_names"] = missing
				item["raw_complete"] = report.RawComplete
				item["normalized_complete"] = report.Normalized
				item["raw_only_records"] = report.RawOnly
				switch {
				case !published:
					item["status"] = "ready_to_import"
				case report.State != "complete":
					item["status"] = "incomplete"
				case !report.Normalized && report.RawOnly != "0":
					item["status"] = "format_unbound"
				case !report.Normalized:
					item["status"] = "incomplete"
				case last.Scope != "full_named_release" || len(missing) > 0:
					item["status"] = "incomplete"
				default:
					item["status"] = "complete"
				}
			}
			reports.Close()
			if e = reports.Err(); e != nil {
				return nil, e
			}
			item["import_report_ids"] = imports
			item["release_import_report_ids"] = byRelease
			var revoked bool
			if e = s.DB.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM source_permission WHERE source_id=$1 AND revoked_at IS NOT NULL)", id).Scan(&revoked); e != nil {
				return nil, e
			}
			if revoked {
				item["reasons"] = append(item["reasons"].([]string), "A source permission has an actual retained revocation; selected-use consumers must use current terms.")
			}
		}
		out = append(out, item)
	}
	return out, nil
}

func sourceStatusBase(id string) map[string]any {
	return map[string]any{"source_id": id, "selected_release_ids": []string{}, "release_ids": []string{}, "import_report_ids": []string{}, "release_import_report_ids": map[string][]string{}, "status": "not_acquired", "missing_component_names": []string{"actual selected full release"}, "reasons": []string{}, "raw_complete": false, "normalized_complete": false, "raw_only_records": "0"}
}
