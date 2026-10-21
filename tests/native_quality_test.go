package app

// Constructed model replies test native orchestration/storage, not model quality.
import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"os"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/empirical"
	"tangerine.local/api/internal/lab"
	"testing"
	"time"
)

func qualitySubmission(t *testing.T, f *nativeInterpretation, cases, variants, repetitions int) QualitySubmission {
	t.Helper()
	ctx := context.Background()
	configuration, _, e := f.s.Store.Configuration(ctx)
	requireListening(t, e)
	bundle, e := f.s.Store.ActiveLabBundle(ctx)
	requireListening(t, e)
	record, e := f.s.Store.Attempt(ctx, f.attempt)
	requireListening(t, e)
	resources, e := f.s.Store.interpretationResources(ctx, record)
	requireListening(t, e)
	input, _ := interpretationInput(record, resources, nil)
	assets := map[string]json.RawMessage{"bundle": mustJSON(bundle)}
	dataset := QualityDataset{Version: "2.0.0", Scope: "stage", Stage: ptrQuality("blind_claim_extraction"), Cases: []QualityCase{}}
	expected := map[string]any{"schema_version": "1.0.0", "expected_mapping": nil, "expected_metric_values": []any{}, "expected_canonical_sha256": nil, "semantic_propositions": []any{}}
	for i := 0; i < cases; i++ {
		id := fmt.Sprint("case-", i)
		in, ex := mustJSON(input), mustJSON(expected)
		assets[id+"-input"] = in
		assets[id+"-expected"] = ex
		dataset.Cases = append(dataset.Cases, QualityCase{Version: "2.0.0", ID: id, Stage: "blind_claim_extraction", Polarity: []string{"positive", "negative"}[i%2], Origin: "constructed", Basis: "authored_assertion", Group: id, Split: "development", Taxonomy: []string{"grammar.verbs.subject_verb_agreement"}, Input: id + "-input", InputSHA: contracts.Digest(in), Expectations: id + "-expected", ExpectationsSHA: contracts.Digest(ex), References: []string{}})
	}
	var ds map[string]any
	_ = json.Unmarshal(mustJSON(dataset), &ds)
	delete(ds, "dataset_sha256")
	dataset.SHA = lab.Hash(ds)
	assets["dataset"] = mustJSON(dataset)
	plan := QualityExperiment{ID: uuid.NewString(), Scope: "stage", Dataset: "dataset", DatasetSHA: dataset.SHA, Scorer: "quality-v1", Variants: []QualityVariant{}, Repetitions: repetitions}
	for i := 0; i < variants; i++ {
		var c map[string]any
		_ = json.Unmarshal(mustJSON(configuration), &c)
		c["llm_profiles"].([]any)[0].(map[string]any)["temperature"] = float64(i) / 10
		delete(c, "configuration_sha256")
		c["configuration_sha256"] = lab.Hash(c)
		raw := mustJSON(c)
		name := fmt.Sprint("config-", i)
		assets[name] = raw
		plan.Variants = append(plan.Variants, QualityVariant{ID: fmt.Sprint("variant-", i), BundleID: "bundle", BundleSHA: bundle.SHA, Profile: configuration["llm_profile"].(string), Config: name, ConfigSHA: contracts.Digest(raw)})
	}
	return QualitySubmission{Experiment: plan, Assets: assets}
}
func ptrQuality(s string) *string { return &s }
func admitQuality(t *testing.T, f *nativeInterpretation, c, v, n int) QualityExperiment {
	t.Helper()
	p, e := f.s.Store.AdmitExperiment(context.Background(), qualitySubmission(t, f, c, v, n))
	requireListening(t, e)
	return p
}
func TestNativeQualityFrozenPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	p := admitQuality(t, f, 2, 2, 2)
	if len(p.Rows) != 8 {
		t.Fatal(p)
	}
	before, _, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	p, e = f.s.RunQualityExperiment(context.Background(), p.ID, false, f.model.Client())
	requireListening(t, e)
	if p.Status != "completed" || f.calls.Load() != 8 {
		t.Fatal(p.Status, f.calls.Load())
	}
	for _, r := range p.Rows {
		if r.Status != "complete" || len(r.Receipts) != 1 || r.Output == nil || len(r.Metrics) != 22 {
			t.Fatal(r)
		}
	}
	after, _, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	if lab.Hash(before) != lab.Hash(after) {
		t.Fatal("experiment changed Settings")
	}
	if len(p.Aggregates) != 44 || p.Comparison == nil {
		t.Fatal(p)
	}
	p, e = f.s.RunQualityExperiment(context.Background(), p.ID, false, f.model.Client())
	requireListening(t, e)
	if f.calls.Load() != 8 {
		t.Fatal("read/replay dispatched")
	}
	_ = os.WriteFile("/evidence/quality-positive.json", mustJSON(p), 0600)
}
func TestNativeQualityFailureNegative(t *testing.T) {
	f := interpretationNative(t, "bad-extraction")
	p := admitQuality(t, f, 2, 1, 1)
	p, e := f.s.RunQualityExperiment(context.Background(), p.ID, false, f.model.Client())
	requireListening(t, e)
	if p.Status != "partial" || len(p.Rows) != 2 {
		t.Fatal(p)
	}
	for _, r := range p.Rows {
		if r.Status != "failed" || r.Error == nil || r.Output == nil || len(r.Receipts) != 2 {
			t.Fatal(r)
		}
	}
	if p.Aggregates[0].Metric.Numerator == nil || *p.Aggregates[0].Metric.Numerator != "0" || *p.Aggregates[0].Metric.Denominator != "2" {
		t.Fatal(p.Aggregates[0])
	}
}
func TestNativeQualityDigestNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	r := qualitySubmission(t, f, 1, 1, 1)
	r.Experiment.DatasetSHA = fmt.Sprintf("%064d", 0)
	if _, e := f.s.Store.AdmitExperiment(context.Background(), r); e == nil {
		t.Fatal("admitted mismatched dataset")
	}
	if f.calls.Load() != 0 {
		t.Fatal("admission dispatched")
	}
}
func TestNativeQualityPopulationPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	p := admitQuality(t, f, 2, 2, 1)
	packet, e := f.s.Store.QualityDiagnostic(context.Background(), p.ID)
	requireListening(t, e)
	if len(packet["artifacts"].([]any)) != 2 {
		t.Fatal(packet)
	}
	frozen, e := f.s.Store.frozenExperiment(context.Background(), p.ID)
	requireListening(t, e)
	coverage := qualityCoverage(p, frozen.Dataset)
	if len(coverage) != 122 {
		t.Fatal(len(coverage))
	}
	for _, r := range coverage {
		if r["completed_rows"] != 0 {
			t.Fatal("planned became observed")
		}
	}
}
func TestNativeQualityCancellationNegative(t *testing.T) {
	f := interpretationNative(t, "blocked")
	p := admitQuality(t, f, 2, 1, 1)
	done := make(chan QualityExperiment, 1)
	errs := make(chan error, 1)
	go func() {
		r, e := f.s.RunQualityExperiment(context.Background(), p.ID, false, f.model.Client())
		done <- r
		errs <- e
	}()
	select {
	case <-f.entered:
	case <-time.After(15 * time.Second):
		t.Fatal("model not reached")
	}
	e := f.s.Store.CancelQualityExperiment(context.Background(), p.ID)
	requireListening(t, e)
	close(f.release)
	var result QualityExperiment
	select {
	case result = <-done:
	case <-time.After(15 * time.Second):
		t.Fatal("cancel did not finish")
	}
	requireListening(t, <-errs)
	if result.Status != "cancelled" || result.Rows[1].Status != "not_run" {
		t.Fatal(result)
	}
	if f.calls.Load() > 1 {
		t.Fatal("unstarted dispatched", f.calls.Load())
	}
}
func TestNativeQualityResumePositive(t *testing.T) {
	f := interpretationNative(t, "good")
	p := admitQuality(t, f, 2, 1, 1)
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE quality_experiment SET cancel_requested=true,payload=jsonb_set(payload,'{status}','\"cancelled\"') WHERE id=$1", p.ID)
	requireListening(t, e)
	p, e = f.s.RunQualityExperiment(context.Background(), p.ID, true, f.model.Client())
	requireListening(t, e)
	if p.Status != "completed" || f.calls.Load() != 2 {
		t.Fatal(p.Status, f.calls.Load())
	}
	var events int
	e = f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM quality_experiment_event WHERE experiment_id=$1", p.ID).Scan(&events)
	requireListening(t, e)
	if events < 4 {
		t.Fatal("missing durable transitions", events)
	}
}
func TestNativeQualityConcurrentNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	p := admitQuality(t, f, 1, 1, 1)
	owner, e := f.s.Store.claimQualityBatch(context.Background(), p.ID, false)
	requireListening(t, e)
	if _, e = f.s.RunQualityExperiment(context.Background(), p.ID, true, f.model.Client()); e == nil {
		t.Fatal("second batch acquired")
	}
	if f.calls.Load() != 0 {
		t.Fatal("concurrent call dispatched")
	}
	_, e = f.s.Store.DB.Exec(context.Background(), "UPDATE quality_experiment SET lease_until=clock_timestamp()-interval '1 second' WHERE id=$1", p.ID)
	requireListening(t, e)
	newOwner, e := f.s.Store.claimQualityBatch(context.Background(), p.ID, true)
	requireListening(t, e)
	if owner == newOwner {
		t.Fatal("stale owner reused")
	}
	if e = f.s.Store.saveQualityProgress(context.Background(), p, owner, true); e == nil {
		t.Fatal("stale write accepted")
	}
}
func TestNativeEmpiricalStoredPositive(t *testing.T) {
	s := listeningNative(t)
	n := int64(10)
	a := "grammar.verbs.subject_verb_agreement"
	r, e := s.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Constructed source population", Input: empirical.Input{Population: empirical.Population{Release: "constructed-release", View: "one", Window: "sentence", Origin: "authored_assertion"}, Windows: []empirical.Window{{ID: "window", Annotated: true, Tokens: &n, Events: []empirical.Event{{ID: "event", Native: "agreement", Leaf: &a, Secondary: []string{}}}}}}})
	requireListening(t, e)
	report := r["report"].(empirical.Report)
	if len(report.Leaves) != 122 || report.Events != 1 {
		t.Fatal(report)
	}
	read, e := s.EmpiricalReport(context.Background(), r["id"].(string))
	requireListening(t, e)
	if lab.Hash(json.RawMessage(read)) != lab.Hash(r) {
		t.Fatal("changed report read")
	}
	rs, e := s.EmpiricalReports(context.Background())
	requireListening(t, e)
	if len(rs) != 1 {
		t.Fatal(rs)
	}
}
func TestNativeEmpiricalMissingNegative(t *testing.T) {
	s := listeningNative(t)
	r, e := s.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "No observations", Input: empirical.Input{Population: empirical.Population{Release: "missing-original", View: "none", Window: "utterance", Origin: "unknown"}, Windows: []empirical.Window{}}})
	requireListening(t, e)
	report := r["report"].(empirical.Report)
	for _, l := range report.Leaves {
		if l.Prevalence.Exact != nil {
			t.Fatal("invented source coverage", l)
		}
	}
}

