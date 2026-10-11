package app

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"io"
	"net/http"
	"strconv"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

// Blueprint content is an accepted private typed JSON asset. Its logical ID is
// indexed by the immutable write operation; readback trusts the saved content.
func (s *Storage) WriteBlueprint(ctx context.Context, raw []byte, key string) (map[string]any, error) {
	_, accepted, e := contracts.Validate("blueprint-write", "2.0.0", raw)
	if e != nil {
		return nil, &provider.Failure{Code: "SCHEMA_INVALID"}
	}
	raw = accepted
	request := OperationRequest{Name: "write_blueprint", Key: key, Path: "/api/v1/blueprints", Body: raw}
	op, e := s.ReserveOperation(ctx, request)
	if e != nil {
		return nil, e
	}
	if op.State == "complete" {
		var id string
		e = s.DB.QueryRow(ctx, "SELECT subject_id FROM operation WHERE id=$1", op.ID).Scan(&id)
		if e != nil {
			return nil, e
		}
		return s.Blueprint(ctx, id)
	}
	claim, e := s.DB.Exec(ctx, "UPDATE operation SET state='running' WHERE id=$1 AND state='reserved'", op.ID)
	if e != nil {
		return nil, e
	}
	if claim.RowsAffected() != 1 {
		return nil, &provider.Failure{Code: "LEASE_ACTIVE"}
	}
	defer func() {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer done()
		_, _ = s.DB.Exec(end, "UPDATE operation SET state='interrupted',finished_at=clock_timestamp() WHERE id=$1 AND state='running'", op.ID)
	}()
	c, _, e := s.Configuration(ctx)
	if e != nil {
		return nil, e
	}
	b, e := expandBlueprint(raw, c)
	if e != nil {
		return nil, e
	}
	payload, _ := lab.Canonical(b)
	asset, e := s.saveProviderBytes(ctx, payload, "provider_input")
	if e != nil {
		return nil, e
	}
	_, e = s.DB.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2::text,result_document_id=(SELECT document_id FROM entity_head WHERE id=$3),finished_at=clock_timestamp() WHERE id=$1 AND state='running'", op.ID, b["id"], asset.ID)
	return b, e
}
func (s *Storage) Blueprint(ctx context.Context, id string) (map[string]any, error) {
	var asset string
	e := s.DB.QueryRow(ctx, "SELECT a.asset_id FROM operation o JOIN asset_location a ON a.asset_id=o.result_document_id WHERE o.operation_name='write_blueprint' AND o.subject_id=$1 AND o.state='complete'", id).Scan(&asset)
	// Asset IDs and immutable document envelopes need not be the same. Resolve
	// through the asset's stable entity head instead of assuming that coincidence.
	if errors.Is(e, pgx.ErrNoRows) {
		e = s.DB.QueryRow(ctx, "SELECT h.id FROM operation o JOIN entity_head h ON h.document_id=o.result_document_id WHERE o.operation_name='write_blueprint' AND o.subject_id=$1 AND o.state='complete' AND h.kind='asset'", id).Scan(&asset)
	}
	if e != nil {
		return nil, e
	}
	raw, e := s.ReadAsset(ctx, asset)
	if e != nil {
		return nil, e
	}
	var b map[string]any
	if e = json.Unmarshal(raw, &b); e != nil {
		return nil, e
	}
	return b, nil
}

