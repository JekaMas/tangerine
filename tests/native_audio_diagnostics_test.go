package app

// Constructed upstream reports exercise the real persistence/HTTP/context owners.
// Native ffmpeg/Praat/Whisper/model observations are separate explicitly named cases.
import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"testing"
	"time"
)

func diagnosticFixture(t *testing.T, mode string) (listeningFixture, *int) {
	t.Helper()
	f := listeningCase(t)
	calls := 0
	endpoint := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		var p map[string]any
		if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
			t.Error(err)
		}
		if r.Header.Get("Authorization") != "Bearer diagnostic-owned" {
			t.Error("missing private auth")
		}
		if mode == "failure" {
			w.WriteHeader(503)
			_ = json.NewEncoder(w).Encode(map[string]any{"error": "SPEECH_UNAVAILABLE"})
			return
		}
		row := map[string]any{"id": uuid.NewString(), "audio_sha256": p["audio_sha256"], "method_id": p["method_id"], "method_version": "constructed-transport-v1", "feature": "integrated_lufs", "interval": map[string]any{"start": 0, "end": 24000, "sample_rate_hz": 24000}, "status": "observed", "numeric_value": "-18.25", "categorical_value": nil, "unit": "LUFS", "evidence_asset_ids": []any{}, "reason": nil}
		if mode == "clock" {
			row["interval"].(map[string]any)["end"] = 24001
		}
		if mode == "hash" {
			row["audio_sha256"] = strings.Repeat("0", 64)
		}
		if mode == "missing" {
			row["numeric_value"] = nil
		}
		_ = json.NewEncoder(w).Encode(map[string]any{"measurements": []any{row}, "native": map[string]any{"origin": "constructed_transport_fixture"}, "receipt": map[string]any{"inference_calls": 0}})
	}))
	t.Cleanup(endpoint.Close)
	f.s.SpeechURL = endpoint.URL
	f.s.speechToken = "diagnostic-owned"
	return f, &calls
}
func diagnosticRequest(f listeningFixture, methods ...string) AudioMeasureRequest {
	return AudioMeasureRequest{Case: f.id, AudioSHA: f.audioSHA, Methods: methods}
}
func diagnosticEvidence(t *testing.T, f listeningFixture, v map[string]any) {
	t.Helper()
	root := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	if root == "" || v == nil {
		return
	}
	run := v["run"].(map[string]any)
	raw, _ := json.MarshalIndent(v, "", "  ")
	requireListening(t, os.WriteFile(filepath.Join(root, "run-"+run["id"].(string)+".json"), raw, 0600))
	assets := []string{run["input_asset_id"].(string)}
	for _, field := range []string{"output_asset_ids", "support_asset_ids"} {
		assets = append(assets, diagnosticArrayIDs(run[field])...)
	}
	for _, id := range diagnosticArrayIDs(run["receipt_ids"]) {
		d, err := f.s.Store.ReadDocument(context.Background(), id)
		requireListening(t, err)
		requireListening(t, os.WriteFile(filepath.Join(root, "receipt-"+id+".json"), d.Payload, 0600))
		var r map[string]any
		requireListening(t, json.Unmarshal(d.Payload, &r))
		var copied bytes.Buffer
		requireListening(t, f.s.Store.LabCommand(context.Background(), bytes.NewBuffer(sourceBytes(map[string]any{"action": "diagnostic-read", "id": r["operation_id"]})), &copied))
		requireListening(t, os.WriteFile(filepath.Join(root, "diagnostic-"+r["operation_id"].(string)+".json"), copied.Bytes(), 0600))
		for _, field := range []string{"wire_request_asset_id", "wire_response_asset_id", "context_snapshot_id"} {
			assets = append(assets, r[field].(string))
		}
	}
	for _, id := range assets {
		raw, err := f.s.Store.ReadAsset(context.Background(), id)
		requireListening(t, err)
		requireListening(t, os.WriteFile(filepath.Join(root, "asset-"+id+".json"), raw, 0600))
	}
}
func diagnosticRun(t *testing.T, f listeningFixture, methods ...string) map[string]any {
	t.Helper()
	v, err := f.s.MeasureCase(context.Background(), diagnosticRequest(f, methods...), uuid.NewString(), nil)
	diagnosticEvidence(t, f, v)
	if err != nil {
		t.Fatal(v, err)
	}
	return v
}

