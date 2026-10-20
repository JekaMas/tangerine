package app

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"go.yaml.in/yaml/v3"
	"net/http"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

// RenderPreparation is the foreground rendering owner. It never regenerates
// clean/mutated text or dispatches a previously completed piece on Resume.
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
		var document string
		if e = s.Store.DB.QueryRow(ctx, "SELECT result_document_id FROM operation WHERE id=$1", op.ID).Scan(&document); e != nil {
			return nil, e
		}
		d, e := s.Store.ReadDocument(ctx, document)
		if e != nil {
			return nil, e
		}
		var p map[string]any
		e = json.Unmarshal(d.Payload, &p)
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
		_, e = s.Store.DB.Exec(ctx, "UPDATE operation SET state='complete',subject_id=$2::text,result_document_id=(SELECT document_id FROM entity_head WHERE id=$2::text),finished_at=clock_timestamp() WHERE id=$1 AND state='reserved'", op.ID, id)
		return p, e
	}
	var count int
	e = s.Store.DB.QueryRow(ctx, "SELECT count(*) FROM operation WHERE operation_name='speech_render' AND subject_id=$1", id).Scan(&count)
	if e != nil {
		return p, e
	}
	if attempt != count+1 {
		return p, ErrConflict
	}
	claimed, e := s.Store.DB.Exec(ctx, "UPDATE operation SET state='running',subject_id=$2 WHERE id=$1 AND state='reserved'", op.ID, id)
	if e != nil {
		return p, e
	}
	if claimed.RowsAffected() != 1 {
		return p, &provider.Failure{Code: "LEASE_ACTIVE"}
	}
	defer func() {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer done()
		_, _ = s.Store.DB.Exec(end, "UPDATE operation SET state='interrupted',finished_at=clock_timestamp() WHERE id=$1 AND state='running'", op.ID)
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

func speechProfile(settings map[string]any, registry []byte) (map[string]any, error) {
	blueprint := settings["blueprint"].(map[string]any)
	id := blueprint["provider_profile_id"].(string)
	if rows, ok := settings["configuration"].(map[string]any)["speech_profiles"].([]any); ok {
		for _, v := range rows {
			p := v.(map[string]any)
			if p["id"] == id {
				return p, nil
			}
		}
	}
	var catalog map[string]any
	if e := yaml.Unmarshal(registry, &catalog); e != nil {
		return nil, e
	}
	for _, v := range catalog["profiles"].([]any) {
		p := v.(map[string]any)
		if p["id"] != id {
			continue
		}
		voices := []any{}
		for locale, items := range p["voices"].(map[string]any) {
			for _, voice := range items.([]any) {
				voices = append(voices, map[string]any{"id": voice, "locale": locale, "accent_description": nil})
			}
		}
		model, _ := p["model"].(string)
		mode := "unknown"
		if p["provider"] == "local_kokoro" {
			mode = "local"
		}
		return map[string]any{"id": id, "provider": p["provider"], "adapter_version": id, "model": model, "endpoint": nil, "billing_mode": mode, "account_tier": nil, "overage_disabled": nil, "voices": voices, "capabilities": p["capabilities"], "voice_settings": map[string]any{"speed": nil}}, nil
	}
	return nil, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
}

func compileSpeechPlan(preparation string, settings, candidate, profile map[string]any) (map[string]any, error) {
	blueprint := settings["blueprint"].(map[string]any)
	speakers := map[string]map[string]any{}
	for _, value := range blueprint["speakers"].([]any) {
		sp := value.(map[string]any)
		speakers[sp["id"].(string)] = sp
	}
	locale := blueprint["variety_policy"].(map[string]any)["target_locale"]
	gap := float64(250)
	if configuration, ok := settings["configuration"].(map[string]any); ok {
		if defaults, ok := configuration["preparation_defaults"].(map[string]any); ok {
			if v, ok := defaults["gap_after_ms"].(float64); ok {
				gap = v
			}
		}
	}
	turns := []any{}
	for _, value := range candidate["utterances"].([]any) {
		u := value.(map[string]any)
		sp := speakers[u["speaker_id"].(string)]
		if sp == nil {
			return nil, ErrReference
		}
		voice := sp["voice_profile_id"]
		selectedLocale := locale
		for _, v := range profile["voices"].([]any) {
			p := v.(map[string]any)
			if p["id"] == voice {
				selectedLocale = p["locale"]
				break
			}
		}
		turns = append(turns, map[string]any{"id": u["id"], "utterance_id": u["id"], "speaker_id": u["speaker_id"], "voice_id": voice, "locale": selectedLocale, "operations": []any{map[string]any{"kind": "text", "text": u["surface_text"]}}, "gap_after_ms": gap})
	}
	if edits, ok := candidate["acoustic_edits"].([]any); ok && len(edits) > 0 {
		return nil, &provider.Failure{Code: "ACOUSTIC_RENDER_REQUIRED"}
	}
	caseID := uuid.NewSHA1(uuid.NameSpaceOID, []byte(preparation+":speech-case")).String()
	plan := map[string]any{"schema_version": "2.0.0", "id": uuid.NewSHA1(uuid.NameSpaceOID, []byte(preparation+":speech-plan")).String(), "case_version_id": caseID, "blueprint_sha256": lab.Hash(blueprint), "provider_profile_id": profile["id"], "profile_sha256": lab.Hash(profile), "required_capabilities": []any{"plain_text", "multi_turn"}, "turns": turns, "audio_format": "riff_pcm_s16le_24000_mono"}
	plan["plan_sha256"] = speechPlanHash(plan)
	return plan, nil
}

func (s *Server) speechCall(ctx context.Context, path string, packet any, client *http.Client) (map[string]any, error) {
	if client == nil {
		client = &http.Client{Timeout: OverallDeadline, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	}
	var raw []byte
	var e error
	method := http.MethodGet
	if packet != nil {
		raw, e = lab.Canonical(packet)
		if e != nil {
			return nil, e
		}
		method = http.MethodPost
	}
	request, e := http.NewRequestWithContext(ctx, method, s.SpeechURL+path, bytes.NewReader(raw))
	if e != nil {
		return nil, e
	}
	request.Header.Set("Authorization", "Bearer "+s.speechToken)
	request.Header.Set("Content-Type", "application/json")
	response, e := client.Do(request)
	if e != nil {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		return nil, &provider.Failure{Code: "SPEECH_UNAVAILABLE"}
	}
	defer response.Body.Close()
	var output map[string]any
	if e = json.NewDecoder(response.Body).Decode(&output); e != nil {
		return nil, &provider.Failure{Code: "SPEECH_UNAVAILABLE"}
	}
	if response.StatusCode != 200 {
		code, _ := output["error"].(string)
		if code == "" {
			code = "SPEECH_UNAVAILABLE"
		}
		return output, &provider.Failure{Code: code}
	}
	return output, nil
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
		frozen = map[string]any{"plan": plan, "profile": profile, "pieces": prepared["pieces"], "model_context": prepared["model_context"]}
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
			pieces = append(pieces, map[string]any{"id": pieceID, "utterance_id": request["utterance_id"], "operation_indexes": []any{float64(0)}, "request_sha256": lab.Hash(request), "source_asset_id": nil, "asset_id": nil, "audio_sha256": nil, "sample_count": nil, "state": "pending", "receipt_ids": []any{}, "last_error_asset_id": nil})
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
		piece["state"] = "running"
		if e := s.saveSpeechProgress(ctx, p, progress, op.ID); e != nil {
			return e
		}
		result, receipt, callErr := s.completedSpeechPiece(ctx, piece["id"].(string))
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
		sampleMap = append(sampleMap, map[string]any{"piece_id": piece["id"], "source_start": 0, "source_end": end - start, "final_start": start, "final_end": end, "kind": "copy"})
		gap := int(requests[i].(map[string]any)["gap_after_ms"].(float64)) * 24
		pcm = append(pcm, make([]byte, gap*2)...)
		if gap > 0 {
			sampleMap = append(sampleMap, map[string]any{"piece_id": piece["id"], "source_start": end - start, "source_end": end - start, "final_start": end, "final_end": end + gap, "kind": "gap"})
		}
	}
	plannedPauses := []any{}
	for _, v := range sampleMap {
		row := v.(map[string]any)
		if row["kind"] == "gap" {
			plannedPauses = append(plannedPauses, []any{row["final_start"], row["final_end"]})
		}
	}
	quality, e := s.speechCall(ctx, "/internal/v1/quality", map[string]any{"pcm_base64": base64.StdEncoding.EncodeToString(pcm), "planned_pause_intervals": plannedPauses}, client)
	if e != nil {
		return e
	}
	audio := speechWAV(pcm)
	asset, e := s.saveAudioBytes(ctx, audio)
	if e != nil {
		return e
	}
	raw, _ := lab.Canonical(map[string]any{"clock": 24000, "intervals": sampleMap, "sample_count": len(pcm) / 2, "audio_sha256": asset.SHA, "quality": quality})
	mapping, e := s.Store.saveProviderBytes(ctx, raw, "canonical_json")
	if e != nil {
		return e
	}
	progress["assembled_asset_id"] = asset.ID
	progress["assembled_sha256"] = asset.SHA
	progress["sample_map_asset_id"] = mapping.ID
	if e = s.saveSpeechProgress(ctx, p, progress, op.ID); e != nil {
		return e
	}
	p["audio_asset_id"] = asset.ID
	p["audio_sha256"] = asset.SHA
	return s.saveSpeechKey(ctx, p, settings, frozen, progress)
}

func speechWAV(pcm []byte) []byte {
	out := make([]byte, 44, len(pcm)+44)
	copy(out, "RIFF")
	binary.LittleEndian.PutUint32(out[4:], uint32(len(pcm)+36))
	copy(out[8:], "WAVEfmt ")
	binary.LittleEndian.PutUint32(out[16:], 16)
	binary.LittleEndian.PutUint16(out[20:], 1)
	binary.LittleEndian.PutUint16(out[22:], 1)
	binary.LittleEndian.PutUint32(out[24:], 24000)
	binary.LittleEndian.PutUint32(out[28:], 48000)
	binary.LittleEndian.PutUint16(out[32:], 2)
	binary.LittleEndian.PutUint16(out[34:], 16)
	copy(out[36:], "data")
	binary.LittleEndian.PutUint32(out[40:], uint32(len(pcm)))
	return append(out, pcm...)
}
func (s *Server) saveAudioBytes(ctx context.Context, data []byte) (Asset, error) {
	body, _ := lab.Canonical(map[string]any{"sha256": contracts.Digest(data), "size": len(data)})
	a, e := s.Store.ReserveAsset(ctx, AssetRequest{Operation: OperationRequest{Name: "speech-audio", Key: uuid.NewString(), Path: "/speech/audio", Body: body}, SHA: contracts.Digest(data), Size: int64(len(data)), Purpose: "audio_delivery", MIME: "audio/wav"})
	if e != nil {
		return a, e
	}
	if _, e = s.Store.UploadAsset(ctx, a.ID, data); e != nil {
		return a, e
	}
	return s.Store.LinkAsset(ctx, a.ID, nil)
}
func (s *Server) saveSpeechProgress(ctx context.Context, p, progress map[string]any, operation string) error {
	progress["revision"] = progress["revision"].(float64) + 1
	raw, _ := lab.Canonical(progress)
	asset, e := s.Store.saveProviderBytes(ctx, raw, "canonical_json")
	if e != nil {
		return e
	}
	p["render_progress_asset_id"] = asset.ID
	rev := int64(p["revision"].(float64))
	p["revision"] = float64(rev + 1)
	p["updated_at"] = time.Now().UTC().Format(time.RFC3339Nano)
	return s.Store.checkpoint(ctx, p, &rev, operation, false)
}
func (s *Storage) ensureSpeechCase(ctx context.Context, plan map[string]any, candidate string) error {
	id := plan["case_version_id"].(string)
	var present bool
	if e := s.DB.QueryRow(ctx, "SELECT EXISTS(SELECT 1 FROM entity_head WHERE id=$1 AND kind='case-head')", id).Scan(&present); e != nil {
		return e
	}
	if present {
		return nil
	}
	d, e := s.ReadDocument(ctx, candidate)
	if e != nil {
		return e
	}
	raw, _ := lab.Canonical(map[string]any{"id": id, "revision": 0, "status": "draft", "candidate_id": candidate, "parent_case_version_id": nil, "ground_truth_id": nil, "delivery_asset_id": nil, "created_at": time.Now().UTC().Format(time.RFC3339Nano), "quarantine_open": false})
	_, e = s.WriteDocuments(ctx, []DocumentWrite{{ID: uuid.NewString(), Kind: "case-head", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: id, State: "draft"}, References: []Reference{{Pointer: "/candidate_id", ID: candidate, Scope: "local", Kind: "candidate-envelope", SHA: d.SHA, Relation: "candidate_id"}}}})
	return e
}

