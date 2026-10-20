// Package lab owns deterministic prompt/context tooling; it never calls a model.
package lab

import (
	"embed"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"regexp"
	"strings"
	"tangerine.local/api/internal/contracts"
	"time"
)

//go:embed builtin.json
var builtin embed.FS

type Policy struct {
	Stage       string   `json:"stage"`
	Phase       *string  `json:"phase"`
	Instruction string   `json:"instruction_template"`
	Order       []string `json:"component_order"`
	Variables   []string `json:"template_variables"`
	Notes       string   `json:"selection_notes"`
}
type Binding struct {
	Stage           string   `json:"stage"`
	Phase           *string  `json:"phase"`
	PromptID        string   `json:"prompt_id"`
	Template        string   `json:"template"`
	Variables       []string `json:"template_variables"`
	PromptSHA       string   `json:"prompt_sha256"`
	RegistryName    *string  `json:"registry_name"`
	RegistryVersion *int     `json:"registry_version"`
	ContextName     *string  `json:"context_registry_name"`
	ContextVersion  *int     `json:"context_registry_version"`
	Policy          Policy   `json:"context_policy"`
	PolicySHA       string   `json:"context_policy_sha256"`
	InputSchema     string   `json:"input_schema"`
	InputSHA        string   `json:"input_schema_sha256"`
	OutputSchema    string   `json:"output_schema"`
	OutputSHA       string   `json:"output_schema_sha256"`
}
type Bundle struct {
	Version  string    `json:"schema_version"`
	ID       string    `json:"id"`
	Origin   string    `json:"origin"`
	Created  string    `json:"created_at"`
	Bindings []Binding `json:"bindings"`
	SHA      string    `json:"bundle_sha256"`
}

func Canonical(v any) ([]byte, error) {
	b, e := json.Marshal(map[string]any{"value": v})
	if e != nil {
		return nil, e
	}
	b, e = contracts.Canonical(b)
	if e != nil {
		return nil, e
	}
	var wrapper map[string]json.RawMessage
	e = json.Unmarshal(b, &wrapper)
	return wrapper["value"], e
}
func Hash(v any) string {
	b, e := Canonical(v)
	if e != nil {
		return ""
	}
	return contracts.Digest(b)
}
func Pair(stage string, phase *string) string {
	if phase != nil {
		return stage + ":" + *phase
	}
	return stage
}
func BuiltinBindings() []Binding {
	b, _ := builtin.ReadFile("builtin.json")
	var rows []Binding
	_ = json.Unmarshal(b, &rows)
	for i := range rows {
		rows[i].PolicySHA = Hash(rows[i].Policy)
	}
	return rows
}
func Builtins(now time.Time) Bundle {
	b := Bundle{"2.0.0", uuid.NewString(), "builtin", now.UTC().Format(time.RFC3339Nano), BuiltinBindings(), ""}
	b.Seal()
	return b
}
func (b *Bundle) Seal() {
	raw, _ := Canonical(b)
	var m map[string]any
	_ = json.Unmarshal(raw, &m)
	delete(m, "bundle_sha256")
	b.SHA = Hash(m)
}
func ValidateBundle(b Bundle) error {
	raw, e := Canonical(b)
	if e != nil {
		return e
	}
	if _, _, e = contracts.Validate("prompt-bundle", "2.0.0", raw); e != nil {
		return e
	}
	if id, e := uuid.Parse(b.ID); e != nil || id.Version() != 4 {
		return errors.New("bundle identity must be UUIDv4")
	}
	if _, e := time.Parse(time.RFC3339Nano, b.Created); e != nil {
		return e
	}
	manifest := map[string]Binding{}
	for _, v := range BuiltinBindings() {
		manifest[Pair(v.Stage, v.Phase)] = v
	}
	if len(b.Bindings) != len(manifest) {
		return errors.New("complete nine-binding bundle required")
	}
	seen := map[string]bool{}
	for _, v := range b.Bindings {
		pair := Pair(v.Stage, v.Phase)
		original, ok := manifest[pair]
		if !ok || seen[pair] || v.PromptID != original.PromptID {
			return errors.New("missing, duplicate or mismatched manifest binding")
		}
		seen[pair] = true
		if Pair(v.Policy.Stage, v.Policy.Phase) != pair || v.PromptSHA != contracts.Digest([]byte(v.Template)) || v.PolicySHA != Hash(v.Policy) {
			return errors.New("binding content mismatch")
		}
		if v.InputSchema != original.InputSchema || v.OutputSchema != original.OutputSchema || v.InputSHA != original.InputSHA || v.OutputSHA != original.OutputSHA {
			return errors.New("schema identity mismatch")
		}
		if b.Origin == "builtin" {
			if v.RegistryName != nil || v.RegistryVersion != nil || v.ContextName != nil || v.ContextVersion != nil || v.Template != original.Template || Hash(v.Policy) != Hash(original.Policy) {
				return errors.New("builtin content or registry mismatch")
			}
		}
		if b.Origin == "registry_export" {
			if v.RegistryName == nil || v.RegistryVersion == nil || v.ContextName == nil || v.ContextVersion == nil || *v.RegistryVersion < 1 || *v.ContextVersion < 1 || *v.RegistryName != "tangerine-"+v.PromptID || *v.ContextName != "tangerine-context-"+v.PromptID {
				return errors.New("exact numeric registry versions required")
			}
		}
		if e := ValidatePolicy(v.Policy, original.Policy); e != nil {
			return e
		}
	}
	return nil
}
func ValidatePolicy(p, original Policy) error {
	seen := map[string]bool{}
	for _, k := range p.Order {
		if seen[k] {
			return errors.New("duplicate context component")
		}
		seen[k] = true
		if p.Stage == "blind_claim_extraction" && (k == "mutation_key" || k == "prior_decisions" || k == "canonical_script" || k == "candidate" || k == "scoring_result") {
			return errors.New("blind extraction disclosure conflict")
		}
		if p.Stage == "mapping_audit" && (k == "prior_decisions" || k == "scoring_result" || k == "candidate") {
			return errors.New("independent audit disclosure conflict")
		}
	}
	for _, k := range original.Order {
		if k != "source_excerpt" && !seen[k] {
			return fmt.Errorf("required context component omitted: %s", k)
		}
	}
	return nil
}

