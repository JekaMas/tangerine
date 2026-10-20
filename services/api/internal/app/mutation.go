package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"net/http"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

// PrepareMutation continues this exact saved clean preparation. Its maintenance
// entrypoint and the later combined Generate action share this production owner.
func (s *Server) PrepareMutation(ctx context.Context, r CanonicalPreparationRequest, key string, client *http.Client) (map[string]any, error) {
	raw, _ := lab.Canonical(r)
	if _, _, e := contracts.Validate("generation-request", "2.0.0", raw); e != nil {
		return nil, e
	}
	if r.PreparationID == nil || len(r.Sources) > 0 {
		return nil, ErrConflict
	}
	op, e := s.Store.ReserveOperation(ctx, OperationRequest{Name: "mutation_prepare", Key: key, Path: "/prepare/mutation", Body: raw})
	if e != nil {
		return nil, e
	}
	if op.State == "complete" || op.State == "failed" {
		p, e := s.Store.mutationActionResult(ctx, op.ID)
		if e != nil {
			return nil, e
		}
		if op.State == "failed" {
			return p, &provider.Failure{Code: p["last_failure"].(map[string]any)["code"].(string)}
		}
		return p, nil
	}
	p, e := s.Store.Preparation(ctx, *r.PreparationID)
	if e != nil {
		return nil, e
	}
	raw, e = s.Store.ReadAsset(ctx, p["settings_asset_id"].(string))
	if e != nil {
		return p, e
	}
	var settings map[string]any
	if e = json.Unmarshal(raw, &settings); e != nil {
		return p, e
	}
	if settings["blueprint"].(map[string]any)["id"] != r.BlueprintID || settings["configuration"].(map[string]any)["configuration_sha256"] != r.ConfigurationSHA {
		return p, ErrConflict
	}
	states := p["phase_states"].(map[string]any)
	if states["canonical_text"] != "complete" {
		return p, ErrConflict
	}
	if states["mutation"] == "complete" {
		e = s.Store.acknowledgeMutation(ctx, op.ID, p["id"].(string))
		return p, e
	}
	if r.Attempt != len(p["operation_ids"].([]any))+1 {
		return p, ErrConflict
	}
	if e = s.Store.claimMutation(ctx, op.ID); e != nil {
		return p, e
	}
	defer func() {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer done()
		s.Store.releaseMutation(end, op.ID)
	}()
	if e = s.Store.takePreparation(ctx, p, op.ID, "mutation"); e != nil {
		return p, e
	}
	return s.finishMutation(ctx, p, settings, op, key, client)
}

func (s *Server) finishMutation(ctx context.Context, p, settings map[string]any, op Operation, key string, client *http.Client) (map[string]any, error) {
	blueprint := settings["blueprint"].(map[string]any)
	config := settings["configuration"].(map[string]any)
	result := LLMResult{}
	var callErr error
	var candidate map[string]any
	var manifest map[string]any
	child, e := s.Store.completedMutationChild(ctx, p["operation_ids"].([]any))
	callErr = e
	if callErr == nil && child != "" {
		result, callErr = s.Store.ReadLLMResult(ctx, child)
	}
	if callErr == nil && result.OperationID == "" {
		result, callErr = s.invokeMutation(ctx, p, settings, key, client)
	}

	if len(result.ReceiptIDs) > 0 {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
		_, e := s.Store.LLMDiagnostic(end, result, config["llm_lab_capture_content"] == true, config["llm_lab_trace_enabled"] == true)
		done()
		if e != nil && callErr == nil {
			callErr = e
		}
	}
	if callErr == nil {
		callErr = func() error {
			// Accepted provider output is decoded and used; no admission replay.
			if e := json.Unmarshal(result.Output, &candidate); e != nil {
				return e
			}
			mutated, e := s.Store.saveProviderBytes(ctx, result.Output, "provider_output")
			if e != nil {
				return e
			}
			var seed any
			if r, ok := blueprint["exercise_request"].(map[string]any); ok {
				seed = r["mutation_seed"]
			}
			manifest = mutationManifest(candidate, p["canonical_asset_id"].(string), p["canonical_sha256"].(string), mutated.ID, mutated.SHA, settings["recipe_registry_sha256"].(string), nil, seed)
			body, e := lab.Canonical(manifest)
			if e != nil {
				return e
			}
			manifestAsset, e := s.Store.saveProviderBytes(ctx, body, "provider_output")
			if e != nil {
				return e
			}
			id := uuid.NewString()
			envelope := map[string]any{"id": id, "revision": 0, "candidate_sha256": mutated.SHA, "candidate": candidate, "preparation_id": p["id"]}
			body, e = lab.Canonical(envelope)
			if e != nil {
				return e
			}
			if e = s.Store.saveMutationCandidate(ctx, id, body); e != nil {
				return e
			}

			p["candidate_id"] = id
			p["mutated_asset_id"] = mutated.ID
			p["mutation_manifest_asset_id"] = manifestAsset.ID
			return nil
		}()
	}
	rev := int64(p["revision"].(float64))
	p["revision"] = float64(rev + 1)
	p["updated_at"] = time.Now().UTC().Format(time.RFC3339Nano)
	states := p["phase_states"].(map[string]any)
	if callErr != nil {
		code, message := provider.SafeError(callErr)
		states["mutation"] = "failed"
		p["last_failure"] = map[string]any{"code": code, "message": message, "request_id": op.ID, "retryable": true, "object_id": nil, "details": []any{}}
	} else {
		states["mutation"] = "complete"
		p["last_failure"] = nil
	}
	p["active_operation_id"] = nil
	end, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer done()
	words := 0
	if manifest != nil {
		words = manifest["canonical_word_count"].(int)
	}
	if e := s.Store.checkpoint(end, p, &rev, op.ID, callErr == nil, words); e != nil {
		return p, e
	}
	return p, callErr
}

