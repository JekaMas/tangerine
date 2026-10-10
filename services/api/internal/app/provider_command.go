package app

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"github.com/jackc/pgx/v5"
	"io"
	"os"
	"sort"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

// ProviderCommand is development tooling for the same application owner used by
// later generation/grading pipelines, never a separate grader or provider SDK.
func (s *Server) ProviderCommand(ctx context.Context, input io.Reader, output io.Writer) error {
	var r struct {
		Operation      OperationRequest `json:"operation"`
		Stage          string           `json:"stage"`
		Phase          *string          `json:"phase"`
		Input          map[string]any   `json:"input"`
		Components     map[string]any   `json:"components"`
		TraceEnabled   *bool            `json:"trace_enabled"`
		CaptureContent *bool            `json:"capture_content"`
	}
	if e := lab.DecodeCommand(input, &r); e != nil {
		return e
	}
	c, _, e := s.Store.Configuration(ctx)
	if e != nil {
		return e
	}
	if r.TraceEnabled != nil {
		c["llm_lab_trace_enabled"] = *r.TraceEnabled
	}
	if r.CaptureContent != nil {
		c["llm_lab_capture_content"] = *r.CaptureContent
	}
	delete(c, "configuration_sha256")
	c["configuration_sha256"] = lab.Hash(c)
	b, e := s.Store.ActiveLabBundle(ctx)
	if e != nil {
		return e
	}
	result, e := s.InvokeLLM(ctx, LLMRequest{Operation: r.Operation, Stage: r.Stage, Phase: r.Phase, Input: r.Input, Components: r.Components, Configuration: c, Bundle: b}, nil)
	code := ""
	if e != nil {
		code, _ = provider.SafeError(e)
	}
	if len(result.ReceiptIDs) > 0 {
		packet, err := s.Store.LLMDiagnostic(ctx, result, c["llm_lab_capture_content"] == true, c["llm_lab_trace_enabled"] == true)
		if err != nil {
			return err
		}
		_ = packet
	}
	// Native receipt identities remain available even when the model fails.
	if err := json.NewEncoder(output).Encode(map[string]any{"result": result, "error_code": code}); err != nil {
		return err
	}
	return e
}
func (s *Storage) LLMDiagnostic(ctx context.Context, r LLMResult, capture, traceEnabled bool) (Asset, error) {
	var existing string
	e := s.DB.QueryRow(ctx, "SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND o.idempotency_key=$1 AND a.state='linked'", r.OperationID).Scan(&existing)
	if e == nil {
		raw, e := s.ReadAsset(ctx, existing)
		if e != nil {
			return Asset{}, e
		}
		var packet struct{ Capture, TraceEnabled bool }
		var flags map[string]any
		_ = json.Unmarshal(raw, &flags)
		packet.Capture = flags["capture"] == true
		packet.TraceEnabled = flags["trace_enabled"] == true
		if packet.Capture != capture || packet.TraceEnabled != traceEnabled {
			return Asset{}, ErrConflict
		}
		return readAsset(ctx, s.DB, "asset_id", existing, false)
	}
	if !errors.Is(e, pgx.ErrNoRows) {
		return Asset{}, e
	}

	docs := []any{}
	wireAssets := []any{}
	for _, id := range append(append([]string{r.BindingID}, r.ReceiptIDs...), r.ContextIDs...) {
		d, e := s.ReadDocument(ctx, id)
		if e != nil {
			return Asset{}, e
		}
		docs = append(docs, d)
		if d.Kind == "provider-receipt" {
			var receipt map[string]any
			_ = json.Unmarshal(d.Payload, &receipt)
			for _, key := range []string{"wire_request_asset_id", "wire_response_asset_id"} {
				if id, ok := receipt[key].(string); ok {
					b, e := s.ReadAsset(ctx, id)
					if e != nil {
						return Asset{}, e
					}
					wireAssets = append(wireAssets, map[string]any{"asset_id": id, "sha256": contracts.Digest(b), "body": string(b), "framing": providerMIME(b)})
				}
			}
		}
	}
	payload, _ := lab.Canonical(map[string]any{"origin": "native_provider_transport", "result": r, "documents": docs, "wire_assets": wireAssets, "transport_attempt_count": len(r.ReceiptIDs)})
	// Originals remain in the immutable native documents and wire/component assets.
	// Never persist the ephemeral credential set, even inside a private export file.
	secrets := append([]string(nil), r.privateSecrets...)
	for _, key := range []string{"OPENAI_API_KEY", "DEEPSEEK_API_KEY", "AZURE_SPEECH_KEY", "ELEVENLABS_API_KEY", "API_INTERNAL_TOKEN", "SPEECH_INTERNAL_TOKEN", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY", "MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD"} {
		if value := os.Getenv(key); value != "" {
			secrets = append(secrets, value)
		}
	}
	var binding struct {
		CredentialRef string `json:"credential_ref"`
	}
	if len(docs) > 0 {
		b, _ := json.Marshal(docs[0])
		var saved SavedDocument
		_ = json.Unmarshal(b, &saved)
		_ = json.Unmarshal(saved.Payload, &binding)
	}
	manager := newProviderManager(s)
	secrets = append(secrets, manager.CredentialValues(ctx, binding.CredentialRef)...)
	copy, e := lab.Sanitize(payload, secrets, true)
	if e != nil {
		return Asset{}, e
	}
	sort.Strings(copy.Reasons)
	packet, _ := lab.Canonical(map[string]any{"operation": r.OperationID, "origin": "native_provider_transport", "capture": capture, "trace_enabled": traceEnabled, "artifacts": []any{map[string]any{"name": "provider-context-receipts.json", "body": string(copy.Bytes), "sha256": copy.SHA, "native_original_sha256": copy.OriginalSHA, "native_redaction_reasons": copy.Reasons}}})

	// Reuse the native diagnostic store; readback/sync uses the original operation
	// linkage and cannot trigger any model request.
	var buffer bytes.Buffer
	command, _ := json.Marshal(map[string]any{"action": "diagnostic-save", "payload": json.RawMessage(packet)})
	if e := s.LabCommand(ctx, bytes.NewReader(command), &buffer); e != nil {
		return Asset{}, e
	}
	var a Asset
	e = json.Unmarshal(buffer.Bytes(), &a)
	return a, e
}
