package app

import (
	"context"
	_ "embed"
	"github.com/google/uuid"
	"tangerine.local/api/internal/contracts"
)

//go:embed generationdata/audio-judge-v1.txt
var audioJudgePrompt []byte

// Built-in identity is materialized only by an explicit configuration write.
func audioDiagnosticDefaults() map[string]any {
	profiles := []any{}
	for _, row := range [][4]string{{"qwen-omni-7b", "local_qwen25_omni", "Qwen/Qwen2.5-Omni-7B", "ae9e1690543ffd5c0221dc27f79834d0294cba00"}, {"qwen-omni-3b", "local_qwen25_omni", "Qwen/Qwen2.5-Omni-3B", "f75b40e3da2003cdd6e1829b1f420ca70797c34e"}, {"gemini-audio", "gemini_interactions", "gemini-3.8-flash", ""}} {
		p := map[string]any{"schema_version": "2.0.0", "id": row[0], "provider": row[1], "model": row[2], "revision": row[3], "credential_ref": nil, "billing_mode": "local", "device": "cpu", "max_clip_seconds": 10, "max_output_tokens": 512, "prompt_asset_id": "builtin-audio-judge-v1", "prompt_sha256": contracts.Digest(audioJudgePrompt)}
		if row[0] == "qwen-omni-3b" {
			p["compute_type"] = "int8_dynamic"
			p["quantization_engine"] = "qnnpack"
			p["repetition_penalty"] = 1.1
		}
		if row[1] == "gemini_interactions" {
			p["revision"], p["credential_ref"], p["billing_mode"], p["device"] = nil, "GEMINI_API_KEY", "free_tier", "provider"
		}
		profiles = append(profiles, p)
	}
	return map[string]any{"profiles": profiles, "model_setup": map[string]string{"qwen-omni-7b": "scripts/tangerine model-setup qwen25-omni-audio-v1", "qwen-omni-3b": "scripts/tangerine model-setup qwen25-omni-3b-audio-v1", "asr": "scripts/tangerine model-setup faster-whisper-local-en-v1"}, "prompt_sha256": contracts.Digest(audioJudgePrompt)}
}

func (s *Storage) resolveDiagnosticPrompt(ctx context.Context, c map[string]any) ([]Reference, error) {
	p, ok := c["audio_diagnostic_profile"].(map[string]any)
	if !ok {
		return nil, nil
	}
	id := p["prompt_asset_id"].(string)
	if id == "builtin-audio-judge-v1" {
		digest := contracts.Digest(audioJudgePrompt)
		if p["prompt_sha256"] != digest {
			return nil, ErrReference
		}
		a, err := s.ReserveAsset(ctx, AssetRequest{Operation: OperationRequest{Name: "diagnostic-prompt", Key: uuid.NewString(), Path: "/audio/diagnostic/prompt", Body: sourceBytes(map[string]any{"sha256": digest})}, SHA: digest, Size: int64(len(audioJudgePrompt)), Purpose: "provider_input", MIME: "text/plain"})
		if err != nil {
			return nil, err
		}
		if _, err = s.UploadAsset(ctx, a.ID, audioJudgePrompt); err != nil {
			return nil, err
		}
		if a, err = s.LinkAsset(ctx, a.ID, nil); err != nil {
			return nil, err
		}
		id = a.ID
		p["prompt_asset_id"] = id
	}
	ref, err := s.assetByteReference(ctx, id, "/audio_diagnostic_profile/prompt_asset_id", "diagnostic-prompt")
	if err != nil {
		return nil, err
	}
	if ref.SHA != p["prompt_sha256"] {
		return nil, ErrReference
	}
	return []Reference{ref}, nil
}
