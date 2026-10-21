package app

// Constructed model/speech responses drive the genuine foreground owners; these
// tests do not establish model quality, accents or a hosted billing entitlement.
import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"io"
	"net/http"
	"net/http/httptest"
	"net/http/httputil"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"
)

func recoveryHTTP(t *testing.T, s *Server, path, key string, body any) *httptest.ResponseRecorder {
	t.Helper()
	r := httptest.NewRequest(http.MethodPost, path, strings.NewReader(string(mustJSON(body))))
	r.Header.Set("Authorization", "Bearer "+s.token)
	r.Header.Set("Origin", s.Origin)
	r.Header.Set("Content-Type", "application/json")
	r.Header.Set("Idempotency-Key", key)
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	return w
}
func recoveryRequest(t *testing.T, s *Server) CanonicalPreparationRequest {
	t.Helper()
	b, e := s.Store.WriteBlueprint(context.Background(), mustJSON(map[string]any{"exercise_request": qualityGenerationRequest()}), uuid.NewString())
	requireListening(t, e)
	c, _, e := s.Store.Configuration(context.Background())
	requireListening(t, e)
	return CanonicalPreparationRequest{BlueprintID: b["id"].(string), ConfigurationSHA: c["configuration_sha256"].(string), Sources: []string{}, Attempt: 1}
}
func TestNativeRecoveryGeneratePositive(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	s.token = "recovery-token"
	speech := qualitySpeechTarget(t, s, false)
	key := uuid.NewString()
	request := recoveryRequest(t, s)
	w := recoveryHTTP(t, s, "/api/v1/candidates:generate", key, request)
	if w.Code != 200 || calls.Load() != 2 || speech.Load() != 1 {
		t.Fatal(w.Code, w.Body.String(), calls.Load(), speech.Load())
	}
	var p map[string]any
	requireListening(t, json.Unmarshal(w.Body.Bytes(), &p))
	if p["audio_available"] != true || p["settings_asset_id"] != nil || p["key_id"] != nil {
		t.Fatal(p)
	}
	w = recoveryHTTP(t, s, "/api/v1/candidates:generate", key, request)
	if w.Code != 200 || calls.Load() != 2 || speech.Load() != 1 {
		t.Fatal("replay dispatched", w.Code, w.Body.String(), calls.Load(), speech.Load())
	}
	saveRecoveryControl(t, s)
}
func TestNativeRecoveryResumePositive(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	s.token = "recovery-token"
	failed := qualitySpeechTarget(t, s, true)
	w := recoveryHTTP(t, s, "/api/v1/candidates:generate", uuid.NewString(), recoveryRequest(t, s))
	if w.Code == 200 || calls.Load() != 2 || failed.Load() != 1 {
		t.Fatal(w.Code, w.Body.String(), calls.Load(), failed.Load())
	}
	var response map[string]any
	requireListening(t, json.Unmarshal(w.Body.Bytes(), &response))
	p := response["preparation"].(map[string]any)
	id := p["id"].(string)
	c, rev, e := s.Store.Configuration(context.Background())
	requireListening(t, e)
	c["speech_profile"] = "azure-standard-en-v1"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = s.Store.PutConfiguration(context.Background(), mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	speech := qualitySpeechTarget(t, s, false)
	resumeKey := uuid.NewString()
	w = recoveryHTTP(t, s, "/api/v1/preparations/"+id+":resume", resumeKey, map[string]any{})
	if w.Code != 200 || calls.Load() != 2 || speech.Load() != 1 {
		t.Fatal(w.Code, w.Body.String(), calls.Load(), speech.Load())
	}
	firstResult := w.Body.String()
	w = recoveryHTTP(t, s, "/api/v1/preparations/"+id+":resume", resumeKey, map[string]any{})
	if w.Code != 200 || w.Body.String() != firstResult || calls.Load() != 2 || speech.Load() != 1 {
		t.Fatal("Resume replay changed the action", w.Code, w.Body.String(), firstResult)
	}

	saved, e := s.Store.Preparation(context.Background(), id)
	requireListening(t, e)
	if saved["selected_speech_profile"] != "kokoro-local-en-v1" {
		t.Fatal("settings replaced", saved)
	}
	rows, e := s.Store.Preparations(context.Background(), 50, "")
	requireListening(t, e)
	if len(rows["items"].([]map[string]any)) != 1 || calls.Load() != 2 {
		t.Fatal("readback called provider")
	}
}
func TestNativeRecoveryUnknownNegative(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	s.token = "recovery-token"
	w := recoveryHTTP(t, s, "/api/v1/preparations/"+uuid.NewString()+":resume", uuid.NewString(), map[string]any{})
	if w.Code != 404 || calls.Load() != 0 {
		t.Fatal(w.Code, w.Body.String(), calls.Load())
	}
}
func TestNativeRecoveryMalformedNegative(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	s.token = "recovery-token"
	for _, body := range []any{map[string]any{}, map[string]any{"generation_attempt": -1}} {
		w := recoveryHTTP(t, s, "/api/v1/candidates:generate", uuid.NewString(), body)
		if w.Code == 200 || calls.Load() != 0 {
			t.Fatal(w.Code, calls.Load())
		}
	}
}
func TestNativeRecoveryMutationFailureNegative(t *testing.T) {
	s, calls := qualityGenerationServer(t, true)
	s.token = "recovery-token"
	speech := qualitySpeechTarget(t, s, false)
	w := recoveryHTTP(t, s, "/api/v1/candidates:generate", uuid.NewString(), recoveryRequest(t, s))
	if w.Code == 200 || calls.Load() != 3 || speech.Load() != 0 {
		t.Fatal(w.Code, w.Body.String(), calls.Load(), speech.Load())
	}
	rows, e := s.Store.Preparations(context.Background(), 50, "")
	requireListening(t, e)
	p := rows["items"].([]map[string]any)[0]
	if p["phase_states"].(map[string]any)["canonical_text"] != "complete" || p["canonical_asset_id"] == nil {
		t.Fatal("source lost", p)
	}
}

func TestNativeRecoveryDeletionPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	plan, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{id}})
	requireListening(t, e)
	if len(plan.Documents) == 0 || len(plan.Blocked) != 0 {
		t.Fatal(plan)
	}
	result, e := f.s.Store.ApplyDeletion(context.Background(), plan.ID, plan.Digest)
	requireListening(t, e)
	if result.State != "erased" {
		t.Fatal(result)
	}
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM entity_head WHERE id=$1", id).Scan(&n))
	if n != 0 {
		t.Fatal("attempt remains")
	}
	_, e = f.s.Store.ReadAsset(context.Background(), recoveryAudioID(t, f))
	requireListening(t, e)
}
func TestNativeRecoveryDeletionConfirmationNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	p, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{id}})
	requireListening(t, e)
	if _, e = f.s.Store.ApplyDeletion(context.Background(), p.ID, strings.Repeat("0", 64)); e == nil {
		t.Fatal("wrong confirmation admitted")
	}
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM entity_head WHERE id=$1", id).Scan(&n))
	if n != 1 {
		t.Fatal("unconfirmed erasure")
	}
}
func TestNativeRecoveryReferencedMediaNegative(t *testing.T) {
	f := listeningCase(t)
	p, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{recoveryAudioID(t, f)}})
	requireListening(t, e)
	if len(p.Blocked) == 0 {
		t.Fatal("referenced audio not blocked", p)
	}
	if _, e = f.s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest); e == nil {
		t.Fatal("referenced audio removed")
	}
}
func TestNativeRecoveryCleanupPreviewPositive(t *testing.T) {
	s := listeningNative(t)
	p, e := s.PlanDeletion(context.Background(), DeletionSelection{Orphans: true})
	requireListening(t, e)
	if p.State != "preview" || len(p.Documents) != 0 || len(p.Assets) != 0 {
		t.Fatal(p)
	}
}

