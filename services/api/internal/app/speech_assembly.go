package app

import (
	"context"
	"encoding/json"
	"net/http"
	"sort"
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
	sources := []speechSource{}
	audios := map[string][]byte{}
	scopeStarts := map[string]int{}
	for i, value := range progress["pieces"].([]any) {
		piece := value.(map[string]any)
		audio, e := s.Store.ReadAsset(ctx, piece["asset_id"].(string))
		if e != nil {
			return e
		}
		request := requests[i].(map[string]any)
		text := ""
		for _, v := range request["operations"].([]any) {
			if t, ok := v.(map[string]any)["text"].(string); ok {
				text += t
			}
		}
		words := []speechWord{}
		if rows, ok := piece["word_intervals"]; ok {
			raw, _ := json.Marshal(rows)
			_ = json.Unmarshal(raw, &words)
		}
		if state, ok := piece["acoustic_state"].(map[string]any); ok && len(overlapIntents(frozen["plan"].(map[string]any))) > 0 {
			native, e := s.acousticRead(ctx, state["native_asset_id"].(string))
			if e != nil {
				return e
			}
			words = speechWords(native, request)
		}
		id, turn := piece["id"].(string), piece["utterance_id"].(string)
		sources = append(sources, speechSource{id, turn, text, scopeStarts[turn], len(audio[44:]) / 2, int(request["gap_after_ms"].(float64)) * 24, words})
		scopeStarts[turn] += len([]rune(text))
		audios[id] = audio[44:]
	}
	composition, accepted := savedComposition(progress)
	if !accepted {
		var e error
		composition, e = planSpeechComposition(sources, overlapIntents(frozen["plan"].(map[string]any)))
		if e != nil {
			return e
		}
		progress["composition"] = compositionValue(composition)
		if e = s.saveSpeechProgress(ctx, p, progress, operation); e != nil {
			return e
		}
	}
	pcm, e := composeSpeechPCM(ctx, composition, audios)
	if e != nil {
		return e
	}
	sampleMap := []any{}
	for i, value := range progress["pieces"].([]any) {
		piece := value.(map[string]any)
		placement := composition.Pieces[i]
		rows, e := s.acousticPieceRows(ctx, piece, 0)
		if e != nil {
			return e
		}
		sampleMap = append(sampleMap, compositionRows(rows, placement, composition.Tracks)...)
	}
	// Only uncovered final time is silence. A shorter backchannel cannot move
	// the following turn into the unfinished foreground speaker.
	cursor := 0
	placements := append([]speechPlacement{}, composition.Pieces...)
	sort.SliceStable(placements, func(i, j int) bool { return placements[i].Start < placements[j].Start })
	for _, p := range placements {
		if p.Start > cursor {
			sampleMap = append(sampleMap, sampleGap(p.PieceID, cursor, p.Start-cursor))
		}
		if p.End > cursor {
			cursor = p.End
		}
	}
	if cursor < composition.SampleCount {
		sampleMap = append(sampleMap, sampleGap("tail", cursor, composition.SampleCount-cursor))
	}
	sort.SliceStable(sampleMap, func(i, j int) bool {
		a, b := sampleMap[i].(map[string]any), sampleMap[j].(map[string]any)
		if sampleNumber(a["final_start"]) == sampleNumber(b["final_start"]) {
			return sampleNumber(a["final_end"]) < sampleNumber(b["final_end"])
		}
		return sampleNumber(a["final_start"]) < sampleNumber(b["final_start"])
	})
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