func TestNativeDiagnosticPersistencePositive(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	before, err := f.s.Store.ReadDocument(context.Background(), f.id)
	requireListening(t, err)
	v := diagnosticRun(t, f, "ffmpeg-ebur128-v1")
	run := v["run"].(map[string]any)
	if *calls != 1 || run["status"] != "complete" || len(v["measurements"].([]map[string]any)) != 1 {
		t.Fatal(v, *calls)
	}
	rows, err := f.s.Store.reviewMeasurements(context.Background(), f.id)
	requireListening(t, err)
	if len(rows) != 1 {
		t.Fatal(rows)
	}
	after, err := f.s.Store.ReadDocument(context.Background(), f.id)
	requireListening(t, err)
	if string(before.Payload) != string(after.Payload) {
		t.Fatal("advisory diagnostics changed key")
	}
	listed, err := f.s.Store.listAudioDiagnostics(context.Background(), f.id, "")
	requireListening(t, err)
	if len(listed["items"].([]any)) != 1 || *calls != 1 {
		t.Fatal(listed, *calls)
	}
	var contexts, receipts int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='provider-receipt' AND payload->>'context_snapshot_id' IS NOT NULL").Scan(&contexts))
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='provider-receipt'").Scan(&receipts))
	if contexts != 1 || receipts != 1 {
		t.Fatal(contexts, receipts)
	}
}
func TestNativeDiagnosticReplayPositive(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	key := uuid.NewString()
	request := diagnosticRequest(f, "ffmpeg-ebur128-v1")
	a, err := f.s.MeasureCase(context.Background(), request, key, nil)
	requireListening(t, err)
	f.s.SpeechURL = "http://unavailable.invalid"
	b, err := f.s.MeasureCase(context.Background(), request, key, nil)
	requireListening(t, err)
	if a["run"].(map[string]any)["id"] != b["run"].(map[string]any)["id"] || *calls != 1 {
		t.Fatal(a, b, *calls)
	}
}
func TestNativeDiagnosticFailedHistoryNegative(t *testing.T) {
	f, calls := diagnosticFixture(t, "failure")
	key := uuid.NewString()
	request := diagnosticRequest(f, "ffmpeg-ebur128-v1")
	for i := 0; i < 2; i++ {
		v, err := f.s.MeasureCase(context.Background(), request, key, nil)
		if err == nil || v["run"].(map[string]any)["status"] != "failed" {
			t.Fatal(v, err)
		}
	}
	if *calls != 1 {
		t.Fatal("failed replay dispatched again", *calls)
	}
	listed, err := f.s.Store.listAudioDiagnostics(context.Background(), f.id, "")
	requireListening(t, err)
	if len(listed["items"].([]any)) != 1 {
		t.Fatal(listed)
	}
}
func TestNativeDiagnosticOutputClockNegative(t *testing.T) {
	f, calls := diagnosticFixture(t, "clock")
	v, err := f.s.MeasureCase(context.Background(), diagnosticRequest(f, "ffmpeg-ebur128-v1"), uuid.NewString(), nil)
	if err == nil || *calls != 1 || len(v["run"].(map[string]any)["output_asset_ids"].([]any)) != 1 || len(v["run"].(map[string]any)["measurement_ids"].([]any)) != 0 {
		t.Fatal(v, err, *calls)
	}
}
func TestNativeDiagnosticOutputHashNegative(t *testing.T) {
	f, _ := diagnosticFixture(t, "hash")
	v, err := f.s.MeasureCase(context.Background(), diagnosticRequest(f, "ffmpeg-ebur128-v1"), uuid.NewString(), nil)
	if err == nil || v["run"].(map[string]any)["status"] != "failed" {
		t.Fatal(v, err)
	}
}
func TestNativeDiagnosticMissingObservationNegative(t *testing.T) {
	f, _ := diagnosticFixture(t, "missing")
	v, err := f.s.MeasureCase(context.Background(), diagnosticRequest(f, "ffmpeg-ebur128-v1"), uuid.NewString(), nil)
	if err == nil || v["run"].(map[string]any)["status"] != "failed" {
		t.Fatal(v, err)
	}
}
func TestNativeDiagnosticRequestHashNegative(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	r := diagnosticRequest(f, "ffmpeg-ebur128-v1")
	r.AudioSHA = strings.Repeat("0", 64)
	key := uuid.NewString()
	for i := 0; i < 2; i++ {
		_, err := f.s.MeasureCase(context.Background(), r, key, nil)
		if !errors.Is(err, ErrRevision) || *calls != 0 {
			t.Fatal(err, *calls)
		}
	}
	var active int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM operation WHERE operation_name='speech_measure' AND state='running'").Scan(&active))
	if active != 0 {
		t.Fatal("invalid preflight consumed foreground claim", active)
	}
}
func TestNativeDiagnosticUnknownMethodNegative(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	_, err := f.s.MeasureCase(context.Background(), diagnosticRequest(f, "invented-method"), uuid.NewString(), nil)
	if err == nil || *calls != 0 {
		t.Fatal(err, *calls)
	}
}
func TestNativeDiagnosticUnrelatedReadNegative(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	diagnosticRun(t, f, "ffmpeg-ebur128-v1")
	rows, err := f.s.Store.reviewMeasurements(context.Background(), uuid.NewString())
	requireListening(t, err)
	if len(rows) != 0 || *calls != 1 {
		t.Fatal(rows, *calls)
	}
}
func diagnosticConfiguration(t *testing.T, f listeningFixture, p any, include bool) (map[string]any, error) {
	t.Helper()
	c, rev, err := f.s.Store.Configuration(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	if include {
		c["audio_diagnostic_profile"] = p
	} else {
		delete(c, "audio_diagnostic_profile")
	}
	raw, _ := json.Marshal(c)
	c, _, err = f.s.Store.PutConfiguration(context.Background(), raw, uuid.NewString(), rev)
	return c, err
}
func TestNativeDiagnosticPromptConfigurationPositive(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	p := audioDiagnosticDefaults()["profiles"].([]any)[1].(map[string]any)
	c, err := diagnosticConfiguration(t, f, p, true)
	requireListening(t, err)
	saved := c["audio_diagnostic_profile"].(map[string]any)
	id := saved["prompt_asset_id"].(string)
	if id == "builtin-audio-judge-v1" {
		t.Fatal("builtin prompt not materialized")
	}
	raw, err := f.s.Store.ReadAsset(context.Background(), id)
	requireListening(t, err)
	if string(raw) != string(audioJudgePrompt) {
		t.Fatal("wrong prompt")
	}
	c, err = diagnosticConfiguration(t, f, nil, false)
	requireListening(t, err)
	if c["audio_diagnostic_profile"].(map[string]any)["prompt_asset_id"] != id || *calls != 0 {
		t.Fatal(c, *calls)
	}
	c, err = diagnosticConfiguration(t, f, nil, true)
	requireListening(t, err)
	if c["audio_diagnostic_profile"] != nil {
		t.Fatal("explicit disable ignored", c)
	}
}
func TestNativeDiagnosticPromptHashNegative(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	p := audioDiagnosticDefaults()["profiles"].([]any)[1].(map[string]any)
	p["prompt_sha256"] = strings.Repeat("0", 64)
	_, err := diagnosticConfiguration(t, f, p, true)
	if !errors.Is(err, ErrReference) || *calls != 0 {
		t.Fatal(err, *calls)
	}
}
func TestNativeDiagnosticHTTPPositive(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	raw, _ := json.Marshal(diagnosticRequest(f, "ffmpeg-ebur128-v1"))
	w := f.request("POST", "/api/v1/cases/"+f.id+"/measurements", string(raw), uuid.NewString(), "")
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	w = f.request("GET", "/api/v1/cases/"+f.id+"/measurements", "", "", "")
	if w.Code != 200 || !strings.Contains(w.Body.String(), "-18.25") || *calls != 1 {
		t.Fatal(w.Code, w.Body.String(), *calls)
	}
}
func TestNativeDiagnosticHTTPIdentityNegative(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	raw, _ := json.Marshal(diagnosticRequest(f, "ffmpeg-ebur128-v1"))
	w := f.request("POST", "/api/v1/cases/"+uuid.NewString()+"/measurements", string(raw), uuid.NewString(), "")
	if w.Code != 400 || *calls != 0 {
		t.Fatal(w.Code, w.Body.String(), *calls)
	}
}
func TestNativeDiagnosticDeletionPositive(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	v := diagnosticRun(t, f, "ffmpeg-ebur128-v1")
	run := v["run"].(map[string]any)
	p, err := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{f.id}})
	requireListening(t, err)
	wanted := map[string]bool{run["id"].(string): false, run["measurement_ids"].([]any)[0].(string): false}
	for _, id := range p.Documents {
		if _, ok := wanted[id]; ok {
			wanted[id] = true
		}
	}
	for id, found := range wanted {
		if !found {
			t.Fatal("diagnostic omitted from erasure", id, p)
		}
	}
	p, err = f.s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest)
	requireListening(t, err)
	if p.State != "native_erased" || p.LabCleanup != "pending_explicit_local_lab_cleanup" || *calls != 1 {
		t.Fatal(p, *calls)
	}
	for id := range wanted {
		var count int
		requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE id=$1", id).Scan(&count))
		if count != 0 {
			t.Fatal("diagnostic survived native deletion", id)
		}
	}
}
func TestNativeDiagnosticNativeMethodsPositive(t *testing.T) {
	f := listeningCase(t)
	f.s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	f.s.speechToken = "actual-local-speech-test"
	v := diagnosticRun(t, f, "ffmpeg-ebur128-v1", "praat-ac-v1")
	if len(v["measurements"].([]map[string]any)) != 13 {
		t.Fatal(v)
	}
	raw, _ := json.MarshalIndent(v, "", "  ")
	if root := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE"); root != "" {
		requireListening(t, os.WriteFile(filepath.Join(root, "actual-measurements.json"), raw, 0600))
	}
}