func recoveryAudioID(t *testing.T, f listeningFixture) string {
	t.Helper()
	var id string
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT audio_asset_id FROM listening_case WHERE case_version_id=$1", f.id).Scan(&id))
	return id
}
func TestNativeRecoveryScoredDeletionPositive(t *testing.T) {
	f := scoringFixture(t, false)
	_, e := f.interpret(t, uuid.NewString())
	requireListening(t, e)
	p, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{f.attempt}})
	requireListening(t, e)
	if len(p.Blocked) > 0 {
		t.Fatal(p)
	}
	_, e = f.s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest)
	requireListening(t, e)
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE payload->>'attempt_id'=$1", f.attempt).Scan(&n))
	if n != 0 {
		t.Fatal("answer/result remains", n)
	}
}
func TestNativeRecoveryCaseDeletionPositive(t *testing.T) {
	f := listeningCase(t)
	attempt := f.start(t)
	p, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{f.id}})
	requireListening(t, e)
	if len(p.Blocked) > 0 || !containsString(p.Heads, attempt) {
		t.Fatal(p)
	}
	_, e = f.s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest)
	requireListening(t, e)
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM listening_case WHERE case_version_id=$1", f.id).Scan(&n))
	if n != 0 {
		t.Fatal("case remains")
	}
}
func TestNativeRecoveryChangedPlanNegative(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	p, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{id}})
	requireListening(t, e)
	_, _, e = f.s.Store.WriteAnswer(context.Background(), id, uuid.NewString(), 0, answerPacket("Retained new draft.", "en"), false)
	requireListening(t, e)
	if _, e = f.s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest); e == nil {
		t.Fatal("changed preview applied")
	}
}
func TestNativeRecoveryWorkspaceSetupPositive(t *testing.T) {
	s, _ := qualityGenerationServer(t, false)
	public := preparationNative(t)
	c, _, e := s.Store.Configuration(context.Background())
	requireListening(t, e)
	t.Log("source", c["llm_profiles"].([]any)[0].(map[string]any)["model"], c["llm_profile"])
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, rev, e := public.Configuration(context.Background())
	requireListening(t, e)
	_, _, e = public.PutConfiguration(context.Background(), mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	f := recoveryWorkspaceCase(t)
	fresh, _, e := f.s.Store.Configuration(context.Background())
	requireListening(t, e)
	t.Log("stored", fresh["llm_profiles"].([]any)[0].(map[string]any)["model"], fresh["llm_profile"])
	f.start(t)
}
func TestNativeRecoverySourceDeletionPositive(t *testing.T) {
	f := sourceFixture(t)
	f.bea(t)
	run := f.run(t, "native", nil)
	p, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{f.release.ID}})
	requireListening(t, e)
	if len(p.Blocked) > 0 || len(p.Source.Files) != 5 || !containsString(p.Source.Imports, run.Report.ID) {
		t.Fatal(p)
	}
	_, e = f.s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest)
	requireListening(t, e)
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID).Scan(&n))
	if n != 0 {
		t.Fatal("source records remain")
	}
}
func TestNativeRecoveryPrivateBytesDeletionPositive(t *testing.T) {
	f := scoringFixture(t, false)
	f.attempt = f.start(t)
	marker := "PRIVATE-ERASE-" + uuid.NewString()
	_, _, e := f.s.Store.WriteAnswer(context.Background(), f.attempt, uuid.NewString(), 0, answerPacket("Use opens. "+marker, "en"), true)
	requireListening(t, e)
	_, e = f.interpret(t, uuid.NewString())
	requireListening(t, e)
	keys := []string{}
	for object := range f.s.Store.Media.ListObjects(context.Background(), f.s.Store.Bucket, minio.ListObjectsOptions{Recursive: true}) {
		if object.Err != nil {
			t.Fatal(object.Err)
		}
		r, e := f.s.Store.Media.GetObject(context.Background(), f.s.Store.Bucket, object.Key, minio.GetObjectOptions{})
		requireListening(t, e)
		body, e := io.ReadAll(r)
		r.Close()
		requireListening(t, e)
		if strings.Contains(string(body), marker) {
			keys = append(keys, object.Key)
		}
	}
	if len(keys) < 3 {
		t.Fatal("missing independent private-body observations", len(keys))
	}
	p, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{f.attempt}})
	requireListening(t, e)
	_, e = f.s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest)
	requireListening(t, e)
	for _, key := range keys {
		_, e = f.s.Store.Media.StatObject(context.Background(), f.s.Store.Bucket, key, minio.StatObjectOptions{})
		if e == nil {
			t.Fatalf("private copied answer remains in %s; plan=%+v", key, p)
		}
	}
}
func TestNativeRecoveryCancelNegative(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	s.token = "recovery-token"
	qualitySpeechTarget(t, s, false)
	entered := make(chan struct{})
	release := make(chan struct{})
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/internal/v1/piece" {
			close(entered)
			select {
			case <-r.Context().Done():
			case <-release:
			}
			return
		}
		var input map[string]any
		_ = json.NewDecoder(r.Body).Decode(&input)
		if r.URL.Path == "/internal/v1/plan" {
			_ = json.NewEncoder(w).Encode(map[string]any{"pieces": input["plan"].(map[string]any)["turns"], "model_context": map[string]any{"origin": "constructed"}})
		}
	}))
	defer target.Close()
	s.SpeechURL = target.URL
	request := recoveryRequest(t, s)
	ctx, cancel := context.WithCancel(context.Background())
	req := httptest.NewRequest("POST", "/api/v1/candidates:generate", strings.NewReader(string(mustJSON(request)))).WithContext(ctx)
	for k, v := range map[string]string{"Authorization": "Bearer " + s.token, "Origin": s.Origin, "Content-Type": "application/json", "Idempotency-Key": uuid.NewString()} {
		req.Header.Set(k, v)
	}
	w := httptest.NewRecorder()
	done := make(chan struct{})
	go func() { s.Handler().ServeHTTP(w, req); close(done) }()
	<-entered
	rows0, pe := s.Store.Preparations(context.Background(), 50, "")
	requireListening(t, pe)
	preparing := rows0["items"].([]map[string]any)[0]
	plan, pe := s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{preparing["id"].(string)}})
	requireListening(t, pe)
	if len(plan.Blocked) == 0 {
		t.Fatal("active preparation deletion was not blocked")
	}
	cancel()
	<-done
	close(release)
	if w.Code == 200 || calls.Load() != 2 {
		t.Fatal(w.Code, calls.Load())
	}
	rows, e := s.Store.Preparations(context.Background(), 50, "")
	requireListening(t, e)
	p := rows["items"].([]map[string]any)[0]
	states := p["phase_states"].(map[string]any)
	if states["canonical_text"] != "complete" || states["mutation"] != "complete" || states["render"] == "complete" {
		t.Fatal(states)
	}
	speech := qualitySpeechTarget(t, s, false)
	fresh := NewServer(s.Store, s.Origin, s.SpeechURL)
	fresh.token = s.token
	w = recoveryHTTP(t, fresh, "/api/v1/preparations/"+p["id"].(string)+":resume", uuid.NewString(), map[string]any{})
	if w.Code != 200 || calls.Load() != 2 || speech.Load() != 1 {
		t.Fatal(w.Code, w.Body.String(), calls.Load(), speech.Load())
	}
}
func TestNativeRecoveryConcurrentReplayNegative(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	s.token = "recovery-token"
	qualitySpeechTarget(t, s, false)
	original, _ := url.Parse(s.SpeechURL)
	proxy := httputil.NewSingleHostReverseProxy(original)
	entered, release := make(chan struct{}), make(chan struct{})
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/internal/v1/piece" {
			close(entered)
			<-release
		}
		proxy.ServeHTTP(w, r)
	}))
	defer target.Close()
	s.SpeechURL = target.URL
	key := uuid.NewString()
	request := recoveryRequest(t, s)
	done := make(chan *httptest.ResponseRecorder, 1)
	go func() { done <- recoveryHTTP(t, s, "/api/v1/candidates:generate", key, request) }()
	<-entered
	w := recoveryHTTP(t, s, "/api/v1/candidates:generate", key, request)
	close(release)
	first := <-done
	if w.Code != 409 || !strings.Contains(w.Body.String(), "LEASE_ACTIVE") || first.Code != 200 || calls.Load() != 2 {
		t.Fatal(w.Code, w.Body.String(), first.Code, first.Body.String(), calls.Load())
	}
}
func TestNativeRecoveryGeneratedDeletionPositive(t *testing.T) {
	s, _ := qualityGenerationServer(t, false)
	s.token = "recovery-token"
	qualitySpeechTarget(t, s, false)
	w := recoveryHTTP(t, s, "/api/v1/candidates:generate", uuid.NewString(), recoveryRequest(t, s))
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	var response map[string]any
	requireListening(t, json.Unmarshal(w.Body.Bytes(), &response))
	prep, e := s.Store.Preparation(context.Background(), response["id"].(string))
	requireListening(t, e)
	var published string
	requireListening(t, s.Store.DB.QueryRow(context.Background(), "SELECT case_version_id FROM listening_case WHERE source_key_id=$1", prep["key_id"]).Scan(&published))
	p, e := s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{published}})
	requireListening(t, e)
	if len(p.Blocked) > 0 || !containsString(p.Documents, prep["key_id"].(string)) || !containsString(p.Heads, prep["id"].(string)) {
		t.Fatal("preparation/key outside deletion plan", p)
	}
	_, e = s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest)
	requireListening(t, e)
	var n int
	requireListening(t, s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE id=$1 OR payload->>'id'=$2", prep["key_id"], prep["id"]).Scan(&n))
	if n != 0 {
		t.Fatal("generated key/text history remains")
	}
}

