package app

// Constructed canonical/mutation LLM responses; actual local Kokoro recordings,
// the production planner/composer/key/finalizer, real PostgreSQL and private
// MinIO. Once rendered, exact local recordings are replayed rather than inferred
// again. No hosted model, paid provider or learner qualification gate.
import (
	"bytes"
	"context"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/scoring"
	"testing"
)

func overlapCheck(t *testing.T, e error) {
	t.Helper()
	if e != nil {
		t.Fatal(e)
	}
}
func overlapJSON(v any) []byte { raw, _ := json.MarshalIndent(v, "", "  "); return raw }
func overlapScene(t *testing.T, id, kind string, mutation bool) map[string]any {
	_, _, c, _ := overlapFixture(t, kind)
	c["blueprint_id"] = id
	if kind == "cooperative_backchannel" {
		text := "Feel free to say mm-hm while I speak. We will visit the museum tomorrow morning."
		turns := c["utterances"].([]any)
		turns[0].(map[string]any)["canonical_text"] = text
		turns[0].(map[string]any)["surface_text"] = text
		turns[1].(map[string]any)["canonical_text"] = "Mm-hm."
		turns[1].(map[string]any)["surface_text"] = "Mm-hm."
		a := strings.Index(text, "visit the museum")
		scope := map[string]any{"start_cp": float64(a), "end_cp": float64(a + 16), "exact_text": "visit the museum"}
		c["overlap_intents"].([]any)[0].(map[string]any)["target_scope"] = scope
		u := c["planned_units"].([]any)[0].(map[string]any)
		u["text_spans"] = []any{map[string]any{"utterance_id": "u1", "span": scope}}
		u["rationale"] = "The invited quiet backchannel leaves the main message audible."
		u["correction_eligible"] = false
		u["corrections"] = []any{}
		u["explanation_eligible"] = false
		u["rationale_required_propositions"] = []any{}
	}
	if !mutation {
		c["planned_units"] = []any{}
		c["overlap_intents"] = []any{}
	}
	return c
}
func nativeOverlap(t *testing.T, kind string, interrupt bool) {
	ctx := context.Background()
	dir := filepath.Join(os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE"), kind)
	overlapCheck(t, os.MkdirAll(dir, 0700))
	cache := os.Getenv("TANGERINE_OVERLAP_RECORDINGS")
	overlapCheck(t, os.MkdirAll(cache, 0700))
	s, r, _, _ := prepareNativeFixtureOptions(t, "", 200, func(c map[string]any) {
		c["speech_profile"] = "kokoro-local-en-v1"
		c["llm_lab_capture_content"] = true
		c["llm_lab_trace_enabled"] = true
		p := c["llm_profiles"].([]any)[0].(map[string]any)
		p["context_budget_tokens"] = 1000000
		p["structured_output"] = false
	}, func(b map[string]any) {
		request := b["exercise_request"].(map[string]any)
		request["speaker_count"] = 2
		request["category_ids"] = []any{"discourse.turn_taking"}
		if kind == "cooperative_backchannel" {
			request["mutation_count"] = 0
		} else {
			request["mutation_count"] = 1
		}
		b["speakers"] = []any{explicitSpeechSpeaker("s1", "af_heart"), explicitSpeechSpeaker("s2", "am_adam")}
	})
	mutation := false
	textClient := &http.Client{Transport: preparationTrip(func(req *http.Request) (*http.Response, error) {
		input, _ := io.ReadAll(req.Body)
		overlapCheck(t, os.WriteFile(filepath.Join(dir, fmt.Sprintf("text-context-%t.json", mutation)), input, 0600))
		c := overlapScene(t, r.BlueprintID, kind, mutation)
		body := overlapJSON(map[string]any{"id": "constructed-overlap-text", "object": "response", "status": "completed", "model": "constructed-clean-text", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": string(overlapJSON(c))}}}}})
		return &http.Response{StatusCode: 200, Header: http.Header{"Content-Type": []string{"application/json"}}, Body: io.NopCloser(bytes.NewReader(body))}, nil
	})}
	p, e := s.PrepareCanonical(ctx, r, uuid.NewString(), textClient)
	overlapCheck(t, e)
	id := p["id"].(string)
	r.PreparationID = &id
	r.Attempt = 2
	mutation = true
	p, e = s.PrepareMutation(ctx, r, uuid.NewString(), textClient)
	overlapCheck(t, e)
	var pieceCalls, modelCalls atomic.Int32
	renderCtx, cancel := context.WithCancel(ctx)
	defer cancel()
	interrupted := false
	worker := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		raw, _ := io.ReadAll(req.Body)
		var packet map[string]any
		overlapCheck(t, json.Unmarshal(raw, &packet))
		if req.URL.Path == "/internal/v1/quality" && interrupt && !interrupted {
			interrupted = true
			cancel()
			w.WriteHeader(503)
			return
		}
		if req.URL.Path == "/internal/v1/piece" {
			pieceCalls.Add(1)
			key := lab.Hash(map[string]any{"profile": packet["profile"], "turn": packet["turn"]})
			path := filepath.Join(cache, key+".json")
			cached, err := os.ReadFile(path)
			if err == nil {
				w.Header().Set("Content-Type", "application/json")
				_, _ = w.Write(cached)
				return
			}
			if !os.IsNotExist(err) || os.Getenv("TANGERINE_OVERLAP_ALLOW_LOCAL") != "1" {
				t.Error("missing retained recording; local synthesis was not enabled", key)
				w.WriteHeader(503)
				return
			}
			modelCalls.Add(1)
			result, err := s.speechCall(ctx, req.URL.Path, packet, &http.Client{Transport: preparationTrip(func(original *http.Request) (*http.Response, error) {
				original.URL.Scheme = "http"
				original.URL.Host = strings.TrimPrefix(os.Getenv("TANGERINE_SPEECH_TEST_URL"), "http://")
				original.Header.Set("Authorization", "Bearer actual-local-speech-test")
				return http.DefaultTransport.RoundTrip(original)
			})})
			if err != nil {
				t.Error(err)
				w.WriteHeader(503)
				return
			}
			body := overlapJSON(result)
			overlapCheck(t, os.WriteFile(path, body, 0600))
			w.Header().Set("Content-Type", "application/json")
			_, _ = w.Write(body)
			return
		}
		upstream, _ := http.NewRequest(req.Method, os.Getenv("TANGERINE_SPEECH_TEST_URL")+req.URL.Path, bytes.NewReader(raw))
		upstream.Header.Set("Authorization", "Bearer actual-local-speech-test")
		upstream.Header.Set("Content-Type", "application/json")
		res, err := http.DefaultClient.Do(upstream)
		if err != nil {
			t.Error(err)
			w.WriteHeader(503)
			return
		}
		defer res.Body.Close()
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(res.StatusCode)
		_, _ = io.Copy(w, res.Body)
	}))
	defer worker.Close()
	s.SpeechURL = worker.URL
	s.speechToken = "actual-local-speech-test"
	action := uuid.NewString()
	p, e = s.RenderPreparation(renderCtx, id, action, 1, nil)
	if interrupt {
		if e == nil {
			t.Fatal("test-owned cancellation did not interrupt finalization")
		}
		before := speechProgress(t, s, p)
		if before["composition"] == nil || before["assembled_asset_id"] != nil {
			t.Fatal("resolved composition not durable before mixing", before)
		}
		overlapCheck(t, os.WriteFile(filepath.Join(dir, "interrupted-progress.json"), overlapJSON(before), 0600))
		calls := pieceCalls.Load()
		restarted := NewServer(preparationNative(t), s.Origin, s.SpeechURL)
		restarted.speechToken = s.speechToken
		s = restarted
		p, e = s.RenderPreparation(ctx, id, uuid.NewString(), 2, nil)
		overlapCheck(t, e)
		if pieceCalls.Load() != calls {
			t.Fatal("resume repeated synthesis")
		}
	} else {
		overlapCheck(t, e)
	}
	if p["phase_states"].(map[string]any)["render"] != "complete" {
		t.Fatal(p)
	}
	progress := speechProgress(t, s, p)
	comp, ok := savedComposition(progress)
	if !ok || len(comp.Overlaps) != 1 {
		t.Fatal(progress)
	}
	keyDoc, e := s.Store.ReadDocument(ctx, p["key_id"].(string))
	overlapCheck(t, e)
	var key map[string]any
	overlapCheck(t, json.Unmarshal(keyDoc.Payload, &key))
	overlapCheck(t, os.WriteFile(filepath.Join(dir, "key.json"), keyDoc.Payload, 0600))
	audio, e := s.Store.ReadAsset(ctx, p["audio_asset_id"].(string))
	overlapCheck(t, e)
	overlapCheck(t, os.WriteFile(filepath.Join(dir, "mixed.wav"), audio, 0600))
	if (len(audio)-44)/2 != comp.SampleCount {
		t.Fatal("wrong final clock")
	}
	// Independent audio oracle sums each source at the resolved literal clocks.
	expected := make([]float64, comp.SampleCount)
	originals := map[string][]byte{}
	for i, v := range progress["pieces"].([]any) {
		piece := v.(map[string]any)
		source, e := s.Store.ReadAsset(ctx, piece["asset_id"].(string))
		overlapCheck(t, e)
		originals[piece["id"].(string)] = source[44:]
		overlapCheck(t, os.WriteFile(filepath.Join(dir, fmt.Sprintf("source-%d.wav", i+1)), source, 0600))
	}
	for _, track := range comp.Tracks {
		raw := originals[track.PieceID]
		for n := track.SourceStart; n < track.SourceEnd; n++ {
			expected[track.FinalStart+n-track.SourceStart] += float64(int16(binary.LittleEndian.Uint16(raw[n*2:]))) * track.Gain
		}
	}
	for n, v := range expected {
		got := int16(binary.LittleEndian.Uint16(audio[44+n*2:]))
		want := int16(mathRound(v))
		if got != want {
			t.Fatalf("native sample %d got %d want %d", n, got, want)
		}
	}
	unit := key["units"].([]any)[0].(map[string]any)
	interval := unit["audio_intervals"].([]any)[0].(map[string]any)
	o := comp.Overlaps[0]
	if interval["start_ms"] != float64(o.Start/24) || interval["end_ms"] != float64((o.End+23)/24) {
		t.Fatal("masking key not concurrent", interval, comp)
	}
	input := scoring.Input{Units: []scoring.Unit{{ID: "e1", Domain: "discourse", Category: "discourse.turn_taking", Kind: unit["expected_judgment"].(string), Weight: 2}}, Enabled: map[string]bool{"detection": true}, Unresolved: map[string]bool{}}
	if kind == "cooperative_backchannel" {
		input.Decisions = []scoring.Decision{{ID: "d1", Unit: "e1", Verdict: "confirmed_acceptable"}}
	} else {
		input.Decisions = []scoring.Decision{{ID: "d1", Unit: "e1", Verdict: "matched_error"}}
	}
	result, e := scoring.Score(input)
	overlapCheck(t, e)
	if kind == "cooperative_backchannel" && (result.Counts.G != 0 || result.Counts.TP != 0 || result.Counts.FP != 0 || result.Counts.FN != 0) {
		t.Fatal("cooperation scored as an error", result.Counts)
	}
	if kind == "obstructive" && (result.Counts.G != 1 || result.Counts.TP != 1 || result.Counts.FN != 0 || result.Counts.FP != 0) {
		t.Fatal("real interruption did not receive the expected detection credit", result.Counts)
	}
	// Full and range reads serve the stored sample stream; repeated render reuses
	// the completed preparation with an unreachable synthesis endpoint.
	playback := httptest.NewRecorder()
	req := httptest.NewRequest("GET", "/audio", nil)
	req.SetPathValue("id", id)
	s.speechPlayback(playback, req)
	if playback.Code != 200 || !bytes.Equal(playback.Body.Bytes(), audio) {
		t.Fatal("stored playback mismatch")
	}
	calls := pieceCalls.Load()
	restarted := NewServer(preparationNative(t), s.Origin, "http://unreachable.invalid")
	again, e := restarted.RenderPreparation(ctx, id, uuid.NewString(), 3, nil)
	overlapCheck(t, e)
	if again["audio_asset_id"] != p["audio_asset_id"] || pieceCalls.Load() != calls {
		t.Fatal("reopen dispatched synthesis")
	}
	for name, value := range map[string]any{"progress.json": progress, "preparation.json": p, "score.json": result, "observation.json": map[string]any{"origin": "actual-local-recordings-constructed-text-semantic-decisions", "piece_requests": pieceCalls.Load(), "new_local_recordings": modelCalls.Load(), "context": "saved generated utterances, target scope, actual decoder-derived timing; no auditory judge", "resume_tested": interrupt}} {
		overlapCheck(t, os.WriteFile(filepath.Join(dir, name), overlapJSON(value), 0600))
	}
	for kind, value := range map[string]any{"render-progress": progress, "speech-composition": compositionValue(comp)} {
		if _, _, e := contracts.Validate(kind, "2.0.0", overlapJSON(value)); e != nil {
			t.Fatal(kind, e)
		}
	}
	for name, id := range map[string]string{"render-plan.json": p["render_plan_asset_id"].(string), "sample-map.json": progress["sample_map_asset_id"].(string), "settings.json": p["settings_asset_id"].(string)} {
		raw, e := s.Store.ReadAsset(ctx, id)
		overlapCheck(t, e)
		overlapCheck(t, os.WriteFile(filepath.Join(dir, name), raw, 0600))
	}
}
func mathRound(v float64) float64 {
	if v < 0 {
		return float64(int64(v - .5))
	}
	return float64(int64(v + .5))
}
func TestNativeOverlapObstructive(t *testing.T) { nativeOverlap(t, "obstructive", true) }
func TestNativeOverlapCooperative(t *testing.T) { nativeOverlap(t, "cooperative_backchannel", false) }
