package app

// A finite, explicit on-demand smoke observation for the affected shipped
// prompts. It creates its own exercise/attempt and never rewrites user records.
import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"os"
	"path/filepath"
	"tangerine.local/api/internal/lab"
	"testing"
)

func TestLinguisticAffectedAnswerNegative(t *testing.T) {
	dir := os.Getenv("TANGERINE_LINGUISTIC_FLOW")
	if dir == "" {
		t.Skip("Explicit included/local flow observation only")
	}
	read := func(name string, value any) {
		raw, e := os.ReadFile(filepath.Join(dir, name))
		if e != nil {
			t.Fatal(e)
		}
		if e = json.Unmarshal(raw, value); e != nil {
			t.Fatal(e)
		}
	}
	save := func(name string, value any) {
		raw, _ := json.MarshalIndent(value, "", "  ")
		if e := os.WriteFile(filepath.Join(dir, name), append(raw, '\n'), 0600); e != nil {
			t.Fatal(e)
		}
	}
	var frozen struct {
		Configuration map[string]any `json:"configuration"`
		Bundle        lab.Bundle     `json:"bundle"`
	}
	read("flow-binding.json", &frozen)
	ctx := qualityContext(context.Background(), qualityBinding{Configuration: frozen.Configuration, Bundle: frozen.Bundle})
	store, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	if e != nil {
		t.Fatal(e)
	}
	defer store.DB.Close()
	var key map[string]any
	read("published-ground-truth.json", &key)
	caseID := key["case_version_id"].(string)
	// Authored after inspecting the actual clean/surface utterances, independently
	// of the generated rubric: two ticket -> two tickets is the number error.
	// Shall I book is a valid British offer. Both universal explanations are false.
	answer := "The first speaker says 'two ticket'. It should be 'two tickets' because all English plurals end in -s. Also, change 'Shall I book' to 'Should I book' because shall is never correct in a British offer."
	var start map[string]any
	if _, err := os.Stat(filepath.Join(dir, "attempt-start.json")); os.IsNotExist(err) {
		raw, _ := json.Marshal(map[string]any{"case_version_id": caseID, "case_sha256": key["case_sha256"], "requested_language": "en"})
		start, e = store.StartAttempt(ctx, raw, uuid.NewString())
		if e != nil {
			t.Fatal(e)
		}
		save("attempt-start.json", start)
	} else {
		read("attempt-start.json", &start)
	}
	attempt := start["attempt_id"].(string)
	record, e := store.Attempt(ctx, attempt)
	if e != nil {
		t.Fatal(e)
	}
	if record.Attempt["submitted_at"] == nil {
		raw, _ := json.Marshal(map[string]any{"answer_text": answer, "requested_language": "en"})
		_, _, e = store.WriteAnswer(ctx, attempt, uuid.NewString(), 0, raw, true)
		if e != nil {
			t.Fatal(e)
		}
	}
	s := NewServer(store, os.Getenv("APP_ORIGIN"), os.Getenv("SPEECH_URL"))
	record, e = store.Attempt(ctx, attempt)
	if e != nil {
		t.Fatal(e)
	}
	state, e := s.InterpretAttempt(ctx, attempt, uuid.NewString(), int64(record.Attempt["revision"].(float64)), record.Attempt["answer_utf8_sha256"].(string), record.Attempt["configuration_sha256"].(string), nil)
	save("interpretation-observation.json", map[string]any{"state": state, "error": fmt.Sprint(e), "answer": answer})
	if e != nil {
		t.Fatal("actual answer pipeline", e)
	}
	if state.Result == nil {
		t.Fatal("actual result missing", state)
	}
	result, e := store.readScoringResult(ctx, *state.Result)
	if e != nil {
		t.Fatal(e)
	}
	save("actual-score-feedback.json", result)
	if state.Mapping != nil {
		var mapping SemanticMapping
		if e = store.readInterpretationJSON(ctx, *state.Mapping, &mapping); e != nil {
			t.Fatal(e)
		}
		save("actual-mapping.json", mapping)
	}
	score := result["score"].(map[string]any)
	counts := score["counts"].(map[string]any)
	if counts["tp"] != float64(1) || counts["fp"] != float64(1) || counts["fn"] != float64(0) {
		t.Fatal("independent error/control judgments differ", counts)
	}
	metrics := score["metrics"].(map[string]any)
	for name, want := range map[string]float64{"correction.strict_accuracy": 1, "explanation.graded_accuracy": 0, "detection.precision": 0.5} {
		metric := metrics[name].(map[string]any)
		if metric["value"] != want {
			t.Fatal(name, metric, want)
		}
	}
	if result["feedback_status"] != "complete" {
		t.Fatal("actual comments/recommendations incomplete", result["feedback_status"])
	}
	save("answer-expectations.json", map[string]any{"origin": "independent authored judgment of actual text, not key self-consistency", "tp": 1, "fp": 1, "fn": 0, "correction": 1, "supplied_false_explanation": 0, "omission_policy": "no penalty; covered in native all-leaf tests", "attempt_id": attempt, "result_id": *state.Result})
}

