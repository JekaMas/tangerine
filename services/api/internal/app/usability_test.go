package app

import (
	"encoding/json"
	"reflect"
	"testing"
)

func TestPreparationOrdinaryChoicesPositive(t *testing.T) {
	for _, level := range []any{nil, "A1", "A2", "B1", "B2", "C1", "C2"} {
		for _, family := range []string{"grammar", "lexis", "pronunciation", "pronunciation.segmental", "pronunciation.suprasegmental", "fluency", "discourse", "pragmatics_register"} {
			for _, count := range []any{nil, float64(0), float64(3)} {
				request := map[string]any{"topic": "Insurance choices", "speaker_count": 2, "text_length_words": 180, "english_level": level, "category_families": []any{family}, "mutation_count": count}
				raw, _ := json.Marshal(map[string]any{"exercise_request": request})
				blueprint, err := ExpandBlueprint(raw, DefaultConfiguration())
				if err != nil {
					t.Fatal(level, family, count, err)
				}
				saved := blueprint["exercise_request"].(map[string]any)
				if saved["english_level"] != level || saved["mutation_count"] != count || !reflect.DeepEqual(saved["category_families"], []any{family}) {
					t.Fatal(saved)
				}
				for _, value := range blueprint["speakers"].([]any) {
					if value.(map[string]any)["learner_cefr"] != level {
						t.Fatal("level not propagated", blueprint)
					}
				}
			}
		}
	}
}

func TestPreparationOrdinaryInvalidNegative(t *testing.T) {
	for _, invalid := range []map[string]any{{"english_level": "A0"}, {"category_families": []any{"made_up"}}, {"mutation_count": -1}, {"mutation_count": 1.5}, {"speaker_count": 0}, {"text_length_words": 0}} {
		request := map[string]any{"topic": "Insurance choices", "speaker_count": 2, "text_length_words": 180}
		for key, value := range invalid {
			request[key] = value
		}
		raw, _ := json.Marshal(map[string]any{"exercise_request": request})
		if _, err := ExpandBlueprint(raw, DefaultConfiguration()); err == nil {
			t.Fatal("invalid request accepted", invalid)
		}
	}
}

func TestCheckingStagesPositive(t *testing.T) {
	record := AttemptRecord{Attempt: map[string]any{"state": "evaluating"}, Context: map[string]any{"configuration": map[string]any{}}}
	id := "accepted-checkpoint"
	state := &InterpretationState{Status: "running"}
	if checkingStage(record, state) != "extraction" {
		t.Fatal("extraction")
	}
	state.Extraction = &id
	if checkingStage(record, state) != "matching" {
		t.Fatal("matching")
	}
	state.Mapping = &id
	if checkingStage(record, state) != "scoring" {
		t.Fatal("scoring")
	}
	record.Context["configuration"].(map[string]any)["mapping_audit_enabled"] = true
	if checkingStage(record, state) != "audit" {
		t.Fatal("audit")
	}
	state.Audit = &id
	state.Result = &id
	if checkingStage(record, state) != "feedback" {
		t.Fatal("feedback")
	}
	record.Attempt["state"] = "completed"
	state.Status = "complete"
	if checkingStage(record, state) != "complete" {
		t.Fatal("complete")
	}
}

func TestCheckingIncompleteNegative(t *testing.T) {
	record := AttemptRecord{Attempt: map[string]any{"state": "submitted"}, Context: map[string]any{}}
	if checkingStage(record, nil) != "not_started" {
		t.Fatal("unsaved progress invented")
	}
	state := &InterpretationState{Status: "failed"}
	if checkingStage(record, state) != "failed" {
		t.Fatal("failure hidden")
	}
	id := "saved-score"
	state.Result = &id
	if checkingStage(record, state) != "failed" {
		t.Fatal("partial saved score hides failure")
	}
}

func TestPreparationSummaryChoicesPositive(t *testing.T) {
	request := map[string]any{"topic": "Insurance choices", "speaker_count": 2, "text_length_words": 180, "english_level": "B2", "category_families": []any{"grammar", "lexis"}, "mutation_count": 0}
	summary := speechSummary(map[string]any{"id": "p1", "phase_states": map[string]any{"render": "not_started"}, "exercise_request": request, "key_id": "private-key"})
	if !reflect.DeepEqual(summary["exercise_request"], request) {
		t.Fatal(summary)
	}
	if _, leaked := summary["key_id"]; leaked {
		t.Fatal("key leaked")
	}
}

func TestPreparationLegacySummaryNegative(t *testing.T) {
	summary := speechSummary(map[string]any{"id": "old", "phase_states": map[string]any{"render": "complete"}})
	if _, invented := summary["exercise_request"]; invented {
		t.Fatal("legacy request invented")
	}
}
