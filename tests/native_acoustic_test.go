package app

import (
	"bytes"
	"context"
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
	"testing"
)

// Constructed text-LLM packets; real selected Kokoro, native controllers,
// private HTTP, PostgreSQL, MinIO, checkpoints, evidence and finalization.
func nativeAcousticFixture(t *testing.T, kind string) (*Server, map[string]any) {
	return nativeAcousticFixtureCandidate(t, kind, nil)
}
func nativeAcousticFixtureCandidate(t *testing.T, kind string, customize func(map[string]any)) (*Server, map[string]any) {
	t.Helper()
	ctx := context.Background()
	s, r, client, _ := prepareNativeFixtureOptions(t, "", 200, func(c map[string]any) {
		c["llm_lab_capture_content"] = true
		c["llm_lab_trace_enabled"] = true
		profile := c["llm_profiles"].([]any)[0].(map[string]any)
		profile["context_budget_tokens"] = float64(1000000)
		profile["structured_output"] = false
	}, nil)
	// Only the upstream text-model response is a constructed external boundary.
	// Its original/candidate/manifest/envelope are admitted and saved by the real
	// canonical/mutation owners. No prepared asset/head is rewritten here.
	original := client.Transport
	mutation := false
	var candidate map[string]any
	client.Transport = preparationTrip(func(req *http.Request) (*http.Response, error) {
		if mutation {
			raw, e := io.ReadAll(req.Body)
			if e != nil {
				return nil, e
			}
			expectedText := "The café opens tomorrow."
			if kind == "vot_edit" {
				expectedText = "Pan is ready."
			}
			for _, fragment := range []string{expectedText, "canonical_script", "mutation_recipes", "production_recipes", "mutation"} {
				if !strings.Contains(string(raw), fragment) {
					t.Error("complete mutation context absent", fragment)
				}
			}
			content, _ := json.Marshal(candidate)
			quoted, _ := json.Marshal(string(content))
			body := []byte(`{"object":"response","id":"acoustic-fixture","status":"completed","model":"constructed-clean-text","output":[{"type":"message","content":[{"type":"output_text","text":` + string(quoted) + `}]}]}`)
			return &http.Response{StatusCode: 200, Header: http.Header{"Content-Type": []string{"application/json"}}, Body: io.NopCloser(bytes.NewReader(body)), ContentLength: int64(len(body))}, nil
		}
		res, e := original.RoundTrip(req)
		if e != nil || kind != "vot_edit" {
			return res, e
		}
		raw, e := io.ReadAll(res.Body)
		res.Body.Close()
		if e != nil {
			return nil, e
		}
		var wire map[string]any
		if e = json.Unmarshal(raw, &wire); e != nil {
			return nil, e
		}
		block := wire["output"].([]any)[0].(map[string]any)["content"].([]any)[0].(map[string]any)
		var clean map[string]any
		if e = json.Unmarshal([]byte(block["text"].(string)), &clean); e != nil {
			return nil, e
		}
		u := clean["utterances"].([]any)[0].(map[string]any)
		u["canonical_text"] = "Pan is ready."
		u["surface_text"] = u["canonical_text"]
		raw, _ = json.Marshal(clean)
		block["text"] = string(raw)
		raw, _ = json.Marshal(wire)
		res.Body = io.NopCloser(bytes.NewReader(raw))
		res.ContentLength = int64(len(raw))
		return res, nil
	})
	clean, e := s.PrepareCanonical(ctx, r, uuid.NewString(), client)
	if e != nil {
		t.Fatal(e)
	}
	r.PreparationID = new(string)
	*r.PreparationID = clean["id"].(string)
	r.Attempt = 2
	_, _, candidate, _ = acousticMutationFixture()
	candidate["blueprint_id"] = r.BlueprintID
	unit := candidate["planned_units"].([]any)[0].(map[string]any)
	op := candidate["acoustic_edits"].([]any)[0].(map[string]any)
	params := op["parameters"].(map[string]any)
	realization := unit["realization"].(map[string]any)
	op["controller"] = kind
	unit["primary_taxonomy_id"] = "pronunciation.segmental.consonant_devoicing"
	repair := "Retain final /z/ rather than /s/."
	correctionKind := "phoneme"
	if kind != "phone_pair" {
		realization["intended_ipa"] = realization["canonical_ipa"]
		params["reference_ipa"] = nil
		params["mutated_ipa"] = nil
		params["phone_start"] = nil
		params["phone_end"] = nil
	}
	switch kind {
	case "vowel_duration":
		params["duration_ratio"] = .45
		params["phone_start"] = float64(0)
		params["phone_end"] = float64(2)
		unit["primary_taxonomy_id"] = "pronunciation.segmental.vowel_length"
		repair = "Restore the reference vowel duration."
	case "pitch_duration":
		params["duration_ratio"] = 1.25
		params["gain_db"] = 4.0
		unit["primary_taxonomy_id"] = "pronunciation.suprasegmental.sentence_stress_prominence"
		unit["domain"] = "pronunciation.suprasegmental"
		realization["mode"] = "acoustic_suprasegmental"
		repair = "Restore the reference phrase prominence."
		correctionKind = "prosody"
	case "pitch_range":
		op["controller"] = "pitch_duration"
		unit["primary_taxonomy_id"] = "pronunciation.suprasegmental.pitch_range"
		unit["domain"] = "pronunciation.suprasegmental"
		realization["mode"] = "acoustic_suprasegmental"
		repair = "Restore the reference pitch range."
		correctionKind = "prosody"
	case "pause_insert":
		params["pause_ms"] = float64(2000)
		unit["primary_taxonomy_id"] = "fluency.pause_location"
		unit["domain"] = "fluency"
		realization["mode"] = "temporal_fluency"
		realization["planned_pause_ms"] = float64(2000)
		repair = "Remove the intrusive pause before opens."
		correctionKind = "fluency"
	case "vot_edit":
		params["vot_ms"] = float64(0)
		params["phone_start"] = float64(0)
		params["phone_end"] = float64(4)
		unit["primary_taxonomy_id"] = "pronunciation.segmental.consonant_aspiration"
		repair = "Restore aspiration of the initial stressed /p/."
		u := candidate["utterances"].([]any)[0].(map[string]any)
		u["canonical_text"] = "Pan is ready."
		u["surface_text"] = u["canonical_text"]
		op["scope"] = map[string]any{"start": float64(0), "end": float64(3)}
		unit["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(0), "end_cp": float64(3), "exact_text": "Pan"}
		realization["canonical_text"] = "Pan"
		realization["surface_text"] = "Pan"
		realization["canonical_ipa"] = "pʰæn"
		realization["intended_ipa"] = "pæn"
	}
	unit["accepted_taxonomy_ids"] = []any{unit["primary_taxonomy_id"]}
	unit["rationale"] = repair
	unit["rationale_required_propositions"] = []any{map[string]any{"id": "p1", "description": repair}}
	correction := unit["corrections"].([]any)[0].(map[string]any)
	correction["kind"] = correctionKind
	correction["text"] = repair
	correction["ipa"] = realization["canonical_ipa"]
	correction["required_propositions"] = []any{map[string]any{"id": "p1", "description": repair}}
	params["expected_feature"] = kind + " controlled contrast"
	params["accepted_reference"] = repair
	if customize != nil {
		customize(candidate)
	}
	mutation = true
	p, e := s.PrepareMutation(ctx, r, uuid.NewString(), client)
	if e != nil {
		t.Fatal(e)
	}
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	if s.SpeechURL == "" {
		t.Fatal("actual speech worker required")
	}
	return s, p
}

func acousticTarget(t *testing.T, s *Server, p map[string]any) map[string]any {
	t.Helper()
	progress := speechProgress(t, s, p)
	for _, v := range progress["pieces"].([]any) {
		piece := v.(map[string]any)
		if piece["acoustic_state"] != nil {
			return piece
		}
	}
	t.Fatal("no retained acoustic piece")
	return nil
}
func acousticRun(t *testing.T, kind string) (*Server, map[string]any, map[string]any) {
	t.Helper()
	s, p := nativeAcousticFixture(t, kind)
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	piece := acousticTarget(t, s, p)
	dir := os.Getenv("TANGERINE_PREPARATION_TEST_EVIDENCE")
	if dir != "" {
		raw, _ := json.Marshal(map[string]any{"preparation": p, "piece": piece, "progress": speechProgress(t, s, p)})
		if e := os.WriteFile(filepath.Join(dir, "acoustic-"+kind+".json"), raw, 0600); e != nil {
			t.Fatal(e)
		}
		for i, v := range speechProgress(t, s, p)["pieces"].([]any) {
			part := v.(map[string]any)
			for j, id := range part["receipt_ids"].([]any) {
				doc, e := s.Store.ReadDocument(context.Background(), id.(string))
				if e != nil {
					t.Fatal(e)
				}
				var receipt map[string]any
				json.Unmarshal(doc.Payload, &receipt)
				response, e := s.Store.ReadAsset(context.Background(), receipt["wire_response_asset_id"].(string))
				if e != nil {
					t.Fatal(e)
				}
				entry, _ := json.Marshal(map[string]any{"receipt": receipt, "response": json.RawMessage(response)})
				contextDoc, e := s.acousticRead(context.Background(), receipt["context_snapshot_id"].(string))
				if e != nil {
					t.Fatal(e)
				}
				if contextDoc["scope"].(map[string]any)["preparation_id"] != p["id"] || contextDoc["scope"].(map[string]any)["render_plan_asset_id"] != p["render_plan_asset_id"] {
					t.Fatal("native receipt lost its case/preparation lineage", contextDoc)
				}
				prefix := fmt.Sprintf("acoustic-%s-%d-%d", kind, i, j)
				if e = os.WriteFile(filepath.Join(dir, prefix+"-native.json"), entry, 0600); e != nil {
					t.Fatal(e)
				}
				command, _ := json.Marshal(map[string]any{"action": "diagnostic-read", "id": receipt["operation_id"]})
				var packet bytes.Buffer
				if e = s.Store.LabCommand(context.Background(), bytes.NewReader(command), &packet); e != nil {
					t.Fatal(e)
				}
				if e = os.WriteFile(filepath.Join(dir, prefix+"-diagnostic.json"), packet.Bytes(), 0600); e != nil {
					t.Fatal(e)
				}
			}
			if part["acoustic_state"] != nil {
				audio, e := s.Store.ReadAsset(context.Background(), part["source_asset_id"].(string))
				if e != nil {
					t.Fatal(e)
				}
				if e = os.WriteFile(filepath.Join(dir, "acoustic-"+kind+"-source.wav"), audio, 0600); e != nil {
					t.Fatal(e)
				}
				audio, e = s.Store.ReadAsset(context.Background(), part["asset_id"].(string))
				if e != nil {
					t.Fatal(e)
				}
				if e = os.WriteFile(filepath.Join(dir, "acoustic-"+kind+"-result.wav"), audio, 0600); e != nil {
					t.Fatal(e)
				}
			}
		}

	}
	state := piece["acoustic_state"].(map[string]any)
	source, err := s.Store.ReadAsset(context.Background(), piece["source_asset_id"].(string))
	if err != nil {
		t.Fatal(err)
	}
	previous := source
	for _, v := range state["completed_steps"].([]any) {
		stage := v.(map[string]any)
		production, err := s.acousticRead(context.Background(), stage["production_plan_asset_id"].(string))
		if err != nil {
			t.Fatal(err)
		}
		step := production["steps"].([]any)[0].(map[string]any)
		span := step["source_interval"].(map[string]any)
		a, b := int(span["start"].(float64)), int(span["end"].(float64))
		next, err := s.Store.ReadAsset(context.Background(), stage["result_asset_id"].(string))
		if err != nil {
			t.Fatal(err)
		}
		if step["controller"] == "pause_insert" {
			a -= 120
			b = int(span["start"].(float64)) + 120
		}
		if a < 0 {
			a = 0
		}
		if b > (len(previous)-44)/2 {
			b = (len(previous) - 44) / 2
		}
		tail := len(previous) - 44 - 2*b
		if !bytes.Equal(previous[44:44+2*a], next[44:44+2*a]) || !bytes.Equal(previous[len(previous)-tail:], next[len(next)-tail:]) {
			t.Fatal("unselected phrase context changed", kind, a, b)
		}
		previous = next
	}
	if len(speechProgress(t, s, p)["pieces"].([]any)) != 1 {
		t.Fatal("word-boundary clips introduced artificial phrase boundaries")
	}
	return s, p, piece
}
func TestNativeAcousticPairPositive(t *testing.T) {
	s, _, piece := acousticRun(t, "phone_pair")
	state := piece["acoustic_state"].(map[string]any)
	if state["paired_assets"] == nil || piece["source_asset_id"] == piece["asset_id"] {
		t.Fatal(piece)
	}
	native, e := s.acousticRead(context.Background(), state["native_asset_id"].(string))
	if e != nil || len(native["model_visible_calls"].([]any)) == 0 {
		t.Fatal(native, e)
	}
}
func TestNativeAcousticDurationPositive(t *testing.T) {
	s, _, piece := acousticRun(t, "vowel_duration")
	source, e := s.Store.ReadAsset(context.Background(), piece["source_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	result, e := s.Store.ReadAsset(context.Background(), piece["asset_id"].(string))
	if e != nil || len(result) >= len(source) {
		t.Fatal(len(source), len(result), e)
	}
}
func TestNativeAcousticPitchPositive(t *testing.T) {
	for _, kind := range []string{"pitch_duration", "pitch_range"} {
		s, _, piece := acousticRun(t, kind)
		state := piece["acoustic_state"].(map[string]any)
		stage := state["completed_steps"].([]any)[0].(map[string]any)
		diag, e := s.acousticRead(context.Background(), stage["diagnostic_asset_id"].(string))
		if e != nil {
			t.Fatal(e)
		}
		obs := diag["observations"].(map[string]any)
		if obs["after"].(map[string]any)["state"] != "measured" || obs["perceived_feature"] != nil {
			t.Fatal(obs)
		}
	}
}

func TestNativeAcousticPausePositive(t *testing.T) {
	s, _, piece := acousticRun(t, "pause_insert")
	source, e := s.Store.ReadAsset(context.Background(), piece["source_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	if piece["sample_count"] != float64((len(source)-44)/2+48000) {
		t.Fatal(piece)
	}
}
func TestNativeAcousticVOTPositive(t *testing.T) {
	s, _, piece := acousticRun(t, "vot_edit")
	state := piece["acoustic_state"].(map[string]any)
	stage := state["completed_steps"].([]any)[0].(map[string]any)
	diag, e := s.acousticRead(context.Background(), stage["diagnostic_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	land := diag["observations"].(map[string]any)["landmarks"].(map[string]any)
	if land["measured_vot_ms"].(float64) <= 0 {
		t.Fatal("requested zero invented as measured zero", land)
	}
}

// Inject only a test-owned temporary service failure. All successful requests
// go through the actual private worker and actual model/controller owners.
func acousticFaultProxy(t *testing.T, s *Server, fail *atomic.Bool, sourceCalls *atomic.Int32, preparation string) {
	t.Helper()
	target := s.SpeechURL
	proxy := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/internal/v1/piece" {
			sourceCalls.Add(1)
		}
		if r.URL.Path == "/internal/v1/transform" {
			head, err := s.Store.Preparation(r.Context(), preparation)
			if err != nil {
				t.Error(err)
			} else {
				journal, err := s.acousticRead(r.Context(), head["render_progress_asset_id"].(string))
				if err != nil {
					t.Error(err)
				} else {
					found := false
					for _, v := range journal["pieces"].([]any) {
						x := v.(map[string]any)
						if state, ok := x["acoustic_state"].(map[string]any); ok && state["active_production_plan_asset_id"] != nil && x["source_asset_id"] != nil && x["state"] == "running" {
							found = true
						}
					}
					if !found {
						t.Error("transform dispatched before durable running/source/plan checkpoint")
					}
				}
			}
		}
		if r.URL.Path == "/internal/v1/transform" && fail.Load() {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(503)
			io.WriteString(w, `{"error":"SPEECH_UNAVAILABLE"}`)
			return
		}
		req, e := http.NewRequestWithContext(r.Context(), r.Method, target+r.URL.Path, r.Body)
		if e != nil {
			t.Error(e)
			return
		}
		req.Header = r.Header.Clone()
		req.ContentLength = r.ContentLength
		res, e := http.DefaultClient.Do(req)
		if e != nil {
			w.WriteHeader(503)
			return
		}
		defer res.Body.Close()
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(res.StatusCode)
		io.Copy(w, res.Body)
	}))
	t.Cleanup(proxy.Close)
	s.SpeechURL = proxy.URL
}
func TestNativeAcousticResumePositive(t *testing.T) {
	s, p := nativeAcousticFixture(t, "pause_insert")
	var fail atomic.Bool
	var calls atomic.Int32
	fail.Store(true)
	acousticFaultProxy(t, s, &fail, &calls, p["id"].(string))
	first, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	if e == nil {
		t.Fatal("fault ignored")
	}
	piece := acousticTarget(t, s, first)
	source := piece["source_asset_id"]
	plan := piece["acoustic_state"].(map[string]any)["active_production_plan_asset_id"]
	before := calls.Load()
	fail.Store(false)
	final := renderNativeActual(t, s, first, uuid.NewString(), 2)
	piece = acousticTarget(t, s, final)
	if calls.Load() != before || piece["source_asset_id"] != source {
		t.Fatal("source resynthesized", before, calls.Load())
	}
	stage := piece["acoustic_state"].(map[string]any)["completed_steps"].([]any)[0].(map[string]any)
	if stage["production_plan_asset_id"] != plan {
		t.Fatal("retry rebound immutable plan")
	}
}
func TestNativeAcousticSampleMapPositive(t *testing.T) {
	s, p, _ := acousticRun(t, "pause_insert")
	progress := speechProgress(t, s, p)
	raw, e := s.Store.ReadAsset(context.Background(), progress["sample_map_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	if _, _, e = contracts.Validate("audio-sample-map", "2.0.0", raw); e != nil {
		t.Fatal(e)
	}
	var m map[string]any
	json.Unmarshal(raw, &m)
	var pause bool
	for _, v := range m["rows"].([]any) {
		r := v.(map[string]any)
		if r["kind"] == "pause" {
			pause = true
			if r["final_end"].(float64)-r["final_start"].(float64) != 48000 {
				t.Fatal(r)
			}
		}
	}
	if !pause {
		t.Fatal("planned pause lost")
	}
}
func TestNativeAcousticKeyPositive(t *testing.T) {
	s, p, _ := acousticRun(t, "phone_pair")
	key, e := s.Store.ReadDocument(context.Background(), p["key_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var k map[string]any
	json.Unmarshal(key.Payload, &k)
	u := k["units"].([]any)[0].(map[string]any)
	interval := u["audio_intervals"].([]any)[0].(map[string]any)
	if interval["start_ms"].(float64) <= 0 || interval["end_ms"].(float64) >= k["audio"].(map[string]any)["duration_ms"].(float64) {
		t.Fatal("acoustic key still spans unrelated turns", u)
	}
}
func acousticWorkerPlan(t *testing.T, s *Server, p map[string]any) map[string]any {
	t.Helper()
	settings, e := s.acousticRead(context.Background(), p["settings_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	candidate, e := s.acousticRead(context.Background(), p["mutated_asset_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	profile := settings["speech_profile"].(map[string]any)
	plan, e := compileSpeechPlan(p["id"].(string), settings, candidate, profile)
	if e != nil {
		t.Fatal(e)
	}
	return map[string]any{"profile": profile, "plan": plan}
}
func TestNativeAcousticUnknownControlNegative(t *testing.T) {
	s, p := nativeAcousticFixture(t, "phone_pair")
	packet := acousticWorkerPlan(t, s, p)
	packet["plan"].(map[string]any)["turns"].([]any)[0].(map[string]any)["acoustic_edits"].([]any)[0].(map[string]any)["controller"] = "unknown"
	_, e := s.speechCall(context.Background(), "/internal/v1/plan", packet, nil)
	if e == nil || p["audio_asset_id"] != nil || p["phase_states"].(map[string]any)["render"] != "not_started" {
		t.Fatal(p, e)
	}
}
func TestNativeAcousticOverlapNegative(t *testing.T) {
	s, p := nativeAcousticFixtureCandidate(t, "pause_insert", func(c map[string]any) {
		c["acoustic_edits"] = append(c["acoustic_edits"].([]any), c["acoustic_edits"].([]any)[0])
	})
	result, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	if e == nil || result["render_progress_asset_id"] != nil {
		t.Fatal(result, e)
	}
}

func TestNativeAcousticFailedPrivateNegative(t *testing.T) {
	s, p := nativeAcousticFixture(t, "pause_insert")
	var fail atomic.Bool
	var calls atomic.Int32
	fail.Store(true)
	acousticFaultProxy(t, s, &fail, &calls, p["id"].(string))
	p, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	if e == nil {
		t.Fatal("fault ignored")
	}
	summary := speechSummary(p)
	raw, _ := json.Marshal(summary)
	if bytes.Contains(raw, []byte("source_asset_id")) || summary["audio_available"] != false {
		t.Fatal(summary)
	}
	counter := summary["render_progress_summary"].(map[string]any)
	if counter["complete_pieces"] != 0 || counter["total_pieces"] != 1 || counter["ready_to_assemble"] != false {
		t.Fatal(counter)
	}
}
func TestNativeAcousticNoOutputNegative(t *testing.T) {
	s, p := nativeAcousticFixture(t, "pause_insert")
	var fail atomic.Bool
	var calls atomic.Int32
	fail.Store(true)
	acousticFaultProxy(t, s, &fail, &calls, p["id"].(string))
	p, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	if e == nil {
		t.Fatal("fault ignored")
	}
	r := httptest.NewRequest("GET", "/audio", nil)
	r.SetPathValue("id", p["id"].(string))
	w := httptest.NewRecorder()
	s.speechPlayback(w, r)
	if w.Code != 409 || p["key_id"] != nil {
		t.Fatal(w.Code, p)
	}
}

func TestNativeAcousticIPAUnavailableNegative(t *testing.T) {
	s, p := nativeAcousticFixtureCandidate(t, "phone_pair", func(c map[string]any) {
		c["acoustic_edits"].([]any)[0].(map[string]any)["parameters"].(map[string]any)["mutated_ipa"] = "∅"
	})
	p, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	if e == nil || p["render_progress_asset_id"] != nil {
		t.Fatal(p, e)
	}
}
func TestNativeAcousticParametersNegative(t *testing.T) {
	s, p := nativeAcousticFixture(t, "pause_insert")
	packet := acousticWorkerPlan(t, s, p)
	packet["plan"].(map[string]any)["turns"].([]any)[0].(map[string]any)["acoustic_edits"].([]any)[0].(map[string]any)["parameters"].(map[string]any)["pause_ms"] = float64(-1)
	_, e := s.speechCall(context.Background(), "/internal/v1/plan", packet, nil)
	if e == nil || p["render_progress_asset_id"] != nil {
		t.Fatal(p, e)
	}
}
func TestNativeAcousticAlignmentNegative(t *testing.T) {
	s, p := nativeAcousticFixtureCandidate(t, "vowel_duration", func(c map[string]any) {
		x := c["acoustic_edits"].([]any)[0].(map[string]any)["parameters"].(map[string]any)
		x["phone_start"] = float64(999)
		x["phone_end"] = float64(1000)
	})
	p, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	if e == nil || p["audio_asset_id"] != nil || p["phase_states"].(map[string]any)["render"] != "failed" || p["last_failure"].(map[string]any)["code"] != "CAPABILITY_UNQUALIFIED" {
		t.Fatal(p, e)
	}
	piece := acousticTarget(t, s, p)
	if piece["source_asset_id"] == nil || piece["asset_id"] != nil || piece["last_error_asset_id"] == nil {
		t.Fatal("unresolved operation lost source/reason", piece)
	}
}
func TestNativeAcousticUnvoicedNegative(t *testing.T) {
	s, p := nativeAcousticFixtureCandidate(t, "vot_edit", func(c map[string]any) {
		c["acoustic_edits"].([]any)[0].(map[string]any)["scope"] = map[string]any{"start": float64(7), "end": float64(12)}
		u := c["planned_units"].([]any)[0].(map[string]any)
		u["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": float64(7), "end_cp": float64(12), "exact_text": "ready"}
		u["realization"].(map[string]any)["canonical_text"] = "ready"
		u["realization"].(map[string]any)["surface_text"] = "ready"
	})
	p, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 1, nil)
	if e == nil || p["key_id"] != nil || p["phase_states"].(map[string]any)["render"] != "failed" || p["last_failure"].(map[string]any)["code"] != "CAPABILITY_UNQUALIFIED" {
		t.Fatal("unrealizable stop accepted", p, e)
	}
}

func seedAcousticJournal(t *testing.T, s *Server, p, progress map[string]any) {
	t.Helper()
	ctx := context.Background()
	op, e := s.Store.ReserveOperation(ctx, OperationRequest{Name: "acoustic-recovery-fixture", Key: uuid.NewString(), Path: "/test/acoustic-recovery", Body: []byte(`{}`)})
	if e != nil {
		t.Fatal(e)
	}
	if _, e = s.Store.DB.Exec(ctx, "UPDATE operation SET state='running' WHERE id=$1", op.ID); e != nil {
		t.Fatal(e)
	}
	p["audio_asset_id"] = nil
	p["audio_sha256"] = nil
	p["key_id"] = nil
	if e = s.Store.takePreparation(ctx, p, op.ID, "render"); e != nil {
		t.Fatal(e)
	}
	progress["assembled_asset_id"] = nil
	progress["assembled_sha256"] = nil
	progress["sample_map_asset_id"] = nil
	p["phase_states"].(map[string]any)["render"] = "interrupted"
	if e = s.saveSpeechProgress(ctx, p, progress, op.ID); e != nil {
		t.Fatal(e)
	}
	s.Store.releaseSpeech(ctx, op.ID)
}
func TestNativeAcousticChildRecoveryPositive(t *testing.T) {
	s, p := nativeAcousticFixture(t, "phone_pair")
	var fail atomic.Bool
	var calls atomic.Int32
	acousticFaultProxy(t, s, &fail, &calls, p["id"].(string))
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	progress := speechProgress(t, s, p)
	piece := acousticTarget(t, s, p)
	state := piece["acoustic_state"].(map[string]any)
	originalPlan := state["completed_steps"].([]any)[0].(map[string]any)["production_plan_asset_id"]
	originalSHA := piece["audio_sha256"]
	before := calls.Load()
	for _, v := range progress["pieces"].([]any) {
		x := v.(map[string]any)
		if x["id"] == piece["id"] {
			for _, k := range []string{"source_asset_id", "asset_id", "audio_sha256", "sample_count"} {
				x[k] = nil
			}
			delete(x, "acoustic_state")
			x["state"] = "interrupted"
			x["receipt_ids"] = []any{}
		}
	}
	seedAcousticJournal(t, s, p, progress)
	p = renderNativeActual(t, s, p, uuid.NewString(), 2)
	piece = acousticTarget(t, s, p)
	state = piece["acoustic_state"].(map[string]any)
	if calls.Load() != before || piece["audio_sha256"] != originalSHA || state["completed_steps"].([]any)[0].(map[string]any)["production_plan_asset_id"] != originalPlan {
		t.Fatal("completed child lost source/plan correspondence or repeated inference", piece, before, calls.Load())
	}
}
func TestNativeAcousticFinalizationResumePositive(t *testing.T) {
	s, p := nativeAcousticFixture(t, "pause_insert")
	var fail atomic.Bool
	var calls atomic.Int32
	acousticFaultProxy(t, s, &fail, &calls, p["id"].(string))
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	sha := p["audio_sha256"]
	progress := speechProgress(t, s, p)
	before := calls.Load()
	seedAcousticJournal(t, s, p, progress)
	p = renderNativeActual(t, s, p, uuid.NewString(), 2)
	if p["audio_sha256"] != sha || calls.Load() != before || p["key_id"] == nil {
		t.Fatal("completed pieces were rerendered or finalization changed samples", p)
	}
}
func resetAcousticTransform(t *testing.T, s *Server, p map[string]any, childState string) {
	t.Helper()
	progress := speechProgress(t, s, p)
	piece := acousticTarget(t, s, p)
	state := piece["acoustic_state"].(map[string]any)
	originalPlan := state["completed_steps"].([]any)[0].(map[string]any)["production_plan_asset_id"]
	source, _, e := s.Store.completedSpeechPiece(context.Background(), piece["id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	nativeID, e := s.acousticDocument(context.Background(), source["receipt"].(map[string]any)["native"])
	if e != nil {
		t.Fatal(e)
	}
	for _, v := range progress["pieces"].([]any) {
		x := v.(map[string]any)
		if x["id"] == piece["id"] {
			x["acoustic_state"] = map[string]any{"current_asset_id": x["source_asset_id"], "native_asset_id": nativeID, "next_step": float64(0), "completed_steps": []any{}, "active_production_plan_asset_id": originalPlan}
			x["asset_id"] = nil
			x["audio_sha256"] = nil
			x["sample_count"] = nil
			x["state"] = "interrupted"
		}
	}
	id := acousticChild(piece, "step-0:transform")["id"]
	if childState == "different_subject" {
		_, e = s.Store.DB.Exec(context.Background(), "UPDATE operation SET subject_id=$2 WHERE subject_id=$1 AND operation_name='speech-inference'", id, uuid.NewString())
	} else {
		_, e = s.Store.DB.Exec(context.Background(), "UPDATE operation SET state=$2 WHERE subject_id=$1 AND operation_name='speech-inference'", id, childState)
	}
	if e != nil {
		t.Fatal(e)
	}
	seedAcousticJournal(t, s, p, progress)
}
func TestNativeAcousticWrongChildNegative(t *testing.T) {
	s, p := nativeAcousticFixture(t, "pause_insert")
	var fail atomic.Bool
	var calls atomic.Int32
	acousticFaultProxy(t, s, &fail, &calls, p["id"].(string))
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	before := calls.Load()
	resetAcousticTransform(t, s, p, "different_subject")
	fail.Store(true)
	p, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 2, nil)
	if e == nil || p["audio_asset_id"] != nil || calls.Load() != before {
		t.Fatal("a different subject child was reused or source was replaced", p, e)
	}
}
func TestNativeAcousticFailedChildNegative(t *testing.T) {
	s, p := nativeAcousticFixture(t, "pause_insert")
	var fail atomic.Bool
	var calls atomic.Int32
	acousticFaultProxy(t, s, &fail, &calls, p["id"].(string))
	p = renderNativeActual(t, s, p, uuid.NewString(), 1)
	before := calls.Load()
	resetAcousticTransform(t, s, p, "failed")
	fail.Store(true)
	p, e := s.RenderPreparation(context.Background(), p["id"].(string), uuid.NewString(), 2, nil)
	if e == nil || p["audio_asset_id"] != nil || p["key_id"] != nil || calls.Load() != before {
		t.Fatal("failed child was accepted as completed output", p, e)
	}
}