func saveRecoveryControl(t *testing.T, s *Server) {
	t.Helper()
	root := os.Getenv("TANGERINE_RECOVERY_CAPTURE")
	if root == "" {
		return
	}
	rows, e := s.Store.DB.Query(context.Background(), "SELECT id,kind,payload FROM document WHERE kind IN('provider-receipt','llm-context-snapshot') ORDER BY id")
	requireListening(t, e)
	documents := []any{}
	receipts, snapshots, speechReceipts := 0, 0, 0
	for rows.Next() {
		var id, kind string
		var raw []byte
		requireListening(t, rows.Scan(&id, &kind, &raw))
		documents = append(documents, map[string]any{"id": id, "kind": kind, "payload": json.RawMessage(raw)})
		if kind == "provider-receipt" {
			var payload map[string]any
			requireListening(t, json.Unmarshal(raw, &payload))
			if payload["stage"] == "case_generation" {
				receipts++
			} else {
				speechReceipts++
			}
		} else {
			snapshots++
		}
	}
	rows.Close()
	requireListening(t, rows.Err())
	if receipts != 2 || snapshots != 2 || speechReceipts != 1 {
		t.Fatal("native/independent fixture dispatch mismatch", receipts, snapshots, speechReceipts)
	}
	requireListening(t, os.WriteFile(filepath.Join(root, "control-native.json"), mustJSON(map[string]any{"origin": "constructed model transport; genuine native owners", "independent_fixture_dispatches": 2, "native_receipts": receipts, "native_snapshots": snapshots, "native_speech_receipts": speechReceipts, "independent_speech_dispatches": 1, "actual_llm_inference_calls": 0, "documents": documents, "proof": "Deterministic coordination/context capture only. Unchanged model quality evidence is retained separately."}), 0600))
}