func (s *Server) speechPlayback(w http.ResponseWriter, r *http.Request) {
	p, e := s.Store.Preparation(r.Context(), r.PathValue("id"))
	if e != nil {
		preparationHTTPError(w, 404, "NOT_FOUND")
		return
	}
	if p["phase_states"].(map[string]any)["render"] != "complete" {
		preparationHTTPError(w, 409, "AUDIO_NOT_READY")
		return
	}
	audio, e := s.Store.ReadAsset(r.Context(), p["audio_asset_id"].(string))
	if e != nil {
		preparationHTTPError(w, 503, "STORAGE_UNAVAILABLE")
		return
	}
	w.Header().Set("Content-Type", "audio/wav")
	w.Header().Set("Cache-Control", "no-store")
	http.ServeContent(w, r, "exercise.wav", time.Time{}, bytes.NewReader(audio))
}
func (s *Server) speechRender(w http.ResponseWriter, r *http.Request) {
	var input struct {
		PreparationID string `json:"preparation_id"`
		Attempt       int    `json:"render_attempt"`
	}
	if e := DecodeJSON(w, r, &input); e != nil {
		preparationHTTPError(w, 400, "INVALID_JSON")
		return
	}
	if input.PreparationID != r.PathValue("id") {
		preparationHTTPError(w, 400, "CONSTRAINT_CONFLICT")
		return
	}
	p, e := s.RenderPreparation(r.Context(), input.PreparationID, r.Header.Get("Idempotency-Key"), input.Attempt, nil)
	if e != nil {
		code, _ := speechPublicFailure(e)
		writeJSON(w, 422, map[string]any{"preparation": speechSummary(p), "code": code})
		return
	}
	writeJSON(w, 200, speechSummary(p))
}
func speechSummary(p map[string]any) map[string]any {
	if p == nil {
		return nil
	}
	return map[string]any{"id": p["id"], "revision": p["revision"], "phase_states": p["phase_states"], "audio_available": p["phase_states"].(map[string]any)["render"] == "complete", "last_failure": p["last_failure"]}
}

