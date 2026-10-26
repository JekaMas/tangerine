package app

// Only text generation and semantic replies are constructed. The selected
// speech adapter, persistence, acoustic finalization, Listen and scorer are real.
import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/google/uuid"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

const elevenAnswer = "The second think in speaker one's turn uses /s/; use /θɪŋk/."

func elevenProfile() map[string]any {
	endpoint := os.Getenv("TANGERINE_ELEVENLABS_ENDPOINT")
	if endpoint == "" {
		endpoint = "https://api.elevenlabs.io"
	}
	return map[string]any{"id": "elevenlabs-i22", "provider": "elevenlabs", "adapter_version": "elevenlabs-dictionary-v1", "model": "eleven_flash_v2", "endpoint": endpoint,
		"credential_refs": []any{"ELEVENLABS_API_KEY"}, "billing_mode": "free_tier", "account_tier": "free", "overage_disabled": true,
		"capabilities": controlledCapabilities, "voices": []any{map[string]any{"id": "EXAVITQu4vr4xnSDxMaL", "locale": "en-US", "accent_description": "American English"}, map[string]any{"id": "JBFqnCBsd6RMkjVDRZzb", "locale": "en-GB", "accent_description": "British English"}},
		"assets": []any{}, "voice_settings": map[string]any{"stability": .5, "similarity_boost": .75, "style": nil, "use_speaker_boost": nil, "speed": 1.0}, "catalogue_asset_id": nil, "voice_description_asset_id": nil}
}

func elevenCandidate(blueprint string, mutation bool) map[string]any {
	_, _, c, _ := acousticMutationFixture()
	c["blueprint_id"] = blueprint
	c["utterances"] = []any{map[string]any{"id": "u1", "speaker_id": "s1", "canonical_text": "I think we should think again.", "surface_text": "I think we should think again."}, map[string]any{"id": "u2", "speaker_id": "s2", "canonical_text": "I think so.", "surface_text": "I think so."}}
	if !mutation {
		c["planned_units"] = []any{}
		c["acoustic_edits"] = []any{}
		return c
	}
	u := c["planned_units"].([]any)[0].(map[string]any)
	u["primary_taxonomy_id"] = "pronunciation.segmental.consonant_substitution"
	u["accepted_taxonomy_ids"] = []any{u["primary_taxonomy_id"]}
	u["text_spans"].([]any)[0].(map[string]any)["span"] = map[string]any{"start_cp": 18, "end_cp": 23, "exact_text": "think"}
	r := u["realization"].(map[string]any)
	r["canonical_text"] = "think"
	r["surface_text"] = "think"
	r["canonical_ipa"] = "θɪŋk"
	r["intended_ipa"] = "sɪŋk"
	u["rationale"] = "The second think uses /s/ instead of /θ/."
	u["rationale_required_propositions"] = []any{map[string]any{"id": "p1", "description": "/s/ replaces the intended /θ/."}}
	correction := u["corrections"].([]any)[0].(map[string]any)
	correction["kind"] = "phoneme"
	correction["text"] = "Use /θɪŋk/."
	correction["ipa"] = "θɪŋk"
	correction["required_propositions"] = []any{map[string]any{"id": "p1", "description": "Restore /θ/ in think."}}
	op := c["acoustic_edits"].([]any)[0].(map[string]any)
	op["scope"] = map[string]any{"start": 18, "end": 23}
	p := op["parameters"].(map[string]any)
	p["reference_ipa"] = "θɪŋk"
	p["mutated_ipa"] = "sɪŋk"
	p["phone_start"] = nil
	p["phone_end"] = nil
	p["expected_feature"] = "Second think: /s/ for /θ/."
	p["accepted_reference"] = "θɪŋk"
	return c
}

