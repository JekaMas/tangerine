package source

import (
	"encoding/json"
	"strings"
	"testing"
)

func TestJFLEGNativePlanPositive(t *testing.T) {
	for file, table := range map[string]string{"owner/dev/dev.src": "jfleg_source", "owner/test/test.ref3": "jfleg_ref3", "owner/dev/dev.spellchecked.src": "jfleg_spellchecked"} {
		options, actual, ok := NativePlan("JFLEG", NewMember(file))
		if !ok || options.Format != "lines" || actual != table {
			t.Fatalf("%s: %s %+v %v", file, actual, options, ok)
		}
	}
	if !Known("JFLEG") || len(IDs) != 11 || len(AllIDs()) != 16 {
		t.Fatal("supplement replaced original source scope")
	}
	copy := AllIDs()
	copy[0] = "changed"
	if IDs[0] != "TET-GOLD-1" {
		t.Fatal("original source registry mutated")
	}
}
func TestJFLEGNativePlanNegative(t *testing.T) {
	for _, file := range []string{"owner/dev/test.ref0", "owner/EACL_exp/dev.src", "owner/dev/dev.ref4", "owner/EACL_exp/m2converter/dev.ref.m2"} {
		if _, _, ok := JFLEGFile(file); ok {
			t.Fatal("non-core representation replaced primary input", file)
		}
	}
	if Known("JFLEG-MISSING") {
		t.Fatal("unimplemented source accepted")
	}
	if JFLEGExperimentalOrigin("owner/EACL_exp/m2converter/dev.ref.m2") != "source_tool_derivation" {
		t.Fatal("M2 tool labels called native human error types")
	}
	if JFLEGExperimentalOrigin("owner/EACL_exp/manual_eval/coded_sentences.csv") != "source_experimental_annotation" {
		t.Fatal("native experimental annotation lost")
	}
}
func TestJFLEGCompleteMembersPositive(t *testing.T) {
	members := []Member{}
	for _, name := range JFLEGRequiredMembers {
		members = append(members, NewMember("owner/"+name))
	}
	if got := MissingNative("JFLEG", members); len(got) != 0 {
		t.Fatal("complete owner inventory missing", got)
	}
	if len(JFLEGRequiredMembers) != 29 {
		t.Fatal("owner release scope changed")
	}
}
func TestJFLEGCompleteMembersNegative(t *testing.T) {
	missing := MissingNative("JFLEG", []Member{NewMember("owner/dev/dev.src"), NewMember("foreign/README.md")})
	if len(missing) != 27 {
		t.Fatal("partial core input called complete", missing)
	}
	for _, name := range missing {
		if name == "dev/dev.src" || name == "README.md" {
			t.Fatal("present exact member lost")
		}
	}
}
func TestJFLEGCoarseDifferencePositive(t *testing.T) {
	for _, c := range []struct {
		a, b             string
		span             [2]int
		old, replacement string
	}{{"a cat", "a dog", [2]int{2, 5}, "cat", "dog"}, {"café x", "café y", [2]int{5, 6}, "x", "y"}, {"hi.", "hi there.", [2]int{2, 2}, "", " there"}, {"a bad day", "a day", [2]int{2, 6}, "bad ", ""}} {
		d := CoarseCorrectionDifference(c.a, c.b, "ref0")
		if d.OriginalSpan != c.span || d.OriginalText != c.old || d.Replacement != c.replacement {
			t.Fatalf("literal difference %+v", d)
		}
		a := []rune(c.a)
		replayed := string(a[:d.OriginalSpan[0]]) + d.Replacement + string(a[d.OriginalSpan[1]:])
		if replayed != c.b {
			t.Fatal("transform does not replay", d)
		}
	}
}
func TestJFLEGCoarseDifferenceNegative(t *testing.T) {
	for _, pair := range [][2]string{{"very very good", "very good"}, {"same ", "same "}, {"é", "e"}} {
		d := CoarseCorrectionDifference(pair[0], pair[1], "ref2")
		if d.LinguisticAlignment != "not_computed" || d.CategoryMapping != "not_supplied" {
			t.Fatal("invented linguistic labels", d)
		}
	}
	d := CoarseCorrectionDifference("same ", "same ", "ref0")
	if d.Kind != "unchanged" || d.Replacement != "" {
		t.Fatal("unchanged reference became mistake")
	}
	d = CoarseCorrectionDifference("é", "e", "ref1")
	if d.Kind == "unchanged" {
		t.Fatal("source unicode normalized")
	}
}
func TestJFLEGReferenceEvaluationPositive(t *testing.T) {
	original := SourceText{Text: "We go . "}
	refs := []CorrectionReference{{ID: "ref0", SourceText: original}, {ID: "ref1", SourceText: original}, {ID: "ref2", SourceText: SourceText{Text: "We will go . "}}, {ID: "ref3", SourceText: original}}
	example := NewCorrectionExample("pinned", "native", "dev", 0, original, refs, nil)
	outputs := []CorrectionOutput{}
	for _, r := range refs {
		outputs = append(outputs, CorrectionOutput{Example: example.ID, Text: r.Text})
	}
	report := EvaluateCorrections(CorrectionEvaluationRequest{Dataset: CorrectionDataset{Source: "JFLEG", Release: "actual", SourceVersion: "owner-v1", SourceManifest: strings.Repeat("a", 64), Partition: "dev", Examples: []CorrectionExample{example}}, Outputs: outputs})
	if report.Totals["reference_matches"] != 4 || len(report.Rows[0].Matched) != 3 || report.Rows[0].Matched[2] != "ref3" || report.Totals["logical_examples"] != 1 {
		t.Fatalf("alternatives conflated: %+v", report)
	}
	if report.SourceVersion != "owner-v1" || report.SourceManifest != strings.Repeat("a", 64) || report.Partition != "dev" {
		t.Fatal("evaluation lost source context")
	}
	if len(example.References) != 4 || len(example.Differences) != 4 || example.Split != "development" {
		t.Fatal("source positions lost")
	}
}
func TestJFLEGReferenceEvaluationNegative(t *testing.T) {
	e := NewCorrectionExample("pinned", "r", "test", 2, SourceText{Text: "original "}, []CorrectionReference{{ID: "ref0", SourceText: SourceText{Text: "A supplied reference . "}}}, nil)
	report := EvaluateCorrections(CorrectionEvaluationRequest{Dataset: CorrectionDataset{Source: "JFLEG", Examples: []CorrectionExample{e}}, Outputs: []CorrectionOutput{{Example: e.ID, Text: "Another valid correction."}, {Example: "unknown", Text: "A supplied reference . "}}})
	if report.Rows[0].Status != "not_in_reference_set" || report.Rows[1].Status != "unknown_example" {
		t.Fatal("unmatched input received a false reference", report)
	}
	for _, r := range report.Rows {
		if r.SemanticJudgment != "not_run" {
			t.Fatal("native membership became semantic grading")
		}
	}
	raw, _ := json.Marshal(report)
	if strings.Contains(string(raw), "incorrect") {
		t.Fatal("out-of-set repair called wrong")
	}
	if e.ReferenceCompleteness != "partial" || e.Split != "held_out" || len(e.References) != 1 {
		t.Fatal("partial references invented")
	}
}
