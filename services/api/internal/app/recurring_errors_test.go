package app

import (
	"encoding/json"
	"errors"
	"fmt"
	"reflect"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/provider"
	"testing"
)

// Constructed independent fixtures: twenty clean finite verbs, with explicitly
// chosen numbers of errors. No LLM or production quota computes the expectation.
func recurringFixture(n, percent, changed int) (map[string]any, map[string]any, map[string]any, map[string]any) {
	b, clean, candidate, taxonomy := mutationFixture()
	b["speakers"] = []any{map[string]any{"id": "s1"}}
	b["exercise_request"].(map[string]any)["recurring_errors"] = []any{map[string]any{"speaker_number": float64(1), "target_percent": float64(percent), "instruction": nil}}
	base, actual, opportunities, spans, utterances := []any{}, []any{}, []any{}, []any{}, []any{}
	for i := 0; i < n; i++ {
		id := fmt.Sprintf("u%d", i+1)
		text, word, end := "The café opens tomorrow.", "opens", 14
		if i < changed {
			text, word, end = "The café open tomorrow.", "open", 13
		}
		base = append(base, map[string]any{"id": id, "speaker_id": "s1", "canonical_text": "The café opens tomorrow.", "surface_text": "The café opens tomorrow."})
		actual = append(actual, map[string]any{"id": id, "speaker_id": "s1", "canonical_text": "The café opens tomorrow.", "surface_text": text})
		surface := map[string]any{"start_cp": float64(9), "end_cp": float64(end), "exact_text": word}
		opportunities = append(opportunities, map[string]any{"utterance_id": id, "canonical_span": map[string]any{"start_cp": float64(9), "end_cp": float64(14), "exact_text": "opens"}, "surface_span": surface, "mutated": i < changed})
		if i < changed {
			spans = append(spans, map[string]any{"utterance_id": id, "span": surface})
			utterances = append(utterances, id)
		}
	}
	clean["utterances"], candidate["utterances"] = base, actual
	unit := candidate["planned_units"].([]any)[0].(map[string]any)
	unit["text_spans"], unit["utterance_ids"] = spans, utterances
	unit["recurrence"] = map[string]any{"speaker_number": float64(1), "target_percent": float64(percent), "rule": "Omit the third-person singular -s from opens after the singular subject café.", "opportunities": opportunities}
	return b, clean, candidate, taxonomy
}
func recurrenceRows(c map[string]any) []any {
	return c["planned_units"].([]any)[0].(map[string]any)["recurrence"].(map[string]any)["opportunities"].([]any)
}
func TestRecurringProfilesPositive(t *testing.T) {
	raw := []byte(`{"exercise_request":{"topic":"A train journey","speaker_count":2,"text_length_words":150,"mutation_count":2,"recurring_errors":[{"speaker_number":1,"target_percent":85,"instruction":"Drop plural endings"},{"speaker_number":2,"target_percent":95,"instruction":null}]}}`)
	b, err := ExpandBlueprint(raw, DefaultConfiguration())
	if err != nil || len(recurringProfiles(b)) != 2 || recurringProfiles(b)[1]["target_percent"] != float64(85) || recurringProfiles(b)[2]["instruction"] != nil {
		t.Fatal(b, err)
	}
}
func TestRecurringProfilesNegative(t *testing.T) {
	for _, request := range []string{
		`{"speaker_count":1,"mutation_count":1,"recurring_errors":[{"speaker_number":2,"target_percent":85,"instruction":null}]}`,
		`{"speaker_count":2,"mutation_count":2,"recurring_errors":[{"speaker_number":1,"target_percent":85,"instruction":null},{"speaker_number":1,"target_percent":95,"instruction":null}]}`,
		`{"speaker_count":2,"mutation_count":1,"recurring_errors":[{"speaker_number":1,"target_percent":85,"instruction":null},{"speaker_number":2,"target_percent":95,"instruction":null}]}`,
	} {
		var req map[string]any
		_ = json.Unmarshal([]byte(request), &req)
		req["topic"], req["text_length_words"] = "Travel", 150
		raw, _ := json.Marshal(map[string]any{"exercise_request": req})
		if _, err := ExpandBlueprint(raw, DefaultConfiguration()); err == nil {
			t.Fatal("contradictory profile admitted", request)
		}
	}
}
func TestRecurringQuotaPositive(t *testing.T) {
	for _, row := range [][3]int{{20, 70, 14}, {20, 85, 17}, {20, 95, 19}, {7, 85, 6}, {4, 85, 3}, {2, 85, 2}} {
		b, _, c, _ := recurringFixture(row[0], row[1], row[2])
		if recurringQuota(row[1], row[0]) != row[2] || admitRecurringPatterns(c, b) != nil {
			t.Fatal(row)
		}
	}
}
func TestRecurringQuotaNegative(t *testing.T) {
	b, _, c, _ := recurringFixture(20, 85, 16)
	err := admitRecurringPatterns(c, b)
	var invalid *provider.OutputValidationError
	if !errors.As(err, &invalid) || !strings.Contains(invalid.Detail, "floor") {
		t.Fatal("16/20 accepted as rounded85%", err)
	}
}
func TestRecurringSpeakerNegative(t *testing.T) {
	b, _, c, _ := recurringFixture(4, 85, 3)
	c["utterances"].([]any)[3].(map[string]any)["speaker_id"] = "s2"
	if err := admitRecurringPatterns(c, b); err == nil {
		t.Fatal("other speaker entered denominator")
	}
}
func TestRecurringScopeNegative(t *testing.T) {
	for _, mode := range []string{"duplicate", "quote", "unkeyed"} {
		b, _, c, _ := recurringFixture(4, 85, 3)
		rows := recurrenceRows(c)
		switch mode {
		case "duplicate":
			rows[3] = rows[0]
		case "quote":
			rows[0].(map[string]any)["canonical_span"].(map[string]any)["start_cp"] = float64(8)
		case "unkeyed":
			c["planned_units"].([]any)[0].(map[string]any)["text_spans"] = []any{}
		}
		if err := admitRecurringPatterns(c, b); err == nil {
			t.Fatal("bad context admitted", mode)
		}
	}
}
func TestRecurringCorrectNegative(t *testing.T) {
	for _, mode := range []string{"wording", "acoustic"} {
		b, _, c, _ := recurringFixture(4, 85, 3)
		if mode == "wording" {
			c["utterances"].([]any)[3].(map[string]any)["surface_text"] = "The café open tomorrow."
			recurrenceRows(c)[3].(map[string]any)["surface_span"] = map[string]any{"start_cp": float64(9), "end_cp": float64(13), "exact_text": "open"}
		} else {
			c["acoustic_edits"] = []any{map[string]any{"unit_id": "other", "utterance_id": "u4", "scope": map[string]any{"start": float64(9), "end": float64(14)}}}
		}
		if err := admitRecurringPatterns(c, b); err == nil {
			t.Fatal("changed correct exception admitted", mode)
		}
	}
}
func TestRecurringGroupPositive(t *testing.T) {
	b, clean, c, taxonomy := recurringFixture(7, 85, 6)
	if err := admitMutation(t, b, clean, c, taxonomy); err != nil {
		t.Fatal(err)
	}
	summary := recurringSummary(c["planned_units"].([]any)[0].(map[string]any))
	if summary["opportunity_count"] != 7 || summary["mutation_count"] != 6 || summary["realized_percent_display"] != "85.7" {
		t.Fatal(summary)
	}
}
func TestRecurringPersistencePositive(t *testing.T) {
	_, _, c, _ := recurringFixture(4, 85, 3)
	m := mutationManifest(c, "canonical", strings.Repeat("a", 64), "mutated", strings.Repeat("b", 64), strings.Repeat("c", 64), nil, nil)
	raw, _ := json.Marshal(m)
	if _, _, err := contracts.Validate("mutation-manifest", "2.0.0", raw); err != nil {
		t.Fatal(err)
	}
	b, err := ExpandBlueprint([]byte(`{"exercise_request":{"topic":"The café","speaker_count":1,"text_length_words":80,"category_families":["grammar"],"mutation_count":1,"recurring_errors":[{"speaker_number":1,"target_percent":85,"instruction":null}]}}`), DefaultConfiguration())
	if err != nil {
		t.Fatal(err)
	}
	pieces, progress := []any{}, []any{}
	for _, value := range c["utterances"].([]any) {
		turn := value.(map[string]any)
		pieces = append(pieces, map[string]any{"gap_after_ms": float64(0)})
		progress = append(progress, map[string]any{"utterance_id": turn["id"], "sample_count": float64(24000), "receipt_ids": []any{}})
	}
	key := projectSpeechKey(map[string]any{"blueprint": b, "configuration": DefaultConfiguration()}, c, map[string]any{"plan": map[string]any{"case_version_id": "case1"}, "pieces": pieces}, map[string]any{"pieces": progress}, "audio1", strings.Repeat("d", 64), "1.0.0")
	raw, _ = json.Marshal(key)
	if _, _, err := contracts.Validate("ground-truth", "2.0.0", raw); err != nil {
		t.Fatal(err)
	}
	evaluation := recurringEvaluationKey(key)
	for _, kind := range []string{"evaluation-key", "teacher-key"} {
		raw = recurringProjectionBytes(evaluation, kind)
		if _, _, err := contracts.Validate(kind, "2.0.0", raw); err != nil {
			t.Fatal("grading and disclosure must receive the complete recurring ledger", kind, err)
		}
	}
	evaluation["units"].([]any)[0].(map[string]any)["recurrence"].(map[string]any)["target_percent"] = float64(120)
	for _, kind := range []string{"evaluation-key", "teacher-key"} {
		raw = recurringProjectionBytes(evaluation, kind)
		if _, _, err := contracts.Validate(kind, "2.0.0", raw); err == nil {
			t.Fatal("invalid recurring frequency passed grading/disclosure input admission", kind)
		}
	}
	evaluation["units"].([]any)[0].(map[string]any)["recurrence"].(map[string]any)["target_percent"] = float64(85)
	want := c["planned_units"].([]any)[0].(map[string]any)["recurrence"]
	if !reflect.DeepEqual(key["units"].([]any)[0].(map[string]any)["recurrence"], want) || !reflect.DeepEqual(m["planned_units"].([]any)[0].(map[string]any)["recurrence"], want) {
		t.Fatal("ledger lost")
	}
	if !reflect.DeepEqual(reviewCandidate(key)["planned_units"].([]any)[0].(map[string]any)["recurrence"], want) {
		t.Fatal("optional review projection lost the group")
	}
}

