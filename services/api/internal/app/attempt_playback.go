package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/lab"
)

func (s *Storage) RecordPlayback(ctx context.Context, id, key string, raw []byte) (map[string]any, error) {
	input, raw, e := attemptInput("play-event-request", raw)
	if e != nil {
		return nil, e
	}
	if input["attempt_id"] != id {
		return nil, ErrInput
	}
	request := OperationRequest{Name: "play_event", Key: key, Path: "/api/v1/attempts/" + id + "/playback", Body: raw}
	digest, e := operationDigest(request)
	if e != nil {
		return nil, ErrInput
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return nil, e
	}
	defer tx.Rollback(context.Background())
	op, _, e := reserveOperation(ctx, tx, request, digest)
	if e != nil {
		return nil, e
	}
	var revision int64
	finish := func(event string) (map[string]any, error) {
		if _, e = tx.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2,result_document_id=$3,finished_at=clock_timestamp() WHERE id=$1", op.ID, id, event); e != nil {
			return nil, e
		}
		return map[string]any{"operation_id": op.ID, "state": "complete", "subject": map[string]any{"kind": "attempt", "id": id, "version_id": nil}, "revision": revision, "artifact_ids": []any{event}, "issue_ids": []any{}}, tx.Commit(ctx)
	}
	if op.Result != nil {
		if e = tx.QueryRow(ctx, "SELECT attempt_revision FROM playback_index WHERE event_id=$1", *op.Result).Scan(&revision); e != nil {
			return nil, e
		}
		return finish(*op.Result)
	}
	var initialSHA, audioSHA string
	var count int64
	if e = tx.QueryRow(ctx, `SELECT d.payload_sha256,l.audio_sha256,l.sample_count,h.revision FROM attempt_context c JOIN entity_head h ON h.id=c.attempt_id JOIN listening_case l ON l.case_version_id=c.case_version_id JOIN document d ON d.id=c.attempt_id WHERE c.attempt_id=$1`, id).Scan(&initialSHA, &audioSHA, &count, &revision); e != nil {
		return nil, e
	}
	if input["audio_sha256"] != audioSHA || input["position_sample"].(float64) > float64(count) {
		return nil, ErrInput
	}
	page := input["page_instance_id"].(string)
	sequence := int64(input["client_sequence"].(float64))
	if _, e = tx.Exec(ctx, "SELECT pg_advisory_xact_lock(hashtextextended($1,79004755))", id+":"+page); e != nil {
		return nil, e
	}
	var previous []byte
	var eventID string
	e = tx.QueryRow(ctx, "SELECT d.id,d.payload,p.attempt_revision FROM playback_index p JOIN document d ON d.id=p.event_id WHERE p.attempt_id=$1 AND p.page_instance_id=$2 AND p.event_sequence=$3", id, page, sequence).Scan(&eventID, &previous, &revision)
	if e == nil {
		var stored map[string]any
		_ = json.Unmarshal(previous, &stored)
		delete(stored, "id")
		delete(stored, "received_at")
		if lab.Hash(stored) != lab.Hash(input) {
			return nil, ErrConflict
		}
		return finish(eventID)
	}
	if e != pgx.ErrNoRows {
		return nil, e
	}
	var max int64
	if e = tx.QueryRow(ctx, "SELECT coalesce(max(event_sequence),-1) FROM playback_index WHERE attempt_id=$1 AND page_instance_id=$2", id, page).Scan(&max); e != nil {
		return nil, e
	}
	if sequence <= max {
		return nil, ErrConflict
	}
	if e = retainAttemptRequest(ctx, tx, "play-event-request", raw, op.ID); e != nil {
		return nil, e
	}
	var at string
	if e = tx.QueryRow(ctx, "SELECT to_char(clock_timestamp() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.US\"Z\"')").Scan(&at); e != nil {
		return nil, e
	}
	eventID = uuid.NewString()
	input["id"] = eventID
	input["received_at"] = at
	payload, _ := lab.Canonical(input)
	w := DocumentWrite{ID: eventID, Kind: "playback-event", Version: "2.0.0", Scope: "local", Payload: payload, References: []Reference{{Pointer: "/attempt_id", ID: id, Scope: "local", Kind: "attempt", SHA: initialSHA, Relation: "attempt"}}}
	d, e := validateDocument(w)
	if e != nil {
		return nil, e
	}
	if e = insertDocument(ctx, tx, w, d); e != nil {
		return nil, e
	}
	if _, e = tx.Exec(ctx, "INSERT INTO playback_index(event_id,attempt_id,page_instance_id,event_sequence,received_at,attempt_revision) VALUES($1,$2,$3,$4,$5,$6)", eventID, id, page, sequence, at, revision); e != nil {
		return nil, e
	}
	return finish(eventID)
}
