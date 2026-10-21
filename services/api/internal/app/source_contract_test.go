package app

import (
	"context"
	"encoding/json"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
	"testing"
)

func TestSourceProgressPositive(t *testing.T) {
	r := SourceReport{Observed: "4", Accepted: "0", Quarantined: "4", Rejected: "0", RawOnly: "0"}
	for _, state := range []string{"mapped", "metadata", "unmapped", "quarantined"} {
		sourceAdvanceCounts(&r, state)
	}
	if r.Observed != "4" || r.Accepted != "3" || r.Quarantined != "1" || r.RawOnly != "1" || r.Rejected != "0" {
		t.Fatalf("wrong literal progress%+v", r)
	}
}
func TestSourceProgressNegative(t *testing.T) {
	r := SourceReport{Observed: "1", Accepted: "0", Quarantined: "1", Rejected: "0", RawOnly: "0"}
	sourceAdvanceCounts(&r, "quarantined")
	if r.Accepted != "0" || r.Quarantined != "1" || r.RawOnly != "0" {
		t.Fatal("unavailable native row became accepted")
	}
}
func TestSourceGoldIdentityPositive(t *testing.T) {
	a := map[string]any{"case_version_id": "old", "case_sha256": "old-local-envelope", "audio": map[string]any{"sha256": "same-bytes", "asset_id": "asset-a"}, "speakers": []any{map[string]any{"id": "speaker-a"}}, "utterances": []any{map[string]any{"id": "u1", "speaker_id": "speaker-a", "text": "A café opens."}}, "units": []any{map[string]any{"id": "unit-a", "utterance_ids": []any{"u1"}, "primary_taxonomy_id": "grammar.verb_agreement", "rationale": "Same rule"}}}
	var b map[string]any
	_ = json.Unmarshal(sourceBytes(a), &b)
	b["case_version_id"] = "new"
	b["case_sha256"] = "new-local-envelope"
	b["audio"].(map[string]any)["asset_id"] = "asset-b"
	b["speakers"].([]any)[0].(map[string]any)["id"] = "speaker-b"
	u := b["utterances"].([]any)[0].(map[string]any)
	u["id"] = "u2"
	u["speaker_id"] = "speaker-b"
	unit := b["units"].([]any)[0].(map[string]any)
	unit["id"] = "unit-b"
	unit["utterance_ids"] = []any{"u2"}
	if sourceGoldCondition(a) != sourceGoldCondition(b) {
		t.Fatal("ID aliases counted as independent gold stimuli")
	}
	if len(taxonomyCoverageIDs()) != 122 {
		t.Fatal("coverage catalogue incomplete")
	}
}
func TestSourceGoldIdentityNegative(t *testing.T) {
	if _, e := sourceGoldAdmission(map[string]any{"pair_id": "fake", "pair_role": "positive", "split": "dev", "label_origin": "human_guessed", "group_ids": []any{"g"}}); e == nil {
		t.Fatal("missing key accepted as gold")
	}
	a := map[string]any{"public_context": "One individual", "units": []any{map[string]any{"rationale": "singular"}}}
	b := map[string]any{"public_context": "Many people", "units": []any{map[string]any{"rationale": "plural"}}}
	if sourceGoldCondition(a) == sourceGoldCondition(b) {
		t.Fatal("different contextual key conditions merged")
	}
}
func TestSourceCorpusPositive(t *testing.T) {
	r := SourceRun{Report: SourceReport{Release: "r"}, Frozen: SourceFrozen{Release: SourceRelease{Source: "FCE-2.1", Origin: "actual://source"}}}
	m := source.Mapped{ID: "record1", Member: "train.m2"}
	member := source.Member{SHA: strings.Repeat("a", 64), AssetID: "source-bytes"}
	lic := map[string]any{"source_id": "FCE-2.1", "source_record_id": nil, "rights_approval_id": nil, "uses": []string{}, "status": "pending", "licence_evidence_hash": nil}
	c, e := sourceCorpus(r, m, member, map[string]any{"text": "Native text"}, lic)
	if e != nil {
		t.Fatal(e)
	}
	if c["schema_version"] != "1.0.0" {
		t.Fatal("changed preserved corpus version")
	}
	if _, _, e = contracts.Validate("corpus-record", "1.0.0", sourceBytes(c)); e != nil {
		t.Fatal(e)
	}
}
func TestSourceCorpusNegative(t *testing.T) {
	r := SourceRun{Report: SourceReport{Release: "r"}, Frozen: SourceFrozen{Release: SourceRelease{Source: "FCE-2.1", Origin: "actual://source"}}}
	if _, e := sourceCorpus(r, source.Mapped{ID: "record1"}, source.Member{}, map[string]any{"origin": "invented_direct_hearing"}, map[string]any{}); e == nil {
		t.Fatal("invented corpus source admitted")
	}
}

