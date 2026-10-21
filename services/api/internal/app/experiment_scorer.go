package app

import (
	"encoding/json"
	"fmt"
	"math/big"
	"strings"
	"tangerine.local/api/internal/experiment"
)

func qualityIncrement(stats map[string]string, k string, n int) {
	v := new(big.Int)
	v.SetString(stats[k], 10)
	stats[k] = v.Add(v, big.NewInt(int64(n))).String()
}
func qualityDeterministicEvidence(c QualityCase, p QualityExperiment, input, expected map[string]any, output any, packet map[string]any, e *experiment.Evidence) {
	if e.Basis == nil {
		e.Basis = map[string]string{}
	}
	if e.Missing == nil {
		e.Missing = map[string]string{}
	}
	if c.Basis == "self_consistency" {
		for _, id := range []string{"detection_precision", "detection_recall", "detection_f1", "category_accuracy", "repair_accuracy", "explanation_accuracy", "score_mae_pp"} {
			e.Basis["llm_lab."+id] = "self_consistency"
		}
	}
	candidate, _ := output.(map[string]any)
	if ref, ok := expected["expected_mapping"].(map[string]any); ok {
		actual := candidate
		if p.Scope == "answer_pipeline" {
			if native, ok := candidate["quality_native_mapping"]; ok {
				_ = json.Unmarshal(sourceBytes(native), &actual)
			}
		}
		if actual != nil {
			qualityMappingEvidence(ref, actual, e)
			e.Aligned = true
			var mapping SemanticMapping
			_ = json.Unmarshal(sourceBytes(actual), &mapping)
			e.Detected = []string{}
			seen := map[string]bool{}
			for _, d := range mapping.Decisions {
				if d.Decision == "matched_error" && d.Unit != nil && !seen[*d.Unit] {
					seen[*d.Unit] = true
					e.Detected = append(e.Detected, *d.Unit)
				}
			}
		}
	}
	// Expected scalar values are references, never copied into observed values.
	if score, ok := packet["native_score"].(map[string]any); ok {
		qualityScoreError(expected, score, e)
	}
	if c.Stage == "case_generation" && c.Phase != nil && *c.Phase == "mutation" {
		if canonical, ok := expected["expected_canonical_sha256"].(string); ok {
			e.Stats["completed_mutation_outputs"] = "1"
			e.Stats["mutation_outputs_with_exact_saved_canonical"] = "0"
			if packet["canonical_sha256"] == canonical {
				e.Stats["mutation_outputs_with_exact_saved_canonical"] = "1"
			}
		}
	}
	if p.Scope == "generation_pipeline" || p.Scope == "full_flow" {
		if original, ok := packet["initial_canonical_sha256"].(string); ok {
			if final, ok := packet["canonical_sha256"].(string); ok {
				e.Stats["completed_mutation_outputs"] = "1"
				e.Stats["mutation_outputs_with_exact_saved_canonical"] = "0"
				if original == final {
					e.Stats["mutation_outputs_with_exact_saved_canonical"] = "1"
				}
			}
		}
	}
	e.Missing["llm_lab.audio_target_confirmation_rate"] = "no_relevant_actual_audio_observation"
}
func qualityMappingEvidence(reference, actual map[string]any, e *experiment.Evidence) {
	var want, got SemanticMapping
	_ = json.Unmarshal(sourceBytes(reference), &want)
	_ = json.Unmarshal(sourceBytes(actual), &got)
	expected := map[string]SemanticDecision{}
	predicted := map[string]SemanticDecision{}
	for _, d := range want.Decisions {
		if d.Unit != nil && d.Decision == "matched_error" && d.Duplicate == nil {
			expected[*d.Unit] = d
		}
	}
	for _, d := range got.Decisions {
		if d.Unit != nil && d.Decision == "matched_error" && d.Duplicate == nil {
			predicted[*d.Unit] = d
		}
	}
	tp, fp, fn := 0, 0, 0
	falseClaims := map[string]bool{}
	for _, d := range got.Decisions {
		if d.Decision == "false_positive" && d.Duplicate == nil && !falseClaims[d.Claim] {
			falseClaims[d.Claim] = true
			fp++
		}
	}
	for unit, w := range expected {
		g, ok := predicted[unit]
		if !ok {
			fn++
			continue
		}
		tp++
		if w.Category != nil {
			qualityIncrement(e.Stats, "applicable_reference_category_decisions", 1)
			n := 0
			if g.Category != nil && *w.Category == *g.Category {
				n = 1
			}
			qualityIncrement(e.Stats, "correct_reference_category_decisions", n)
			qualityIncrement(e.Stats, "leaf_tp:"+*w.Category, 1)
			qualityIncrement(e.Stats, "leaf_fn:"+*w.Category, 0)
		}
		qualityComponentEvidence(w.Correction, g.Correction, "repair", e)
		qualityComponentEvidence(w.Explanation, g.Explanation, "explanation", e)
	}
	for unit := range predicted {
		if _, ok := expected[unit]; !ok {
			fp++
		}
	}
	for unit, w := range expected {
		if _, ok := predicted[unit]; !ok && w.Category != nil {
			qualityIncrement(e.Stats, "leaf_tp:"+*w.Category, 0)
			qualityIncrement(e.Stats, "leaf_fn:"+*w.Category, 1)
		}
	}
	e.Stats["TP"] = fmt.Sprint(tp)
	e.Stats["FP"] = fmt.Sprint(fp)
	e.Stats["FN"] = fmt.Sprint(fn)
}
func qualityComponentEvidence(w, g SemanticComponent, kind string, e *experiment.Evidence) {
	if !w.Supplied {
		return
	}
	expected := map[string]string{}
	for _, id := range w.Satisfied {
		expected[id] = "supported"
	}
	for _, id := range w.Violated {
		expected[id] = "violated"
	}
	actual := map[string]string{}
	for _, id := range g.Satisfied {
		actual[id] = "supported"
	}
	for _, id := range g.Violated {
		actual[id] = "violated"
	}
	n, d := "correct_applicable_repair_propositions", "applicable_reference_repair_propositions"
	if kind == "explanation" {
		n, d = "correct_applicable_explanation_propositions", "applicable_reference_explanation_propositions"
	}
	for id, status := range expected {
		qualityIncrement(e.Stats, d, 1)
		yes := 0
		if actual[id] == status {
			yes = 1
		}
		qualityIncrement(e.Stats, n, yes)
	}
}
func qualityScoreError(expected, score map[string]any, e *experiment.Evidence) {
	composite, ok := score["composite"].(map[string]any)
	if !ok {
		return
	}
	exact, ok := composite["exact_value_0_100"].(map[string]any)
	if !ok {
		return
	}
	n, _ := experiment.Rat(fmt.Sprint(exact["numerator"]))
	d, _ := experiment.Rat(fmt.Sprint(exact["denominator"]))
	if n == nil || d == nil || d.Sign() == 0 {
		return
	}
	actual := n.Quo(n, d)
	rows, _ := expected["expected_metric_values"].([]any)
	for _, v := range rows {
		m := v.(map[string]any)
		if m["metric_id"] != "composite" {
			continue
		}
		want, er := experiment.Rat(fmt.Sprint(m["value"]))
		if m["numerator"] != nil && m["denominator"] != nil {
			n, en := experiment.Rat(fmt.Sprint(m["numerator"]))
			d, ed := experiment.Rat(fmt.Sprint(m["denominator"]))
			if en != nil || ed != nil || d.Sign() == 0 {
				return
			}
			want = n.Quo(n, d)
			er = nil
		}
		if er != nil {
			return
		}
		diff := new(big.Rat).Sub(actual, want)
		if diff.Sign() < 0 {
			diff.Neg(diff)
		}
		e.Stats["absolute_score_error_pp_numerator"] = diff.Num().String()
		e.Stats["absolute_score_error_pp_denominator"] = diff.Denom().String()
		e.Stats["paired_reference_scores"] = "1"
	}
}

