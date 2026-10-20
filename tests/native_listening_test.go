package app

// Constructed key/PCM are external fixture inputs. Actual admission, publication,
// transactions, HTTP and MinIO remain production owners; no inference is substituted.
import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"net/http/httptest"
	"net/url"
	"os"
	"strings"
	"sync"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"testing"
)

type listeningFixture struct {
	s                 *Server
	id, sha, audioSHA string
	audio             []byte
	key               map[string]any
}

func listeningNative(t *testing.T) *Storage {
	t.Helper()
	base := os.Getenv("DATABASE_URL")
	if base == "" {
		t.Fatal("native DATABASE_URL required")
	}
	schema := "listen_" + strings.ReplaceAll(uuid.NewString(), "-", "")
	admin, e := OpenStorage(context.Background(), base, "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	if e != nil {
		t.Fatal(e)
	}
	if _, e = admin.DB.Exec(context.Background(), "CREATE SCHEMA "+schema); e != nil {
		t.Fatal(e)
	}
	u, _ := url.Parse(base)
	q := u.Query()
	q.Set("search_path", schema)
	u.RawQuery = q.Encode()
	s, e := OpenStorage(context.Background(), u.String(), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(func() {
		s.DB.Close()
		_, _ = admin.DB.Exec(context.Background(), "DROP SCHEMA "+schema+" CASCADE")
		admin.DB.Close()
	})
	if e = s.Migrate(context.Background()); e != nil {
		t.Fatal(e)
	}
	if e = s.InitMedia(context.Background()); e != nil {
		t.Fatal(e)
	}
	return s
}
func listeningCase(t *testing.T) listeningFixture {
	t.Helper()
	s := NewServer(listeningNative(t), "http://localhost:3000", "http://unused.invalid")
	s.token = "listening-owned-token"
	configuration := DefaultConfiguration()
	configuration["llm_profiles"].([]any)[0].(map[string]any)["model"] = "constructed-evaluator"
	for _, field := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(configuration, field)
	}
	configBytes, _ := json.Marshal(configuration)
	if _, _, err := s.Store.PutConfiguration(context.Background(), configBytes, uuid.NewString(), -1); err != nil {
		t.Fatal(err)
	}
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
func (f listeningFixture) start(t *testing.T) string {
	t.Helper()
	raw, _ := json.Marshal(map[string]any{"case_version_id": f.id, "case_sha256": f.sha, "requested_language": "en"})
	v, e := f.s.Store.StartAttempt(context.Background(), raw, uuid.NewString())
	if e != nil {
		t.Fatal(e)
	}
	return v["attempt_id"].(string)
}
func (f listeningFixture) request(method, path, body, key, revision string) *httptest.ResponseRecorder {
	r := httptest.NewRequest(method, path, strings.NewReader(body))
	r.Header.Set("Authorization", "Bearer "+f.s.token)
	r.Header.Set("Origin", f.s.Origin)
	r.Header.Set("Content-Type", "application/json")
	r.Header.Set("Idempotency-Key", key)
	if revision != "" {
		r.Header.Set("If-Match", revision)
	}
	w := httptest.NewRecorder()
	f.s.Handler().ServeHTTP(w, r)
	return w
}
func requireListening(t *testing.T, e error) {
	t.Helper()
	if e != nil {
		t.Fatal(e)
	}
}
func TestNativeListeningPublishPositive(t *testing.T) {
	f := listeningCase(t)
	w := f.request("GET", "/api/v1/library", "", "", "")
	if w.Code != 200 || !strings.Contains(w.Body.String(), f.id) || !strings.Contains(w.Body.String(), f.sha) {
		t.Fatal(w.Code, w.Body.String())
	}
	d, e := f.s.Store.ReadDocument(context.Background(), f.id)
	requireListening(t, e)
	var key map[string]any
	_ = json.Unmarshal(d.Payload, &key)
	if key["case_version_id"] != f.id || key["case_sha256"] != f.sha || key["status"] != "published" {
		t.Fatal(key)
	}
}
func TestNativeListeningPublicationReplayPositive(t *testing.T) {
	f := listeningCase(t)
	var source string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT source_key_id FROM listening_case WHERE case_version_id=$1", f.id).Scan(&source))
	tx, e := beginWrite(context.Background(), f.s.Store)
	requireListening(t, e)
	defer tx.Rollback(context.Background())
	id, e := f.s.Store.publishListeningCase(context.Background(), tx, source, map[string]any{}, "Different", "dialogue")
	requireListening(t, e)
	if id != f.id {
		t.Fatal(id)
	}
	requireListening(t, tx.Commit(context.Background()))
}
func TestNativeListeningUnavailableNegative(t *testing.T) {
	f := listeningCase(t)
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE exercise_catalog SET availability='quarantined' WHERE id=$1", f.id)
	requireListening(t, e)
	raw, _ := json.Marshal(map[string]any{"case_version_id": f.id, "case_sha256": f.sha, "requested_language": "en"})
	_, e = f.s.Store.StartAttempt(context.Background(), raw, uuid.NewString())
	if !errors.Is(e, ErrCaseUnavailable) {
		t.Fatal(e)
	}
}
func TestNativeListeningSelectionDigestNegative(t *testing.T) {
	f := listeningCase(t)
	raw, _ := json.Marshal(map[string]any{"case_version_id": f.id, "case_sha256": strings.Repeat("0", 64), "requested_language": "en"})
	_, e := f.s.Store.StartAttempt(context.Background(), raw, uuid.NewString())
	if !errors.Is(e, ErrCaseUnavailable) {
		t.Fatal(e)
	}
}
func TestNativeListeningStartPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	r, e := f.s.Store.Attempt(context.Background(), id)
	requireListening(t, e)
	if r.Attempt["case_version_id"] != f.id || r.Attempt["audio_sha256"] != f.audioSHA || r.Attempt["state"] != "started" || r.Attempt["evaluation_policy_version"] != "answer-components-v2" || len(r.Context["evaluator_bindings"].([]any)) != 5 {
		t.Fatal(r)
	}
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM operation WHERE operation_name IN('llm-inference','speech-inference')").Scan(&n))
	if n != 0 {
		t.Fatal(n)
	}
}
func TestNativeListeningStartReplayPositive(t *testing.T) {
	f := listeningCase(t)
	key := uuid.NewString()
	raw, _ := json.Marshal(map[string]any{"case_version_id": f.id, "case_sha256": f.sha, "requested_language": "ru"})
	a, e := f.s.Store.StartAttempt(context.Background(), raw, key)
	requireListening(t, e)
	b, e := f.s.Store.StartAttempt(context.Background(), raw, key)
	requireListening(t, e)
	if lab.Hash(a) != lab.Hash(b) {
		t.Fatal(a, b)
	}
}
func TestNativeListeningStartConflictNegative(t *testing.T) {
	f := listeningCase(t)
	key := uuid.NewString()
	raw, _ := json.Marshal(map[string]any{"case_version_id": f.id, "case_sha256": f.sha, "requested_language": "en"})
	_, e := f.s.Store.StartAttempt(context.Background(), raw, key)
	requireListening(t, e)
	raw, _ = json.Marshal(map[string]any{"case_version_id": f.id, "case_sha256": f.sha, "requested_language": "ru"})
	_, e = f.s.Store.StartAttempt(context.Background(), raw, key)
	if !errors.Is(e, ErrConflict) {
		t.Fatal(e)
	}
	// A missing core evaluator still needs Settings; optional readiness is separate.
	c, rev, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	c["llm_profiles"].([]any)[0].(map[string]any)["model"] = "unselected"
	for _, field := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, field)
	}
	configRaw, _ := json.Marshal(c)
	_, _, e = f.s.Store.PutConfiguration(context.Background(), configRaw, uuid.NewString(), rev)
	requireListening(t, e)
	response := f.request("POST", "/api/v1/attempts", string(raw), uuid.NewString(), "")
	if response.Code != 409 || !strings.Contains(response.Body.String(), "CAPABILITY_UNQUALIFIED") {
		t.Fatal(response.Code, response.Body.String())
	}

}
func TestNativeListeningFrozenSettingsNegative(t *testing.T) {
	f := listeningCase(t)
	// Optional audit/feedback/adjudication setup cannot gate ordinary entry.
	optionalConfig, optionalRevision, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	original := optionalConfig["llm_profiles"].([]any)[0].(map[string]any)
	optional := map[string]any{}
	for field, value := range original {
		optional[field] = value
	}
	optional["id"] = "optional-unselected"
	optional["model"] = "unselected"
	optionalConfig["llm_profiles"] = append(optionalConfig["llm_profiles"].([]any), optional)
	for _, role := range []string{"mapping_audit", "feedback", "adjudication"} {
		optionalConfig["stage_profiles"].(map[string]any)[role] = "optional-unselected"
	}
	for _, field := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(optionalConfig, field)
	}
	configRaw, _ := json.Marshal(optionalConfig)
	_, _, e = f.s.Store.PutConfiguration(context.Background(), configRaw, uuid.NewString(), optionalRevision)
	requireListening(t, e)
	id := f.start(t)
	before, e := f.s.Store.Attempt(context.Background(), id)
	requireListening(t, e)
	optionalCount := 0
	for _, item := range before.Context["evaluator_bindings"].([]any) {
		profile := item.(map[string]any)["profile"].(map[string]any)
		if profile["id"] == "optional-unselected" && profile["model"] == "unselected" {
			optionalCount++
		}
	}
	if optionalCount != 3 {
		t.Fatal("optional selections were not retained", before.Context["evaluator_bindings"])
	}
	c, rev, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	c["feedback_language"] = "ru"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	raw, _ := json.Marshal(c)
	_, _, e = f.s.Store.PutConfiguration(context.Background(), raw, uuid.NewString(), rev)
	requireListening(t, e)
	after, e := f.s.Store.Attempt(context.Background(), id)
	requireListening(t, e)
	if lab.Hash(before.Context["configuration"]) != lab.Hash(after.Context["configuration"]) {
		t.Fatal("old attempt adopted settings")
	}
}
func TestNativeListeningDraftPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	text := "  He go → He goes.\r\nОшибка e\u0301 🟠  "
	a, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket(text, "ru"), false)
	requireListening(t, e)
	if a["state"] != "started" || a["answer_text"] != text || a["answer_utf8_sha256"] != contracts.Digest([]byte(text)) || a["revision"] != float64(1) {
		t.Fatal(a)
	}
	r, e := f.s.Store.Attempt(context.Background(), id)
	requireListening(t, e)
	if r.Attempt["answer_text"] != text || r.Context["requested_language"] != "ru" {
		t.Fatal(r)
	}
}
func TestNativeListeningDraftReplayPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	key := uuid.NewString()
	a, op, e := f.s.Store.WriteAnswer(context.Background(), id, key, 0, answerPacket("draft", "en"), false)
	requireListening(t, e)
	b, replay, e := f.s.Store.WriteAnswer(context.Background(), id, key, 0, answerPacket("draft", "en"), false)
	requireListening(t, e)
	if op != replay || lab.Hash(a) != lab.Hash(b) {
		t.Fatal(a, b)
	}
}
func TestNativeListeningDraftStaleNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("first", "en"), false)
	requireListening(t, e)
	_, _, e = f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("stale", "en"), false)
	if !errors.Is(e, ErrRevision) {
		t.Fatal(e)
	}
	r, e := f.s.Store.Attempt(context.Background(), id)
	requireListening(t, e)
	if r.Attempt["answer_text"] != "first" {
		t.Fatal(r)
	}
}
func TestNativeListeningDraftConflictNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	key := uuid.NewString()
	_, _, e := f.s.Store.WriteAnswer(context.Background(), id, key, 0, answerPacket("first", "en"), false)
	requireListening(t, e)
	_, _, e = f.s.Store.WriteAnswer(context.Background(), id, key, 0, answerPacket("different", "en"), false)
	if !errors.Is(e, ErrConflict) {
		t.Fatal(e)
	}
}
func TestNativeListeningSubmitPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	a, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("Согласование: goes.", "ru"), true)
	requireListening(t, e)
	if a["state"] != "saved" || a["submitted_at"] == nil || a["started_at"] == nil {
		t.Fatal(a)
	}
	w := f.request("GET", "/api/v1/attempts/"+id+"/results", "", "", "")
	if w.Code != 200 || !strings.Contains(w.Body.String(), `"status":"saved"`) || !strings.Contains(w.Body.String(), `"score":null`) {
		t.Fatal(w.Code, w.Body.String())
	}
}
func TestNativeListeningEmptySubmitPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	key := uuid.NewString()
	a, _, e := f.s.Store.WriteAnswer(context.Background(), id, key, 0, answerPacket("", "en"), true)
	requireListening(t, e)
	b, _, e := f.s.Store.WriteAnswer(context.Background(), id, key, 0, answerPacket("", "en"), true)
	requireListening(t, e)
	if a["answer_text"] != "" || a["answer_utf8_sha256"] != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" || lab.Hash(a) != lab.Hash(b) {
		t.Fatal(a, b)
	}
}
func TestNativeListeningAfterSubmitNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("frozen", "en"), true)
	requireListening(t, e)
	_, _, e = f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 1, answerPacket("edit", "en"), false)
	if !errors.Is(e, ErrAttemptState) {
		t.Fatal(e)
	}
}
func TestNativeListeningResubmitNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("frozen", "en"), true)
	requireListening(t, e)
	_, _, e = f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 1, answerPacket("replace", "en"), true)
	if !errors.Is(e, ErrAttemptState) {
		t.Fatal(e)
	}
}
func (f listeningFixture) event(id, page, kind string, seq, pos int) []byte {
	raw, _ := json.Marshal(map[string]any{"schema_version": "2.0.0", "attempt_id": id, "audio_sha256": f.audioSHA, "kind": kind, "client_sequence": seq, "page_instance_id": page, "position_sample": pos, "client_time_ms": nil})
	return raw
}
func TestNativeListeningPlaybackPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	for i, k := range []string{"play", "pause", "seek", "ended"} {
		_, e := f.s.Store.RecordPlayback(context.Background(), id, uuid.NewString(), f.event(id, "page1", k, i, 24000))
		requireListening(t, e)
	}
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM playback_index WHERE attempt_id=$1", id).Scan(&n))
	if n != 4 {
		t.Fatal(n)
	}
}
func TestNativeListeningPlaybackReplayPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("draft1", "en"), false)
	requireListening(t, e)
	raw := f.event(id, "p1", "play", 0, 0)
	key := uuid.NewString()
	a, e := f.s.Store.RecordPlayback(context.Background(), id, key, raw)
	requireListening(t, e)
	_, _, e = f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 1, answerPacket("draft2", "en"), false)
	requireListening(t, e)
	b, e := f.s.Store.RecordPlayback(context.Background(), id, key, raw)
	requireListening(t, e)
	c, e := f.s.Store.RecordPlayback(context.Background(), id, uuid.NewString(), raw)
	requireListening(t, e)
	if lab.Hash(a) != lab.Hash(b) || lab.Hash(a["artifact_ids"]) != lab.Hash(c["artifact_ids"]) || a["revision"] != int64(1) || c["revision"] != int64(1) {
		t.Fatal(a, b, c)
	}
	// Browser HTTP reports may arrive in a different order than client ordinals.
	_, e = f.s.Store.RecordPlayback(context.Background(), id, uuid.NewString(), f.event(id, "p1", "ended", 2, 24000))
	requireListening(t, e)
	_, e = f.s.Store.RecordPlayback(context.Background(), id, uuid.NewString(), f.event(id, "p1", "pause", 1, 12000))
	requireListening(t, e)
	_, e = f.s.Store.RecordPlayback(context.Background(), id, uuid.NewString(), f.event(id, "p2", "play", 0, 0))
	requireListening(t, e)
}
func TestNativeListeningPlaybackMismatchNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	for _, raw := range [][]byte{f.event(id, "p1", "play", 0, 24001), f.event("another-attempt", "p1", "play", 0, 0), []byte(strings.ReplaceAll(string(f.event(id, "p1", "play", 0, 0)), f.audioSHA, strings.Repeat("0", 64)))} {
		if _, e := f.s.Store.RecordPlayback(context.Background(), id, uuid.NewString(), raw); !errors.Is(e, ErrInput) {
			t.Fatal(e)
		}
	}
}
func TestNativeListeningPlaybackConflictNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	_, e := f.s.Store.RecordPlayback(context.Background(), id, uuid.NewString(), f.event(id, "p1", "play", 2, 0))
	requireListening(t, e)
	for _, raw := range [][]byte{f.event(id, "p1", "pause", 2, 1), f.event(id, "p1", "seek", 2, 0)} {
		if _, e := f.s.Store.RecordPlayback(context.Background(), id, uuid.NewString(), raw); !errors.Is(e, ErrConflict) {
			t.Fatal(e)
		}
	}
}
func TestNativeListeningHTTPPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	w := f.request("GET", "/api/v1/attempts/"+id, "", "", "")
	if w.Code != 200 || w.Header().Get("ETag") != `"0"` || w.Header().Get("X-Tangerine-Audio-SHA256") != f.audioSHA {
		t.Fatal(w.Code, w.Body.String())
	}
	w = f.request("PUT", "/api/v1/attempts/"+id+"/answer", string(answerPacket(strings.Repeat("🟠", 20000), "ru")), uuid.NewString(), `"0"`)
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
}
func TestNativeListeningRangePositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	r := httptest.NewRequest("GET", "/api/v1/attempts/"+id+"/audio", nil)
	r.Header.Set("Authorization", "Bearer "+f.s.token)
	r.Header.Set("Range", "bytes=44-47")
	w := httptest.NewRecorder()
	f.s.Handler().ServeHTTP(w, r)
	if w.Code != 206 || string(w.Body.Bytes()) != string(f.audio[44:48]) || w.Header().Get("ETag") != `"`+f.audioSHA+`"` {
		t.Fatal(w.Code, w.Body.String())
	}
}
func TestNativeListeningPublicPrivateNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	w := f.request("GET", "/api/v1/attempts/"+id, "", "", "")
	for _, hidden := range []string{"canonical_text", "surface_text", "planned_units", "source_key_id", "provider", "lease_token", "mutation_count", "The café open tomorrow."} {
		if strings.Contains(w.Body.String(), hidden) {
			t.Fatal(hidden, w.Body.String())
		}
	}
	w = f.request("GET", "/api/v1/attempts/"+uuid.NewString(), "", "", "")
	if w.Code != 404 {
		t.Fatal(w.Code)
	}
}
func TestNativeListeningHTTPGuardsNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	w := f.request("PUT", "/api/v1/attempts/"+id+"/answer", string(answerPacket("x", "en")), uuid.NewString(), "")
	if w.Code != 412 {
		t.Fatal(w.Code)
	}
	r := httptest.NewRequest("POST", "/api/v1/attempts", strings.NewReader(`{}`))
	w = httptest.NewRecorder()
	f.s.Handler().ServeHTTP(w, r)
	if w.Code != 403 {
		t.Fatal(w.Code)
	}
}
func TestNativeListeningHistoryPositive(t *testing.T) {
	f := listeningCase(t)
	ids := map[string]bool{}
	for i := 0; i < 5; i++ {
		ids[f.start(t)] = true
	}
	cursor := ""
	seen := map[string]bool{}
	for {
		rows, next, e := f.s.Store.AttemptHistory(context.Background(), 2, cursor)
		requireListening(t, e)
		for _, v := range rows {
			a := v.(map[string]any)
			id := a["id"].(string)
			if !ids[id] || seen[id] {
				t.Fatal(id)
			}
			seen[id] = true
		}
		if next == "" {
			break
		}
		cursor = next
	}
	if len(seen) != 5 {
		t.Fatal(seen)
	}
}
func TestNativeListeningRestartPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("Persistent answer 🟠", "en"), false)
	requireListening(t, e)
	connection := f.s.Store.DB.Config().ConnConfig.ConnString()
	f.s.Store.DB.Close()
	reopened, e := OpenStorage(context.Background(), connection, "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	requireListening(t, e)
	t.Cleanup(reopened.DB.Close)
	server := NewServer(reopened, f.s.Origin, "http://unused.invalid")
	r, e := server.Store.Attempt(context.Background(), id)
	requireListening(t, e)
	if r.Attempt["answer_text"] != "Persistent answer 🟠" || r.Attempt["revision"] != float64(1) {
		t.Fatal(r)
	}
}
func TestNativeListeningCursorNegative(t *testing.T) {
	f := listeningCase(t)
	for _, cursor := range []string{"not-base64", "bm90LXZh bGlk"} {
		if _, _, e := f.s.Store.AttemptHistory(context.Background(), 2, cursor); !errors.Is(e, ErrInput) {
			t.Fatal(e)
		}
	}
	if _, _, e := f.s.Store.AttemptHistory(context.Background(), 101, ""); !errors.Is(e, ErrInput) {
		t.Fatal(e)
	}
}
func TestNativeListeningResultsBeforeSubmitNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	w := f.request("GET", "/api/v1/attempts/"+id+"/results", "", "", "")
	if w.Code != 409 {
		t.Fatal(w.Code, w.Body.String())
	}
}
func TestNativeListeningSequencePositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	revision := int64(0)
	for i := 0; i < 8; i++ {
		text := fmt.Sprintf("draft-%d", i)
		a, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), revision, answerPacket(text, "en"), false)
		requireListening(t, e)
		revision++
		if a["revision"] != float64(revision) || a["state"] != "started" {
			t.Fatal(a)
		}
	}
	a, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), revision, answerPacket("final", "en"), true)
	requireListening(t, e)
	if a["revision"] != float64(9) || a["state"] != "saved" {
		t.Fatal(a)
	}
}
func TestNativeListeningConcurrentPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	gate := make(chan struct{})
	results := make(chan error, 2)
	var wg sync.WaitGroup
	for _, text := range []string{"left", "right"} {
		wg.Add(1)
		go func(v string) {
			defer wg.Done()
			<-gate
			_, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket(v, "en"), false)
			results <- e
		}(text)
	}
	close(gate)
	wg.Wait()
	close(results)
	success, stale := 0, 0
	for e := range results {
		if e == nil {
			success++
		} else if errors.Is(e, ErrRevision) {
			stale++
		} else {
			t.Fatal(e)
		}
	}
	if success != 1 || stale != 1 {
		t.Fatal(success, stale)
	}
}
func TestNativeListeningSequenceStaleNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	for i := 0; i < 3; i++ {
		_, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), int64(i), answerPacket(fmt.Sprint(i), "en"), false)
		requireListening(t, e)
		if _, _, e = f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), int64(i), answerPacket("stale", "en"), true); !errors.Is(e, ErrRevision) {
			t.Fatal(e)
		}

		observed, e := f.s.Store.Attempt(context.Background(), id)
		requireListening(t, e)
		if observed.Attempt["answer_text"] != fmt.Sprint(i) || observed.Attempt["revision"] != float64(i+1) || observed.Attempt["state"] != "started" {
			t.Fatal(observed)
		}
	}
}
func TestNativeListeningImmutableNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	_, _, e := f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("new", "en"), false)
	requireListening(t, e)
	original, e := f.s.Store.ReadDocument(context.Background(), id)
	requireListening(t, e)
	var a map[string]any
	_ = json.Unmarshal(original.Payload, &a)
	if a["answer_text"] != "" || a["revision"] != float64(0) {
		t.Fatal(a)
	}
	if _, e = f.s.Store.DB.Exec(context.Background(), "UPDATE document SET payload='{}' WHERE id=$1", id); e == nil {
		t.Fatal("immutable document changed")
	}
}

func TestNativeListeningRetiredAudioPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	for _, state := range []string{"quarantined", "retired"} {
		_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE exercise_catalog SET availability=$2 WHERE id=$1", f.id, state)
		requireListening(t, e)
		w := f.request("GET", "/api/v1/attempts/"+id+"/audio", "", "", "")
		if w.Code != 200 || string(w.Body.Bytes()) != string(f.audio) {
			t.Fatal(w.Code, w.Body.String())
		}
	}
}
func TestNativeListeningRightsAudioNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE exercise_catalog SET availability='rights_restricted' WHERE id=$1", f.id)
	requireListening(t, e)
	w := f.request("GET", "/api/v1/attempts/"+id+"/audio", "", "", "")
	if w.Code != 403 || !strings.Contains(w.Body.String(), "RIGHTS_BLOCKED") || strings.Contains(w.Body.String(), "canonical_text") {
		t.Fatal(w.Code, w.Body.String())
	}
	// A media restriction must neither erase the frozen response nor stop draft storage.
	_, _, e = f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("Still saved", "en"), false)
	requireListening(t, e)
	record, e := f.s.Store.Attempt(context.Background(), id)
	requireListening(t, e)
	if record.Attempt["answer_text"] != "Still saved" {
		t.Fatal(record)
	}
}
