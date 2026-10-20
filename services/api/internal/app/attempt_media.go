package app

import (
	"context"
	"errors"
)

var ErrAttemptRights = errors.New("listening audio rights restricted")

// Media access owns stored-asset selection and source rights; HTTP owns delivery.
func (s *Storage) AttemptAudio(ctx context.Context, id string) ([]byte, string, error) {
	record, err := s.Attempt(ctx, id)
	if err != nil {
		return nil, "", err
	}
	var availability string
	if err = s.DB.QueryRow(ctx, "SELECT availability FROM exercise_catalog WHERE id::text=$1", record.Attempt["case_version_id"]).Scan(&availability); err != nil {
		return nil, "", err
	}
	if availability == "rights_restricted" {
		return nil, "", ErrAttemptRights
	}
	audio, err := s.ReadAsset(ctx, record.Context["audio_asset_id"].(string))
	if err != nil {
		return nil, "", ErrUnavailable
	}
	return audio, record.Attempt["audio_sha256"].(string), nil
}
