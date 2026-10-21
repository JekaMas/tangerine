package app

import (
	"reflect"
	"strings"
	"testing"
)

func reviewKeyFixture(t *testing.T) (map[string]any, map[string]any, map[string]bool) {
	s, c, f, p := speechKeyFixture(t)
	k := reviewClone(projectSpeechKey(s, c, f, p, "audio1", strings.Repeat("a", 64), "1.1.0"))
	k["status"] = "published"
	candidate := reviewCandidate(k)
	u := k["units"].([]any)[0].(map[string]any)
	id := u["id"].(string)
	proposal := map[string]any{"base_case_sha256": k["case_sha256"], "audio_sha256": k["audio"].(map[string]any)["sha256"], "affected_components": []any{"explanation"}, "proposed_units": candidate["planned_units"], "correspondence_relations": []any{map[string]any{"old_unit_ids": []any{id}, "new_unit_ids": []any{id}, "kind": "same", "reason": "Same heard event."}}, "reason": "Clarify the rationale without changing the recording."}
	return k, proposal, map[string]bool{u["primary_taxonomy_id"].(string): true}
}
func TestReviewKeySamePositive(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	if e := admitKeyRepair(k, p, tax); e != nil {
		t.Fatal(e)
	}
}
func TestReviewKeyHashNegative(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	p["base_case_sha256"] = strings.Repeat("b", 64)
	if admitKeyRepair(k, p, tax) == nil {
		t.Fatal("wrong frozen key accepted")
	}
}
func TestReviewKeyAudioNegative(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	p["audio_sha256"] = strings.Repeat("b", 64)
	if admitKeyRepair(k, p, tax) == nil {
		t.Fatal("different audio accepted")
	}
}
func TestReviewKeyProjectionPositive(t *testing.T) {
	k, p, _ := reviewKeyFixture(t)
	before := reviewClone(k)
	n := 0
	projected, e := projectReviewKey(k, p, "review", func() string { n++; return []string{"case2", "rationale2", "correspondence2"}[n-1] })
	if e != nil || projected.Key["case_version_id"] != "case2" || !reflect.DeepEqual(k, before) || !reflect.DeepEqual(k["audio"], projected.Key["audio"]) || !reflect.DeepEqual(k["utterances"], projected.Key["utterances"]) {
		t.Fatal(projected, e)
	}
	if projected.Correspondence["old_case_version_id"] != "case1" || projected.Correspondence["new_case_version_id"] != "case2" {
		t.Fatal(projected)
	}
}
func TestReviewKeyMissingRelationNegative(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	p["correspondence_relations"] = []any{}
	if admitKeyRepair(k, p, tax) == nil {
		t.Fatal("unexplained omission accepted")
	}
}
func TestReviewKeyAddedPositive(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	u := reviewClone(p["proposed_units"].([]any)[0])
	u["id"] = "new:u2"
	p["proposed_units"] = append(p["proposed_units"].([]any), u)
	p["correspondence_relations"] = append(p["correspondence_relations"].([]any), map[string]any{"old_unit_ids": []any{}, "new_unit_ids": []any{"new:u2"}, "kind": "added", "reason": "Discovered event."})
	if e := admitKeyRepair(k, p, tax); e != nil {
		t.Fatal(e)
	}
}
func TestReviewKeyDuplicateRelationNegative(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	p["correspondence_relations"] = append(p["correspondence_relations"].([]any), p["correspondence_relations"].([]any)[0])
	if admitKeyRepair(k, p, tax) == nil {
		t.Fatal("old/new event counted twice")
	}
}
func TestReviewKeyRemovedPositive(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	r := p["correspondence_relations"].([]any)[0].(map[string]any)
	r["kind"] = "removed"
	r["new_unit_ids"] = []any{}
	p["proposed_units"] = []any{}
	if e := admitKeyRepair(k, p, tax); e != nil {
		t.Fatal(e)
	}
}
func TestReviewKeyRelationShapeNegative(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	p["correspondence_relations"].([]any)[0].(map[string]any)["kind"] = "split"
	if admitKeyRepair(k, p, tax) == nil {
		t.Fatal("one-to-one split accepted")
	}
}
func TestReviewKeyScopeNegative(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	u := p["proposed_units"].([]any)[0].(map[string]any)
	u["text_spans"].([]any)[0].(map[string]any)["span"].(map[string]any)["exact_text"] = "invented recording"
	if admitKeyRepair(k, p, tax) == nil {
		t.Fatal("rewritten recording accepted")
	}
}
func TestReviewKeyPopulationPositive(t *testing.T) {
	k, p, _ := reviewKeyFixture(t)
	u := k["units"].([]any)[0].(map[string]any)
	u["difficulty"] = "hard"
	u["difficulty_evidence_ref"] = "actual-population"
	p["proposed_units"].([]any)[0].(map[string]any)["rationale"] = "An improved optional explanation."
	x, e := projectReviewKey(k, p, "review", allocateReviewID)
	if e != nil {
		t.Fatal(e)
	}
	v := x.Key["units"].([]any)[0].(map[string]any)
	if v["difficulty"] != "hard" || v["difficulty_evidence_ref"] != "actual-population" {
		t.Fatal(v)
	}
}
func TestReviewUnknownCategoryNegative(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	p["proposed_units"].([]any)[0].(map[string]any)["primary_taxonomy_id"] = "invented.category"
	if admitKeyRepair(k, p, tax) == nil {
		t.Fatal("new category invented")
	}
}
func reviewOutputFixture(t *testing.T) (ReviewRun, ReviewFrozen, map[string]any) {
	k, _, tax := reviewKeyFixture(t)
	u := k["units"].([]any)[0].(map[string]any)
	return ReviewRun{Purpose: "case_review"}, ReviewFrozen{Key: k, Resources: InterpretationResources{Key: k, TaxonomyIDs: tax, Evidence: []any{}}}, map[string]any{"schema_version": "2.0.0", "resolution": "supported", "unit_judgments": []any{map[string]any{"unit_id": u["id"], "taxonomy_id": u["primary_taxonomy_id"], "judgment": "true_error", "confirmation": "inferred", "evidence_ids": []any{}, "reason": "Supported by the supplied text."}}, "decisions": nil, "issues": []any{}, "reason": "The key is supported.", "key_repair": nil}
}
func TestReviewSupportedPositive(t *testing.T) {
	r, f, o := reviewOutputFixture(t)
	if _, e := admitReview(reviewBytes(o), r, f); e != nil {
		t.Fatal(e)
	}
}
func TestReviewCaseMappingNegative(t *testing.T) {
	r, f, o := reviewOutputFixture(t)
	o["resolution"] = "mapping_defect"
	if _, e := admitReview(reviewBytes(o), r, f); e == nil {
		t.Fatal("case-only mapping fabricated")
	}
}
func TestReviewUnknownAcousticPositive(t *testing.T) {
	r, f, o := reviewOutputFixture(t)
	f.Key["units"].([]any)[0].(map[string]any)["realization"].(map[string]any)["mode"] = "phonemic"
	o["unit_judgments"].([]any)[0].(map[string]any)["confirmation"] = "unknown"
	if _, e := admitReview(reviewBytes(o), r, f); e != nil {
		t.Fatal(e)
	}
}
func TestReviewInventedAcousticNegative(t *testing.T) {
	r, f, o := reviewOutputFixture(t)
	f.Key["units"].([]any)[0].(map[string]any)["realization"].(map[string]any)["mode"] = "phonemic"
	o["unit_judgments"].([]any)[0].(map[string]any)["confirmation"] = "supported"
	if _, e := admitReview(reviewBytes(o), r, f); e == nil {
		t.Fatal("unobserved acoustic fact accepted")
	}
}
func TestReviewInsufficientPositive(t *testing.T) {
	r, f, o := reviewOutputFixture(t)
	o["resolution"] = "insufficient_evidence"
	if _, e := admitReview(reviewBytes(o), r, f); e != nil {
		t.Fatal(e)
	}
}
func TestReviewMissingUnitNegative(t *testing.T) {
	r, f, o := reviewOutputFixture(t)
	o["unit_judgments"] = []any{}
	if _, e := admitReview(reviewBytes(o), r, f); e == nil {
		t.Fatal("planned control/error omitted")
	}
}
func TestReviewAbsentNullPositive(t *testing.T) {
	value := normalizeReviewShape(map[string]any{"resolution": "supported"}, nil).(map[string]any)
	if v, ok := value["key_repair"]; !ok || v != nil {
		t.Fatal(value)
	}
}
func TestReviewPartialRepairNegative(t *testing.T) {
	r, f, o := reviewOutputFixture(t)
	o["resolution"] = "key_defect"
	if _, e := admitReview(reviewBytes(o), r, f); e == nil {
		t.Fatal("free-form reason became a key")
	}
}
func TestReviewProjectionNoSecretsPositive(t *testing.T) {
	r := ReviewRun{ID: "r1", Frozen: "private-config", Stages: []InterpretationStage{{Result: LLMResult{BindingID: "private-binding"}}}}
	v := reviewView(r, nil)
	if strings.Contains(string(reviewBytes(v)), "private-") {
		t.Fatal(v)
	}
}
func TestReviewUnpublishedRevisionNegative(t *testing.T) {
	v := reviewView(ReviewRun{Status: "failed", NewCase: "unpublished-key", NewResult: "unpublished-result"}, nil)
	if v["new_case_version_id"] != "" || v["new_result_id"] != "" {
		t.Fatal(v)
	}
}

