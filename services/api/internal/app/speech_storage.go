package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

func (s *Storage) ensureSpeechCase(ctx context.Context, plan map[string]any, candidate string) error {
	id := plan["case_version_id"].(string)
	var present bool
	if e := s.DB.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM entity_head WHERE id=$1 AND kind='case-head')", id).Scan(&present); e != nil {
		return e
	}
	if present {
		return nil
	}
	d, e := s.ReadDocument(ctx, candidate)
	if e != nil {
		return e
	}
	raw, _ := lab.Canonical(map[string]any{"id": id, "revision": 0, "status": "draft", "candidate_id": candidate, "parent_case_version_id": nil, "ground_truth_id": nil, "delivery_asset_id": nil, "created_at": time.Now().UTC().Format(time.RFC3339Nano), "quarantine_open": false})
	_, e = s.WriteDocuments(ctx, []DocumentWrite{{ID: uuid.NewString(), Kind: "case-head", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: id, State: "draft"}, References: []Reference{{Pointer: "/candidate_id", ID: candidate, Scope: "local", Kind: "candidate-envelope", SHA: d.SHA, Relation: "candidate_id"}}}})
	return e
}

func (s *Storage) finishSpeechCase(ctx context.Context, tx pgx.Tx, p map[string]any) error {
	raw, e := s.ReadAsset(ctx, p["render_plan_asset_id"].(string))
	if e != nil {
		return e
	}
	var frozen map[string]any
	if e = json.Unmarshal(raw, &frozen); e != nil {
		return e
	}
	id := frozen["plan"].(map[string]any)["case_version_id"]
	var current []byte
	var revision int64
	if e = tx.QueryRow(ctx, "SELECT d.payload,h.revision FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id=$1 AND h.kind='case-head' FOR UPDATE OF h", id).Scan(&current, &revision); e != nil {
		return e
	}
	var head map[string]any
	if e = json.Unmarshal(current, &head); e != nil {
		return e
	}
	head["revision"] = float64(revision + 1)
	head["status"] = "rendered"
	head["delivery_asset_id"] = p["audio_asset_id"]
	head["ground_truth_id"] = p["key_id"]
	raw, _ = lab.Canonical(head)
	write := DocumentWrite{ID: uuid.NewString(), Kind: "case-head", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: id.(string), Expected: &revision, State: "rendered"}}
	var sha string
	if e = tx.QueryRow(ctx, "SELECT payload_sha256 FROM document WHERE id=$1", head["candidate_id"]).Scan(&sha); e != nil {
		return e
	}
	write.References = append(write.References, Reference{Pointer: "/candidate_id", ID: head["candidate_id"].(string), Scope: "local", Kind: "candidate-envelope", SHA: sha, Relation: "candidate_id"})
	if e = tx.QueryRow(ctx, "SELECT payload_sha256 FROM document WHERE id=$1", p["key_id"]).Scan(&sha); e != nil {
		return e
	}
	write.References = append(write.References, Reference{Pointer: "/ground_truth_id", ID: p["key_id"].(string), Scope: "local", Kind: "ground-truth", SHA: sha, Relation: "key"})
	ref, e := s.assetByteReference(ctx, p["audio_asset_id"].(string), "/delivery_asset_id", "audio")
	if e != nil {
		return e
	}
	write.References = append(write.References, ref)
	saved, e := validateDocument(write)
	if e != nil {
		return e
	}
	if e = insertDocument(ctx, tx, write, saved); e != nil {
		return e
	}
	return validateGraph(ctx, tx, write.ID)
}

func (s *Storage) completedSpeechPiece(ctx context.Context, piece string) (map[string]any, string, error) {
	var raw []byte
	var receipt string
	e := s.DB.QueryRow(ctx, "SELECT d.payload,d.id FROM operation o JOIN document d ON d.id=o.result_document_id WHERE o.operation_name='speech-inference' AND o.subject_id=$1 AND o.state='complete' ORDER BY o.started_at DESC LIMIT 1", piece).Scan(&raw, &receipt)
	if e == pgx.ErrNoRows {
		return nil, "", nil
	}
	if e != nil {
		return nil, "", e
	}
	var native map[string]any
	if e = json.Unmarshal(raw, &native); e != nil {
		return nil, "", e
	}
	raw, e = s.ReadAsset(ctx, native["wire_response_asset_id"].(string))
	if e != nil {
		return nil, "", e
	}
	var result map[string]any
	e = json.Unmarshal(raw, &result)
	return result, receipt, e
}

func (s *Storage) speechActionResult(ctx context.Context, operation string) (map[string]any, error) {
	var id string
	if e := s.DB.QueryRow(ctx, "SELECT result_document_id FROM operation WHERE id=$1", operation).Scan(&id); e != nil {
		return nil, e
	}
	d, e := s.ReadDocument(ctx, id)
	if e != nil {
		return nil, e
	}
	var p map[string]any
	e = json.Unmarshal(d.Payload, &p)
	return p, e
}
func (s *Storage) acknowledgeSpeech(ctx context.Context, operation, preparation string) error {
	_, e := s.DB.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2::text,result_document_id=(SELECT document_id FROM entity_head WHERE id=$2::text),finished_at=clock_timestamp() WHERE id=$1 AND state='reserved'", operation, preparation)
	return e
}
func (s *Storage) speechAttemptCount(ctx context.Context, preparation string) (int, error) {
	var count int
	e := s.DB.QueryRow(ctx, "SELECT count(*) FROM operation WHERE operation_name='speech_render' AND subject_id=$1", preparation).Scan(&count)
	return count, e
}
func (s *Storage) claimSpeech(ctx context.Context, operation, preparation string) error {
	tag, e := s.DB.Exec(ctx, "UPDATE operation SET state='running',subject_id=$2 WHERE id=$1 AND state='reserved'", operation, preparation)
	if e != nil {
		return e
	}
	if tag.RowsAffected() != 1 {
		return &provider.Failure{Code: "LEASE_ACTIVE"}
	}
	return nil
}
func (s *Storage) releaseSpeech(ctx context.Context, operation string) {
	_, _ = s.DB.Exec(ctx, "UPDATE operation SET state='interrupted',finished_at=clock_timestamp() WHERE id=$1 AND state='running'", operation)
}
func (s *Storage) startSpeechPiece(ctx context.Context, operation, piece string) error {
	_, e := s.DB.Exec(ctx, "UPDATE operation SET state='running',subject_id=$2 WHERE id=$1 AND state='reserved'", operation, piece)
	return e
}
func (s *Storage) finishSpeechPiece(ctx context.Context, operation, state, receipt string) error {
	_, e := s.DB.Exec(ctx, "UPDATE operation SET state=$2,result_document_id=$3,finished_at=clock_timestamp() WHERE id=$1", operation, state, receipt)
	return e
}
