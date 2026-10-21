package app

// Actual installed local inference. Independent literal linguistic/absence
// assertions below are authored before the model runs; no hosted/paid calls.
import (
	"bytes"
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"testing"
)

var qualityLocalOnce sync.Once
var qualityLocalObserved struct {
	Plan   QualityExperiment
	Judges []map[string]any
	Dir    string
}

func observeQualityLocal(t *testing.T) {
	qualityLocalOnce.Do(func() {
		f := interpretationNative(t, "good")
		r := qualitySubmission(t, f, 1, 2, 1)
		r.Development = true
		profileBytes, e := os.ReadFile(os.Getenv("TANGERINE_QUALITY_LOCAL_PROFILE"))
		requireListening(t, e)
		var profile map[string]any
		requireListening(t, json.Unmarshal(profileBytes, &profile))
		for i := range r.Experiment.Variants {
			v := &r.Experiment.Variants[i]
			var c map[string]any
			requireListening(t, json.Unmarshal(r.Assets[v.Config], &c))
			p := c["llm_profiles"].([]any)[0].(map[string]any)
			for key, value := range profile {
				p[key] = value
			}
			p["temperature"] = float64(i) / 10
			delete(c, "configuration_sha256")
			c["configuration_sha256"] = lab.Hash(c)
			r.Assets[v.Config] = mustJSON(c)
			v.ConfigSHA = contracts.Digest(r.Assets[v.Config])
			judge := v.Profile
			v.Judge = &judge
		}
		expected := map[string]any{"schema_version": "1.0.0", "expected_mapping": nil, "expected_metric_values": []any{}, "expected_canonical_sha256": nil, "semantic_propositions": []any{map[string]any{"id": "preserved_quote", "proposition": "The candidate includes a clause whose exact_text preserves the original listener answer Use opens.", "expected": "supported", "scope": "canonical_text"}, map[string]any{"id": "invented_quote", "proposition": "The candidate includes a listener claim quote with the exact words This is a volcano.", "expected": "unsupported", "scope": "canonical_text"}, map[string]any{"id": "unheard_audio", "proposition": "The actual recording contains a dental fricative at exactly one second.", "expected": "unknown", "scope": "acoustic"}}}
		r.Assets["case-0-expected"] = mustJSON(expected)
		var d QualityDataset
		requireListening(t, json.Unmarshal(r.Assets["dataset"], &d))
		d.Cases[0].ExpectationsSHA = contracts.Digest(r.Assets["case-0-expected"])
		var ds map[string]any
		requireListening(t, json.Unmarshal(mustJSON(d), &ds))
		delete(ds, "dataset_sha256")
		d.SHA = lab.Hash(ds)
		r.Assets["dataset"] = mustJSON(d)
		r.Experiment.DatasetSHA = d.SHA
		prompt, e := os.ReadFile(os.Getenv("TANGERINE_QUALITY_JUDGE_PROMPT"))
		requireListening(t, e)
		registry, e := contracts.Registry()
		requireListening(t, e)
		policy := map[string]any{"prompt_text": string(prompt), "prompt_sha256": contracts.Digest(prompt), "rubric_version": "constructed-reference-v1", "rubric_text": "Use only the supplied context and candidate. supported requires positive support. unsupported means the supplied candidate contradicts the proposition or a complete candidate lacks the asserted quote. A proposition about actual sound cannot be established from text; with no supplied recording or acoustic observation return unknown and say what is missing. Do not invent observations or numeric grades.", "input_schema_sha256": registry["llm-quality-judge-input"].SHA, "output_schema_sha256": registry["llm-quality-judge-output"].SHA}
		r.Assets["judge-policy"] = mustJSON(policy)
		r.Experiment.JudgePolicy = ptrQuality("judge-policy")
		r.Experiment.JudgePolicySHA = ptrQuality(contracts.Digest(r.Assets["judge-policy"]))
		p, e := f.s.Store.AdmitExperiment(context.Background(), r)
		requireListening(t, e)
		dir := os.Getenv("TANGERINE_QUALITY_LOCAL_EVIDENCE")
		requireListening(t, os.MkdirAll(dir, 0700))
		qualityLocalObserved.Dir = dir
		requireListening(t, os.WriteFile(filepath.Join(dir, "submission.json"), mustJSON(r), 0600))
		dispatch, e := os.Create(filepath.Join(dir, "dispatch-observations.jsonl"))
		requireListening(t, e)
		defer dispatch.Close()
		transport := &http.Transport{}
		defer transport.CloseIdleConnections()
		client := &http.Client{Transport: preparationTrip(func(req *http.Request) (*http.Response, error) {
			body, e := io.ReadAll(req.Body)
			if e != nil {
				return nil, e
			}
			req.Body = io.NopCloser(bytes.NewReader(body))
			clone := req.Clone(req.Context())
			u := *req.URL
			u.Host = req.URL.Host
			clone.URL = &u
			response, e := transport.RoundTrip(clone)
			event := map[string]any{"request_sha256": contracts.Digest(body), "actual_endpoint": clone.URL.String(), "billing_mode": "local", "fixture_response": false, "wire_request_body": string(body)}
			if e == nil {
				reply, er := io.ReadAll(response.Body)
				response.Body.Close()
				response.Body = io.NopCloser(bytes.NewReader(reply))
				event["response_sha256"] = contracts.Digest(reply)
				event["wire_response_body"] = string(reply)
				event["status"] = response.StatusCode
				if er != nil {
					e = er
				}
			}
			if e != nil {
				event["error"] = e.Error()
			}
			_ = json.NewEncoder(dispatch).Encode(event)
			return response, e
		})}
		p, e = f.s.RunQualityExperiment(context.Background(), p.ID, false, client)
		requireListening(t, os.WriteFile(filepath.Join(dir, "experiment.json"), mustJSON(p), 0600))
		requireListening(t, e)

		for _, row := range p.Rows {
			raw, e := f.s.Store.ReadAsset(context.Background(), *row.Output)
			requireListening(t, e)
			requireListening(t, os.WriteFile(filepath.Join(dir, row.Variant+"-output.json"), raw, 0600))
			var packet map[string]any
			requireListening(t, json.Unmarshal(raw, &packet))
			if judge, ok := packet["judge"].(map[string]any); ok {
				qualityLocalObserved.Judges = append(qualityLocalObserved.Judges, judge)
			}
		}
		packet, e := f.s.Store.QualityDiagnostic(context.Background(), p.ID)
		requireListening(t, e)
		requireListening(t, os.WriteFile(filepath.Join(dir, "quality-export.json"), mustJSON(packet), 0600))
		rows, e := f.s.Store.DB.Query(context.Background(), "SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND a.state='linked'")
		requireListening(t, e)
		ids := []string{}
		for rows.Next() {
			var id string
			requireListening(t, rows.Scan(&id))
			ids = append(ids, id)
		}
		rows.Close()
		for _, id := range ids {
			b, e := f.s.Store.ReadAsset(context.Background(), id)
			requireListening(t, e)
			requireListening(t, os.WriteFile(filepath.Join(dir, "diagnostic-"+id+".json"), b, 0600))
		}
		if p.Status != "completed" {
			t.Fatalf("actual local experiment incomplete: %s; private outputs retained at %s", p.Status, dir)
		}
		qualityLocalObserved.Plan = p
	})
}
func TestNativeQualityLocalPositive(t *testing.T) {
	observeQualityLocal(t)
	if len(qualityLocalObserved.Plan.Rows) != 2 {
		t.Fatal("actual local observation incomplete")
	}
	for _, row := range qualityLocalObserved.Plan.Rows {
		if row.Status != "complete" || len(row.Receipts) < 2 || len(row.Traces) < 2 {
			t.Fatal(row)
		}
	}
	for _, judge := range qualityLocalObserved.Judges {
		found := false
		for _, v := range judge["verdicts"].([]any) {
			m := v.(map[string]any)
			if m["proposition_id"] == "preserved_quote" {
				found = true
				if m["verdict"] != "supported" {
					t.Fatal("independent preserved-quote reference failed", m)
				}
			}
		}
		if !found {
			t.Fatal("missing positive verdict")
		}
	}
}
func TestNativeQualityLocalNegative(t *testing.T) {
	observeQualityLocal(t)
	if qualityLocalObserved.Plan.ID == "" {
		t.Fatal("actual local observation incomplete; see preceding failure")
	}
	for _, judge := range qualityLocalObserved.Judges {
		bad, audio := false, false
		for _, v := range judge["verdicts"].([]any) {
			m := v.(map[string]any)
			if m["proposition_id"] == "invented_quote" {
				bad = true
				if m["verdict"] != "unsupported" {
					t.Fatal("invented wording falsely supported", m)
				}
			}
			if m["proposition_id"] == "unheard_audio" {
				audio = true
				if m["verdict"] != "unknown" || m["missing_reason"] == nil || strings.TrimSpace(m["missing_reason"].(string)) == "" {
					t.Fatal("text-only sound certainty", m)
				}
			}
		}
		if !bad || !audio {
			t.Fatal("negative/unknown reference missing")
		}
	}
}

var _ = uuid.NewString
