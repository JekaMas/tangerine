package app

import (
	"context"
	"encoding/json"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/lab"
)

func (s *Storage) freezeReview(ctx context.Context, run ReviewRun) (ReviewFrozen, error) {
	f := ReviewFrozen{Manifest: nil, Measurements: []any{}}
	doc, e := s.ReadDocument(ctx, run.Case)
	if e != nil {
		return f, e
	}
	if doc.Kind != "ground-truth" {
		return f, ErrReference
	}
	if e = json.Unmarshal(doc.Payload, &f.Key); e != nil {
		return f, e
	}
	if run.Attempt != "" {
		f.Record, e = s.Attempt(ctx, run.Attempt)
		if e != nil {
			return f, e
		}
		if f.Record.Attempt["submitted_at"] == nil {
			return f, ErrAttemptState
		}
		if f.Record.Attempt["case_version_id"] != run.Case {
			result, err := s.readScoringResult(ctx, run.BaseResult)
			if err != nil {
				return f, err
			}
			score, ok := result["score"].(map[string]any)
			if !ok || score["case_version_id"] != run.Case {
				return f, ErrReference
			}
		}
		if f.Record.Context["result_id"] != run.BaseResult {
			return f, ErrRevision
		}
		state, err := s.interpretationState(ctx, run.Attempt)
		if err != nil {
			return f, err
		}
		if state == nil || state.Extraction == nil || state.Mapping == nil {
			return f, ErrAttemptState
		}
		if e = s.readInterpretationJSON(ctx, *state.Extraction, &f.Extraction); e != nil {
			return f, e
		}
		if e = s.readInterpretationJSON(ctx, *state.Mapping, &f.Mapping); e != nil {
			return f, e
		}
		// A selected prior revision retains its own admitted semantic checkpoint.
		var prior []byte
		e = s.DB.QueryRow(ctx, `SELECT payload FROM review_checkpoint WHERE attempt_id=$1 AND payload->>'new_result_id'=$2 AND payload->>'status'='complete' ORDER BY id LIMIT 1`, run.Attempt, run.BaseResult).Scan(&prior)
		if e != nil && e != pgx.ErrNoRows {
			return f, e
		}
		if e == nil {
			var r ReviewRun
			_ = json.Unmarshal(prior, &r)
			if r.Mapping != "" {
				if e = s.readInterpretationJSON(ctx, r.Mapping, &f.Mapping); e != nil {
					return f, e
				}
			}
			if r.NewCase != "" {
				d, err := s.ReadDocument(ctx, r.NewCase)
				if err != nil {
					return f, err
				}
				_ = json.Unmarshal(d.Payload, &f.Key)
			}
		}
		f.Configuration = f.Record.Context["configuration"].(map[string]any)
		f.Bundle = interpretationBundle(f.Record)
		f.Profile, e = interpretationProfile(f.Record, "adjudication")
		if e != nil {
			return f, e
		}
	} else {
		tx, err := beginWrite(ctx, s)
		if err != nil {
			return f, err
		}
		defer tx.Rollback(context.Background())
		// Review is optional; unrelated core evaluator setup cannot gate this action.
		var raw []byte
		f.Configuration = DefaultConfiguration()
		f.Bundle = lab.Shipped()
		err = tx.QueryRow(ctx, "SELECT d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id='local-configuration' FOR SHARE OF h").Scan(&raw)
		if err != nil && err != pgx.ErrNoRows {
			return f, err
		}
		if err == nil {
			_ = json.Unmarshal(raw, &f.Configuration)
		}
		if id, ok := f.Configuration["active_prompt_bundle_id"].(string); ok {
			if err = tx.QueryRow(ctx, "SELECT payload FROM document WHERE id=$1 AND kind='prompt-bundle'", id).Scan(&raw); err != nil {
				return f, err
			}
			_ = json.Unmarshal(raw, &f.Bundle)
		}
		stage := "case_review"
		if run.Purpose != "case_review" {
			stage = "adjudication"
		}
		f.Profile, e = FreezeProfile(f.Configuration, stage)
		if e != nil {
			return f, e
		}
		f.Record = AttemptRecord{Attempt: map[string]any{"case_version_id": run.Case}, Context: map[string]any{"configuration": f.Configuration, "prompt_bundle": f.Bundle}}
	}

	f.OriginalKey = reviewClone(f.Key)
	if run.TargetCase != "" {
		if run.Attempt == "" {
			return f, ErrInput
		}
		var raw []byte
		e = s.DB.QueryRow(ctx, `SELECT d.payload FROM reviewed_case_successor c JOIN document d ON d.id=c.correspondence_id WHERE c.old_case_version_id=$1 AND c.new_case_version_id=$2`, f.Key["case_version_id"], run.TargetCase).Scan(&raw)
		if e != nil {
			return f, ErrReference
		}
		var correspondence map[string]any
		_ = json.Unmarshal(raw, &correspondence)
		f.Correspondences = []any{correspondence}
		target, err := s.ReadDocument(ctx, run.TargetCase)
		if err != nil {
			return f, err
		}
		_ = json.Unmarshal(target.Payload, &f.Key)
		if f.Key["audio"].(map[string]any)["sha256"] != f.OriginalKey["audio"].(map[string]any)["sha256"] {
			return f, ErrConflict
		}
	}
	f.Resources, e = s.interpretationResources(ctx, AttemptRecord{Attempt: map[string]any{"case_version_id": f.Key["case_version_id"]}})
	if e != nil {
		return f, e
	}
	f.Measurements, e = s.reviewMeasurements(ctx, f.Key["case_version_id"].(string))
	if e != nil {
		return f, e
	}
	// Store the actual authored manifest, when present; imports honestly use null.
	var manifest *string
	e = s.DB.QueryRow(ctx, `WITH RECURSIVE ancestors(id) AS (SELECT $1::text UNION SELECT c.old_case_version_id::text FROM reviewed_case_successor c JOIN ancestors a ON c.new_case_version_id=a.id) SELECT d.payload->>'mutation_manifest_asset_id' FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.kind='preparation-state' AND d.payload->>'key_id' IN (SELECT id FROM ancestors UNION SELECT source_key_id::text FROM listening_case l JOIN ancestors a ON a.id=l.case_version_id) LIMIT 1`, run.Case).Scan(&manifest)
	if e != nil && e != pgx.ErrNoRows {
		return f, e
	}
	if manifest != nil {
		if e = s.readInterpretationJSON(ctx, *manifest, &f.Manifest); e != nil {
			return f, e
		}
	}
	taxonomy, err := generationRegistry("error-taxonomy.v1.yaml")
	if err != nil {
		return f, err
	}
	f.Taxonomy, _, _, err = mutationSelection(map[string]any{"targets": []any{}}, taxonomy, []byte(`{"recipes":[]}`), []byte(`{"rows":[]}`))
	if err != nil {
		return f, err
	}
	return f, nil
}
func reviewCandidate(key map[string]any) map[string]any {
	units := []any{}
	for _, v := range key["units"].([]any) {
		u := v.(map[string]any)
		p := map[string]any{}
		for _, k := range []string{"id", "primary_taxonomy_id", "accepted_taxonomy_ids", "secondary_taxonomy_ids", "domain", "expected_judgment", "status_label", "utterance_ids", "text_spans", "realization", "severity", "weight", "difficulty", "correction_eligible", "corrections", "explanation_eligible", "rationale_required_propositions", "rationale_forbidden_propositions", "rationale"} {
			p[k] = u[k]
		}
		units = append(units, p)
	}
	turns := []any{}
	for _, v := range key["utterances"].([]any) {
		u := v.(map[string]any)
		turns = append(turns, map[string]any{"id": u["id"], "speaker_id": u["speaker_id"], "canonical_text": u["canonical_text"], "surface_text": u["surface_text"]})
	}
	return map[string]any{"schema_version": "1.0.0", "blueprint_id": key["case_version_id"], "status": "candidate", "failure_reason": nil, "utterances": turns, "planned_units": units}
}