func TestNativeQualityStagePositive(t *testing.T) {
	f := interpretationNative(t, "good")
	p := admitQuality(t, f, 1, 1, 1)
	frozen, e := f.s.Store.frozenExperiment(context.Background(), p.ID)
	requireListening(t, e)
	row := p.Rows[0]
	op, e := f.s.Store.qualityRowOperation(context.Background(), p.ID, 0)
	requireListening(t, e)
	ctx := qualityContext(context.Background(), frozen.Variants[row.Variant])
	ctx = context.WithValue(ctx, qualityOperationContextKey{}, op)
	_, result, e := f.s.executeQualityRow(ctx, p, frozen, row, op, f.model.Client())
	if e != nil {
		t.Fatalf("native stage failed before/after %d calls: %T %v", f.calls.Load(), e, e)
	}
	if len(result.ReceiptIDs) != 1 {
		t.Fatal(result)
	}
}
func qualityAnswerSubmission(t *testing.T, f *nativeInterpretation) QualitySubmission {
	r := qualitySubmission(t, f, 1, 1, 1)
	input := map[string]any{"ground_truth": f.key, "answer_asset_id": "answer", "answer_sha256": contracts.Digest([]byte("Use opens.")), "task_components": map[string]any{"detection": true, "classification": true, "correction": true, "explanation": false}}
	record, e := f.s.Store.Attempt(context.Background(), f.attempt)
	requireListening(t, e)
	input["task_components"] = record.Attempt["task_components"]
	document, e := f.s.Store.ReadDocument(context.Background(), f.id)
	requireListening(t, e)
	var published map[string]any
	requireListening(t, json.Unmarshal(document.Payload, &published))
	input["ground_truth"] = published
	asset, e := f.s.Store.saveProviderBytes(context.Background(), []byte("Use opens."), "provider_input")
	requireListening(t, e)
	input["answer_asset_id"] = asset.ID
	var dataset QualityDataset
	_ = json.Unmarshal(r.Assets["dataset"], &dataset)
	dataset.Scope = "answer_pipeline"
	dataset.Stage = nil
	dataset.Cases[0].InputSHA = contracts.Digest(mustJSON(input))
	r.Assets["case-0-input"] = mustJSON(input)
	var ds map[string]any
	_ = json.Unmarshal(mustJSON(dataset), &ds)
	delete(ds, "dataset_sha256")
	dataset.SHA = lab.Hash(ds)
	r.Assets["dataset"] = mustJSON(dataset)
	r.Experiment.Scope = dataset.Scope
	r.Experiment.DatasetSHA = dataset.SHA
	return r
}
func TestNativeQualityAnswerPositive(t *testing.T) {
	f := scoringFixture(t, false)
	r := qualityAnswerSubmission(t, f.nativeInterpretation)
	p, e := f.s.Store.AdmitExperiment(context.Background(), r)
	requireListening(t, e)
	p, e = f.s.RunQualityExperiment(context.Background(), p.ID, false, nil)
	requireListening(t, e)
	if p.Status != "completed" || len(p.Rows[0].Receipts) != 3 {
		t.Fatalf("%s %+v", p.Status, p.Rows[0])
	}
	raw, e := f.s.Store.ReadAsset(context.Background(), *p.Rows[0].Output)
	requireListening(t, e)
	var packet map[string]any
	requireListening(t, json.Unmarshal(raw, &packet))
	score := packet["native_score"].(map[string]any)
	if score["composite"].(map[string]any)["display"] != "100.0" {
		t.Fatal(score)
	}
}
func TestNativeQualityAnswerFailureNegative(t *testing.T) {
	f := scoringFixture(t, true)
	r := qualityAnswerSubmission(t, f.nativeInterpretation)
	p, e := f.s.Store.AdmitExperiment(context.Background(), r)
	requireListening(t, e)
	p, e = f.s.RunQualityExperiment(context.Background(), p.ID, false, nil)
	requireListening(t, e)
	if p.Status != "partial" || p.Rows[0].Status != "failed" || p.Rows[0].Output == nil {
		t.Fatal(p)
	}
	raw, e := f.s.Store.ReadAsset(context.Background(), *p.Rows[0].Output)
	requireListening(t, e)
	var packet map[string]any
	requireListening(t, json.Unmarshal(raw, &packet))
	if packet["native_score"] == nil {
		t.Fatal("lost supported native grade")
	}
}
func TestNativeEmpiricalSourcePositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	value, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Constructed native sentence view", Input: empirical.Input{Population: empirical.Population{Origin: "native", Modality: "writing"}}, Source: &EmpiricalSource{Import: run.Report.ID, Member: "fce/train.m2", Table: "sentences", Annotator: "0"}})
	requireListening(t, e)
	report := value["report"].(empirical.Report)
	if report.SourceAnnotated != 1 || report.MappingIncomplete != 1 || report.Annotated != 0 || report.Unmapped != 1 || len(report.NativeFrequencies) != 1 {
		t.Fatal(report)
	}
	n := report.NativeFrequencies[0]
	if n.ID != "R:VERB:SVA" || n.Events != 1 || n.Prevalence.Exact.Numerator != "1" || n.Prevalence.Exact.Denominator != "1" || n.Density.Exact.Numerator != "1000" || n.Density.Exact.Denominator != "3" {
		t.Fatal(n)
	}
}
func TestNativeEmpiricalMappedPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	event := fmt.Sprintf("%s/fce/train.m2/0/0", run.Report.ID)
	value, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Constructed localized mapping", Input: empirical.Input{Population: empirical.Population{Origin: "native", Crosswalk: "constructed-context-v1", Modality: "writing"}}, Source: &EmpiricalSource{Import: run.Report.ID, Member: "fce/train.m2", Table: "sentences", Annotator: "0", AnnotatedLeaves: []string{"grammar.verbs.subject_verb_agreement"}, LeafByEvent: map[string]string{event: "grammar.verbs.subject_verb_agreement"}}})
	requireListening(t, e)
	report := value["report"].(empirical.Report)
	if report.Annotated != 1 || report.MappingIncomplete != 0 || report.Events != 1 || report.Population.Origin != "operator_localized_mapping" {
		t.Fatal(report)
	}
	for _, l := range report.Leaves {
		if l.ID == "grammar.verbs.subject_verb_agreement" && l.Prevalence.Numerator != "1" {
			t.Fatal(l)
		}
	}
}
func TestNativeEmpiricalAnnotatorNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	value, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Absent selected annotations", Source: &EmpiricalSource{Import: run.Report.ID, Member: "fce/train.m2", Table: "sentences", Annotator: "99"}})
	requireListening(t, e)
	report := value["report"].(empirical.Report)
	if report.Annotated != 0 || report.SourceAnnotated != 0 {
		t.Fatal("absent annotator became annotation", report)
	}
	for _, l := range report.Leaves {
		if l.Prevalence.Exact != nil {
			t.Fatal(l)
		}
	}
}
func TestNativeEmpiricalViewNegative(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	_, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Typo must not become measured empty view", Source: &EmpiricalSource{Import: run.Report.ID, Member: "fce/typo.m2", Table: "sentences", Annotator: "0"}})
	if e == nil {
		t.Fatal("unknown native view accepted")
	}
}

func TestNativeQualityExportPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	ctx := context.Background()
	p := admitQuality(t, f, 1, 1, 1)
	p, e := f.s.RunQualityExperiment(ctx, p.ID, false, f.model.Client())
	requireListening(t, e)
	packet, e := f.s.Store.QualityDiagnostic(ctx, p.ID)
	requireListening(t, e)
	before := lab.Hash(packet)
	calls := f.calls.Load()
	receipt := QualityExportReceipt{Experiment: p.ID, Run: "constructed-sdk-ack", Rows: p.Rows, Artifacts: []json.RawMessage{json.RawMessage(`{"verified":true}`)}}
	requireListening(t, f.s.Store.AcknowledgeQualityExport(ctx, receipt))
	read, e := f.s.Store.QualityExperiment(ctx, p.ID)
	requireListening(t, e)
	if read.Rows[0].Export != "exported" {
		t.Fatal(read.Rows)
	}
	again, e := f.s.Store.QualityDiagnostic(ctx, p.ID)
	requireListening(t, e)
	if lab.Hash(again) != before || f.calls.Load() != calls {
		t.Fatal("export acknowledgment changed immutable packet or dispatched")
	}
}
func TestNativeQualityExportNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	ctx := context.Background()
	p := admitQuality(t, f, 1, 1, 1)
	if e := f.s.Store.AcknowledgeQualityExport(ctx, QualityExportReceipt{Experiment: p.ID, Run: "not-copied", Rows: p.Rows, ProviderCalls: 1, Artifacts: []json.RawMessage{json.RawMessage(`{}`)}}); e == nil {
		t.Fatal("inference receipt accepted as copy-only acknowledgment")
	}
	p, e := f.s.Store.QualityExperiment(ctx, p.ID)
	requireListening(t, e)
	if p.Rows[0].Export == "exported" || f.calls.Load() != 0 {
		t.Fatal(p)
	}
}
func TestNativeEmpiricalDefaultAnnotatorPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	value, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Default native annotation selection", Source: &EmpiricalSource{Import: run.Report.ID, Member: "fce/train.m2", Table: "sentences"}})
	requireListening(t, e)
	r := value["report"].(empirical.Report)
	if r.SourceAnnotated != 1 || r.Unmapped != 1 || r.Population.Annotator != "lowest_integer_per_sentence" {
		t.Fatal(r)
	}
}
func TestNativeQualityTaxonomyNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	r := qualitySubmission(t, f, 1, 1, 1)
	var d QualityDataset
	requireListening(t, json.Unmarshal(r.Assets["dataset"], &d))
	d.Cases[0].Taxonomy = []string{"invented.leaf"}
	var m map[string]any
	requireListening(t, json.Unmarshal(mustJSON(d), &m))
	delete(m, "dataset_sha256")
	d.SHA = lab.Hash(m)
	r.Assets["dataset"] = mustJSON(d)
	r.Experiment.DatasetSHA = d.SHA
	if _, e := f.s.Store.AdmitExperiment(context.Background(), r); e == nil {
		t.Fatal("unknown coverage leaf admitted")
	}
	if f.calls.Load() != 0 {
		t.Fatal("intake dispatched")
	}
}

func TestNativeQualitySettingsPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	ctx := context.Background()
	p := admitQuality(t, f, 1, 1, 1)
	c, rev, e := f.s.Store.Configuration(ctx)
	requireListening(t, e)
	c["llm_profiles"].([]any)[0].(map[string]any)["endpoint"] = "http://127.0.0.1:9/v1/responses"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = f.s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	p, e = f.s.RunQualityExperiment(ctx, p.ID, false, f.model.Client())
	requireListening(t, e)
	if p.Status != "completed" || f.calls.Load() != 1 {
		t.Fatal("resume used current settings", p, f.calls.Load())
	}
}
func TestNativeQualityCheckpointPositive(t *testing.T) {
	f := interpretationNative(t, "good")
	ctx := context.Background()
	p := admitQuality(t, f, 1, 1, 1)
	frozen, e := f.s.Store.frozenExperiment(ctx, p.ID)
	requireListening(t, e)
	operation, e := f.s.Store.qualityRowOperation(ctx, p.ID, 0)
	requireListening(t, e)
	work := qualityContext(ctx, frozen.Variants[p.Rows[0].Variant])
	work = context.WithValue(work, qualityOperationContextKey{}, operation)
	_, _, e = f.s.executeQualityRow(work, p, frozen, p.Rows[0], operation, f.model.Client())
	requireListening(t, e)
	if f.calls.Load() != 1 {
		t.Fatal(f.calls.Load())
	}
	// A stopped controller never saved the row after its native child completed.
	p, e = f.s.RunQualityExperiment(ctx, p.ID, true, f.model.Client())
	requireListening(t, e)
	if p.Status != "completed" || f.calls.Load() != 1 || len(p.Rows[0].Receipts) != 1 {
		t.Fatal("recovery duplicated accepted native call", p, f.calls.Load())
	}
}

