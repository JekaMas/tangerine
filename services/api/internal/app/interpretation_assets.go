package app

import (
	"context"
	"encoding/json"
	"time"
)

func (s *Storage) interpretationJSON(ctx context.Context, value any) (string, error) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	raw, e := json.Marshal(value)
	if e != nil {
		return "", e
	}
	asset, e := s.saveProviderBytes(ctx, raw, "provider_output")
	return asset.ID, e
}
func (s *Storage) readInterpretationJSON(ctx context.Context, id string, value any) error {
	raw, e := s.ReadAsset(ctx, id)
	if e != nil {
		return e
	}
	return json.Unmarshal(raw, value)
}
