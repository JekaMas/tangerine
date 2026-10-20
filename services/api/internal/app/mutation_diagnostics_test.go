package app

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"tangerine.local/api/internal/provider"
	"testing"
	"time"
)

type diagnosticObservation struct {
	Frames              []map[string]any
	Admitted, Diagnosed int
	Output              []byte
	Err                 error
}

// The model reply is an explicit protocol fixture; all projection, diagnostic,
// bounded-repair and admission code is the real production implementation.
func generationDiagnosticFixture(t *testing.T, mode string) diagnosticObservation {
	t.Helper()
	b, clean, c, tax := mutationFixture()
	b["speakers"] = []any{map[string]any{"id": "s1"}}
	raw, _ := json.Marshal(c)
	var bad map[string]any
	_ = json.Unmarshal(raw, &bad)
	unit := bad["planned_units"].([]any)[0].(map[string]any)
	delete(unit["corrections"].([]any)[0].(map[string]any), "canonical")
	unit["explanation_eligible"] = false
	unit["text_spans"].([]any)[0].(map[string]any)["span"].(map[string]any)["start_cp"] = float64(10)
	valid := c
	if mode == "canonical" {
		bad["utterances"] = clean["utterances"]
		valid = clean
	}
	if mode == "malformed" {
		bad["planned_units"] = "wrong type"
	}
	var lock sync.Mutex
	frames := []map[string]any{}
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		raw, _ := io.ReadAll(r.Body)
		var frame map[string]any
		_ = json.Unmarshal(raw, &frame)
		lock.Lock()
		frames = append(frames, frame)
		n := len(frames)
		lock.Unlock()
		out := bad
		if n == 2 && mode != "repeat" && mode != "malformed" {
			out = valid
		}
		raw, _ = json.Marshal(out)
		encoded, _ := json.Marshal(string(raw))
		w.Header().Set("Content-Type", "application/json")
		_, _ = io.WriteString(w, `{"object":"response","status":"completed","output":[{"type":"message","content":[{"type":"output_text","text":`+string(encoded)+`}]}]}`)
	}))
	defer target.Close()
	result := diagnosticObservation{}
	request := provider.ExecuteRequest{Profile: provider.Profile{Provider: "local_responses", Model: "constructed-diagnostic-test", Endpoint: target.URL + "/v1/responses", Auth: "local_none", Billing: "local"}, Instructions: "Original task and complete output contract.", Input: []any{map[string]any{"role": "user", "content": "Complete saved input."}}, OutputKind: "case-candidate", Timeout: 5 * time.Second}
	request.Validate = func(raw []byte) error {
		result.Admitted++
		if mode == "canonical" {
			_, _, err := canonicalContent(raw, b)
			return err
		}
		_, err := mutationContent(raw, b, clean, tax)
		return err
	}
	request.DiagnoseInvalid = func(raw []byte) string {
		result.Diagnosed++
		if mode == "canonical" {
			return canonicalPhaseDiagnostic(raw, b)
		}
		return mutationLocatorDiagnostic(raw)
	}
	result.Output, _, result.Err = provider.Execute(context.Background(), target.Client(), request, "")
	lock.Lock()
	result.Frames = frames
	lock.Unlock()
	return result
}
func diagnosticRepairPayload(t *testing.T, r diagnosticObservation) map[string]any {
	t.Helper()
	if len(r.Frames) != 2 {
		t.Fatal(r)
	}
	messages := r.Frames[1]["input"].([]any)
	raw := messages[len(messages)-1].(map[string]any)["content"].(string)
	payload := map[string]any{}
	if err := json.Unmarshal([]byte(raw), &payload); err != nil {
		t.Fatal(err)
	}
	return payload
}
func TestMutationCombinedDiagnosticsPositive(t *testing.T) {
	r := generationDiagnosticFixture(t, "mutation")
	if r.Err != nil || r.Admitted != 1 || r.Diagnosed != 1 {
		t.Fatal(r)
	}
	detail := diagnosticRepairPayload(t, r)["validation_detail"].(string)
	if !strings.Contains(detail, "canonical") || !strings.Contains(detail, "Final-surface span") || !strings.Contains(detail, `"end_cp":23`) || !strings.Contains(detail, "The café open tomorrow.") {
		t.Fatal(detail)
	}
}
func TestMutationCanonicalDiagnosticsPositive(t *testing.T) {
	r := generationDiagnosticFixture(t, "canonical")
	if r.Err != nil || r.Admitted != 1 || r.Diagnosed != 1 {
		t.Fatal(r)
	}
	detail := diagnosticRepairPayload(t, r)["validation_detail"].(string)
	if !strings.Contains(detail, "canonical") || !strings.Contains(detail, "canonical_text") || !strings.Contains(detail, "planned_units") {
		t.Fatal(detail)
	}
}
func TestMutationRejectedProjectionNegative(t *testing.T) {
	r := generationDiagnosticFixture(t, "repeat")
	if r.Err == nil || len(r.Output) != 0 || len(r.Frames) != 2 || r.Admitted != 0 || r.Diagnosed != 2 {
		t.Fatal(r)
	}
}
func TestMutationUnknownPartialNegative(t *testing.T) {
	r := generationDiagnosticFixture(t, "malformed")
	if r.Err == nil || len(r.Output) != 0 || len(r.Frames) != 2 || r.Admitted != 0 {
		t.Fatal(r)
	}
	detail := diagnosticRepairPayload(t, r)["validation_detail"].(string)
	if strings.Contains(detail, "whole-turn scope") {
		t.Fatal("invented a scope from an unknown partial shape", detail)
	}
	if projected, err := provider.ProjectVisible(`{}`, "case-candidate"); err == nil || len(projected) != 0 {
		t.Fatal("public projection exposed rejected data", string(projected), err)
	}
}