func TestNativeElevenLabsFlow(t *testing.T) {
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_ELEVENLABS_EVIDENCE")
	if dir == "" {
		t.Fatal("owned evidence directory required")
	}
	write := func(name string, value any) {
		t.Helper()
		requireListening(t, os.WriteFile(filepath.Join(dir, name), mustJSON(value), 0600))
	}
	s, r, _, _ := prepareNativeFixtureOptions(t, "", 200, func(c map[string]any) {
		c["speech_profile"] = "elevenlabs-i22"
		c["speech_profiles"] = []any{elevenProfile()}
		c["llm_lab_capture_content"] = true
		c["llm_lab_trace_enabled"] = true
		c["llm_profiles"].([]any)[0].(map[string]any)["context_budget_tokens"] = 1000000
		c["llm_profiles"].([]any)[0].(map[string]any)["structured_output"] = false
	}, func(b map[string]any) {
		b["provider_profile_id"] = "elevenlabs-i22"
		request := b["exercise_request"].(map[string]any)
		request["speaker_count"] = 2
		request["category_ids"] = []any{"pronunciation.segmental.consonant_substitution"}
		request["mutation_count"] = 1
		b["speakers"] = []any{explicitSpeechSpeaker("s1", "EXAVITQu4vr4xnSDxMaL"), explicitSpeechSpeaker("s2", "JBFqnCBsd6RMkjVDRZzb")}
	})
	var mu sync.Mutex
	wires := []any{}
	mutation := false
	textClient := &http.Client{Transport: preparationTrip(func(req *http.Request) (*http.Response, error) {
		raw, _ := io.ReadAll(req.Body)
		mu.Lock()
		wires = append(wires, map[string]any{"origin": "constructed-text-response", "path": req.URL.Path, "request": json.RawMessage(raw)})
		mu.Unlock()
		c := elevenCandidate(r.BlueprintID, mutation)
		body := mustJSON(map[string]any{"id": "constructed-i22-text", "object": "response", "status": "completed", "model": "constructed-clean-text", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": string(mustJSON(c))}}}}})
		return &http.Response{StatusCode: 200, Header: http.Header{"Content-Type": []string{"application/json"}}, Body: io.NopCloser(bytes.NewReader(body))}, nil
	})}
	p, e := s.PrepareCanonical(ctx, r, uuid.NewString(), textClient)
	requireListening(t, e)
	id := p["id"].(string)
	r.PreparationID = &id
	r.Attempt = 2
	mutation = true
	p, e = s.PrepareMutation(ctx, r, uuid.NewString(), textClient)
	requireListening(t, e)
	s.SpeechURL = os.Getenv("TANGERINE_SPEECH_TEST_URL")
	s.speechToken = "actual-local-speech-test"
	var pieces atomic.Int32
	interrupted := &http.Client{Transport: preparationTrip(func(req *http.Request) (*http.Response, error) {
		if req.URL.Path == "/internal/v1/piece" && pieces.Add(1) == 2 {
			return &http.Response{StatusCode: 429, Header: http.Header{"Content-Type": []string{"application/json"}}, Body: io.NopCloser(strings.NewReader(`{"error":"PROVIDER_QUOTA","origin":"controlled second-piece interruption"}`))}, nil
		}
		return http.DefaultTransport.RoundTrip(req)
	})}
	failed, e := s.RenderPreparation(ctx, id, uuid.NewString(), 1, interrupted)
	var failure *provider.Failure
	if !errorsAsProvider(e, &failure) || failure.Code != "PROVIDER_QUOTA" {
		t.Fatalf("expected controlled quota; %v %v", e, failed)
	}
	first := speechProgress(t, s, failed)
	firstPiece := first["pieces"].([]any)[0].(map[string]any)
	if firstPiece["state"] != "complete" {
		t.Fatal("first piece not durable", first)
	}
	frozen, e := s.acousticRead(ctx, failed["render_plan_asset_id"].(string))
	requireListening(t, e)
	write("failed-preparation.json", failed)
	write("failed-progress.json", first)
	write("frozen-plan.json", frozen)
	// Change current settings to an incompatible model/voice. Resume must continue
	// the saved binding and skip the completed first piece.
	c, rev, e := s.Store.Configuration(ctx)
	requireListening(t, e)
	c["speech_profiles"].([]any)[0].(map[string]any)["model"] = "eleven_multilingual_v2"
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	resumed, e := s.RenderPreparation(ctx, id, uuid.NewString(), 2, nil)
	requireListening(t, e)
	progress := speechProgress(t, s, resumed)
	if progress["pieces"].([]any)[0].(map[string]any)["asset_id"] != firstPiece["asset_id"] {
		t.Fatal("resume regenerated first piece")
	}
	if resumed["render_plan_asset_id"] != failed["render_plan_asset_id"] {
		t.Fatal("resume discarded saved dictionaries")
	}
	write("preparation.json", resumed)
	write("progress.json", progress)
	keyDoc, e := s.Store.ReadDocument(ctx, resumed["key_id"].(string))
	requireListening(t, e)
	var key map[string]any
	requireListening(t, json.Unmarshal(keyDoc.Payload, &key))
	write("key.json", key)
	audio, e := s.Store.ReadAsset(ctx, resumed["audio_asset_id"].(string))
	requireListening(t, e)
	requireListening(t, os.WriteFile(filepath.Join(dir, "exercise.wav"), audio, 0600))
	if len(audio) < 4800 {
		t.Fatal("no usable speech")
	}
	// Configure only the owned semantic endpoint before freezing the attempt.
	var semanticCalls atomic.Int32
	semantic := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		semanticCalls.Add(1)
		raw, _ := io.ReadAll(req.Body)
		var wire map[string]any
		_ = json.Unmarshal(raw, &wire)
		var input map[string]any
		var claims []CanonicalClaim
		for _, v := range wire["input"].([]any) {
			content := v.(map[string]any)["content"].(string)
			if strings.HasPrefix(content, "Complete stage input: ") {
				_ = json.Unmarshal([]byte(strings.TrimPrefix(content, "Complete stage input: ")), &input)
			}
			if strings.HasPrefix(content, "extraction: ") {
				var extracted struct {
					Claims []CanonicalClaim `json:"claims"`
				}
				_ = json.Unmarshal([]byte(strings.TrimPrefix(content, "extraction: ")), &extracted)
				claims = extracted.Claims
			}
		}
		var output any
		if _, mapped := input["ground_truth"]; !mapped {
			text := []rune(elevenAnswer)
			a := strings.Index(elevenAnswer, "/θɪŋk/")
			start := len([]rune(elevenAnswer[:a]))
			option := AnswerSpan{Start: start, End: start + 6, Text: "/θɪŋk/"}
			output = AnswerExtraction{Version: "2.0.0", Clauses: []ExtractedClause{{LocalRef: "c0", Span: AnswerSpan{Start: 0, End: len(text), Text: elevenAnswer}, Stance: "assert_error", Correction: &option}}, Unparsed: []AnswerSpan{}, Coverage: []ClaimCoverage{}, Relations: []ClaimRelation{}}
		} else if len(claims) > 0 {
			unit := input["ground_truth"].(map[string]any)["units"].([]any)[0].(map[string]any)
			unitID := unit["id"].(string)
			option := unit["corrections"].([]any)[0].(map[string]any)["id"].(string)
			d := SemanticDecision{Claim: claims[0].ID, Unit: &unitID, Decision: "matched_error", Correction: semanticEmpty(), Explanation: semanticEmpty(), Evidence: []string{}, Reason: "supported", Note: "The second think substitutes /s/ for /θ/."}
			d.Correction.Supplied = true
			d.Correction.Option = &option
			d.Correction.Status = "accepted"
			d.Correction.Satisfied = []string{"p1"}
			output = SemanticMapping{Version: "1.0.0", Decisions: []SemanticDecision{d}}
		} else {
			unit := input["ground_truth"].(map[string]any)["units"].([]any)[0].(map[string]any)["id"]
			decisionIDs := []any{}
			for _, value := range input["decisions"].(map[string]any)["decisions"].([]any) {
				decisionIDs = append(decisionIDs, value.(map[string]any)["claim_id"])
			}
			item := func(kind, text string) map[string]any {
				return map[string]any{"kind": kind, "text": text, "unit_ids": []any{unit}, "decision_ids": decisionIDs, "issue_ids": []any{}, "rationale_ids": []any{}, "grounding_status": "llm_grounded", "status": "final"}
			}
			rec := item("recommendation", "Practice: I think the ship leaves at three. Keep /θ/ distinct from /s/.")
			rec["grounding_status"] = "practice_recommendation"
			output = map[string]any{"schema_version": "2.0.0", "language": input["requested_language"], "items": []any{item("detected", "You found the second think pronounced with /s/."), item("correction", "Use /θɪŋk/ for think."), rec}}
		}
		mu.Lock()
		wires = append(wires, map[string]any{"origin": "constructed-semantic-response", "request": wire, "response": output})
		mu.Unlock()
		_ = json.NewEncoder(w).Encode(map[string]any{"id": "constructed-i22-semantic", "object": "response", "status": "completed", "model": "constructed-i22-semantic", "output": []any{map[string]any{"type": "message", "content": []any{map[string]any{"type": "output_text", "text": string(mustJSON(output))}}}}})
	}))
	defer semantic.Close()
	c, rev, e = s.Store.Configuration(ctx)
	requireListening(t, e)
	lp := c["llm_profiles"].([]any)[0].(map[string]any)
	for k, v := range map[string]any{"provider": "local_responses", "model": "constructed-i22-semantic", "endpoint": semantic.URL + "/v1/responses", "adapter_version": "local-responses-v1", "auth_method": "local_none", "billing_mode": "local", "credential_ref": "local-none", "stream": false, "context_budget_tokens": 1000000, "max_output_tokens": 4096} {
		lp[k] = v
	}
	c["mapping_audit_enabled"] = false
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, e = s.Store.PutConfiguration(ctx, mustJSON(c), uuid.NewString(), rev)
	requireListening(t, e)
	var caseID, sha string
	requireListening(t, s.Store.DB.QueryRow(ctx, "SELECT case_version_id,case_sha256 FROM listening_case WHERE source_key_id=$1", resumed["key_id"]).Scan(&caseID, &sha))
	started, e := s.Store.StartAttempt(ctx, mustJSON(map[string]any{"case_version_id": caseID, "case_sha256": sha, "requested_language": "en"}), uuid.NewString())
	requireListening(t, e)
	attempt := started["attempt_id"].(string)
	write("native-fixture.json", map[string]any{"preparation_id": id, "case_id": caseID, "key_id": resumed["key_id"], "audio_asset_id": resumed["audio_asset_id"], "attempt_id": attempt, "answer": elevenAnswer, "live_speech": os.Getenv("TANGERINE_ELEVENLABS_LIVE") == "1"})
	s.token = "listening-owned-token"
	listener, e := net.Listen("tcp", ":8080")
	requireListening(t, e)
	api := &http.Server{Handler: s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = api.Serve(listener) }()
	defer api.Close()
	if os.Getenv("TANGERINE_ELEVENLABS_BROWSER") != "1" {
		_, _, e = s.Store.WriteAnswer(ctx, attempt, uuid.NewString(), 0, answerPacket(elevenAnswer, "en"), true)
		requireListening(t, e)
		record, e := s.Store.Attempt(ctx, attempt)
		requireListening(t, e)
		_, e = s.InterpretAttempt(ctx, attempt, uuid.NewString(), 1, record.Attempt["answer_utf8_sha256"].(string), record.Attempt["configuration_sha256"].(string), nil)
		requireListening(t, e)
	} else {
		timer := time.NewTimer(90 * time.Minute)
		defer timer.Stop()
		ticker := time.NewTicker(100 * time.Millisecond)
		defer ticker.Stop()
	wait:
		for {
			select {
			case <-timer.C:
				t.Fatal("browser fixture timeout")
			case <-ticker.C:
				if _, e := os.Stat(filepath.Join(dir, "done")); e == nil {
					break wait
				}
			}
		}
	}
	state, e := s.Store.interpretationState(ctx, attempt)
	requireListening(t, e)
	if state.Result == nil {
		t.Fatal("no native score", state)
	}
	record, e := s.Store.Attempt(ctx, attempt)
	requireListening(t, e)
	envelope, e := s.Store.interpretationEnvelope(ctx, record, state)
	requireListening(t, e)
	write("result.json", envelope)
	mu.Lock()
	write("constructed-wires.json", wires)
	mu.Unlock()
	if envelope["feedback_status"] != "complete" || envelope["score"].(map[string]any)["composite"].(map[string]any)["display"] != "100.0" {
		t.Fatal("ordinary answer/feedback did not complete", envelope)
	}
	counts := envelope["score"].(map[string]any)["counts"].(map[string]any)
	if fmt.Sprint(counts["tp"]) != "1" || fmt.Sprint(counts["fn"]) != "0" || fmt.Sprint(counts["fp"]) != "0" {
		t.Fatal("wrong native arithmetic", counts)
	}
	write("result.json", envelope)
	mu.Lock()
	write("constructed-wires.json", wires)
	mu.Unlock()
	write("native-final.json", map[string]any{"semantic_calls": semanticCalls.Load(), "preparation_id": id, "attempt_id": attempt, "result_id": state.Result, "resumed_pieces": progress["pieces"], "first_piece_asset_reused": firstPiece["asset_id"]})
	rows, e := s.Store.DB.Query(ctx, "SELECT id FROM document WHERE kind IN ('provider-receipt','llm-context-snapshot') ORDER BY created_at,id")
	requireListening(t, e)
	ids := []string{}
	for rows.Next() {
		var id string
		requireListening(t, rows.Scan(&id))
		ids = append(ids, id)
	}
	rows.Close()
	docs := []any{}
	assets := map[string]bool{}
	for _, id := range ids {
		d, e := s.Store.ReadDocument(ctx, id)
		requireListening(t, e)
		var value map[string]any
		requireListening(t, json.Unmarshal(d.Payload, &value))
		docs = append(docs, value)
		for k, v := range value {
			if strings.HasSuffix(k, "asset_id") || k == "context_snapshot_id" {
				if id, ok := v.(string); ok {
					assets[id] = true
				}
			}
		}
	}
	write("native-documents.json", docs)
	requireListening(t, os.MkdirAll(filepath.Join(dir, "assets"), 0700))
	for id := range assets {
		data, e := s.Store.ReadAsset(ctx, id)
		if e == nil {
			requireListening(t, os.WriteFile(filepath.Join(dir, "assets", id+".json"), data, 0600))
		}
	}
	t.Logf("ordinary speech completed: preparation=%s attempt=%s result=%s source=%s", id, attempt, *state.Result, lab.Hash(audio))
}

func errorsAsProvider(err error, target **provider.Failure) bool {
	if e, ok := err.(*provider.Failure); ok {
		*target = e
		return true
	}
	return false
}
