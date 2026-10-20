package app

// This owner persists acoustic stages. Numerical/linguistic work belongs to the
// private speech worker; the preparation CAS remains the only progress head.
import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"net/http"
	"tangerine.local/api/internal/lab"
	"time"
)

func acousticChild(piece map[string]any, stage string) map[string]any {
	return map[string]any{"id": uuid.NewSHA1(uuid.NameSpaceOID, []byte(piece["id"].(string)+":"+stage)).String()}
}
func (s *Server) acousticCall(ctx context.Context, p, piece, profile, settings map[string]any, stage, path string, request map[string]any, client *http.Client) (map[string]any, string, error) {
	child := acousticChild(piece, stage)
	result, receipt, e := s.Store.completedSpeechPiece(ctx, child["id"].(string))
	if e != nil || result != nil {
		return result, receipt, e
	}
	result, receipt, e = s.dispatchSpeechStage(ctx, p, child, profile, settings, path, request, client)
	if e != nil {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
		defer done()
		detail := map[string]any{"error": fmt.Sprint(e), "native": result, "stage": stage}
		if id, err := s.acousticDocument(end, detail); err == nil {
			piece["last_error_asset_id"] = id
		}
	}
	return result, receipt, e
}
func (s *Server) acousticDocument(ctx context.Context, value any) (string, error) {
	raw, e := lab.Canonical(value)
	if e != nil {
		return "", e
	}
	a, e := s.Store.saveProviderBytes(ctx, raw, "canonical_json")
	return a.ID, e
}
func (s *Server) acousticRead(ctx context.Context, id string) (map[string]any, error) {
	raw, e := s.Store.ReadAsset(ctx, id)
	if e != nil {
		return nil, e
	}
	var value map[string]any
	e = json.Unmarshal(raw, &value)
	return value, e
}
func (s *Server) acousticAudio(ctx context.Context, encoded string) (Asset, error) {
	raw, e := base64.StdEncoding.DecodeString(encoded)
	if e != nil {
		return Asset{}, e
	}
	return s.saveAudioBytes(ctx, raw)
}