func TestLinguisticAffectedPreparationPositive(t *testing.T) {
	dir := os.Getenv("TANGERINE_LINGUISTIC_FLOW")
	if dir == "" {
		t.Skip("Explicit included/local flow observation only")
	}
	if e := os.MkdirAll(dir, 0700); e != nil {
		t.Fatal(e)
	}
	ctx := context.Background()
	store, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	if e != nil {
		t.Fatal(e)
	}
	defer store.DB.Close()
	config, _, e := store.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	p, e := FreezeProfile(config, "case_generation")
	if e != nil || p.Provider != "openai_chatgpt" || p.Billing != "included_subscription" {
		t.Fatal("Included-only profile required; no fallback", e)
	}
	config["llm_lab_capture_content"] = true
	config["llm_lab_trace_enabled"] = true
	config["mapping_audit_enabled"] = true
	delete(config, "configuration_sha256")
	config["configuration_sha256"] = lab.Hash(config)
	ctx = qualityContext(ctx, qualityBinding{Configuration: config, Bundle: lab.Shipped()})
	s := NewServer(store, os.Getenv("APP_ORIGIN"), os.Getenv("SPEECH_URL"))
	save := func(name string, value any) {
		raw, _ := json.MarshalIndent(value, "", "  ")
		if e := os.WriteFile(filepath.Join(dir, name), append(raw, '\n'), 0600); e != nil {
			t.Fatal(e)
		}
	}
	read := func(name string) map[string]any {
		raw, e := os.ReadFile(filepath.Join(dir, name))
		if os.IsNotExist(e) {
			return nil
		}
		if e != nil {
			t.Fatal(e)
		}
		var value map[string]any
		if e = json.Unmarshal(raw, &value); e != nil {
			t.Fatal(e)
		}
		return value
	}
	b := read("blueprint.json")
	if b == nil {
		raw, _ := json.Marshal(map[string]any{"exercise_request": map[string]any{"topic": "Two colleagues planning a train journey. Include the exact phrase two tickets in natural correct dialogue; use standard British English and keep the numerical context audible.", "speaker_count": 2, "text_length_words": 45, "english_level": "B1", "category_families": []string{"grammar"}, "mutation_count": 1}, "targets": []any{map[string]any{"taxonomy_id": "grammar.nouns.number", "min_count": 1, "max_count": 1, "expected_judgment": "true_error", "hard_render_constraints": []any{}}}})
		b, e = store.WriteBlueprint(ctx, raw, uuid.NewString())
		if e != nil {
			t.Fatal(e)
		}
		save("blueprint.json", b)
	}
	request := CanonicalPreparationRequest{BlueprintID: b["id"].(string), ConfigurationSHA: config["configuration_sha256"].(string), Sources: []string{}, Attempt: 1}
	prep := read("canonical.json")
	if prep == nil {
		prep, e = s.PrepareCanonical(ctx, request, uuid.NewString(), nil)
		save("canonical-observation.json", map[string]any{"preparation": prep, "error": fmt.Sprint(e)})
		if e != nil {
			t.Fatal("actual canonical stage", e)
		}
		save("canonical.json", prep)
	}
	id := prep["id"].(string)
	request.PreparationID = &id
	request.Attempt = 2
	mutated := read("mutation.json")
	if mutated == nil {
		mutated, e = s.PrepareMutation(ctx, request, uuid.NewString(), nil)
		save("mutation-observation.json", map[string]any{"preparation": mutated, "error": fmt.Sprint(e)})
		if e != nil {
			t.Fatal("actual mutation stage", e)
		}
		save("mutation.json", mutated)
	}
	rendered := read("render.json")
	if rendered == nil {
		rendered, e = s.RenderPreparation(ctx, id, uuid.NewString(), 1, nil)
		save("render-observation.json", map[string]any{"preparation": rendered, "error": fmt.Sprint(e)})
		if e != nil {
			t.Fatal("actual local speech stage", e)
		}
		save("render.json", rendered)
	}
	for _, field := range []string{"canonical_asset_id", "mutated_asset_id", "mutation_manifest_asset_id", "audio_asset_id"} {
		asset, e := store.ReadAsset(ctx, rendered[field].(string))
		if e != nil {
			t.Fatal(e)
		}
		name := field + ".json"
		if field == "audio_asset_id" {
			name = "actual-flow.wav"
		}
		if e = os.WriteFile(filepath.Join(dir, name), asset, 0600); e != nil {
			t.Fatal(e)
		}
	}
	doc, e := store.ReadDocument(ctx, rendered["key_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	if e = os.WriteFile(filepath.Join(dir, "ground-truth.json"), doc.Payload, 0600); e != nil {
		t.Fatal(e)
	}
	var key map[string]any
	_ = json.Unmarshal(doc.Payload, &key)
	if len(key["units"].([]any)) != 1 {
		t.Fatal("one explicit requested mutation required")
	}
	unit := key["units"].([]any)[0].(map[string]any)
	if unit["primary_taxonomy_id"] != "grammar.nouns.number" || unit["expected_judgment"] != "true_error" {
		t.Fatal("wrong generated target", unit)
	}
	realization := unit["realization"].(map[string]any)
	if realization["canonical_text"] != "two tickets" || realization["surface_text"] != "two ticket" {
		t.Fatal("independently requested numeric noun contrast is absent", realization)
	}
	// This checkpoint permits source inspection before independently authoring the
	// listener answer. The generated key is not used as linguistic gold.
	var published string
	if e = store.DB.QueryRow(ctx, "SELECT case_version_id FROM listening_case WHERE source_key_id=$1", rendered["key_id"]).Scan(&published); e != nil {
		t.Fatal(e)
	}
	pub, e := store.ReadDocument(ctx, published)
	if e != nil {
		t.Fatal(e)
	}
	if e = os.WriteFile(filepath.Join(dir, "published-ground-truth.json"), pub.Payload, 0600); e != nil {
		t.Fatal(e)
	}
	save("flow-binding.json", map[string]any{"configuration": config, "bundle": lab.Shipped(), "preparation_id": id, "case_id": published, "origin": "actual on-demand generated smoke, not benchmark gold"})
}

func observeLinguisticReviewStage(t *testing.T, answerReview bool) {
	t.Helper()
	dir := os.Getenv("TANGERINE_LINGUISTIC_FLOW")
	if dir == "" {
		t.Skip("Explicit included-plan stage observation only")
	}
	read := func(name string, value any) {
		raw, e := os.ReadFile(filepath.Join(dir, name))
		if e != nil {
			t.Fatal(e)
		}
		if e = json.Unmarshal(raw, value); e != nil {
			t.Fatal(e)
		}
	}
	save := func(name string, value any) {
		raw, _ := json.MarshalIndent(value, "", "  ")
		if e := os.WriteFile(filepath.Join(dir, name), append(raw, '\n'), 0600); e != nil {
			t.Fatal(e)
		}
	}
	ctx := context.Background()
	store, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	if e != nil {
		t.Fatal(e)
	}
	defer store.DB.Close()
	var key map[string]any
	read("published-ground-truth.json", &key)
	var binding struct {
		Configuration map[string]any `json:"configuration"`
		Bundle        lab.Bundle     `json:"bundle"`
	}
	read("flow-binding.json", &binding)
	run := ReviewRun{ID: uuid.NewString(), ReviewContextID: uuid.NewString(), Case: key["case_version_id"].(string), Purpose: "case_review", Modality: "text"}
	stage := "case_review"
	if answerReview {
		var expected map[string]any
		read("answer-expectations.json", &expected)
		run.Purpose = "answer_reconsideration"
		run.Attempt = expected["attempt_id"].(string)
		run.BaseResult = expected["result_id"].(string)
		run.Statement = "Check both supplied universal explanations against ordinary counterexamples. The noun repair two ticket to two tickets is valid; Shall I book is a permitted British offer. Preserve independently supported primary credit."
		stage = "adjudication"
	}
	f, e := store.freezeReview(ctx, run)
	if e != nil {
		t.Fatal(e)
	}
	// Stage experiment only: use the preparation's exact candidate bundle and
	// run-scoped capture; do not activate workspace configuration or publish a
	// review/key/result revision.
	f.Configuration = binding.Configuration
	f.Bundle = binding.Bundle
	p, e := FreezeProfile(f.Configuration, stage)
	if e != nil || p.Provider != "openai_chatgpt" || p.Billing != "included_subscription" {
		t.Fatal("Included-only stage profile required", e)
	}
	f.Profile = p
	input, parts := reviewInput(run, f)
	s := NewServer(store, os.Getenv("APP_ORIGIN"), os.Getenv("SPEECH_URL"))
	outputPath := filepath.Join(dir, stage+"-stage.json")
	var observed struct {
		Output map[string]any `json:"output"`
		Result LLMResult      `json:"result"`
		Error  string         `json:"error"`
	}
	if _, err := os.Stat(outputPath); os.IsNotExist(err) {
		result, err := s.InvokeLLM(ctx, LLMRequest{Stage: stage, FrozenProfile: &p, Input: input, Components: parts, Configuration: f.Configuration, Bundle: f.Bundle, Operation: OperationRequest{Name: "linguistic_stage_smoke", Key: uuid.NewString(), Path: "/lab/linguistic/stage", Body: json.RawMessage(`{}`)}, Validate: func(raw []byte) error { _, err := admitReview(raw, run, f); return err }}, nil)
		if len(result.Output) > 0 {
			_ = json.Unmarshal(result.Output, &observed.Output)
		}
		observed.Result, observed.Error = result, fmt.Sprint(err)
		save(stage+"-stage.json", observed)
		save(stage+"-input.json", map[string]any{"input": input, "components": parts, "scope": "actual native stage experiment; no published review"})
		if len(result.ReceiptIDs) > 0 {
			if _, de := store.LLMDiagnostic(ctx, result, true, true); de != nil {
				t.Fatal("actual diagnostic export", de)
			}
		}
		if err != nil {
			t.Fatal("actual review stage", err)
		}
	} else {
		read(stage+"-stage.json", &observed)
	}
	if observed.Error != "<nil>" || observed.Output["resolution"] != "supported" {
		t.Fatal("independently inspected key/primary judgments were not supported", observed.Error, observed.Output)
	}
	if answerReview {
		decisions := observed.Output["decisions"].(map[string]any)["decisions"].([]any)
		matched, falsePositive, unsupported := 0, 0, 0
		for _, value := range decisions {
			d := value.(map[string]any)
			if d["decision"] == "matched_error" {
				matched++
			}
			if d["decision"] == "false_positive" {
				falsePositive++
			}
			for _, value := range d["explanation"].(map[string]any)["additional_assertions"].([]any) {
				if value.(map[string]any)["judgment"] == "unsupported" {
					unsupported++
				}
			}
		}
		if matched == 0 || falsePositive == 0 || unsupported < 2 {
			t.Fatal("actual reconsideration lost valid correction, acceptable offer or false-explanation findings", matched, falsePositive, unsupported)
		}
	}
}

func TestLinguisticAffectedReviewPositive(t *testing.T) {
	observeLinguisticReviewStage(t, false)
}

func TestLinguisticAffectedAdjudicationNegative(t *testing.T) {
	observeLinguisticReviewStage(t, true)
}
