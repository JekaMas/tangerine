package app

// Constructed records/PCM and local HTTP packets, real PostgreSQL/MinIO,
// publication, list projections and resume owners. No hosted inference.
import (
	"context"
	"encoding/json"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/google/uuid"
)

func historyRequire(t *testing.T, err error) {
	t.Helper()
	if err != nil {
		t.Fatal(err)
	}
}
func historyClone(value map[string]any) map[string]any {
	raw, _ := json.Marshal(value)
	var result map[string]any
	_ = json.Unmarshal(raw, &result)
	return result
}

// Backdate immutable historical fixture envelopes in this disposable database
// only. Normal persistence and admission still run through production owners.
func historyCreatedAt(t *testing.T, s *Storage, id, at string) {
	ctx := context.Background()
	tx, e := s.DB.Begin(ctx)
	historyRequire(t, e)
	defer tx.Rollback(ctx)
	_, e = tx.Exec(ctx, "SET LOCAL session_replication_role='replica'")
	historyRequire(t, e)
	_, e = tx.Exec(ctx, "UPDATE document SET created_at=$2::timestamptz WHERE id=$1", id, at)
	historyRequire(t, e)
	historyRequire(t, tx.Commit(ctx))
}
func historyCase(t *testing.T, s *Server, title string) (string, string) {
	t.Helper()
	ctx := context.Background()
	asset, err := s.saveAudioBytes(ctx, speechWAV([]byte{7, 0, 8, 0, 9, 0}))
	historyRequire(t, err)
	b := preparationBlueprint(t, 1)
	b["public_context"] = title + ". Identify mistakes and offer corrections."
	_, _, candidate, _ := mutationFixture()
	settings := map[string]any{"blueprint": b, "configuration": DefaultConfiguration()}
	frozen := map[string]any{"plan": map[string]any{"case_version_id": "constructed-history"}, "pieces": []any{map[string]any{"utterance_id": "u1", "gap_after_ms": float64(0)}}}
	progress := map[string]any{"pieces": []any{map[string]any{"utterance_id": "u1", "sample_count": float64(3), "receipt_ids": []any{}}}}
	key := projectSpeechKey(settings, candidate, frozen, progress, asset.ID, asset.SHA, "2.0.0")
	source, err := s.Store.saveGroundTruth(ctx, key)
	historyRequire(t, err)
	tx, err := beginWrite(ctx, s.Store)
	historyRequire(t, err)
	defer tx.Rollback(ctx)
	id, err := s.Store.publishListeningCase(ctx, tx, source, b["task_components"].(map[string]any), title, "monologue")
	historyRequire(t, err)
	historyRequire(t, tx.Commit(ctx))
	historyCreatedAt(t, s.Store, id, "2026-10-25T12:30:00Z")
	return id, key["case_sha256"].(string)
}
func historyAttempt(t *testing.T, s *Server, id, sha, answer, at string, complete bool) string {
	t.Helper()
	ctx := context.Background()
	raw, _ := json.Marshal(map[string]any{"case_version_id": id, "case_sha256": sha, "requested_language": "en"})
	start, err := s.Store.StartAttempt(ctx, raw, uuid.NewString())
	historyRequire(t, err)
	aid := start["attempt_id"].(string)
	raw, _ = json.Marshal(map[string]any{"answer_text": answer, "requested_language": "en"})
	a, _, err := s.Store.WriteAnswer(ctx, aid, uuid.NewString(), 0, raw, false)
	historyRequire(t, err)
	// The terminal state is a constructed list-display fixture. This does not
	// claim evaluation/scoring or a genuine learner outcome.
	{
		if complete {
			a["state"] = "completed"
		}
		a["started_at"] = at
		a["revision"] = float64(2)
		rev := int64(1)
		original, err := s.Store.ReadDocument(ctx, aid)
		historyRequire(t, err)
		key, err := s.Store.ReadDocument(ctx, id)
		historyRequire(t, err)
		_, err = s.Store.WriteDocuments(ctx, []DocumentWrite{attemptWrite(a, uuid.NewString(), &rev, key.SHA, original.SHA)})
		historyRequire(t, err)
	}
	historyCreatedAt(t, s.Store, aid, at)
	return aid
}