func (s *Storage) Preparation(ctx context.Context, id string) (map[string]any, error) {
	var doc string
	e := s.DB.QueryRow(ctx, "SELECT document_id FROM entity_head WHERE id=$1 AND kind='preparation-state'", id).Scan(&doc)
	if e != nil {
		return nil, e
	}
	d, e := s.ReadDocument(ctx, doc)
	if e != nil {
		return nil, e
	}
	var p map[string]any
	e = json.Unmarshal(d.Payload, &p)
	return p, e
}
func (s *Storage) Preparations(ctx context.Context, limit int, cursor string) (map[string]any, error) {
	if limit < 1 || limit > 100 {
		return nil, ErrConflict
	}
	var afterTime *string
	afterID := ""
	if cursor != "" {
		raw, e := base64.RawURLEncoding.DecodeString(cursor)
		if e != nil || len(cursor) > 2048 {
			return nil, ErrConflict
		}
		var c []string
		if e = json.Unmarshal(raw, &c); e != nil || len(c) != 2 {
			return nil, ErrConflict
		}
		if _, e = time.Parse(time.RFC3339Nano, c[0]); e != nil {
			return nil, ErrConflict
		}
		if _, e = uuid.Parse(c[1]); e != nil {
			return nil, ErrConflict
		}
		afterTime = &c[0]
		afterID = c[1]
	}
	rows, e := s.DB.Query(ctx, "SELECT h.id FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.kind='preparation-state' AND ($2::timestamptz IS NULL OR ((d.payload->>'created_at')::timestamptz,h.id)>($2::timestamptz,$3)) ORDER BY (d.payload->>'created_at')::timestamptz,h.id LIMIT $1", limit+1, afterTime, afterID)
	if e != nil {
		return nil, e
	}
	ids := []string{}
	for rows.Next() {
		var id string
		if e = rows.Scan(&id); e != nil {
			rows.Close()
			return nil, e
		}
		ids = append(ids, id)
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return nil, e
	}
	more := len(ids) > limit
	if more {
		ids = ids[:limit]
	}
	result := []map[string]any{}
	for _, id := range ids {
		p, e := s.Preparation(ctx, id)
		if e != nil {
			return nil, e
		}
		result = append(result, p)
	}
	var next any = nil
	if more {
		last := result[len(result)-1]
		raw, _ := json.Marshal([]string{last["created_at"].(string), last["id"].(string)})
		next = base64.RawURLEncoding.EncodeToString(raw)
	}
	return map[string]any{"items": result, "next_cursor": next}, nil
}

func (s *Storage) checkpoint(ctx context.Context, p map[string]any, expected *int64, operation string, complete bool, canonicalWords ...int) error {
	wordCount := 0
	if len(canonicalWords) > 0 {
		wordCount = canonicalWords[0]
	}
	phase := "canonical_text"
	if p["phase_states"].(map[string]any)["mutation"] != "not_started" {
		phase = "mutation"
	}
	raw, e := lab.Canonical(p)
	if e != nil {
		return e
	}
	write := DocumentWrite{ID: uuid.NewString(), Kind: "preparation-state", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: p["id"].(string), Expected: expected, State: p["phase_states"].(map[string]any)[phase].(string)}}
	for _, k := range []string{"settings_asset_id", "canonical_asset_id", "mutated_asset_id", "mutation_manifest_asset_id"} {
		if id, ok := p[k].(string); ok {
			var sha string
			e = s.DB.QueryRow(ctx, "SELECT content_sha256 FROM object_node WHERE node_id=$1 AND scope_id=$1 AND kind='asset-bytes'", id).Scan(&sha)
			if e != nil {
				return e
			}
			write.References = append(write.References, Reference{Pointer: "/" + k, ID: id, Scope: id, Kind: "asset-bytes", SHA: sha, Relation: k})
		}
	}
	if id, ok := p["candidate_id"].(string); ok {
		var sha string
		if e := s.DB.QueryRow(ctx, "SELECT payload_sha256 FROM document WHERE id=$1 AND kind='candidate-envelope'", id).Scan(&sha); e != nil {
			return e
		}
		write.References = append(write.References, Reference{Pointer: "/candidate_id", ID: id, Scope: "local", Kind: "candidate-envelope", SHA: sha, Relation: "candidate_id"})
	}
	saved, e := validateDocument(write)
	if e != nil {
		return e
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	var owned bool
	e = tx.QueryRow(ctx, "SELECT state='running' AND started_at>clock_timestamp()-interval '270 seconds' FROM operation WHERE id=$1 FOR UPDATE", operation).Scan(&owned)
	if e != nil {
		return e
	}
	if !owned {
		return &provider.Failure{Code: "LEASE_STALE"}
	}
	if expected != nil {
		var previous []byte
		e = tx.QueryRow(ctx, "SELECT d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id=$1 AND h.revision=$2 FOR UPDATE OF h", p["id"], *expected).Scan(&previous)
		if e != nil {
			return ErrRevision
		}
		var old map[string]any
		_ = json.Unmarshal(previous, &old)
		if old["active_operation_id"] != operation {
			return &provider.Failure{Code: "LEASE_STALE"}
		}
		if p["revision"] != float64(*expected+1) {
			return ErrRevision
		}
	} else if p["original_operation_id"] != operation || p["active_operation_id"] != operation || p["revision"] != float64(0) {
		return ErrReference
	}
	for _, id := range p["operation_ids"].([]any) {
		var exists bool
		if e = tx.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM operation WHERE id=$1 AND workspace_id='local')", id).Scan(&exists); e != nil {
			return e
		}
		if !exists {
			return ErrReference
		}
	}
	if e = insertDocument(ctx, tx, write, saved); e != nil {
		return e
	}
	if e = validateGraph(ctx, tx); e != nil {
		return e
	}
	if complete {
		provenance, err := lab.Canonical(map[string]any{"preparation_id": p["id"], "operation_id": operation, "canonical_sha256": p["canonical_sha256"], "canonical_word_count": wordCount, "origin": "on_demand_model_output", "mutation_complete": phase == "mutation", "mutation_manifest_asset_id": p["mutation_manifest_asset_id"], "audio_complete": false})
		if err != nil {
			return err
		}
		if _, e = tx.Exec(ctx, "INSERT INTO audit_event(workspace_id,action,subject_document_id,event_sha256,event_payload) VALUES('local',$4,$1,$2,$3)", write.ID, contracts.Digest(provenance), provenance, map[string]string{"canonical_text": "preparation.canonical.completed", "mutation": "preparation.mutation.completed"}[phase]); e != nil {
			return e
		}
		if _, e = tx.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2::text,result_document_id=$3,finished_at=clock_timestamp() WHERE id=$1", operation, p["id"], write.ID); e != nil {
			return e
		}
	} else if p["phase_states"].(map[string]any)[phase] == "failed" {
		errorBytes, err := lab.Canonical(p["last_failure"])
		if err != nil {
			return err
		}
		errorWrite := DocumentWrite{ID: uuid.NewString(), Kind: "error-response", Version: "2.0.0", Scope: "local", Payload: errorBytes}
		errorSaved, err := validateDocument(errorWrite)
		if err != nil {
			return err
		}
		if err = insertDocument(ctx, tx, errorWrite, errorSaved); err != nil {
			return err
		}
		if _, e = tx.Exec(ctx, "UPDATE operation SET state='failed',subject_id=$2::text,error_document_id=$3,result_document_id=$4,finished_at=clock_timestamp() WHERE id=$1", operation, p["id"], errorWrite.ID, write.ID); e != nil {
			return e
		}
	} else {
		if _, e = tx.Exec(ctx, "UPDATE operation SET subject_id=$2 WHERE id=$1", operation, p["id"]); e != nil {
			return e
		}
	}
	return tx.Commit(ctx)
}