var variable = regexp.MustCompile(`\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}`)

func RenderTemplate(t string, vars []string, input map[string]any) (string, error) {
	allowed := map[string]bool{}
	replacements := []string{}
	for _, k := range vars {
		if allowed[k] {
			return "", errors.New("duplicate template variable")
		}
		allowed[k] = true
		v, ok := input[k]
		if !ok {
			return "", fmt.Errorf("missing template input: %s", k)
		}
		b, e := Canonical(v)
		if e != nil {
			return "", e
		}
		replacements = append(replacements, "{{"+k+"}}", string(b))
	}
	for _, m := range variable.FindAllStringSubmatch(t, -1) {
		if !allowed[m[1]] {
			return "", fmt.Errorf("undeclared template variable: %s", m[1])
		}
	}
	return strings.NewReplacer(replacements...).Replace(t), nil
}

type Part struct {
	Kind  string          `json:"kind"`
	Trust string          `json:"trust"`
	SHA   string          `json:"sha256"`
	Bytes int             `json:"byte_count"`
	Body  json.RawMessage `json:"body"`
}
type Prepared struct {
	OutputSchema json.RawMessage   `json:"-"`
	BundleSHA    string            `json:"bundle_sha256"`
	BindingSHA   string            `json:"binding_sha256"`
	InputSHA     string            `json:"input_sha256"`
	WireSHA      string            `json:"wire_sha256"`
	Parts        []Part            `json:"parts"`
	Wire         json.RawMessage   `json:"wire"`
	Omitted      map[string]string `json:"omitted"`
	BudgetMethod string            `json:"budget_method"`
	BudgetUsed   int               `json:"input_budget_used"`
}

