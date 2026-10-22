package app

// Interface evidence: real Go/HTTP/Postgres/MinIO owners; only model replies and
// response timing are constructed. Form generation stops after real blueprint save.
import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	"github.com/google/uuid"
	"tangerine.local/api/internal/lab"
)

func TestNativeUsabilitySummaryPersistencePositive(t *testing.T) {
	s, request, client, calls := prepareNativeFixtureRequest(t, "", http.StatusOK, func(input map[string]any) {
		input["exercise_request"].(map[string]any)["english_level"] = "B2"
		input["exercise_request"].(map[string]any)["mutation_count"] = float64(0)
	})
	p, err := s.PrepareCanonical(context.Background(), request, uuid.NewString(), client)
	requireListening(t, err)
	saved, err := s.Store.Preparation(context.Background(), p["id"].(string))
	requireListening(t, err)
	r := speechSummary(saved)["exercise_request"].(map[string]any)
	if r["english_level"] != "B2" || r["mutation_count"] != float64(0) || *calls != 1 {
		t.Fatal(r, *calls)
	}
}

func TestNativeUsabilityBrowserFixture(t *testing.T) {
	f := scoringFixture(t, false)
	dir := os.Getenv("TANGERINE_USABILITY_EVIDENCE")
	if dir == "" {
		t.Fatal("evidence directory required")
	}
	f.modePath = filepath.Join(dir, "mode")
	f.s.token = "listening-owned-token"
	f.s.Origin = os.Getenv("TANGERINE_TEST_ORIGIN")
	// Seed an actual initial preparation through the real freeze/checkpoint owner.
	// It remains not generated; this fixture proves requested-settings display only.
	ctx := context.Background()
	blueprint, err := f.s.Store.WriteBlueprint(ctx, []byte(`{"exercise_request":{"topic":"Saved seed settings","speaker_count":1,"text_length_words":123,"english_level":"A2","mutation_count":0,"category_families":["grammar"]}}`), uuid.NewString())
	requireListening(t, err)
	configuration, _, err := f.s.Store.Configuration(ctx)
	requireListening(t, err)
	op, err := f.s.Store.ReserveOperation(ctx, OperationRequest{Name: "canonical_prepare", Key: uuid.NewString(), Path: "/api/v1/candidates:generate", Body: json.RawMessage(`{}`)})
	requireListening(t, err)
	_, err = f.s.freezePreparation(ctx, blueprint, configuration, lab.Shipped(), op)
	requireListening(t, err)
	var reads, submissions, preparations atomic.Int64
	gate := func(stage string, r *http.Request) bool {
		for {
			value, _ := os.ReadFile(filepath.Join(dir, "gate"))
			if strings.TrimSpace(string(value)) != stage {
				return true
			}
			_ = os.WriteFile(filepath.Join(dir, "entered"), []byte(stage), 0600)
			select {
			case <-r.Context().Done():
				return false
			case <-time.After(20 * time.Millisecond):
			}
		}
	}
	wrap := func(handler http.Handler, feedback bool) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			stage := "feedback"
			if !feedback {
				body, _ := io.ReadAll(r.Body)
				r.Body = io.NopCloser(bytes.NewReader(body))
				if strings.Contains(string(body), `\"ground_truth\"`) {
					stage = "matching"
				} else {
					stage = "extraction"
				}
			}
			if gate(stage, r) {
				handler.ServeHTTP(w, r)
			}
		})
	}
	f.model.Config.Handler = wrap(f.model.Config.Handler, false)
	f.feedback.Config.Handler = wrap(f.feedback.Config.Handler, true)
	listener, err := net.Listen("tcp", ":8080")
	requireListening(t, err)
	server := &http.Server{ReadHeaderTimeout: 5 * time.Second, Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/test-counts" {
			writeJSON(w, 200, map[string]any{"extractions": f.extracts.Load(), "mappings": f.maps.Load(), "feedback": f.feedbackCalls.Load(), "reads": reads.Load(), "submissions": submissions.Load(), "preparations": preparations.Load()})
			return
		}
		if r.Method == "GET" && strings.HasPrefix(r.URL.Path, "/api/v1/attempts/") {
			reads.Add(1)
			if _, err := os.Stat(filepath.Join(dir, "fail-reads")); err == nil {
				writeJSON(w, 503, map[string]any{"code": "TEST_READ_FAILURE"})
				return
			}
		}
		if strings.HasSuffix(r.URL.Path, ":submit") {
			submissions.Add(1)
		}
		if r.URL.Path == "/api/v1/candidates:generate" {
			var request map[string]any
			_ = json.NewDecoder(r.Body).Decode(&request)
			blueprint, err := f.s.Store.Blueprint(r.Context(), request["blueprint_id"].(string))
			if err != nil {
				t.Error(err)
				writeJSON(w, 503, map[string]any{})
				return
			}
			preparations.Add(1)
			_ = os.WriteFile(filepath.Join(dir, "blueprint.json"), mustJSON(blueprint), 0600)
			writeJSON(w, 503, map[string]any{"code": "TEST_GENERATION_PAUSED", "message": "Test-owned generation is paused after saving the request."})
			return
		}
		f.s.Handler().ServeHTTP(w, r)
	})}
	go func() { _ = server.Serve(listener) }()
	defer server.Shutdown(context.Background())
	requireListening(t, os.WriteFile(filepath.Join(dir, "fixture.json"), mustJSON(map[string]any{"case_id": f.id, "case_sha256": f.sha}), 0600))
	for i := 0; i < 6000; i++ {
		if _, err := os.Stat(filepath.Join(dir, "done")); err == nil {
			return
		}
		time.Sleep(100 * time.Millisecond)
	}
	t.Fatal("browser exceeded foreground test deadline")
}
