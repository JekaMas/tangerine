package app

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"net/http"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

// RenderPreparation continues frozen text and mutations with resumable speech.
func (s *Server) RenderPreparation(ctx context.Context, id, key string, attempt int, client *http.Client) (map[string]any, error) {
	ctx, cancel := context.WithTimeout(ctx, OverallDeadline)
	defer cancel()
	if _, e := uuid.Parse(id); e != nil || attempt < 1 {
		return nil, ErrConflict
	}
	body, _ := lab.Canonical(map[string]any{"preparation_id": id, "render_attempt": attempt})
	op, e := s.Store.ReserveOperation(ctx, OperationRequest{Name: "speech_render", Key: key, Path: "/api/v1/cases:render", Body: body})
	if e != nil {
		return nil, e
	}
	if op.State == "complete" || op.State == "failed" {
		p, e := s.Store.speechActionResult(ctx, op.ID)
		if e == nil && op.State == "failed" {
			return p, &provider.Failure{Code: p["last_failure"].(map[string]any)["code"].(string)}
		}
		return p, e
	}
	p, e := s.Store.Preparation(ctx, id)
	if e != nil {
		return nil, e
	}
	states := p["phase_states"].(map[string]any)
	if states["mutation"] != "complete" {
		return p, ErrConflict
	}
	if states["render"] == "complete" {
		e = s.Store.acknowledgeSpeech(ctx, op.ID, id)
		return p, e
	}
	count, e := s.Store.speechAttemptCount(ctx, id)
	if e != nil {
		return p, e
	}
	if attempt != count+1 {
		return p, ErrConflict
	}
	if e = s.Store.claimSpeech(ctx, op.ID, id); e != nil {
		return p, e
	}
	defer func() {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer done()
		s.Store.releaseSpeech(end, op.ID)
	}()
	if e = s.Store.takePreparation(ctx, p, op.ID, "render"); e != nil {
		return p, e
	}
	raw, e := s.Store.ReadAsset(ctx, p["settings_asset_id"].(string))
	if e != nil {
		return p, e
	}
	var settings map[string]any
	if e = json.Unmarshal(raw, &settings); e != nil {
		return p, e
	}
	callErr := s.renderSpeech(ctx, p, settings, op, client)
	rev := int64(p["revision"].(float64))
	p["revision"] = float64(rev + 1)
	p["updated_at"] = time.Now().UTC().Format(time.RFC3339Nano)
	p["active_operation_id"] = nil
	if callErr != nil {
		code, message := speechPublicFailure(callErr)
		states["render"] = "failed"
		p["last_failure"] = map[string]any{"code": code, "message": message, "request_id": op.ID, "retryable": true, "object_id": nil, "details": []any{}}
	} else {
		states["render"] = "complete"
		p["last_failure"] = nil
	}
	end, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer done()
	words := 0
	if id, ok := p["mutation_manifest_asset_id"].(string); ok {
		if raw, err := s.Store.ReadAsset(end, id); err == nil {
			var manifest map[string]any
			_ = json.Unmarshal(raw, &manifest)
			if value, ok := manifest["canonical_word_count"].(float64); ok {
				words = int(value)
			}
		}
	}
	if e = s.Store.checkpoint(end, p, &rev, op.ID, callErr == nil, words); e != nil {
		return p, e
	}
	return p, callErr
}

