package app

// The saved envelope is the durable handoff to the later semantic evaluator.
func savedResult(a map[string]any) map[string]any {
	slots := map[string]string{"annotation.agreement": "ratio", "annotation.cohen_kappa": "ratio", "verification.wer": "ratio", "audio.speech_rate_wpm": "words_per_minute", "audio.articulation_rate_wpm": "words_per_minute", "audio.pause_ratio": "ratio", "audio.disfluency_density": "events_per_100_words", "evaluation.coverage": "ratio", "evaluation.exact_mapping_agreement": "ratio", "telemetry.elapsed_seconds": "seconds", "telemetry.replay_count": "count", "teacher.talk_time": "ratio", "teacher.pronunciation": "ratio", "teacher.classroom_management": "ratio", "teacher.engagement": "ratio"}
	measurements := map[string]any{}
	for name, unit := range slots {
		measurements[name] = map[string]any{"status": "not_run", "exact": nil, "decimal_value": nil, "unit": unit, "method_id": "pending-evaluation", "reason_code": "NOT_RUN", "evidence_ids": []any{}, "display": nil}
	}
	return map[string]any{"schema_version": "2.0.0", "attempt_id": a["attempt_id"], "status": "saved", "score": nil, "auxiliary": map[string]any{"schema_version": "2.0.0", "attempt_id": a["attempt_id"], "case_version_id": a["case_version_id"], "measurements": measurements}, "feedback": nil, "feedback_status": "not_started", "issues": []any{}, "retry_operation": "evaluate", "result_id": nil, "result_revision_ids": []any{}}
}
