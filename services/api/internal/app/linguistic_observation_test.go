package app

// Explicit opt-in experiment on the existing included-only connection. This
// uses the production semantic-judge/provider/diagnostic owners, not a new SDK.
import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"os"
	"path/filepath"
	"tangerine.local/api/internal/experiment"
	"tangerine.local/api/internal/lab"
	"testing"
)

func TestLinguisticIncludedModel(t *testing.T) {
	inputPath := os.Getenv("TANGERINE_LINGUISTIC_BATCH")
	if inputPath == "" {
		t.Skip("Actual included-plan inference requires an explicit frozen batch")
	}
	raw, e := os.ReadFile(inputPath)
	if e != nil {
		t.Fatal(e)
	}
	var batch struct {
		Batch int `json:"batch"`
		Cases []struct {
			ID       string         `json:"id"`
			Input    map[string]any `json:"input"`
			Expected string         `json:"expected"`
		} `json:"cases"`
	}
	if e = json.Unmarshal(raw, &batch); e != nil || len(batch.Cases) == 0 || len(batch.Cases) > 24 {
		t.Fatal("Invalid finite batch", e)
	}
	outdir := os.Getenv("TANGERINE_LINGUISTIC_OUTPUT")
	if e = os.MkdirAll(outdir, 0700); e != nil {
		t.Fatal(e)
	}
	save := func(name string, value any) {
		b, err := json.MarshalIndent(value, "", "  ")
		if err != nil {
			t.Fatal(err)
		}
		if err = os.WriteFile(filepath.Join(outdir, name), append(b, '\n'), 0600); err != nil {
			t.Fatal(err)
		}
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
	p, e := FreezeProfile(config, "linguistic_audit")
	if e != nil || p.Provider != "openai_chatgpt" || p.Billing != "included_subscription" {
		t.Fatal("Only the existing included ChatGPT profile is allowed; no fallback", e)
	}
	config["llm_lab_trace_enabled"] = true
	config["llm_lab_capture_content"] = true
	delete(config, "configuration_sha256")
	config["configuration_sha256"] = lab.Hash(config)
	s := NewServer(store, os.Getenv("APP_ORIGIN"), os.Getenv("SPEECH_URL"))
	candidate := map[string]any{}
	propositions := []any{}
	expected := map[string]string{}
	for _, row := range batch.Cases {
		candidate[row.ID] = row.Input
		propositions = append(propositions, map[string]any{"id": row.ID, "proposition": fmt.Sprintf("For item %s, answer its exact question using its context and realization.", row.ID), "scope": "canonical_text"})
		expected[row.ID] = row.Expected
	}
	// Expected labels, taxonomy IDs, control reasons and canonical counterparts
	// stay outside the candidate and every model-visible context fragment.
	input, _ := json.Marshal(candidate)
	asset, e := store.saveProviderBytes(ctx, input, "provider_output")
	if e != nil {
		t.Fatal(e)
	}
	caseID := fmt.Sprintf("linguistic-batch-%02d", batch.Batch)
	qc := QualityCase{ID: caseID, Input: asset.ID, InputSHA: asset.SHA, Basis: "authored_assertion", References: []string{}}
	profileID := p.ID
	plan := QualityExperiment{Scope: "stage", Variants: []QualityVariant{{ID: "included-only", Judge: &profileID}}}
	prompt := "Assess each supplied question independently from its context and realization. Return llm-quality-judge-output JSON, one verdict per input proposition. supported means the exact question's assertion is true; unsupported means false; unknown requires genuinely missing evidence. Never infer actual heard audio from text, IPA intentions, punctuation or a provider receipt. In a stipulated phonetic/timing description assess that symbolic contrast against the stated target, without claiming it happened in audio. Ordinary contextual English admits different varieties, registers, senses, collocations, allophones, connected speech and successful repairs. Explicit drill conformance is local to that task. Do not treat one preferred form or accent as universal. Inspect all/always claims with counterexamples. Provide a contextual reason and evidence locator for every verdict. Do not guess missing audio. No expected labels or reference answer are supplied."
	rubric := "The candidate has independent keyed items. Each contains a context, realization, modality and question. Judge only that question, not whether the supplied text is a well-formed review record. For an assertion_truth item judge the entire quoted assertion. For a stipulated realization, accept its stated facts for a hypothetical target-conformance judgment, without treating them as an observation of our generated WAV. No clinical diagnosis or universal native-accent norm. Preserve ambiguity rather than silently choosing a favorable hidden interpretation."
	frozen := qualityFrozen{Inputs: map[string]json.RawMessage{caseID: input}, Expected: map[string]json.RawMessage{}, Variants: map[string]qualityBinding{"included-only": {Configuration: config, Bundle: lab.Shipped()}}, Judge: map[string]any{"prompt_text": prompt, "rubric_text": rubric}}
	frozen.Expected[caseID], _ = json.Marshal(map[string]any{"semantic_propositions": propositions})
	save("withheld-expectations.json", expected)
	save("candidate-input.json", candidate)
	save("policy.json", map[string]any{"prompt": prompt, "rubric": rubric, "profile": p, "bundle": frozen.Variants["included-only"].Bundle})
	judgment, result, err := s.qualityJudge(ctx, plan, frozen, qc, experiment.Row{Variant: "included-only"}, map[string]any{"candidate_output": candidate}, uuid.NewString(), nil)
	save("native-result.json", map[string]any{"judgment": judgment, "result": result, "error": fmt.Sprint(err)})
	if len(result.ReceiptIDs) > 0 {
		var diagnostic bytes.Buffer
		command, _ := json.Marshal(map[string]any{"action": "diagnostic-read", "id": result.OperationID})
		if de := store.LabCommand(ctx, bytes.NewReader(command), &diagnostic); de == nil {
			if de = os.WriteFile(filepath.Join(outdir, "native-diagnostic.json"), diagnostic.Bytes(), 0600); de != nil {
				t.Error(de)
			}
		} else {
			t.Error("actual native diagnostic readback", de)
		}
	}
	if err != nil {
		t.Fatal("Actual model call/admission failed; no paid fallback", err)
	}
	observed := map[string]string{}
	for _, value := range judgment["verdicts"].([]any) {
		v := value.(map[string]any)
		observed[v["proposition_id"].(string)] = v["verdict"].(string)
	}
	for _, row := range batch.Cases {
		t.Run(row.ID, func(t *testing.T) {
			if observed[row.ID] != expected[row.ID] {
				t.Fatalf("actual semantic judgment %q, independently expected %q", observed[row.ID], expected[row.ID])
			}
		})
	}
	save("observed-labels.json", observed)
}