func (s *Server) renderSpeech(ctx context.Context, p, settings map[string]any, op Operation, client *http.Client) error {
	var frozen, progress map[string]any
	if id, ok := p["render_plan_asset_id"].(string); ok {
		raw, e := s.Store.ReadAsset(ctx, id)
		if e != nil {
			return e
		}
		if e = json.Unmarshal(raw, &frozen); e != nil {
			return e
		}
	}
	if frozen == nil {
		raw, e := s.Store.ReadAsset(ctx, settings["speech_registry_asset_id"].(string))
		if e != nil {
			return e
		}
		profile, e := speechProfile(settings, raw)
		if e != nil {
			return e
		}
		raw, e = s.Store.ReadAsset(ctx, p["mutated_asset_id"].(string))
		if e != nil {
			return e
		}
		var candidate map[string]any
		if e = json.Unmarshal(raw, &candidate); e != nil {
			return e
		}
		plan, e := compileSpeechPlan(p["id"].(string), settings, candidate, profile)
		if e != nil {
			return e
		}
		if e = s.Store.ensureSpeechCase(ctx, plan, p["candidate_id"].(string)); e != nil {
			return e
		}
		prepared, e := s.speechCall(ctx, "/internal/v1/plan", map[string]any{"profile": profile, "plan": plan}, client)
		if e != nil {
			return e
		}
		manifestBytes, e := s.Store.ReadAsset(ctx, p["mutation_manifest_asset_id"].(string))
		if e != nil {
			return e
		}
		frozen = map[string]any{"mutation_manifest_sha256": lab.Hash(json.RawMessage(manifestBytes)), "plan": plan, "profile": profile, "pieces": prepared["pieces"], "model_context": prepared["model_context"]}
		raw, _ = lab.Canonical(frozen)
		asset, e := s.Store.saveProviderBytes(ctx, raw, "canonical_json")
		if e != nil {
			return e
		}
		p["render_plan_asset_id"] = asset.ID
	}
	if id, ok := p["render_progress_asset_id"].(string); ok {
		raw, e := s.Store.ReadAsset(ctx, id)
		if e != nil {
			return e
		}
		if e = json.Unmarshal(raw, &progress); e != nil {
			return e
		}
	}
	plan := frozen["plan"].(map[string]any)
	profile := frozen["profile"].(map[string]any)
	requests, ok := frozen["pieces"].([]any)
	if !ok || len(requests) == 0 {
		return &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
	}
	if progress == nil {
		pieces := []any{}
		for i, value := range requests {
			request := value.(map[string]any)
			pieceID := uuid.NewSHA1(uuid.NameSpaceOID, []byte(fmt.Sprintf("%s:%s:%d", p["id"], plan["plan_sha256"], i))).String()
			pieces = append(pieces, map[string]any{"id": pieceID, "utterance_id": request["utterance_id"], "operation_indexes": []any{float64(0)}, "request_sha256": lab.Hash(map[string]any{"profile": profile, "render_plan_sha256": plan["plan_sha256"], "request": request}), "source_asset_id": nil, "asset_id": nil, "audio_sha256": nil, "sample_count": nil, "state": "pending", "receipt_ids": []any{}, "last_error_asset_id": nil})
		}
		progress = map[string]any{"schema_version": "2.0.0", "id": uuid.NewString(), "preparation_id": p["id"], "revision": float64(0), "render_plan_sha256": plan["plan_sha256"], "production_plan_asset_id": nil, "pieces": pieces, "assembled_asset_id": nil, "assembled_sha256": nil, "sample_map_asset_id": nil}
	}
	for _, value := range progress["pieces"].([]any) {
		piece := value.(map[string]any)
		if piece["state"] == "running" {
			piece["state"] = "interrupted"
		}
	}
	if e := s.saveSpeechProgress(ctx, p, progress, op.ID); e != nil {
		return e
	}
	for i, value := range progress["pieces"].([]any) {
		piece := value.(map[string]any)
		if piece["state"] == "complete" {
			continue
		}
		if e := ctx.Err(); e != nil {
			return &provider.Failure{Code: "SPEECH_TIMEOUT"}
		}
		if turn := requests[i].(map[string]any); len(mutationAcousticEdits(turn)) > 0 {
			piece["state"] = "running"
			if e := s.saveSpeechProgress(ctx, p, progress, op.ID); e != nil {
				return e
			}
			if e := s.renderAcousticPiece(ctx, p, settings, frozen, progress, piece, turn, op.ID, client); e != nil {
				piece["state"] = "failed"
				end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
				_ = s.saveSpeechProgress(end, p, progress, op.ID)
				done()
				return e
			}
			continue
		}
		piece["state"] = "running"
		if e := s.saveSpeechProgress(ctx, p, progress, op.ID); e != nil {
			return e
		}
		result, receipt, callErr := s.Store.completedSpeechPiece(ctx, piece["id"].(string))
		if callErr != nil {
			return callErr
		}
		if result == nil {
			result, receipt, callErr = s.dispatchSpeechPiece(ctx, p, piece, profile, settings, requests[i], client)
		}
		if receipt != "" {
			piece["receipt_ids"] = append(piece["receipt_ids"].([]any), receipt)
		}
		if callErr != nil {
			piece["state"] = "failed"
			failureBytes, _ := lab.Canonical(map[string]any{"code": fmt.Sprint(callErr)})
			end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
			failureAsset, e := s.Store.saveProviderBytes(end, failureBytes, "canonical_json")
			if e == nil {
				piece["last_error_asset_id"] = failureAsset.ID
				e = s.saveSpeechProgress(end, p, progress, op.ID)
			}
			done()
			if e != nil {
				return e
			}
			return callErr
		}
		encoded, ok := result["audio_base64"].(string)
		if !ok {
			return &provider.Failure{Code: "AUDIO_FORMAT_INVALID"}
		}
		audio, e := base64.StdEncoding.DecodeString(encoded)
		if e != nil || len(audio) < 44 {
			return &provider.Failure{Code: "AUDIO_FORMAT_INVALID"}
		}
		asset, e := s.saveAudioBytes(ctx, audio)
		if e != nil {
			return e
		}
		piece["asset_id"] = asset.ID
		piece["source_asset_id"] = asset.ID
		piece["audio_sha256"] = asset.SHA
		piece["sample_count"] = float64((len(audio) - 44) / 2)
		piece["state"] = "complete"
		piece["last_error_asset_id"] = nil
		if e = s.saveSpeechProgress(ctx, p, progress, op.ID); e != nil {
			return e
		}
	}
	return s.assembleSpeech(ctx, p, settings, frozen, progress, requests, op.ID, client)
}
