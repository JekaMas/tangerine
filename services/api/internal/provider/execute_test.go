package provider

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"testing"
	"time"
)

func TestProviderProjectionFencePositive(t *testing.T) {
	b, e := ProjectVisible("Here it is:\n```json\n{\"answer_text\":\"real answer\",\"requested_language\":\"en\",\"extra\":true}\n```", "answer-write")
	if e != nil || string(b) != `{"answer_text":"real answer","requested_language":"en"}` {
		t.Fatal(e, string(b))
	}
}
func TestProviderProjectionIdenticalPositive(t *testing.T) {
	b, e := ProjectVisible(`{"answer_text":"yes","requested_language":"en","one":1} {"requested_language":"en","answer_text":"yes","two":2}`, "answer-write")
	if e != nil || string(b) != `{"answer_text":"yes","requested_language":"en"}` {
		t.Fatal(e, string(b))
	}
}
func TestProviderProjectionAmbiguousNegative(t *testing.T) {
	if _, e := ProjectVisible(`{"answer_text":"yes","requested_language":"en"} {"answer_text":"no","requested_language":"en"}`, "answer-write"); e == nil {
		t.Fatal("distinct candidates accepted")
	}
}
func TestProviderProjectionMissingNegative(t *testing.T) {
	for _, s := range []string{`{"requested_language":"en"}`, `{"answer_text":"first","answer_text":"last","requested_language":"en"}`, `{"answer_text":"x","requested_language":"en"`} {
		if _, e := ProjectVisible(s, "answer-write"); e == nil {
			t.Fatal("invalid accepted", s)
		}
	}
}
func executeFixture(t *testing.T, bodies []string, statuses []int) (ExecuteRequest, *http.Client, *int) {
	t.Helper()
	calls := 0
	client := &http.Client{Transport: trip(func(r *http.Request) (*http.Response, error) {
		index := calls
		calls++
		if index >= len(bodies) {
			t.Fatal("unexpected extra call")
		}
		status := 200
		if statuses != nil {
			status = statuses[index]
		}
		return &http.Response{StatusCode: status, Header: make(http.Header), Body: io.NopCloser(strings.NewReader(bodies[index])), Request: r}, nil
	})}
	p := planProfile()
	p.Stream = false
	p.Provider = "local_responses"
	p.Auth = "local_none"
	p.Billing = "local"
	p.Endpoint = "http://127.0.0.1:11434/v1/responses"
	r := ExecuteRequest{Profile: p, Input: []any{map[string]any{"role": "user", "content": "initial input"}}, Instructions: "original", OutputKind: "answer-write", Timeout: 10 * time.Second}
	return r, client, &calls
}
func reply(visible string) string {
	v := map[string]any{"status": "completed", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": visible}}}}}
	b, _ := json.Marshal(v)
	return string(b)
}

const goodAnswer = `{"answer_text":"ok","requested_language":"en"}`

func TestProviderRetryPositive(t *testing.T) {
	r, c, n := executeFixture(t, []string{"temporary", reply(goodAnswer)}, []int{503, 200})
	b, a, e := Execute(context.Background(), c, r, "")
	if e != nil || *n != 2 || string(b) != goodAnswer || a[1].Kind != "transport_retry" {
		t.Fatal(e, *n, string(b), a)
	}
}
func TestProviderFallbackPositive(t *testing.T) {
	r, c, n := executeFixture(t, []string{`{"error":{"code":"unsupported_parameter"}}`, reply(goodAnswer)}, []int{400, 200})
	r.Format = map[string]any{"type": "json_schema"}
	b, a, e := Execute(context.Background(), c, r, "")
	if e != nil || *n != 2 || string(b) != goodAnswer || a[1].Kind != "structured_fallback" || strings.Contains(string(a[1].Wire), `"text"`) {
		t.Fatal(e, *n)
	}
}
func TestProviderRetryBoundNegative(t *testing.T) {
	r, c, n := executeFixture(t, []string{"unavailable", "still unavailable"}, []int{503, 503})
	_, a, e := Execute(context.Background(), c, r, "")
	if e == nil || *n != 2 || len(a) != 2 {
		t.Fatal(e, *n)
	}
}
func TestProviderRefusalNoRetryNegative(t *testing.T) {
	r, c, n := executeFixture(t, []string{`{"status":"completed","output":[{"type":"message","content":[{"type":"refusal","refusal":"refused"}]}]}`}, nil)
	_, a, e := Execute(context.Background(), c, r, "")
	if e == nil || *n != 1 || a[0].Response.Outcome != "refusal" {
		t.Fatal(e, *n)
	}
}
func TestProviderRepairPositive(t *testing.T) {
	r, c, n := executeFixture(t, []string{reply("broken"), reply(goodAnswer)}, nil)
	b, a, e := Execute(context.Background(), c, r, "")
	if e != nil || *n != 2 || string(b) != goodAnswer || a[1].Kind != "semantic_repair" || !strings.Contains(string(a[1].Wire), "raw_visible_output") || !strings.Contains(string(a[1].Wire), "initial input") {
		t.Fatal(e, *n)
	}
}
func TestProviderRepairSemanticPositive(t *testing.T) {
	r, c, n := executeFixture(t, []string{reply(`{"answer_text":"wrong reference","requested_language":"en"}`), reply(goodAnswer)}, nil)
	r.Validate = func(b []byte) error {
		if strings.Contains(string(b), "wrong reference") {
			return fmt.Errorf("authored reference conflict")
		}
		return nil
	}
	b, a, e := Execute(context.Background(), c, r, "")
	if e != nil || *n != 2 || string(b) != goodAnswer || len(a) != 2 {
		t.Fatal(e, *n)
	}
}
func TestProviderRepairExhaustedNegative(t *testing.T) {
	r, c, n := executeFixture(t, []string{reply("broken"), reply("still broken")}, nil)
	_, a, e := Execute(context.Background(), c, r, "")
	if e == nil || *n != 2 || len(a) != 2 {
		t.Fatal(e, *n)
	}
}
func TestProviderRepairQuotaNegative(t *testing.T) {
	r, c, n := executeFixture(t, []string{`{"error":{"code":"subscription_sharing_usage_limit_exceeded"}}`}, []int{429})
	_, a, e := Execute(context.Background(), c, r, "")
	code, _ := SafeError(e)
	if code != "LOCAL_BUDGET_EXCEEDED" || *n != 1 || len(a) != 1 {
		t.Fatal(e, *n)
	}
}
func TestProviderSaveBeforeUsePositive(t *testing.T) {
	r, c, n := executeFixture(t, []string{reply(goodAnswer)}, nil)
	saved := false
	r.After = func(ctx context.Context, a Attempt) error {
		if a.Response.Visible != goodAnswer || a.Index != 0 {
			t.Fatal("wrong saved attempt")
		}
		saved = true
		return nil
	}
	b, _, e := Execute(context.Background(), c, r, "")
	if e != nil || !saved || *n != 1 || string(b) != goodAnswer {
		t.Fatal(e)
	}
}
func TestProviderCancelReceiptPositive(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	r, c, n := executeFixture(t, []string{reply(goodAnswer)}, nil)
	r.Before = func(context.Context, Attempt) error { cancel(); return nil }
	saved := false
	r.After = func(save context.Context, a Attempt) error {
		if save.Err() != nil || a.Response.Outcome != "cancelled" {
			t.Fatal("cancel lost native receipt")
		}
		saved = true
		return nil
	}
	_, _, e := Execute(ctx, c, r, "")
	if e == nil || !saved || *n != 0 {
		t.Fatal(e, saved, *n)
	}
}
func TestProviderSaveFailureNegative(t *testing.T) {
	r, c, n := executeFixture(t, []string{reply(goodAnswer)}, nil)
	r.After = func(context.Context, Attempt) error { return fmt.Errorf("test-owned media failure") }
	b, a, e := Execute(context.Background(), c, r, "")
	if e == nil || b != nil || len(a) != 1 || *n != 1 {
		t.Fatal(e)
	}
}
func TestProviderDeadlineSharedNegative(t *testing.T) {
	for _, status := range []int{503, 200} {
		r, c, n := executeFixture(t, []string{reply(goodAnswer)}, []int{status})
		if _, err := Serialize(r.Profile, r.Instructions, r.Input, nil); err != nil {
			t.Fatal(err)
		}
		r.Timeout = 100 * time.Millisecond
		r.After = func(context.Context, Attempt) error { time.Sleep(200 * time.Millisecond); return nil }
		output, a, e := Execute(context.Background(), c, r, "")
		code, _ := SafeError(e)
		if code != "DEADLINE_EXCEEDED" || output != nil || *n != 1 || len(a) != 1 {
			t.Fatal(status, e, *n, string(output))
		}
	}
}