func TestNativeRecoveryCanonicalResumeReplayPositive(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	s.token = "recovery-token"
	speech := qualitySpeechTarget(t, s, false)
	c, rev, e := s.Store.Configuration(context.Background())
	requireListening(t, e)
	profile := c["llm_profiles"].([]any)[0].(map[string]any)
	endpoint, _ := url.Parse(profile["endpoint"].(string))
	proxy := httputil.NewSingleHostReverseProxy(endpoint)
	var dispatches atomic.Int32
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if dispatches.Add(1) <= 2 {
			w.WriteHeader(503)
			_, _ = w.Write([]byte(`{"error":{"code":"constructed_unavailable"}}`))
			return
		}
		proxy.ServeHTTP(w, r)
	}))
	defer target.Close()
	profile["endpoint"] = target.URL + "/v1/responses"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = s.Store.PutConfiguration(context.Background(), mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	w := recoveryHTTP(t, s, "/api/v1/candidates:generate", uuid.NewString(), recoveryRequest(t, s))
	if w.Code == 200 {
		t.Fatal("failure hidden")
	}
	var result map[string]any
	requireListening(t, json.Unmarshal(w.Body.Bytes(), &result))
	id := result["preparation"].(map[string]any)["id"].(string)
	key := uuid.NewString()
	w = recoveryHTTP(t, s, "/api/v1/preparations/"+id+":resume", key, map[string]any{})
	if w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	first := w.Body.String()
	w = recoveryHTTP(t, s, "/api/v1/preparations/"+id+":resume", key, map[string]any{})
	if w.Code != 200 || w.Body.String() != first || dispatches.Load() != 4 || calls.Load() != 2 || speech.Load() != 1 {
		t.Fatal("canonical Resume replay", w.Code, w.Body.String(), dispatches.Load(), calls.Load(), speech.Load())
	}
}