// This fixture performs actual Kokoro decoding, then publishes its actual new
// WAV through the regular key/admission/publication owners. No reference audio
// or diagnostic result is supplied to the recognizer.
func diagnosticActualCase(t *testing.T) listeningFixture {
	t.Helper()
	f := listeningCase(t)
	f.s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	f.s.speechToken = "actual-local-speech-test"
	packet := map[string]any{"profile": map[string]any{"provider": "local_kokoro", "billing_mode": "local", "voices": []any{map[string]any{"id": "af_heart", "locale": "en-US"}}}, "turn": map[string]any{"voice_id": "af_heart", "locale": "en-US", "operations": []any{map[string]any{"kind": "text", "text": "Hello world."}}}}
	result, err := f.s.speechCall(context.Background(), "/internal/v1/piece", packet, nil)
	requireListening(t, err)
	audio, err := base64.StdEncoding.DecodeString(result["audio_base64"].(string))
	requireListening(t, err)
	asset, err := f.s.saveAudioBytes(context.Background(), audio)
	requireListening(t, err)
	b := preparationBlueprint(t, 1)
	_, _, candidate, _ := mutationFixture()
	candidate["utterances"].([]any)[0].(map[string]any)["canonical_text"] = "Hello world."
	candidate["utterances"].([]any)[0].(map[string]any)["surface_text"] = "Hello world."
	candidate["planned_units"] = []any{}
	frozen := map[string]any{"plan": map[string]any{"case_version_id": "actual-diagnostic-input"}, "pieces": []any{map[string]any{"utterance_id": "u1", "gap_after_ms": float64(0)}}}
	progress := map[string]any{"pieces": []any{map[string]any{"utterance_id": "u1", "sample_count": result["sample_count"], "receipt_ids": []any{}}}}
	key := projectSpeechKey(map[string]any{"blueprint": b, "configuration": DefaultConfiguration()}, candidate, frozen, progress, asset.ID, asset.SHA, "2.0.0")
	source, err := f.s.Store.saveGroundTruth(context.Background(), key)
	requireListening(t, err)
	tx, err := beginWrite(context.Background(), f.s.Store)
	requireListening(t, err)
	defer tx.Rollback(context.Background())
	id, err := f.s.Store.publishListeningCase(context.Background(), tx, source, b["task_components"].(map[string]any), "Actual audio diagnostic", "monologue")
	requireListening(t, err)
	requireListening(t, tx.Commit(context.Background()))
	if root := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE"); root != "" {
		requireListening(t, os.WriteFile(filepath.Join(root, "actual-diagnostic.wav"), audio, 0600))
	}
	return listeningFixture{s: f.s, id: id, sha: key["case_sha256"].(string), audioSHA: asset.SHA, audio: audio, key: key}
}
func TestNativeDiagnosticActualASRPositive(t *testing.T) {
	f := diagnosticActualCase(t)
	diagnosticCapture(t, f)
	v := diagnosticRun(t, f, "faster-whisper-local-en-v1")
	rows := v["measurements"].([]map[string]any)
	if len(rows) != 1 || rows[0]["feature"] != "WER" || rows[0]["numeric_value"] != "0" {
		t.Fatal("Independent Hello world transcription disagreed with literal reference", v)
	}
	run := v["run"].(map[string]any)
	output, err := f.s.Store.ReadAsset(context.Background(), run["output_asset_ids"].([]any)[0].(string))
	requireListening(t, err)
	var raw map[string]any
	requireListening(t, json.Unmarshal(output, &raw))
	native := raw["native"].(map[string]any)
	if text := strings.TrimSpace(native["hypothesis"].(string)); text != "Hello world." && text != "Hello, world." {
		t.Fatal("unexpected raw transcription", text)
	}
	params := native["parameters"].(map[string]any)
	if params["initial_prompt"] != nil || params["condition_on_previous_text"] != false || params["word_timestamps"] != true || len(native["segments"].([]any)) == 0 {
		t.Fatal(native)
	}
	if root := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE"); root != "" {
		requireListening(t, os.WriteFile(filepath.Join(root, "actual-asr.json"), output, 0600))
	}
}