func (s *Server) freezePreparation(ctx context.Context, b map[string]any, c map[string]any, bundle lab.Bundle, op Operation) (map[string]any, error) {
	bindings, e := preparationBindings(c, bundle)
	if e != nil {
		return nil, e
	}
	assets := map[string]Asset{}
	for _, n := range []string{"providers.v1.yaml", "mutation-recipes.v1.json", "acoustic-production.v1.json", "error-taxonomy.v1.yaml"} {
		raw, e := generationRegistry(n)
		if e != nil {
			return nil, e
		}
		a, e := s.Store.saveProviderBytes(ctx, raw, "provider_input")
		if e != nil {
			return nil, e
		}
		assets[n] = a
	}
	speech, recipes, production := assets["providers.v1.yaml"], assets["mutation-recipes.v1.json"], assets["acoustic-production.v1.json"]
	req := b["exercise_request"]
	settings := map[string]any{"schema_version": "2.0.0", "exercise_request": req, "blueprint": b, "configuration": c, "prompt_bundle": bundle, "generation_bindings": bindings, "speech_registry_asset_id": speech.ID, "speech_registry_sha256": speech.SHA, "recipe_registry_asset_id": recipes.ID, "recipe_registry_sha256": recipes.SHA, "production_registry_asset_id": production.ID, "production_registry_sha256": production.SHA, "source_record_ids": []any{}, "taxonomy_registry_asset_id": assets["error-taxonomy.v1.yaml"].ID, "taxonomy_registry_sha256": assets["error-taxonomy.v1.yaml"].SHA}
	raw, _ := lab.Canonical(settings)
	asset, e := s.Store.saveProviderBytes(ctx, raw, "provider_input")
	if e != nil {
		return nil, e
	}
	now := time.Now().UTC().Format(time.RFC3339Nano)
	p := map[string]any{"schema_version": "2.0.0", "id": uuid.NewString(), "revision": float64(0), "original_operation_id": op.ID, "operation_ids": []any{op.ID}, "active_operation_id": op.ID, "settings_asset_id": asset.ID, "settings_sha256": asset.SHA, "phase_states": map[string]any{"canonical_text": "running", "mutation": "not_started", "render": "not_started"}, "created_at": now, "updated_at": now}
	for _, k := range []string{"canonical_asset_id", "canonical_sha256", "candidate_id", "mutated_asset_id", "mutation_manifest_asset_id", "render_plan_asset_id", "render_progress_asset_id", "audio_asset_id", "audio_sha256", "key_id", "last_failure"} {
		p[k] = nil
	}
	if e = s.Store.checkpoint(ctx, p, nil, op.ID, false); e != nil {
		return nil, e
	}
	return p, nil
}

