package app

// PostgreSQL owns atomic attempt snapshots, revision transitions and operation replay.
import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

type AttemptRecord struct{ Attempt, Context map[string]any }

func readAttemptPayload(ctx context.Context, q interface {
	QueryRow(context.Context, string, ...any) pgx.Row
}, id string) (map[string]any, error) {
	var raw []byte
	e := q.QueryRow(ctx, "SELECT payload FROM document WHERE id=$1 AND kind='attempt'", id).Scan(&raw)
	if e != nil {
		return nil, e
	}
	var a map[string]any
	e = json.Unmarshal(raw, &a)
	return a, e
}
func (s *Storage) Attempt(ctx context.Context, id string) (AttemptRecord, error) {
	var a, c []byte
	e := s.DB.QueryRow(ctx, `SELECT d.payload,jsonb_build_object('case_item',c.case_item,'configuration',c.configuration,'prompt_bundle',c.prompt_bundle,'evaluator_bindings',c.evaluator_bindings,'requested_language',c.requested_language,'audio_asset_id',l.audio_asset_id,'audio_sha256',l.audio_sha256,'sample_count',l.sample_count,'result_id',c.result_id) FROM entity_head h JOIN document d ON d.id=h.document_id JOIN attempt_context c ON c.attempt_id=h.id JOIN listening_case l ON l.case_version_id=c.case_version_id WHERE h.id=$1 AND h.kind='attempt'`, id).Scan(&a, &c)
	if e != nil {
		return AttemptRecord{}, e
	}
	r := AttemptRecord{}
	_ = json.Unmarshal(a, &r.Attempt)
	e = json.Unmarshal(c, &r.Context)
	return r, e
}
func attemptWrite(a map[string]any, id string, expected *int64, caseSHA, initialSHA string) DocumentWrite {
	raw, _ := lab.Canonical(a)
	attempt := a["attempt_id"].(string)
	if expected == nil {
		initialSHA = contracts.Digest(raw)
	}
	return DocumentWrite{ID: id, Kind: "attempt", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: attempt, Expected: expected, State: a["state"].(string)}, References: []Reference{{Pointer: "/attempt_id", ID: attempt, Scope: "local", Kind: "attempt", SHA: initialSHA, Relation: "attempt"}, {Pointer: "/case_version_id", ID: a["case_version_id"].(string), Scope: "local", Kind: "ground-truth", SHA: caseSHA, Relation: "case-version"}}}
}
func configurationInTransaction(ctx context.Context, tx pgx.Tx) (map[string]any, lab.Bundle, []any, error) {
	var raw []byte
	c := DefaultConfiguration()
	bundle := lab.Shipped()
	e := tx.QueryRow(ctx, "SELECT d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id='local-configuration' FOR SHARE OF h").Scan(&raw)
	if e != nil && e != pgx.ErrNoRows {
		return nil, bundle, nil, e
	}
	if e == nil {
		_ = json.Unmarshal(raw, &c)
	}
	if id, ok := c["active_prompt_bundle_id"].(string); ok {
		if e = tx.QueryRow(ctx, "SELECT payload FROM document WHERE id=$1 AND kind='prompt-bundle'", id).Scan(&raw); e != nil {
			return nil, bundle, nil, e
		}
		if e = json.Unmarshal(raw, &bundle); e != nil {
			return nil, bundle, nil, e
		}
	}
	// Configuration/profile-role references were admitted by PutConfiguration.
	// Select trusted snapshots here rather than repeat its whole-profile validation.
	profilesRaw, _ := json.Marshal(c["llm_profiles"])
	var profiles []provider.Profile
	_ = json.Unmarshal(profilesRaw, &profiles)
	bindings := []any{}
	for _, role := range []string{"blind_claim_extraction", "claim_mapping", "mapping_audit", "feedback", "adjudication"} {
		selected := c["llm_profile"].(string)
		if override, ok := c["stage_profiles"].(map[string]any)[role].(string); ok {
			selected = override
		}
		var p provider.Profile
		for _, profile := range profiles {
			if profile.ID == selected {
				p = profile
				break
			}
		}
		if p.ID == "" {
			return nil, bundle, nil, ErrReference
		}
		if p.Model == "unselected" {
			return nil, bundle, nil, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
		}
		if e = provider.Included(p); e != nil {
			return nil, bundle, nil, e
		}
		for _, binding := range bundle.Bindings {
			if binding.Stage == role {
				bindings = append(bindings, map[string]any{"stage": role, "profile": p, "prompt_binding": binding, "prompt_bundle_sha256": bundle.SHA})
			}
		}
	}
	return c, bundle, bindings, nil
}
func (s *Storage) StartAttempt(ctx context.Context, raw []byte, key string) (map[string]any, error) {
	input, raw, e := attemptInput("attempt-start-request", raw)
	if e != nil {
		return nil, e
	}
	request := OperationRequest{Name: "start_attempt", Key: key, Path: "/api/v1/attempts", Body: raw}
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
	if op.Result != nil {
		a, e := readAttemptPayload(ctx, tx, *op.Result)
		if e != nil {
			return nil, e
		}
		var item []byte
		if e = tx.QueryRow(ctx, "SELECT case_item FROM attempt_context WHERE attempt_id=$1", a["attempt_id"]).Scan(&item); e != nil {
			return nil, e
		}
		var view map[string]any
		_ = json.Unmarshal(item, &view)
		return teacherStartView(a, map[string]any{"case_item": view, "requested_language": input["requested_language"]}), tx.Commit(ctx)
	}
	var item, flags []byte
	var audioSHA, casePayloadSHA string
	e = tx.QueryRow(ctx, `SELECT jsonb_build_object('id',c.id,'title',c.title,'public_context',c.public_context,'duration_ms',c.duration_ms,'format',c.format,'difficulty',c.difficulty,'availability',c.availability,'case_sha256',l.case_sha256),l.task_components,l.audio_sha256,d.payload_sha256 FROM exercise_catalog c JOIN listening_case l ON l.case_version_id=c.id::text JOIN document d ON d.id=l.case_version_id JOIN asset_location a ON a.asset_id=l.audio_asset_id WHERE c.id::text=$1 AND c.availability='published' AND l.case_sha256=$2 AND a.state='linked' FOR SHARE OF c`, input["case_version_id"], input["case_sha256"]).Scan(&item, &flags, &audioSHA, &casePayloadSHA)
	if e == pgx.ErrNoRows {
		return nil, ErrCaseUnavailable
	}
	if e != nil {
		return nil, e
	}
	if e = retainAttemptRequest(ctx, tx, "attempt-start-request", raw, op.ID); e != nil {
		return nil, e
	}
	configuration, bundle, bindings, e := configurationInTransaction(ctx, tx)
	if e != nil {
		return nil, e
	}
	var at string
	if e = tx.QueryRow(ctx, "SELECT to_char(clock_timestamp() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.US\"Z\"')").Scan(&at); e != nil {
		return nil, e
	}
	id := uuid.NewString()
	var components, itemValue map[string]any
	_ = json.Unmarshal(flags, &components)
	_ = json.Unmarshal(item, &itemValue)
	a := map[string]any{"schema_version": "2.0.0", "attempt_id": id, "case_version_id": input["case_version_id"], "case_sha256": input["case_sha256"], "answer_text": "", "answer_utf8_sha256": contracts.Digest(nil), "task_components": components, "evaluation_policy_version": "answer-components-v2", "scoring_policy_version": "2.0.0", "state": "started", "revision": float64(0), "submitted_at": nil, "idempotency_key": key, "lease_token": nil, "lease_expires_at": nil, "workspace_id": "local", "started_at": at, "lease_epoch": 0, "audio_sha256": audioSHA, "configuration_sha256": configuration["configuration_sha256"], "feedback_status": "not_started"}
	w := attemptWrite(a, id, nil, casePayloadSHA, "")
	d, e := validateDocument(w)
	if e != nil {
		return nil, e
	}
	if e = insertDocument(ctx, tx, w, d); e != nil {
		return nil, e
	}
	cfg, _ := json.Marshal(configuration)
	pb, _ := json.Marshal(bundle)
	bs, _ := json.Marshal(bindings)
	if _, e = tx.Exec(ctx, "INSERT INTO attempt_context(attempt_id,case_version_id,case_item,configuration,prompt_bundle,evaluator_bindings,requested_language) VALUES($1,$2,$3,$4,$5,$6,$7)", id, input["case_version_id"], item, cfg, pb, bs, input["requested_language"]); e != nil {
		return nil, e
	}
	if _, e = tx.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2,result_document_id=$2,finished_at=clock_timestamp() WHERE id=$1", op.ID, id); e != nil {
		return nil, e
	}
	return teacherStartView(a, map[string]any{"case_item": itemValue, "requested_language": input["requested_language"]}), tx.Commit(ctx)
}
func (s *Storage) WriteAnswer(ctx context.Context, id, key string, revision int64, raw []byte, submit bool) (map[string]any, string, error) {
	input, raw, e := attemptInput("answer-write", raw)
	if e != nil {
		return nil, "", e
	}
	name, path := "draft_answer", "/api/v1/attempts/"+id+"/answer"
	if submit {
		name = "submit_answer"
		path = "/api/v1/attempts/" + id + ":submit"
	}
	request := OperationRequest{Name: name, Path: path, Key: key, Revision: &revision, Body: raw}
	digest, e := operationDigest(request)
	if e != nil {
		return nil, "", ErrInput
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return nil, "", e
	}
	defer tx.Rollback(context.Background())
	op, _, e := reserveOperation(ctx, tx, request, digest)
	if e != nil {
		return nil, "", e
	}
	if op.Result != nil {
		a, e := readAttemptPayload(ctx, tx, *op.Result)
		if e != nil {
			return nil, "", e
		}
		return a, op.ID, tx.Commit(ctx)
	}
	var docID, initialSHA, caseSHA, at string
	var current int64
	e = tx.QueryRow(ctx, "SELECT document_id,revision FROM entity_head WHERE id=$1 AND kind='attempt' FOR UPDATE", id).Scan(&docID, &current)
	if e != nil {
		return nil, "", e
	}
	if current != revision {
		return nil, "", ErrRevision
	}
	a, e := readAttemptPayload(ctx, tx, docID)
	if e != nil {
		return nil, "", e
	}
	if a["state"] != "started" {
		return nil, "", ErrAttemptState
	}
	if e = tx.QueryRow(ctx, "SELECT d.payload_sha256,c.payload_sha256,to_char(clock_timestamp() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.US\"Z\"') FROM document d JOIN document c ON c.id=$2 WHERE d.id=$1", id, a["case_version_id"]).Scan(&initialSHA, &caseSHA, &at); e != nil {
		return nil, "", e
	}
	if e = retainAttemptRequest(ctx, tx, "answer-write", raw, op.ID); e != nil {
		return nil, "", e
	}
	next := frozenAnswer(a, input, key, at, submit)
	w := attemptWrite(next, uuid.NewString(), &revision, caseSHA, initialSHA)
	d, e := validateDocument(w)
	if e != nil {
		return nil, "", e
	}
	if e = insertDocument(ctx, tx, w, d); e != nil {
		return nil, "", e
	}
	if _, e = tx.Exec(ctx, "UPDATE attempt_context SET requested_language=$2 WHERE attempt_id=$1", id, input["requested_language"]); e != nil {
		return nil, "", e
	}
	if _, e = tx.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2,result_document_id=$3,finished_at=clock_timestamp() WHERE id=$1", op.ID, id, w.ID); e != nil {
		return nil, "", e
	}
	return next, op.ID, tx.Commit(ctx)
}

// The canonical request was admitted at the transport/domain boundary already.
// Retain its exact content/language with the operation, without revalidating it.
func retainAttemptRequest(ctx context.Context, tx pgx.Tx, kind string, raw []byte, operation string) error {
	registry, e := contracts.Registry()
	if e != nil {
		return e
	}
	c := registry[kind]
	id := uuid.NewString()
	w := DocumentWrite{ID: id, Kind: kind, Version: c.Version, Scope: "local", Payload: raw}
	d := SavedDocument{ID: id, Kind: kind, Version: c.Version, SchemaSHA: c.SHA, SHA: contracts.Digest(raw), Payload: raw}
	if e = insertDocument(ctx, tx, w, d); e != nil {
		return e
	}
	_, e = tx.Exec(ctx, "UPDATE operation SET input_document_id=$2 WHERE id=$1", operation, id)
	return e
}
