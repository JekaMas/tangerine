package app

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/provider"
)

// Resume selects this action's original canonical checkpoint when it exists.
// Current-head counters are appropriate only for a genuinely new Resume action.
func (s *Storage) resumePreparation(ctx context.Context, id, key string) (map[string]any, int, error) {
	var operation, state string
	var document *string
	e := s.DB.QueryRow(ctx, "SELECT id,state,result_document_id FROM operation WHERE operation_name='canonical_prepare' AND idempotency_key=$1", interpretationCallKey(key, "canonical")).Scan(&operation, &state, &document)
	var p map[string]any
	if errors.Is(e, pgx.ErrNoRows) {
		p, e = s.Preparation(ctx, id)
	} else if e == nil {
		if state != "complete" && state != "failed" {
			return nil, 0, &provider.Failure{Code: "LEASE_ACTIVE"}
		}
		if document == nil {
			return nil, 0, ErrUnavailable
		}
		var d SavedDocument
		d, e = s.ReadDocument(ctx, *document)
		if e == nil {
			e = json.Unmarshal(d.Payload, &p)
		}
	}
	if e != nil {
		return nil, 0, e
	}
	if p["id"] != id {
		return nil, 0, ErrConflict
	}
	attempt := len(p["operation_ids"].([]any)) + 1
	for i, value := range p["operation_ids"].([]any) {
		if value == operation {
			attempt = i + 1
			break
		}
	}
	return p, attempt, nil
}
func (s *Storage) generationRenderReplay(ctx context.Context, key string) (map[string]any, bool, error) {
	var id, state string
	e := s.DB.QueryRow(ctx, "SELECT id,state FROM operation WHERE operation_name='speech_render' AND idempotency_key=$1", interpretationCallKey(key, "render")).Scan(&id, &state)
	if errors.Is(e, pgx.ErrNoRows) {
		return nil, false, nil
	}
	if e != nil {
		return nil, true, e
	}
	if state != "complete" && state != "failed" {
		return nil, true, &provider.Failure{Code: "LEASE_ACTIVE"}
	}
	p, e := s.speechActionResult(ctx, id)
	if e == nil && p["last_failure"] != nil {
		e = &provider.Failure{Code: p["last_failure"].(map[string]any)["code"].(string)}
	}
	return p, true, e
}