func TestSourceParserDispositionPositive(t *testing.T) {
	row := source.Row{"member": "a.csv", "header": []string{"id", "response"}, "cells": []string{"one", "Actual text"}}
	binding := map[string]any{"fields": []any{map[string]any{"source_path": "response", "target_field": "text", "conversion": "identity", "required": true, "null_values": []any{}}}}
	m := source.LegacyRecord("NIR-DATA", "r", "a.csv", "records", 0, row, binding)
	if m.Status != "mapped" {
		t.Fatal("valid native mapping withheld")
	}
}
func TestSourceParserDispositionNegative(t *testing.T) {
	row := source.Row{"member": "a.csv", "invalid": true, "header": []string{"id", "response"}, "cells": []string{"one", "Actual text", "unbound-extra"}}
	binding := map[string]any{"fields": []any{map[string]any{"source_path": "response", "target_field": "text", "conversion": "identity", "required": true, "null_values": []any{}}}}
	m := source.LegacyRecord("NIR-DATA", "r", "a.csv", "records", 0, row, binding)
	if m.Status != "quarantined" {
		t.Fatal("mapping promoted a rejected native-format row")
	}
}

func TestSourceGoldAdmissionPositive(t *testing.T) {
	key, _, _ := reviewKeyFixture(t)
	key["variety_policy"] = map[string]any{"target_locale": "en-US", "accepted_varieties": []any{"en-US"}, "register": "neutral", "assessment_basis": "explicit_target_form", "public_constraints": "Judge the supplied public language context."}

	gold := map[string]any{"ground_truth": key, "pair_id": "pair1", "pair_role": "positive", "split": "dev", "label_origin": "source_import", "group_ids": []any{"genuine1"}}
	if _, e := sourceGoldAdmission(gold); e != nil {
		t.Fatal(e)
	}
}
func TestSourceGoldAdmissionNegative(t *testing.T) {
	key, _, _ := reviewKeyFixture(t)
	key["variety_policy"] = map[string]any{"target_locale": "en-US", "accepted_varieties": []any{"en-US"}, "register": "neutral", "assessment_basis": "explicit_target_form", "public_constraints": "Judge the supplied public language context."}

	key["schema_version"] = "1.0.0"
	gold := map[string]any{"ground_truth": key, "pair_id": "pair1", "pair_role": "positive", "split": "dev", "label_origin": "source_import", "group_ids": []any{"genuine1"}}
	if _, e := sourceGoldAdmission(gold); e == nil {
		t.Fatal("unadmitted key version became gold")
	}
}
func TestSourceAcousticBoundsPositive(t *testing.T) { sourceAcousticBounds(t, "0.5", false) }
func TestSourceAcousticBoundsNegative(t *testing.T) { sourceAcousticBounds(t, "0.5001", true) }
func sourceAcousticBounds(t *testing.T, end string, bad bool) {
	m := source.BaseProjection("L2-ARCTIC", "r", "ABA/annotation/a.TextGrid", "intervals", 0, source.Row{"tier": "phones", "start_seconds": "0", "end_seconds": end, "label": "T,D,s"})
	member := source.Member{Path: "ABA/wav/a.wav", AssetID: "actual-wave", Media: map[string]any{"sample_rate_hz": 44100, "sample_count": 22050, "channels": 1}}
	s := &Storage{}
	r := SourceRun{Frozen: SourceFrozen{Release: SourceRelease{Source: "L2-ARCTIC"}}}
	if e := s.enrichNative(context.Background(), r, &m, map[string]source.Member{member.Path: member}); e != nil {
		t.Fatal(e)
	}
	if (m.Status == "quarantined") != bad {
		t.Fatalf("wrong actual media bound disposition%+v", m)
	}
}