func TestI19HistoryBrowserFixture(t *testing.T) {
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_HISTORY_EVIDENCE")
	if dir == "" {
		t.Fatal("owned evidence directory required")
	}
	s, p, calls := nativeSpeechFixture(t, 2)
	s.Origin = "http://localhost:3000"
	s.token = "history-owned-token"
	failed, err := s.RenderPreparation(ctx, p["id"].(string), uuid.NewString(), 1, nil)
	if err == nil || *calls != 2 {
		t.Fatal("expected constructed second-piece failure", err, *calls)
	}
	before := speechProgress(t, s, failed)
	firstAsset := before["pieces"].([]any)[0].(map[string]any)["asset_id"]
	var failureIDs []string
	for _, phase := range []string{"mutation", "canonical_text"} {
		copy := historyClone(failed)
		copy["id"] = uuid.NewString()
		copy["revision"] = float64(0)
		copy["created_at"] = "2026-10-25T12:30:00Z"
		copy["phase_states"] = map[string]any{"canonical_text": "complete", "mutation": "failed", "render": "not_started"}
		code, message, topic := "DEADLINE_EXCEEDED", "", "Picnic"
		if phase == "canonical_text" {
			copy["phase_states"] = map[string]any{"canonical_text": "failed", "mutation": "not_started", "render": "not_started"}
			code, message, topic = "PROVIDER_FAILURE", "service_unavailable", "Insurance"
		}
		copy["exercise_request"] = map[string]any{"topic": topic, "speaker_count": float64(1), "text_length_words": float64(90), "category_families": []any{}, "english_level": nil, "mutation_count": nil}
		copy["last_failure"] = map[string]any{"code": code, "message": message, "retryable": true, "request_id": uuid.NewString(), "object_id": nil, "details": []any{}}
		copy["render_progress_summary"] = speechProgressSummary(nil)
		raw, _ := json.Marshal(copy)
		w := DocumentWrite{ID: uuid.NewString(), Kind: "preparation-state", Version: "2.0.0", Scope: "local", Payload: raw, Head: &HeadWrite{ID: copy["id"].(string), State: "failed"}}
		rows, e := s.Store.DB.Query(ctx, "SELECT source_pointer,target_id,target_scope_id,target_kind,expected_sha256,relation FROM object_reference WHERE source_document_id=(SELECT document_id FROM entity_head WHERE id=$1)", failed["id"])
		historyRequire(t, e)
		for rows.Next() {
			var ref Reference
			historyRequire(t, rows.Scan(&ref.Pointer, &ref.ID, &ref.Scope, &ref.Kind, &ref.SHA, &ref.Relation))
			w.References = append(w.References, ref)
		}
		rows.Close()
		_, e = s.Store.WriteDocuments(ctx, []DocumentWrite{w})
		historyRequire(t, e)
		failureIDs = append(failureIDs, copy["id"].(string))
	}
	picnic, sha := historyCase(t, s, "Picnic")
	insurance, insuranceSHA := historyCase(t, s, "Insurance")
	changed, _ := historyCase(t, s, "Changed")
	a := historyAttempt(t, s, picnic, sha, strings.Repeat("A", 170), "2026-10-25T12:30:00Z", false)
	b := historyAttempt(t, s, picnic, sha, "  I heard\n two\t tickets.  ", "2026-10-25T13:30:00Z", true)
	c := historyAttempt(t, s, insurance, insuranceSHA, "", "2026-10-25T14:30:00Z", false)
	// Changing current catalog metadata cannot rename the heard snapshots.
	_, err = s.Store.DB.Exec(ctx, "UPDATE exercise_catalog SET title='Changed' WHERE id=$1", picnic)
	historyRequire(t, err)
	actual := s.Handler()
	read := func(path string) json.RawMessage {
		r := httptest.NewRequest("GET", path, nil)
		r.Header.Set("Authorization", "Bearer "+s.token)
		w := httptest.NewRecorder()
		actual.ServeHTTP(w, r)
		if w.Code != 200 {
			t.Fatal(path, w.Code, w.Body.String())
		}
		return append(json.RawMessage(nil), w.Body.Bytes()...)
	}
	t.Run("NativeProjection", func(t *testing.T) {
		rows, _, err := s.Store.AttemptHistory(ctx, 50, "")
		historyRequire(t, err)
		var found bool
		for _, item := range rows {
			r := item.(map[string]any)
			if r["id"] == a {
				found = true
				if r["exercise_title"] != "Picnic" || r["answer_excerpt"] != strings.Repeat("A", 160)+"…" {
					t.Fatal(r)
				}
			}
		}
		if !found {
			t.Fatal("seeded attempt absent")
		}
		pack := map[string]any{"attempts": read("/api/v1/attempts"), "preparations": read("/api/v1/preparations?view=public"), "library": read("/api/v1/library"), "ids": map[string]any{"attempts": []string{a, b, c}, "picnic": picnic, "insurance": insurance, "changed": changed, "resume": p["id"], "failures": failureIDs}, "first_piece_asset": firstAsset, "speech_dispatches_before": *calls}
		raw, _ := json.MarshalIndent(pack, "", "  ")
		historyRequire(t, os.WriteFile(filepath.Join(dir, "native-before.json"), raw, 0600))
	})
	t.Run("NativePagination", func(t *testing.T) {
		ids := map[any]bool{}
		cursor := ""
		for {
			rows, next, err := s.Store.AttemptHistory(ctx, 1, cursor)
			historyRequire(t, err)
			for _, row := range rows {
				id := row.(map[string]any)["id"]
				if ids[id] {
					t.Fatal("duplicate", id)
				}
				ids[id] = true
			}
			if next == "" {
				break
			}
			cursor = next
		}
		if len(ids) != 3 {
			t.Fatal(ids)
		}
	})
	var mu sync.Mutex
	counts := map[string]int{}
	scenario := ""
	listener, err := net.Listen("tcp", ":8080")
	historyRequire(t, err)
	server := &http.Server{ReadHeaderTimeout: 5 * time.Second, Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var rule struct {
			Scenario string         `json:"scenario"`
			Failures map[string]int `json:"failures"`
			Legacy   bool           `json:"legacy"`
		}
		raw, _ := os.ReadFile(filepath.Join(dir, "control.json"))
		_ = json.Unmarshal(raw, &rule)
		mu.Lock()
		if scenario != rule.Scenario {
			scenario = rule.Scenario
			counts = map[string]int{}
		}
		key := r.Method + " " + r.URL.Path
		counts[key]++
		n := counts[key]
		mu.Unlock()
		row, _ := json.Marshal(map[string]any{"scenario": rule.Scenario, "method": r.Method, "path": r.URL.Path, "query": r.URL.RawQuery, "occurrence": n})
		mu.Lock()
		file, e := os.OpenFile(filepath.Join(dir, "requests.jsonl"), os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
		if e == nil {
			_, _ = file.Write(append(row, '\n'))
			_ = file.Close()
		}
		mu.Unlock()
		if fail := rule.Failures[key]; fail < 0 || (fail > 0 && n <= fail) {
			writeJSON(w, 503, map[string]any{"code": "TEST_LIST_FAILURE", "message": "private backend detail"})
			return
		}
		if rule.Legacy && r.Method == "GET" {
			file := ""
			switch r.URL.Path {
			case "/api/v1/attempts":
				file = "legacy-attempts.json"
			case "/api/v1/preparations":
				file = "legacy-preparations.json"
			case "/api/v1/library":
				file = "legacy-library.json"
			}
			if file != "" {
				data, e := os.ReadFile(filepath.Join(dir, file))
				if e == nil {
					if r.URL.Path == "/api/v1/attempts" && r.URL.Query().Get("cursor") == "" {
						w.Header().Set("X-Tangerine-Next-Cursor", "legacy-next")
					}
					w.Header().Set("Content-Type", "application/json")
					_, _ = w.Write(data)
					return
				}
			}
		}
		if r.Method != "GET" && !strings.HasSuffix(r.URL.Path, ":resume") {
			writeJSON(w, 409, map[string]any{"code": "TEST_ACTION_EXCLUDED"})
			return
		}
		actual.ServeHTTP(w, r)
		if strings.HasSuffix(r.URL.Path, ":resume") {
			after, e := s.Store.Preparation(ctx, p["id"].(string))
			if e == nil {
				progress := speechProgress(t, s, after)
				raw, _ := json.MarshalIndent(map[string]any{"preparation": speechSummary(after), "first_piece_asset": progress["pieces"].([]any)[0].(map[string]any)["asset_id"], "speech_dispatches_after": *calls}, "", "  ")
				_ = os.WriteFile(filepath.Join(dir, "native-after.json"), raw, 0600)
			}
		}
	})}
	go func() { _ = server.Serve(listener) }()
	defer server.Close()
	historyRequire(t, os.WriteFile(filepath.Join(dir, "ready"), []byte("ready"), 0600))
	timer := time.NewTimer(60 * time.Minute)
	defer timer.Stop()
	tick := time.NewTicker(100 * time.Millisecond)
	defer tick.Stop()
	for {
		select {
		case <-timer.C:
			t.Fatal("fixture review deadline")
		case <-tick.C:
			if _, err := os.Stat(filepath.Join(dir, "done")); err == nil {
				return
			}
		}
	}
}

