package app

import (
	"context"
	"tangerine.local/api/internal/lab"
)

// Final mapping references each actual accepted piece and the final controller
// correspondence. Intermediate maps remain retained in acoustic stage lineage.
func (s *Server) acousticPieceRows(ctx context.Context, piece map[string]any, start int) ([]any, error) {
	rows := []any{}
	if state, ok := piece["acoustic_state"].(map[string]any); ok {
		steps := state["completed_steps"].([]any)
		if len(steps) > 0 {
			last := steps[len(steps)-1].(map[string]any)
			diagnostic, e := s.acousticRead(ctx, last["diagnostic_asset_id"].(string))
			if e != nil {
				return nil, e
			}
			for _, value := range diagnostic["sample_rows"].([]any) {
				row := map[string]any{}
				for k, v := range value.(map[string]any) {
					row[k] = v
				}
				row["final_start"] = float64(start) + row["final_start"].(float64)
				row["final_end"] = float64(start) + row["final_end"].(float64)
				rows = append(rows, row)
			}
			return rows, nil
		}
	}
	rows = append(rows, map[string]any{"piece_id": piece["id"], "source_audio_sha256": piece["audio_sha256"], "source_sample_rate_hz": 24000, "source_start": 0, "source_end": piece["sample_count"], "final_start": start, "final_end": start + int(piece["sample_count"].(float64)), "kind": "copy", "transform_id": nil, "crossfade_group_id": nil})
	return rows, nil
}
func sampleGap(pieceID any, start, gap int) map[string]any {
	return map[string]any{"piece_id": pieceID, "source_audio_sha256": nil, "source_sample_rate_hz": nil, "source_start": 0, "source_end": 0, "final_start": start, "final_end": start + gap, "kind": "gap", "transform_id": nil, "crossfade_group_id": nil}
}
func actualSampleMap(planSHA, outputSHA any, count int, rows []any) map[string]any {
	return map[string]any{"schema_version": "2.0.0", "id": lab.Hash(map[string]any{"output": outputSHA, "rows": rows}), "render_plan_sha256": planSHA, "output_audio_sha256": outputSHA, "sample_rate_hz": 24000, "sample_count": count, "rows": rows}
}
