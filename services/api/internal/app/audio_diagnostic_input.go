package app

// This owner selects trusted saved lineage. It never re-audits accepted bytes.
import (
	"context"
	"encoding/json"
	"github.com/jackc/pgx/v5"
	"strings"
	"tangerine.local/api/internal/provider"
)

type AudioMeasureRequest struct {
	Case     string   `json:"case_version_id"`
	AudioSHA string   `json:"audio_sha256"`
	Methods  []string `json:"method_ids"`
}
type diagnosticFrozen struct {
	Key, Configuration, Manifest, Progress map[string]any
	Audio                                  []byte
	Samples                                int64
	Canonical, Surface                     string
}

func (s *Storage) diagnosticInputs(ctx context.Context, r AudioMeasureRequest) (diagnosticFrozen, error) {
	f := diagnosticFrozen{}
	if err := s.reviewSourceAllowed(ctx, r.Case); err != nil {
		return f, err
	}
	doc, err := s.ReadDocument(ctx, r.Case)
	if err != nil {
		return f, err
	}
	if doc.Kind != "ground-truth" {
		return f, ErrReference
	}
	if err = json.Unmarshal(doc.Payload, &f.Key); err != nil {
		return f, err
	}
	audio := f.Key["audio"].(map[string]any)
	if audio["sha256"] != r.AudioSHA {
		return f, ErrRevision
	}
	f.Audio, err = s.ReadAsset(ctx, audio["asset_id"].(string))
	if err != nil {
		return f, err
	}
	if err = s.DB.QueryRow(ctx, "SELECT sample_count FROM listening_case WHERE case_version_id=$1", r.Case).Scan(&f.Samples); err != nil {
		return f, err
	}
	f.Configuration, _, err = s.Configuration(ctx)
	if err != nil {
		return f, err
	}
	var manifest, progress *string
	err = s.DB.QueryRow(ctx, `WITH RECURSIVE ancestors(id) AS (SELECT $1::text UNION SELECT c.old_case_version_id::text FROM reviewed_case_successor c JOIN ancestors a ON c.new_case_version_id=a.id) SELECT d.payload->>'mutation_manifest_asset_id',d.payload->>'render_progress_asset_id' FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.kind='preparation-state' AND d.payload->>'key_id' IN (SELECT id FROM ancestors UNION SELECT source_key_id::text FROM listening_case l JOIN ancestors a ON a.id=l.case_version_id) LIMIT 1`, r.Case).Scan(&manifest, &progress)
	if err != nil && err != pgx.ErrNoRows {
		return f, err
	}
	if manifest != nil {
		if err = s.readInterpretationJSON(ctx, *manifest, &f.Manifest); err != nil {
			return f, err
		}
	}
	if progress != nil {
		if err = s.readInterpretationJSON(ctx, *progress, &f.Progress); err != nil {
			return f, err
		}
	}
	originals, presented := []string{}, []string{}
	for _, v := range f.Key["utterances"].([]any) {
		u := v.(map[string]any)
		originals = append(originals, u["canonical_text"].(string))
		presented = append(presented, u["surface_text"].(string))
	}
	f.Canonical, f.Surface = strings.Join(originals, "\n"), strings.Join(presented, "\n")
	return f, nil
}

func diagnosticMethod(method string) bool {
	switch method {
	case "ffmpeg-ebur128-v1", "praat-ac-v1", "faster-whisper-local-en-v1", "qwen25-omni-audio-v1", "gemini-audio-v1":
		return true
	}
	return false
}
func diagnosticProfile(c map[string]any, method string) (map[string]any, error) {
	if method != "qwen25-omni-audio-v1" && method != "gemini-audio-v1" {
		return map[string]any{"id": method, "provider": "local_audio_diagnostic", "model": method, "billing_mode": "local"}, nil
	}
	p, ok := c["audio_diagnostic_profile"].(map[string]any)
	if !ok {
		return nil, &provider.Failure{Code: "CAPABILITY_UNAVAILABLE"}
	}
	if method == "qwen25-omni-audio-v1" && (p["provider"] != "local_qwen25_omni" || p["billing_mode"] != "local") {
		return nil, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
	}
	if method == "gemini-audio-v1" && (p["provider"] != "gemini_interactions" || p["billing_mode"] != "free_tier" && p["billing_mode"] != "included_subscription") {
		return nil, &provider.Failure{Code: "PAID_USE_FORBIDDEN"}
	}
	return p, nil
}

func diagnosticIntent(f diagnosticFrozen, interval map[string]any) map[string]any {
	candidate := reviewCandidate(reviewClone(f.Key))
	selected := []any{}
	ids := []any{}
	features := []any{}
	seen := map[string]bool{}
	units := f.Key["units"].([]any)
	for i, v := range units {
		u := v.(map[string]any)
		overlap := false
		for _, v := range u["audio_intervals"].([]any) {
			a := v.(map[string]any)
			if a["start_ms"].(float64)*24 < interval["end"].(float64) && a["end_ms"].(float64)*24 > interval["start"].(float64) {
				overlap = true
			}
		}
		if !overlap {
			continue
		}
		p := candidate["planned_units"].([]any)[i].(map[string]any)
		r := p["realization"].(map[string]any)
		for _, k := range []string{"observed_ipa", "observed_pace_wpm", "observed_pause_ms"} {
			r[k] = nil
		}
		prosody, _ := r["prosody"].([]any)
		if len(prosody) == 0 && !seen["speech_realization"] {
			seen["speech_realization"] = true
			features = append(features, "speech_realization")
		}
		for _, v := range prosody {
			pr := v.(map[string]any)
			pr["observation"] = nil
			pr["evidence_ids"] = []any{}
			feature := pr["feature"].(string)
			if !seen[feature] {
				seen[feature] = true
				features = append(features, feature)
			}
		}
		selected = append(selected, p)
		ids = append(ids, u["id"])
	}
	if len(features) == 0 {
		features = []any{"speech_realization"}
	}
	edits := []any{}
	if f.Manifest != nil {
		if rows, ok := f.Manifest["acoustic_edits"].([]any); ok {
			for _, v := range rows {
				r := v.(map[string]any)
				for _, id := range ids {
					if r["unit_id"] == id {
						edits = append(edits, r)
						break
					}
				}
			}
		}
	}
	return map[string]any{"schema_version": "2.0.0", "case_version_id": f.Key["case_version_id"], "audio_sha256": f.Key["audio"].(map[string]any)["sha256"], "source_interval": interval, "canonical_text": f.Canonical, "surface_text": f.Surface, "units": ids, "features": features, "planned_units": selected, "acoustic_edits": edits, "reference_clip_asset_id": nil, "task_target": f.Key["public_context"]}
}