func TestNativeRecoveryExpiredDeletionPositive(t *testing.T) {
	f := listeningCase(t)
	id := f.start(t)
	op, e := f.s.Store.ReserveOperation(context.Background(), OperationRequest{Name: "expired_recovery", Key: uuid.NewString(), Path: "/test", Body: mustJSON(map[string]any{"attempt_id": id})})
	requireListening(t, e)
	_, e = f.s.Store.DB.Exec(context.Background(), "UPDATE operation SET subject_id=$2,state='running',started_at=clock_timestamp()-interval '271 seconds' WHERE id=$1", op.ID, id)
	requireListening(t, e)
	p, e := f.s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{id}})
	requireListening(t, e)
	if len(p.Blocked) > 0 {
		t.Fatal("expired operation permanently blocks cleanup", p)
	}
	_, e = f.s.Store.ApplyDeletion(context.Background(), p.ID, p.Digest)
	requireListening(t, e)
	var n int
	requireListening(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM operation WHERE id=$1", op.ID).Scan(&n))
	if n != 0 {
		t.Fatal("expired operation retained", n)
	}
}
func TestNativeRecoveryExperimentDeletionPositive(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	p, e := s.Store.AdmitExperiment(context.Background(), qualitySimpleSubmission(t, s, "generation_pipeline", qualityGenerationRequest()))
	requireListening(t, e)
	p, e = s.RunQualityExperiment(context.Background(), p.ID, false, nil)
	requireListening(t, e)
	if p.Status != "completed" || calls.Load() != 2 || len(p.Rows[0].Receipts) != 2 || p.Comparison == nil {
		t.Fatal("fixture incomplete", p)
	}
	plan, e := s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{p.ID}})
	requireListening(t, e)
	for _, id := range p.Rows[0].Receipts {
		if !containsString(plan.Documents, id) {
			t.Error("experiment receipt omitted", id)
		}
	}
	if !containsString(plan.Assets, *p.Comparison) {
		t.Error("comparison artifact omitted", *p.Comparison)
	}
	if t.Failed() {
		t.FailNow()
	}
	_, e = s.Store.ApplyDeletion(context.Background(), plan.ID, plan.Digest)
	requireListening(t, e)
	for _, id := range p.Rows[0].Receipts {
		var n int
		requireListening(t, s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE id=$1", id).Scan(&n))
		if n != 0 {
			t.Fatal("receipt retained", id)
		}
	}
	if _, e = s.Store.ReadAsset(context.Background(), *p.Comparison); e == nil {
		t.Fatal("comparison bytes retained")
	}
	var remaining int
	requireListening(t, s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM quality_call WHERE receipt_id=ANY($1)", p.Rows[0].Receipts).Scan(&remaining))
	if remaining != 0 {
		t.Fatal("experiment call index retained", remaining)
	}
	if calls.Load() != 2 {
		t.Fatal("deletion invoked provider", calls.Load())
	}
}

func TestNativeRecoveryExperimentReferenceNegative(t *testing.T) {
	s, calls := qualityGenerationServer(t, false)
	p, e := s.Store.AdmitExperiment(context.Background(), qualitySimpleSubmission(t, s, "generation_pipeline", qualityGenerationRequest()))
	requireListening(t, e)
	p, e = s.RunQualityExperiment(context.Background(), p.ID, false, nil)
	requireListening(t, e)
	if p.Status != "completed" || calls.Load() != 2 || p.Comparison == nil {
		t.Fatal("fixture incomplete", p)
	}
	for _, id := range []string{p.Rows[0].Receipts[0], *p.Comparison} {
		plan, e := s.Store.PlanDeletion(context.Background(), DeletionSelection{IDs: []string{id}})
		requireListening(t, e)
		if len(plan.Blocked) == 0 {
			t.Error("retained experiment reference was not protected", id)
			continue
		}
		if _, e = s.Store.ApplyDeletion(context.Background(), plan.ID, plan.Digest); e != ErrRevision {
			t.Error("wrong retained-reference rejection", id, e)
		}
	}
	retained, e := s.Store.QualityExperiment(context.Background(), p.ID)
	requireListening(t, e)
	if retained.Status != "completed" || calls.Load() != 2 {
		t.Fatal("retained experiment changed", retained)
	}
	if _, e = s.Store.ReadAsset(context.Background(), *p.Comparison); e != nil {
		t.Fatal("comparison lost", e)
	}
}