type CanonicalPreparationRequest struct {
	BlueprintID      string   `json:"blueprint_id"`
	ConfigurationSHA string   `json:"effective_configuration_sha256"`
	Sources          []string `json:"source_record_ids"`
	Attempt          int      `json:"generation_attempt"`
	PreparationID    *string  `json:"preparation_id"`
}

// PrepareCanonical is the real stage owner used by the later combined Generate
// action. It does not return a candidate-envelope or claim mutation completion.
func (s *Server) PrepareCanonical(ctx context.Context, r CanonicalPreparationRequest, key string, client *http.Client) (map[string]any, error) {
	raw, _ := lab.Canonical(r)
	if _, _, e := contracts.Validate("generation-request", "2.0.0", raw); e != nil {
		return nil, e
	}
	if len(r.Sources) != 0 {
		return nil, &provider.Failure{Code: "SOURCE_FORMAT_UNBOUND"}
	}
	if r.PreparationID == nil && r.Attempt != 1 {
		return nil, ErrConflict
	}
	request := OperationRequest{Name: "canonical_prepare", Key: key, Path: "/api/v1/candidates:generate", Body: raw}
	op, e := s.Store.ReserveOperation(ctx, request)
	if e != nil {
		return nil, e
	}
	if op.State == "complete" || op.State == "failed" {
		// Replay belongs to this action's immutable result, while ordinary
		// preparation readback follows its current head. A later successful
		// continuation must not erase a failed action's response.
		var documentID string
		if e = s.Store.DB.QueryRow(ctx, "SELECT result_document_id FROM operation WHERE id=$1", op.ID).Scan(&documentID); e != nil {
			return nil, e
		}
		document, err := s.Store.ReadDocument(ctx, documentID)
		if err != nil {
			return nil, err
		}
		var saved map[string]any
		if err = json.Unmarshal(document.Payload, &saved); err != nil {
			return nil, err
		}
		if op.State == "failed" {
			failure := saved["last_failure"].(map[string]any)
			return saved, &provider.Failure{Code: failure["code"].(string)}
		}
		return saved, nil
	}
	var p map[string]any
	if r.PreparationID != nil {
		p, e = s.Store.Preparation(ctx, *r.PreparationID)
		if e != nil {
			return nil, e
		}
	}
	var settings map[string]any
	if p != nil {
		b, e := s.Store.ReadAsset(ctx, p["settings_asset_id"].(string))
		if e != nil {
			return p, e
		}
		if e = json.Unmarshal(b, &settings); e != nil {
			return p, e
		}
		if settings["blueprint"].(map[string]any)["id"] != r.BlueprintID || settings["configuration"].(map[string]any)["configuration_sha256"] != r.ConfigurationSHA {
			return p, ErrConflict
		}
		if p["phase_states"].(map[string]any)["canonical_text"] == "complete" {
			_, e = s.Store.DB.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2::text,result_document_id=(SELECT document_id FROM entity_head WHERE id=$2::text),finished_at=clock_timestamp() WHERE id=$1", op.ID, p["id"])
			return p, e
		}
	}
	claim, e := s.Store.DB.Exec(ctx, "UPDATE operation SET state='running' WHERE id=$1 AND state='reserved'", op.ID)
	if e != nil {
		return p, e
	}
	if claim.RowsAffected() != 1 {
		return p, &provider.Failure{Code: "LEASE_ACTIVE"}
	}
	defer func() {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer done()
		_, _ = s.Store.DB.Exec(end, "UPDATE operation SET state='interrupted',finished_at=clock_timestamp() WHERE id=$1 AND state='running'", op.ID)
	}()
	if p == nil {
		b, e := s.Store.Blueprint(ctx, r.BlueprintID)
		if e != nil {
			return nil, e
		}
		c, _, e := s.Store.Configuration(ctx)
		if e != nil {
			return nil, e
		}
		if c["configuration_sha256"] != r.ConfigurationSHA {
			return nil, ErrConflict
		}
		bundle, e := s.Store.ActiveLabBundle(ctx)
		if e != nil {
			return nil, e
		}
		p, e = s.freezePreparation(ctx, b, c, bundle, op)
		if e != nil {
			return nil, e
		}
		raw, e = s.Store.ReadAsset(ctx, p["settings_asset_id"].(string))
		if e != nil {
			return p, e
		}
		_ = json.Unmarshal(raw, &settings)
	} else {
		if r.Attempt != len(p["operation_ids"].([]any))+1 {
			return p, ErrConflict
		}
		if e = s.Store.takePreparation(ctx, p, op.ID); e != nil {
			return p, e
		}
	}
	return s.finishCanonical(ctx, p, settings, op, key, client)
}

