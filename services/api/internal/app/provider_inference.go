package app

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"net/http"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

type LLMRequest struct {
	NormalizeProjection func(any) any
	FrozenProfile       *provider.Profile
	TransportRetry      func() bool
	Timeout             time.Duration
	Operation           OperationRequest
	Stage               string
	Phase               *string
	Input               map[string]any
	Components          map[string]any
	Configuration       map[string]any
	Bundle              lab.Bundle
	DiagnoseInvalid     func([]byte) string
	Validate            func([]byte) error
}
type LLMResult struct {
	Output         json.RawMessage `json:"output"`
	ReceiptIDs     []string        `json:"receipt_ids"`
	ContextIDs     []string        `json:"context_snapshot_ids"`
	OperationID    string          `json:"operation_id"`
	BindingID      string          `json:"binding_id"`
	privateSecrets []string
}

func stageTimeout(stage string, phase *string) time.Duration {
	switch stage {
	case "case_generation":
		if phase != nil && *phase == "canonical_text" {
			return 90 * time.Second
		}
		return 240 * time.Second
	case "blind_claim_extraction", "feedback":
		return 40 * time.Second
	case "claim_mapping":
		return 70 * time.Second
	default:
		return 220 * time.Second
	}
}
func traceID(n int) string {
	b := make([]byte, n)
	if _, e := rand.Read(b); e != nil {
		panic(e)
	}
	return hex.EncodeToString(b)
}