func (s *Storage) finishSpeechCase(ctx context.Context, tx pgx.Tx, p map[string]any) error {
	raw, e := s.ReadAsset(ctx, p["render_plan_asset_id"].(string))
	if e != nil {
		return e
	}
	var frozen map[string]any
	if e = json.Unmarshal(raw, &frozen); e != nil {
		return e
	}
	id := frozen["plan"].(map[string]any)["case_version_id"]
	var current []byte
	var revision int64
	if e = tx.QueryRow(ctx, "SELECT d.payload,h.revision FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id=$1 AND h.kind='case-head' FOR UPDATE OF h", id).Scan(&current, &revision); e != nil {
		return e
	}
	var head map[string]any
	if e = json.Unmarshal(current, &head); e != nil {
		return e
	}
	head["revision"] = float64(revision + 1)
	head["status"] = "rendered"
	head["delivery_asset_id"] = p["audio_asset_id"]
	head["ground_truth_id"] = p["key_id"]
	raw, _ = lab.Canonical(head)
	write := DocumentWrite{ID: uuid.NewString(), Kind: "case-head", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: id.(string), Expected: &revision, State: "rendered"}}
	var sha string
	if e = tx.QueryRow(ctx, "SELECT payload_sha256 FROM document WHERE id=$1", head["candidate_id"]).Scan(&sha); e != nil {
		return e
	}
	write.References = append(write.References, Reference{Pointer: "/candidate_id", ID: head["candidate_id"].(string), Scope: "local", Kind: "candidate-envelope", SHA: sha, Relation: "candidate_id"})
	if e = tx.QueryRow(ctx, "SELECT payload_sha256 FROM document WHERE id=$1", p["key_id"]).Scan(&sha); e != nil {
		return e
	}
	write.References = append(write.References, Reference{Pointer: "/ground_truth_id", ID: p["key_id"].(string), Scope: "local", Kind: "ground-truth", SHA: sha, Relation: "key"})
	ref, e := s.assetByteReference(ctx, p["audio_asset_id"].(string), "/delivery_asset_id", "audio")
	if e != nil {
		return e
	}
	write.References = append(write.References, ref)
	saved, e := validateDocument(write)
	if e != nil {
		return e
	}
	if e = insertDocument(ctx, tx, write, saved); e != nil {
		return e
	}
	return validateGraph(ctx, tx, write.ID)
}

