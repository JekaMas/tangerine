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

// Explicit remote-protocol substitution; this observes real request serialization
// and bounded repair behavior, not model quality, hosted access or a corpus.
func mutationRepairFixture(t *testing.T, mode string) ([]map[string]any, error) {
	t.Helper()
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
		w.Header().Set("Content-Type", "application/json")
		if mode == "quota" {
			w.WriteHeader(429)
			_, _ = io.WriteString(w, `{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}`)
			return
		}
		text := "broken output"
		if mode == "semantic" && n == 1 {
			text = `{"answer_text":"wrong reference","requested_language":"en"}`
		}
		if n == 2 && mode != "broken" {
			text = `{"answer_text":"valid answer","requested_language":"en"}`
		}
		encoded, _ := json.Marshal(text)
		_, _ = io.WriteString(w, `{"object":"response","status":"completed","output":[{"type":"message","content":[{"type":"output_text","text":`+string(encoded)+`}]}]}`)
	}))
	defer target.Close()
	request := provider.ExecuteRequest{Profile: provider.Profile{Provider: "local_responses", Model: "constructed-prefix-test", Endpoint: target.URL + "/v1/responses", Auth: "local_none", Billing: "local"}, Instructions: "original trusted task", Input: []any{map[string]any{"role": "user", "content": "complete original context"}}, OutputKind: "answer-write", Timeout: 5 * time.Second}
	if mode == "semantic" {
		request.Validate = func(raw []byte) error {
			if strings.Contains(string(raw), "wrong reference") {
				return &provider.OutputValidationError{Detail: "Preserve the requested answer reference."}
			}
			return nil
		}
	}
	_, _, err := provider.Execute(context.Background(), target.Client(), request, "")
	lock.Lock()
	defer lock.Unlock()
	return frames, err
}
func assertMutationRepairPrefix(t *testing.T, frames []map[string]any) map[string]any {
	t.Helper()
	if len(frames) != 2 || frames[0]["instructions"] != "original trusted task" || frames[1]["instructions"] != "original trusted task" {
		t.Fatal("repair changed the instruction prefix", frames)
	}
	a, b := frames[0]["input"].([]any), frames[1]["input"].([]any)
	if len(a) != 1 || len(b) != 2 {
		t.Fatal(a, b)
	}
	x, _ := json.Marshal(a[0])
	y, _ := json.Marshal(b[0])
	if string(x) != string(y) {
		t.Fatal("original context changed", a, b)
	}
	payload := map[string]any{}
	if err := json.Unmarshal([]byte(b[1].(map[string]any)["content"].(string)), &payload); err != nil {
		t.Fatal(err)
	}
	if b[1].(map[string]any)["role"] != "user" || !strings.HasPrefix(payload["repair_instruction"].(string), provider.RepairInstruction) {
		t.Fatal(b)
	}
	return payload
}
func TestMutationRepairPrefixPositive(t *testing.T) {
	frames, err := mutationRepairFixture(t, "format")
	if err != nil {
		t.Fatal(err)
	}
	p := assertMutationRepairPrefix(t, frames)
	if p["raw_visible_output"] != "broken output" || p["validation_code"] != "PROVIDER_OUTPUT_INVALID" {
		t.Fatal(p)
	}
}
func TestMutationRepairDetailPositive(t *testing.T) {
	frames, err := mutationRepairFixture(t, "semantic")
	if err != nil {
		t.Fatal(err)
	}
	p := assertMutationRepairPrefix(t, frames)
	if p["validation_detail"] != "Preserve the requested answer reference." || !strings.Contains(p["raw_visible_output"].(string), "wrong reference") {
		t.Fatal(p)
	}
}
func TestMutationRepairBoundNegative(t *testing.T) {
	frames, err := mutationRepairFixture(t, "broken")
	if err == nil {
		t.Fatal("unrepaired output accepted")
	}
	assertMutationRepairPrefix(t, frames)
}
func TestMutationRepairQuotaNegative(t *testing.T) {
	frames, err := mutationRepairFixture(t, "quota")
	if err == nil || len(frames) != 1 || len(frames[0]["input"].([]any)) != 1 || frames[0]["instructions"] != "original trusted task" {
		t.Fatal(frames, err)
	}
}
