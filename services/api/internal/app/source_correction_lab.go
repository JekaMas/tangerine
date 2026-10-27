package app

import (
	"context"
	"encoding/json"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
)

// Fresh portable data are admitted once at the Lab input boundary. Evaluation
// itself only compares supplied text; it does not grade semantic correctness or
// change any learner score and has no model/client dependency.
func (s *Storage) EvaluateSourceCorrections(ctx context.Context, raw []byte) (map[string]any, error) {
	_, body, e := contracts.Validate("source-correction-evaluation-request", "2.0.0", raw)
	if e != nil {
		return nil, e
	}
	var request source.CorrectionEvaluationRequest
	if e = json.Unmarshal(body, &request); e != nil {
		return nil, e
	}
	input, e := s.saveProviderBytes(ctx, body, "canonical_json")
	if e != nil {
		return nil, e
	}
	report := source.EvaluateCorrections(request)
	report.InputAsset = input.ID
	asset, e := s.saveProviderBytes(ctx, sourceBytes(report), "canonical_json")
	if e != nil {
		return nil, e
	}
	return map[string]any{"report": report, "asset_id": asset.ID, "input_asset_id": input.ID, "provider_calls": 0}, nil
}
