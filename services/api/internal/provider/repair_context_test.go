package provider

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"testing"
)

func TestGeminiRepairContextPositive(t *testing.T) {
	r, _, _ := executeFixture(t, nil, nil)
	r.Profile = geminiProfile()
	calls := 0
	client := &http.Client{Transport: trip(func(req *http.Request) (*http.Response, error) {
		calls++
		visible := "broken"
		if calls == 2 {
			visible = goodAnswer
		}
		body, _ := json.Marshal(map[string]any{"status": "completed", "steps": []any{map[string]any{"type": "model_output", "content": []any{map[string]any{"type": "text", "text": visible}}}}})
		return &http.Response{StatusCode: 200, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(string(body)))}, nil
	})}
	r.After = func(_ context.Context, a Attempt) error {
		if a.Index == 0 {
			if a.Repair != nil {
				t.Fatal("initial request fabricated repair context")
			}
			return nil
		}
		var wire struct{ Input string }
		var messages []struct{ Content string }
		if json.Unmarshal(a.Wire, &wire) != nil || json.Unmarshal([]byte(wire.Input), &messages) != nil || a.Repair == nil || messages[len(messages)-1].Content != a.Repair.Content || a.Repair.Instruction != RepairInstruction+"PROVIDER_OUTPUT_INVALID" {
			t.Fatal("Gemini repair message lost at serialization", a)
		}
		var data map[string]any
		_ = json.Unmarshal([]byte(a.Repair.Content), &data)
		if data["raw_visible_output"] != "broken" {
			t.Fatal("original response lost", data)
		}
		return nil
	}
	b, attempts, e := Execute(context.Background(), client, r, "controlled-gemini-key")
	if e != nil || calls != 2 || len(attempts) != 2 || string(b) != goodAnswer {
		t.Fatal(e, calls, string(b))
	}
}

func TestProviderRepairRetryContextPositive(t *testing.T) {
	r, c, n := executeFixture(t, []string{reply("broken"), "temporarily unavailable", reply(goodAnswer)}, []int{200, 503, 200})
	b, a, e := Execute(context.Background(), c, r, "")
	if e != nil || *n != 3 || string(b) != goodAnswer || a[0].Repair != nil || a[1].Repair == nil || a[2].Kind != "transport_retry" || a[2].Repair != a[1].Repair {
		t.Fatal("retry lost the same repair context", e, a)
	}
}

func TestProviderNoRepairContextNegative(t *testing.T) {
	r, c, _ := executeFixture(t, []string{"temporary", reply(goodAnswer)}, []int{503, 200})
	_, a, e := Execute(context.Background(), c, r, "")
	if e != nil || a[0].Repair != nil || a[1].Repair != nil {
		t.Fatal("transport retry invented semantic repair", e, a)
	}
}