// Source completion is durable before resolution/transform dispatch. A retry
// reuses accepted audio and native timing, including a completed child whose
// parent checkpoint was lost, through the existing operation/receipt owner.
func (s *Server) renderAcousticPiece(ctx context.Context, p, settings, frozen, progress, piece, turn map[string]any, operation string, client *http.Client) error {
	profile := frozen["profile"].(map[string]any)
	state, _ := piece["acoustic_state"].(map[string]any)
	if state == nil {
		source, receipt, e := s.Store.completedSpeechPiece(ctx, piece["id"].(string))
		if e != nil {
			return e
		}
		if source == nil {
			source, receipt, e = s.dispatchSpeechPiece(ctx, p, piece, profile, settings, turn, client)
		}
		if receipt != "" {
			piece["receipt_ids"] = append(piece["receipt_ids"].([]any), receipt)
		}
		if e != nil {
			return e
		}
		original, e := s.acousticAudio(ctx, source["audio_base64"].(string))
		if e != nil {
			return e
		}
		native := source["receipt"].(map[string]any)["native"].(map[string]any)
		nativeID, e := s.acousticDocument(ctx, native)
		if e != nil {
			return e
		}
		state = map[string]any{"native_asset_id": nativeID, "current_asset_id": original.ID, "completed_steps": []any{}, "next_step": float64(0)}
		pairs := map[string]any{}
		if entries, ok := native["paired_mutations"].(map[string]any); ok {
			for unit, value := range entries {
				altered, err := s.acousticAudio(ctx, value.(map[string]any)["audio_base64"].(string))
				if err != nil {
					return err
				}
				pairs[unit] = altered.ID
			}
		}
		if paired, ok := native["paired_mutation"].(map[string]any); ok {
			altered, err := s.acousticAudio(ctx, paired["audio_base64"].(string))
			if err != nil {
				return err
			}
			for _, value := range turn["acoustic_edits"].([]any) {
				pairs[value.(map[string]any)["unit_id"].(string)] = altered.ID
			}
		}
		state["paired_assets"] = pairs

		piece["source_asset_id"] = original.ID
		piece["acoustic_state"] = state
		if e = s.saveSpeechProgress(ctx, p, progress, operation); e != nil {
			return e
		}
	}
	edits := turn["acoustic_edits"].([]any)
	for index := int(state["next_step"].(float64)); index < len(edits); index++ {
		currentID := state["current_asset_id"].(string)
		audio, e := s.Store.ReadAsset(ctx, currentID)
		if e != nil {
			return e
		}
		native, e := s.acousticRead(ctx, state["native_asset_id"].(string))
		if e != nil {
			return e
		}
		stepTurn := map[string]any{}
		for k, v := range turn {
			stepTurn[k] = v
		}
		stepTurn["acoustic_edits"] = []any{edits[index]}
		stage := fmt.Sprintf("step-%d", index)
		var step map[string]any
		var productionID string
		var receipt string
		if id, ok := state["active_production_plan_asset_id"].(string); ok {
			production, e := s.acousticRead(ctx, id)
			if e != nil {
				return e
			}
			step = production["steps"].([]any)[0].(map[string]any)
			productionID = id
		} else {
			productionID, step, e = s.recoveredAcousticProduction(ctx, piece, stage)
			if e != nil {
				return e
			}
			if productionID == "" {
				resolved, r, e := s.acousticCall(ctx, p, piece, profile, settings, stage+":resolve", "/internal/v1/resolve", map[string]any{"audio_base64": base64.StdEncoding.EncodeToString(audio), "native": native, "turn": stepTurn, "piece_id": piece["id"]}, client)
				if r != "" {
					piece["receipt_ids"] = append(piece["receipt_ids"].([]any), r)
				}
				if e != nil {
					return e
				}
				step = resolved["steps"].([]any)[0].(map[string]any)
				step["id"] = uuid.NewSHA1(uuid.NameSpaceOID, []byte(piece["id"].(string)+stage)).String()
				production := map[string]any{"schema_version": "2.0.0", "id": uuid.NewString(), "case_version_id": frozen["plan"].(map[string]any)["case_version_id"], "mutation_manifest_sha256": frozen["mutation_manifest_sha256"], "render_plan_sha256": progress["render_plan_sha256"], "controller_registry_sha256": settings["production_registry_sha256"], "steps": []any{step}}
				productionID, e = s.acousticDocument(ctx, production)
				if e != nil {
					return e
				}
			}
			progress["production_plan_asset_id"] = productionID
			state["active_production_plan_asset_id"] = productionID
			if e = s.saveSpeechProgress(ctx, p, progress, operation); e != nil {
				return e
			}
		}
		request := map[string]any{"audio_base64": base64.StdEncoding.EncodeToString(audio), "step": step, "native": native, "production_plan_asset_id": productionID, "piece_id": piece["id"]}
		if step["controller"] == "phone_pair" {
			raw, e := s.Store.ReadAsset(ctx, state["paired_assets"].(map[string]any)[step["unit_id"].(string)].(string))
			if e != nil {
				return e
			}
			request["replacement_base64"] = base64.StdEncoding.EncodeToString(raw)
		}
		transformed, receipt, e := s.acousticCall(ctx, p, piece, profile, settings, stage+":transform", "/internal/v1/transform", request, client)
		if receipt != "" {
			piece["receipt_ids"] = append(piece["receipt_ids"].([]any), receipt)
		}
		if e != nil {
			return e
		}
		output, e := s.acousticAudio(ctx, transformed["audio_base64"].(string))
		if e != nil {
			return e
		}
		diagnosticID, e := s.acousticDocument(ctx, transformed)
		if e != nil {
			return e
		}
		nativeID := state["native_asset_id"]
		if transformed["native"] != nil {
			nativeID, e = s.acousticDocument(ctx, transformed["native"])
			if e != nil {
				return e
			}
		}
		state["completed_steps"] = append(state["completed_steps"].([]any), map[string]any{"production_plan_asset_id": productionID, "source_asset_id": currentID, "result_asset_id": output.ID, "diagnostic_asset_id": diagnosticID, "unit_id": step["unit_id"]})
		state["current_asset_id"] = output.ID
		state["native_asset_id"] = nativeID
		if n, ok := transformed["native"].(map[string]any); ok {
			intervals := map[string]any{}
			rows, _ := n["acoustic_scopes"].([]any)
			for _, v := range rows {
				r := v.(map[string]any)
				intervals[r["unit_id"].(string)] = map[string]any{"start": r["start"], "end": r["end"]}
			}
			piece["unit_intervals"] = intervals
		}
		state["next_step"] = float64(index + 1)
		delete(state, "active_production_plan_asset_id")
		piece["asset_id"] = output.ID
		piece["audio_sha256"] = output.SHA
		piece["sample_count"] = transformed["sample_count"]
		if e = s.saveSpeechProgress(ctx, p, progress, operation); e != nil {
			return e
		}
	}
	piece["state"] = "complete"
	piece["last_error_asset_id"] = nil
	return s.saveSpeechProgress(ctx, p, progress, operation)
}

// A completed transform receipt retains the original resolved child even if its
// parent journal response was lost. Reuse that accepted identity, not a new UUID.
func (s *Server) recoveredAcousticProduction(ctx context.Context, piece map[string]any, stage string) (string, map[string]any, error) {
	result, receipt, e := s.Store.completedSpeechPiece(ctx, acousticChild(piece, stage+":transform")["id"].(string))
	if e != nil || result == nil {
		return "", nil, e
	}
	d, e := s.Store.ReadDocument(ctx, receipt)
	if e != nil {
		return "", nil, e
	}
	var r map[string]any
	if e = json.Unmarshal(d.Payload, &r); e != nil {
		return "", nil, e
	}
	input, e := s.acousticRead(ctx, r["wire_request_asset_id"].(string))
	if e != nil {
		return "", nil, e
	}
	id := input["production_plan_asset_id"].(string)
	production, e := s.acousticRead(ctx, id)
	if e != nil {
		return "", nil, e
	}
	return id, production["steps"].([]any)[0].(map[string]any), nil
}
