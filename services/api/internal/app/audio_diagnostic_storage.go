package app

// Immutable diagnostic documents use the existing asset/reference/operation graph.
import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"strings"
)

func (s *Storage) diagnosticDocument(ctx context.Context, id, kind string, payload map[string]any, refs map[string]string) (DocumentWrite, SavedDocument, error) {
	raw := sourceBytes(payload)
	w := DocumentWrite{ID: id, Kind: kind, Version: "2.0.0", Scope: "local", Payload: raw}
	for pointer, target := range refs {
		var reference Reference
		if kind == "audio-measurement" || pointer == "/input_asset_id" || strings.HasPrefix(pointer, "/output_asset_ids/") || strings.HasPrefix(pointer, "/support_asset_ids/") {
			ref, err := s.assetByteReference(ctx, target, pointer, "audio-diagnostic")
			if err != nil {
				return w, SavedDocument{}, err
			}
			reference = ref
		} else {
			doc, err := s.ReadDocument(ctx, target)
			if err != nil {
				return w, SavedDocument{}, err
			}
			reference = Reference{Pointer: pointer, ID: target, Scope: "local", Kind: doc.Kind, SHA: doc.SHA, Relation: "audio-diagnostic"}
		}
		w.References = append(w.References, reference)
	}
	d, err := validateDocument(w)
	return w, d, err
}

func (s *Storage) finishAudioDiagnostic(ctx context.Context, op Operation, run map[string]any, rows []map[string]any) (map[string]any, error) {
	writes := []DocumentWrite{}
	saved := []SavedDocument{}
	for _, row := range rows {
		id, ok := row["id"].(string)
		if !ok {
			return nil, ErrInput
		}
		if parsed, err := uuid.Parse(id); err != nil || parsed.Version() != 4 {
			return nil, ErrInput
		}
		refs := map[string]string{}
		for i, id := range diagnosticArrayIDs(row["evidence_asset_ids"]) {
			refs[fmt.Sprintf("/evidence_asset_ids/%d", i)] = id
		}
		w, d, err := s.diagnosticDocument(ctx, id, "audio-measurement", row, refs)
		if err != nil {
			return nil, err
		}
		writes = append(writes, w)
		saved = append(saved, d)
		run["measurement_ids"] = append(run["measurement_ids"].([]any), id)
	}
	refs := map[string]string{"/case_version_id": run["case_version_id"].(string), "/input_asset_id": run["input_asset_id"].(string)}
	for _, field := range []string{"output_asset_ids", "support_asset_ids", "receipt_ids"} {
		for i, id := range diagnosticArrayIDs(run[field]) {
			refs[fmt.Sprintf("/%s/%d", field, i)] = id
		}
	}
	// Measurements are new forward references in this same transaction.
	w := DocumentWrite{ID: run["id"].(string), Kind: "audio-diagnostic-run", Version: "2.0.0", Scope: "local", Payload: sourceBytes(run)}
	for pointer, target := range refs {
		if pointer == "/input_asset_id" || strings.HasPrefix(pointer, "/output_asset_ids/") || strings.HasPrefix(pointer, "/support_asset_ids/") {
			ref, err := s.assetByteReference(ctx, target, pointer, "audio-diagnostic")
			if err != nil {
				return nil, err
			}
			w.References = append(w.References, ref)
		} else {
			doc, err := s.ReadDocument(ctx, target)
			if err != nil {
				return nil, err
			}
			w.References = append(w.References, Reference{Pointer: pointer, ID: target, Scope: "local", Kind: doc.Kind, SHA: doc.SHA, Relation: "audio-diagnostic"})
		}
	}
	for i, d := range saved {
		w.References = append(w.References, Reference{Pointer: fmt.Sprintf("/measurement_ids/%d", i), ID: d.ID, Scope: "local", Kind: d.Kind, SHA: d.SHA, Relation: "audio-diagnostic"})
	}
	d, err := validateDocument(w)
	if err != nil {
		return nil, err
	}
	writes = append(writes, w)
	saved = append(saved, d)
	tx, err := beginWrite(ctx, s)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback(context.Background())
	for i, w := range writes {
		if err = insertDocument(ctx, tx, w, saved[i]); err != nil {
			return nil, err
		}
	}
	state := "complete"
	if run["status"] == "failed" {
		state = "failed"
	}
	tag, err := tx.Exec(ctx, "UPDATE operation SET state=$2,result_document_id=$3,finished_at=clock_timestamp() WHERE id=$1 AND state='running' AND ($2='failed' OR clock_timestamp()<started_at+interval '270 seconds')", op.ID, state, w.ID)
	if err != nil {
		return nil, err
	}
	if tag.RowsAffected() != 1 {
		return nil, ErrRevision
	}
	if err = tx.Commit(ctx); err != nil {
		return nil, err
	}
	return map[string]any{"run": run, "measurements": rows}, nil
}

func (s *Storage) readAudioDiagnostic(ctx context.Context, id string) (map[string]any, error) {
	doc, err := s.ReadDocument(ctx, id)
	if err != nil {
		return nil, err
	}
	if doc.Kind != "audio-diagnostic-run" {
		return nil, ErrReference
	}
	var run map[string]any
	if err = json.Unmarshal(doc.Payload, &run); err != nil {
		return nil, err
	}
	rows := []any{}
	for _, id := range diagnosticArrayIDs(run["measurement_ids"]) {
		d, err := s.ReadDocument(ctx, id)
		if err != nil {
			return nil, err
		}
		rows = append(rows, json.RawMessage(d.Payload))
	}
	return map[string]any{"run": run, "measurements": rows}, nil
}

func (s *Storage) listAudioDiagnostics(ctx context.Context, caseID, after string) (map[string]any, error) {
	rows, err := s.DB.Query(ctx, `SELECT d.id FROM document d JOIN operation o ON o.result_document_id=d.id WHERE d.kind='audio-diagnostic-run' AND d.payload->>'case_version_id'=$1 AND d.id>$2 ORDER BY d.id LIMIT 21`, caseID, after)
	if err != nil {
		return nil, err
	}
	ids := []string{}
	for rows.Next() {
		var id string
		if err = rows.Scan(&id); err != nil {
			rows.Close()
			return nil, err
		}
		ids = append(ids, id)
	}
	rows.Close()
	if err = rows.Err(); err != nil {
		return nil, err
	}
	var cursor any
	if len(ids) > 20 {
		ids = ids[:20]
		cursor = ids[19]
	}
	out := []any{}
	for _, id := range ids {
		v, err := s.readAudioDiagnostic(ctx, id)
		if err != nil {
			return nil, err
		}
		out = append(out, v)
	}
	return map[string]any{"items": out, "next_cursor": cursor}, nil
}

// Already admitted immutable reports are optional review context. They are not
// native Evidence IDs, new ground-truth observations or primary-score inputs.
func (s *Storage) reviewMeasurements(ctx context.Context, caseID string) ([]any, error) {
	rows, err := s.DB.Query(ctx, `SELECT m.payload FROM document r JOIN operation o ON o.result_document_id=r.id CROSS JOIN LATERAL jsonb_array_elements_text(r.payload->'measurement_ids') x(id) JOIN document m ON m.id=x.id WHERE r.kind='audio-diagnostic-run' AND r.payload->>'case_version_id'=$1 ORDER BY r.id,m.id`, caseID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	out := []any{}
	for rows.Next() {
		var raw []byte
		if err = rows.Scan(&raw); err != nil {
			return nil, err
		}
		out = append(out, json.RawMessage(raw))
	}
	return out, rows.Err()
}
