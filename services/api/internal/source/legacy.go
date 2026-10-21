package source

import (
	"fmt"
	"strconv"
	"strings"
)

func LegacyRecord(id, release, member, table string, ordinal int, row Row, binding map[string]any) Mapped {
	m := BaseProjection(id, release, member, table, ordinal, row)
	record := map[string]any{}
	raw := m.Value["raw_metadata"].(map[string]any)
	fields, _ := binding["fields"].([]any)
	bad := false
	for _, v := range fields {
		f, ok := v.(map[string]any)
		if !ok {
			continue
		}
		locator, _ := f["source_path"].(string)
		target, _ := f["target_field"].(string)
		conversion, _ := f["conversion"].(string)
		value, found := legacyValue(row, locator)
		for _, marker := range asArray(f["null_values"]) {
			if value == marker {
				value = nil
			}
		}
		if (!found || value == nil) && f["required"] == true {
			bad = true
			m.Issues = append(m.Issues, Issue{member, "required_missing", locator})
		}
		if conversion == "raw_only" || target == "raw_only" {
			continue
		}
		kind := conversion
		if kind == "source_token_span" {
			kind = "token_span"
		}
		if kind == "source_seconds" {
			raw[target] = value
			continue
		}
		converted, e := Convert(value, kind, Program{Origin: "zero_based_half_open"}, row)
		if e != nil {
			bad = true
			m.Issues = append(m.Issues, Issue{member, "conversion_failed", locator + ": " + e.Error()})
			continue
		}
		switch target {
		case "text", "speaker_id", "l1":
			record[target] = converted
		case "learner_id":
			if converted != nil {
				record["group_ids"] = []string{learnerGroup(id, fmt.Sprint(converted))}
			}
		}
		raw[target] = converted
	}
	if _, ok := record["text"].(string); ok && !bad {
		record["origin"] = "external_written"
		m.Value["corpus_record"] = record
		m.Status = "mapped"
	}
	if row["invalid"] == true {
		m.Status = "quarantined"
		m.Issues = append(m.Issues, Issue{member, "native_invalid", "Native format row failed its parser admission"})
	}
	return m
}
func legacyValue(row Row, p string) (any, bool) {
	if strings.HasPrefix(p, "/") {
		return Pointer(row, p)
	}
	if strings.HasPrefix(p, "csv:column[") && strings.HasSuffix(p, "]") {
		i, e := strconv.Atoi(strings.TrimSuffix(strings.TrimPrefix(p, "csv:column["), "]"))
		if e != nil {
			return nil, false
		}
		return Pointer(row, fmt.Sprintf("/cells/%d", i))
	}
	if h, ok := row["header"].([]any); ok {
		idx := -1
		for i, v := range h {
			if v == p {
				if idx != -1 {
					return nil, false
				}
				idx = i
			}
		}
		if idx >= 0 {
			return Pointer(row, fmt.Sprintf("/cells/%d", idx))
		}
	}
	if h, ok := row["header"].([]string); ok {
		idx := -1
		for i, v := range h {
			if v == p {
				if idx != -1 {
					return nil, false
				}
				idx = i
			}
		}
		if idx >= 0 {
			return Pointer(row, fmt.Sprintf("/cells/%d", idx))
		}
	}
	return Pointer(row, "/value/"+strings.ReplaceAll(strings.ReplaceAll(p, "~", "~0"), "/", "~1"))
}

// A documented learner_id mapping on EFCAMDAT derivatives uses the shared
// original learner namespace. Other vendor identities remain separate.
func learnerGroup(id, learner string) string {
	if strings.HasPrefix(id, "EFCAMDAT-") {
		return StableID("efcamdat-learner", learner)
	}
	return StableID(id, "native-learner", learner)
}
