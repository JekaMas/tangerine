package app

import (
	"context"
	"errors"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/provider"
)

// GenerateExercise coordinates existing durable owners; it owns no transport,
// prompt construction, storage schema or scoring logic.
func (s *Server) GenerateExercise(ctx context.Context, input CanonicalPreparationRequest, key string) (map[string]any, error) {
	p, e := s.PrepareCanonical(ctx, input, interpretationCallKey(key, "canonical"), nil)
	if e == nil {
		id := p["id"].(string)
		input.PreparationID = &id
		input.Attempt = len(p["operation_ids"].([]any)) + 1
		p, e = s.PrepareMutation(ctx, input, interpretationCallKey(key, "mutation"), nil)
	}
	if e == nil {
		var previous, state string
		replayErr := s.Store.DB.QueryRow(ctx, "SELECT id,state FROM operation WHERE operation_name='speech_render' AND idempotency_key=$1", interpretationCallKey(key, "render")).Scan(&previous, &state)
		if replayErr == nil {
			if state != "complete" && state != "failed" {
				return p, &provider.Failure{Code: "LEASE_ACTIVE"}
			}
			p, e = s.Store.speechActionResult(ctx, previous)
			if e == nil && p["last_failure"] != nil {
				e = &provider.Failure{Code: p["last_failure"].(map[string]any)["code"].(string)}
			}
			return p, e
		}
		if !errors.Is(replayErr, pgx.ErrNoRows) {
			return p, replayErr
		}
		count, ce := s.Store.speechAttemptCount(ctx, p["id"].(string))
		e = ce
		if e == nil {
			p, e = s.RenderPreparation(ctx, p["id"].(string), interpretationCallKey(key, "render"), count+1, nil)
		}
	}
	return p, e
}