func TestReviewCaseInputPositive(t *testing.T) {
	r, f, _ := reviewOutputFixture(t)
	entry := map[string]any{"id": "grammar.verbs.subject_verb_agreement", "label": "Agreement", "definition": "Subject and verb agreement."}
	other := map[string]any{"id": "grammar.articles.usage", "label": "Articles", "definition": "Article usage."}
	f.Taxonomy = map[string]any{"taxonomy_sha256": strings.Repeat("a", 64), "entries": []any{entry, other}}
	f.Resources.Taxonomy = []any{entry, other}
	input, parts := reviewInput(r, f)
	if len(input["taxonomy_context"].(map[string]any)["entries"].([]any)) != 1 || len(parts["taxonomy"].(map[string]any)["registered_catalog"].([]any)) != 2 {
		t.Fatal("lost selected rules or full catalogue", input, parts)
	}
	if input["purpose"] != "case_review" || input["candidate"] == nil || input["answer"] != nil || input["extraction"] != nil || input["prior_decisions"] != nil || parts["canonical_script"] == nil {
		t.Fatal(input)
	}
}
func TestReviewSplitPositive(t *testing.T) {
	k, p, tax := reviewKeyFixture(t)
	first := p["proposed_units"].([]any)[0].(map[string]any)
	second := reviewClone(first)
	second["id"] = "new:second"
	p["proposed_units"] = append(p["proposed_units"].([]any), second)
	p["affected_components"] = []any{"key", "detection"}
	p["correspondence_relations"] = []any{map[string]any{"old_unit_ids": []any{first["id"]}, "new_unit_ids": []any{first["id"], "new:second"}, "kind": "split", "reason": "Two separately scored obligations."}}
	if e := admitKeyRepair(k, p, tax); e != nil {
		t.Fatal(e)
	}
}

