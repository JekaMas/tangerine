package source

import (
	"fmt"
	"path"
	"strings"
)

const JFLEGParserVersion = "source-native-jfleg-v1"
const CorrectionScorerVersion = "source-reference-membership-v1"

// Complete owner snapshot members at the selected commit; code stays inert.
var JFLEGRequiredMembers = []string{
	"EACL_exp/m2converter/README.md",
	"EACL_exp/m2converter/dev.ref.m2",
	"EACL_exp/m2converter/getpostagger.sh",
	"EACL_exp/m2converter/m2converter.py",
	"EACL_exp/m2converter/test.ref.m2",
	"EACL_exp/m2converter/util/__init__.py",
	"EACL_exp/m2converter/util/assignIOB.py",
	"EACL_exp/m2converter/util/edit_dist.py",
	"EACL_exp/manual_eval/README.md",
	"EACL_exp/manual_eval/coded_sentences.csv",
	"EACL_exp/mturk/pairwise.csv",
	"EACL_exp/mturk/sample.csv",
	"EACL_exp/mturk/template.html",
	"EACLshort037.pdf",
	"README.md",
	"dev/dev.ref0",
	"dev/dev.ref1",
	"dev/dev.ref2",
	"dev/dev.ref3",
	"dev/dev.spellchecked.src",
	"dev/dev.src",
	"eval/gleu.py",
	"eval/readme.md",
	"test/test.ref0",
	"test/test.ref1",
	"test/test.ref2",
	"test/test.ref3",
	"test/test.spellchecked.src",
	"test/test.src",
}

// JFLEGFile identifies only the owner's documented parallel core files. The
// experimental M2/CSV representations never replace the original .src input.
func JFLEGFile(member string) (partition, table string, ok bool) {
	partition = path.Base(path.Dir(member))
	if partition != "dev" && partition != "test" {
		return "", "", false
	}
	base := path.Base(member)
	if base == partition+".src" {
		return partition, "jfleg_source", true
	}
	if base == partition+".spellchecked.src" {
		return partition, "jfleg_spellchecked", true
	}
	for i := 0; i < 4; i++ {
		if base == fmt.Sprintf("%s.ref%d", partition, i) {
			return partition, fmt.Sprintf("jfleg_ref%d", i), true
		}
	}
	return "", "", false
}

// SourceText keeps the supplied text, native line terminator and actual byte
// locator together. Text is not trimmed, retokenized, normalized or corrected.
type SourceText struct {
	Text       string `json:"text"`
	Member     string `json:"member"`
	AssetID    string `json:"asset_id"`
	SHA        string `json:"sha256"`
	LineIndex  int64  `json:"line_index"`
	LineEnding string `json:"line_ending"`
	Origin     string `json:"origin"`
}
type CorrectionReference struct {
	ID string `json:"reference_id"`
	SourceText
}
type CorrectionDifference struct {
	Reference           string `json:"reference_id"`
	Method              string `json:"method"`
	Kind                string `json:"kind"`
	OriginalSpan        [2]int `json:"original_codepoint_span"`
	ReferenceSpan       [2]int `json:"reference_codepoint_span"`
	OriginalText        string `json:"original_text"`
	Replacement         string `json:"replacement_text"`
	LinguisticAlignment string `json:"linguistic_alignment"`
	CategoryMapping     string `json:"category_mapping"`
}
type CorrectionExample struct {
	Version               string                 `json:"schema_version"`
	ID                    string                 `json:"id"`
	RecordID              string                 `json:"corpus_record_id"`
	Group                 string                 `json:"group_id"`
	Partition             string                 `json:"source_partition"`
	Split                 string                 `json:"split"`
	Original              SourceText             `json:"original"`
	References            []CorrectionReference  `json:"references"`
	Spellchecked          *SourceText            `json:"spellchecked"`
	Differences           []CorrectionDifference `json:"derived_differences"`
	ReferenceCompleteness string                 `json:"reference_completeness"`
}

// CoarseCorrectionDifference summarizes an exact text transformation. It does
// not claim the uniquely correct/minimal linguistic alignment of repeated words,
// supply error categories or turn four references into simultaneous mistakes.
func CoarseCorrectionDifference(original, reference, id string) CorrectionDifference {
	a, b := []rune(original), []rune(reference)
	prefix := 0
	for prefix < len(a) && prefix < len(b) && a[prefix] == b[prefix] {
		prefix++
	}
	suffix := 0
	for suffix < len(a)-prefix && suffix < len(b)-prefix && a[len(a)-1-suffix] == b[len(b)-1-suffix] {
		suffix++
	}
	d := CorrectionDifference{Reference: id, Method: "unicode-common-ends-v1", Kind: "coarse_replace", OriginalSpan: [2]int{prefix, len(a) - suffix}, ReferenceSpan: [2]int{prefix, len(b) - suffix}, OriginalText: string(a[prefix : len(a)-suffix]), Replacement: string(b[prefix : len(b)-suffix]), LinguisticAlignment: "not_computed", CategoryMapping: "not_supplied"}
	if original == reference {
		d.Kind = "unchanged"
	}
	return d
}
func NewCorrectionExample(version, record, partition string, ordinal int64, original SourceText, references []CorrectionReference, spellchecked *SourceText) CorrectionExample {
	id := fmt.Sprintf("%s:%d", partition, ordinal)
	split := "development"
	if partition == "test" {
		split = "held_out"
	}
	e := CorrectionExample{Version: "2.0.0", ID: id, RecordID: record, Group: StableID("jfleg", version, id), Partition: partition, Split: split, Original: original, References: references, Spellchecked: spellchecked, Differences: []CorrectionDifference{}, ReferenceCompleteness: "partial"}
	if len(references) == 4 {
		e.ReferenceCompleteness = "complete"
	}
	for _, r := range references {
		e.Differences = append(e.Differences, CoarseCorrectionDifference(original.Text, r.Text, r.ID))
	}
	return e
}

