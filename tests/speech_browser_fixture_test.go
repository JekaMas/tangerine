package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// A disposable, actually stored generated preparation for the native browser.
// Constructed LLM text/key; actual local speech, database, assets and HTTP owner.
func TestNativeSpeechBrowserFixture(t *testing.T) {
	s, p, _ := nativeSpeechFixtureMode(t, 0, true)
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	s.token = os.Getenv("API_INTERNAL_TOKEN")
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	dir := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	progress := speechProgress(t, s, p)
	first := progress["pieces"].([]any)[0].(map[string]any)
	doc, err := s.Store.ReadDocument(context.Background(), first["receipt_ids"].([]any)[0].(string))
	if err != nil {
		t.Fatal(err)
	}
	var receipt map[string]any
	if err = json.Unmarshal(doc.Payload, &receipt); err != nil {
		t.Fatal(err)
	}
	response, err := s.Store.ReadAsset(context.Background(), receipt["wire_response_asset_id"].(string))
	if err != nil {
		t.Fatal(err)
	}
	actual, _ := json.Marshal(map[string]any{"preparation": p, "progress": progress, "receipt": receipt, "response": json.RawMessage(response)})
	if err = os.WriteFile(filepath.Join(dir, "browser-actual.json"), actual, 0600); err != nil {
		t.Fatal(err)
	}
	var diagnostic strings.Builder
	command, _ := json.Marshal(map[string]any{"action": "diagnostic-read", "id": receipt["operation_id"]})
	if err = s.Store.LabCommand(context.Background(), strings.NewReader(string(command)), &diagnostic); err != nil {
		t.Fatal(err)
	}
	if err = os.WriteFile(filepath.Join(dir, "browser-actual-diagnostic.json"), []byte(diagnostic.String()), 0600); err != nil {
		t.Fatal(err)
	}
	wav, err := s.Store.ReadAsset(context.Background(), p["audio_asset_id"].(string))
	if err != nil {
		t.Fatal(err)
	}
	if err = os.WriteFile(filepath.Join(dir, "browser-audio.wav"), wav, 0600); err != nil {
		t.Fatal(err)
	}
	listener, e := net.Listen("tcp", "0.0.0.0:8080")
	if e != nil {
		t.Fatal(e)
	}
	server := http.Server{Handler: s.Handler()}
	go server.Serve(listener)
	defer server.Shutdown(context.Background())
	data, _ := json.Marshal(map[string]any{"preparation_id": p["id"], "audio_asset_id": p["audio_asset_id"]})
	if e = os.WriteFile(filepath.Join(dir, "browser-fixture.json"), data, 0600); e != nil {
		t.Fatal(e)
	}
	deadline := time.Now().Add(240 * time.Second)
	for time.Now().Before(deadline) {
		if _, e = os.Stat(filepath.Join(dir, "browser-done")); e == nil {
			return
		}
		time.Sleep(100 * time.Millisecond)
	}
	t.Fatal("Browser did not finish its actual observations")
}
