package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestNativeReviewBrowserFixture(t *testing.T) {
	f := reviewFixture(t, "supported")
	seedReviewBrowserAuditory(t, f.s, f.id)
	f.s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	f.s.speechToken = "actual-local-speech-test"
	root := f.attempt
	second := f.start(t)
	f.attempt = second
	_, _, err := f.s.Store.WriteAnswer(context.Background(), second, uuid.NewString(), 0, answerPacket("Use opens.", "en"), true)
	requireListening(t, err)
	_, err = f.interpret(t, uuid.NewString())
	requireListening(t, err)
	f.attempt = root
	dir := os.Getenv("TANGERINE_INTERPRETATION_EVIDENCE")
	if dir == "" {
		t.Fatal("evidence required")
	}
	f.reviewPath = filepath.Join(dir, "review-mode")
	f.s.token = "listening-owned-token"
	listener, e := net.Listen("tcp", ":8080")
	requireListening(t, e)
	server := &http.Server{Handler: f.s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer func() {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = server.Shutdown(ctx)
	}()
	var schema string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT current_schema()").Scan(&schema))
	requireListening(t, os.WriteFile(filepath.Join(dir, "fixture.json"), mustJSON(map[string]any{"case_id": f.id, "case_sha256": f.sha, "attempt_id": f.attempt, "second_attempt_id": second, "schema": schema}), 0600))
	deadline := time.After(600 * time.Second)
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-deadline:
			t.Fatal("browser deadline")
		case <-ticker.C:
			if _, e = os.Stat(filepath.Join(dir, "done")); e == nil {
				return
			}
		}
	}
}

// Constructed model report, actual storage/readback/UI. No auditory inference
// is claimed by this fixture; the separate ActualAuditory case owns that.
func seedReviewBrowserAuditory(t *testing.T, s *Server, caseID string) {
	t.Helper()
	ctx := context.Background()
	doc, err := s.Store.ReadDocument(ctx, caseID)
	requireListening(t, err)
	var key map[string]any
	requireListening(t, json.Unmarshal(doc.Payload, &key))
	target := key["units"].([]any)[0].(map[string]any)["id"].(string)
	finding := map[string]any{"unit_id": target, "feature": "speech_realization", "status": "supported", "description": "Clearly audible target feature.", "reason": "Constructed auditory metadata fixture.", "clip_interval": nil, "proposed_ipa": "pɛn"}
	input, err := s.Store.saveProviderBytes(ctx, []byte(`{"origin":"constructed_auditory_metadata_fixture"}`), "provider_input")
	requireListening(t, err)
	output, err := s.Store.saveProviderBytes(ctx, sourceBytes(finding), "provider_output")
	requireListening(t, err)
	op, err := s.Store.ReserveOperation(ctx, OperationRequest{Name: "speech_measure", Key: uuid.NewString(), Path: "/test/constructed-auditory-metadata", Body: []byte(`{}`)})
	requireListening(t, err)
	requireListening(t, s.Store.claimInference(ctx, op.ID))
	defer s.Store.releaseInference(ctx, op.ID)
	row := map[string]any{"id": uuid.NewString(), "audio_sha256": key["audio"].(map[string]any)["sha256"], "method_id": "qwen25-omni-audio-v1", "method_version": "constructed-metadata-v1", "feature": "speech_realization", "interval": map[string]any{"start": 0, "end": 24000, "sample_rate_hz": 24000}, "status": "observed", "numeric_value": nil, "categorical_value": "model_supported", "unit": "category", "evidence_asset_ids": []any{output.ID}, "reason": nil, "target_unit_id": target, "auditory_finding": finding}
	run := map[string]any{"schema_version": "2.0.0", "id": uuid.NewString(), "case_version_id": caseID, "operation_id": op.ID, "status": "complete", "method_ids": []any{"qwen25-omni-audio-v1"}, "input_asset_id": input.ID, "output_asset_ids": []any{output.ID}, "support_asset_ids": []any{}, "receipt_ids": []any{}, "measurement_ids": []any{}, "failure_code": nil}
	_, err = s.Store.finishAudioDiagnostic(ctx, op, run, []map[string]any{row})
	requireListening(t, err)
	rows, err := s.Store.reviewMeasurements(ctx, caseID)
	requireListening(t, err)
	if len(rows) != 1 {
		t.Fatal(rows)
	}
	var saved map[string]any
	requireListening(t, json.Unmarshal(rows[0].(json.RawMessage), &saved))
	if saved["target_unit_id"] != target || saved["auditory_finding"].(map[string]any)["proposed_ipa"] != "pɛn" {
		t.Fatal(saved)
	}
}
