package app

import (
	"context"
	"encoding/json"
	"tangerine.local/api/internal/experiment"
	"tangerine.local/api/internal/lab"
)

type QualityCase struct {
	Context         *string  `json:"context_asset_id,omitempty"`
	ContextSHA      *string  `json:"context_sha256,omitempty"`
	Version         string   `json:"schema_version"`
	ID              string   `json:"id"`
	Stage           string   `json:"stage"`
	Phase           *string  `json:"phase"`
	Polarity        string   `json:"polarity"`
	Origin          string   `json:"origin"`
	Basis           string   `json:"expectation_basis"`
	Group           string   `json:"group_id"`
	Split           string   `json:"split"`
	Taxonomy        []string `json:"taxonomy_ids"`
	Input           string   `json:"input_asset_id"`
	InputSHA        string   `json:"input_sha256"`
	Expectations    string   `json:"expectations_asset_id"`
	ExpectationsSHA string   `json:"expectations_sha256"`
	References      []string `json:"reference_receipt_ids"`
}
type QualityDataset struct {
	Version string        `json:"schema_version"`
	Scope   string        `json:"scope"`
	Stage   *string       `json:"stage"`
	Phase   *string       `json:"phase"`
	Cases   []QualityCase `json:"cases"`
	SHA     string        `json:"dataset_sha256"`
}
type QualityVariant struct {
	ID        string  `json:"id"`
	BundleID  string  `json:"bundle_id"`
	BundleSHA string  `json:"bundle_sha256"`
	Profile   string  `json:"profile_id"`
	Config    string  `json:"configuration_asset_id"`
	ConfigSHA string  `json:"configuration_sha256"`
	Judge     *string `json:"judge_profile_id"`
}
type QualityAggregate struct {
	Variant string            `json:"variant_id"`
	Metric  experiment.Metric `json:"metric"`
}
type QualityExperiment struct {
	Version        string             `json:"schema_version"`
	ID             string             `json:"id"`
	Scope          string             `json:"scope"`
	Dataset        string             `json:"dataset_asset_id"`
	DatasetSHA     string             `json:"dataset_sha256"`
	Scorer         string             `json:"scorer_version"`
	RegistrySHA    string             `json:"metric_registry_sha256"`
	Variants       []QualityVariant   `json:"variants"`
	Repetitions    int                `json:"repetitions"`
	Status         string             `json:"status"`
	Rows           []experiment.Row   `json:"rows"`
	Comparison     *string            `json:"comparison_asset_id"`
	Created        string             `json:"created_at"`
	Finished       *string            `json:"finished_at"`
	Aggregates     []QualityAggregate `json:"aggregates"`
	JudgePolicy    *string            `json:"judge_policy_asset_id"`
	JudgePolicySHA *string            `json:"judge_policy_sha256"`
}
type qualityAnswerInput struct {
	Case   string `json:"case_version_id"`
	SHA    string `json:"case_sha256"`
	Answer string `json:"answer_text"`
}
type qualityFrozen struct {
	DevelopmentID       *string                       `json:"development_run_id"`
	Answers             map[string]qualityAnswerInput `json:"answers"`
	SubmittedDataset    string                        `json:"submitted_dataset_asset_id"`
	SubmittedDatasetSHA string                        `json:"submitted_dataset_sha256"`
	Contexts            map[string]map[string]any     `json:"contexts"`
	Dataset             QualityDataset                `json:"dataset"`
	Inputs              map[string]json.RawMessage    `json:"inputs"`
	Expected            map[string]json.RawMessage    `json:"expectations"`
	Variants            map[string]qualityBinding     `json:"variants"`
	Judge               map[string]any                `json:"judge_policy"`
}
type qualityBinding struct {
	Configuration map[string]any `json:"configuration"`
	Bundle        lab.Bundle     `json:"prompt_bundle"`
}
type qualityContextKey struct{}

func qualityContext(ctx context.Context, b qualityBinding) context.Context {
	return context.WithValue(ctx, qualityContextKey{}, b)
}
func frozenQuality(ctx context.Context) (qualityBinding, bool) {
	b, ok := ctx.Value(qualityContextKey{}).(qualityBinding)
	return b, ok
}