func TestNativeReleaseWordCountsPositive(t *testing.T) {
	s, p, _ := nativeSpeechFixture(t, 0)
	saved, err := s.Store.Preparation(context.Background(), p["id"].(string))
	requireListening(t, err)
	summary := speechSummary(saved)
	if summary["canonical_word_count"] != float64(4) || summary["surface_word_count"] != float64(4) {
		t.Fatal("actual admitted word counts not retained", summary)
	}
}

func TestNativeDiagnosticRightsNegative(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	_, err := f.s.Store.DB.Exec(context.Background(), "UPDATE exercise_catalog SET availability='rights_restricted' WHERE id::text=$1", f.id)
	requireListening(t, err)
	_, err = f.s.MeasureCase(context.Background(), diagnosticRequest(f, "ffmpeg-ebur128-v1"), uuid.NewString(), nil)
	if !errors.Is(err, ErrAttemptRights) || *calls != 0 {
		t.Fatal(err, *calls)
	}
}
func TestNativeDiagnosticCancellationNegative(t *testing.T) {
	f := listeningCase(t)
	entered := make(chan struct{})
	done := make(chan struct{})
	endpoint := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		close(entered)
		select {
		case <-r.Context().Done():
		case <-done:
		}
	}))
	defer endpoint.Close()
	defer close(done)
	f.s.SpeechURL = endpoint.URL
	f.s.speechToken = "cancel-owned"
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go func() {
		select {
		case <-entered:
			cancel()
		case <-time.After(10 * time.Second):
			cancel()
		}
	}()
	v, err := f.s.MeasureCase(ctx, diagnosticRequest(f, "ffmpeg-ebur128-v1"), uuid.NewString(), nil)
	diagnosticEvidence(t, f, v)
	if !errors.Is(err, context.Canceled) || v == nil {
		t.Fatal(v, err)
	}
	run := v["run"].(map[string]any)
	if run["status"] != "failed" || run["failure_code"] != "CANCELLED" || len(run["receipt_ids"].([]any)) != 1 {
		t.Fatal(v)
	}
	listed, err := f.s.Store.listAudioDiagnostics(context.Background(), f.id, "")
	requireListening(t, err)
	if len(listed["items"].([]any)) != 1 {
		t.Fatal(listed)
	}
}
func TestNativeDiagnosticPaginationPositive(t *testing.T) {
	f, calls := diagnosticFixture(t, "")
	for i := 0; i < 21; i++ {
		diagnosticRun(t, f, "ffmpeg-ebur128-v1")
	}
	first, err := f.s.Store.listAudioDiagnostics(context.Background(), f.id, "")
	requireListening(t, err)
	cursor, ok := first["next_cursor"].(string)
	if !ok || len(first["items"].([]any)) != 20 {
		t.Fatal(first)
	}
	last, err := f.s.Store.listAudioDiagnostics(context.Background(), f.id, cursor)
	requireListening(t, err)
	if len(last["items"].([]any)) != 1 || last["next_cursor"] != nil || *calls != 21 {
		t.Fatal(last, *calls)
	}
	seen := map[string]bool{}
	for _, page := range []map[string]any{first, last} {
		for _, v := range page["items"].([]any) {
			id := v.(map[string]any)["run"].(map[string]any)["id"].(string)
			if seen[id] {
				t.Fatal("repeated history row", id)
			}
			seen[id] = true
		}
	}
}

