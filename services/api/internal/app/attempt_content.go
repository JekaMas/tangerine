package app

// Pure request admission and safe projections; no SQL, media or model dispatch.
import (
	"encoding/json"
	"errors"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"unicode/utf8"
)

var ErrAttemptState = errors.New("attempt is already submitted")
var ErrCaseUnavailable = errors.New("case is unavailable for new attempts")
var ErrInput = errors.New("invalid listening input")
var ErrCapacity = errors.New("answer exceeds 20000 codepoints")

func attemptInput(kind string, raw []byte) (map[string]any, []byte, error) {
	if !utf8.Valid(raw) {
		return nil, nil, ErrInput
	}
	var input map[string]any
	if json.Unmarshal(raw, &input) != nil || input == nil {
		return nil, nil, ErrInput
	}
	fields := map[string][]string{"attempt-start-request": {"case_version_id", "case_sha256", "requested_language"}, "answer-write": {"answer_text", "requested_language"}, "play-event-request": {"schema_version", "attempt_id", "audio_sha256", "kind", "client_sequence", "page_instance_id", "position_sample", "client_time_ms"}}
	projected := map[string]any{}
	for _, k := range fields[kind] {
		if v, ok := input[k]; ok {
			projected[k] = v
		}
	}
	if text, ok := projected["answer_text"].(string); ok && utf8.RuneCountInString(text) > 20000 {
		return nil, nil, ErrCapacity
	}
	accepted, _ := lab.Canonical(projected)
	_, accepted, e := contracts.Validate(kind, "2.0.0", accepted)
	if e != nil {
		return nil, nil, ErrInput
	}
	return projected, accepted, nil
}
func attemptView(a, context map[string]any) map[string]any {
	id := a["attempt_id"].(string)
	var results any
	if a["submitted_at"] != nil {
		results = "/api/v1/attempts/" + id + "/results"
	}
	return map[string]any{"attempt_id": id, "revision": a["revision"], "state": a["state"], "started_at": a["started_at"], "submitted_at": a["submitted_at"], "answer_text": a["answer_text"], "requested_language": context["requested_language"], "case": context["case_item"], "task_components": a["task_components"], "audio_path": "/api/v1/attempts/" + id + "/audio", "results_path": results}
}
func teacherStartView(a, c map[string]any) map[string]any {
	v := attemptView(a, c)
	out := map[string]any{}
	for _, k := range []string{"attempt_id", "started_at", "case", "audio_path", "task_components", "requested_language"} {
		out[k] = v[k]
	}
	out["maximum_answer_codepoints"] = 20000
	return out
}
func attemptOperation(op string, a map[string]any) map[string]any {
	return map[string]any{"operation_id": op, "state": "complete", "subject": map[string]any{"kind": "attempt", "id": a["attempt_id"], "version_id": nil}, "revision": a["revision"], "artifact_ids": []any{}, "issue_ids": []any{}}
}
func frozenAnswer(a map[string]any, answer map[string]any, key, at string, submit bool) map[string]any {
	out := map[string]any{}
	for k, v := range a {
		out[k] = v
	}
	out["revision"] = a["revision"].(float64) + 1
	out["idempotency_key"] = key
	out["answer_text"] = answer["answer_text"]
	out["answer_utf8_sha256"] = contracts.Digest([]byte(answer["answer_text"].(string)))
	if submit {
		out["state"] = "saved"
		out["submitted_at"] = at
	}
	return out
}
