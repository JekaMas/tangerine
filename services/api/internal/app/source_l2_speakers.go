package app

import (
	"context"
	"tangerine.local/api/internal/source"
)

// One small native metadata join per import/resume. The accepted source table is
// data; neither its bytes nor already projected transcript rows are re-admitted.
func (s *Storage) sourceL2Speakers(ctx context.Context, run SourceRun) (map[string]source.Row, error) {
	out := map[string]source.Row{}
	if !run.Frozen.Native || run.Frozen.Release.Source != "L2-ARCTIC" {
		return out, nil
	}
	rows, e := s.DB.Query(ctx, "SELECT native_row FROM source_row WHERE import_id=$1 AND table_name='speakers' ORDER BY member,ordinal", run.Report.ID)
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	duplicates := map[string]bool{}
	for rows.Next() {
		var raw []byte
		if e = rows.Scan(&raw); e != nil {
			return nil, e
		}
		var row source.Row
		if e = source.Decode(raw, &row); e != nil {
			return nil, e
		}
		key, _ := row["speaker"].(string)
		if _, exists := out[key]; exists {
			duplicates[key] = true
		}
		out[key] = row
	}
	// Ambiguous/missing declarations stay unknown, without guessing or preventing
	// unrelated/partial native source records from being used.
	for key := range duplicates {
		delete(out, key)
	}
	return out, rows.Err()
}
func sourceL2SpeakerProjection(m *source.Mapped, speakers map[string]source.Row, members map[string]source.Member) {
	if m.Table != "transcripts" {
		return
	}
	speaker, _ := source.L2Identity(m.Member)
	info, ok := speakers[speaker]
	if !ok {
		return
	}
	raw := m.Value["raw_metadata"].(map[string]any)
	raw["speaker_metadata"] = info
	member, _ := info["member"].(string)
	raw["speaker_metadata_asset_id"] = members[member].AssetID
	raw["speaker_metadata_locator"] = map[string]any{"member": member, "line_index": info["row"]}
	if cp, ok := m.Value["corpus_record"].(map[string]any); ok {
		cp["l1"] = info["native_language"]
	}
}