func TestNativeQualityReleasePositive(t *testing.T) {
	f := interpretationNative(t, "good")
	ctx := context.Background()
	p := admitQuality(t, f, 1, 1, 1)
	owner, e := f.s.Store.claimQualityBatch(ctx, p.ID, false)
	requireListening(t, e)
	requireListening(t, f.s.Store.releaseQualityBatch(ctx, p.ID, owner))
	next, e := f.s.Store.claimQualityBatch(ctx, p.ID, true)
	requireListening(t, e)
	if next == owner || f.calls.Load() != 0 {
		t.Fatal("release did not allow explicit new ownership", next)
	}
}
func TestNativeQualityStaleReleaseNegative(t *testing.T) {
	f := interpretationNative(t, "good")
	ctx := context.Background()
	p := admitQuality(t, f, 1, 1, 1)
	owner, e := f.s.Store.claimQualityBatch(ctx, p.ID, false)
	requireListening(t, e)
	requireListening(t, f.s.Store.releaseQualityBatch(ctx, p.ID, uuid.NewString()))
	var active string
	requireListening(t, f.s.Store.DB.QueryRow(ctx, "SELECT active_operation_id FROM quality_experiment WHERE id=$1", p.ID).Scan(&active))
	if active != owner || f.calls.Load() != 0 {
		t.Fatal("stale controller released another owner", active)
	}
}
