package app

// The foreground controller composes admitted stage owners. It never selects a
// more favorable answer, dispatches from a read, or replaces a frozen profile.
import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"net/http"
	"strings"
	"time"

	"github.com/google/uuid"
	"tangerine.local/api/internal/provider"
)

type InterpretationStage struct {
	Stage      string    `json:"stage"`
	Result     LLMResult `json:"result"`
	Diagnostic *string   `json:"diagnostic_asset_id"`
	Error      string    `json:"error_code"`
	Reused     bool      `json:"reused"`
}

func interpretationCallKey(operation, stage string) string {
	h := sha256.Sum256([]byte(operation + "/" + stage))
	b := h[:16]
	b[6] = (b[6] & 15) | 64
	b[8] = (b[8] & 63) | 128
	id, _ := uuid.FromBytes(b)
	return id.String()
}
func (s *Server) InterpretAttempt(ctx context.Context, id, key string, revision int64, answerSHA, configSHA string, client *http.Client) (InterpretationState, error) {
	return s.interpretAttempt(ctx, id, key, revision, answerSHA, configSHA, client, false)
}
func (s *Server) interpretAttempt(ctx context.Context, id, key string, revision int64, answerSHA, configSHA string, client *http.Client, feedbackOnly bool) (InterpretationState, error) {
	lease, e := s.Store.acquireInterpretation(ctx, id, key, revision, answerSHA, configSHA, feedbackOnly)
	if e != nil {
		return InterpretationState{}, e
	}
	if lease.Replay {
		var raw []byte
		var kind, document string
		e = s.Store.DB.QueryRow(ctx, "SELECT d.payload,d.kind,d.id FROM operation o JOIN document d ON d.id=coalesce(o.result_document_id,o.error_document_id) WHERE o.id=$1", lease.Operation).Scan(&raw, &kind, &document)
		var state InterpretationState
		if e == nil {
			if kind == "error-response" {
				var failure struct {
					Code string `json:"code"`
				}
				e = json.Unmarshal(raw, &failure)
				state = InterpretationState{Version: "2.0.0", ID: document, Status: "failed", Failure: &failure.Code}
			} else {
				e = json.Unmarshal(raw, &state)
			}
		}
		if e == nil && state.Status == "failed" && state.Failure != nil {
			e = &provider.Failure{Code: *state.Failure}
		}
		return state, e
	}
	work, cancel := context.WithDeadline(ctx, lease.Deadline)
	defer cancel()
	a := lease.Snapshot.Attempt
	state := InterpretationState{Version: "2.0.0", Attempt: id, Case: a["case_version_id"].(string), AnswerSHA: answerSHA, ConfigSHA: configSHA, BundleSHA: interpretationBundle(lease.Snapshot).SHA, Status: "running"}
	if lease.Previous != nil && lease.Previous.Resources != "" {
		state = *lease.Previous
		state.Status = "running"
		state.Failure = nil
	}
	resources := InterpretationResources{}
	issues := []InterpretationIssue{}
	stages := []InterpretationStage{}
	extraction := CanonicalExtraction{}
	mapping := SemanticMapping{}
	acceptedState := state
	retryAvailable := true
	retry := func() bool {
		if !retryAvailable {
			return false
		}
		retryAvailable = false
		return true
	}
	checkpoint := func(finish bool) error {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
		defer done()
		var err error
		state.Issues, err = s.Store.interpretationJSON(end, issues)
		if err != nil {
			return err
		}
		state.Stages, err = s.Store.interpretationJSON(end, stages)
		if err != nil {
			return err
		}
		err = s.Store.checkpointInterpretation(end, lease, &state, finish)
		if err == nil {
			acceptedState = state
		} else {
			state.Extraction = acceptedState.Extraction
			state.Mapping = acceptedState.Mapping
			state.Audit = acceptedState.Audit
			state.Result = acceptedState.Result
			state.FeedbackStatus = acceptedState.FeedbackStatus
		}
		return err
	}
	fail := func(err error) (InterpretationState, error) {
		state.Resources = acceptedState.Resources
		state.Extraction = acceptedState.Extraction
		state.Mapping = acceptedState.Mapping
		state.Audit = acceptedState.Audit
		state.Result = acceptedState.Result
		state.FeedbackStatus = acceptedState.FeedbackStatus
		code, _ := provider.SafeError(err)
		if code == "" {
			code = "INFRASTRUCTURE_UNAVAILABLE"
		}
		state.Status = "failed"
		state.Failure = &code
		if state.Resources == "" {
			if failureID, saveErr := s.Store.failInterpretationLease(context.WithoutCancel(ctx), lease, code); saveErr == nil {
				state.ID = failureID
			} else {
				return state, saveErr
			}
			return state, err
		}
		if saveErr := checkpoint(true); saveErr != nil {
			if failureID, fallbackErr := s.Store.failInterpretationLease(context.WithoutCancel(ctx), lease, code); fallbackErr != nil {
				return state, fallbackErr
			} else {
				state.ID = failureID
			}
			return state, saveErr
		}
		return state, err
	}
	if state.Resources == "" {
		resources, e = s.Store.interpretationResources(work, lease.Snapshot)
		if e != nil {
			return fail(e)
		}
		state.Resources, e = s.Store.interpretationJSON(work, resources)
		if e != nil {
			return fail(e)
		}
	} else {
		if e = s.Store.readInterpretationJSON(work, state.Resources, &resources); e != nil {
			return fail(e)
		}
		if state.Issues != "" {
			if e = s.Store.readInterpretationJSON(work, state.Issues, &issues); e != nil {
				return fail(e)
			}
		}
		if state.Stages != "" {
			if e = s.Store.readInterpretationJSON(work, state.Stages, &stages); e != nil {
				return fail(e)
			}
		}
	}
	if e = checkpoint(false); e != nil {
		return fail(e)
	}
	invoke := func(stage string, c *CanonicalExtraction, validate func([]byte) error) (LLMResult, error) {
		input, parts := interpretationInput(lease.Snapshot, resources, c)
		p, err := interpretationProfile(lease.Snapshot, stage)
		if err != nil {
			return LLMResult{}, err
		}
		cap := 40 * time.Second
		if stage != "blind_claim_extraction" {
			cap = 70 * time.Second
		}
		remaining := time.Until(lease.Deadline) - 5*time.Second
		if remaining < cap {
			cap = remaining
		}
		if cap <= 0 {
			return LLMResult{}, context.DeadlineExceeded
		}
		result, err := s.InvokeLLM(work, LLMRequest{NormalizeProjection: func(value any) any { return normalizeInterpretationShape(value, c) }, FrozenProfile: &p, TransportRetry: retry, Timeout: cap, Operation: OperationRequest{Name: stage, Key: interpretationCallKey(lease.Operation, stage), Path: "/api/v1/attempts/" + id + "/interpretation/" + stage, Body: json.RawMessage(`{}`)}, Stage: stage, Input: input, Components: parts, Configuration: lease.Snapshot.Context["configuration"].(map[string]any), Bundle: interpretationBundle(lease.Snapshot), Validate: validate}, client)
		observation := InterpretationStage{Stage: stage, Result: result}
		if err != nil {
			observation.Error, _ = provider.SafeError(err)
		}
		if len(result.ReceiptIDs) > 0 {
			end, done := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
			cfg := lease.Snapshot.Context["configuration"].(map[string]any)
			diagnostic, de := s.Store.LLMDiagnostic(end, result, cfg["llm_lab_capture_content"] == true, cfg["llm_lab_trace_enabled"] == true)
			done()
			if de == nil {
				observation.Diagnostic = &diagnostic.ID
			}
		}
		stages = append(stages, observation)
		return result, err
	}
	answer := a["answer_text"].(string)
	if state.Extraction != nil {
		if e = s.Store.readInterpretationJSON(work, *state.Extraction, &extraction); e != nil {
			return fail(e)
		}
		stages = append(stages, InterpretationStage{Stage: "blind_claim_extraction", Reused: true})
	} else {
		if strings.TrimSpace(answer) == "" {
			extraction = CanonicalExtraction{Extraction: AnswerExtraction{Version: "2.0.0", Clauses: []ExtractedClause{}, Unparsed: []AnswerSpan{}, Coverage: []ClaimCoverage{}, Relations: []ClaimRelation{}}, Claims: []CanonicalClaim{}, Conflicts: []string{}}
			if answer != "" {
				coverage := ClaimCoverage{Kind: "whitespace", Refs: []string{}}
				coverage.Span.End = len([]rune(answer))
				extraction.Extraction.Coverage = []ClaimCoverage{coverage}
			}
		} else {
			_, e = invoke("blind_claim_extraction", nil, func(raw []byte) error {
				var err error
				extraction, err = normalizeExtraction(answer, answerSHA, raw)
				return err
			})
			if e != nil {
				return fail(e)
			}
		}
		asset, err := s.Store.interpretationJSON(work, extraction)
		if err != nil {
			return fail(err)
		}
		state.Extraction = &asset
		if e = checkpoint(false); e != nil {
			return fail(e)
		}
	}
	if state.Mapping != nil {
		if e = s.Store.readInterpretationJSON(work, *state.Mapping, &mapping); e != nil {
			return fail(e)
		}
		stages = append(stages, InterpretationStage{Stage: "claim_mapping", Reused: true})
	} else {
		if len(extraction.Claims) == 0 && len(extraction.Extraction.Unparsed) == 0 {
			mapping = SemanticMapping{Version: "1.0.0", Decisions: []SemanticDecision{}}
		} else {
			_, e = invoke("claim_mapping", &extraction, func(raw []byte) error {
				var err error
				mapping, issues, err = normalizeMapping(answer, extraction, resources.Key, resources.TaxonomyIDs, resources.Evidence, a["task_components"].(map[string]any), raw)
				return err
			})
			if e != nil {
				return fail(e)
			}
		}
		asset, err := s.Store.interpretationJSON(work, mapping)
		if err != nil {
			return fail(err)
		}
		state.Mapping = &asset
		if e = checkpoint(false); e != nil {
			return fail(e)
		}
	}
	if !feedbackOnly && lease.Snapshot.Context["configuration"].(map[string]any)["mapping_audit_enabled"] == true && state.Audit == nil && len(extraction.Claims) > 0 {
		// An audit is a separate request over the same frozen extraction and key. Its
		// input is built without the mapper output, and its failure is nonblocking.
		currentIssues := []InterpretationIssue{}
		for _, issue := range issues {
			if issue.Code != "audit_disagreement" {
				currentIssues = append(currentIssues, issue)
			}
		}
		issues = currentIssues
		audit := SemanticMapping{}
		_, auditErr := invoke("mapping_audit", &extraction, func(raw []byte) error {
			var err error
			audit, _, err = normalizeMapping(answer, extraction, resources.Key, resources.TaxonomyIDs, resources.Evidence, a["task_components"].(map[string]any), raw)
			return err
		})
		if auditErr == nil {
			asset, err := s.Store.interpretationJSON(work, audit)
			if err != nil {
				return fail(err)
			}
			state.Audit = &asset
			if !compareMapping(mapping, audit) {
				issues = append(issues, InterpretationIssue{"audit_disagreement", []string{}, []string{}, []string{}, false, "Optional audit differs; supported mapper decisions are retained."})
			}
		} else {
			issues = append(issues, InterpretationIssue{"audit_disagreement", []string{}, []string{}, []string{}, false, "Optional audit was unavailable; supported mapper decisions are retained."})
		}
	}
	state.Status = "complete"
	for _, issue := range issues {
		if issue.Blocks {
			state.Status = "review_required"
		}
	}
	if e = s.finalizeScoring(ctx, work, lease, &state, resources, extraction, mapping, issues, &stages, client, retry, checkpoint); e != nil {
		return fail(e)
	}
	if e = checkpoint(true); e != nil {
		return fail(e)
	}
	return state, nil
}