// Constructed model annotations exercise actual admission, transaction and
// readback. No upstream model call or acoustic accuracy is claimed.
func diagnosticAnnotationFixture(t *testing.T, status string) (listeningFixture, map[string]any, Asset) {
	t.Helper()
	f := listeningCase(t)
	target := f.key["units"].([]any)[0].(map[string]any)["id"]
	finding := map[string]any{"unit_id": target, "feature": "speech_realization", "status": status, "description": "Constructed target description.", "reason": "Constructed advisory explanation.", "clip_interval": nil, "proposed_ipa": nil, "model_annotation": map[string]any{"note": "Uncalibrated model commentary.", "source_asset_id": "model-local-annotation", "native_score": 99}}
	output, err := f.s.Store.saveProviderBytes(context.Background(), sourceBytes(finding), "provider_output")
	requireListening(t, err)
	row := map[string]any{"id": uuid.NewString(), "audio_sha256": f.audioSHA, "method_id": "qwen25-omni-audio-v1", "method_version": "constructed-annotation-v1", "feature": "speech_realization", "interval": map[string]any{"start": 0, "end": 24000, "sample_rate_hz": 24000}, "status": "observed", "numeric_value": nil, "categorical_value": "model_supported", "unit": "category", "evidence_asset_ids": []any{output.ID}, "reason": nil, "target_unit_id": target, "auditory_finding": finding}
	return f, row, output
}

