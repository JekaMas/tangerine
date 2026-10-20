package app

import (
	"context"
	"net/http"
	"tangerine.local/api/internal/lab"
)

// assembleSpeech persists accepted samples and diagnostics before final key linkage.
// Provider failures are handled at the transport owner; this path never revalidates pieces.
func (s *Server) assembleSpeech(ctx context.Context, p, settings, frozen, progress map[string]any, requests []any, operation string, client *http.Client) error {
	if id, ok := progress["assembled_asset_id"].(string); ok {
		p["audio_asset_id"] = id
		p["audio_sha256"] = progress["assembled_sha256"]
		return s.saveSpeechKey(ctx, p, settings, frozen, progress)
	}
	pcm := []byte{}
	sampleMap := []any{}
	for i, value := range progress["pieces"].([]any) {
		piece := value.(map[string]any)
		audio, e := s.Store.ReadAsset(ctx, piece["asset_id"].(string))
		if e != nil {
			return e
		}
		start := len(pcm) / 2
		pcm = append(pcm, audio[44:]...)
		end := len(pcm) / 2
		rows, e := s.acousticPieceRows(ctx, piece, start)
		if e != nil {
			return e
		}
		sampleMap = append(sampleMap, rows...)
		gap := int(requests[i].(map[string]any)["gap_after_ms"].(float64)) * 24
		pcm = append(pcm, make([]byte, gap*2)...)
		if gap > 0 {
			sampleMap = append(sampleMap, sampleGap(piece["id"], end, gap))
		}
	}
	plannedPauses := []any{}
	for _, v := range sampleMap {
		row := v.(map[string]any)
		if row["kind"] == "gap" || row["kind"] == "pause" {
			plannedPauses = append(plannedPauses, []any{row["final_start"], row["final_end"]})
		}
	}
	quality, e := s.speechQuality(ctx, pcm, plannedPauses, client)
	if e != nil {
		return e
	}
	audio := speechWAV(pcm)
	asset, e := s.saveAudioBytes(ctx, audio)
	if e != nil {
		return e
	}
	raw, _ := lab.Canonical(map[string]any{"clock": 24000, "intervals": sampleMap, "sample_count": len(pcm) / 2, "audio_sha256": asset.SHA, "quality": quality, "pace": speechPaceObservations(settings)})
	mapping, e := s.Store.saveProviderBytes(ctx, raw, "canonical_json")
	if e != nil {
		return e
	}
	typedMap, e := s.acousticDocument(ctx, actualSampleMap(progress["render_plan_sha256"], asset.SHA, len(pcm)/2, sampleMap))
	if e != nil {
		return e
	}
	progress["diagnostic_asset_id"] = mapping.ID
	progress["assembled_asset_id"] = asset.ID
	progress["assembled_sha256"] = asset.SHA
	progress["sample_map_asset_id"] = typedMap
	if e = s.saveSpeechProgress(ctx, p, progress, operation); e != nil {
		return e
	}
	p["audio_asset_id"] = asset.ID
	p["audio_sha256"] = asset.SHA
	return s.saveSpeechKey(ctx, p, settings, frozen, progress)
}
