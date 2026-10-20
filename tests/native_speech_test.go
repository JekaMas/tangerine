package app

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/provider"
	"testing"
	"time"
)

// Constructed transport packets only. PostgreSQL/MinIO/CAS/receipts/playback are real;
// actual Kokoro/eSpeak and model/Lab observations are separate recorded cases.
func nativeSpeechFixture(t *testing.T, fail int) (*Server, map[string]any, *int) {
	t.Helper()
	return nativeSpeechFixtureMode(t, fail, false)
}
func nativeSpeechFixtureMode(t *testing.T, fail int, live bool) (*Server, map[string]any, *int) {
	t.Helper()
	mode := ""
	if live {
		mode = "speech-live"
	}
	s, r, c, _, _ := nativeMutationFixture(t, mode)
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	calls := 0
	endpoint := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		if req.Header.Get("Authorization") != "Bearer speech-test-token" {
			t.Error("private token absent")
		}
		var packet map[string]any
		if e := json.NewDecoder(req.Body).Decode(&packet); e != nil {
			t.Fatal(e)
		}
		w.Header().Set("Content-Type", "application/json")
		if req.URL.Path == "/internal/v1/plan" {
			turn := packet["plan"].(map[string]any)["turns"].([]any)[0].(map[string]any)
			first := map[string]any{}
			second := map[string]any{}
			for k, v := range turn {
				first[k] = v
				second[k] = v
			}
			first["operations"] = []any{map[string]any{"kind": "text", "text": "The café"}}
			first["gap_after_ms"] = 0
			second["operations"] = []any{map[string]any{"kind": "text", "text": " open tomorrow."}}
			_ = json.NewEncoder(w).Encode(map[string]any{"pieces": []any{first, second}, "model_context": map[string]any{"origin": "constructed_transport_fixture"}})
			return
		}
		if req.URL.Path == "/internal/v1/quality" {
			_ = json.NewEncoder(w).Encode(map[string]any{"origin": "constructed_transport_fixture", "warnings": []any{}})
			return
		}
		calls++
		if fail == calls {
			w.WriteHeader(429)
			_ = json.NewEncoder(w).Encode(map[string]any{"error": "PROVIDER_QUOTA"})
			return
		}
		turn := packet["turn"].(map[string]any)
		if turn["voice_id"] != "af_heart" || turn["locale"] != "en-US" {
			t.Error("voice changed", turn)
		}
		audio := speechWAV([]byte{7, 0, 8, 0, 9, 0})
		_ = json.NewEncoder(w).Encode(map[string]any{"audio_base64": base64.StdEncoding.EncodeToString(audio), "sample_count": 3, "receipt": map[string]any{"origin": "constructed_transport_fixture"}})
	}))
	t.Cleanup(endpoint.Close)
	s.SpeechURL = endpoint.URL
	s.speechToken = "speech-test-token"
	return s, p, &calls
}
func renderNative(t *testing.T, s *Server, p map[string]any, key string, attempt int) map[string]any {
	t.Helper()
	v, e := s.RenderPreparation(context.Background(), p["id"].(string), key, attempt, nil)
	if e != nil {
		t.Fatal(v, e)
	}
	return v
}
func speechProgress(t *testing.T, s *Server, p map[string]any) map[string]any {
	t.Helper()
	raw, e := s.Store.ReadAsset(context.Background(), p["render_progress_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var d map[string]any
	_ = json.Unmarshal(raw, &d)
	return d
}
func TestNativeSpeechCheckpointPositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	p = renderNative(t, s, p, uuid.NewString(), 1)
	if *calls != 2 || p["phase_states"].(map[string]any)["render"] != "complete" {
		t.Fatal(p, *calls)
	}
	audio, e := s.Store.ReadAsset(context.Background(), p["audio_asset_id"].(string))
	if e != nil || len(audio) != 44+12+12000 || string(audio[44:50]) != string([]byte{7, 0, 8, 0, 9, 0}) {
		t.Fatal(len(audio), e)
	}
	progress := speechProgress(t, s, p)
	if progress["assembled_asset_id"] != p["audio_asset_id"] || progress["sample_map_asset_id"] == nil {
		t.Fatal(progress)
	}
}
func TestNativeSpeechCasePositive(t *testing.T) {
	s, p, _ := nativeSpeechFixture(t, 0)
	p = renderNative(t, s, p, uuid.NewString(), 1)
	var status string
	var audio string
	id := uuid.NewSHA1(uuid.NameSpaceOID, []byte(p["id"].(string)+":speech-case")).String()
	e := s.Store.DB.QueryRow(context.Background(), "SELECT state,d.payload->>'delivery_asset_id' FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id=$1", id).Scan(&status, &audio)
	if e != nil || status != "rendered" || audio != p["audio_asset_id"] {
		t.Fatal(status, audio, e)
	}
}
func TestNativeSpeechMissingMutationNegative(t *testing.T) {
	s, r, c, calls := prepareNativeFixture(t, "", 200)
	p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	if _, e = s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil); e == nil || *calls != 1 {
		t.Fatal(e, *calls)
	}
}
func TestNativeSpeechAttemptNegative(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	if _, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 2, nil); e == nil || *calls != 0 {
		t.Fatal(e, *calls)
	}
}
func TestNativeSpeechResumePositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 2)
	id := p["id"].(string)
	key := uuid.NewString()
	failed, e := s.RenderPreparation(context.Background(), id, key, 1, nil)
	if e == nil || *calls != 2 {
		t.Fatal(failed, e, *calls)
	}
	before := speechProgress(t, s, failed)
	first := before["pieces"].([]any)[0].(map[string]any)["asset_id"]
	if first == nil || before["pieces"].([]any)[1].(map[string]any)["state"] != "failed" {
		t.Fatal(before)
	}
	complete := renderNative(t, s, failed, uuid.NewString(), 2)
	after := speechProgress(t, s, complete)
	if *calls != 3 || after["pieces"].([]any)[0].(map[string]any)["asset_id"] != first {
		t.Fatal(*calls, after)
	}
	old, e := s.RenderPreparation(context.Background(), id, key, 1, nil)
	if e == nil || old["phase_states"].(map[string]any)["render"] != "failed" || *calls != 3 {
		t.Fatal(old, e, *calls)
	}
}
func TestNativeSpeechRestartPositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	key := uuid.NewString()
	p = renderNative(t, s, p, key, 1)
	restarted := *s
	restarted.Store = preparationNative(t)
	restarted.SpeechURL = "http://unreachable.invalid"
	saved := renderNative(t, &restarted, p, key, 1)
	if saved["audio_asset_id"] != p["audio_asset_id"] || *calls != 2 {
		t.Fatal(saved, *calls)
	}
}
func TestNativeSpeechKeyConflictNegative(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	key := uuid.NewString()
	p = renderNative(t, s, p, key, 1)
	if _, e := s.RenderPreparation(context.Background(), p["id"].(string), key, 2, nil); !errors.Is(e, ErrConflict) || *calls != 2 {
		t.Fatal(e, *calls)
	}
}
func TestNativeSpeechDeadlineNegative(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, e := s.RenderPreparation(ctx, p["id"].(string), uuid.NewString(), 1, nil); e == nil || *calls != 0 {
		t.Fatal(e, *calls)
	}
}
func TestNativeSpeechPlaybackPositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	p = renderNative(t, s, p, uuid.NewString(), 1)
	id := p["id"].(string)
	for i := 0; i < 2; i++ {
		r := httptest.NewRequest("GET", "/audio", nil)
		r.SetPathValue("id", id)
		w := httptest.NewRecorder()
		s.speechPlayback(w, r)
		if w.Code != 200 || w.Header().Get("Content-Type") != "audio/wav" || len(w.Body.Bytes()) != 12056 {
			t.Fatal(w.Code, w.Header(), w.Body.Len())
		}
	}
	if *calls != 2 {
		t.Fatal("playback synthesized", *calls)
	}
}
func TestNativeSpeechRangePositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	p = renderNative(t, s, p, uuid.NewString(), 1)
	r := httptest.NewRequest("GET", "/audio", nil)
	r.SetPathValue("id", p["id"].(string))
	r.Header.Set("Range", "bytes=44-49")
	w := httptest.NewRecorder()
	s.speechPlayback(w, r)
	if w.Code != 206 || w.Header().Get("Content-Range") != "bytes 44-49/12056" || string(w.Body.Bytes()) != string([]byte{7, 0, 8, 0, 9, 0}) || *calls != 2 {
		t.Fatal(w.Code, w.Header(), w.Body.Bytes(), *calls)
	}
}
func TestNativeSpeechUnreadyNegative(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	r := httptest.NewRequest("GET", "/audio", nil)
	r.SetPathValue("id", p["id"].(string))
	w := httptest.NewRecorder()
	s.speechPlayback(w, r)
	if w.Code != 409 || !strings.Contains(w.Body.String(), "AUDIO_NOT_READY") || *calls != 0 {
		t.Fatal(w.Code, w.Body.String(), *calls)
	}
}
func TestNativeSpeechUnknownNegative(t *testing.T) {
	s, _, calls := nativeSpeechFixture(t, 0)
	r := httptest.NewRequest("GET", "/audio", nil)
	r.SetPathValue("id", uuid.NewString())
	w := httptest.NewRecorder()
	s.speechPlayback(w, r)
	if w.Code != 404 || *calls != 0 {
		t.Fatal(w.Code, *calls)
	}
}
func TestNativeSpeechEvidencePositive(t *testing.T) {
	s, p, _ := nativeSpeechFixture(t, 0)
	p = renderNative(t, s, p, uuid.NewString(), 1)
	progress := speechProgress(t, s, p)
	for _, v := range progress["pieces"].([]any) {
		piece := v.(map[string]any)
		ids := piece["receipt_ids"].([]any)
		if len(ids) != 1 {
			t.Fatal(piece)
		}
		doc, e := s.Store.ReadDocument(context.Background(), ids[0].(string))
		if e != nil {
			t.Fatal(e)
		}
		var receipt map[string]any
		_ = json.Unmarshal(doc.Payload, &receipt)
		if receipt["stage"] != "tts" || receipt["context_snapshot_id"] == nil || receipt["outcome"] != "complete" {
			t.Fatal(receipt)
		}
		wire, err := s.Store.ReadAsset(context.Background(), receipt["wire_response_asset_id"].(string))
		if err != nil || !strings.HasSuffix(string(wire), "\n") || receipt["http_status"] != float64(200) {
			t.Fatal("original JSONEncoder response newline and actual HTTP status lost", string(wire), receipt["http_status"], err)
		}
	}
}
func TestNativeSpeechFrozenPositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 2)
	p, _ = s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	c, rev, e := s.Store.Configuration(context.Background())
	if e != nil {
		t.Fatal(e)
	}
	c["speech_profile"] = "azure-standard-en-v1"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	raw, _ := json.Marshal(c)
	if _, _, e = s.Store.PutConfiguration(context.Background(), raw, uuid.NewString(), rev); e != nil {
		t.Fatal(e)
	}
	p = renderNative(t, s, p, uuid.NewString(), 2)
	if *calls != 3 {
		t.Fatal(p, *calls)
	}
}
func TestNativeSpeechLeaseNegative(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	id := p["id"].(string)
	op, e := s.Store.ReserveOperation(context.Background(), OperationRequest{Name: "owner", Key: uuid.NewString(), Path: "/speech/owner", Body: []byte(`{}`)})
	if e != nil {
		t.Fatal(e)
	}
	_, e = s.Store.DB.Exec(context.Background(), "UPDATE operation SET state='running',subject_id=$2 WHERE id=$1", op.ID, id)
	if e != nil {
		t.Fatal(e)
	}
	if e = s.Store.takePreparation(context.Background(), p, op.ID, "render"); e != nil {
		t.Fatal(e)
	}
	_, e = s.RenderPreparation(context.Background(), id, uuid.NewString(), 1, nil)
	var fail *provider.Failure
	if !errors.As(e, &fail) || fail.Code != "LEASE_ACTIVE" || *calls != 0 {
		t.Fatal(e, *calls)
	}
}
func TestNativeSpeechMalformedActionNegative(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	r := httptest.NewRequest("POST", "/render", strings.NewReader(`{"preparation_id":"wrong","render_attempt":1}`))
	r.Header.Set("Content-Type", "application/json")
	r.SetPathValue("id", p["id"].(string))
	w := httptest.NewRecorder()
	s.speechRender(w, r)
	if w.Code != 400 || *calls != 0 {
		t.Fatal(w.Code, *calls)
	}
}

