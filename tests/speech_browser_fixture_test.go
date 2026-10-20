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

// A disposable, actually stored generated preparation for the native browser.
// Constructed LLM text/key; actual local speech, database, assets and HTTP owner.
func TestNativeSpeechBrowserFixture(t *testing.T) {
	s, p, _ := nativeSpeechFixtureMode(t, 0, true)
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	s.token = os.Getenv("API_INTERNAL_TOKEN")
	p = renderNative(t, s, p, uuid.NewString(), 1)
	listener, e := net.Listen("tcp", "0.0.0.0:8080")
	if e != nil {
		t.Fatal(e)
	}
	server := http.Server{Handler: s.Handler()}
	go server.Serve(listener)
	defer server.Shutdown(context.Background())
	dir := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
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