// invokeMutation owns only frozen model/context construction and dispatch.
func (s *Server) invokeMutation(ctx context.Context, p, settings map[string]any, key string, client *http.Client) (LLMResult, error) {
	blueprint := settings["blueprint"].(map[string]any)
	config := settings["configuration"].(map[string]any)
	raw, e := s.Store.ReadAsset(ctx, p["canonical_asset_id"].(string))
	if e != nil {
		return LLMResult{}, e
	}
	var clean map[string]any
	if e = json.Unmarshal(raw, &clean); e != nil {
		return LLMResult{}, e
	}
	taxonomyID, ok := settings["taxonomy_registry_asset_id"].(string)
	if !ok {
		return LLMResult{}, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
	}
	taxonomyBytes, e := s.Store.ReadAsset(ctx, taxonomyID)
	if e != nil {
		return LLMResult{}, e
	}
	recipeBytes, e := s.Store.ReadAsset(ctx, settings["recipe_registry_asset_id"].(string))
	if e != nil {
		return LLMResult{}, e
	}
	productionBytes, e := s.Store.ReadAsset(ctx, settings["production_registry_asset_id"].(string))
	if e != nil {
		return LLMResult{}, e
	}
	taxonomy, recipes, production, e := mutationSelection(blueprint, taxonomyBytes, recipeBytes, productionBytes)
	if e != nil {
		return LLMResult{}, e
	}
	input := map[string]any{"schema_version": "2.0.0", "blueprint": blueprint, "taxonomy_records_asset_id": taxonomyID, "taxonomy_records_sha256": settings["taxonomy_registry_sha256"], "allowed_source_record_ids": []any{}, "request_language": "en", "source_excerpts": []any{}, "taxonomy_context": taxonomy, "phase": "mutation", "canonical_script": clean, "canonical_script_sha256": p["canonical_sha256"], "mutation_recipes": recipes, "recipe_registry_sha256": settings["recipe_registry_sha256"], "production_recipes": production, "production_registry_sha256": settings["production_registry_sha256"]}
	components := map[string]any{"blueprint": blueprint, "taxonomy": taxonomy, "public_context": blueprint["public_context"], "source_excerpt": nil, "canonical_script": clean, "recipes": map[string]any{"mutation_recipes": recipes, "production_recipes": production}}
	var bundle lab.Bundle
	bundleRaw, _ := json.Marshal(settings["prompt_bundle"])
	if e = json.Unmarshal(bundleRaw, &bundle); e != nil {
		return LLMResult{}, e
	}
	phase := "mutation"
	result, e := s.InvokeLLM(ctx, LLMRequest{Timeout: preparationTimeout(settings, "mutation"), Operation: OperationRequest{Name: "mutation", Key: key, Path: "/prepare/mutation/model", Body: json.RawMessage(`{}`)}, Stage: "case_generation", Phase: &phase, Input: input, Components: components, Configuration: config, Bundle: bundle, Validate: func(raw []byte) error { _, e := mutationContent(raw, blueprint, clean, taxonomy); return e }}, client)
	return result, e
}