func (s *Storage) takePreparation(ctx context.Context, p map[string]any, operation string, phases ...string) error {
	phase := "canonical_text"
	if len(phases) > 0 {
		phase = phases[0]
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	var own bool
	if e = tx.QueryRow(ctx, "SELECT state='running' AND started_at>clock_timestamp()-interval '270 seconds' FROM operation WHERE id=$1 FOR UPDATE", operation).Scan(&own); e != nil {
		return e
	}
	if !own {
		return &provider.Failure{Code: "LEASE_STALE"}
	}
	rev := int64(p["revision"].(float64))
	var old []byte
	if e = tx.QueryRow(ctx, "SELECT d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id=$1 AND h.revision=$2 FOR UPDATE OF h", p["id"], rev).Scan(&old); e != nil {
		return ErrRevision
	}
	if active, ok := p["active_operation_id"].(string); ok {
		var live bool
		if e = tx.QueryRow(ctx, "SELECT state='running' AND started_at>clock_timestamp()-interval '270 seconds' FROM operation WHERE id=$1", active).Scan(&live); e != nil {
			return e
		}
		if live {
			return &provider.Failure{Code: "LEASE_ACTIVE"}
		}
		_, e = tx.Exec(ctx, "UPDATE operation SET state='interrupted',finished_at=clock_timestamp() WHERE id=$1 AND state='running'", active)
		if e != nil {
			return e
		}
	}
	p["revision"] = float64(rev + 1)
	p["active_operation_id"] = operation
	p["operation_ids"] = append(p["operation_ids"].([]any), operation)
	p["updated_at"] = time.Now().UTC().Format(time.RFC3339Nano)
	p["phase_states"].(map[string]any)[phase] = "running"
	raw, _ := lab.Canonical(p)
	w := DocumentWrite{ID: uuid.NewString(), Kind: "preparation-state", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: p["id"].(string), Expected: &rev, State: "running"}}
	for _, field := range []string{"settings_asset_id", "canonical_asset_id", "mutated_asset_id", "mutation_manifest_asset_id"} {
		if id, ok := p[field].(string); ok {
			var sha string
			if e = tx.QueryRow(ctx, "SELECT content_sha256 FROM object_node WHERE node_id=$1 AND scope_id=$1 AND kind='asset-bytes'", id).Scan(&sha); e != nil {
				return e
			}
			w.References = append(w.References, Reference{Pointer: "/" + field, ID: id, Scope: id, Kind: "asset-bytes", SHA: sha, Relation: field})
		}
	}
	d, e := validateDocument(w)
	if e != nil {
		return e
	}
	if e = insertDocument(ctx, tx, w, d); e != nil {
		return e
	}
	if e = validateGraph(ctx, tx); e != nil {
		return e
	}
	return tx.Commit(ctx)
}

