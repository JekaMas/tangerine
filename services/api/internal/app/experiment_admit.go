package app

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/experiment"
	"tangerine.local/api/internal/lab"
	"time"
)

// Submission aliases make portable experiment files usable without exposing storage
// internals. Every body is saved privately before the frozen experiment is created.
type QualitySubmission struct {
	DevelopmentID *string                    `json:"development_run_id,omitempty"`
	Development   bool                       `json:"development"`
	Experiment    QualityExperiment          `json:"experiment"`
	Assets        map[string]json.RawMessage `json:"assets"`
}

func (s *Storage) AdmitExperiment(ctx context.Context, r QualitySubmission) (QualityExperiment, error) {
	p := r.Experiment
	f := qualityFrozen{Answers: map[string]qualityAnswerInput{}, Contexts: map[string]map[string]any{}, Inputs: map[string]json.RawMessage{}, Expected: map[string]json.RawMessage{}, Variants: map[string]qualityBinding{}}
	if _, e := uuid.Parse(p.ID); e != nil {
		p.ID = uuid.NewString()
	}
	if r.Development {
		id := p.ID
		if r.DevelopmentID != nil {
			if _, e := uuid.Parse(*r.DevelopmentID); e != nil {
				return p, ErrInput
			}
			id = *r.DevelopmentID
		}
		f.DevelopmentID = &id
	}
	if p.Repetitions == 0 {
		p.Repetitions = 1
	}
	if p.Scorer == "" {
		p.Scorer = "quality-v1"
	}
	if p.Scorer != "quality-v1" {
		return p, fmt.Errorf("unknown diagnostic scorer")
	}
	aliases := map[string]Asset{}
	resolve := func(id string) ([]byte, string, string, error) {
		if a, ok := aliases[id]; ok {
			return r.Assets[id], a.ID, a.SHA, nil
		}
		if b, ok := r.Assets[id]; ok {
			a, e := s.saveProviderBytes(ctx, b, "provider_input")
			if e != nil {
				return nil, "", "", e
			}
			aliases[id] = a
			return b, a.ID, a.SHA, nil
		}
		b, e := s.ReadAsset(ctx, id)
		return b, id, contracts.Digest(b), e
	}
	raw, datasetID, _, e := resolve(p.Dataset)
	if e != nil {
		return p, e
	}
	if e = lab.ValidateDataset(raw); e != nil {
		return p, e
	}
	if e = json.Unmarshal(raw, &f.Dataset); e != nil {
		return p, e
	}
	if p.Scope != f.Dataset.Scope {
		return p, ErrInput
	}
	var manifest map[string]any
	_ = json.Unmarshal(raw, &manifest)
	delete(manifest, "dataset_sha256")
	digest := lab.Hash(manifest)
	if f.Dataset.SHA != digest || p.DatasetSHA != digest {
		return p, fmt.Errorf("dataset digest mismatch")
	}
	p.Dataset = datasetID
	f.SubmittedDataset = datasetID
	f.SubmittedDatasetSHA = p.DatasetSHA
	leaves := map[string]bool{}
	for _, id := range taxonomyLeafIDs() {
		leaves[id] = true
	}
	for i, c := range f.Dataset.Cases {
		for _, id := range c.Taxonomy {
			if !leaves[id] {
				return p, fmt.Errorf("unknown dataset taxonomy leaf: %s", id)
			}
		}
		b, id, sha, e := resolve(c.Input)
		if e != nil {
			return p, e
		}
		if sha != c.InputSHA {
			return p, fmt.Errorf("case input digest mismatch")
		}
		c.Input = id
		f.Inputs[c.ID] = b
		if p.Scope == "answer_pipeline" {
			admitted, e := s.admitQualityAnswer(ctx, b)
			if e != nil {
				return p, e
			}
			f.Answers[c.ID] = admitted
		}
		if p.Scope == "stage" {
			var input map[string]any
			if e = json.Unmarshal(b, &input); e != nil {
				return p, e
			}
			f.Contexts[c.ID] = qualityStageComponents(c.Stage, input)
			if c.Context != nil {
				body, contextID, contextSHA, err := resolve(*c.Context)
				if err != nil {
					return p, err
				}
				if c.ContextSHA == nil || *c.ContextSHA != contextSHA {
					return p, ErrReference
				}
				var parts map[string]any
				if err = json.Unmarshal(body, &parts); err != nil || parts == nil {
					return p, ErrInput
				}
				f.Contexts[c.ID] = parts
				c.Context = &contextID
			}
			if c.Stage == "feedback" && f.Contexts[c.ID]["answer"] == nil {
				record, e := s.Attempt(ctx, fmt.Sprint(input["attempt_id"]))
				if e != nil {
					return p, fmt.Errorf("feedback stage needs frozen upstream context asset or saved attempt")
				}
				f.Contexts[c.ID]["answer"] = record.Attempt["answer_text"]
			}

		}
		b, id, sha, e = resolve(c.Expectations)
		if e != nil {
			return p, e
		}
		if sha != c.ExpectationsSHA {
			return p, fmt.Errorf("expectation digest mismatch")
		}
		if _, _, e = contracts.Validate("llm-quality-expectations", "2.0.0", b); e != nil {
			return p, e
		}
		c.Expectations = id
		f.Expected[c.ID] = b
		if c.Basis == "independent_llm" && len(c.References) == 0 {
			return p, fmt.Errorf("independent reference requires actual receipt")
		}
		for _, id := range c.References {
			doc, e := s.ReadDocument(ctx, id)
			if e != nil || doc.Kind != "provider-receipt" {
				return p, ErrReference
			}
		}
		f.Dataset.Cases[i] = c
	}
	// Expand portable references into an admitted immutable dataset. Preserve both
	// original requested identity and the new exact resolved manifest identity.
	var admitted map[string]any
	_ = json.Unmarshal(sourceBytes(f.Dataset), &admitted)
	delete(admitted, "dataset_sha256")
	f.Dataset.SHA = lab.Hash(admitted)
	datasetAsset, e := s.saveProviderBytes(ctx, sourceBytes(f.Dataset), "provider_input")
	if e != nil {
		return p, e
	}
	p.Dataset = datasetAsset.ID
	p.DatasetSHA = f.Dataset.SHA
	seen := map[string]bool{}
	for vi, v := range p.Variants {
		if v.ID == "" || seen[v.ID] {
			return p, ErrInput
		}
		seen[v.ID] = true
		b, configID, sha, e := resolve(v.Config)
		if e != nil {
			return p, e
		}
		if sha != v.ConfigSHA {
			return p, fmt.Errorf("configuration digest mismatch")
		}
		v.Config = configID
		var binding qualityBinding
		if e = json.Unmarshal(b, &binding.Configuration); e != nil {
			return p, e
		}
		if _, _, e = contracts.Validate("configuration", "2.0.0", b); e != nil {
			return p, e
		}
		if e = validateProfileSelection(binding.Configuration); e != nil {
			return p, e
		}
		b, bundleID, _, e := resolve(v.BundleID)
		if e != nil {
			doc, de := s.ReadDocument(ctx, v.BundleID)
			if de != nil {
				return p, e
			}
			b = doc.Payload
			bundleID = doc.ID
		}
		v.BundleID = bundleID
		if e = json.Unmarshal(b, &binding.Bundle); e != nil {
			return p, e
		}
		if e = lab.ValidateBundle(binding.Bundle); e != nil {
			return p, e
		}
		if binding.Bundle.SHA != v.BundleSHA {
			return p, fmt.Errorf("bundle digest mismatch")
		}
		selected := false
		for _, x := range binding.Configuration["llm_profiles"].([]any) {
			if x.(map[string]any)["id"] == v.Profile {
				selected = true
			}
		}
		if !selected {
			return p, ErrReference
		}
		binding.Configuration["llm_profile"] = v.Profile
		binding.Configuration["active_prompt_bundle_id"] = nil
		// Variant stage overrides remain explicit. General profile selection applies
		// where no stage override is set in the complete frozen configuration.
		if r.Development {
			binding.Configuration["llm_lab_trace_enabled"] = true
			binding.Configuration["llm_lab_capture_content"] = true
		}
		binding.Configuration["configuration_sha256"] = nil
		delete(binding.Configuration, "configuration_sha256")
		binding.Configuration["configuration_sha256"] = lab.Hash(binding.Configuration)
		f.Variants[v.ID] = binding
		p.Variants[vi] = v
	}
	if len(p.Variants) == 0 {
		return p, ErrInput
	}
	if p.JudgePolicy != nil {
		b, policyID, sha, e := resolve(*p.JudgePolicy)
		if e != nil {
			return p, e
		}
		p.JudgePolicy = &policyID
		if p.JudgePolicySHA == nil || sha != *p.JudgePolicySHA {
			return p, ErrReference
		}
		if e = json.Unmarshal(b, &f.Judge); e != nil {
			return p, e
		}
		if _, _, e = contracts.Validate("llm-quality-judge-policy", "2.0.0", b); e != nil {
			return p, e
		}
	}
	if f.Judge != nil {
		registry, e := contracts.Registry()
		if e != nil {
			return p, e
		}
		if f.Judge["prompt_sha256"] != contracts.Digest([]byte(fmt.Sprint(f.Judge["prompt_text"]))) || f.Judge["input_schema_sha256"] != registry["llm-quality-judge-input"].SHA || f.Judge["output_schema_sha256"] != registry["llm-quality-judge-output"].SHA {
			return p, fmt.Errorf("new judge policy identity mismatch")
		}
	}

	registry, e := generationRegistry("llm-quality-metrics.v1.json")
	if e != nil {
		return p, e
	}
	if p.RegistrySHA != "" && p.RegistrySHA != contracts.Digest(registry) {
		return p, fmt.Errorf("diagnostic registry mismatch")
	}
	p.RegistrySHA = contracts.Digest(registry)
	p.Version = "2.0.0"
	p.Created = time.Now().UTC().Format(time.RFC3339Nano)
	p.Finished = nil
	p.Status = "planned"
	p.Comparison = nil
	p.Aggregates = []QualityAggregate{}
	p.Rows = []experiment.Row{}
	for _, c := range f.Dataset.Cases {
		for _, v := range p.Variants {
			for n := 1; n <= p.Repetitions; n++ {
				p.Rows = append(p.Rows, experiment.Row{Case: c.ID, Variant: v.ID, Repetition: n, Status: "not_run", Receipts: []string{}, Traces: []string{}, Metrics: []experiment.Metric{}, Export: "disabled"})
			}
		}
	}
	if _, _, e = contracts.Validate("llm-experiment", "2.0.0", sourceBytes(p)); e != nil {
		return p, e
	}
	asset, e := s.saveProviderBytes(ctx, sourceBytes(f), "provider_input")
	if e != nil {
		return p, e
	}
	_, e = s.DB.Exec(ctx, "INSERT INTO quality_experiment(id,frozen_asset_id,payload) VALUES($1,$2,$3)", p.ID, asset.ID, sourceBytes(p))
	return p, e
}
