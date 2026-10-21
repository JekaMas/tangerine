package app

import (
	"context"
	"encoding/base64"
	"net/http"
)

// Supply an available paired source piece only when its entire recording fits
// one diagnostic clip and every selected unit belongs to that utterance. It is
// separately labelled reference audio, never assumed aligned to the target.
// Longer/multi-piece references remain absent rather than guessed/truncated.
func (s *Server) diagnosticReference(ctx context.Context, f diagnosticFrozen, input, packet map[string]any, client *http.Client) error {
	utterance := ""
	for _, v := range input["planned_units"].([]any) {
		ids := v.(map[string]any)["utterance_ids"].([]any)
		if len(ids) != 1 {
			return nil
		}
		id := ids[0].(string)
		if utterance != "" && utterance != id {
			return nil
		}
		utterance = id
	}
	if utterance == "" || f.Progress == nil {
		return nil
	}
	var piece map[string]any
	for _, v := range f.Progress["pieces"].([]any) {
		p := v.(map[string]any)
		if p["utterance_id"] == utterance {
			if piece != nil {
				return nil
			}
			piece = p
		}
	}
	if piece == nil || piece["acoustic_state"] == nil {
		return nil
	}
	id, ok := piece["source_asset_id"].(string)
	if !ok {
		return nil
	}
	audio, err := s.Store.ReadAsset(ctx, id)
	if err != nil {
		return err
	}
	plan, err := s.speechCall(ctx, "/internal/v1/measure-plan", map[string]any{"audio_base64": base64.StdEncoding.EncodeToString(audio), "max_clip_seconds": 10}, client)
	if err != nil {
		return err
	}
	clips := plan["clips"].([]any)
	if len(clips) != 1 {
		return nil
	}
	clip := clips[0].(map[string]any)
	raw, err := base64.StdEncoding.DecodeString(clip["audio_base64"].(string))
	if err != nil {
		return err
	}
	saved, err := s.saveAudioBytes(ctx, raw)
	if err != nil {
		return err
	}
	input["reference_clip_asset_id"] = saved.ID
	packet["reference_audio_base64"] = clip["audio_base64"]
	return nil
}