var _ = io.EOF
var _ = time.Second

func TestNativeSpeechActualKokoroPositive(t *testing.T) {
	s, r, c, _, _ := nativeMutationFixture(t, "speech-british")
	p, err := s.PrepareMutation(context.Background(), r, uuid.NewString(), c)
	if err != nil {
		t.Fatal(err)
	}
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	if s.SpeechURL == "" {
		t.Fatal("Actual local speech service is required")
	}
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	progress := speechProgress(t, s, p)
	first := progress["pieces"].([]any)[0].(map[string]any)
	if first["sample_count"].(float64) < 2400 || len(first["receipt_ids"].([]any)) != 1 {
		t.Fatal(first)
	}
	id := first["receipt_ids"].([]any)[0].(string)
	doc, e := s.Store.ReadDocument(context.Background(), id)
	if e != nil {
		t.Fatal(e)
	}
	var receipt map[string]any
	_ = json.Unmarshal(doc.Payload, &receipt)
	raw, e := s.Store.ReadAsset(context.Background(), receipt["wire_response_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var response map[string]any
	_ = json.Unmarshal(raw, &response)
	native := response["receipt"].(map[string]any)
	if native["provider"] != "local_kokoro" || native["voice_id"] != "bf_emma" || native["locale"] != "en-GB" || native["observed_accent"] != nil {
		t.Fatal(native)
	}
	dir := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	if dir != "" {
		out, _ := json.Marshal(map[string]any{"preparation": p, "progress": progress, "receipt": receipt, "response": response})
		if e = os.WriteFile(filepath.Join(dir, "actual-kokoro.json"), out, 0600); e != nil {
			t.Fatal(e)
		}
		var packet strings.Builder
		command, _ := json.Marshal(map[string]any{"action": "diagnostic-read", "id": receipt["operation_id"]})
		if e = s.Store.LabCommand(context.Background(), strings.NewReader(string(command)), &packet); e != nil {
			t.Fatal(e)
		}
		if e = os.WriteFile(filepath.Join(dir, "actual-kokoro-diagnostic.json"), []byte(packet.String()), 0600); e != nil {
			t.Fatal(e)
		}
	}
}

func TestNativeSpeechActualEspeakPositive(t *testing.T) {
	s, r, c, _, _ := nativeMutationFixture(t, "speech-espeak")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	if s.SpeechURL == "" {
		t.Fatal("Actual local speech service is required")
	}
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	progress := speechProgress(t, s, p)
	first := progress["pieces"].([]any)[0].(map[string]any)
	if first["sample_count"].(float64) < 2400 || len(first["receipt_ids"].([]any)) != 1 {
		t.Fatal(first)
	}
	id := first["receipt_ids"].([]any)[0].(string)
	doc, e := s.Store.ReadDocument(context.Background(), id)
	if e != nil {
		t.Fatal(e)
	}
	var receipt map[string]any
	_ = json.Unmarshal(doc.Payload, &receipt)
	raw, e := s.Store.ReadAsset(context.Background(), receipt["wire_response_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var response map[string]any
	_ = json.Unmarshal(raw, &response)
	native := response["receipt"].(map[string]any)
	if native["provider"] != "local_espeak_ng" || native["voice_id"] != "en-us" || native["observed_accent"] != nil {
		t.Fatal(native)
	}
	dir := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	if dir != "" {
		out, _ := json.Marshal(map[string]any{"preparation": p, "progress": progress, "receipt": receipt, "response": response})
		if e = os.WriteFile(filepath.Join(dir, "actual-espeak.json"), out, 0600); e != nil {
			t.Fatal(e)
		}
		var packet strings.Builder
		command, _ := json.Marshal(map[string]any{"action": "diagnostic-read", "id": receipt["operation_id"]})
		if e = s.Store.LabCommand(context.Background(), strings.NewReader(string(command)), &packet); e != nil {
			t.Fatal(e)
		}
		if e = os.WriteFile(filepath.Join(dir, "actual-espeak-diagnostic.json"), []byte(packet.String()), 0600); e != nil {
			t.Fatal(e)
		}
	}
}

func TestNativeSpeechSafeListPositive(t *testing.T) {
	s, p, _ := nativeSpeechFixture(t, 0)
	p = renderNative(t, s, p, uuid.NewString(), 1)
	r := httptest.NewRequest("GET", "/api/v1/preparations?view=public", nil)
	w := httptest.NewRecorder()
	s.preparationList(w, r)
	if w.Code != 200 || strings.Contains(w.Body.String(), "key_id") || strings.Contains(w.Body.String(), "mutated_asset") || !strings.Contains(w.Body.String(), "next_render_attempt") {
		t.Fatal(w.Code, w.Body.String())
	}
}
func TestNativeSpeechChildRecoveryPositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 2)
	p, _ = s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	progress := speechProgress(t, s, p)
	first := progress["pieces"].([]any)[0].(map[string]any)
	first["state"] = "interrupted"
	first["asset_id"] = nil
	first["source_asset_id"] = nil
	first["audio_sha256"] = nil
	first["sample_count"] = nil
	first["receipt_ids"] = []any{}
	// Simulate loss of the piece linkage after a real completed child, with a new
	// immutable test-owned journal/head. Never mutate accepted document payloads.
	op, e := s.Store.ReserveOperation(context.Background(), OperationRequest{Name: "speech-recovery-fixture", Key: uuid.NewString(), Path: "/speech/recovery-fixture", Body: []byte(`{}`)})
	if e != nil {
		t.Fatal(e)
	}
	_, e = s.Store.DB.Exec(context.Background(), "UPDATE operation SET state='running' WHERE id=$1", op.ID)
	if e != nil {
		t.Fatal(e)
	}
	if e = s.Store.takePreparation(context.Background(), p, op.ID, "render"); e != nil {
		t.Fatal(e)
	}
	if e = s.saveSpeechProgress(context.Background(), p, progress, op.ID); e != nil {
		t.Fatal(e)
	}
	_, e = s.Store.DB.Exec(context.Background(), "UPDATE operation SET state='interrupted' WHERE id=$1", op.ID)
	if e != nil {
		t.Fatal(e)
	}
	p = renderNative(t, s, p, uuid.NewString(), 2)
	if *calls != 3 {
		t.Fatal("completed child re-synthesized", *calls)
	}
}
func TestNativeSpeechPublicUnreadyNegative(t *testing.T) {
	s, p, _ := nativeSpeechFixture(t, 0)
	r := httptest.NewRequest("GET", "/api/v1/preparations?view=public", nil)
	w := httptest.NewRecorder()
	s.preparationList(w, r)
	var output map[string]any
	if e := json.Unmarshal(w.Body.Bytes(), &output); e != nil {
		t.Fatal(e)
	}
	for _, v := range output["items"].([]any) {
		row := v.(map[string]any)
		if row["id"] == p["id"] && row["audio_available"] != false {
			t.Fatal(row)
		}
	}
}
func TestNativeSpeechPublicLimitNegative(t *testing.T) {
	s, _, calls := nativeSpeechFixture(t, 0)
	r := httptest.NewRequest("GET", "/api/v1/preparations?view=public&limit=0", nil)
	w := httptest.NewRecorder()
	s.preparationList(w, r)
	if w.Code != 400 || *calls != 0 {
		t.Fatal(w.Code, *calls)
	}
}

func TestNativeSpeechHandlerRenderPositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	s.token = "owned-api-token"
	raw, _ := json.Marshal(map[string]any{"preparation_id": p["id"], "render_attempt": 1})
	r := httptest.NewRequest("POST", "/api/v1/preparations/"+p["id"].(string)+":render", strings.NewReader(string(raw)))
	r.Header.Set("Authorization", "Bearer owned-api-token")
	r.Header.Set("Origin", "http://localhost:3000")
	r.Header.Set("Content-Type", "application/json")
	r.Header.Set("Idempotency-Key", uuid.NewString())
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	if w.Code != 200 || *calls != 2 || strings.Contains(w.Body.String(), "key_id") {
		t.Fatal(w.Code, w.Body.String(), *calls)
	}
}
func TestNativeSpeechHandlerPlaybackPositive(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	p = renderNative(t, s, p, uuid.NewString(), 1)
	s.token = "owned-api-token"
	r := httptest.NewRequest("GET", "/api/v1/preparations/"+p["id"].(string)+"/audio", nil)
	r.Header.Set("Authorization", "Bearer owned-api-token")
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	if w.Code != 200 || w.Header().Get("Content-Type") != "audio/wav" || w.Body.Len() != 12056 || *calls != 2 {
		t.Fatal(w.Code, w.Body.Len(), *calls)
	}
}
func TestNativeSpeechHandlerDeniedNegative(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	s.token = "owned-api-token"
	r := httptest.NewRequest("GET", "/api/v1/preparations/"+p["id"].(string)+"/audio", nil)
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	if w.Code != 403 || *calls != 0 {
		t.Fatal(w.Code, *calls)
	}
}
func TestNativeSpeechHandlerUnknownNegative(t *testing.T) {
	s, p, calls := nativeSpeechFixture(t, 0)
	s.token = "owned-api-token"
	r := httptest.NewRequest("POST", "/api/v1/preparations/"+p["id"].(string)+":invented", nil)
	r.Header.Set("Authorization", "Bearer owned-api-token")
	r.Header.Set("Origin", "http://localhost:3000")
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	if w.Code != 404 || *calls != 0 {
		t.Fatal(w.Code, *calls)
	}
}
func TestNativeSpeechActualWrongVoiceNegative(t *testing.T) {
	s, _, _ := nativeSpeechFixture(t, 0)
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	_, e := s.speechCall(context.Background(), "/internal/v1/piece", map[string]any{"profile": map[string]any{"provider": "local_kokoro", "billing_mode": "local", "voices": []any{}}, "turn": map[string]any{"voice_id": "unknown", "locale": "en-US"}}, nil)
	var failure *provider.Failure
	if !errors.As(e, &failure) || failure.Code != "VOICE_UNAVAILABLE" {
		t.Fatal(e)
	}
}
func TestNativeSpeechActualPaidNegative(t *testing.T) {
	s, _, _ := nativeSpeechFixture(t, 0)
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	_, e := s.speechCall(context.Background(), "/internal/v1/piece", map[string]any{"profile": map[string]any{"provider": "elevenlabs", "billing_mode": "metered"}, "turn": map[string]any{}}, nil)
	var failure *provider.Failure
	if !errors.As(e, &failure) || failure.Code != "PAID_USE_FORBIDDEN" {
		t.Fatal(e)
	}
}

func TestNativeSpeechActualQwenCustomPositive(t *testing.T) {
	s, r, c, _, _ := nativeMutationFixture(t, "speech-qwen-custom")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	if s.SpeechURL == "" {
		t.Fatal("Actual local speech service is required")
	}
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	progress := speechProgress(t, s, p)
	first := progress["pieces"].([]any)[0].(map[string]any)
	if first["sample_count"].(float64) < 2400 || len(first["receipt_ids"].([]any)) != 1 {
		t.Fatal(first)
	}
	id := first["receipt_ids"].([]any)[0].(string)
	doc, e := s.Store.ReadDocument(context.Background(), id)
	if e != nil {
		t.Fatal(e)
	}
	var receipt map[string]any
	_ = json.Unmarshal(doc.Payload, &receipt)
	raw, e := s.Store.ReadAsset(context.Background(), receipt["wire_response_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var response map[string]any
	_ = json.Unmarshal(raw, &response)
	native := response["receipt"].(map[string]any)
	if native["provider"] != "local_qwen3_tts" || native["voice_id"] != "Ryan" || native["observed_accent"] != nil {
		t.Fatal(native)
	}
	calls, ok := native["native"].(map[string]any)["model_visible_calls"].([]any)
	if !ok || len(calls) < 2 {
		t.Fatal("actual Qwen tokenizer/decoder inputs absent", native["native"])
	}
	encodedCalls, _ := json.Marshal(calls)
	if !strings.Contains(string(encodedCalls), "_tokenize_texts") || !strings.Contains(string(encodedCalls), "input_ids") || strings.Contains(string(encodedCalls), "inspection_limit") {
		t.Fatal("incomplete actual model input capture", string(encodedCalls))
	}
	dir := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	if dir != "" {
		out, _ := json.Marshal(map[string]any{"preparation": p, "progress": progress, "receipt": receipt, "response": response})
		if e = os.WriteFile(filepath.Join(dir, "actual-qwen-custom.json"), out, 0600); e != nil {
			t.Fatal(e)
		}
		var packet strings.Builder
		command, _ := json.Marshal(map[string]any{"action": "diagnostic-read", "id": receipt["operation_id"]})
		if e = s.Store.LabCommand(context.Background(), strings.NewReader(string(command)), &packet); e != nil {
			t.Fatal(e)
		}
		if e = os.WriteFile(filepath.Join(dir, "actual-qwen-custom-diagnostic.json"), []byte(packet.String()), 0600); e != nil {
			t.Fatal(e)
		}
	}
}

func TestNativeSpeechActualQwenBasePositive(t *testing.T) {
	s, r, c, _, _ := nativeMutationFixture(t, "speech-qwen-base")
	p, e := s.PrepareMutation(context.Background(), r, uuid.NewString(), c)
	if e != nil {
		t.Fatal(e)
	}
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	if s.SpeechURL == "" {
		t.Fatal("Actual local speech service is required")
	}
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	progress := speechProgress(t, s, p)
	first := progress["pieces"].([]any)[0].(map[string]any)
	if first["sample_count"].(float64) < 2400 || len(first["receipt_ids"].([]any)) != 1 {
		t.Fatal(first)
	}
	id := first["receipt_ids"].([]any)[0].(string)
	doc, e := s.Store.ReadDocument(context.Background(), id)
	if e != nil {
		t.Fatal(e)
	}
	var receipt map[string]any
	_ = json.Unmarshal(doc.Payload, &receipt)
	raw, e := s.Store.ReadAsset(context.Background(), receipt["wire_response_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var response map[string]any
	_ = json.Unmarshal(raw, &response)
	native := response["receipt"].(map[string]any)
	if native["provider"] != "local_qwen3_tts" || native["voice_id"] != "tangerine-american-1" || native["observed_accent"] != nil {
		t.Fatal(native)
	}
	calls, ok := native["native"].(map[string]any)["model_visible_calls"].([]any)
	if !ok || len(calls) < 2 {
		t.Fatal("actual Qwen tokenizer/decoder inputs absent", native["native"])
	}
	encodedCalls, _ := json.Marshal(calls)
	if !strings.Contains(string(encodedCalls), "_tokenize_texts") || !strings.Contains(string(encodedCalls), "input_ids") || strings.Contains(string(encodedCalls), "inspection_limit") {
		t.Fatal("incomplete actual model input capture", string(encodedCalls))
	}
	dir := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	if dir != "" {
		out, _ := json.Marshal(map[string]any{"preparation": p, "progress": progress, "receipt": receipt, "response": response})
		if e = os.WriteFile(filepath.Join(dir, "actual-qwen-base.json"), out, 0600); e != nil {
			t.Fatal(e)
		}
		var packet strings.Builder
		command, _ := json.Marshal(map[string]any{"action": "diagnostic-read", "id": receipt["operation_id"]})
		if e = s.Store.LabCommand(context.Background(), strings.NewReader(string(command)), &packet); e != nil {
			t.Fatal(e)
		}
		if e = os.WriteFile(filepath.Join(dir, "actual-qwen-base-diagnostic.json"), []byte(packet.String()), 0600); e != nil {
			t.Fatal(e)
		}
	}
}

func TestNativeSpeechQwenMissingVoiceNegative(t *testing.T) {
	s, _, _ := nativeSpeechFixture(t, 0)
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	_, e := s.speechCall(context.Background(), "/internal/v1/piece", map[string]any{"profile": map[string]any{"id": "qwen-base-v1", "provider": "local_qwen3_tts", "adapter_version": "qwen-base-v1", "billing_mode": "local", "voices": []any{map[string]any{"id": "missing-reference", "locale": "en-US"}}}, "turn": map[string]any{"voice_id": "missing-reference", "locale": "en-US", "operations": []any{map[string]any{"kind": "text", "text": "Hello."}}}}, nil)
	var failure *provider.Failure
	if !errors.As(e, &failure) || failure.Code != "VOICE_SETUP_REQUIRED" {
		t.Fatal(e)
	}
}
func TestNativeSpeechQwenUnsupportedOperationNegative(t *testing.T) {
	s, _, _ := nativeSpeechFixture(t, 0)
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	_, e := s.speechCall(context.Background(), "/internal/v1/piece", map[string]any{"profile": map[string]any{"id": "qwen-base-v1", "provider": "local_qwen3_tts", "adapter_version": "qwen-base-v1", "billing_mode": "local", "voices": []any{map[string]any{"id": "tangerine-american-1", "locale": "en-US"}}}, "turn": map[string]any{"voice_id": "tangerine-american-1", "locale": "en-US", "operations": []any{map[string]any{"kind": "phoneme", "text": "Hello.", "ipa": "hi"}}}}, nil)
	var failure *provider.Failure
	if !errors.As(e, &failure) || failure.Code != "CAPABILITY_UNAVAILABLE" {
		t.Fatal(e)
	}
}

// Independent observer around the actual private HTTP transport. It does not
// replace speech, storage or evidence writers, and never records credentials.
func renderNativeActual(t *testing.T, s *Server, p map[string]any, key string, attempt int) map[string]any {
	t.Helper()
	root := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	dir := filepath.Join(root, t.Name())
	if e := os.MkdirAll(dir, 0700); e != nil {
		t.Fatal(e)
	}
	file, e := os.OpenFile(filepath.Join(dir, "dispatch-observations.jsonl"), os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	if e != nil {
		t.Fatal(e)
	}
	defer file.Close()
	transport := &http.Transport{}
	defer transport.CloseIdleConnections()
	client := &http.Client{Transport: preparationTrip(func(req *http.Request) (*http.Response, error) {
		request, err := io.ReadAll(req.Body)
		if err != nil {
			return nil, err
		}
		req.Body = io.NopCloser(bytes.NewReader(request))
		response, err := transport.RoundTrip(req)
		row := map[string]any{"path": req.URL.Path, "wire_request_sha256": contracts.Digest(request), "fixture_response": false, "origin": "actual_private_speech_http"}
		capture := uuid.NewString()
		requestPath := capture + "-request.bytes"
		if e := os.WriteFile(filepath.Join(dir, requestPath), request, 0600); e != nil {
			t.Error(e)
		}
		row["request_artifact"] = requestPath
		if response != nil {
			body, readErr := io.ReadAll(response.Body)
			response.Body.Close()
			response.Body = io.NopCloser(bytes.NewReader(body))
			row["wire_response_sha256"] = contracts.Digest(body)
			row["http_status"] = response.StatusCode
			responsePath := capture + "-response.bytes"
			if e := os.WriteFile(filepath.Join(dir, responsePath), body, 0600); e != nil {
				t.Error(e)
			}
			row["response_artifact"] = responsePath
			if err == nil {
				err = readErr
			}
		}
		if err != nil {
			row["transport_error"] = err.Error()
		}
		if e := json.NewEncoder(file).Encode(row); e != nil {
			t.Error(e)
		}
		return response, err
	})}
	out, err := s.RenderPreparation(context.Background(), p["id"].(string), key, attempt, client)
	if err != nil {
		t.Fatal(out, err)
	}
	return out
}
