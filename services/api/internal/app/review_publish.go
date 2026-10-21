package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"time"
)

func acceptedReviewDocument(kind, id string, value any) (DocumentWrite, SavedDocument, error) {
	registry, e := contracts.Registry()
	if e != nil {
		return DocumentWrite{}, SavedDocument{}, e
	}
	raw, _ := lab.Canonical(value)
	c := registry[kind]
	w := DocumentWrite{ID: id, Kind: kind, Version: c.Version, Scope: "local", Payload: raw}
	return w, SavedDocument{ID: id, Kind: kind, Version: c.Version, SchemaSHA: c.SHA, SHA: contracts.Digest(raw), Payload: raw}, nil
}
func reviewReceipts(r ReviewRun) []any {
	ids := []any{}
	for _, stage := range r.Stages {
		for _, id := range stage.Result.ReceiptIDs {
			ids = append(ids, id)
		}
	}
	return ids
}
func (s *Storage) finishReview(ctx context.Context, l reviewLease, r *ReviewRun, f ReviewFrozen, p ReviewProjection, output map[string]any, prepared ReviewedResult) error {
	type row struct {
		w DocumentWrite
		d SavedDocument
	}
	rows := []row{}
	add := func(kind, id string, value any, admitted bool) error {
		var w DocumentWrite
		var d SavedDocument
		var err error
		if admitted {
			w, d, err = acceptedReviewDocument(kind, id, value)
		} else {
			w, d, err = reviewDocument(kind, id, value)
		}
		if err == nil {
			rows = append(rows, row{w, d})
		}
		return err
	}
	recordID := r.AdjudicationID
	resolution := "approve_interpretation"
	if r.Resolution == "key_defect" {
		resolution = "reject_key"
	}
	if r.Resolution == "insufficient_evidence" {
		resolution = "insufficient_evidence"
	}
	unitIDs := []any{}
	for _, v := range f.Key["units"].([]any) {
		unitIDs = append(unitIDs, v.(map[string]any)["id"])
	}
	adjudication := map[string]any{"id": recordID, "case_version_id": f.Key["case_version_id"], "audio_sha256": f.Key["audio"].(map[string]any)["sha256"], "adjudicator_person_id": nil, "qualification_ids": []any{}, "prior_review_decision_ids": []any{}, "unit_ids": unitIDs, "evidence_ids": r.Evidence, "resolution": resolution, "reason": output["reason"], "created_at": time.Now().UTC().Format(time.RFC3339Nano), "origin": "llm", "provider_receipt_ids": reviewReceipts(*r), "input_modality": r.Modality}
	if e := add("adjudication", recordID, adjudication, false); e != nil {
		return e
	}

	contextRecord := map[string]any{"schema_version": "2.0.0", "id": r.ReviewContextID, "case_version_id": f.Key["case_version_id"], "audio_sha256": r.AudioSHA, "person_id": nil, "qualification_ids": []any{}, "author_person_ids": []any{}, "conflicts": []any{}, "prior_key_exposure": true, "other_review_exposure": false, "phase": "final_submitted", "created_at": r.Created, "origin": "llm", "provider_receipt_ids": reviewReceipts(*r), "input_modality": r.Modality}
	if e := add("review-context", r.ReviewContextID, contextRecord, false); e != nil {
		return e
	}
	disposition := "approve"
	if r.Resolution == "key_defect" {
		disposition = "reject"
	}
	if r.Resolution == "insufficient_evidence" {
		disposition = "needs_review"
	}
	decision := map[string]any{"schema_version": "2.0.0", "id": r.ReviewDecisionID, "review_context_id": r.ReviewContextID, "blind_annotation_id": nil, "disclosure_id": nil, "case_version_id": f.Key["case_version_id"], "case_sha256": f.Key["case_sha256"], "audio_sha256": r.AudioSHA, "decision": disposition, "approved_unit_ids": []any{}, "correspondences": []any{}, "rationale_record_ids": []any{}, "reason": output["reason"], "adjudication_id": recordID, "person_id": nil, "submitted_at": time.Now().UTC().Format(time.RFC3339Nano), "origin": "llm", "provider_receipt_ids": reviewReceipts(*r), "input_modality": r.Modality}
	if disposition == "approve" {
		decision["approved_unit_ids"] = unitIDs
	}
	if e := add("review-decision", r.ReviewDecisionID, decision, false); e != nil {
		return e
	}
	if r.Purpose != "case_review" {
		resolution := r.Resolution
		if resolution == "supported" {
			resolution = "original_result_supported"
		}
		dispute := map[string]any{"schema_version": "2.0.0", "id": r.ID, "purpose": r.Purpose, "attempt_id": r.Attempt, "case_version_id": r.Case, "result_id": r.BaseResult, "state": "resolved", "claim_ids": r.Claims, "unit_ids": r.Units, "evidence_ids": r.Evidence, "statement": r.Statement, "resolution": resolution, "resolution_note": output["reason"], "adjudicator_person_id": nil, "new_case_version_id": nil, "unit_correspondence_id": nil, "created_at": r.Created, "resolved_at": time.Now().UTC().Format(time.RFC3339Nano), "revision": r.Revision, "origin": "llm", "provider_receipt_ids": reviewReceipts(*r), "input_modality": r.Modality}
		if r.Attempt == "" {
			dispute["attempt_id"] = nil
			dispute["result_id"] = nil
		}
		if r.NewCase != "" {
			dispute["new_case_version_id"] = r.NewCase
			dispute["unit_correspondence_id"] = r.Correspondence
		}
		if e := add("dispute", r.ID, dispute, false); e != nil {
			return e
		}
	}
	if r.Resolution == "key_defect" {
		if e := add("ground-truth", r.NewCase, p.Key, true); e != nil {
			return e
		}
		if e := add("unit-correspondence", r.Correspondence, p.Correspondence, true); e != nil {
			return e
		}
		for _, v := range p.Rationales {
			if e := add("rationale", v["id"].(string), v, true); e != nil {
				return e
			}
		}
	}
	state, envelope, resultID := prepared.State, prepared.Envelope, prepared.ID
	changed := state != nil
	if changed {
		if e := add("result-envelope", resultID, envelope, false); e != nil {
			return e
		}
		if e := add("interpretation-checkpoint", state.ID, state, false); e != nil {
			return e
		}
	}

	if changed {
		revision := map[string]any{"schema_version": "2.0.0", "id": r.ResultRevisionID, "attempt_id": r.Attempt, "original_result_id": r.BaseResult, "previous_revision_id": nil, "new_result_id": resultID, "dispute_id": r.ID, "unit_correspondence_id": nil, "audio_sha256": r.AudioSHA, "selection_event_id": r.SelectionID, "created_at": time.Now().UTC().Format(time.RFC3339Nano)}
		var previous []byte
		err := s.DB.QueryRow(ctx, "SELECT payload FROM document WHERE kind='result-revision' AND payload->>'new_result_id'=$1 ORDER BY created_at DESC LIMIT 1", r.BaseResult).Scan(&previous)
		if err != nil && err != pgx.ErrNoRows {
			return err
		}
		if err == nil {
			var old map[string]any
			_ = json.Unmarshal(previous, &old)
			revision["previous_revision_id"] = old["id"]
			revision["original_result_id"] = old["original_result_id"]
		}
		if r.Correspondence != "" {
			revision["unit_correspondence_id"] = r.Correspondence
		}
		if e := add("result-revision", r.ResultRevisionID, revision, false); e != nil {
			return e
		}
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	if e = reviewOwned(ctx, tx, l, false); e != nil {
		return e
	}
	if r.Attempt != "" {
		var current string
		var payload []byte
		var revision int64
		e = tx.QueryRow(ctx, "SELECT c.result_id,d.payload,h.revision FROM attempt_context c JOIN entity_head h ON h.id=c.attempt_id JOIN document d ON d.id=h.document_id WHERE c.attempt_id=$1 FOR UPDATE OF c,h", r.Attempt).Scan(&current, &payload, &revision)
		if e != nil {
			return e
		}
		if current != r.BaseResult {
			return ErrRevision
		}
		var a map[string]any
		_ = json.Unmarshal(payload, &a)
		if a["lease_token"] != nil {
			expires, _ := time.Parse(time.RFC3339Nano, a["lease_expires_at"].(string))
			if expires.After(time.Now()) {
				return ErrEvaluationActive
			}
		}
		if changed {
			a["state"] = "completed"
			if state.Status == "review_required" {
				a["state"] = "review_required"
			}
			a["feedback_status"] = "not_started"
			a["revision"] = float64(revision + 1)
			if e = s.writeInterpretationAttempt(ctx, tx, a, revision); e != nil {
				return e
			}
		}
	}
	if r.Resolution == "key_defect" {
		// Every new version is immutable; the unique predecessor edge is the CAS for
		// competing proposals. Descendants can themselves acquire one successor.
		var existing string
		e = tx.QueryRow(ctx, "SELECT new_case_version_id FROM reviewed_case_successor WHERE old_case_version_id=$1", f.Key["case_version_id"]).Scan(&existing)
		if e == nil {
			return ErrRevision
		}
		if e != pgx.ErrNoRows {
			return e
		}
	}
	for _, v := range rows {
		if e = insertDocument(ctx, tx, v.w, v.d); e != nil {
			return e
		}
	}
	if r.Resolution == "key_defect" {
		var source, audio, sha, audioSHA, title, format string
		var count int64
		var flags []byte
		e = tx.QueryRow(ctx, "SELECT l.source_key_id,l.audio_asset_id,l.case_sha256,l.audio_sha256,l.sample_count,l.task_components,c.title,c.format FROM listening_case l JOIN exercise_catalog c ON c.id::text=l.case_version_id WHERE l.case_version_id=$1", f.Key["case_version_id"]).Scan(&source, &audio, &sha, &audioSHA, &count, &flags, &title, &format)
		if e != nil {
			return e
		}
		_, e = tx.Exec(ctx, "INSERT INTO listening_case(case_version_id,source_key_id,audio_asset_id,case_sha256,audio_sha256,sample_count,task_components) VALUES($1,$1,$2,$3,$4,$5,$6)", r.NewCase, audio, p.Key["case_sha256"], audioSHA, count, flags)
		if e != nil {
			return e
		}
		_, e = tx.Exec(ctx, "INSERT INTO exercise_catalog(id,title,published_at,source_revision,audio_sha256,public_context,duration_ms,format,difficulty,availability) SELECT $2::uuid,title,clock_timestamp(),$2::text,audio_sha256,public_context,duration_ms,format,'unrated',CASE WHEN availability='rights_restricted' THEN 'rights_restricted' ELSE 'published' END FROM exercise_catalog WHERE id::text=$1", f.Key["case_version_id"], r.NewCase)
		if e != nil {
			return e
		}
		_, e = tx.Exec(ctx, "INSERT INTO reviewed_case_successor(old_case_version_id,new_case_version_id,review_id,correspondence_id) VALUES($1,$2,$3,$4)", f.Key["case_version_id"], r.NewCase, r.ID, r.Correspondence)
		if e != nil {
			return e
		}
		if e = s.advanceReviewCaseHead(ctx, tx, source, f.Key["case_version_id"].(string), r.NewCase); e != nil {
			return e
		}
		// Existing attempts keep access; only new selection moves to the successor.
		_, e = tx.Exec(ctx, "UPDATE exercise_catalog SET availability='retired' WHERE id::text=$1 AND availability<>'rights_restricted'", f.Key["case_version_id"])
		if e != nil {
			return e
		}
	}
	if changed {
		_, e = tx.Exec(ctx, "UPDATE attempt_context SET result_id=$2 WHERE attempt_id=$1", r.Attempt, resultID)
		if e != nil {
			return e
		}
		_, e = tx.Exec(ctx, "UPDATE interpretation_checkpoint SET document_id=$2,operation_id=$3,epoch=$4,deadline_at=clock_timestamp() WHERE attempt_id=$1", r.Attempt, state.ID, l.Operation, l.Epoch)
		if e != nil {
			return e
		}
	}
	if changed || r.Resolution == "key_defect" {
		selection := map[string]any{"id": r.SelectionID, "review_id": r.ID, "operation_id": l.Operation, "previous_case_version_id": f.Key["case_version_id"], "new_case_version_id": r.NewCase, "attempt_id": r.Attempt, "previous_result_id": r.BaseResult, "new_result_id": resultID}
		_, e = tx.Exec(ctx, "INSERT INTO audit_event(workspace_id,operation_id,action,event_sha256,event_payload) VALUES('local',$1,'review.selection',$2,$3)", l.Operation, lab.Hash(selection), reviewBytes(selection))
		if e != nil {
			return e
		}
	}
	final := *r
	final.Status = "complete"
	final.Failure = ""
	final.NewResult = resultID
	if e = writeReviewCheckpoint(ctx, tx, &final); e != nil {
		return e
	}
	_, e = tx.Exec(ctx, "UPDATE operation SET state='complete',finished_at=clock_timestamp(),result_document_id=$2 WHERE id=$1", l.Operation, recordID)
	if e != nil {
		return e
	}
	if e = tx.Commit(ctx); e != nil {
		return e
	}
	*r = final
	return nil
}

// Advance an existing generated-case head, when one exists. Source-imported
// playable versions may have no preparation head; their catalog successor is real.
func (s *Storage) advanceReviewCaseHead(ctx context.Context, tx pgx.Tx, source, old, next string) error {
	var raw []byte
	var id string
	var revision int64
	e := tx.QueryRow(ctx, `SELECT h.id,h.revision,d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.kind='case-head' AND (d.payload->>'ground_truth_id'=$1 OR d.payload->>'ground_truth_id'=$2) FOR UPDATE OF h`, source, old).Scan(&id, &revision, &raw)
	if e == pgx.ErrNoRows {
		return nil
	}
	if e != nil {
		return e
	}
	var head map[string]any
	_ = json.Unmarshal(raw, &head)
	head["revision"] = float64(revision + 1)
	head["parent_case_version_id"] = old
	head["ground_truth_id"] = next
	w, d, e := acceptedReviewDocument("case-head", uuid.NewString(), head)
	if e != nil {
		return e
	}
	w.Head = &HeadWrite{ID: id, Expected: &revision, State: "published"}
	return insertDocument(ctx, tx, w, d)
}