func speechProfiles(configuration map[string]any) []map[string]any {
	result := []map[string]any{}
	if rows, ok := configuration["speech_profiles"].([]any); ok {
		for _, row := range rows {
			result = append(result, row.(map[string]any))
		}
	}
	return result
}

func (s *Server) completedSpeechPiece(ctx context.Context, piece string) (map[string]any, string, error) {
	var raw []byte
	var receipt string
	e := s.Store.DB.QueryRow(ctx, "SELECT d.payload,d.id FROM operation o JOIN document d ON d.id=o.result_document_id WHERE o.operation_name='speech-inference' AND o.subject_id=$1 AND o.state='complete' ORDER BY o.started_at DESC LIMIT 1", piece).Scan(&raw, &receipt)
	if e == pgx.ErrNoRows {
		return nil, "", nil
	}
	if e != nil {
		return nil, "", e
	}
	var native map[string]any
	if e = json.Unmarshal(raw, &native); e != nil {
		return nil, "", e
	}
	raw, e = s.Store.ReadAsset(ctx, native["wire_response_asset_id"].(string))
	if e != nil {
		return nil, "", e
	}
	var result map[string]any
	e = json.Unmarshal(raw, &result)
	return result, receipt, e
}
func (s *Server) dispatchSpeechPiece(ctx context.Context, p, piece, profile, settings map[string]any, turn any, client *http.Client) (map[string]any, string, error) {
	deadline, _ := ctx.Deadline()
	timeout := time.Until(deadline).Seconds()
	request := map[string]any{"profile": profile, "turn": turn, "timeout_seconds": timeout}
	input, _ := lab.Canonical(request)
	inputAsset, e := s.Store.saveProviderBytes(ctx, input, "provider_input")
	if e != nil {
		return nil, "", e
	}
	child, e := s.Store.ReserveOperation(ctx, OperationRequest{Name: "speech-inference", Key: uuid.NewString(), Path: "/speech/piece", Body: input})
	if e != nil {
		return nil, "", e
	}
	if _, e = s.Store.DB.Exec(ctx, "UPDATE operation SET state='running',subject_id=$2 WHERE id=$1 AND state='reserved'", child.ID, piece["id"]); e != nil {
		return nil, "", e
	}
	started := time.Now().UTC()
	result, callErr := s.speechCall(ctx, "/internal/v1/piece", request, client)
	finished := time.Now().UTC()
	response, _ := lab.Canonical(result)
	evidenceCtx, evidenceDone := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer evidenceDone()
	responseAsset, e := s.Store.saveProviderBytes(evidenceCtx, response, "provider_output")
	if e != nil {
		return nil, "", e
	}
	receipt, e := s.saveSpeechEvidence(evidenceCtx, child, profile, settings["configuration"].(map[string]any), inputAsset, responseAsset, started, finished, callErr)
	if e != nil {
		return nil, "", e
	}

	childState := "complete"
	if callErr != nil {
		childState = "failed"
	}
	if _, e = s.Store.DB.Exec(evidenceCtx, "UPDATE operation SET state=$2,result_document_id=$3,finished_at=clock_timestamp() WHERE id=$1", child.ID, childState, receipt); e != nil {
		return nil, "", e
	}

	return result, receipt, callErr
}

