package scoring

import "math/big"

var Domains = []string{"grammar", "lexis", "pronunciation.segmental", "pronunciation.suprasegmental", "fluency", "discourse", "pragmatics_register", "acceptable_variant", "unattributed_fp"}

type Unit struct {
	ID, Domain, Category, Kind string
	Accepted                   []string
	Weight                     int64
	Correction, Explanation    bool
}
type Decision struct {
	ID, Unit, Verdict, Category             string
	Members                                 []string
	CorrectionSupplied, ExplanationSupplied bool
	Correction, Explanation                 *big.Rat
}
type Input struct {
	Attempt, Case, DecisionSHA, Policy string
	Units                              []Unit
	Decisions                          []Decision
	Enabled                            map[string]bool
	Unresolved                         map[string]bool
	DomainUnresolved                   map[string]map[string]bool
	DuplicateClaims, UnresolvedClaims  int64
}
type Counts struct {
	G          int64 `json:"true_errors"`
	TP         int64 `json:"tp"`
	FN         int64 `json:"fn"`
	FP         int64 `json:"fp"`
	D          int64 `json:"designated_decoys"`
	DF         int64 `json:"decoy_false_positives"`
	Duplicates int64 `json:"duplicate_claims"`
	Unresolved int64 `json:"unresolved_claims"`
}
type DomainResult struct {
	Domain    string            `json:"domain"`
	G         int64             `json:"true_errors"`
	TP        int64             `json:"tp"`
	FN        int64             `json:"fn"`
	FP        int64             `json:"fp"`
	Precision Metric            `json:"precision"`
	Recall    Metric            `json:"recall"`
	F1        Metric            `json:"f1"`
	Metrics   map[string]Metric `json:"metrics"`
}
type Composite struct {
	Value   *float64 `json:"value_0_100"`
	Exact   *Exact   `json:"exact_value_0_100"`
	Enabled []string `json:"enabled_components"`
	Reason  *string  `json:"reason"`
	Display *string  `json:"display,omitempty"`
}
type Item struct {
	Unit        string         `json:"unit_id"`
	Kind        string         `json:"kind"`
	Category    string         `json:"category_id"`
	DecisionIDs []string       `json:"decision_ids"`
	Reference   map[string]any `json:"reference,omitempty"`
}
type Result struct {
	Version     string            `json:"schema_version"`
	Attempt     string            `json:"attempt_id"`
	Case        string            `json:"case_version_id"`
	DecisionSHA string            `json:"decision_set_sha256"`
	Policy      string            `json:"scoring_policy_version"`
	Status      string            `json:"status"`
	Counts      *Counts           `json:"counts"`
	Metrics     map[string]Metric `json:"metrics"`
	Domains     []DomainResult    `json:"domain_results"`
	Composite   Composite         `json:"composite"`
	Decisions   []string          `json:"item_decision_ids"`
	Semantic    bool              `json:"semantic_judgments_present"`
	Statistics  map[string]any    `json:"sufficient_statistics"`
	Explanation Metric            `json:"optional_explanation"`
	Items       []Item            `json:"items"`
}
