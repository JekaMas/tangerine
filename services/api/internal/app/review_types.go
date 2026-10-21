package app

import (
	"encoding/json"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

// ReviewRun is a durable foreground checkpoint. Frozen model inputs and native
// receipts stay private; reviewView is the explicit learner projection.
type ReviewRun struct {
	SelectionID      string `json:"selection_event_id"`
	TargetCase       string `json:"target_case_version_id"`
	ReviewContextID  string `json:"review_context_id"`
	ReviewDecisionID string `json:"review_decision_id"`
	AdjudicationID   string `json:"adjudication_id"`
	ResultRevisionID string `json:"result_revision_id"`

	AudioSHA       string                `json:"audio_sha256"`
	ID             string                `json:"id"`
	Purpose        string                `json:"purpose"`
	Case           string                `json:"case_version_id"`
	Attempt        string                `json:"attempt_id"`
	BaseResult     string                `json:"base_result_id"`
	Statement      string                `json:"statement"`
	Claims         []string              `json:"claim_ids"`
	Units          []string              `json:"unit_ids"`
	Evidence       []string              `json:"evidence_ids"`
	Modality       string                `json:"input_modality"`
	Status         string                `json:"status"`
	Revision       int64                 `json:"revision"`
	Frozen         string                `json:"frozen_asset_id"`
	Output         string                `json:"output_asset_id"`
	Projection     string                `json:"projection_asset_id"`
	Mapping        string                `json:"mapping_asset_id"`
	Issues         string                `json:"issues_asset_id"`
	NewResult      string                `json:"new_result_id"`
	NewCase        string                `json:"new_case_version_id"`
	Correspondence string                `json:"unit_correspondence_id"`
	Resolution     string                `json:"resolution"`
	Failure        string                `json:"failure_code"`
	Created        string                `json:"created_at"`
	Stages         []InterpretationStage `json:"stages"`
}
type ReviewFrozen struct {
	Measurements    []any                   `json:"measurements"`
	OriginalKey     map[string]any          `json:"original_key"`
	Correspondences []any                   `json:"unit_correspondences"`
	Taxonomy        map[string]any          `json:"taxonomy_context"`
	Record          AttemptRecord           `json:"record"`
	Resources       InterpretationResources `json:"resources"`
	Key             map[string]any          `json:"key"`
	Extraction      CanonicalExtraction     `json:"extraction"`
	Mapping         SemanticMapping         `json:"mapping"`
	Manifest        any                     `json:"mutation_manifest"`
	Profile         provider.Profile        `json:"profile"`
	Bundle          lab.Bundle              `json:"bundle"`
	Configuration   map[string]any          `json:"configuration"`
}
type ReviewProjection struct {
	Key            map[string]any    `json:"key"`
	Correspondence map[string]any    `json:"correspondence"`
	IDs            map[string]string `json:"local_ids"`
	Rationales     []map[string]any  `json:"rationales"`
}
type reviewLease struct {
	Run       ReviewRun
	Operation string
	Epoch     int64
	Replay    bool
}

func reviewClone(value any) map[string]any {
	raw, _ := json.Marshal(value)
	var out map[string]any
	_ = json.Unmarshal(raw, &out)
	return out
}
func reviewView(r ReviewRun, output map[string]any) map[string]any {
	if r.Status != "complete" {
		r.NewResult = ""
		r.NewCase = ""
		r.Correspondence = ""
	}
	if output != nil {
		output = reviewClone(output)
		delete(output, "admitted_mapping")
	}
	return map[string]any{"schema_version": "2.0.0", "id": r.ID, "purpose": r.Purpose, "case_version_id": r.Case, "attempt_id": r.Attempt, "base_result_id": r.BaseResult, "statement": r.Statement, "status": r.Status, "revision": r.Revision, "resolution": r.Resolution, "failure_code": r.Failure, "new_result_id": r.NewResult, "new_case_version_id": r.NewCase, "unit_correspondence_id": r.Correspondence, "created_at": r.Created, "origin": "llm", "person_id": nil, "qualification_ids": []any{}, "input_modality": r.Modality, "findings": output}
}
