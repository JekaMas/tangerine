package app

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"go.yaml.in/yaml/v3"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
)

// projectSpeechKey copies the accepted key and uses containing-turn intervals
// from actual piece sample counts. No character-proportional timing is invented.
func projectSpeechKey(settings, candidate, plan, progress map[string]any, audioID, audioSHA, taxonomyVersion string) map[string]any {
	blueprint := settings["blueprint"].(map[string]any)
	intervals := map[string]map[string]any{}
	acousticIntervals := map[string][]any{}
	samples := 0
	receipts := []any{}
	for i, v := range progress["pieces"].([]any) {
		piece := v.(map[string]any)
		turn := plan["pieces"].([]any)[i].(map[string]any)
		start := samples
		end := start + int(piece["sample_count"].(float64))
		id := piece["utterance_id"].(string)
		if intervals[id] == nil {
			intervals[id] = map[string]any{"start_ms": start / 24, "end_ms": (end + 23) / 24}
		} else {
			intervals[id]["end_ms"] = (end + 23) / 24
		}
		samples = end + int(turn["gap_after_ms"].(float64))*24
		receipts = append(receipts, piece["receipt_ids"].([]any)...)
		seenAcoustic := map[string]bool{}
		for _, v := range mutationAcousticEdits(turn) {
			edit := v.(map[string]any)
			id := edit["unit_id"].(string)
			if seenAcoustic[id] {
				continue
			}
			seenAcoustic[id] = true
			a, b := start, end
			if rows, ok := piece["unit_intervals"].(map[string]any); ok {
				if row, ok := rows[id].(map[string]any); ok {
					a = start + int(row["start"].(float64))
					b = start + int(row["end"].(float64))
				}
			}
			acousticIntervals[id] = append(acousticIntervals[id], map[string]any{"start_ms": a / 24, "end_ms": (b + 23) / 24})
		}
	}
	speakers := []any{}
	for _, v := range blueprint["speakers"].([]any) {
		sp := v.(map[string]any)
		speakers = append(speakers, map[string]any{"id": sp["id"], "voice_profile_id": sp["voice_profile_id"], "l1": sp["l1"], "learner_cefr": sp["learner_cefr"], "requested_accent": sp["requested_accent"], "observed_accent_notes": nil, "accent_evidence": "not_verified"})
	}
	utterances := []any{}
	for _, v := range candidate["utterances"].([]any) {
		u := v.(map[string]any)
		utterances = append(utterances, map[string]any{"id": u["id"], "speaker_id": u["speaker_id"], "canonical_text": u["canonical_text"], "surface_text": u["surface_text"], "audio_interval": intervals[u["id"].(string)]})
	}
	units := []any{}
	for _, v := range candidate["planned_units"].([]any) {
		accepted := v.(map[string]any)
		unit := map[string]any{}
		for k, value := range accepted {
			unit[k] = value
		}
		ranges := []any{}
		for _, id := range accepted["utterance_ids"].([]any) {
			ranges = append(ranges, intervals[id.(string)])
		}
		if actual := acousticIntervals[accepted["id"].(string)]; len(actual) > 0 {
			ranges = actual
		}
		unit["audio_intervals"] = ranges
		unit["context_evidence"] = []any{map[string]any{"source_id": "GENERATED-EXERCISE", "locator": "public_context", "evidence_hash": lab.Hash(blueprint["public_context"])}}
		unit["evidence_ids"] = receipts
		unit["verification"] = "candidate"
		unit["difficulty"] = "unrated"
		unit["difficulty_evidence_ref"] = nil
		unit["source"] = map[string]any{"source_id": "GENERATED-EXERCISE", "source_record_id": nil, "rights_approval_id": nil, "uses": settings["configuration"].(map[string]any)["intended_uses"], "status": "approved", "licence_evidence_hash": nil}
		units = append(units, unit)
	}
	key := map[string]any{"schema_version": "2.0.0", "case_version_id": plan["plan"].(map[string]any)["case_version_id"], "taxonomy_version": taxonomyVersion, "status": "rendered", "public_context": blueprint["public_context"], "variety_policy": blueprint["variety_policy"], "audio": map[string]any{"asset_id": audioID, "sha256": audioSHA, "duration_ms": (samples + 23) / 24, "sample_rate_hz": 24000, "channels": 1, "origin": "synthetic", "source_profile_id": "GENERATED-EXERCISE"}, "speakers": speakers, "utterances": utterances, "units": units, "review_decisions": []any{}, "content_provenance_ids": []any{}, "verification_policy_version": "2.0.0"}
	content := map[string]any{}
	for _, field := range []string{"public_context", "variety_policy", "audio", "speakers", "utterances", "units", "taxonomy_version", "verification_policy_version"} {
		content[field] = key[field]
	}
	key["case_sha256"] = lab.Hash(content)
	return key
}
func (s *Server) saveSpeechKey(ctx context.Context, p, settings, frozen, progress map[string]any) error {
	if p["key_id"] != nil {
		return nil
	}
	raw, e := s.Store.ReadAsset(ctx, p["mutated_asset_id"].(string))
	if e != nil {
		return e
	}
	var candidate map[string]any
	if e = json.Unmarshal(raw, &candidate); e != nil {
		return e
	}
	taxonomyBytes, e := s.Store.ReadAsset(ctx, settings["taxonomy_registry_asset_id"].(string))
	if e != nil {
		return e
	}
	var taxonomy map[string]any
	if e = yaml.Unmarshal(taxonomyBytes, &taxonomy); e != nil {
		return e
	}
	key := projectSpeechKey(settings, candidate, frozen, progress, p["audio_asset_id"].(string), p["audio_sha256"].(string), taxonomy["version"].(string))
	id, e := s.Store.saveGroundTruth(ctx, key)
	if e == nil {
		p["key_id"] = id
	}
	return e
}

// Newly produced/imported complete keys share one schema admission and immutable write.
func (s *Storage) saveGroundTruth(ctx context.Context, key map[string]any) (string, error) {
	raw, e := lab.Canonical(key)
	if e != nil {
		return "", e
	}
	c, raw, e := contracts.Validate("ground-truth", "2.0.0", raw)
	if e != nil {
		return "", fmt.Errorf("new render key: %w", e)
	}
	id := uuid.NewString()
	w := DocumentWrite{ID: id, Kind: "ground-truth", Version: c.Version, Scope: "local", Payload: raw}
	d := SavedDocument{ID: id, Kind: w.Kind, Version: w.Version, SchemaSHA: c.SHA, SHA: contracts.Digest(raw), Payload: raw}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return "", e
	}
	defer tx.Rollback(context.Background())
	if e = insertDocument(ctx, tx, w, d); e != nil {
		return "", e
	}
	return id, tx.Commit(ctx)
}