func (s *Server) finishCanonical(ctx context.Context, p, settings map[string]any, op Operation, key string, client *http.Client) (map[string]any, error) {
	blueprint := settings["blueprint"].(map[string]any)
	config := settings["configuration"].(map[string]any)
	var bundle lab.Bundle
	raw, _ := json.Marshal(settings["prompt_bundle"])
	_ = json.Unmarshal(raw, &bundle)
	taxonomy, e := s.Store.saveProviderBytes(ctx, []byte("[]"), "provider_input")
	if e != nil {
		return p, e
	}
	input := map[string]any{"schema_version": "2.0.0", "blueprint": blueprint, "taxonomy_records_asset_id": taxonomy.ID, "taxonomy_records_sha256": taxonomy.SHA, "allowed_source_record_ids": []any{}, "request_language": "en", "source_excerpts": []any{}, "taxonomy_context": map[string]any{"taxonomy_sha256": taxonomy.SHA, "entries": []any{}, "judgment_rules": []any{}}, "phase": "canonical_text", "canonical_script": nil, "canonical_script_sha256": nil, "mutation_recipes": []any{}, "recipe_registry_sha256": settings["recipe_registry_sha256"], "production_recipes": []any{}, "production_registry_sha256": settings["production_registry_sha256"]}
	components := map[string]any{"blueprint": blueprint, "taxonomy": input["taxonomy_context"], "public_context": blueprint["public_context"], "source_excerpt": nil}
	phase := "canonical_text"
	// A process may lose the parent checkpoint response after the exact child
	// result has committed. Recover only a completed child of this preparation's
	// recorded operations, never a latest-by-blueprint search or a new model call.
	result := LLMResult{}
	var callErr error
	for _, parent := range p["operation_ids"].([]any) {
		var child string
		err := s.Store.DB.QueryRow(ctx, "SELECT child.id FROM operation parent JOIN operation child ON child.idempotency_key=parent.idempotency_key AND child.operation_name='canonical_text' WHERE parent.id=$1 AND parent.operation_name='canonical_prepare' AND child.state='complete'", parent).Scan(&child)
		if errors.Is(err, pgx.ErrNoRows) {
			continue
		}
		if err != nil {
			return p, err
		}
		previous, err := s.Store.ReadLLMResult(ctx, child)
		if err != nil {
			return p, err
		}
		result = previous
		break
	}
	if result.OperationID == "" {
		result, callErr = s.InvokeLLM(ctx, LLMRequest{Operation: OperationRequest{Name: "canonical_text", Key: key, Path: "/prepare/canonical", Body: json.RawMessage(`{}`)}, Stage: "case_generation", Phase: &phase, Input: input, Components: components, Configuration: config, Bundle: bundle, Validate: func(raw []byte) error { _, _, e := canonicalContent(raw, blueprint); return e }}, client)
	}
	if len(result.ReceiptIDs) > 0 {
		finish, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
		_, e = s.Store.LLMDiagnostic(finish, result, config["llm_lab_capture_content"] == true, config["llm_lab_trace_enabled"] == true)
		done()
		if e != nil && callErr == nil {
			callErr = e
		}
	}
	rev := int64(p["revision"].(float64))
	p["revision"] = float64(rev + 1)
	p["updated_at"] = time.Now().UTC().Format(time.RFC3339Nano)
	words := 0
	if callErr == nil {
		// The provider acceptance step already checked the output. Keep and use it.
		var accepted map[string]any
		if e = json.Unmarshal(result.Output, &accepted); e != nil {
			return p, e
		}
		for _, u := range accepted["utterances"].([]any) {
			words += len(strings.Fields(u.(map[string]any)["canonical_text"].(string)))
		}
		a, e := s.Store.saveProviderBytes(ctx, result.Output, "provider_output")
		if e != nil {
			callErr = e
		} else {
			p["canonical_asset_id"] = a.ID
			p["canonical_sha256"] = a.SHA
			p["phase_states"].(map[string]any)["canonical_text"] = "complete"
			p["last_failure"] = nil
		}
	}
	if callErr != nil {
		code, message := provider.SafeError(callErr)
		p["phase_states"].(map[string]any)["canonical_text"] = "failed"
		p["last_failure"] = map[string]any{"code": code, "message": message, "request_id": op.ID, "retryable": true, "object_id": nil, "details": []any{}}
	}
	p["active_operation_id"] = nil
	finish, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer done()
	if e = s.Store.checkpoint(finish, p, &rev, op.ID, callErr == nil, words); e != nil {
		return p, e
	}
	return p, callErr
}

