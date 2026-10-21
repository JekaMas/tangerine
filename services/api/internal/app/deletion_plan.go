package app

import (
	"context"
	"encoding/json"
	"github.com/jackc/pgx/v5"
	"sort"
	"tangerine.local/api/internal/lab"
)

func sortedKeys(set map[string]bool) []string {
	out := []string{}
	for k := range set {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

// A plan expands explicit logical subjects to their stored versions and dependent
// records. It does not follow shared case/configuration inputs out of an attempt.
func (s *Storage) deletionPlan(ctx context.Context, tx pgx.Tx, input DeletionSelection) (DeletionPlan, error) {
	p := DeletionPlan{Selection: input, Documents: []string{}, Assets: []string{}, Keys: []string{}, Operations: []string{}, Heads: []string{}, Blocked: []string{}, State: "preview", LabCleanup: "not_requested"}
	var sourceErr error
	p.Source, sourceErr = sourceErasure(ctx, tx, input.IDs)
	if sourceErr != nil {
		return p, sourceErr
	}
	roots := map[string]bool{}
	for _, id := range input.IDs {
		if id == "" || id == "local-configuration" {
			return p, ErrInput
		}
		roots[id] = true
	}
	// Receipts are experiment-owned native evidence; the existing graph expansion
	// follows their operations, bindings, contexts and private diagnostic copies.
	receipts, e := erasureStrings(ctx, tx, `SELECT jsonb_array_elements_text(r.value->'receipt_ids') FROM quality_experiment q CROSS JOIN LATERAL jsonb_array_elements(q.payload->'rows') AS r(value) WHERE q.id=ANY($1) ORDER BY 1`, p.Source.Experiments)
	if e != nil {
		return p, e
	}
	for _, id := range receipts {
		roots[id] = true
	}
	if input.Orphans {
		rows, e := tx.Query(ctx, `SELECT asset_id FROM asset_location a WHERE a.state='orphaned' AND reserved_at<clock_timestamp()-interval '30 days' AND NOT EXISTS(SELECT 1 FROM object_reference r WHERE r.target_id=a.asset_id)`)
		if e != nil {
			return p, e
		}
		for rows.Next() {
			var id string
			if e = rows.Scan(&id); e != nil {
				rows.Close()
				return p, e
			}
			roots[id] = true
		}
		rows.Close()
		if e = rows.Err(); e != nil {
			return p, e
		}
	}
	if len(roots) == 0 && !input.Orphans {
		return p, ErrInput
	}
	// Expand immutable version membership and semantic ownership through explicit
	// fields. Case deletion includes its attempts; the preview names every record.
	seenStages := map[string]bool{}
	documents, operations, heads, assets := map[string]bool{}, map[string]bool{}, map[string]bool{}, map[string]bool{}
	for changed := true; changed; {
		changed = false
		ids := sortedKeys(roots)
		rows, e := tx.Query(ctx, `SELECT id,kind,payload FROM document WHERE id IN(SELECT source_key_id FROM listening_case WHERE case_version_id=ANY($1)) OR (kind IN('effective-binding','provider-receipt','llm-context-snapshot','interpretation-state','result-envelope','stage-cache','extracted-claims','claim-decisions','audio-measurement') AND id IN(SELECT n.document_id FROM object_reference r JOIN object_node n ON n.node_id=r.target_id AND n.scope_id=r.target_scope_id WHERE r.source_document_id=ANY($1))) OR id=ANY($1) OR payload->>'id'=ANY($1) OR payload->>'attempt_id'=ANY($1) OR payload->>'case_version_id'=ANY($1) OR payload#>>'{score,case_version_id}'=ANY($1) OR payload->>'preparation_id'=ANY($1) OR payload->>'key_id'=ANY($1) OR payload->>'operation_id'=ANY($1) OR id IN(SELECT document_id FROM entity_head WHERE id=ANY($1)) OR id IN(SELECT source_document_id FROM object_reference WHERE target_id=ANY($1))`, ids)
		if e != nil {
			return p, e
		}
		for rows.Next() {
			var id, kind string
			var raw []byte
			if e = rows.Scan(&id, &kind, &raw); e != nil {
				rows.Close()
				return p, e
			}
			if kind == "configuration" || kind == "prompt-bundle" {
				p.Blocked = append(p.Blocked, id)
				continue
			}
			if !documents[id] {
				changed = true
				documents[id] = true
				roots[id] = true
			}
			var body map[string]any
			_ = json.Unmarshal(raw, &body)
			if kind == "preparation-state" || kind == "candidate-envelope" {
				if value, ok := body["id"].(string); ok && !roots[value] {
					roots[value] = true
					changed = true
				}
			}
			if kind == "interpretation-checkpoint" {
				if stages, ok := body["stages_asset_id"].(string); ok && stages != "" && !seenStages[stages] {
					seenStages[stages] = true
					b, err := s.ReadAsset(ctx, stages)
					if err != nil {
						rows.Close()
						return p, err
					}
					var entries []InterpretationStage
					if err = json.Unmarshal(b, &entries); err != nil {
						rows.Close()
						return p, err
					}
					for _, entry := range entries {
						links := append(append([]string{entry.Result.OperationID, entry.Result.BindingID}, entry.Result.ReceiptIDs...), entry.Result.ContextIDs...)
						if entry.Diagnostic != nil {
							links = append(links, *entry.Diagnostic)
						}
						for _, link := range links {
							if link != "" && !roots[link] {
								roots[link] = true
								changed = true
							}
						}
					}
				}
			}
			for _, key := range []string{"attempt_id", "operation_id"} {
				if value, ok := body[key].(string); ok && !roots[value] {
					roots[value] = true
					changed = true
				}
			}
		}
		rows.Close()
		if e = rows.Err(); e != nil {
			return p, e
		}
		rows, e = tx.Query(ctx, `SELECT id,input_document_id,result_document_id,error_document_id FROM operation WHERE subject_id=ANY($1) OR id=ANY($1) OR id IN(SELECT row_operation_id FROM quality_call WHERE receipt_id=ANY($1)) OR idempotency_key IN(SELECT idempotency_key FROM operation WHERE id=ANY($1)) OR (operation_name='lab-diagnostic' AND idempotency_key::text=ANY($1))`, sortedKeys(roots))
		if e != nil {
			return p, e
		}
		for rows.Next() {
			var id string
			var in, out, failed *string
			if e = rows.Scan(&id, &in, &out, &failed); e != nil {
				rows.Close()
				return p, e
			}
			operations[id] = true
			if !roots[id] {
				changed = true
			}
			roots[id] = true
			for _, v := range []*string{in, out, failed} {
				if v != nil && !roots[*v] {
					roots[*v] = true
					changed = true
				}
			}
		}
		rows.Close()
		if e = rows.Err(); e != nil {
			return p, e
		}
	}
	// Retained experiments still own their recorded receipts. Reject implicit
	// erasure rather than leaving their frozen results with missing evidence.
	retainedExperiments, e := erasureStrings(ctx, tx, `SELECT q.id FROM quality_experiment q WHERE NOT(q.id=ANY($1)) AND EXISTS(SELECT 1 FROM jsonb_array_elements(q.payload->'rows') AS r(value) CROSS JOIN LATERAL jsonb_array_elements_text(r.value->'receipt_ids') AS receipt(id) WHERE receipt.id=ANY($2)) ORDER BY q.id`, p.Source.Experiments, sortedKeys(documents))
	if e != nil {
		return p, e
	}
	for _, id := range retainedExperiments {
		p.Blocked = append(p.Blocked, "retained_experiment:"+id)
	}
	ids := sortedKeys(roots)
	rows, e := tx.Query(ctx, `SELECT id FROM entity_head WHERE document_id=ANY($1) OR id=ANY($2)`, sortedKeys(documents), ids)
	if e != nil {
		return p, e
	}
	for rows.Next() {
		var id string
		if e = rows.Scan(&id); e != nil {
			rows.Close()
			return p, e
		}
		heads[id] = true
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return p, e
	}
	// Private bytes explicitly bound to selected documents are candidates. Shared
	// retained references keep the asset, rather than deleting another exercise.
	rows, e = tx.Query(ctx, `SELECT DISTINCT a.asset_id,a.storage_key FROM asset_location a WHERE a.asset_id=ANY($1) OR a.owner_head_id=ANY($1) OR a.asset_id IN(SELECT target_id FROM object_reference WHERE source_document_id=ANY($2) AND target_kind IN('asset','asset-bytes'))`, append(append(ids, sortedKeys(heads)...), p.Source.AssetIDs...), sortedKeys(documents))
	if e != nil {
		return p, e
	}
	keyByID := map[string]string{}
	for rows.Next() {
		var id, key string
		if e = rows.Scan(&id, &key); e != nil {
			rows.Close()
			return p, e
		}
		keyByID[id] = key
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return p, e
	}
	for id, key := range keyByID {
		var shared bool
		e = tx.QueryRow(ctx, `SELECT EXISTS(SELECT 1 FROM object_reference r JOIN document d ON d.id=r.source_document_id WHERE r.target_id=$1 AND NOT(r.source_document_id=ANY($2)) AND d.kind<>'asset') OR EXISTS(SELECT 1 FROM listening_case WHERE audio_asset_id=$1 AND NOT(case_version_id=ANY($2))) OR EXISTS(SELECT 1 FROM source_file WHERE asset_id=$1 AND NOT(id=ANY($3))) OR EXISTS(SELECT 1 FROM empirical_report WHERE (asset_id=$1 OR input_asset_id=$1) AND NOT(id=ANY($4))) OR EXISTS(SELECT 1 FROM quality_experiment q WHERE NOT(q.id=ANY($5)) AND (q.frozen_asset_id=$1 OR q.payload->>'comparison_asset_id'=$1 OR EXISTS(SELECT 1 FROM jsonb_array_elements(q.payload->'rows') AS r(value) WHERE r.value->>'output_asset_id'=$1))) OR EXISTS(SELECT 1 FROM quality_export WHERE asset_id=$1 AND NOT(experiment_id=ANY($5)))`, id, sortedKeys(documents), p.Source.Files, p.Source.Reports, p.Source.Experiments).Scan(&shared)
		if e != nil {
			return p, e
		}
		if shared {
			if containsString(input.IDs, id) {
				p.Blocked = append(p.Blocked, id)
			}
			continue
		}
		assets[id] = true
		p.Keys = append(p.Keys, key)
		heads[id] = true
		dr, e := tx.Query(ctx, `SELECT id FROM document WHERE kind='asset' AND payload->>'id'=$1`, id)
		if e != nil {
			return p, e
		}
		for dr.Next() {
			var d string
			if e = dr.Scan(&d); e != nil {
				dr.Close()
				return p, e
			}
			documents[d] = true
		}
		dr.Close()
		if e = dr.Err(); e != nil {
			return p, e
		}
	}
	var active bool
	e = tx.QueryRow(ctx, `SELECT EXISTS(SELECT 1 FROM operation WHERE state='running' AND started_at>clock_timestamp()-interval '270 seconds' AND (id=ANY($1) OR subject_id=ANY($2))) OR EXISTS(SELECT 1 FROM evaluation_lease WHERE attempt_id=ANY($2) AND expires_at>clock_timestamp())`, sortedKeys(operations), ids).Scan(&active)
	if e != nil {
		return p, e
	}
	var sourceActive bool
	if e = tx.QueryRow(ctx, `SELECT EXISTS(SELECT 1 FROM source_import i JOIN operation o ON o.id=i.operation_id WHERE i.id=ANY($1) AND i.deadline_at>clock_timestamp() AND o.state='running') OR EXISTS(SELECT 1 FROM quality_experiment WHERE id=ANY($2) AND active_operation_id IS NOT NULL AND lease_until>clock_timestamp())`, p.Source.Imports, p.Source.Experiments).Scan(&sourceActive); e != nil {
		return p, e
	}
	if active || sourceActive {
		p.Blocked = append(p.Blocked, "active_foreground_operation")
	}
	for _, id := range input.IDs {
		if !heads[id] && !documents[id] && !assets[id] && !containsString(p.Source.Releases, id) && !containsString(p.Source.Imports, id) && !containsString(p.Source.Reports, id) && !containsString(p.Source.Experiments, id) {
			p.Blocked = append(p.Blocked, "unknown:"+id)
		}
	}
	p.Documents = sortedKeys(documents)
	p.Assets = sortedKeys(assets)
	p.Operations = sortedKeys(operations)
	p.Heads = sortedKeys(heads)
	sort.Strings(p.Keys)
	sort.Strings(p.Blocked)
	var captures bool
	e = tx.QueryRow(ctx, `SELECT EXISTS(SELECT 1 FROM document WHERE id=ANY($1) AND kind IN('provider-receipt','llm-context-snapshot'))`, p.Documents).Scan(&captures)
	if e != nil {
		return p, e
	}
	if captures || len(p.Source.Experiments) > 0 {
		p.LabCleanup = "pending_explicit_local_lab_cleanup"
	}
	if len(p.Blocked) > 0 {
		p.State = "blocked_active_reference"
	}
	p.Digest = lab.Hash(p)
	return p, nil
}
func containsString(values []string, target string) bool {
	for _, v := range values {
		if v == target {
			return true
		}
	}
	return false
}