func TestNativeDiagnosticExtraAnnotationPositive(t *testing.T) {
	f, row, output := diagnosticAnnotationFixture(t, "supported")
	ctx := context.Background()
	input, err := f.s.Store.saveProviderBytes(ctx, []byte(`{"origin":"constructed_annotation_fixture"}`), "provider_input")
	requireListening(t, err)
	op, err := f.s.Store.ReserveOperation(ctx, OperationRequest{Name: "speech_measure", Key: uuid.NewString(), Path: "/test/annotation", Body: []byte(`{}`)})
	requireListening(t, err)
	requireListening(t, f.s.Store.claimInference(ctx, op.ID))
	defer f.s.Store.releaseInference(ctx, op.ID)
	run := map[string]any{"schema_version": "2.0.0", "id": uuid.NewString(), "case_version_id": f.id, "operation_id": op.ID, "status": "complete", "method_ids": []any{"qwen25-omni-audio-v1"}, "input_asset_id": input.ID, "output_asset_ids": []any{output.ID}, "support_asset_ids": []any{}, "receipt_ids": []any{}, "measurement_ids": []any{}, "failure_code": nil}
	_, err = f.s.Store.finishAudioDiagnostic(ctx, op, run, []map[string]any{row})
	requireListening(t, err)
	rows, err := f.s.Store.reviewMeasurements(ctx, f.id)
	requireListening(t, err)
	if len(rows) != 1 {
		t.Fatal(rows)
	}
	var saved map[string]any
	requireListening(t, json.Unmarshal(rows[0].(json.RawMessage), &saved))
	annotation := saved["auditory_finding"].(map[string]any)["model_annotation"].(map[string]any)
	if saved["numeric_value"] != nil || annotation["source_asset_id"] != "model-local-annotation" || annotation["native_score"] != float64(99) {
		t.Fatal("Annotation was lost or became a native score", saved)
	}
	var links int
	requireListening(t, f.s.Store.DB.QueryRow(ctx, "SELECT count(*) FROM object_reference WHERE source_document_id=$1 AND source_pointer LIKE '/auditory_finding/%'", row["id"]).Scan(&links))
	if links != 0 {
		t.Fatal("Model-local IDs became native resource links", links)
	}
	out := map[string]any{"schema_version": "2.0.0", "findings": []any{row["auditory_finding"]}, "summary": "Constructed advisory output.", "model_annotation": "Uncalibrated root commentary."}
	_, _, err = contracts.Validate("audio-judge-output", "2.0.0", sourceBytes(out))
	requireListening(t, err)
}

func TestNativeDiagnosticAmbiguousJudgmentNegative(t *testing.T) {
	f, row, output := diagnosticAnnotationFixture(t, "supported or contradicted")
	_, _, err := f.s.Store.diagnosticDocument(context.Background(), row["id"].(string), "audio-measurement", row, map[string]string{"/evidence_asset_ids/0": output.ID})
	if err == nil {
		t.Fatal("An ambiguous judgment acquired a canonical status")
	}
	var count int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE id=$1", row["id"]).Scan(&count))
	if count != 0 {
		t.Fatal("Rejected measurement was published", count)
	}
}

func TestNativeDiagnosticModelReferenceNegative(t *testing.T) {
	f, row, output := diagnosticAnnotationFixture(t, "supported")
	row["auditory_finding"].(map[string]any)["model_annotation"].(map[string]any)["source_asset_id"] = output.ID
	refs := map[string]string{"/evidence_asset_ids/0": output.ID, "/auditory_finding/model_annotation/source_asset_id": output.ID}
	_, _, err := f.s.Store.diagnosticDocument(context.Background(), row["id"].(string), "audio-measurement", row, refs)
	if err == nil {
		t.Fatal("Model inference acquired a native resource reference")
	}
}

