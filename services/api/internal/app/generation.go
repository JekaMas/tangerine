package app

import (
	"context"
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
		replay, exists, replayErr := s.Store.generationRenderReplay(ctx, key)
		if exists {
			return replay, replayErr
		}

		count, ce := s.Store.speechAttemptCount(ctx, p["id"].(string))
		e = ce
		if e == nil {
			p, e = s.RenderPreparation(ctx, p["id"].(string), interpretationCallKey(key, "render"), count+1, nil)
		}
	}
	return p, e
}
