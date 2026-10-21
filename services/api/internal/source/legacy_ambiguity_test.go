package source

import "testing"

func sourceBindingAmbiguity(t *testing.T, text string) Mapped {
	t.Helper()
	n, e := Parse("records.jsonl", []byte(text), Options{Format: "jsonl"})
	if e != nil {
		t.Fatal(e)
	}
	binding := map[string]any{"fields": []any{map[string]any{"source_path": "/value/response", "target_field": "text", "required": true, "conversion": "identity", "null_values": []any{}}}}
	return LegacyRecord("NIR-DATA", "r", "records.jsonl", "records", 0, n.Tables[0].Rows[0], binding)
}
func TestSourceMappingAmbiguousPositive(t *testing.T) {
	m := sourceBindingAmbiguity(t, `{"response":"One explicit native value"}`)
	equal(t, "mapped", m.Status)
}
func TestSourceMappingAmbiguousNegative(t *testing.T) {
	m := sourceBindingAmbiguity(t, `{"response":"Original value","response":"Conflicting value"}`)
	equal(t, "quarantined", m.Status)
	equal(t, true, m.Raw["ambiguous_keys"])
}
