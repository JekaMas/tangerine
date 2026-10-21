package app

import (
	"context"
	"encoding/json"
	"fmt"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"unicode/utf8"
)

// The portable fixed-answer packet is admitted once. Repetitions trust this saved
// exact target/text and call the existing native attempt/evaluation/scoring owners.
func (s *Storage) admitQualityAnswer(ctx context.Context, raw []byte) (qualityAnswerInput, error) {
	var out qualityAnswerInput
	if _, _, e := contracts.Validate("llm-quality-answer-input", "2.0.0", raw); e != nil {
		return out, e
	}
	var input map[string]any
	if e := json.Unmarshal(raw, &input); e != nil {
		return out, e
	}
	key := input["ground_truth"].(map[string]any)
	source := fmt.Sprint(key["case_version_id"])
	var flags []byte
	e := s.DB.QueryRow(ctx, "SELECT case_version_id,case_sha256,task_components FROM listening_case WHERE case_version_id=$1 AND case_sha256=$2", source, key["case_sha256"]).Scan(&out.Case, &out.SHA, &flags)
	if e != nil {
		return out, e
	}
	doc, e := s.ReadDocument(ctx, out.Case)
	if e != nil {
		return out, e
	}
	if lab.Hash(json.RawMessage(doc.Payload)) != lab.Hash(key) {
		return out, ErrReference
	}
	if lab.Hash(json.RawMessage(flags)) != lab.Hash(input["task_components"]) {
		return out, ErrReference
	}
	answer, e := s.ReadAsset(ctx, fmt.Sprint(input["answer_asset_id"]))
	if e != nil {
		return out, e
	}
	if !utf8.Valid(answer) || contracts.Digest(answer) != input["answer_sha256"] {
		return out, ErrReference
	}
	out.Answer = string(answer)
	return out, nil
}