func (s *Server) PreparationCommand(ctx context.Context, input io.Reader, output io.Writer) error {
	var r struct {
		Action    string                      `json:"action"`
		Blueprint json.RawMessage             `json:"blueprint"`
		Request   CanonicalPreparationRequest `json:"request"`
		Key       string                      `json:"key"`
		ID        string                      `json:"id"`
	}
	if e := lab.DecodeCommand(input, &r); e != nil {
		return e
	}
	var v any
	var e error
	switch r.Action {
	case "blueprint":
		v, e = s.Store.WriteBlueprint(ctx, r.Blueprint, r.Key)
	case "read":
		v, e = s.Store.Preparation(ctx, r.ID)
	case "canonical":
		v, e = s.PrepareCanonical(ctx, r.Request, r.Key, nil)
	case "mutation":
		v, e = s.PrepareMutation(ctx, r.Request, r.Key, nil)
	case "list":
		v, e = s.Store.Preparations(ctx, 50, "")
	default:
		return ErrConflict
	}
	if v != nil {
		if err := json.NewEncoder(output).Encode(v); err != nil {
			return err
		}
	}
	return e
}

func preparationHTTPError(w http.ResponseWriter, status int, code string) {
	writeJSON(w, status, map[string]any{"code": code, "message": strings.ReplaceAll(strings.ToLower(code), "_", " "), "request_id": uuid.NewString(), "retryable": status >= 500, "object_id": nil, "details": []any{}})
}
func (s *Server) preparationList(w http.ResponseWriter, r *http.Request) {
	limit := 50
	var e error
	if q := r.URL.Query().Get("limit"); q != "" {
		limit, e = strconv.Atoi(q)
	}
	if e != nil || limit < 1 || limit > 100 {
		preparationHTTPError(w, 400, "CONSTRAINT_CONFLICT")
		return
	}
	p, e := s.Store.Preparations(r.Context(), limit, r.URL.Query().Get("cursor"))
	if e != nil {
		status, code := 503, "INFRASTRUCTURE_UNAVAILABLE"
		if errors.Is(e, ErrConflict) {
			status, code = 400, "CONSTRAINT_CONFLICT"
		}
		preparationHTTPError(w, status, code)
		return
	}
	writeJSON(w, 200, p)
}
func (s *Server) blueprintWrite(w http.ResponseWriter, r *http.Request) {
	if r.Header.Get("Content-Type") != "application/json" {
		preparationHTTPError(w, 400, "INVALID_JSON")
		return
	}
	raw, e := io.ReadAll(http.MaxBytesReader(w, r.Body, 16*1024))
	if e != nil {
		preparationHTTPError(w, 400, "INVALID_JSON")
		return
	}
	if id, e := uuid.Parse(r.Header.Get("Idempotency-Key")); e != nil || id.Version() != 4 {
		preparationHTTPError(w, 400, "SCHEMA_INVALID")
		return
	}
	b, e := s.Store.WriteBlueprint(r.Context(), raw, r.Header.Get("Idempotency-Key"))
	if e != nil {
		status, code := 503, "INFRASTRUCTURE_UNAVAILABLE"
		if errors.Is(e, ErrConflict) {
			status, code = 409, "IDEMPOTENCY_CONFLICT"
		}
		var failure *provider.Failure
		if errors.As(e, &failure) && failure.Code == "SCHEMA_INVALID" {
			status, code = 400, failure.Code
		}
		preparationHTTPError(w, status, code)
		return
	}
	writeJSON(w, 201, b)
}
func (s *Server) blueprintGet(w http.ResponseWriter, r *http.Request) {
	b, e := s.Store.Blueprint(r.Context(), r.PathValue("id"))
	if e != nil {
		status, code := 503, "INFRASTRUCTURE_UNAVAILABLE"
		if errors.Is(e, pgx.ErrNoRows) {
			status, code = 404, "NOT_FOUND"
		}
		preparationHTTPError(w, status, code)
		return
	}
	writeJSON(w, 200, b)
}