type CorrectionDataset struct {
	Version        string              `json:"schema_version"`
	Kind           string              `json:"kind"`
	Source         string              `json:"source_id"`
	Release        string              `json:"release_id"`
	SourceVersion  string              `json:"source_version"`
	SourceURI      string              `json:"source_uri"`
	SourceManifest string              `json:"source_manifest_sha256"`
	Partition      string              `json:"source_partition"`
	ScorerVersion  string              `json:"scorer_version"`
	Licence        string              `json:"licence"`
	Attribution    string              `json:"attribution"`
	Examples       []CorrectionExample `json:"examples"`
}
type CorrectionOutput struct {
	Example string `json:"example_id"`
	Text    string `json:"text"`
}
type CorrectionEvaluationRequest struct {
	Dataset CorrectionDataset  `json:"dataset"`
	Outputs []CorrectionOutput `json:"outputs"`
}
type CorrectionEvaluationRow struct {
	Index            int      `json:"output_index"`
	Example          string   `json:"example_id"`
	Matched          []string `json:"matched_reference_ids"`
	Status           string   `json:"status"`
	SemanticJudgment string   `json:"semantic_judgment"`
}
type CorrectionEvaluation struct {
	Version        string                    `json:"schema_version"`
	Source         string                    `json:"source_id"`
	Release        string                    `json:"release_id"`
	SourceVersion  string                    `json:"source_version"`
	SourceManifest string                    `json:"source_manifest_sha256"`
	Partition      string                    `json:"source_partition"`
	InputAsset     string                    `json:"input_asset_id,omitempty"`
	ScorerVersion  string                    `json:"scorer_version"`
	MatchPolicy    string                    `json:"match_policy"`
	Rows           []CorrectionEvaluationRow `json:"rows"`
	Totals         map[string]int            `json:"totals"`
}

// EvaluateCorrections records exact reference membership, never semantic grades.
// An unseen but valid repair remains unjudged; duplicated references keep every
// matched position. The function neither reads media nor invokes any model.
func EvaluateCorrections(r CorrectionEvaluationRequest) CorrectionEvaluation {
	examples := map[string]CorrectionExample{}
	for _, example := range r.Dataset.Examples {
		examples[example.ID] = example
	}
	report := CorrectionEvaluation{Version: "2.0.0", Source: r.Dataset.Source, Release: r.Dataset.Release, SourceVersion: r.Dataset.SourceVersion, SourceManifest: r.Dataset.SourceManifest, Partition: r.Dataset.Partition, ScorerVersion: CorrectionScorerVersion, MatchPolicy: "exact_native_text_v1", Rows: []CorrectionEvaluationRow{}, Totals: map[string]int{"logical_examples": len(examples), "submitted_outputs": len(r.Outputs), "reference_matches": 0, "not_in_reference_set": 0, "unknown_examples": 0, "logical_examples_with_outputs": 0, "unsubmitted_examples": len(examples)}}
	submitted := map[string]bool{}
	for i, output := range r.Outputs {
		row := CorrectionEvaluationRow{Index: i, Example: output.Example, Matched: []string{}, Status: "unknown_example", SemanticJudgment: "not_run"}
		if example, ok := examples[output.Example]; ok {
			submitted[example.ID] = true
			row.Status = "not_in_reference_set"
			for _, reference := range example.References {
				if reference.Text == output.Text {
					row.Matched = append(row.Matched, reference.ID)
				}
			}
			if len(row.Matched) > 0 {
				row.Status = "reference_match"
				report.Totals["reference_matches"]++
			} else {
				report.Totals["not_in_reference_set"]++
			}
		} else {
			report.Totals["unknown_examples"]++
		}
		report.Rows = append(report.Rows, row)
	}
	report.Totals["logical_examples_with_outputs"] = len(submitted)
	report.Totals["unsubmitted_examples"] = len(examples) - len(submitted)
	return report
}

func JFLEGExperimentalOrigin(member string) string {
	n := strings.ToLower(member)
	if strings.Contains(n, "/m2converter/") {
		return "source_tool_derivation"
	}
	if strings.Contains(n, "/manual_eval/") || strings.Contains(n, "/mturk/") {
		return "source_experimental_annotation"
	}
	return "source_metadata"
}
