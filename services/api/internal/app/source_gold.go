package app

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"sync"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
)

// Gold import only accounts actual supplied labels and pair metadata. It neither
// creates benchmark populations nor claims semantic validity or runs a model.
func sourceGoldAdmission(value any) (map[string]any, error) {
	gold, ok := value.(map[string]any)
	if !ok {
		return nil, fmt.Errorf("gold descriptor absent")
	}
	key, ok := gold["ground_truth"].(map[string]any)
	if !ok {
		return nil, fmt.Errorf("actual source key absent")
	}
	if _, _, e := contracts.Validate("ground-truth", "2.0.0", sourceBytes(key)); e != nil {
		return nil, e
	}
	for _, field := range []string{"pair_id", "split", "label_origin"} {
		if v, ok := gold[field].(string); !ok || v == "" {
			return nil, fmt.Errorf("missing gold %s", field)
		}
	}
	if gold["pair_role"] != "positive" && gold["pair_role"] != "control" {
		return nil, fmt.Errorf("missing actual pair role")
	}
	if gold["label_origin"] != "llm" && gold["label_origin"] != "source_import" {
		return nil, fmt.Errorf("unrecognized actual label origin")
	}
	if len(stringArray(gold["group_ids"])) == 0 {
		return nil, fmt.Errorf("missing genuine grouping metadata")
	}
	return gold, nil
}
func stringArray(v any) []string {
	out := []string{}
	switch a := v.(type) {
	case []any:
		for _, v := range a {
			if s, ok := v.(string); ok {
				out = append(out, s)
			}
		}
	case []string:
		out = append(out, a...)
	}
	return out
}
func (s *Storage) sourceGoldMissing(ctx context.Context, id string, members []source.Member) ([]string, error) {
	audio := map[string]bool{}
	for _, member := range members {
		if strings.EqualFold(filepathExtension(member.Path), ".wav") && member.Media["error"] == nil && member.Media["sample_rate_hz"] != nil {
			audio[member.SHA] = true
		}
	}
	rows, e := s.DB.Query(ctx, "SELECT projection #> '{raw_metadata,gold}' FROM source_row WHERE import_id=$1 AND state='mapped' AND projection #> '{raw_metadata,gold}' IS NOT NULL", id)
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	stimuli := map[string]bool{}
	leaves := map[string]map[string]map[string]bool{}
	domains := map[string]bool{}
	groups := map[string]string{}
	overlap := false
	for rows.Next() {
		var raw []byte
		if e = rows.Scan(&raw); e != nil {
			return nil, e
		}
		var gold map[string]any
		if e = source.Decode(raw, &gold); e != nil {
			return nil, e
		}
		key := gold["ground_truth"].(map[string]any)
		a := key["audio"].(map[string]any)
		hash, _ := a["sha256"].(string)
		if !audio[hash] {
			continue
		}
		contextBytes, _ := contracts.Canonical(sourceBytes(map[string]any{"public_context": key["public_context"]}))
		identity := hash + "/" + contracts.Digest(contextBytes) + "/" + sourceGoldCondition(key)
		stimuli[identity] = true
		split := gold["split"].(string)
		for _, g := range stringArray(gold["group_ids"]) {
			if old, ok := groups[g]; ok && old != split {
				overlap = true
			}
			groups[g] = split
		}
		for _, v := range key["units"].([]any) {
			u := v.(map[string]any)
			leaf := u["primary_taxonomy_id"].(string)
			domain := u["domain"].(string)
			domains[domain] = true
			if leaves[leaf] == nil {
				leaves[leaf] = map[string]map[string]bool{}
			}
			pair := split + "/" + gold["pair_id"].(string)
			if leaves[leaf][pair] == nil {
				leaves[leaf][pair] = map[string]bool{}
			}
			leaves[leaf][pair][gold["pair_role"].(string)+"/"+identity] = true
		}
	}
	if e = rows.Err(); e != nil {
		return nil, e
	}
	missing := []string{}
	if len(stimuli) < 732 {
		missing = append(missing, fmt.Sprintf("732distinct playable stimulus conditions; observed%d", len(stimuli)))
	}
	if len(domains) != 8 {
		missing = append(missing, fmt.Sprintf("eight supplied domains; observed%d", len(domains)))
	}
	if overlap {
		missing = append(missing, "source-connected groups overlap declared splits")
	}
	categories := taxonomyCoverageIDs()
	if len(categories) != 122 {
		return nil, fmt.Errorf("packaged taxonomy coverage unavailable")
	}
	for _, leaf := range categories {
		splits := map[string]bool{}
		conditions := map[string]bool{}
		for pair, roles := range leaves[leaf] {
			positive, control := false, false
			for role := range roles {
				positive = positive || strings.HasPrefix(role, "positive/")
				control = control || strings.HasPrefix(role, "control/")
				conditions[strings.SplitN(role, "/", 2)[1]] = true
			}
			if positive && control {
				splits[strings.SplitN(pair, "/", 2)[0]] = true
			}
		}
		if len(splits) < 3 || len(conditions) < 6 {
			missing = append(missing, "six distinct positive/control stimuli across three independent split families for "+leaf)
		}
	}
	return missing, nil
}
func filepathExtension(name string) string {
	at := strings.LastIndex(name, ".")
	if at < 0 {
		return ""
	}
	return name[at:]
}

var sourceTaxonomyOnce sync.Once
var sourceTaxonomyIDs []string

func taxonomyCoverageIDs() []string {
	sourceTaxonomyOnce.Do(func() {
		raw, _ := generationRegistry("mutation-recipes.v1.json")
		var registry map[string]any
		_ = json.Unmarshal(raw, &registry)
		if recipes, ok := registry["recipes"].([]any); ok {
			for _, v := range recipes {
				r := v.(map[string]any)
				if id, ok := r["taxonomy_id"].(string); ok {
					sourceTaxonomyIDs = append(sourceTaxonomyIDs, id)
				}
			}
		}
	})
	return sourceTaxonomyIDs
}
func sourceGoldCondition(key map[string]any) string {
	references := map[string]string{}
	for _, field := range []string{"speakers", "utterances"} {
		if a, ok := key[field].([]any); ok {
			for index, v := range a {
				if m, ok := v.(map[string]any); ok {
					if id, ok := m["id"].(string); ok {
						references[id] = fmt.Sprintf("%s:%d", field, index)
					}
				}
			}
		}
	}
	meta := map[string]bool{"id": true, "case_version_id": true, "case_sha256": true, "asset_id": true, "evidence_ids": true, "content_provenance_ids": true, "review_decisions": true, "source": true, "verification": true, "status": true, "difficulty_evidence_ref": true}
	var stable func(any) any
	stable = func(v any) any {
		switch x := v.(type) {
		case map[string]any:
			out := map[string]any{}
			for k, v := range x {
				if !meta[k] {
					out[k] = stable(v)
				}
			}
			return out
		case []any:
			out := make([]any, len(x))
			for i, v := range x {
				out[i] = stable(v)
			}
			return out
		case string:
			if ref, ok := references[x]; ok {
				return ref
			}
			return x
		default:
			return v
		}
	}
	raw, _ := contracts.Canonical(sourceBytes(stable(key)))
	return contracts.Digest(raw)
}
