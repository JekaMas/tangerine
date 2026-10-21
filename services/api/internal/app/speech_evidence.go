package app

import (
	"bytes"
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"os"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

// The snapshot is native synthesis context, not an invented text-LLM prompt.
// The existing receipt and Lab exporter own real model inputs/outputs/traces.
func (s *Server) saveSpeechEvidence(ctx context.Context, op Operation, profile, configuration map[string]any, input, response Asset, start, end time.Time, status int, callErr error, scopes ...map[string]any) (string, error) {
	scope := map[string]any{}
	if len(scopes) > 0 {
		scope = scopes[0]
	}
	stage, origin := "tts", "native_speech_transport"
	if selected, ok := scope["stage"].(string); ok {
		stage, origin = selected, "native_audio_diagnostic"
	}
	contextRaw, _ := lab.Canonical(map[string]any{"scope": scope, "origin": origin, "operation_id": op.ID, "profile": profile, "wire_request_asset_id": input.ID, "wire_response_asset_id": response.ID, "input_sha256": input.SHA, "binding_sha256": lab.Hash(profile)})
	snapshot, e := s.Store.saveProviderBytes(ctx, contextRaw, "provider_input")
	if e != nil {
		return "", e
	}
	outcome := "complete"
	var code any = nil
	if callErr != nil {
		outcome = "transport_error"
		code, _ = provider.SafeError(callErr)
	}
	responseBytes, e := s.Store.ReadAsset(ctx, response.ID)
	if e != nil {
		return "", e
	}
	var result map[string]any
	_ = json.Unmarshal(responseBytes, &result)
	var actualModel any = nil
	if native, ok := result["receipt"].(map[string]any); ok {
		actualModel = native["model"]
	}
	id := uuid.NewString()
	var httpStatus any
	if status != 0 {
		httpStatus = status
	}
	receipt := map[string]any{"schema_version": "2.0.0", "id": id, "operation_id": op.ID, "stage": stage, "binding_sha256": lab.Hash(profile), "input_sha256": input.SHA, "wire_request_asset_id": input.ID, "wire_response_asset_id": response.ID, "provider_request_id": nil, "http_status": httpStatus, "outcome": outcome, "error_code": code, "input_tokens": nil, "cached_input_tokens": nil, "output_tokens": nil, "reasoning_tokens": nil, "cost_micro_usd": nil, "cost_basis": "unknown", "transport_attempt": 1, "started_at": start.Format(time.RFC3339Nano), "finished_at": end.Format(time.RFC3339Nano), "model_returned": actualModel, "context_snapshot_id": snapshot.ID, "trace_id": traceID(16), "span_id": traceID(8)}
	raw, _ := lab.Canonical(receipt)
	write := DocumentWrite{ID: id, Kind: "provider-receipt", Version: "2.0.0", Scope: "local", Payload: raw}
	for pointer, asset := range map[string]Asset{"/wire_request_asset_id": input, "/wire_response_asset_id": response, "/context_snapshot_id": snapshot} {
		write.References = append(write.References, Reference{Pointer: pointer, ID: asset.ID, Scope: asset.ID, Kind: "asset-bytes", SHA: asset.SHA, Relation: "native-speech"})
	}
	saved, e := s.Store.WriteDocuments(ctx, []DocumentWrite{write})
	if e != nil {
		return "", e
	}
	if e = s.Store.linkQualityCall(ctx, id, "speech", status != 0, callErr == nil); e != nil {
		return "", e
	}
	requestBytes, e := s.Store.ReadAsset(ctx, input.ID)
	if e != nil {
		return "", e
	}

	body, _ := lab.Canonical(map[string]any{"origin": origin, "documents": saved, "context": json.RawMessage(contextRaw), "wire_assets": []any{map[string]any{"asset_id": input.ID, "sha256": input.SHA, "body": string(requestBytes)}, map[string]any{"asset_id": response.ID, "sha256": response.SHA, "body": string(responseBytes)}}})
	secrets := []string{}
	for _, name := range []string{"AZURE_SPEECH_KEY", "ELEVENLABS_API_KEY", "GEMINI_API_KEY", "SPEECH_INTERNAL_TOKEN", "API_INTERNAL_TOKEN", "MINIO_ROOT_PASSWORD"} {
		if value := os.Getenv(name); value != "" {
			secrets = append(secrets, value)
		}
	}
	sanitized, e := lab.Sanitize(body, secrets, true)
	if e != nil {
		return "", e
	}
	packet := map[string]any{"operation": op.ID, "origin": origin, "capture": configuration["llm_lab_capture_content"] == true, "trace_enabled": configuration["llm_lab_trace_enabled"] == true, "artifacts": []any{map[string]any{"name": "provider-context-receipts.json", "body": string(sanitized.Bytes), "sha256": contracts.Digest(sanitized.Bytes), "native_original_sha256": sanitized.OriginalSHA, "native_redaction_reasons": sanitized.Reasons}}}
	command, _ := json.Marshal(map[string]any{"action": "diagnostic-save", "payload": packet})
	var output bytes.Buffer
	if e = s.Store.LabCommand(ctx, bytes.NewReader(command), &output); e != nil {
		return "", e
	}
	return id, nil
}
