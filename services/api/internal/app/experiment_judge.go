package app

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/experiment"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/source"
	"time"
)

func (s *Server) qualityJudge(ctx context.Context, p QualityExperiment, f qualityFrozen, c QualityCase, row experiment.Row, packet map[string]any, operation string, client *http.Client) (map[string]any, LLMResult, error) {
	work, done, e := s.Store.qualityOwnerContext(ctx)
	if e != nil {
		return nil, LLMResult{}, e
	}
	defer done()
	ctx = work
	var expected map[string]any
	_ = json.Unmarshal(f.Expected[c.ID], &expected)
	propositions := []any{}
	for _, v := range expected["semantic_propositions"].([]any) {
		m := v.(map[string]any)
		propositions = append(propositions, map[string]any{"id": m["id"], "proposition": m["proposition"], "scope": m["scope"]})
	}
	if len(propositions) == 0 {
		return map[string]any{"schema_version": "2.0.0", "verdicts": []any{}}, LLMResult{}, nil
	}
	var variant QualityVariant
	for _, v := range p.Variants {
		if v.ID == row.Variant {
			variant = v
		}
	}
	if variant.Judge == nil {
		return nil, LLMResult{}, fmt.Errorf("semantic propositions require configured judge")
	}
	binding := f.Variants[row.Variant]
	profileConfig := map[string]any{}
	_ = json.Unmarshal(sourceBytes(binding.Configuration), &profileConfig)
	profileConfig["llm_profile"] = *variant.Judge
	profileConfig["stage_profiles"] = map[string]any{}
	profile, e := FreezeProfile(profileConfig, "linguistic_audit")
	if e != nil {
		return nil, LLMResult{}, e
	}
	candidate := packet["candidate_output"]
	asset, e := s.Store.saveProviderBytes(ctx, sourceBytes(candidate), "provider_output")
	if e != nil {
		return nil, LLMResult{}, e
	}
	contextBody := json.RawMessage(f.Inputs[c.ID])
	input := map[string]any{"schema_version": "2.0.0", "case_id": c.ID, "scope": p.Scope, "expectation_basis": c.Basis, "context_asset_ids": []string{c.Input}, "context": []any{map[string]any{"asset_id": c.Input, "sha256": c.InputSHA, "body": contextBody}}, "candidate_asset_id": asset.ID, "candidate_sha256": asset.SHA, "candidate_output": candidate, "propositions": propositions, "reference_receipt_ids": c.References}
	bundle := binding.Bundle
	bundle.Bindings = append([]lab.Binding{}, binding.Bundle.Bindings...)
	for i, b := range bundle.Bindings {
		if b.Stage != "linguistic_audit" {
			continue
		}
		b.PromptID = "lab-judge-v1"
		b.Template = fmt.Sprint(f.Judge["prompt_text"])
		b.PromptSHA = contracts.Digest([]byte(b.Template))
		b.Variables = []string{}
		b.Policy = lab.Policy{Stage: b.Stage, Instruction: fmt.Sprint(f.Judge["rubric_text"]), Order: []string{"prompt", "context_policy", "candidate", "rubric", "wire_schema"}, Variables: []string{}, Notes: "Dedicated diagnostic policy; original nine stage bundle remains unchanged"}
		b.PolicySHA = lab.Hash(b.Policy)
		b.InputSchema = "llm-quality-judge-input.schema.json"
		b.OutputSchema = "llm-quality-judge-output.schema.json"
		registry, _ := contracts.Registry()
		b.InputSHA = registry["llm-quality-judge-input"].SHA
		b.OutputSHA = registry["llm-quality-judge-output"].SHA
		bundle.Bindings[i] = b
	}
	bundle.Seal()
	var contextValue any
	_ = json.Unmarshal(f.Inputs[c.ID], &contextValue)
	judgeAssets := map[string]any{asset.ID: candidate, c.Input: contextValue}
	validate := func(raw []byte) error {
		return validateQualityJudge(raw, propositions, judgeAssets)
	}
	result, e := s.InvokeLLM(ctx, LLMRequest{NormalizeProjection: func(v any) any { return normalizeQualityJudge(v, judgeAssets) }, Operation: OperationRequest{Name: "quality_judge", Key: interpretationCallKey(operation, "judge"), Path: "/lab/eval/judge", Body: sourceBytes(input)}, FrozenProfile: &profile, Stage: "linguistic_audit", Input: input, Components: map[string]any{"candidate": candidate, "rubric": f.Judge["rubric_text"]}, Configuration: profileConfig, Bundle: bundle, Validate: validate}, client)
	if len(result.ReceiptIDs) > 0 {
		cleanup, cleanupDone := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer cleanupDone()
		_, de := s.Store.LLMDiagnostic(cleanup, result, binding.Configuration["llm_lab_capture_content"] == true, binding.Configuration["llm_lab_trace_enabled"] == true)
		if de != nil && e == nil {
			e = de
		}
	}
	var out map[string]any
	if len(result.Output) > 0 {
		_ = json.Unmarshal(result.Output, &out)
	}
	return out, result, e
}
func validateQualityJudge(raw []byte, propositions []any, assets map[string]any) error {
	var out struct {
		Verdicts []struct {
			ID       string  `json:"proposition_id"`
			Verdict  string  `json:"verdict"`
			Missing  *string `json:"missing_reason"`
			Evidence []struct {
				Asset   string `json:"asset_id"`
				Pointer string `json:"pointer"`
			} `json:"evidence"`
		} `json:"verdicts"`
	}
	if e := json.Unmarshal(raw, &out); e != nil {
		return e
	}
	allowed := map[string]bool{}
	for _, v := range propositions {
		allowed[fmt.Sprint(v.(map[string]any)["id"])] = true
	}
	seen := map[string]bool{}
	for _, v := range out.Verdicts {
		if !allowed[v.ID] || seen[v.ID] {
			return fmt.Errorf("unknown/duplicate proposition")
		}
		seen[v.ID] = true
		if v.Verdict == "unknown" && (v.Missing == nil || *v.Missing == "") {
			return fmt.Errorf("unknown needs missing evidence reason")
		}
		for _, ref := range v.Evidence {
			value, ok := assets[ref.Asset]
			if !ok {
				return ErrReference
			}
			if b, ok := value.(json.RawMessage); ok {
				_ = json.Unmarshal(b, &value)
			}
			if strings.HasPrefix(ref.Pointer, "cp:") {
				text, ok := value.(string)
				parts := strings.Split(ref.Pointer, ":")
				if !ok || len(parts) != 3 {
					return ErrReference
				}
				a, ea := strconv.Atoi(parts[1])
				b, eb := strconv.Atoi(parts[2])
				if ea != nil || eb != nil || a < 0 || b < a || b > len([]rune(text)) {
					return ErrReference
				}
			} else if _, ok := source.Pointer(value, ref.Pointer); !ok {
				return ErrReference
			}
		}
	}
	if len(seen) != len(allowed) {
		return fmt.Errorf("missing proposition verdict")
	}
	return nil
}
func qualityJudgeEvidence(c QualityCase, expected, judgment map[string]any, e *experiment.Evidence) {
	if e.Basis == nil {
		e.Basis = map[string]string{}
	}
	if e.Missing == nil {
		e.Missing = map[string]string{}
	}
	expect := map[string]map[string]any{}
	for _, v := range expected["semantic_propositions"].([]any) {
		m := v.(map[string]any)
		expect[fmt.Sprint(m["id"])] = m
	}
	for _, v := range judgment["verdicts"].([]any) {
		m := v.(map[string]any)
		reference := expect[fmt.Sprint(m["proposition_id"])]
		metric, n, d := "request_fulfillment_rate", "satisfied_applicable_request_predicates", "applicable_request_predicates"
		switch reference["scope"] {
		case "mutation":
			metric, n, d = "mutation_list_consistency_rate", "mutations_with_consistent_span_category_repair_and_surface", "applicable_declared_mutations"
		case "feedback":
			metric, n, d = "feedback_grounding_rate", "supported_factual_items_or_correctly_labelled_practice", "applicable_feedback_items"
		case "answer_mapping":
			metric, n, d = "explanation_accuracy", "correct_applicable_explanation_propositions", "applicable_reference_explanation_propositions"
		case "acoustic":
			e.Missing["llm_lab.audio_target_confirmation_rate"] = "text_judge_cannot_confirm_audio"
			continue
		}
		basis := "llm_judged"
		if c.Basis == "self_consistency" {
			basis = "self_consistency"
		}
		e.Basis["llm_lab."+metric] = basis
		if m["verdict"] == "unknown" {
			continue
		}
		qualityIncrement(e.Stats, d, 1)
		if m["verdict"] == "supported" {
			qualityIncrement(e.Stats, n, 1)
		} else {
			qualityIncrement(e.Stats, n, 0)
		}
	}
}