// Positive and negative use actual generated recordings. The negative key is
// deliberately constructed with unfulfilled pause intent and the real clean
// source recording; it never rewrites a published case or invents acoustic gold.
func actualAuditoryFixture(t *testing.T, absent bool) (listeningFixture, string) {
	s, p := nativeAcousticFixture(t, "pause_insert")
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	var id string
	requireListening(t, s.Store.DB.QueryRow(context.Background(), "SELECT case_version_id FROM listening_case WHERE source_key_id=$1", p["key_id"]).Scan(&id))
	doc, err := s.Store.ReadDocument(context.Background(), id)
	requireListening(t, err)
	var key map[string]any
	requireListening(t, json.Unmarshal(doc.Payload, &key))
	audio := key["audio"].(map[string]any)
	f := listeningFixture{s: s, id: id, key: key, audioSHA: audio["sha256"].(string)}

	if absent {
		frozen, err := s.Store.diagnosticInputs(context.Background(), diagnosticRequest(f, "qwen25-omni-audio-v1"))
		requireListening(t, err)
		piece := frozen.Progress["pieces"].([]any)[0].(map[string]any)
		clean, err := s.Store.ReadAsset(context.Background(), piece["source_asset_id"].(string))
		requireListening(t, err)
		asset, err := s.saveAudioBytes(context.Background(), clean)
		requireListening(t, err)
		key = reviewClone(key)
		n := (len(clean) - 44) / 2
		duration := float64((n + 23) / 24)
		key["audio"].(map[string]any)["asset_id"] = asset.ID
		key["audio"].(map[string]any)["sha256"] = asset.SHA
		key["audio"].(map[string]any)["duration_ms"] = duration
		for _, value := range key["utterances"].([]any) {
			value.(map[string]any)["audio_interval"] = map[string]any{"start_ms": float64(0), "end_ms": duration}
		}
		for _, value := range key["units"].([]any) {
			u := value.(map[string]any)
			u["audio_intervals"] = []any{map[string]any{"start_ms": float64(0), "end_ms": duration}}
			u["evidence_ids"] = []any{}
		}
		content := map[string]any{}
		for _, field := range []string{"public_context", "variety_policy", "audio", "speakers", "utterances", "units", "taxonomy_version", "verification_policy_version"} {
			content[field] = key[field]
		}
		key["case_sha256"] = lab.Hash(content)
		source, err := s.Store.saveGroundTruth(context.Background(), key)
		requireListening(t, err)
		tx, err := beginWrite(context.Background(), s.Store)
		requireListening(t, err)
		defer tx.Rollback(context.Background())
		id, err = s.Store.publishListeningCase(context.Background(), tx, source, preparationBlueprint(t, 1)["task_components"].(map[string]any), "Constructed missing-pause diagnostic contrast", "monologue")
		requireListening(t, err)
		requireListening(t, tx.Commit(context.Background()))
		saved, err := s.Store.ReadDocument(context.Background(), id)
		requireListening(t, err)
		requireListening(t, json.Unmarshal(saved.Payload, &key))
		f = listeningFixture{s: s, id: id, key: key, audioSHA: asset.SHA}
	}
	profile := audioDiagnosticDefaults()["profiles"].([]any)[1].(map[string]any)
	profile["compute_type"] = "float32"
	profile["repetition_penalty"] = 1.0
	delete(profile, "quantization_engine")
	method := "qwen25-omni-audio-v1"
	if path := os.Getenv("TANGERINE_AUDIO_JUDGE_TEST_PROFILE"); path != "" {
		raw, err := os.ReadFile(path)
		requireListening(t, err)
		profile = nil
		requireListening(t, json.Unmarshal(raw, &profile))
		if profile["provider"] != "gemini_interactions" || profile["billing_mode"] != "free_tier" {
			t.Fatal("The selected hosted qualification must use the approved Gemini free-tier binding")
		}
		method = "gemini-audio-v1"
	}
	_, err = diagnosticConfiguration(t, f, profile, true)
	requireListening(t, err)
	return f, method
}
func TestNativeDiagnosticActualAuditoryPositive(t *testing.T) {
	f, method := actualAuditoryFixture(t, false)
	v := diagnosticRun(t, f, method)
	assertActualAuditory(t, f, v, "pause_insert", "supported", 2)
}
func TestNativeDiagnosticActualAuditoryContrastNegative(t *testing.T) {
	f, method := actualAuditoryFixture(t, true)
	v := diagnosticRun(t, f, method)
	assertActualAuditory(t, f, v, "speech_realization", "contradicted", 1)
}
func assertActualAuditory(t *testing.T, f listeningFixture, v map[string]any, expectedFeature, expectedStatus string, expectedClips int) {
	t.Helper()
	s := f.s
	rows := v["measurements"].([]map[string]any)
	if len(rows) == 0 {
		t.Fatal("actual judge omitted every selected target", v)
	}
	for _, r := range rows {
		if r["numeric_value"] != nil || r["unit"] != "category" {
			t.Fatal("auditory inference invented native numeric scores", r)
		}
	}
	run := v["run"].(map[string]any)
	raw, err := s.Store.ReadAsset(context.Background(), run["output_asset_ids"].([]any)[0].(string))
	requireListening(t, err)
	var result map[string]any
	requireListening(t, json.Unmarshal(raw, &result))
	wire := result["wire"].(map[string]any)
	actualFindings := 0
	for _, row := range rows {
		if row["auditory_finding"] != nil {
			actualFindings++
		}
	}
	if actualFindings == 0 {
		t.Fatal("no actual model finding; native unknowns do not qualify inference", result)
	}
	if wire["provider"] == "local_qwen25_omni" {
		parameters := wire["parameters"].(map[string]any)
		if parameters["compute_type"] != "float32" || parameters["dtype"] != "float32" || parameters["attention"] != "sdpa" || parameters["audio_attention"] != "sdpa" || parameters["repetition_penalty"] != 1.0 || parameters["quantized_linear_modules"].(float64) != 0 {
			t.Fatal("Selected unquantized float32/SDPA inference was not realized", parameters)
		}
		if wire["provider"] != "local_qwen25_omni" || len(wire["model_visible_calls"].([]any)) == 0 || len(wire["input_audio"].([]any)) != expectedClips {
			t.Fatal("missing actual target/reference/model call", wire)
		}
		if len(run["support_asset_ids"].([]any)) < expectedClips {
			t.Fatal("paired reference not durably retained", run)
		}
		loading := wire["checkpoint_loading"].(map[string]any)
		if len(loading["missing_keys"].([]any)) != 0 || len(loading["mismatched_keys"].([]any)) != 0 {
			t.Fatal("Checkpoint initialization differs from declared Thinker", loading)
		}
	} else if wire["provider"] == "gemini_interactions" {
		request := wire["request"].(map[string]any)
		profile := wire["profile"].(map[string]any)
		if wire["http_status"] != float64(200) || profile["billing_mode"] != "free_tier" || request["model"] != profile["model"] || request["store"] != false || request["stream"] != false || request["background"] != false {
			t.Fatal("Approved stateless free-tier binding was not realized", wire)
		}
		clips := 0
		for _, value := range request["input"].([]any) {
			part := value.(map[string]any)
			if part["type"] == "audio" {
				clips++
				if part["mime_type"] != "audio/wav" || part["data"] == "" {
					t.Fatal("Actual audio is missing", part)
				}
			}
		}
		if clips != expectedClips || len(run["support_asset_ids"].([]any)) < expectedClips {
			t.Fatal("Missing actual target/reference", clips, run)
		}
	} else {
		t.Fatal("Unexpected auditory provider", wire["provider"])
	}
	actual := 0
	for _, value := range result["output"].(map[string]any)["findings"].([]any) {
		finding := value.(map[string]any)
		if finding["unit_id"] == "e1" && finding["feature"] == expectedFeature {
			actual++
			if finding["status"] != expectedStatus {
				t.Fatal("actual audio contrast judgment differs from independent expected presence/absence", finding, expectedStatus)
			}
		}
	}
	if actual == 0 {
		t.Fatal("model supplied no actual requested contrast judgment", result["output"])
	}

}

