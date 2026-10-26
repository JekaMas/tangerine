package app

// Disposable native storage/HTTP fixture. Constructed key/PCM are metadata only;
// no generator/evaluator/speech SDK is dispatched by this fixture or its UI tests.
import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"net"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func TestGuidedToolsNativeFixture(t *testing.T) {
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_GUIDED_EVIDENCE")
	if dir == "" {
		t.Fatal("evidence directory required")
	}
	var f listeningFixture
	var first, second, audioID string
	prior, readErr := os.ReadFile(filepath.Join(dir, "native-fixture.json"))
	if readErr == nil {
		var saved struct {
			Schema string `json:"schema"`
			First  string `json:"first_attempt"`
			Second string `json:"second_attempt"`
			Case   string `json:"case_id"`
			Audio  string `json:"audio_asset_id"`
		}
		requireListening(t, json.Unmarshal(prior, &saved))
		endpoint, e := url.Parse(os.Getenv("DATABASE_URL"))
		requireListening(t, e)
		query := endpoint.Query()
		query.Set("search_path", saved.Schema)
		endpoint.RawQuery = query.Encode()
		store, e := OpenStorage(ctx, endpoint.String(), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
		requireListening(t, e)
		t.Cleanup(store.DB.Close)
		f = listeningFixture{s: NewServer(store, "http://localhost:3000", "http://unused.invalid"), id: saved.Case}
		first, second, audioID = saved.First, saved.Second, saved.Audio
	} else {
		f = listeningCase(t)
		config, revision, e := f.s.Store.Configuration(ctx)
		requireListening(t, e)
		for _, item := range config["llm_profiles"].([]any) {
			p := item.(map[string]any)
			p["model"] = "Constructed local model"
			p["provider"] = "local_responses"
			p["endpoint"] = "http://127.0.0.1:9/v1/responses"
			p["auth_method"] = "local_none"
			p["billing_mode"] = "local"
			p["credential_ref"] = "local-none"
		}
		for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
			delete(config, k)
		}
		_, _, e = f.s.Store.PutConfiguration(ctx, mustJSON(config), uuid.NewString(), revision)
		requireListening(t, e)
		first, second = f.start(t), f.start(t)
		_, e = f.s.Store.DB.Exec(ctx, "UPDATE exercise_catalog SET title='Picnic practice' WHERE id=$1", f.id)
		requireListening(t, e)
		requireListening(t, f.s.Store.DB.QueryRow(ctx, "SELECT audio_asset_id FROM listening_case WHERE case_version_id=$1", f.id).Scan(&audioID))
		defaults, _, e := f.s.Store.Configuration(ctx)
		requireListening(t, e)
		bundle, e := f.s.Store.ActiveLabBundle(ctx)
		requireListening(t, e)
		var schema string
		requireListening(t, f.s.Store.DB.QueryRow(ctx, "SELECT current_schema()").Scan(&schema))
		fixture := map[string]any{"schema": schema, "first_attempt": first, "second_attempt": second, "case_id": f.id, "audio_asset_id": audioID, "configuration": defaults, "bundle": bundle}
		requireListening(t, os.WriteFile(filepath.Join(dir, "native-fixture.json"), mustJSON(fixture), 0600))
	}
	f.s.token = "listening-owned-token"
	listener, e := net.Listen("tcp", ":8080")
	requireListening(t, e)
	server := &http.Server{Handler: f.s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer server.Close()
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	deadline := time.After(2 * time.Hour)
	for {
		select {
		case <-deadline:
			t.Fatal("test-owned browser fixture did not finish")
		case <-ticker.C:
			if _, e := os.Stat(filepath.Join(dir, "done")); e != nil {
				continue
			}
			reports, e := f.s.Store.EmpiricalReports(ctx)
			requireListening(t, e)
			experiments, e := f.s.Store.QualityExperiments(ctx)
			requireListening(t, e)
			var calls int
			requireListening(t, f.s.Store.DB.QueryRow(ctx, "SELECT count(*) FROM document WHERE kind='provider-receipt'").Scan(&calls))
			_, firstErr := f.s.Store.Attempt(ctx, first)
			_, secondErr := f.s.Store.Attempt(ctx, second)
			_, audioErr := f.s.Store.ReadAsset(ctx, audioID)
			result := map[string]any{"provider_receipts": calls, "first_attempt_present": firstErr == nil, "second_attempt_present": secondErr == nil, "shared_audio_present": audioErr == nil, "reports": reports, "experiments": experiments}
			raw, _ := json.MarshalIndent(result, "", "  ")
			requireListening(t, os.WriteFile(filepath.Join(dir, "native-final.json"), raw, 0600))
			if calls != 0 {
				t.Fatal("starter flow dispatched provider", calls)
			}
			if secondErr != nil || audioErr != nil {
				t.Fatal("cleanup affected shared fixture", secondErr, audioErr)
			}
			return
		}
	}
}
