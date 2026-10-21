package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"path/filepath"
	"testing"
	"time"
)

// Owns only constructed upstream responses. Production API, web, database,
// object storage, launcher, archive, restore and browser remain genuine.
func TestRecoveryWorkspaceFixture(t *testing.T) {
	root := os.Getenv("TANGERINE_RECOVERY_EVIDENCE")
	if root == "" {
		t.Fatal("private evidence required")
	}
	s, calls := qualityGenerationServer(t, false)
	qualitySpeechTarget(t, s, false)
	// Copy the constructed native fixture to the ordinary public application schema.
	// Native seed source below uses this genuine public Storage directly.
	public := recoveryPublicStore(t)
	c, _, e := s.Store.Configuration(context.Background())
	requireListening(t, e)
	endpoint, _ := url.Parse(c["llm_profiles"].([]any)[0].(map[string]any)["endpoint"].(string))
	modelProxy := httputil.NewSingleHostReverseProxy(endpoint)
	speechEndpoint, _ := url.Parse(s.SpeechURL)
	speechProxy := httputil.NewSingleHostReverseProxy(speechEndpoint)
	modelListener, e := net.Listen("tcp", "0.0.0.0:8081")
	requireListening(t, e)
	speechListener, e := net.Listen("tcp", "0.0.0.0:8091")
	requireListening(t, e)
	modelServer := &http.Server{Handler: modelProxy}
	speechServer := &http.Server{Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			w.WriteHeader(200)
			return
		}
		speechProxy.ServeHTTP(w, r)
	})}
	go modelServer.Serve(modelListener)
	go speechServer.Serve(speechListener)
	defer modelServer.Close()
	defer speechServer.Close()
	c["llm_profiles"].([]any)[0].(map[string]any)["endpoint"] = "http://llm-local:8081/v1/responses"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = public.PutConfiguration(context.Background(), mustJSON(c), uuid.NewString(), -1)
	requireListening(t, e)
	// A real saved attempt/answer and playable case with literal PCM are seeded.
	f := recoveryWorkspaceCase(t)
	check, _, ce := f.s.Store.Configuration(context.Background())
	requireListening(t, ce)
	t.Log("configured model", check["llm_profiles"].([]any)[0].(map[string]any)["model"], "selected", check["llm_profile"])
	attempt := f.start(t)
	answer := "Use opens. Café is singular.\nExact saved answer — original bytes."
	_, _, e = f.s.Store.WriteAnswer(context.Background(), attempt, uuid.NewString(), 0, answerPacket(answer, "en"), false)
	requireListening(t, e)
	fixture := map[string]any{"case": f.id, "sha": f.sha, "audio_sha": f.audioSHA, "attempt": attempt, "answer": answer, "audio_bytes": len(f.audio), "schema": "public", "proof": "Constructed model/speech inputs and PCM; genuine native stored case, draft, PostgreSQL/MinIO and private application readback."}
	data, _ := json.Marshal(fixture)
	requireListening(t, os.WriteFile(filepath.Join(root, "fixture.json"), data, 0600))
	for {
		if _, e = os.Stat(filepath.Join(root, "done")); e == nil {
			break
		}
		time.Sleep(100 * time.Millisecond)
	}
	requireListening(t, os.WriteFile(filepath.Join(root, "dispatch-count.json"), mustJSON(map[string]any{"calls": calls.Load()}), 0600))
}

func recoveryWorkspaceCase(t *testing.T) listeningFixture {
	t.Helper()
	s := NewServer(recoveryPublicStore(t), "http://localhost:3000", "http://unused.invalid")
	s.token = "listening-owned-token"
	ctx := context.Background()
	pcm := make([]byte, 48000)
	for i := 0; i < len(pcm); i += 2 {
		pcm[i] = byte(i % 251)
	}
	audio := speechWAV(pcm)
	asset, e := s.saveAudioBytes(ctx, audio)
	if e != nil {
		t.Fatal(e)
	}
	b := preparationBlueprint(t, 1)
	b["public_context"] = "Café opening. Identify mistakes and offer corrections."
	_, _, candidate, _ := mutationFixture()
	settings := map[string]any{"blueprint": b, "configuration": DefaultConfiguration()}
	frozen := map[string]any{"plan": map[string]any{"case_version_id": "constructed-native-input"}, "pieces": []any{map[string]any{"utterance_id": "u1", "gap_after_ms": float64(0)}}}
	progress := map[string]any{"pieces": []any{map[string]any{"utterance_id": "u1", "sample_count": float64(24000), "receipt_ids": []any{}}}}
	key := projectSpeechKey(settings, candidate, frozen, progress, asset.ID, asset.SHA, "2.0.0")
	source, e := s.Store.saveGroundTruth(ctx, key)
	if e != nil {
		t.Fatal(e)
	}
	tx, e := beginWrite(ctx, s.Store)
	if e != nil {
		t.Fatal(e)
	}
	defer tx.Rollback(ctx)
	id, e := s.Store.publishListeningCase(ctx, tx, source, b["task_components"].(map[string]any), "Café opening", "monologue")
	if e != nil {
		t.Fatal(e)
	}
	if e = tx.Commit(ctx); e != nil {
		t.Fatal(e)
	}
	return listeningFixture{s: s, id: id, sha: key["case_sha256"].(string), audioSHA: asset.SHA, audio: audio, key: key}
}

func recoveryPublicStore(t *testing.T) *Storage {
	t.Helper()
	s, e := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	requireListening(t, e)
	t.Cleanup(s.DB.Close)
	return s
}
