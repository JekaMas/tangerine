package app

import (
	"context"
	"github.com/google/uuid"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"time"
)

func (s *Server) saveAudioBytes(ctx context.Context, data []byte) (Asset, error) {
	digest := contracts.Digest(data)
	body, _ := lab.Canonical(map[string]any{"sha256": digest, "size": len(data)})
	a, e := s.Store.ReserveAsset(ctx, AssetRequest{Operation: OperationRequest{Name: "speech-audio", Key: uuid.NewString(), Path: "/speech/audio", Body: body}, SHA: digest, Size: int64(len(data)), Purpose: "audio_delivery", MIME: "audio/wav"})
	if e != nil {
		return a, e
	}
	if _, e = s.Store.UploadAsset(ctx, a.ID, data); e != nil {
		return a, e
	}
	return s.Store.LinkAsset(ctx, a.ID, nil)
}
func (s *Server) saveSpeechProgress(ctx context.Context, p, progress map[string]any, operation string) error {
	progress["revision"] = progress["revision"].(float64) + 1
	raw, _ := lab.Canonical(progress)
	asset, e := s.Store.saveProviderBytes(ctx, raw, "canonical_json")
	if e != nil {
		return e
	}
	p["render_progress_asset_id"] = asset.ID
	rev := int64(p["revision"].(float64))
	p["revision"] = float64(rev + 1)
	p["updated_at"] = time.Now().UTC().Format(time.RFC3339Nano)
	return s.Store.checkpoint(ctx, p, &rev, operation, false)
}
