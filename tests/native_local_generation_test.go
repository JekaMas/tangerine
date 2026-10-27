package app

// I34 is opt-in installed-local inference. Constructed requests and failure
// packets are labelled separately. No client can reach a hosted model.
import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/google/uuid"
	"tangerine.local/api/internal/provider"
)

func i34Client(t *testing.T) *http.Client {
	t.Helper()
	transport := &http.Transport{}
	t.Cleanup(transport.CloseIdleConnections)
	rows := []any{}
	return &http.Client{Transport: g23Trip(func(req *http.Request) (*http.Response, error) {
		if req.URL.Scheme != "http" || req.URL.Host != "ollama:11434" || req.URL.Path != "/v1/responses" {
			t.Errorf("forbidden nonlocal inference route: %s", req.URL)
			return nil, errors.New("I34 prohibits hosted inference")
		}
		raw, e := io.ReadAll(req.Body)
		if e != nil {
			return nil, e
		}
		req.Body = io.NopCloser(bytes.NewReader(raw))
		row := map[string]any{"url": req.URL.String(), "request": json.RawMessage(raw), "started_at": time.Now().UTC().Format(time.RFC3339Nano), "authorization_present": req.Header.Get("Authorization") != "", "origin": "actual installed local model; no response substitution"}
		rows = append(rows, row)
		g23Write(t, "dispatches.json", rows)
		started := time.Now()
		response, e := transport.RoundTrip(req)
		row["seconds"] = time.Since(started).Seconds()
		row["finished_at"] = time.Now().UTC().Format(time.RFC3339Nano)
		if e != nil {
			row["transport_error"] = e.Error()
		} else {
			body, readErr := io.ReadAll(response.Body)
			_ = response.Body.Close()
			response.Body = io.NopCloser(bytes.NewReader(body))
			row["http_status"] = response.StatusCode
			if json.Valid(body) {
				row["response"] = json.RawMessage(body)
			} else {
				row["response_text"] = string(body)
			}
			if readErr != nil {
				row["read_error"] = readErr.Error()
			}
		}
		g23Write(t, "dispatches.json", rows)
		return response, e
	})}
}

func i34Profile(t *testing.T, s *Server, plan map[string]any, structured bool, id string) string {
	t.Helper()
	c, rev, e := s.Store.Configuration(context.Background())
	g23Require(t, e)
	p := c["llm_profiles"].([]any)[0].(map[string]any)
	for k, v := range plan["common_profile"].(map[string]any) {
		p[k] = v
	}
	for k, v := range map[string]any{"id": id, "provider": "local_responses", "model": plan["model"], "endpoint": "http://ollama:11434/v1/responses", "credential_ref": "local-none", "adapter_version": "local-responses-v1", "stream": false, "structured_output": structured} {
		p[k] = v
	}
	c["llm_profiles"], c["llm_profile"] = []any{p}, id
	for role := range c["stage_profiles"].(map[string]any) {
		c["stage_profiles"].(map[string]any)[role] = nil
	}
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	saved, _, e := s.Store.PutConfiguration(context.Background(), g23JSON(c), uuid.NewString(), rev)
	g23Require(t, e)
	return saved["configuration_sha256"].(string)
}

func i34Snapshot(t *testing.T, s *Server, prefix string, p map[string]any) {
	t.Helper()
	if p == nil {
		return
	}
	read, e := s.Store.Preparation(context.Background(), p["id"].(string))
	g23Require(t, e)
	g23Write(t, prefix+"preparation.json", read)
	for _, name := range []string{"settings_asset_id", "canonical_asset_id", "candidate_asset_id", "mutated_asset_id", "mutation_manifest_asset_id"} {
		if id, ok := read[name].(string); ok && id != "" {
			raw, e := s.Store.ReadAsset(context.Background(), id)
			g23Require(t, e)
			g23Require(t, os.WriteFile(filepath.Join(os.Getenv("TANGERINE_GEMINI_EVIDENCE"), prefix+name+".json"), raw, 0600))
		}
	}
}

func TestNativeLocalGenerationComparison(t *testing.T) {
	if os.Getenv("TANGERINE_LOCAL_LIVE") != "1" {
		t.Fatal("explicit local functional inference required")
	}
	raw, e := os.ReadFile("/plan/PLAN.json")
	g23Require(t, e)
	var plan map[string]any
	g23Require(t, json.Unmarshal(raw, &plan))
	s, _ := g23Setup(t)
	defer g23Dump(t, s, "")
	client := i34Client(t)
	observations := []any{}
	for _, a := range plan["alternatives"].([]any) {
		alternative := a.(map[string]any)
		for _, c := range plan["cases"].([]any) {
			casePlan := c.(map[string]any)
			id := alternative["id"].(string) + "-" + casePlan["id"].(string)
			sha := i34Profile(t, s, plan, alternative["structured_output"].(bool), id)
			request := map[string]any{}
			for k, v := range plan["case_settings"].(map[string]any) {
				request[k] = v
			}
			request["topic"], request["mutation_count"] = casePlan["topic"], casePlan["mutation_count"]
			b, e := s.Store.WriteBlueprint(context.Background(), g23JSON(map[string]any{"exercise_request": request}), uuid.NewString())
			g23Require(t, e)
			g23Write(t, id+"-blueprint.json", b)
			r := CanonicalPreparationRequest{BlueprintID: b["id"].(string), ConfigurationSHA: sha, Sources: []string{}, Attempt: 1}
			ctx, cancel := context.WithTimeout(context.Background(), 270*time.Second)
			start := time.Now()
			p, e := s.PrepareCanonical(ctx, r, uuid.NewString(), client)
			row := map[string]any{"id": id, "alternative": alternative["id"], "case": casePlan["id"], "canonical_seconds": time.Since(start).Seconds(), "configuration_sha256": sha}
			i34Snapshot(t, s, id+"-", p)
			if e == nil {
				pid := p["id"].(string)
				r.PreparationID = &pid
				r.Attempt = len(p["operation_ids"].([]any)) + 1
				startMutation := time.Now()
				p, e = s.PrepareMutation(ctx, r, uuid.NewString(), client)
				row["mutation_seconds"] = time.Since(startMutation).Seconds()
				i34Snapshot(t, s, id+"-", p)
			}
			row["total_seconds"] = time.Since(start).Seconds()
			cancel()
			row["admitted"] = e == nil
			if e != nil {
				code, detail := provider.SafeError(e)
				row["error_code"], row["error_detail"] = code, detail
			}
			if p != nil {
				row["preparation_id"] = p["id"]
			}
			observations = append(observations, row)
			g23Write(t, "observations.json", observations)
			t.Log("observed", id, "admitted", e == nil, "seconds", time.Since(start).Seconds())
		}
	}
}
