package app

// A separate keyless local example, not fallback inside the frozen Gemini case.
import (
	"context"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/google/uuid"
)

func TestNativeLocalFullFlowBrowserFixture(t *testing.T) {
	if os.Getenv("TANGERINE_LOCAL_LIVE") != "1" {
		t.Fatal("explicit installed-local functional scope required")
	}
	s, _ := g23Setup(t)
	c, rev, err := s.Store.Configuration(context.Background())
	g23Require(t, err)
	base := c["llm_profiles"].([]any)[0].(map[string]any)
	generationModel, budget, structured := "tangerine-qwen35-9b-i6-20261020", 262144, true
	if os.Getenv("TANGERINE_I29_ALL_GPT_OSS") == "1" {
		generationModel, budget, structured = "gpt-oss:20b", 131072, false
	}
	if selected := os.Getenv("TANGERINE_I29_GENERATION_MODEL"); selected != "" {
		generationModel, budget, structured = selected, 131072, false
	}
	profiles := []any{}
	for _, spec := range []struct {
		id, model, effort string
		budget, output    int
		temperature       float64
		structured        bool
	}{
		{"generation-local-i29", generationModel, "low", budget, 8000, .2, structured},
		{"checking-local-i29", "gpt-oss:20b", "low", 131072, 4096, 0, false},
	} {
		p := map[string]any{}
		for k, v := range base {
			p[k] = v
		}
		for k, v := range map[string]any{"id": spec.id, "provider": "local_responses", "model": spec.model, "endpoint": "http://ollama:11434/v1/responses", "auth_method": "local_none", "billing_mode": "local", "credential_ref": "local-none", "adapter_version": "local-responses-v1", "context_budget_tokens": spec.budget, "max_output_tokens": spec.output, "temperature": spec.temperature, "reasoning_effort": spec.effort, "structured_output": spec.structured} {
			p[k] = v
		}
		profiles = append(profiles, p)
	}
	c["llm_profiles"], c["llm_profile"] = profiles, "generation-local-i29"
	for role := range c["stage_profiles"].(map[string]any) {
		id := "checking-local-i29"
		if role == "case_generation" {
			id = "generation-local-i29"
		}
		c["stage_profiles"].(map[string]any)[role] = id
	}
	for _, k := range []string{"workspace_id", "configuration_sha256", "provider_access_policy"} {
		delete(c, k)
	}
	_, _, err = s.Store.PutConfiguration(context.Background(), g23JSON(c), uuid.NewString(), rev)
	g23Require(t, err)
	defer i29Observe(t)()
	listener, err := net.Listen("tcp", ":8080")
	g23Require(t, err)
	server := &http.Server{Handler: s.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = server.Serve(listener) }()
	defer server.Close()
	dir := os.Getenv("TANGERINE_GEMINI_EVIDENCE")
	g23Write(t, "ready.json", map[string]any{"billing": "local; no provider key", "generation_model": generationModel, "checking_model": "gpt-oss:20b", "speech": "installed local Kokoro", "origin": "separate actual local workspace; CUA drives ordinary UI"})
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	deadline := time.After(3 * time.Hour)
	checkpoint := ""
	for {
		select {
		case <-deadline:
			t.Fatal("owned local observation deadline")
		case <-ticker.C:
			if raw, e := os.ReadFile(filepath.Join(dir, "capture-request")); e == nil && string(raw) != checkpoint {
				checkpoint = string(raw)
				i29Snapshot(t, s, checkpoint)
			}
			if _, e := os.Stat(filepath.Join(dir, "done")); e == nil {
				i29Snapshot(t, s, "final")
				return
			}
		}
	}
}
