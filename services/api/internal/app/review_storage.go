package app

// Storage owns foreground leases and atomic pointer publication. Model calls and
// linguistic decisions live in the controller and admission owners.
import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"time"
)

func (s *Storage) Review(ctx context.Context, id string) (ReviewRun, error) {
	var raw []byte
	var r ReviewRun
	e := s.DB.QueryRow(ctx, "SELECT payload FROM review_checkpoint WHERE id=$1", id).Scan(&raw)
	if e == nil {
		e = json.Unmarshal(raw, &r)
	}
	return r, e
}
func (s *Storage) createReview(ctx context.Context, r ReviewRun, key string, f ReviewFrozen) (ReviewRun, error) {
	raw := reviewBytes(map[string]any{"purpose": r.Purpose, "case_version_id": r.Case, "audio_sha256": r.AudioSHA, "attempt_id": r.Attempt, "target_case_version_id": r.TargetCase, "result_id": r.BaseResult, "statement": r.Statement, "claim_ids": r.Claims, "unit_ids": r.Units, "evidence_ids": r.Evidence})
	request := OperationRequest{Name: "create_review", Key: key, Path: "/api/v1/reviews", Body: raw}
	digest, e := operationDigest(request)
	if e != nil {
		return r, ErrInput
	}
	frozen, e := s.interpretationJSON(ctx, f)
	if e != nil {
		return r, e
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return r, e
	}
	defer tx.Rollback(context.Background())
	op, newly, e := reserveOperation(ctx, tx, request, digest)
	if e != nil {
		return r, e
	}
	if !newly {
		var id string
		e = tx.QueryRow(ctx, "SELECT subject_id FROM operation WHERE id=$1", op.ID).Scan(&id)
		if e != nil {
			return r, e
		}
		if e = tx.Commit(ctx); e != nil {
			return r, e
		}
		return s.Review(ctx, id)
	}
	r.Modality = "text"
	if len(f.Resources.Evidence) > 0 {
		r.Modality = "text_with_speech_evidence"
	}
	r.ID = uuid.NewString()
	r.ReviewContextID = uuid.NewString()
	r.ReviewDecisionID = uuid.NewString()
	r.AdjudicationID = uuid.NewString()
	r.ResultRevisionID = uuid.NewString()
	r.SelectionID = uuid.NewString()
	r.Frozen = frozen
	r.Case = f.Key["case_version_id"].(string)
	if r.TargetCase != "" {
		r.NewCase = r.TargetCase
		r.Correspondence = f.Correspondences[0].(map[string]any)["id"].(string)
	}
	r.AudioSHA = f.Key["audio"].(map[string]any)["sha256"].(string)
	r.Status = "ready"
	r.Created = time.Now().UTC().Format(time.RFC3339Nano)
	r.Stages = []InterpretationStage{}
	var attempt any
	if r.Attempt != "" {
		attempt = r.Attempt
	}
	_, e = tx.Exec(ctx, "INSERT INTO review_checkpoint(id,case_version_id,attempt_id,revision,payload) VALUES($1,$2,$3,0,$4)", r.ID, r.Case, attempt, reviewBytes(r))
	if e != nil {
		return r, e
	}
	_, e = tx.Exec(ctx, "INSERT INTO review_event(review_id,revision,payload) VALUES($1,0,$2)", r.ID, reviewBytes(r))
	if e != nil {
		return r, e
	}
	_, e = tx.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2,finished_at=clock_timestamp() WHERE id=$1", op.ID, r.ID)
	if e != nil {
		return r, e
	}
	return r, tx.Commit(ctx)
}
func (s *Storage) acquireReview(ctx context.Context, id, key string, revision int64) (reviewLease, error) {
	lease := reviewLease{}
	request := OperationRequest{Name: "run_review", Key: key, Path: "/api/v1/reviews/" + id + ":run", Revision: &revision, Body: json.RawMessage(`{}`)}
	digest, e := operationDigest(request)
	if e != nil {
		return lease, ErrInput
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return lease, e
	}
	defer tx.Rollback(context.Background())
	op, newly, e := reserveOperation(ctx, tx, request, digest)
	if e != nil {
		return lease, e
	}
	var raw []byte
	var current, epoch int64
	var live bool
	e = tx.QueryRow(ctx, "SELECT payload,revision,epoch,coalesce(clock_timestamp()<deadline_at,false) FROM review_checkpoint WHERE id=$1 FOR UPDATE", id).Scan(&raw, &current, &epoch, &live)
	if e != nil {
		return lease, e
	}
	if e = json.Unmarshal(raw, &lease.Run); e != nil {
		return lease, e
	}
	lease.Operation = op.ID
	if !newly {
		lease.Replay = true
		return lease, tx.Commit(ctx)
	}
	if lease.Run.Status == "complete" {
		lease.Replay = true
		_, e = tx.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2,finished_at=clock_timestamp() WHERE id=$1", op.ID, id)
		if e != nil {
			return lease, e
		}
		return lease, tx.Commit(ctx)
	}
	if lease.Run.Status == "running" && live {
		return lease, ErrEvaluationActive
	}
	if current != revision {
		return lease, ErrRevision
	}
	lease.Epoch = epoch + 1
	lease.Run.Revision++
	lease.Run.Status = "running"
	lease.Run.Failure = ""
	_, e = tx.Exec(ctx, "UPDATE review_checkpoint SET operation_id=$2,epoch=$3,deadline_at=clock_timestamp()+interval '270 seconds',revision=$4,payload=$5 WHERE id=$1", id, op.ID, lease.Epoch, lease.Run.Revision, reviewBytes(lease.Run))
	if e != nil {
		return lease, e
	}
	_, e = tx.Exec(ctx, "INSERT INTO review_event(review_id,revision,payload) VALUES($1,$2,$3)", id, lease.Run.Revision, reviewBytes(lease.Run))
	if e != nil {
		return lease, e
	}
	_, e = tx.Exec(ctx, "UPDATE operation SET state='running',subject_id=$2 WHERE id=$1", op.ID, id)
	if e != nil {
		return lease, e
	}
	return lease, tx.Commit(ctx)
}
func reviewOwned(ctx context.Context, tx pgx.Tx, l reviewLease, lateFailure bool) error {
	var epoch int64
	var live bool
	var operation string
	e := tx.QueryRow(ctx, "SELECT epoch,operation_id,clock_timestamp()<deadline_at FROM review_checkpoint WHERE id=$1 FOR UPDATE", l.Run.ID).Scan(&epoch, &operation, &live)
	if e != nil {
		return e
	}
	if epoch != l.Epoch || operation != l.Operation || (!live && !lateFailure) {
		return ErrEvaluationLease
	}
	return nil
}
func writeReviewCheckpoint(ctx context.Context, tx pgx.Tx, r *ReviewRun) error {
	r.Revision++
	_, e := tx.Exec(ctx, "UPDATE review_checkpoint SET revision=$2,payload=$3 WHERE id=$1", r.ID, r.Revision, reviewBytes(r))
	if e != nil {
		return e
	}
	_, e = tx.Exec(ctx, "INSERT INTO review_event(review_id,revision,payload) VALUES($1,$2,$3)", r.ID, r.Revision, reviewBytes(r))
	return e
}
func (s *Storage) checkpointReview(ctx context.Context, l reviewLease, r *ReviewRun, finish bool) error {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	if e = reviewOwned(ctx, tx, l, finish && r.Status == "failed"); e != nil {
		return e
	}
	if e = writeReviewCheckpoint(ctx, tx, r); e != nil {
		return e
	}
	if finish {
		state := "complete"
		if r.Status == "failed" {
			state = "failed"
		}
		_, e = tx.Exec(ctx, "UPDATE operation SET state=$2,finished_at=clock_timestamp() WHERE id=$1", l.Operation, state)
		if e != nil {
			return e
		}
	}
	return tx.Commit(ctx)
}

// Newly generated domain documents are admitted once here. Foreign owners are
// already selected by the transaction; no stored-data/schema-byte requalification.
func reviewDocument(kind, id string, value any) (DocumentWrite, SavedDocument, error) {
	c, raw, e := contracts.Validate(kind, "2.0.0", reviewBytes(value))
	w := DocumentWrite{ID: id, Kind: kind, Version: "2.0.0", Scope: "local", Payload: raw}
	if e != nil {
		return w, SavedDocument{}, e
	}
	return w, SavedDocument{ID: id, Kind: kind, Version: w.Version, SchemaSHA: c.SHA, SHA: contracts.Digest(raw), Payload: raw}, nil
}

// A current source-use restriction is activity state, not saved-data/schema
// requalification. Check once before a foreground operation transfers its input.
func (s *Storage) reviewSourceAllowed(ctx context.Context, caseID string) error {
	var availability string
	e := s.DB.QueryRow(ctx, "SELECT availability FROM exercise_catalog WHERE id::text=$1", caseID).Scan(&availability)
	if e == pgx.ErrNoRows {
		return nil
	}
	if e != nil {
		return e
	}
	if availability == "rights_restricted" {
		return ErrAttemptRights
	}
	return nil
}