func recurringProjectionBytes(value map[string]any, kind string) []byte {
	raw, _ := json.Marshal(value)
	if kind == "teacher-key" {
		var teacher map[string]any
		_ = json.Unmarshal(raw, &teacher)
		for _, unit := range teacher["units"].([]any) {
			delete(unit.(map[string]any), "evidence_ids")
		}
		raw, _ = json.Marshal(teacher)
	}
	return raw
}

func recurringEvaluationKey(key map[string]any) map[string]any {
	value := map[string]any{}
	for _, field := range []string{"schema_version", "case_version_id", "taxonomy_version", "public_context", "variety_policy", "audio", "speakers", "utterances", "units", "verification_policy_version", "case_sha256"} {
		value[field] = key[field]
	}
	return value
}
func TestRecurringScorePositive(t *testing.T) {
	r, key, extraction, mapping := scoredCategoryFixture()
	r.Attempt["task_components"].(map[string]any)["classification"] = false
	_, _, candidate, _ := recurringFixture(20, 85, 17)
	key.Key["units"].([]any)[0].(map[string]any)["recurrence"] = candidate["planned_units"].([]any)[0].(map[string]any)["recurrence"]
	score, err := scoreInterpretation(r, key, extraction, mapping, nil)
	if err != nil || score.Counts.TP != 1 || score.Counts.G != 1 || score.Composite.Exact.Numerator != "100" || score.Composite.Exact.Denominator != "1" {
		t.Fatal(score, err)
	}
	if score.Items[0].Reference["recurrence"].(map[string]any)["mutation_count"] != 17 {
		t.Fatal(score.Items)
	}
	raw, _ := json.Marshal(score)
	var document map[string]any
	_ = json.Unmarshal(raw, &document)
	summary := map[string]any{}
	for _, field := range []string{"schema_version", "attempt_id", "case_version_id", "decision_set_sha256", "scoring_policy_version", "status", "counts", "composite", "optional_explanation", "items"} {
		summary[field] = document[field]
	}
	raw, _ = json.Marshal(summary)
	if _, _, err := contracts.Validate("feedback-score", "2.0.0", raw); err != nil {
		t.Fatal("comments must receive the saved recurring score facts", err)
	}
	summary["items"].([]any)[0].(map[string]any)["reference"].(map[string]any)["recurrence"].(map[string]any)["target_percent"] = "frequent"
	raw, _ = json.Marshal(summary)
	if _, _, err := contracts.Validate("feedback-score", "2.0.0", raw); err == nil {
		t.Fatal("invalid recurring summary passed comments input admission")
	}
}
func TestRecurringSpeechPlanPositive(t *testing.T) {
	settings, candidate, profile := speechFixture(t)
	unit := candidate["planned_units"].([]any)[0].(map[string]any)
	unit["recurrence"] = map[string]any{}
	candidate["acoustic_edits"] = []any{map[string]any{"unit_id": "e1", "utterance_id": "u1", "controller": "phone_pair"}, map[string]any{"unit_id": "e1", "utterance_id": "u1", "controller": "phone_pair"}}
	profile["provider"], profile["adapter_version"] = "local_kokoro", "kokoro-controlled-v1"
	plan, err := compileSpeechPlan("p1", settings, candidate, profile)
	if err != nil || !reflect.DeepEqual(plan["turns"].([]any)[0].(map[string]any)["recurring_unit_ids"], []any{"e1"}) {
		t.Fatal(plan, err)
	}
}
func TestRecurringSpeechPlanNegative(t *testing.T) {
	settings, candidate, profile := speechFixture(t)
	plan, err := compileSpeechPlan("p1", settings, candidate, profile)
	if err != nil {
		t.Fatal(err)
	}
	if _, exists := plan["turns"].([]any)[0].(map[string]any)["recurring_unit_ids"]; exists {
		t.Fatal("ordinary plan acquired a recurring group")
	}
}
func TestRecurringControlNegative(t *testing.T) {
	b, _, c, _ := recurringFixture(4, 85, 3)
	delete(b["exercise_request"].(map[string]any), "recurring_errors")
	if err := admitRecurringPatterns(c, b); err == nil {
		t.Fatal("unsolicited recurring group")
	}
	b, _, c, _ = recurringFixture(4, 85, 3)
	b["exercise_request"].(map[string]any)["mutation_count"] = float64(0)
	c["planned_units"] = []any{}
	if err := admitRecurringPatterns(c, b); err != nil {
		t.Fatal(err)
	}
}
func TestRecurringReasonNegative(t *testing.T) {
	r, key, extraction, mapping := scoredCategoryFixture()
	r.Attempt["task_components"].(map[string]any)["classification"] = false
	_, _, candidate, _ := recurringFixture(4, 85, 3)
	key.Key["units"].([]any)[0].(map[string]any)["recurrence"] = candidate["planned_units"].([]any)[0].(map[string]any)["recurrence"]
	score, err := scoreInterpretation(r, key, extraction, mapping, nil)
	if err != nil || score.Composite.Exact.Numerator != "100" || score.Explanation.Numerator == nil || *score.Explanation.Numerator != "0" {
		t.Fatal("reason erased primary or gained false credit", score, err)
	}
}