// InvokeLLM is the shared production owner. Pipelines supply frozen configuration,
// bundle and independently validated inputs; this owner never changes selection.
func (s *Server) InvokeLLM(ctx context.Context, request LLMRequest, client *http.Client) (LLMResult, error) {
	result := LLMResult{ReceiptIDs: []string{}, ContextIDs: []string{}}
	var p provider.Profile
	var e error
	if request.FrozenProfile != nil {
		p = *request.FrozenProfile
		e = provider.Included(p)
		if p.Model == "unselected" {
			e = &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
		}
	} else {
		p, e = FreezeProfile(request.Configuration, request.Stage)
	}
	if e != nil {
		return result, e
	}
	timeout := request.Timeout
	if timeout == 0 {
		timeout = stageTimeout(request.Stage, request.Phase)
	}
	prepared, e := lab.BuildContext(request.Bundle, request.Stage, request.Phase, request.Input, request.Components)
	if e != nil {
		return result, e
	}
	var binding lab.Binding
	for _, b := range request.Bundle.Bindings {
		if lab.Pair(b.Stage, b.Phase) == lab.Pair(request.Stage, request.Phase) {
			binding = b
		}
	}
	format, e := inferenceOutputFormat(p, prepared.OutputSchema)
	if e != nil {
		return result, e
	}
	request.Operation.Body, _ = lab.Canonical(map[string]any{"original_request": json.RawMessage(request.Operation.Body), "configuration_sha256": lab.Hash(request.Configuration), "bundle_sha256": request.Bundle.SHA, "stage": request.Stage, "phase": request.Phase, "timeout_seconds": int(timeout / time.Second), "input_sha256": prepared.InputSHA, "components_sha256": lab.Hash(request.Components)})
	op, e := s.Store.ReserveOperation(ctx, request.Operation)
	if e != nil {
		return result, e
	}
	result.OperationID = op.ID
	if op.State == "complete" {
		return s.Store.ReadLLMResult(ctx, op.ID)
	}
	credential, e := providerCredential(ctx, s.Providers, p, p.CredentialRef)
	if e != nil {
		return result, e
	}
	result.privateSecrets = []string{credential}
	if p.Auth == "chatgpt_plan_oauth" {
		c, e := s.Store.providerByID(ctx, p.CredentialRef)
		if e != nil || c.ModelsAsset == nil {
			return result, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
		}
		raw, e := s.Store.ReadAsset(ctx, *c.ModelsAsset)
		if e != nil {
			return result, e
		}
		var catalogue struct{ Models []provider.Model }
		_ = json.Unmarshal(raw, &catalogue)
		found := false
		for _, m := range catalogue.Models {
			found = found || (m.Slug == p.Model && m.Visibility == "list")
		}
		if !found {
			return result, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
		}
	}
	if e = s.Store.claimInference(ctx, op.ID); e != nil {
		return result, e
	}
	defer func() {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer done()
		s.Store.releaseInference(end, op.ID)
	}()

	// Bindings have a server-generated immutable envelope and a semantic self digest
	// excluding only its envelope ID and the digest itself.
	raw, _ := json.Marshal(p)
	var effective map[string]any
	_ = json.Unmarshal(raw, &effective)
	delete(effective, "roles")
	effective["schema_version"] = "2.0.0"
	effective["stage"] = request.Stage
	effective["phase"] = request.Phase
	effective["prompt_id"] = binding.PromptID
	effective["prompt_sha256"] = binding.PromptSHA
	effective["input_schema_sha256"] = binding.InputSHA
	effective["output_schema_sha256"] = binding.OutputSHA
	effective["wire_schema_sha256"] = contracts.Digest(prepared.OutputSchema)
	effective["timeout_seconds"] = int(timeout / time.Second)
	effective["prompt_bundle_sha256"] = request.Bundle.SHA
	effective["context_policy_sha256"] = binding.PolicySHA
	delete(effective, "id")
	effective["binding_sha256"] = lab.Hash(effective)
	effective["id"] = uuid.NewString()
	result.BindingID = effective["id"].(string)
	body, _ := lab.Canonical(effective)
	if _, e = s.Store.WriteDocuments(ctx, []DocumentWrite{{ID: result.BindingID, Kind: "effective-binding", Version: "2.0.0", Scope: "local", Payload: body}}); e != nil {
		return result, e
	}
	if e = s.Store.bindInference(ctx, op.ID, result.BindingID); e != nil {
		return result, e
	}
	components := []any{}
	for _, part := range prepared.Parts {
		a, e := s.Store.saveProviderBytes(ctx, part.Body, "provider_input")
		if e != nil {
			return result, e
		}
		components = append(components, map[string]any{"kind": part.Kind, "trust": part.Trust, "asset_id": a.ID, "asset_sha256": part.SHA, "included": true, "reason": nil, "byte_count": part.Bytes, "token_count": nil})
	}
	instructions, input := inferenceFrame(prepared, request.Stage, request.Phase, request.Input)
	// Omitted components are retained deterministically and without invented counts.
	for _, kind := range binding.Policy.Order {
		if reason, ok := prepared.Omitted[kind]; ok {
			components = append(components, map[string]any{"kind": kind, "trust": "input_data", "asset_id": nil, "asset_sha256": nil, "included": false, "reason": reason, "byte_count": nil, "token_count": nil})
		}
	}
	counter, e := provider.NewContextCounter(p)
	if e != nil {
		return result, e
	}
	reserved := 4096
	if p.MaxOutput != nil && *p.MaxOutput > reserved {
		reserved = *p.MaxOutput
	}
	inputUsage := map[int]int{}
	trace := traceID(16)
	requestAssets := map[int]Asset{}
	er := provider.ExecuteRequest{NormalizeProjection: request.NormalizeProjection, Profile: p, Instructions: instructions, Input: input, OutputKind: strings.TrimSuffix(binding.OutputSchema, ".schema.json"), Format: format, Timeout: timeout, Validate: request.Validate, DiagnoseInvalid: request.DiagnoseInvalid, AllowTransportRetry: request.TransportRetry}
	// JSON-schema decoding is opt-in for profiles with observed provider support;
	// plain JSON still receives the same complete output contract in instructions.
	er.Before = func(ctx context.Context, a provider.Attempt) error {
		used, err := counter.Count(a.Wire)
		if err != nil {
			return err
		}
		if reserved >= p.ContextBudget || used > p.ContextBudget-reserved {
			return &provider.Failure{Code: "INPUT_CAPACITY_EXCEEDED"}
		}
		inputUsage[a.Index] = used
		asset, e := s.Store.saveProviderBytes(ctx, a.Wire, "provider_input")
		if e == nil {
			requestAssets[a.Index] = asset
		}
		return e
	}
	er.After = func(ctx context.Context, a provider.Attempt) error {
		req := requestAssets[a.Index]
		receiptID := uuid.NewString()
		snapshotID := uuid.NewString()
		span := traceID(8)
		var responseID any = nil
		if len(a.Response.Raw) > 0 {
			asset, e := s.Store.saveProviderBytes(ctx, a.Response.Raw, "provider_output")
			if e != nil {
				return e
			}
			responseID = asset.ID
		}
		tokens := func(key string) any {
			if n := a.Response.Usage[key]; n != nil && *n >= 0 {
				return fmt.Sprint(*n)
			}
			return nil
		}
		receipt := map[string]any{"schema_version": "2.0.0", "id": receiptID, "operation_id": op.ID, "stage": request.Stage, "binding_sha256": effective["binding_sha256"], "input_sha256": prepared.InputSHA, "wire_request_asset_id": req.ID, "wire_response_asset_id": responseID, "provider_request_id": a.Response.RequestID, "http_status": a.Response.HTTPStatus, "outcome": a.Response.Outcome, "error_code": a.Response.ErrorCode, "input_tokens": tokens("input_tokens"), "cached_input_tokens": tokens("cached_tokens"), "output_tokens": tokens("output_tokens"), "reasoning_tokens": tokens("reasoning_tokens"), "cost_micro_usd": nil, "cost_basis": "unknown", "transport_attempt": a.Index, "started_at": a.Response.Started.Format(time.RFC3339Nano), "finished_at": a.Response.Finished.Format(time.RFC3339Nano), "model_returned": a.Response.Model, "context_snapshot_id": snapshotID, "trace_id": trace, "span_id": span}
		attemptComponents := append([]any(nil), components...)
		if a.Repair != nil {
			for _, part := range []struct{ Kind, Trust, Body string }{{"prompt", "owned_instruction", a.Repair.Instruction}, {"candidate", "input_data", a.Repair.Content}} {
				asset, e := s.Store.saveProviderBytes(ctx, []byte(part.Body), "provider_input")
				if e != nil {
					return e
				}
				attemptComponents = append(attemptComponents, map[string]any{"kind": part.Kind, "trust": part.Trust, "asset_id": asset.ID, "asset_sha256": asset.SHA, "included": true, "reason": nil, "byte_count": len(part.Body), "token_count": nil})
			}
		}
		snapshot := map[string]any{"schema_version": "2.0.0", "id": snapshotID, "operation_id": op.ID, "stage": request.Stage, "phase": request.Phase, "bundle_sha256": request.Bundle.SHA, "binding_sha256": effective["binding_sha256"], "input_sha256": prepared.InputSHA, "components": attemptComponents, "tokenizer": counter.Tokenizer, "budget_method": counter.Method, "context_budget_tokens": p.ContextBudget, "reserved_output_tokens": reserved, "input_budget_used": inputUsage[a.Index], "rendered_request_asset_id": req.ID, "receipt_id": receiptID, "trace_id": trace, "span_id": span, "created_at": a.Response.Finished.Format(time.RFC3339Nano)}
		rb, _ := lab.Canonical(receipt)
		sb, _ := lab.Canonical(snapshot)
		rw := DocumentWrite{ID: receiptID, Kind: "provider-receipt", Version: "2.0.0", Scope: "local", Payload: rb}
		sw := DocumentWrite{ID: snapshotID, Kind: "llm-context-snapshot", Version: "2.0.0", Scope: "local", Payload: sb}
		for pointer, id := range map[string]string{"/wire_request_asset_id": req.ID} {
			ref, e := s.Store.assetByteReference(ctx, id, pointer, "native-wire")
			if e != nil {
				return e
			}
			rw.References = append(rw.References, ref)
		}
		if responseID != nil {
			ref, e := s.Store.assetByteReference(ctx, responseID.(string), "/wire_response_asset_id", "native-wire")
			if e != nil {
				return e
			}
			rw.References = append(rw.References, ref)
		}
		rw.References = append(rw.References, Reference{Pointer: "/context_snapshot_id", ID: snapshotID, Scope: "local", Kind: sw.Kind, SHA: contracts.Digest(sb), Relation: "native-context"})
		ref, e := s.Store.assetByteReference(ctx, req.ID, "/rendered_request_asset_id", "native-wire")
		if e != nil {
			return e
		}
		sw.References = append(sw.References, ref, Reference{Pointer: "/receipt_id", ID: receiptID, Scope: "local", Kind: rw.Kind, SHA: contracts.Digest(rb), Relation: "native-receipt"})
		for i, item := range attemptComponents {
			c := item.(map[string]any)
			if id, ok := c["asset_id"].(string); ok {
				ref, e := s.Store.assetByteReference(ctx, id, fmt.Sprintf("/components/%d/asset_id", i), "native-context-component")
				if e != nil {
					return e
				}
				sw.References = append(sw.References, ref)
			}
		}
		if _, e = s.Store.WriteDocuments(ctx, []DocumentWrite{rw, sw}); e != nil {
			return e
		}
		if e = s.Store.linkQualityCall(ctx, receiptID, a.Kind, len(a.Response.Raw) > 0, len(a.Projection) > 0); e != nil {
			return e
		}
		result.ReceiptIDs = append(result.ReceiptIDs, receiptID)
		result.ContextIDs = append(result.ContextIDs, snapshotID)
		if p.Auth == "chatgpt_plan_oauth" && a.Err != nil {
			_, code := provider.SafeError(a.Err)
			if code == "subscription_sharing_usage_limit_exceeded" || code == "subscription_sharing_usage_unavailable" {
				state := "usage_limited"
				if code == "subscription_sharing_usage_unavailable" {
					state = "unavailable"
				}
				if e = s.Providers.Mark(ctx, p.CredentialRef, state, code); e != nil {
					return e
				}
			}
		}
		return nil
	}
	output, _, e := provider.Execute(ctx, client, er, credential)
	if e == nil {
		finishCtx, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
		defer done()
		asset, saveErr := s.Store.saveProviderBytes(finishCtx, output, "provider_output")
		if saveErr != nil {
			return result, saveErr
		}
		e = s.Store.completeInference(finishCtx, op.ID, asset.ID)
	}
	if e == nil && ctx.Err() != nil {
		e = ctx.Err()
	}
	if e == nil {
		result.Output = output
	}
	return result, e
}
