package app

import (
	"context"
	"fmt"
	"path"
	"tangerine.local/api/internal/source"
)

type jflegLine struct {
	member  string
	ordinal int64
}
type jflegContext map[jflegLine]source.Row

// The complete staging phase precedes projection. Load parallel references once
// per import/resume, not once per sentence or on ordinary saved-data reads.
func (s *Storage) sourceJFLEGContext(ctx context.Context, run SourceRun) (jflegContext, error) {
	out := jflegContext{}
	if !run.Frozen.Native || run.Frozen.Release.Source != "JFLEG" {
		return out, nil
	}
	rows, e := s.DB.Query(ctx, "SELECT member,ordinal,native_row FROM source_row WHERE import_id=$1 AND table_name IN ('jfleg_ref0','jfleg_ref1','jfleg_ref2','jfleg_ref3','jfleg_spellchecked') ORDER BY member,ordinal", run.Report.ID)
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	for rows.Next() {
		var key jflegLine
		var raw []byte
		if e = rows.Scan(&key.member, &key.ordinal, &raw); e != nil {
			return nil, e
		}
		var row source.Row
		if e = source.Decode(raw, &row); e != nil {
			return nil, e
		}
		out[key] = row
	}
	return out, rows.Err()
}
func jflegText(row source.Row, member source.Member, ordinal int64, origin string) source.SourceText {
	text, _ := row["text"].(string)
	ending, _ := row["line_ending"].(string)
	return source.SourceText{Text: text, Member: member.Path, AssetID: member.AssetID, SHA: member.SHA, LineIndex: ordinal, LineEnding: ending, Origin: origin}
}
func sourceJFLEGProjection(m *source.Mapped, run SourceRun, members map[string]source.Member, parallel jflegContext) {
	raw := m.Value["raw_metadata"].(map[string]any)
	if m.Table != "jfleg_source" {
		raw["annotation_origin"] = source.JFLEGExperimentalOrigin(m.Member)
		if raw["annotation_origin"] == "source_tool_derivation" && (m.Table == "sentences" || m.Table == "edits") {
			// The owner's experimental M2 conversion is retained as metadata, not
			// admitted as an authoritative alignment of the original/ref files.
			raw["tool_annotation_usable_as_gold"] = false
			m.Status = "metadata"
			for i := range m.Issues {
				m.Issues[i].Code = "source_tool_annotation"
				m.Issues[i].Detail = "Experimental M2 tool annotation retained; source token bounds are not usable as gold"
			}
		}
		if _, table, ok := source.JFLEGFile(m.Member); ok {
			raw["annotation_origin"] = "source_annotation"
			if table == "jfleg_spellchecked" {
				raw["annotation_origin"] = "source_tool_derivation"
			}
		}
		raw["project_taxonomy_mapping"] = "not_supplied"
		return
	}
	partition, _, _ := source.JFLEGFile(m.Member)
	original := jflegText(m.Raw, members[m.Member], int64(m.Ordinal), "source_original")
	refs := []source.CorrectionReference{}
	for i := 0; i < 4; i++ {
		name := path.Join(path.Dir(m.Member), fmt.Sprintf("%s.ref%d", partition, i))
		if row, ok := parallel[jflegLine{name, int64(m.Ordinal)}]; ok {
			refs = append(refs, source.CorrectionReference{ID: fmt.Sprintf("ref%d", i), SourceText: jflegText(row, members[name], int64(m.Ordinal), "source_annotation")})
		}
	}
	var spellchecked *source.SourceText
	name := path.Join(path.Dir(m.Member), partition+".spellchecked.src")
	if row, ok := parallel[jflegLine{name, int64(m.Ordinal)}]; ok {
		text := jflegText(row, members[name], int64(m.Ordinal), "source_tool_derivation")
		spellchecked = &text
	}
	example := source.NewCorrectionExample(run.Frozen.Release.Release, m.ID, partition, int64(m.Ordinal), original, refs, spellchecked)
	raw["annotation_origin"] = "source_original_with_native_correction_references"
	raw["alternative_references_are_not_simultaneous_mutations"] = true
	raw["project_taxonomy_mapping"] = "not_supplied"
	m.Value["written_correction_example"] = example
	if cp, ok := m.Value["corpus_record"].(map[string]any); ok {
		cp["group_ids"] = []string{example.Group}
	}
}
