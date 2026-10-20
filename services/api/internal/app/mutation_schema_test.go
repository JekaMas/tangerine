package app

import (
	"bytes"
	"encoding/json"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/provider"
	"testing"
)

func TestMutationCompleteWireSchemaPositive(t *testing.T) {
	raw, err := contracts.WireSchema("case-candidate")
	if err != nil {
		t.Fatal(err)
	}
	var s map[string]any
	if err = json.Unmarshal(raw, &s); err != nil {
		t.Fatal(err)
	}
	if s["$ref"] != "#/$defs/case-candidate" {
		t.Fatal(s["$ref"])
	}
	defs := s["$defs"].(map[string]any)
	acoustic := defs["acoustic-edit"].(map[string]any)
	for _, name := range []string{"unit_id", "utterance_id", "scope", "controller", "parameters"} {
		if acoustic["properties"].(map[string]any)[name] == nil {
			t.Fatal("missing referenced acoustic field", name)
		}
	}
	var walk func(any)
	walk = func(v any) {
		switch x := v.(type) {
		case []any:
			for _, e := range x {
				walk(e)
			}
		case map[string]any:
			for k, e := range x {
				if k == "$ref" && !strings.HasPrefix(e.(string), "#/") {
					t.Fatal("external reference left in model context", e)
				}
				walk(e)
			}
		}
	}
	walk(s)
}
func TestMutationStructuredWirePositive(t *testing.T) {
	schema, err := contracts.WireSchema("case-candidate")
	if err != nil {
		t.Fatal(err)
	}
	p := provider.Profile{Provider: "local_responses", Model: "fixture", Endpoint: "http://127.0.0.1:11434/v1/responses", Auth: "local_none", Billing: "local", StructuredOutput: true}
	format, err := inferenceOutputFormat(p, schema)
	if err != nil {
		t.Fatal(err)
	}
	f := format.(map[string]any)
	if f["type"] != "json_schema" || f["strict"] != true || !bytes.Equal(f["schema"].(json.RawMessage), schema) {
		t.Fatal(f)
	}
	raw, err := provider.Serialize(p, "Original complete contract.", []any{map[string]any{"role": "user", "content": "Actual stage input."}}, format)
	if err != nil {
		t.Fatal(err)
	}
	var wire map[string]any
	_ = json.Unmarshal(raw, &wire)
	if wire["text"].(map[string]any)["format"].(map[string]any)["schema"].(map[string]any)["$defs"].(map[string]any)["acoustic-edit"] == nil {
		t.Fatal("final wire lost referenced contract")
	}
}
func TestMutationPlainWireNegative(t *testing.T) {
	p := provider.Profile{Provider: "local_responses", Model: "fixture", Endpoint: "http://127.0.0.1:11434/v1/responses", Auth: "local_none", Billing: "local"}
	format, err := inferenceOutputFormat(p, nil)
	if err != nil || format != nil {
		t.Fatal("plain profile gained a response restriction", format, err)
	}
	raw, err := provider.Serialize(p, "Plain output.", []any{}, format)
	if err != nil {
		t.Fatal(err)
	}
	var wire map[string]any
	_ = json.Unmarshal(raw, &wire)
	if wire["text"] != nil {
		t.Fatal(wire)
	}
}
func TestMutationPlanSchemaNegative(t *testing.T) {
	if _, err := inferenceOutputFormat(provider.Profile{Provider: "openai_chatgpt", StructuredOutput: true}, json.RawMessage(`{}`)); err == nil {
		t.Fatal("unsupported plan formatter silently enabled")
	}
	if raw, err := contracts.WireSchema("unknown-fixture-contract"); err == nil || len(raw) != 0 {
		t.Fatal("unknown contract fabricated", string(raw), err)
	}
}