func TestReviewDecisionContainerPositive(t *testing.T) {
	row := map[string]any{"claim_id": "actual-claim", "decision": "ignore"}
	for _, value := range []any{[]any{row}, row, map[string]any{"decisions": []any{row}}} {
		out := normalizeReviewShape(map[string]any{"resolution": "supported", "decisions": value}, nil).(map[string]any)
		d := out["decisions"].(map[string]any)
		if d["schema_version"] != "1.0.0" || d["decisions"].([]any)[0].(map[string]any)["claim_id"] != "actual-claim" {
			t.Fatal(out)
		}
	}
}
func TestReviewMissingDecisionMeaningNegative(t *testing.T) {
	out := normalizeReviewShape(map[string]any{"resolution": "mapping_defect", "decisions": nil}, nil).(map[string]any)
	if out["decisions"] != nil {
		t.Fatal("invented semantic decision")
	}
}

func TestReviewSourcePositive(t *testing.T) {
	k, p, _ := reviewKeyFixture(t)
	source := k["units"].([]any)[0].(map[string]any)["source"].(map[string]any)
	source["source_id"] = "CONSTRUCTED-NATIVE-SOURCE"
	source["source_record_id"] = "record-42"
	source["rights_approval_id"] = "retained-permission"
	source["licence_evidence_hash"] = strings.Repeat("e", 64)
	u := reviewClone(p["proposed_units"].([]any)[0])
	u["id"] = "new:event"
	p["proposed_units"] = append(p["proposed_units"].([]any), u)
	out, e := projectReviewKey(k, p, "review", allocateReviewID)
	if e != nil || !reflect.DeepEqual(out.Key["units"].([]any)[1].(map[string]any)["source"], source) {
		t.Fatal("native source/terms lost", out, e)
	}
}
func TestReviewSourceNegative(t *testing.T) {
	k, p, _ := reviewKeyFixture(t)
	u := reviewClone(p["proposed_units"].([]any)[0])
	u["id"] = "new:event"
	u["source"] = map[string]any{"source_id": "invented-permission"}
	p["proposed_units"] = append(p["proposed_units"].([]any), u)
	out, e := projectReviewKey(k, p, "review", allocateReviewID)
	if e != nil {
		t.Fatal(e)
	}
	if out.Key["units"].([]any)[1].(map[string]any)["source"].(map[string]any)["source_id"] == "invented-permission" {
		t.Fatal("proposal fabricated source authority")
	}
}
