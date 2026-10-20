package provider

import "testing"

func TestEvaluationProjectionObjectPositive(t *testing.T) {
	raw := `{"answer_text":"saved","requested_language":"en"`
	b, err := projectStageVisible(raw, "answer-write", false, func(v any) any { return v })
	if err != nil || string(b) != `{"answer_text":"saved","requested_language":"en"}` {
		t.Fatal(string(b), err)
	}
}
func TestEvaluationProjectionContainersPositive(t *testing.T) {
	raw := `{"answer_text":"literal { bracket [ text","requested_language":"en","extra":[{"note":"unchanged"}`
	b, err := projectStageVisible(raw, "answer-write", false, func(v any) any { return v })
	if err != nil || string(b) != `{"answer_text":"literal { bracket [ text","requested_language":"en"}` {
		t.Fatal(string(b), err)
	}
}
func TestEvaluationProjectionTruncatedNegative(t *testing.T) {
	for _, raw := range []string{`{"answer_text":"unfinished`, `{"answer_text":`, `{"answer_text":"saved",`, `{"answer_text":"saved"]`} {
		if completeStageContainers(raw) != raw {
			t.Fatal("invented or rewrote a value", raw)
		}
	}
}
func TestEvaluationProjectionDefaultNegative(t *testing.T) {
	if b, err := ProjectVisible(`{"answer_text":"saved","requested_language":"en"`, "answer-write"); err == nil || b != nil {
		t.Fatal("changed the standalone caller policy", string(b), err)
	}
}
