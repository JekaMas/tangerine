package lab

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"tangerine.local/api/internal/contracts"
	"testing"
	"time"
)

func bundle() Bundle { return Builtins(time.Date(2026, 10, 10, 12, 0, 0, 0, time.UTC)) }
func must(t *testing.T, e error) {
	t.Helper()
	if e != nil {
		t.Fatal(e)
	}
}
func no(t *testing.T, e error) {
	t.Helper()
	if e == nil {
		t.Fatal("expected rejection")
	}
}
func input() map[string]any {
	return map[string]any{"schema_version": "2.0.0", "answer_text": "The first speaker said ‘He go’. {{answer_text}}", "answer_sha256": contracts.Digest([]byte("The first speaker said ‘He go’. {{answer_text}}")), "task_components": map[string]any{"detection": true, "classification": true, "correction": true, "explanation": false}, "requested_language": "en"}
}
func components() map[string]any {
	return map[string]any{"taxonomy": []string{"G01"}, "public_context": "Two friends", "answer": input()["answer_text"]}
}
func join() Join {
	return Join{Dispatches: []Dispatch{{"d1", "mapping", "request1"}}, Native: []Observation{{ID: "n1", Dispatch: "d1", Surface: "mapping", RequestSHA: "request1", Receipt: "r1", Outcome: "complete"}}, Exports: []Export{{"n1", "request1", "r1", "run1", "native/n1.json", true}}, RequiredSurfaces: []string{"mapping"}, Properties: []string{"P1"}, Cases: []string{"C1"}}
}
func complete(t *testing.T, j Join) {
	t.Helper()
	c := Reconcile(j)
	if c.Status != "observed" {
		t.Fatal(c)
	}
}
func incomplete(t *testing.T, j Join) {
	t.Helper()
	if Reconcile(j).Status != "incomplete" {
		t.Fatal("false evidence completeness")
	}
}
func TestLabBundleCompletePositive(t *testing.T) {
	b := bundle()
	must(t, ValidateBundle(b))
	if len(b.Bindings) != 9 || b.SHA == "" {
		t.Fatal(b)
	}
}
func TestLabBundleUnicodePositive(t *testing.T) {
	b := bundle()
	b.Origin = "local_import"
	b.Bindings[4].Template = "Café café 🟠"
	b.Bindings[4].PromptSHA = contracts.Digest([]byte(b.Bindings[4].Template))
	b.Seal()
	must(t, ValidateBundle(b))
	raw, _ := Canonical(b)
	if !bytes.Contains(raw, []byte("Café café 🟠")) {
		t.Fatal("Unicode altered")
	}
}
func TestLabBundleMissingNegative(t *testing.T) {
	b := bundle()
	b.Bindings = b.Bindings[:8]
	b.Seal()
	no(t, ValidateBundle(b))
	b = bundle()
	b.Bindings[1] = b.Bindings[0]
	b.Seal()
	no(t, ValidateBundle(b))
}
func TestLabBundleHashNegative(t *testing.T) {
	b := bundle()
	b.Bindings[4].Template += "hidden"
	b.Seal()
	no(t, ValidateBundle(b))
	b = bundle()
	b.Bindings[4].InputSHA = strings.Repeat("0", 64)
	b.Seal()
	no(t, ValidateBundle(b))
}
func registry() Bundle {
	b := bundle()
	b.Origin = "registry_export"
	for i := range b.Bindings {
		v := &b.Bindings[i]
		name := "tangerine-" + v.PromptID
		context := "tangerine-context-" + v.PromptID
		n := 1
		v.RegistryName = &name
		v.ContextName = &context
		v.RegistryVersion = &n
		v.ContextVersion = &n
	}
	b.Seal()
	return b
}
func TestLabRegistryNumericPositive(t *testing.T) { must(t, ValidateBundle(registry())) }
func TestLabRegistryFreezePositive(t *testing.T) {
	b := registry()
	before := Hash(b)
	other := registry()
	two := 2
	other.Bindings[0].RegistryVersion = &two
	other.Seal()
	if b.SHA == other.SHA || Hash(b) != before {
		t.Fatal("alias changed frozen binding")
	}
}
func TestLabRegistryMissingNegative(t *testing.T) {
	b := registry()
	b.Bindings[0].RegistryVersion = nil
	b.Seal()
	no(t, ValidateBundle(b))
}
func TestLabRegistryBuiltinMismatchNegative(t *testing.T) {
	b := bundle()
	n := 1
	b.Bindings[0].RegistryVersion = &n
	b.Seal()
	no(t, ValidateBundle(b))
	b = registry()
	bad := "foreign"
	b.Bindings[0].RegistryName = &bad
	b.Seal()
	no(t, ValidateBundle(b))
}
func TestLabTemplateLiteralPositive(t *testing.T) {
	v, e := RenderTemplate("Describe {{answer_text}}", []string{"answer_text"}, input())
	must(t, e)
	if v != "Describe \"The first speaker said ‘He go’. {{answer_text}}\"" {
		t.Fatal(v)
	}
}
func TestLabTemplateNonRecursivePositive(t *testing.T) {
	v, e := RenderTemplate("{{a}} {{b}}", []string{"a", "b"}, map[string]any{"a": "{{b}}", "b": "safe"})
	must(t, e)
	if v != "\"{{b}}\" \"safe\"" {
		t.Fatal(v)
	}
}
func TestLabTemplateMissingNegative(t *testing.T) {
	_, e := RenderTemplate("{{missing}}", []string{"missing"}, input())
	no(t, e)
}
func TestLabTemplateEnvironmentNegative(t *testing.T) {
	_, e := RenderTemplate("{{API_KEY}}", nil, input())
	no(t, e)
	_, e = RenderTemplate("{{a}}", []string{"a", "a"}, map[string]any{"a": 1})
	no(t, e)
}
func TestLabContextCompletePositive(t *testing.T) {
	p, e := Prepare(bundle(), "blind_claim_extraction", nil, input(), components(), 100000, 1000)
	must(t, e)
	if p.WireSHA != contracts.Digest(p.Wire) || !bytes.Contains(p.Wire, []byte("task_components")) || !bytes.Contains(p.Wire, []byte("{{answer_text}}")) {
		t.Fatal(p)
	}
}
func TestLabContextOptionalPositive(t *testing.T) {
	c := components()
	delete(c, "public_context")
	p, e := Prepare(bundle(), "blind_claim_extraction", nil, input(), c, 100000, 1000)
	must(t, e)
	if p.Omitted["public_context"] == "" {
		t.Fatal("omission hidden")
	}
}
func TestLabContextLeakNegative(t *testing.T) {
	b := bundle()
	b.Origin = "local_import"
	b.Bindings[3].Policy.Order = append(b.Bindings[3].Policy.Order, "mutation_key")
	b.Bindings[3].PolicySHA = Hash(b.Bindings[3].Policy)
	b.Seal()
	no(t, ValidateBundle(b))
	c := components()
	c["mutation_key"] = "hidden"
	_, e := Prepare(bundle(), "blind_claim_extraction", nil, input(), c, 100000, 1000)
	no(t, e)
}
func TestLabContextBudgetNegative(t *testing.T) {
	c := components()
	c["answer"] = "different answer"
	_, mismatch := Prepare(bundle(), "blind_claim_extraction", nil, input(), c, 100000, 1000)
	no(t, mismatch)
	p, e := Prepare(bundle(), "blind_claim_extraction", nil, input(), components(), 100, 50)
	no(t, e)
	if p.Wire == nil || p.BudgetUsed < 100 {
		t.Fatal("required input not retained")
	}
}
func TestLabPrivacyCapturePositive(t *testing.T) {
	raw := []byte(`{"answer":"ordinary answer","Authorization":"CANARY","url":"https://api.example/?key=CANARY&mode=safe","personal_metadata":{"name":"private"}}`)
	r, e := Sanitize(raw, []string{"CANARY"}, true)
	must(t, e)
	if !bytes.Contains(r.Bytes, []byte("ordinary answer")) || bytes.Contains(r.Bytes, []byte("CANARY")) || bytes.Contains(r.Bytes, []byte("private")) || r.SHA == r.OriginalSHA {
		t.Fatal(r)
	}
	if !bytes.Contains(raw, []byte("CANARY")) {
		t.Fatal("native input changed")
	}
}
func TestLabPrivacyDisabledPositive(t *testing.T) {
	r, e := Sanitize([]byte(`{"answer":"private"}`), nil, false)
	must(t, e)
	if bytes.Contains(r.Bytes, []byte("private")) || len(r.Reasons) != 1 {
		t.Fatal(r)
	}
}
func TestLabPrivacyCanaryNegative(t *testing.T) {
	headers, err := Sanitize([]byte(`{"X-API-KEY":"undeclared-key","access_token":"oauth-value","refresh_token":"refresh-value","api_key_CANARY":"value","CANARY_field":"value"}`), []string{"CANARY"}, true)
	must(t, err)
	encoded, _ := json.Marshal(headers)
	if bytes.Contains(encoded, []byte("CANARY")) {
		t.Fatal("credential leaked through metadata")
	}
	if string(headers.Bytes) != "{}" {
		t.Fatal("credential fields exported", string(headers.Bytes))
	}
	r, e := Sanitize([]byte(`{"response":"secret-value","url":"https://user:pass@local/?token=OTHER"}`), []string{"secret-value"}, true)
	must(t, e)
	if strings.Contains(string(r.Bytes), "secret-value") || strings.Contains(string(r.Bytes), "pass") || strings.Contains(string(r.Bytes), "OTHER") {
		t.Fatal("secret escaped")
	}
}
func TestLabPrivacyMalformedNegative(t *testing.T) {
	_, duplicate := Sanitize([]byte(`{"answer":"one","answer":"two"}`), nil, true)
	no(t, duplicate)
	_, e := Sanitize([]byte(`{"answer":`), nil, true)
	no(t, e)
}
func contextBinding() []byte {
	h := strings.Repeat("a", 64)
	b := map[string]any{"schema_version": "2.0.0", "id": "fixture-binding", "stage": "blind_claim_extraction", "phase": nil, "provider": "constructed", "model": "no-model-call", "endpoint": "https://example.invalid/fixture", "reasoning_effort": nil, "temperature": nil, "max_output_tokens": 1000, "context_budget_tokens": 32000, "prompt_id": "extract-v1", "prompt_sha256": h, "input_schema_sha256": h, "output_schema_sha256": h, "wire_schema_sha256": h, "adapter_version": "constructed-v1", "credential_ref": "unused-fixture", "store": false, "stream": true, "tools": []any{}, "timeout_seconds": 120}
	hashable := map[string]any{}
	for k, v := range b {
		if k != "id" {
			hashable[k] = v
		}
	}
	b["binding_sha256"] = Hash(hashable)
	raw, _ := Canonical(b)
	return raw
}
func TestLabJoinMatchedPositive(t *testing.T) {
	must(t, ValidateContextBinding(contextBinding(), "blind_claim_extraction", nil))
	id := "saved-context"
	if !ContextAvailable("llm", &id) || !ContextAvailable("tts", nil) {
		t.Fatal("actual modality context rejected")
	}
	phase := "canonical_text"
	if !MatchContextPhase("case_generation", &phase, "case_generation", &phase, "case_generation", &phase) {
		t.Fatal("matching generation phase rejected")
	}
	w := Witness{"op", "mapping", "binding", "input", "wire", "receipt"}
	if !MatchWitness(w, w) {
		t.Fatal("matching native correspondence rejected")
	}
	complete(t, join())
	c := Reconcile(join())
	if c.Ratio == nil || *c.Ratio != "1/1" {
		t.Fatal(c)
	}
}
func TestLabJoinFailedCallPositive(t *testing.T) {
	prepared := join()
	prepared.Native = append(prepared.Native, Observation{ID: "prepared", Surface: "mapping", RequestSHA: "saved-input", Receipt: "prepared-receipt", Outcome: "preparation_failed"})
	prepared.Exports = append(prepared.Exports, Export{"prepared", "saved-input", "prepared-receipt", "run1", "native/prepared.json", true})
	complete(t, prepared)
	if Reconcile(prepared).Observed != 1 {
		t.Fatal("invented dispatch for preparation failure")
	}

	j := join()
	j.Native[0].Outcome = "transport_error"
	complete(t, j)
}
func TestLabJoinOrphanNegative(t *testing.T) {
	duplicate := join()
	duplicate.Native = append(duplicate.Native, Observation{ID: "n2", Dispatch: "d1", Surface: "mapping", RequestSHA: "request1", Receipt: "r1", Outcome: "complete"})
	duplicate.Exports = append(duplicate.Exports, Export{"n2", "request1", "r1", "run1", "native/n2.json", true})
	counted := Reconcile(duplicate)
	if counted.Status != "incomplete" || counted.Matched != 0 || counted.Observed != 1 || counted.Ratio == nil || *counted.Ratio != "0/1" {
		t.Fatal("duplicate dispatch inflated coverage", counted)
	}

	wrong := join()
	wrong.Native[0].Outcome = "preparation_failed"
	incomplete(t, wrong)

	j := join()
	j.Dispatches = append(j.Dispatches, Dispatch{"d2", "mapping", "request2"})
	incomplete(t, j)
}
func TestLabJoinChangedWireNegative(t *testing.T) {
	no(t, ValidateContextBinding(contextBinding(), "feedback", nil))
	var tampered map[string]any
	must(t, json.Unmarshal(contextBinding(), &tampered))
	tampered["model"] = "changed-after-freeze"
	raw, _ := Canonical(tampered)
	no(t, ValidateContextBinding(raw, "blind_claim_extraction", nil))

	if ContextAvailable("llm", nil) || ContextAvailable("judge", nil) {
		t.Fatal("missing required context accepted")
	}
	canonical, mutation := "canonical_text", "mutation"
	if MatchContextPhase("case_generation", &canonical, "case_generation", &mutation, "case_generation", &canonical) || MatchContextPhase("case_generation", &canonical, "case_generation", &canonical, "case_generation", nil) {
		t.Fatal("wrong or absent generation phase accepted")
	}
	w := Witness{"op", "mapping", "binding", "input", "wire", "receipt"}
	wrong := w
	wrong.Binding = "different"
	if MatchWitness(w, wrong) || MatchWitness(Witness{}, Witness{}) {
		t.Fatal("unsupported witness correspondence")
	}
	j := join()
	j.Native[0].RequestSHA = "changed"
	incomplete(t, j)
	j = join()
	j.Exports[0].Receipt = "other"
	incomplete(t, j)
}
func TestLabCacheReferencePositive(t *testing.T) {
	j := join()
	j.Native = append(j.Native, Observation{ID: "cache", Cache: true, Original: "n1", Receipt: "r1"})
	complete(t, j)
	if Reconcile(j).Observed != 1 {
		t.Fatal("invented dispatch")
	}
}
func TestLabZeroCallArtifactPositive(t *testing.T) {
	j := Join{Properties: []string{"P"}, Cases: []string{"C"}, ZeroReason: "deterministic Lab tooling only", DeterministicArtifact: &Export{Run: "actualrun", Artifact: "native/cases.json", Verified: true}}
	complete(t, j)
	if Reconcile(j).Ratio != nil {
		t.Fatal("zero denominator must be N/A")
	}
}
func TestLabCacheInvalidNegative(t *testing.T) {
	empty := join()
	empty.Native = append(empty.Native, Observation{ID: "cache", Cache: true, Original: "missing"})
	incomplete(t, empty)
	j := join()
	j.Native = append(j.Native, Observation{ID: "cache", Cache: true, Original: "missing", Receipt: "r1"})
	incomplete(t, j)
}
func TestLabZeroFalseCoverageNegative(t *testing.T) {
	j := Join{Properties: []string{"P"}, Cases: []string{"C"}, RequiredSurfaces: []string{"mapping"}, ZeroReason: "nothing executed"}
	incomplete(t, j)
}
func TestLabPopulationOrderPositive(t *testing.T) {
	r, e := PlannedRows([]string{"a", "b"}, []string{"base", "candidate"}, 2)
	must(t, e)
	want := []Row{{"a", "base", 1, "not_run"}, {"a", "base", 2, "not_run"}, {"a", "candidate", 1, "not_run"}, {"a", "candidate", 2, "not_run"}, {"b", "base", 1, "not_run"}, {"b", "base", 2, "not_run"}, {"b", "candidate", 1, "not_run"}, {"b", "candidate", 2, "not_run"}}
	if Hash(r) != Hash(want) {
		t.Fatal(r)
	}
}
func TestLabPopulationNoExclusionPositive(t *testing.T) {
	r, e := PlannedRows([]string{"a", "b"}, []string{"base", "candidate"}, 1)
	must(t, e)
	r[0].Status = "failed"
	r[1].Status = "cancelled"
	if len(r) != 4 || r[2].Status != "not_run" || r[3].Status != "not_run" {
		t.Fatal("population changed")
	}
}
func TestLabPopulationDuplicateNegative(t *testing.T) {
	_, e := PlannedRows([]string{"a", "a"}, []string{"base"}, 1)
	no(t, e)
}
func TestLabPopulationEmptyNegative(t *testing.T) {
	_, e := PlannedRows(nil, []string{"base"}, 1)
	no(t, e)
	_, e = PlannedRows([]string{"a"}, []string{"base"}, 0)
	no(t, e)
}
func TestLabExportSuccessPositive(t *testing.T) {
	calls := 0
	s := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		if r.Header.Get("x-mlflow-experiment-id") != "7" || r.Header.Get("Content-Type") != "application/x-protobuf" {
			t.Error("protocol mismatch")
		}
		w.WriteHeader(200)
	}))
	defer s.Close()
	status, e := ExportJSON(context.Background(), s.Client(), s.URL, []byte("actual protobuf"), "7", 5*time.Second)
	must(t, e)
	if status != "exported" || calls != 1 {
		t.Fatal(status, calls)
	}
}
func TestLabExportRetryExplicitPositive(t *testing.T) {
	calls := 0
	s := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		if calls == 1 {
			w.WriteHeader(503)
		} else {
			w.WriteHeader(200)
		}
	}))
	defer s.Close()
	_, e := ExportJSON(context.Background(), s.Client(), s.URL, []byte("saved"), "7", 0)
	no(t, e)
	status, e := ExportJSON(context.Background(), s.Client(), s.URL, []byte("saved"), "7", 0)
	must(t, e)
	if calls != 2 || status != "exported" {
		t.Fatal(calls)
	}
}
func TestLabExportFailureNegative(t *testing.T) {
	calls := 0
	s := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { calls++; w.WriteHeader(503) }))
	defer s.Close()
	status, e := ExportJSON(context.Background(), s.Client(), s.URL, []byte("saved"), "7", 0)
	no(t, e)
	if status != "unexported" || calls != 1 {
		t.Fatal("hidden retries")
	}
}
func TestLabExportReserveNegative(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	status, e := ExportJSON(ctx, http.DefaultClient, "http://127.0.0.1:1", nil, "7", 5*time.Second)
	no(t, e)
	if status != "unexported" {
		t.Fatal(status)
	}
}
func span() TraceSpan {
	return TraceSpan{Trace: strings.Repeat("1", 32), Span: strings.Repeat("2", 16), Name: "mapping", Start: time.Unix(1, 0), End: time.Unix(2, 0), Attributes: map[string]string{"stage": "claim_mapping", "receipt_id": "r1"}}
}
func TestLabTraceActualPositive(t *testing.T) {
	b, e := OTLP(span())
	must(t, e)
	if !bytes.Contains(b, []byte("claim_mapping")) || !bytes.Contains(b, []byte("receipt_id")) {
		t.Fatal("lost attributes")
	}
}
func TestLabTraceParentPositive(t *testing.T) {
	s := span()
	s.Parent = strings.Repeat("3", 16)
	s.Error = true
	b, e := OTLP(s)
	must(t, e)
	if !bytes.Contains(b, bytes.Repeat([]byte{0x33}, 8)) {
		t.Fatal("lost parent")
	}
}
func TestLabTraceSecretNegative(t *testing.T) {
	s := span()
	s.Attributes["Authorization"] = "secret"
	_, e := OTLP(s)
	no(t, e)
}
func TestLabTraceIdentityNegative(t *testing.T) {
	s := span()
	s.Trace = "bad"
	_, e := OTLP(s)
	no(t, e)
	s = span()
	s.End = s.Start.Add(-time.Second)
	_, e = OTLP(s)
	no(t, e)
}
func TestLabCommandBuiltinsPositive(t *testing.T) {
	var out bytes.Buffer
	must(t, Command(strings.NewReader(`{"action":"builtins"}`), &out))
	var b Bundle
	must(t, json.Unmarshal(out.Bytes(), &b))
	must(t, ValidateBundle(b))
}
func TestLabCommandPlanPositive(t *testing.T) {
	var out bytes.Buffer
	must(t, Command(strings.NewReader(`{"action":"plan","cases":["a"],"variants":["b"],"repetitions":1}`), &out))
	if !strings.Contains(out.String(), `"status":"not_run"`) {
		t.Fatal(out.String())
	}
}
func TestLabCommandExtraNegative(t *testing.T) {
	var out bytes.Buffer
	no(t, Command(strings.NewReader(`{"action":"builtins","unknown":true}`), &out))
	if out.Len() != 0 {
		t.Fatal("partial result")
	}
}
func TestLabCommandTrailingNegative(t *testing.T) {
	for _, raw := range []string{`{"action":"plan","action":"builtins"}`, `{"action":"sanitize","capture":false,"capture":true}`} {
		var out bytes.Buffer
		no(t, Command(strings.NewReader(raw), &out))
		if out.Len() != 0 {
			t.Fatal("ambiguous command emitted a result")
		}
	}

	var out bytes.Buffer
	no(t, Command(strings.NewReader(`{"action":"builtins"} {}`), &out))
	if out.Len() != 0 {
		t.Fatal("partial result")
	}
}
func inventory(dependency string) map[string]any {
	return map[string]any{"schema_version": "2.0.0", "id": "inventory", "source_revision": "constructed fixture", "dependencies": []any{map[string]any{"path": "owner.go", "sha256": dependency, "purpose": "test owner"}}, "entries": []any{map[string]any{"id": "planned", "stage": "mapping", "phase": nil, "kind": "llm", "implementation_state": "planned", "owner_paths": []string{"services/api"}, "owner_symbols": []string{}, "adapter_paths": []string{}, "trusted_fragments": []any{}, "discovery_evidence_refs": []string{"literal fixture"}, "coverage_reason": "later provider iteration"}}, "non_ai_calls": []any{}, "unresolved_paths": []string{}}
}
func sealed(m map[string]any, key string) []byte {
	delete(m, key)
	m[key] = Hash(m)
	b, _ := Canonical(m)
	return b
}
func TestLabInventoryPlannedPositive(t *testing.T) {
	h := strings.Repeat("a", 64)
	must(t, ValidateInventory(sealed(inventory(h), "inventory_sha256"), map[string]string{"owner.go": h}))
}
func TestLabInventorySourcePositive(t *testing.T) {
	if !MatchDependencies([]Dependency{{"a", "one"}, {"b", "two"}}, []Dependency{{"b", "two"}, {"a", "one"}}) {
		t.Fatal("dependency order altered identity")
	}
	h := contracts.Digest([]byte("actual owner"))
	must(t, ValidateInventory(sealed(inventory(h), "inventory_sha256"), map[string]string{"owner.go": h}))
}
func TestLabInventoryDriftNegative(t *testing.T) {
	for _, claim := range [][]Dependency{{{"a", "wrong"}}, {{"a", "one"}, {"a", "wrong"}}, {{"b", "one"}}} {
		if MatchDependencies([]Dependency{{"a", "one"}}, claim) {
			t.Fatal("changed dependency accepted")
		}
	}
	h := strings.Repeat("a", 64)
	no(t, ValidateInventory(sealed(inventory(h), "inventory_sha256"), map[string]string{"owner.go": strings.Repeat("b", 64)}))
}
func TestLabInventoryUnresolvedNegative(t *testing.T) {
	h := strings.Repeat("a", 64)
	x := inventory(h)
	x["unresolved_paths"] = []string{"hidden_helper.go"}
	no(t, ValidateInventory(sealed(x, "inventory_sha256"), map[string]string{"owner.go": h}))
}
func TestLabConfigurationDefault(t *testing.T) {
	raw := []byte(`{"schema_version":"2.0.0","workspace_id":"local","llm_profile":"chatgpt-plan-responses-v1","feedback_language":"en","intended_uses":["local_analysis","derivative_exercises"],"credential_refs":{"deepseek":null,"openai":null,"azure":null},"azure_region":null,"connectors":[],"limits":{"daily_micro_usd":null,"monthly_micro_usd":null,"concurrent_paid_operations":1,"archive_bytes":"34359738368","expanded_bytes":"137438953472","archive_members":250000,"member_bytes":"34359738368"},"llm_profiles":[{"id":"chatgpt-plan-responses-v1","provider":"openai_chatgpt","model":"unselected","endpoint":"https://api.openai.com/v1/responses","reasoning_effort":null,"temperature":null,"max_output_tokens":null,"context_budget_tokens":128000,"adapter_version":"chatgpt-plan-responses-v1","credential_ref":"chatgpt_plan_oauth","store":false,"stream":true,"tools":[],"roles":["case_generation","linguistic_audit","blind_claim_extraction","claim_mapping","mapping_audit","feedback","case_review","adjudication"],"auth_method":"chatgpt_plan_oauth","billing_mode":"included_subscription"}],"stage_profiles":{"case_generation":null,"linguistic_audit":null,"blind_claim_extraction":null,"claim_mapping":null,"mapping_audit":null,"feedback":null,"case_review":null,"adjudication":null},"mapping_audit_enabled":false,"llm_lab_trace_enabled":false,"llm_lab_capture_content":false}`)
	var v map[string]any
	must(t, json.Unmarshal(raw, &v))
	v["configuration_sha256"] = Hash(v)
	raw, _ = Canonical(v)
	_, _, e := contracts.Validate("configuration", "2.0.0", raw)
	must(t, e)
}
func dataset() map[string]any {
	h := strings.Repeat("a", 64)
	c := map[string]any{"schema_version": "2.0.0", "id": "case1", "stage": "blind_claim_extraction", "phase": nil, "polarity": "positive", "origin": "constructed", "expectation_basis": "authored_assertion", "group_id": "group1", "split": "development", "taxonomy_ids": []string{"G01"}, "input_asset_id": "input1", "input_sha256": h, "expectations_asset_id": "expected1", "expectations_sha256": h, "reference_receipt_ids": []string{}}
	return map[string]any{"schema_version": "2.0.0", "scope": "stage", "stage": "blind_claim_extraction", "phase": nil, "cases": []any{c}}
}
func TestLabDatasetFrozenPositive(t *testing.T) {
	must(t, ValidateCaseResults([]byte(`{"cases":[{"case_id":"c1","property_id":"p1","status":"passed"},{"case_id":"c2","property_id":"p1","status":"failed"}]}`), []string{"p1"}, []string{"c1", "c2"}))
	must(t, ValidateDataset(sealed(dataset(), "dataset_sha256")))
}
func TestLabDatasetOriginPositive(t *testing.T) {
	d := dataset()
	d["cases"].([]any)[0].(map[string]any)["polarity"] = "negative"
	must(t, ValidateDataset(sealed(d, "dataset_sha256")))
}
func TestLabDatasetDuplicateNegative(t *testing.T) {
	for _, raw := range []string{`{"cases":[]}`, `{"cases":[{"case_id":"c1","property_id":"p1","status":"not_run"}]}`, `{"cases":[{"case_id":"c1","property_id":"p2","status":"passed"}]}`, `{"cases":[{"case_id":"c1","property_id":"p1","status":"passed"},{"case_id":"c1","property_id":"p1","status":"passed"}]}`} {
		no(t, ValidateCaseResults([]byte(raw), []string{"p1"}, []string{"c1"}))
	}
	d := dataset()
	d["cases"] = []any{d["cases"].([]any)[0], d["cases"].([]any)[0]}
	no(t, ValidateDataset(sealed(d, "dataset_sha256")))
}
func TestLabDatasetStageNegative(t *testing.T) {
	d := dataset()
	d["stage"] = "feedback"
	no(t, ValidateDataset(sealed(d, "dataset_sha256")))
}

func TestLabTraceDevelopmentPositive(t *testing.T) {
	s := span()
	s.Attributes["tangerine.development_run_id"] = "77777777-7777-4777-8777-777777777777"
	b, e := OTLP(s)
	must(t, e)
	if !bytes.Contains(b, []byte("tangerine.development_run_id")) || !bytes.Contains(b, []byte("77777777-7777-4777-8777-777777777777")) {
		t.Fatal("development correspondence was dropped")
	}
}
func TestLabTraceDevelopmentSecretNegative(t *testing.T) {
	s := span()
	s.Attributes["tangerine.development_run_id"] = "77777777-7777-4777-8777-777777777777"
	s.Attributes["Authorization"] = "private-canary"
	b, e := OTLP(s)
	if e == nil || len(b) != 0 {
		t.Fatal("secret attribute bypassed single trace admission")
	}
}
