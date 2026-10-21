package app

// Explicit foreground orchestration only. Reads never dispatch; successful
// semantic and projection checkpoints survive an interrupted continuation.
import (
	"context"
	"encoding/json"
	"errors"
	"github.com/jackc/pgx/v5"
	"net/http"
	"strings"
	"tangerine.local/api/internal/provider"
	"time"
)

func (s *Server) CreateReview(ctx context.Context, r ReviewRun, key string) (ReviewRun, error) {
	if r.Purpose != "case_review" && r.Purpose != "dispute" && r.Purpose != "answer_reconsideration" {
		return r, ErrInput
	}
	if r.Case == "" || r.Purpose == "dispute" && strings.TrimSpace(r.Statement) == "" || len([]rune(r.Statement)) > 20000 {
		return r, ErrInput
	}
	if r.Purpose == "case_review" {
		if r.Attempt != "" || r.BaseResult != "" {
			return r, ErrInput
		}
	} else if r.Purpose == "answer_reconsideration" && (r.Attempt == "" || r.BaseResult == "") || (r.Attempt == "") != (r.BaseResult == "") {
		return r, ErrInput
	}
	if r.Claims == nil {
		r.Claims = []string{}
	}
	if r.Units == nil {
		r.Units = []string{}
	}
	if r.Evidence == nil {
		r.Evidence = []string{}
	}
	request := OperationRequest{Name: "create_review", Key: key, Path: "/api/v1/reviews", Body: reviewBytes(map[string]any{"purpose": r.Purpose, "case_version_id": r.Case, "audio_sha256": r.AudioSHA, "attempt_id": r.Attempt, "target_case_version_id": r.TargetCase, "result_id": r.BaseResult, "statement": r.Statement, "claim_ids": r.Claims, "unit_ids": r.Units, "evidence_ids": r.Evidence})}
	digest, e := operationDigest(request)
	if e != nil {
		return r, ErrInput
	}
	var existing, oldSHA string
	e = s.Store.DB.QueryRow(ctx, "SELECT subject_id,request_sha256 FROM operation WHERE operation_name='create_review' AND idempotency_key=$1", key).Scan(&existing, &oldSHA)
	if e == nil {
		if digest != oldSHA {
			return r, ErrConflict
		}
		return s.Store.Review(ctx, existing)
	}
	if e != pgx.ErrNoRows {
		return r, e
	}
	f, e := s.Store.freezeReview(ctx, r)
	if e != nil {
		return r, e
	}
	if r.AudioSHA != "" && r.AudioSHA != f.Key["audio"].(map[string]any)["sha256"] {
		return r, ErrConflict
	}
	units := map[string]bool{}
	for _, v := range f.Key["units"].([]any) {
		units[v.(map[string]any)["id"].(string)] = true
	}
	for _, id := range r.Units {
		if !units[id] {
			return r, ErrReference
		}
	}
	claims := map[string]bool{}
	for _, v := range f.Extraction.Claims {
		claims[v.ID] = true
	}
	for _, id := range r.Claims {
		if !claims[id] {
			return r, ErrReference
		}
	}
	evidence := map[string]bool{}
	for _, v := range f.Resources.Evidence {
		evidence[v.(map[string]any)["id"].(string)] = true
	}
	for _, id := range r.Evidence {
		if !evidence[id] {
			return r, ErrReference
		}
	}
	return s.Store.createReview(ctx, r, key, f)
}
func (s *Server) RunReview(ctx context.Context, id, key string, revision int64, client *http.Client) (ReviewRun, error) {
	lease, e := s.Store.acquireReview(ctx, id, key, revision)
	if e != nil {
		return ReviewRun{}, e
	}
	r := lease.Run
	if lease.Replay {
		return r, nil
	}
	var deadline time.Time
	if e = s.Store.DB.QueryRow(ctx, "SELECT deadline_at FROM review_checkpoint WHERE id=$1", id).Scan(&deadline); e != nil {
		return r, e
	}
	work, cancel := context.WithDeadline(ctx, deadline)
	defer cancel()
	checkpoint := func(finish bool) error {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
		defer done()
		return s.Store.checkpointReview(end, lease, &r, finish)
	}
	fail := func(err error) (ReviewRun, error) {
		r.Status = "failed"
		r.Failure, _ = provider.SafeError(err)
		if errors.Is(err, ErrAttemptRights) {
			r.Failure = "SOURCE_USE_RESTRICTED"
		}
		if r.Failure == "" {
			r.Failure = "INFRASTRUCTURE_UNAVAILABLE"
		}
		if saveErr := checkpoint(true); saveErr != nil {
			return r, saveErr
		}
		return r, err
	}
	f := ReviewFrozen{}
	if e = s.Store.readInterpretationJSON(work, r.Frozen, &f); e != nil {
		return fail(e)
	}
	if e = s.Store.reviewSourceAllowed(work, f.Key["case_version_id"].(string)); e != nil {
		return fail(e)
	}
	retryAvailable := true
	retry := func() bool {
		if !retryAvailable {
			return false
		}
		retryAvailable = false
		return true
	}
	invoke := func(stage string, p provider.Profile, input, parts map[string]any, normalize func(any) any, validate func([]byte) error) (LLMResult, error) {
		cap := min(stageTimeout(stage, nil), time.Until(deadline)-5*time.Second)
		if cap <= 0 {
			return LLMResult{}, context.DeadlineExceeded
		}
		hint := "Return the complete final review JSON, all actual base unit judgments and the requested supported resolution. Preserve the frozen answer/audio and correction versus optional reason."
		res, err := s.InvokeLLM(work, LLMRequest{Stage: stage, FrozenProfile: &p, NormalizeProjection: normalize, DiagnoseInvalid: func([]byte) string { return hint }, TransportRetry: retry, Timeout: cap, Input: input, Components: parts, Configuration: f.Configuration, Bundle: f.Bundle, Operation: OperationRequest{Name: stage, Key: interpretationCallKey(lease.Operation, stage), Path: "/api/v1/reviews/" + id + "/" + stage, Body: json.RawMessage(`{}`)}, Validate: func(b []byte) error {
			err := validate(b)
			if err != nil {
				hint = err.Error()
			}
			return err
		}}, client)
		observation := InterpretationStage{Stage: stage, Result: res}
		if err != nil {
			observation.Error, _ = provider.SafeError(err)
		}
		if len(res.ReceiptIDs) > 0 {
			end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
			d, de := s.Store.LLMDiagnostic(end, res, f.Configuration["llm_lab_capture_content"] == true, f.Configuration["llm_lab_trace_enabled"] == true)
			done()
			if de == nil {
				observation.Diagnostic = &d.ID
			}
		}
		r.Stages = append(r.Stages, observation)
		return res, err
	}
	var out map[string]any
	if r.Output == "" {
		input, parts := reviewInput(r, f)
		stage := "adjudication"
		if r.Purpose == "case_review" {
			stage = "case_review"
		}
		_, e = invoke(stage, f.Profile, input, parts, func(v any) any { return normalizeReviewShape(v, &f.Extraction) }, func(raw []byte) error { var err error; out, err = admitReview(raw, r, f); return err })
		if e != nil {
			return fail(e)
		}
		r.Output, e = s.Store.interpretationJSON(work, out)
		if e != nil {
			return fail(e)
		}
		r.Resolution = out["resolution"].(string)
		if e = checkpoint(false); e != nil {
			return fail(e)
		}
	} else {
		if e = s.Store.readInterpretationJSON(work, r.Output, &out); e != nil {
			return fail(e)
		}
	}
	projection := ReviewProjection{}
	resources := f.Resources
	if r.Resolution == "key_defect" {
		if r.Projection == "" {
			projection, e = projectReviewKey(f.Key, out["key_repair"].(map[string]any), r.ReviewDecisionID, allocateReviewID)
			if e != nil {
				return fail(e)
			}
			// These are new generated records: one schema admission precedes persistence.
			if _, _, e = contractsForReviewProjection(projection); e != nil {
				return fail(e)
			}
			r.Projection, e = s.Store.interpretationJSON(work, projection)
			if e != nil {
				return fail(e)
			}
			r.NewCase = projection.Key["case_version_id"].(string)
			r.Correspondence = projection.Correspondence["id"].(string)
			if e = checkpoint(false); e != nil {
				return fail(e)
			}
		} else {
			if e = s.Store.readInterpretationJSON(work, r.Projection, &projection); e != nil {
				return fail(e)
			}
		}
		resources.Key = reviewClone(f.Resources.Key)
		for k := range resources.Key {
			resources.Key[k] = projection.Key[k]
		}
		resources.Rationales = []any{}
		for _, v := range projection.Rationales {
			resources.Rationales = append(resources.Rationales, v)
		}
	}
	mapping := f.Mapping
	issues := []InterpretationIssue{}
	if r.Attempt != "" && (r.Resolution == "mapping_defect" || r.Resolution == "key_defect" || r.TargetCase != "" && r.Resolution == "supported") {
		if r.Mapping != "" {
			if e = s.Store.readInterpretationJSON(work, r.Mapping, &mapping); e != nil {
				return fail(e)
			}
			if r.Issues != "" {
				if e = s.Store.readInterpretationJSON(work, r.Issues, &issues); e != nil {
					return fail(e)
				}
			}
		} else {
			if admitted, ok := out["admitted_mapping"].(map[string]any); ok {
				var stored struct {
					Mapping SemanticMapping       `json:"mapping"`
					Issues  []InterpretationIssue `json:"issues"`
				}
				raw := reviewBytes(admitted)
				if r.Resolution == "key_defect" {
					raw = reviewBytes(remapReviewIDs(admitted, projection.IDs))
				}
				if e = json.Unmarshal(raw, &stored); e != nil {
					return fail(e)
				}
				mapping = stored.Mapping
				issues = stored.Issues
			} else {
				record := f.Record
				record.Attempt = reviewClone(record.Attempt)
				record.Attempt["case_version_id"] = resources.Key["case_version_id"]
				input, parts := interpretationInput(record, resources, &f.Extraction)
				p, err := interpretationProfile(f.Record, "claim_mapping")
				if err != nil {
					return fail(err)
				}
				_, e = invoke("claim_mapping", p, input, parts, func(v any) any { return normalizeInterpretationShape(v, &f.Extraction) }, func(raw []byte) error {
					var err error
					mapping, issues, err = normalizeMapping(record.Attempt["answer_text"].(string), f.Extraction, resources.Key, resources.TaxonomyIDs, resources.Evidence, record.Attempt["task_components"].(map[string]any), raw)
					return err
				})
				if e != nil {
					return fail(e)
				}
			}
			r.Issues, e = s.Store.interpretationJSON(work, issues)
			if e != nil {
				return fail(e)
			}
			r.Mapping, e = s.Store.interpretationJSON(work, mapping)
			if e != nil {
				return fail(e)
			}
			if e = checkpoint(false); e != nil {
				return fail(e)
			}
		}
	}
	// Final publication is one transaction. No supported change is exposed while a
	// required key projection or conditional same-answer mapping is still incomplete.
	prepared, err := s.prepareReviewedResult(work, &r, f, resources, mapping, issues)
	if err != nil {
		return fail(err)
	}
	if e = s.Store.finishReview(work, lease, &r, f, projection, out, prepared); e != nil {
		return fail(e)
	}
	return r, nil
}
func contractsForReviewProjection(p ReviewProjection) (DocumentWrite, SavedDocument, error) {
	w, d, e := reviewDocument("ground-truth", p.Key["case_version_id"].(string), p.Key)
	if e != nil {
		return w, d, e
	}
	if _, _, e = reviewDocument("unit-correspondence", p.Correspondence["id"].(string), p.Correspondence); e != nil {
		return w, d, e
	}
	for _, r := range p.Rationales {
		if _, _, e = reviewDocument("rationale", r["id"].(string), r); e != nil {
			return w, d, e
		}
	}
	return w, d, nil
}