func speechPublicFailure(err error) (string, string) {
	code, _ := provider.SafeError(err)
	native := code
	switch code {
	case "PAID_USE_FORBIDDEN", "PROVIDER_QUOTA":
		code = "LOCAL_BUDGET_EXCEEDED"
	case "MODEL_SETUP_REQUIRED", "VOICE_SETUP_REQUIRED", "VOICE_UNAVAILABLE", "CAPABILITY_UNAVAILABLE", "ACOUSTIC_RENDER_REQUIRED", "MODEL_BINDING_MISMATCH":
		code = "CAPABILITY_UNQUALIFIED"
	case "AUDIO_FORMAT_INVALID", "AUDIO_SILENT":
		code = "PROVIDER_OUTPUT_INVALID"
	case "SPEECH_TIMEOUT":
		code = "DEADLINE_EXCEEDED"
	case "SPEECH_UNAVAILABLE":
		code = "INFRASTRUCTURE_UNAVAILABLE"
	case "PROVIDER_FAILED", "SYNTHESIS_FAILED":
		code = "PROVIDER_FAILURE"
	}
	return code, strings.ReplaceAll(strings.ToLower(native), "_", " ") + ". Saved text and completed audio pieces are retained."
}

func speechPlanHash(plan map[string]any) string {
	content := map[string]any{}
	for k, v := range plan {
		if k != "id" && k != "schema_version" && k != "plan_sha256" {
			content[k] = v
		}
	}
	return lab.Hash(content)
}