func diagnosticCapture(t *testing.T, f listeningFixture) {
	t.Helper()
	c, rev, err := f.s.Store.Configuration(context.Background())
	requireListening(t, err)
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	c["llm_lab_capture_content"], c["llm_lab_trace_enabled"] = true, true
	_, _, err = f.s.Store.PutConfiguration(context.Background(), sourceBytes(c), uuid.NewString(), rev)
	requireListening(t, err)
}

func TestNativeReleaseMutationLocatorPositive(t *testing.T) {
	s, r, client, calls, _ := nativeMutationFixture(t, "unique-locator")
	p, err := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	requireListening(t, err)
	if *calls != 1 {
		t.Fatal("literal arithmetic caused another model call", *calls)
	}
	raw, err := s.Store.ReadAsset(context.Background(), p["mutation_manifest_asset_id"].(string))
	requireListening(t, err)
	var c map[string]any
	requireListening(t, json.Unmarshal(raw, &c))
	span := projectedSpan(c)
	if span["start_cp"] != float64(9) || span["end_cp"] != float64(13) {
		t.Fatal(span)
	}
	saveNativeMutationEvidence(t, s, p)
}

func TestNativeReleaseMutationShapePositive(t *testing.T) {
	s, r, client, calls, _ := nativeMutationFixture(t, "shape-defaults")
	p, err := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	requireListening(t, err)
	if *calls != 1 {
		t.Fatal("empty shape defaults caused another model call", *calls)
	}
	raw, err := s.Store.ReadAsset(context.Background(), p["mutation_manifest_asset_id"].(string))
	requireListening(t, err)
	var c map[string]any
	requireListening(t, json.Unmarshal(raw, &c))
	u := c["planned_units"].([]any)[0].(map[string]any)
	if len(u["rationale_forbidden_propositions"].([]any)) != 0 || u["corrections"].([]any)[0].(map[string]any)["canonical"] != true || u["rationale"] != "A singular subject requires singular agreement." {
		t.Fatal(c)
	}
}

func TestNativeReleaseConservativeContextPositive(t *testing.T) {
	s, r, client, calls, _ := nativeMutationFixture(t, "token-unknown-fit")
	p, err := s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
	requireListening(t, err)
	if *calls != 1 || p["phase_states"].(map[string]any)["mutation"] != "complete" {
		t.Fatal(p, *calls)
	}
}