// Generation statistics read the actual saved native manifest/word counts. A
// requested target alone never supplies a measurement or linguistic success.
func qualityGenerationEvidence(input, candidate, manifest map[string]any, e *experiment.Evidence) {
	request := input
	if r, ok := input["exercise_request"].(map[string]any); ok {
		request = r
	}
	qualityRequestMutationEvidence(request, candidate, e)
	target, ok := request["text_length_words"].(float64)
	if !ok || target <= 0 {
		return
	}
	if words, ok := manifest["surface_word_count"].(float64); ok {
		deviation := words - target
		if deviation < 0 {
			deviation = -deviation
		}
		e.Stats["surface_word_absolute_deviation"] = fmt.Sprint(deviation)
		e.Stats["requested_words"] = fmt.Sprint(target)
	}
	if words, ok := manifest["canonical_word_count"].(float64); ok {
		deviation := words - target
		if deviation < 0 {
			deviation = -deviation
		}
		e.Stats["canonical_word_absolute_deviation"] = fmt.Sprint(deviation)
	}
	if requested, ok := request["speaker_count"].(float64); ok {
		speakers := map[string]bool{}
		if turns, ok := candidate["utterances"].([]any); ok {
			for _, turn := range turns {
				speakers[fmt.Sprint(turn.(map[string]any)["speaker_id"])] = true
			}
			qualityIncrement(e.Stats, "applicable_request_predicates", 1)
			n := 0
			if len(speakers) == int(requested) {
				n = 1
			}
			qualityIncrement(e.Stats, "satisfied_applicable_request_predicates", n)
		}
	}
}

func qualityRequestMutationEvidence(request, candidate map[string]any, e *experiment.Evidence) {
	units, ok := candidate["planned_units"].([]any)
	if !ok {
		return
	}
	count := 0
	domains := map[string]bool{}
	for _, v := range units {
		u := v.(map[string]any)
		if u["expected_judgment"] != "true_error" {
			continue
		}
		count++
		id, _ := u["primary_taxonomy_id"].(string)
		for _, family := range []string{"grammar", "lexis", "pronunciation.segmental", "pronunciation.suprasegmental", "fluency", "discourse", "pragmatics_register"} {
			if strings.HasPrefix(id, family+".") {
				domains[family] = true
			}
		}
	}
	predicate := func(ok bool) {
		qualityIncrement(e.Stats, "applicable_request_predicates", 1)
		n := 0
		if ok {
			n = 1
		}
		qualityIncrement(e.Stats, "satisfied_applicable_request_predicates", n)
	}
	if n, ok := request["mutation_count"].(float64); ok {
		predicate(count == int(n))
	}
	families, _ := request["category_families"].([]any)
	for _, v := range families {
		family := fmt.Sprint(v)
		found := domains[family]
		if family == "pronunciation" {
			found = domains["pronunciation.segmental"] || domains["pronunciation.suprasegmental"]
		}
		predicate(found)
	}
}