// BuildContext retains the complete typed DTO. Capacity belongs to the provider
// adapter, which knows the model and the final serialized request.
func BuildContext(b Bundle, stage string, phase *string, input map[string]any, components map[string]any) (Prepared, error) {
	p := Prepared{Omitted: map[string]string{}}
	var binding *Binding
	for i := range b.Bindings {
		if Pair(b.Bindings[i].Stage, b.Bindings[i].Phase) == Pair(stage, phase) {
			binding = &b.Bindings[i]
			break
		}
	}
	if binding == nil {
		return p, errors.New("unavailable binding")
	}
	raw, e := Canonical(input)
	if e != nil {
		return p, e
	}
	kind := strings.TrimSuffix(binding.InputSchema, ".schema.json")
	if _, _, e = contracts.Validate(kind, "2.0.0", raw); e != nil {
		return p, e
	}
	template, e := RenderTemplate(binding.Template, binding.Variables, input)
	if e != nil {
		return p, e
	}
	instruction, e := RenderTemplate(binding.Policy.Instruction, binding.Policy.Variables, input)
	if e != nil {
		return p, e
	}
	if actual, ok := input["answer_text"]; ok {
		if selected, present := components["answer"]; present && Hash(actual) != Hash(selected) {
			return p, errors.New("context answer differs from complete stage input")
		}
	}
	values := map[string]any{}
	for k, v := range components {
		values[k] = v
	}
	values["prompt"] = template
	values["context_policy"] = instruction
	p.OutputSchema, e = contracts.WireSchema(strings.TrimSuffix(binding.OutputSchema, ".schema.json"))
	if e != nil {
		return p, e
	}
	values["wire_schema"] = p.OutputSchema
	allowed := map[string]bool{}
	for _, k := range binding.Policy.Order {
		allowed[k] = true
		v, ok := values[k]
		if !ok || v == nil {
			if k == "source_excerpt" || k == "evidence" || k == "public_context" {
				p.Omitted[k] = "absent optional input"
				continue
			}
			return p, fmt.Errorf("missing context component: %s", k)
		}
		part, e := Canonical(v)
		if e != nil {
			return p, e
		}
		trust := "input_data"
		if k == "prompt" || k == "context_policy" || k == "wire_schema" {
			trust = "owned_instruction"
		}
		p.Parts = append(p.Parts, Part{k, trust, contracts.Digest(part), len(part), part})
	}
	for k := range components {
		if !allowed[k] {
			if stage == "blind_claim_extraction" && (k == "mutation_key" || k == "prior_decisions" || k == "canonical_script") {
				return p, errors.New("forbidden blind extraction component")
			}
			if stage == "mapping_audit" && k == "prior_decisions" {
				return p, errors.New("forbidden first-map decisions")
			}
			p.Omitted[k] = "not selected by frozen policy"
		}
	}
	p.Wire, e = Canonical(map[string]any{"stage": stage, "phase": phase, "parts": p.Parts, "stage_input": input})
	if e != nil {
		return p, e
	}
	p.BundleSHA = b.SHA
	p.BindingSHA = Hash(binding)
	p.InputSHA = contracts.Digest(raw)
	p.WireSHA = contracts.Digest(p.Wire)
	return p, nil
}

// Prepare provides the conservative bound for standalone Lab context previews.
// Runtime dispatch measures the final provider wire instead of this intermediate DTO.
func Prepare(b Bundle, stage string, phase *string, input map[string]any, components map[string]any, budget, reserved int) (Prepared, error) {
	p, err := BuildContext(b, stage, phase, input, components)
	if err != nil {
		return p, err
	}
	p.BudgetMethod = "conservative_bytes"
	p.BudgetUsed = len(p.Wire)
	if budget <= reserved || p.BudgetUsed > budget-reserved {
		return p, errors.New("required context exceeds conservative byte budget; input retained")
	}
	return p, nil
}

// Shipped identifies the authored builtin bundle; repeated readback has no new
// creation event. Runtime exports deliberately allocate a new Bundle identity.
func Shipped() Bundle {
	b := Builtins(time.Date(2026, 10, 10, 7, 0, 0, 0, time.UTC))
	b.ID = "78353c1f-0638-4c96-8de5-6aab4af2b6a6"
	b.Seal()
	return b
}
