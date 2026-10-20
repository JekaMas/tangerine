package app

import (
	"encoding/json"
	"strings"
	"tangerine.local/api/internal/contracts"
	"testing"
)

func answerPacket(text, language string) []byte {
	b, _ := json.Marshal(map[string]any{"answer_text": text, "requested_language": language})
	return b
}
func TestListeningUnicodePositive(t *testing.T) {
	text := "  Ошибка: cafe\u0301 👩‍🏫\r\nHe go → He goes.\t"
	v, _, e := attemptInput("answer-write", answerPacket(text, "ru"))
	if e != nil || v["answer_text"] != text {
		t.Fatal(v, e)
	}
}
func TestListeningLimitPositive(t *testing.T) {
	text := strings.Repeat("🟠", 20000)
	v, _, e := attemptInput("answer-write", answerPacket(text, "en"))
	if e != nil || len([]rune(v["answer_text"].(string))) != 20000 {
		t.Fatal(e)
	}
}
func TestListeningOverLimitNegative(t *testing.T) {
	if _, _, e := attemptInput("answer-write", answerPacket(strings.Repeat("x", 20001), "en")); e != ErrCapacity {
		t.Fatal(e)
	}
}
func TestListeningInvalidInputNegative(t *testing.T) {
	for _, raw := range [][]byte{[]byte(`{"answer_text":"x","requested_language":"fr"}`), []byte("{\"answer_text\":\"\xff\",\"requested_language\":\"en\"}"), []byte(`null`)} {
		if _, _, e := attemptInput("answer-write", raw); e == nil {
			t.Fatal("accepted", string(raw))
		}
	}
}
func TestListeningProjectionPositive(t *testing.T) {
	a := map[string]any{"attempt_id": "a1", "revision": float64(0), "state": "started", "started_at": "2026-10-20T00:00:00Z", "submitted_at": nil, "answer_text": "", "task_components": map[string]any{"detection": true, "classification": true, "correction": true, "explanation": false}}
	c := map[string]any{"case_item": map[string]any{"id": "c"}, "requested_language": "en"}
	v := attemptView(a, c)
	if len(v) != 11 || v["results_path"] != nil || v["answer_text"] != "" {
		t.Fatal(v)
	}
}
func TestListeningSavedEnvelopePositive(t *testing.T) {
	v := savedResult(map[string]any{"attempt_id": "a1", "case_version_id": "c1"})
	raw, _ := json.Marshal(v)
	if _, _, e := contracts.Validate("result-envelope", "2.0.0", raw); e != nil {
		t.Fatal(e)
	}
	if v["score"] != nil || v["status"] != "saved" {
		t.Fatal(v)
	}
}
func TestListeningProjectionPrivateNegative(t *testing.T) {
	a := map[string]any{"attempt_id": "a1", "revision": float64(0), "submitted_at": nil, "key": "hidden", "lease_token": "secret", "provider_body": "private"}
	v := attemptView(a, map[string]any{})
	for _, k := range []string{"key", "lease_token", "provider_body", "configuration"} {
		if _, ok := v[k]; ok {
			t.Fatal(k)
		}
	}
}
func TestListeningHarmlessFieldsNegative(t *testing.T) {
	v, _, e := attemptInput("answer-write", []byte(`{"answer_text":"","requested_language":"en","state":"completed","revision":99,"lease_token":"fake","extra":"ignored"}`))
	if e != nil || len(v) != 2 || v["answer_text"] != "" {
		t.Fatal(v, e)
	}
}