// A compact literal view makes before/after and allowed repairs explicit;
// full key/rules/source data remain unchanged in the typed stage input.
func reviewRepairReference(key map[string]any) []any {
	out := []any{}
	for _, value := range key["units"].([]any) {
		unit := value.(map[string]any)
		realization := unit["realization"].(map[string]any)
		repairs := []any{}
		for _, value := range unit["corrections"].([]any) {
			option := value.(map[string]any)
			repairs = append(repairs, map[string]any{"option_id": option["id"], "kind": option["kind"], "valid_corrected_text": option["text"], "approved_alternative_texts": option["approved_text_alternatives"], "correct_pronunciation": option["ipa"]})
		}
		out = append(out, map[string]any{"unit_id": unit["id"], "mode": realization["mode"], "correct_text_before_mutation": realization["canonical_text"], "presented_text_after_mutation": realization["surface_text"], "correct_pronunciation": realization["canonical_ipa"], "planned_mutated_pronunciation": realization["intended_ipa"], "observed_pronunciation": realization["observed_ipa"], "approved_repair_options": repairs, "current_key_rationale": unit["rationale"], "current_rationale_required_propositions": unit["rationale_required_propositions"], "current_rationale_forbidden_propositions": unit["rationale_forbidden_propositions"]})
	}
	return out
}
func reviewInput(run ReviewRun, f ReviewFrozen) (map[string]any, map[string]any) {
	modality := "text"
	if len(f.Resources.Evidence) > 0 {
		modality = "text_with_speech_evidence"
	}
	taxonomy := reviewTaxonomy(run, f)
	input := map[string]any{"schema_version": "2.0.0", "purpose": run.Purpose, "public_context": f.Key["public_context"], "candidate": nil, "ground_truth": f.Key, "answer": nil, "extraction": nil, "prior_decisions": nil, "dispute_statement": nil, "measurements": f.Measurements, "evidence": f.Resources.Evidence, "taxonomy_context": taxonomy, "input_modality": modality, "mutation_manifest": f.Manifest}
	if f.Measurements == nil {
		input["measurements"] = []any{}
	}
	if run.Purpose == "case_review" {
		input["candidate"] = reviewCandidate(f.Key)
	} else if run.Attempt != "" {
		input["answer"] = f.Record.Attempt["answer_text"]
		input["extraction"] = f.Extraction.Extraction
		input["prior_decisions"] = map[string]any{"schema_version": "1.0.0", "decisions": f.Mapping.Decisions}
		if run.Purpose == "dispute" {
			input["dispute_statement"] = run.Statement
		}
	}
	if run.Purpose == "dispute" {
		input["dispute_statement"] = run.Statement
	}
	parts := map[string]any{"candidate": input["candidate"], "canonical_script": f.Key["utterances"], "public_context": f.Key["public_context"], "taxonomy": map[string]any{"selected_rules": "Use taxonomy_context in Complete stage input for exact relevant rules.", "registered_catalog": mappingTaxonomyContext(f.Resources, run.Statement)}, "mutation_key": map[string]any{"case_version_id": f.Key["case_version_id"], "unit_repair_reference": reviewRepairReference(f.Key), "complete_key_location": "The complete ground_truth and authored mutation_manifest in Complete stage input retain all correction/rationale obligations, original sources and mutation history."}, "evidence": f.Resources.Evidence, "answer": input["answer"], "extraction": input["extraction"], "prior_decisions": input["prior_decisions"], "dispute_statement": input["dispute_statement"]}
	if len(f.Measurements) > 0 {
		parts["evidence"] = map[string]any{"native_evidence": f.Resources.Evidence, "audio_measurements": f.Measurements, "meaning": "Saved method reports only. Model findings are inferences; this review receives reports, not audio. Unavailable measurements remain unknown."}
	}
	if run.Attempt == "" && run.Purpose == "dispute" {
		for _, part := range []string{"answer", "extraction", "prior_decisions"} {
			parts[part] = map[string]any{"applicable": false, "reason": "This is a case-only dispute; no listener answer or answer judgments exist."}
		}
	}
	if run.Attempt != "" {
		views := listenerFeedbackAssessments(f.Extraction, f.Mapping)
		for _, value := range views {
			view := value.(map[string]any)
			view["prior_assessor_note"] = view["contextual_note"]
			delete(view, "contextual_note")
		}
		parts["prior_decisions"] = map[string]any{"assessment_location": "The complete original machine assessment is prior_decisions in Complete stage input. It is not listener wording.", "component_presence": "Only original answer/extraction spans determine supplied components. not_supplied means omitted, not rejected.", "listener_answer_assessments": views}
	}
	if run.TargetCase != "" {
		parts["prior_decisions"] = map[string]any{"prior_decisions": parts["prior_decisions"], "original_ground_truth": f.OriginalKey, "unit_correspondences": f.Correspondences}
	}
	return input, parts
}

// Keep relevant complete rules and the full category catalogue. The immutable
// frozen registry remains available for admission without repeating all rules.
func reviewTaxonomy(run ReviewRun, f ReviewFrozen) map[string]any {
	selected := map[string]bool{}
	for _, v := range mappingTaxonomyContext(f.Resources, run.Statement) {
		row := v.(map[string]any)
		if len(row) > 2 {
			selected[row["id"].(string)] = true
		}
	}
	out := reviewClone(f.Taxonomy)
	entries := []any{}
	for _, v := range f.Taxonomy["entries"].([]any) {
		row := v.(map[string]any)
		if selected[row["id"].(string)] {
			entries = append(entries, row)
		}
	}
	out["entries"] = entries
	return out
}
