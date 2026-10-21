package app

import (
	"context"
	"encoding/json"
	"fmt"
	"go.yaml.in/yaml/v3"
	"net/http"
	"tangerine.local/api/internal/experiment"
	"time"
)

func mergeQualityResult(a *LLMResult, b LLMResult) {
	a.ReceiptIDs = append(a.ReceiptIDs, b.ReceiptIDs...)
	a.ContextIDs = append(a.ContextIDs, b.ContextIDs...)
	if b.OperationID != "" {
		a.OperationID = b.OperationID
	}
	a.Output = b.Output
}
func (s *Server) executeQualityRow(ctx context.Context, p QualityExperiment, f qualityFrozen, row experiment.Row, operation string, client *http.Client) (map[string]any, LLMResult, error) {
	var input, expected map[string]any
	var c QualityCase
	for _, v := range f.Dataset.Cases {
		if v.ID == row.Case {
			c = v
		}
	}
	if e := json.Unmarshal(f.Inputs[c.ID], &input); e != nil {
		return nil, LLMResult{}, e
	}
	if e := json.Unmarshal(f.Expected[c.ID], &expected); e != nil {
		return nil, LLMResult{}, e
	}
	binding := f.Variants[row.Variant]
	result := LLMResult{ReceiptIDs: []string{}, ContextIDs: []string{}}
	packet := map[string]any{"case_id": c.ID, "variant_id": row.Variant, "repetition": row.Repetition, "expectation_basis": c.Basis, "input_asset_id": c.Input, "expectations_asset_id": c.Expectations, "operation_id": operation}
	var output any
	var err error

	switch p.Scope {
	case "stage":
		stageContext, stop, se := s.Store.qualityOwnerContext(ctx)
		if se != nil {
			return packet, result, se
		}
		defer stop()
		parts := f.Contexts[c.ID]
		var validate func([]byte) error
		if c.Stage == "blind_claim_extraction" {
			validate = func(raw []byte) error {
				_, e := normalizeExtraction(fmt.Sprint(input["answer_text"]), fmt.Sprint(input["answer_sha256"]), raw)
				return e
			}
		}
		result, err = s.InvokeLLM(stageContext, LLMRequest{Operation: OperationRequest{Name: "quality_stage", Key: interpretationCallKey(operation, c.Stage), Path: "/lab/eval/stage", Body: sourceBytes(input)}, Stage: c.Stage, Phase: c.Phase, Input: input, Components: parts, Configuration: binding.Configuration, Bundle: binding.Bundle, Validate: validate}, client)
		if len(result.ReceiptIDs) > 0 {
			cleanup, cleanupDone := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
			defer cleanupDone()
			diagnostic, de := s.Store.LLMDiagnostic(cleanup, result, binding.Configuration["llm_lab_capture_content"] == true, binding.Configuration["llm_lab_trace_enabled"] == true)
			if de != nil && err == nil {
				err = de
			}
			if de == nil {
				packet["diagnostic_asset_id"] = diagnostic.ID
			}
		}
		if len(result.Output) > 0 {
			_ = json.Unmarshal(result.Output, &output)
		}
	case "generation_pipeline", "full_flow":
		raw := f.Inputs[c.ID]
		if _, ok := input["topic"]; ok {
			raw = sourceBytes(map[string]any{"exercise_request": input})
		}
		var b map[string]any
		canonicalContext, canonicalDone, ce := s.Store.qualityOwnerContext(ctx)
		if ce != nil {
			return packet, result, ce
		}
		defer canonicalDone()
		b, err = s.Store.WriteBlueprint(canonicalContext, raw, interpretationCallKey(operation, "blueprint"))
		if err == nil {
			request := CanonicalPreparationRequest{BlueprintID: fmt.Sprint(b["id"]), ConfigurationSHA: fmt.Sprint(binding.Configuration["configuration_sha256"]), Sources: []string{}, Attempt: 1}
			var prep map[string]any
			prep, err = s.PrepareCanonical(canonicalContext, request, interpretationCallKey(operation, "canonical"), client)
			if prep != nil {
				output = prep
			}
			if err == nil {
				packet["initial_canonical_sha256"] = prep["canonical_sha256"]
				id := fmt.Sprint(prep["id"])
				request.PreparationID = &id
				request.Attempt = 2
				mutationContext, mutationDone, me := s.Store.qualityOwnerContext(ctx)
				if me != nil {
					return packet, result, me
				}
				defer mutationDone()
				prep, err = s.PrepareMutation(mutationContext, request, interpretationCallKey(operation, "mutation"), client)
				output = prep
				if err == nil && p.Scope == "full_flow" {
					renderContext, renderDone, re := s.Store.qualityOwnerContext(ctx)
					if re != nil {
						return packet, result, re
					}
					defer renderDone()
					prep, err = s.RenderPreparation(renderContext, id, interpretationCallKey(operation, "render"), 1, client)
					output = prep
				}
			}
		}
	case "answer_pipeline":
		answerContext, answerDone, ae := s.Store.qualityOwnerContext(ctx)
		if ae != nil {
			return packet, result, ae
		}
		defer answerDone()
		var score any
		output, score, err = s.qualityAnswer(answerContext, f.Answers[c.ID], operation, client)
		if score != nil {
			packet["native_score"] = score
		}
	default:
		err = ErrInput
	}
	cleanup, cleanupDone := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer cleanupDone()
	if (p.Scope == "generation_pipeline" || p.Scope == "full_flow") && output != nil {
		if prep, ok := output.(map[string]any); ok {
			packet["canonical_sha256"] = prep["canonical_sha256"]
			details := map[string]any{"preparation": prep}
			for key, field := range map[string]string{"canonical": "canonical_asset_id", "mutated": "mutated_asset_id", "mutation_manifest": "mutation_manifest_asset_id"} {
				if id, ok := prep[field].(string); ok {
					b, e := s.Store.ReadAsset(cleanup, id)
					if e != nil && err == nil {
						err = e
					}
					var value map[string]any
					if json.Unmarshal(b, &value) == nil {
						details[key] = value
					}
				}
			}
			output = details
		}
	}
	packet["candidate_output"] = output
	// Gather all actual descendants; this is diagnostics, not a counter used as an
	// independent dispatch-completeness oracle. Native receipts keep failures too.
	actual, e := s.Store.qualityOperationReceipts(cleanup, operation, result.ReceiptIDs)
	if e != nil && err == nil {
		err = e
	}
	result.ReceiptIDs = actual
	evidence, e := s.Store.qualityReceiptEvidence(cleanup, result.ReceiptIDs)
	if e != nil && err == nil {
		err = e
	}
	if evidence.Stats == nil {
		evidence.Stats = map[string]string{}
	}
	if err == nil {
		qualityDeterministicEvidence(c, p, input, expected, output, packet, &evidence)
		if details, ok := output.(map[string]any); ok {
			if manifest, ok := details["mutation_manifest"].(map[string]any); ok {
				candidate, _ := details["mutated"].(map[string]any)
				qualityGenerationEvidence(input, candidate, manifest, &evidence)
			}
		}
		if p.JudgePolicy != nil {
			judgment, jresult, je := s.qualityJudge(ctx, p, f, c, row, packet, operation, client)
			mergeQualityResult(&result, jresult)
			packet["judge"] = judgment
			if je != nil {
				err = je
			} else {
				qualityJudgeEvidence(c, expected, judgment, &evidence)
			}
		}
	}
	if p.JudgePolicy != nil {
		cleanup, cleanupDone := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer cleanupDone()
		actual, re := s.Store.qualityOperationReceipts(cleanup, operation, result.ReceiptIDs)
		if re == nil {
			result.ReceiptIDs = actual
			receipts, re := s.Store.qualityReceiptEvidence(cleanup, actual)
			if re == nil {
				evidence.Durations = receipts.Durations
				evidence.Tokens = receipts.Tokens
				evidence.Costs = receipts.Costs
				for key, value := range receipts.Stats {
					evidence.Stats[key] = value
				}
			} else if err == nil {
				err = re
			}
		} else if err == nil {
			err = re
		}
	}
	packet["diagnostic_evidence"] = evidence
	packet["llm_result"] = result
	return packet, result, err
}
func qualityStageComponents(stage string, in map[string]any) map[string]any {
	out := map[string]any{}
	raw, _ := generationRegistry("error-taxonomy.v1.yaml")
	var taxonomy struct {
		Items []map[string]any `yaml:"items"`
	}
	_ = yaml.Unmarshal(raw, &taxonomy)
	items := []any{}
	for _, item := range taxonomy.Items {
		selected := map[string]any{}
		fields := []string{"id", "label", "definition", "reporting_domain", "inclusion_criteria", "exclusion_criteria"}
		if stage == "blind_claim_extraction" {
			fields = fields[:2]
		}
		for _, key := range fields {
			selected[key] = item[key]
		}
		items = append(items, selected)
	}
	out["taxonomy"] = items
	for _, pair := range [][2]string{{"taxonomy_context", "taxonomy"}, {"canonical_script", "canonical_script"}, {"mutation_recipes", "recipes"}, {"source_excerpts", "source_excerpt"}, {"score_result", "scoring_result"}, {"decisions", "prior_decisions"}, {"answer", "answer"}} {
		if value, ok := in[pair[0]]; ok {
			out[pair[1]] = value
		}
	}
	if candidate, ok := in["candidate"].(map[string]any); ok {
		out["canonical_script"] = candidate
		out["mutation_key"] = candidate["planned_units"]
	}
	if key, ok := in["ground_truth"].(map[string]any); ok {
		out["public_context"] = key["public_context"]
	}

	for _, pair := range [][2]string{{"answer_text", "answer"}, {"ground_truth", "mutation_key"}, {"extraction", "extraction"}, {"scoring_result", "scoring_result"}, {"candidate", "candidate"}, {"evidence", "evidence"}, {"prior_decisions", "prior_decisions"}, {"mutation_manifest", "mutation_key"}, {"blueprint", "blueprint"}, {"taxonomy", "taxonomy"}, {"public_context", "public_context"}, {"rubric", "rubric"}} {
		if v, ok := in[pair[0]]; ok {
			out[pair[1]] = v
		}
	}
	if stage == "blind_claim_extraction" {
		delete(out, "mutation_key")
		delete(out, "prior_decisions")
		delete(out, "scoring_result")
	}
	if stage == "mapping_audit" {
		delete(out, "prior_decisions")
	}
	return out
}
func (s *Server) qualityAnswer(ctx context.Context, in qualityAnswerInput, operation string, client *http.Client) (any, any, error) {
	id, digest, answer := in.Case, in.SHA, in.Answer
	start, e := s.Store.StartAttempt(ctx, sourceBytes(map[string]any{"case_version_id": id, "case_sha256": digest, "requested_language": "en"}), interpretationCallKey(operation, "start"))
	if e != nil {
		return nil, nil, e
	}
	attempt := fmt.Sprint(start["attempt_id"])
	record, e := s.Store.Attempt(ctx, attempt)
	if e != nil {
		return nil, nil, e
	}
	_, _, e = s.Store.WriteAnswer(ctx, attempt, interpretationCallKey(operation, "answer"), 0, sourceBytes(map[string]any{"answer_text": answer, "requested_language": "en"}), true)
	if e != nil {
		return nil, nil, e
	}
	record, e = s.Store.Attempt(ctx, attempt)
	if e != nil {
		return nil, nil, e
	}
	state, e := s.InterpretAttempt(ctx, attempt, interpretationCallKey(operation, "interpret"), int64(record.Attempt["revision"].(float64)), fmt.Sprint(record.Attempt["answer_utf8_sha256"]), fmt.Sprint(record.Attempt["configuration_sha256"]), client)
	if e != nil {
		return state, nil, e
	}
	if state.Result == nil {
		return state, nil, ErrUnavailable
	}
	result, e := s.Store.readScoringResult(ctx, *state.Result)
	if e != nil {
		return state, nil, e
	}
	if state.Mapping != nil {
		raw, e := s.Store.ReadAsset(ctx, *state.Mapping)
		if e != nil {
			return state, nil, e
		}
		result["quality_native_mapping"] = json.RawMessage(raw)
	}
	if result["feedback_status"] != "complete" {
		return result, result["score"], fmt.Errorf("selected answer pipeline feedback incomplete")
	}
	return result, result["score"], nil
}
