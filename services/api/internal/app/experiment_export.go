package app

import (
	"context"
	"encoding/json"
	"os"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/experiment"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

// QualityDiagnostic prepares immutable local copies. Actual MLflow sync remains
// explicit and never dispatches a provider call. Native results survive Lab failure.
func (s *Storage) QualityDiagnostic(ctx context.Context, id string) (map[string]any, error) {
	p, e := s.QualityExperiment(ctx, id)
	if e != nil {
		return nil, e
	}
	f, e := s.frozenExperiment(ctx, id)
	if e != nil {
		return nil, e
	}
	// This immutable diagnostic is a pre-export snapshot; UI copy status is read
	// separately from actual export acknowledgments.
	p.Rows = append([]experiment.Row{}, p.Rows...)
	for i := range p.Rows {
		p.Rows[i].Export = "unexported"
	}
	var artifactErr error
	artifacts := []any{}
	nativePackets := []any{}
	seenOperations := map[string]bool{}
	manager := newProviderManager(s)
	secrets := []string{}
	for _, name := range []string{"OPENAI_API_KEY", "DEEPSEEK_API_KEY", "AZURE_SPEECH_KEY", "ELEVENLABS_API_KEY", "API_INTERNAL_TOKEN", "SPEECH_INTERNAL_TOKEN", "MINIO_SECRET_KEY", "MINIO_ROOT_PASSWORD"} {
		if value := os.Getenv(name); value != "" {
			secrets = append(secrets, value)
		}
	}
	for _, binding := range f.Variants {
		var profiles []provider.Profile
		_ = json.Unmarshal(sourceBytes(binding.Configuration["llm_profiles"]), &profiles)
		for _, profile := range profiles {
			secrets = append(secrets, manager.CredentialValues(ctx, profile.CredentialRef)...)
		}
	}

	add := func(name string, value any) {
		body := sourceBytes(value)
		sanitized, e := lab.Sanitize(body, secrets, true)
		if e != nil {
			artifactErr = e
			return
		}
		body = sanitized.Bytes
		artifacts = append(artifacts, map[string]any{"name": name, "body": string(body), "sha256": contracts.Digest(body)})
	}
	add("experiment.json", p)
	add("coverage.json", qualityCoverage(p, f.Dataset))
	if p.Comparison != nil {
		b, e := s.ReadAsset(ctx, *p.Comparison)
		if e != nil {
			return nil, e
		}
		add("comparison.json", json.RawMessage(b))
	}
	for _, r := range p.Rows {
		if r.Output != nil {
			b, e := s.ReadAsset(ctx, *r.Output)
			if e != nil {
				return nil, e
			}
			if f.Variants[r.Variant].Configuration["llm_lab_capture_content"] == true {
				add("row-"+lab.Hash([]any{r.Case, r.Variant, r.Repetition})+".json", json.RawMessage(b))
			}
			for _, receipt := range r.Receipts {
				doc, e := s.ReadDocument(ctx, receipt)
				if e != nil {
					return nil, e
				}
				var value map[string]any
				_ = json.Unmarshal(doc.Payload, &value)
				operation, _ := value["operation_id"].(string)
				if operation == "" || seenOperations[operation] {
					continue
				}
				seenOperations[operation] = true
				var asset string
				e = s.DB.QueryRow(ctx, "SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND o.idempotency_key::text=$1 AND a.state='linked'", operation).Scan(&asset)
				if e != nil {
					return nil, e
				}
				raw, e := s.ReadAsset(ctx, asset)
				if e != nil {
					return nil, e
				}
				nativePackets = append(nativePackets, json.RawMessage(raw))
			}

		}
	}
	if artifactErr != nil {
		return nil, artifactErr
	}
	return map[string]any{"operation": interpretationCallKey(id, "quality-export/"+lab.Hash(p)), "origin": "native_quality_experiment", "capture": true, "development_run_id": f.DevelopmentID, "provider_packets": nativePackets, "trace_enabled": false, "artifacts": artifacts, "experiment": p}, nil
}
func qualityCoverage(p QualityExperiment, d QualityDataset) []map[string]any {
	out := []map[string]any{}
	for _, id := range taxonomyLeafIDs() {
		pos, neg, observed := 0, 0, 0
		for _, c := range d.Cases {
			found := false
			for _, leaf := range c.Taxonomy {
				found = found || leaf == id
			}
			if !found {
				continue
			}
			if c.Polarity == "positive" {
				pos++
			} else {
				neg++
			}
			for _, r := range p.Rows {
				if r.Case == c.ID && r.Status == "complete" {
					observed++
				}
			}
		}
		out = append(out, map[string]any{"taxonomy_id": id, "positive_cases": pos, "negative_cases": neg, "completed_rows": observed, "missing": pos == 0 || neg == 0})
	}
	return out
}
