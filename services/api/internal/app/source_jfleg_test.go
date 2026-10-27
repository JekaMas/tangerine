package app

import (
	"strings"
	"tangerine.local/api/internal/source"
	"testing"
)

func jflegProjectionFixture() (source.Mapped, SourceRun, map[string]source.Member, jflegContext) {
	member := "owner/dev/dev.src"
	m := source.NativeRecord("JFLEG", "release", member, "jfleg_source", 0, source.Row{"row": 0, "text": "There are reason . ", "line_ending": "\n"})
	run := SourceRun{Frozen: SourceFrozen{Release: SourceRelease{Release: "pinned-owner-version"}}}
	members := map[string]source.Member{member: {Path: member, SHA: strings.Repeat("a", 64), AssetID: "original"}}
	return m, run, members, jflegContext{}
}
func TestSourceJFLEGProjectionPositive(t *testing.T) {
	m, run, members, parallel := jflegProjectionFixture()
	for i, ref := range []string{"There are reasons . ", "There are several reasons . ", "There are reasons . ", "There are reason . "} {
		id := "ref" + string(rune('0'+i))
		name := "owner/dev/dev." + id
		members[name] = source.Member{Path: name, SHA: strings.Repeat("b", 64), AssetID: id}
		parallel[jflegLine{name, 0}] = source.Row{"text": ref, "line_ending": "\n"}
	}
	sourceJFLEGProjection(&m, run, members, parallel)
	e := m.Value["written_correction_example"].(source.CorrectionExample)
	if e.ID != "dev:0" || e.Original.Text != "There are reason . " || e.ReferenceCompleteness != "complete" || e.References[1].Text != "There are several reasons . " || e.References[3].AssetID != "ref3" {
		t.Fatalf("native projection %+v", e)
	}
	if e.Original.AssetID != "original" || e.Differences[3].Kind != "unchanged" {
		t.Fatal("original/control provenance lost")
	}
}
func TestSourceJFLEGProjectionNegative(t *testing.T) {
	m, run, members, parallel := jflegProjectionFixture()
	parallel[jflegLine{"owner/test/test.ref0", 0}] = source.Row{"text": "foreign partition"}
	parallel[jflegLine{"owner/dev/dev.ref1", 1}] = source.Row{"text": "foreign line"}
	sourceJFLEGProjection(&m, run, members, parallel)
	e := m.Value["written_correction_example"].(source.CorrectionExample)
	if len(e.References) != 0 || e.ReferenceCompleteness != "partial" || e.Spellchecked != nil {
		t.Fatalf("invented or foreign references %+v", e)
	}
	if m.Raw["text"] != "There are reason . " {
		t.Fatal("source text changed")
	}
}
func TestSourceJFLEGToolAnnotationPositive(t *testing.T) {
	member := "owner/EACL_exp/m2converter/dev.ref.m2"
	m := source.NativeRecord("JFLEG", "release", member, "edits", 0, source.Row{"invalid": true, "start": 13, "end": 13, "label": "#Del#", "raw": "A 13 13|||#Del#|||.|||REQUIRED|||-NONE-|||0"})
	sourceJFLEGProjection(&m, SourceRun{}, nil, nil)
	if m.Status != "metadata" || m.Raw["invalid"] != true || len(m.Issues) != 1 {
		t.Fatal("experimental tool finding was lost or blocked original references", m)
	}
	raw := m.Value["raw_metadata"].(map[string]any)
	if raw["annotation_origin"] != "source_tool_derivation" || raw["tool_annotation_usable_as_gold"] != false || m.Issues[0].Code != "source_tool_annotation" {
		t.Fatal("tool validity misrepresented", raw, m.Issues)
	}
}
func TestSourceJFLEGToolAnnotationNegative(t *testing.T) {
	m, run, members, parallel := jflegProjectionFixture()
	m.Status = "quarantined"
	m.Raw["invalid"] = true
	sourceJFLEGProjection(&m, run, members, parallel)
	if m.Status != "quarantined" {
		t.Fatal("invalid primary source silently accepted")
	}
}