// Final readback of the exact browser-observed records. The interactive server
// is a test harness; its old default go-test timeout is not product behavior.
func TestI19HistoryPersistedReadback(t *testing.T) {
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_HISTORY_EVIDENCE")
	var before struct {
		IDs struct {
			Attempts []string `json:"attempts"`
			Resume   string   `json:"resume"`
		} `json:"ids"`
		First string `json:"first_piece_asset"`
	}
	raw, e := os.ReadFile(filepath.Join(dir, "native-before.json"))
	historyRequire(t, e)
	historyRequire(t, json.Unmarshal(raw, &before))
	store := preparationNative(t)
	p, e := store.Preparation(ctx, before.IDs.Resume)
	historyRequire(t, e)
	if p["last_failure"] != nil || p["phase_states"].(map[string]any)["render"] != "complete" {
		t.Fatal("resume not durable", p)
	}
	s := NewServer(store, "http://localhost:3000", "http://unreachable.invalid")
	progress := speechProgress(t, s, p)
	pieces := progress["pieces"].([]any)
	if len(pieces) != 2 || pieces[0].(map[string]any)["asset_id"] != before.First {
		t.Fatal("completed piece not retained", progress)
	}
	for _, id := range before.IDs.Attempts {
		record, e := store.Attempt(ctx, id)
		historyRequire(t, e)
		if record.Attempt["attempt_id"] != id {
			t.Fatal("wrong persisted answer", record)
		}
	}
	a, e := store.Attempt(ctx, before.IDs.Attempts[0])
	historyRequire(t, e)
	if a.Attempt["answer_text"] != strings.Repeat("A", 170) || a.Context["case_item"].(map[string]any)["title"] != "Picnic" {
		t.Fatal("heard context or answer changed", a)
	}
	rows, _, e := store.AttemptHistory(ctx, 50, "")
	historyRequire(t, e)
	if len(rows) != 3 {
		t.Fatal("history loss/duplication", rows)
	}
}
