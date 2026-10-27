package app

import (
	"context"
	"errors"
	"fmt"
	"github.com/jackc/pgx/v5"
	"path"
	"sort"
	"strconv"
	"strings"
	"tangerine.local/api/internal/source"
)

type supplementMedia struct {
	Member  source.Member
	Release string
}
type supplementContext struct {
	lines      map[string]source.Row
	metadata   map[string][]source.Row
	media      map[string]supplementMedia
	nli        map[int64]source.Row
	pir        map[int64]source.Row
	csv        map[string]map[string][]source.Row
	background map[string][]map[string]any
}

func nativeLine(row source.Row) (string, string) {
	line, _ := row["text"].(string)
	i := strings.IndexAny(line, " \t")
	if i < 0 {
		return line, ""
	}
	return line[:i], strings.TrimLeft(line[i+1:], " \t")
}
func mediaView(m supplementMedia) map[string]any {
	return map[string]any{"asset_id": m.Member.AssetID, "member": m.Member.Path, "release_id": m.Release, "sha256": m.Member.SHA, "observed_clock": m.Member.Media}
}
func addSupplementMedia(c *supplementContext, release string, members []source.Member, replace bool) {
	for _, m := range members {
		if !strings.EqualFold(path.Ext(m.Path), ".wav") {
			continue
		}
		key := path.Base(path.Dir(m.Path)) + "/" + path.Base(m.Path)
		c.media[m.Path] = supplementMedia{m, release}
		if _, found := c.media[key]; !found || replace {
			c.media[key] = supplementMedia{m, release}
		}
	}
}

// Resolve actual native metadata once per import/resume. Saved readback never
// reopens source bytes, rederives these relations or checks stored hashes.
func (s *Storage) sourceSupplementContext(ctx context.Context, run SourceRun, members []source.Member) (supplementContext, error) {
	c := supplementContext{lines: map[string]source.Row{}, metadata: map[string][]source.Row{}, media: map[string]supplementMedia{}, nli: map[int64]source.Row{}, pir: map[int64]source.Row{}, csv: map[string]map[string][]source.Row{}, background: map[string][]map[string]any{}}
	if !run.Frozen.Native || !source.SpeechSupplement(run.Frozen.Release.Source) {
		return c, nil
	}
	if run.Frozen.Release.Source == "DRAL" && run.Frozen.Release.Release == "8.0-fixes-plus-testdata" {
		var id string
		e := s.DB.QueryRow(ctx, "SELECT id FROM source_release WHERE source_id='DRAL' AND payload->>'source_version'='16kHz-base' ORDER BY created_at DESC,id DESC LIMIT 1").Scan(&id)
		if e == nil {
			base, err := s.sourceMembers(ctx, id)
			if err != nil {
				return c, err
			}
			addSupplementMedia(&c, id, base, false)
		} else if !errors.Is(e, pgx.ErrNoRows) {
			return c, e
		}
	}
	addSupplementMedia(&c, run.Report.Release, members, true)
	rows, e := s.DB.Query(ctx, "SELECT member,table_name,ordinal,native_row FROM source_row WHERE import_id=$1 AND (table_name IN ('sp_edacc_text','sp_edacc_utt2spk','sp_edacc_background','sp_dral_participant','sp_dral_conversation','sp_dral_fragments_short_sets','sp_dral_fragments_long_sets') OR table_name='sp_diplomat' AND (member LIKE '%/NLI_task_dataset/%' OR member LIKE 'NLI_task_dataset/%' OR member LIKE '%PIR_first_subtask_dataset/test.jsonl')) ORDER BY member,ordinal", run.Report.ID)
	if e != nil {
		return c, e
	}
	defer rows.Close()
	for rows.Next() {
		var member, table string
		var ordinal int64
		var raw []byte
		if e = rows.Scan(&member, &table, &ordinal, &raw); e != nil {
			return c, e
		}
		var row source.Row
		if e = source.Decode(raw, &row); e != nil {
			return c, e
		}
		if table == "sp_edacc_text" || table == "sp_edacc_utt2spk" {
			key, _ := nativeLine(row)
			c.lines[path.Dir(member)+"/"+table+"/"+key] = row
		} else {
			c.metadata[table] = append(c.metadata[table], row)
		}
		if table == "sp_diplomat" {
			if path.Base(path.Dir(member)) == "PIR_first_subtask_dataset" {
				value, _ := row["value"].(map[string]any)
				turns, _ := value["correct_turn_number"].([]any)
				for range turns {
					c.pir[int64(len(c.pir))] = row
				}
			} else {
				c.nli[ordinal] = row
			}
		}
		if strings.HasPrefix(table, "sp_dral_") {
			if c.csv[table] == nil {
				c.csv[table] = map[string][]source.Row{}
			}
			key := source.NativeCSV(row)["id"]
			c.csv[table][key] = append(c.csv[table][key], row)
		}
		if table == "sp_edacc_background" {
			key := source.NativeCSV(row)["CONVERSATION_ID"]
			c.background[key] = append(c.background[key], map[string]any{"member": row["member"], "line_index": row["row"]})
		}
	}
	return c, rows.Err()
}

func pairGroup(kind, a, b string) string {
	values := []string{a, b}
	sort.Strings(values)
	return source.StableID(kind, values[0], values[1])
}
func sourceSupplementProjection(m *source.Mapped, run SourceRun, c supplementContext) {
	raw := m.Value["raw_metadata"].(map[string]any)
	raw["annotation_origin"] = "source_metadata"
	raw["project_taxonomy_mapping"] = "not_supplied"
	m.Status = "metadata"
	if m.Raw["ambiguous_keys"] == true || m.Raw["invalid"] == true {
		raw["native_interpretation"] = "source_fields_unusable_or_ambiguous"
		return
	}
	e := map[string]any{"source_id": run.Frozen.Release.Source, "source_version": run.Frozen.Release.Release, "member": m.Member, "line_index": m.Ordinal, "native_fields": m.Raw, "text": nil, "media": nil, "speakers": []string{}, "source_clock": nil, "local_clock": nil, "independent_population_count": nil, "error_labels": "not_supplied"}
	var text, origin string
	var groups []string
	switch run.Frozen.Release.Source {
	case "EDACC":
		if m.Table != "sp_edacc_segments" {
			if m.Table == "sp_edacc_company_ctm" {
				raw["annotation_origin"] = "source_asr_output"
			} else if m.Table == "sp_edacc_stm_filt" || m.Table == "sp_edacc_glm" {
				raw["annotation_origin"] = "source_scoring_view"
			}
			return
		}
		line, _ := m.Raw["text"].(string)
		fields := strings.Fields(line)
		if len(fields) < 4 {
			return
		}
		id, session := fields[0], fields[1]
		_, text = nativeLine(c.lines[path.Dir(m.Member)+"/sp_edacc_text/"+id])
		_, speaker := nativeLine(c.lines[path.Dir(m.Member)+"/sp_edacc_utt2spk/"+id])
		e["kind"], e["native_id"], e["session"], e["text_origin"] = "source_utterance", id, session, "source_reference_transcription"
		e["speakers"] = []string{speaker}
		e["source_clock"] = source.SourceClock(fields[2], fields[3])
		e["local_clock"] = e["source_clock"]
		e["accent_is_error"] = false
		if media, ok := c.media[path.Join(path.Dir(path.Dir(m.Member)), "data", session+".wav")]; ok {
			e["media"] = mediaView(media)
		}
		background := append([]map[string]any{}, c.background[session]...)
		if bare := strings.TrimPrefix(session, "EDACC-"); bare != session {
			background = append(background, c.background[bare]...)
		}
		e["background_source_locators"] = background
		e["background_participant_binding"] = "not_inferred_from_stm_tags"
		origin = "external_human_speech"
		groups = []string{source.StableID("edacc-session", session), source.StableID("edacc-speaker", speaker)}
	case "ELRD":
		if m.Table != "sp_elrd_turns" {
			return
		}
		v, _ := m.Raw["value"].(map[string]any)
		text, _ = v["transcript"].(string)
		speaker, _ := v["speaker"].(string)
		session := strings.TrimSuffix(path.Base(m.Member), ".jsonl")
		start, _ := v["start"].(string)
		end, _ := v["end"].(string)
		e["kind"], e["native_id"], e["session"], e["text_origin"] = "dialogue_turn", fmt.Sprint(m.Ordinal), session, "source_asr_transcription"
		e["speakers"] = []string{speaker}
		e["source_clock"] = source.SourceClock(start, end)
		e["local_clock"] = e["source_clock"]
		if media, ok := c.media[path.Join(path.Dir(path.Dir(m.Member)), "audios", session+".wav")]; ok {
			e["media"] = mediaView(media)
		}
		e["source_terms"] = map[string]string{"audio": "CC-BY-NC-ND-4.0", "transcript": "CC-BY-4.0"}
		raw["annotation_origin"] = "source_asr_transcription"
		origin = "external_human_speech"
		groups = []string{source.StableID("elrd-dialogue", session), source.StableID("elrd-speaker", speaker)}
	case "DIPLOMAT":
		if m.Table != "sp_diplomat" {
			return
		}
		v, _ := m.Raw["value"].(map[string]any)
		turns := v["text"]
		if turns == nil {
			turns = v["dialogue"]
		}
		if a, ok := turns.([]any); ok {
			parts := []string{}
			for _, part := range a {
				if s, ok := part.(string); ok {
					parts = append(parts, s)
				}
			}
			text = strings.Join(parts, "\n")
		} else {
			text, _ = turns.(string)
		}
		group := source.ContextGroup(turns, v["speaker"])
		e["kind"], e["task"], e["native_id"] = "pragmatic_task", path.Base(path.Dir(m.Member)), fmt.Sprint(m.Ordinal)
		e["text_origin"] = "source_task_context"
		e["native_fields"] = v
		e["speakers"] = v["speaker"]
		e["group_method"] = "exact_context_equivalence_not_global_dialogue_id"
		e["label_namespace"] = "DiPlomat_native_not_Tangerine"
		e["native_partition"] = strings.TrimSuffix(path.Base(m.Member), path.Ext(m.Member))
		if task := path.Base(path.Dir(m.Member)); task == "NLI_task_dataset" || task == "NLI_dataset_without_context" {
			e["native_partition"] = "train"
			e["partition_origin"] = "owner_dataset_builder"
		}
		groups = []string{group}
		origin = "external_written"
		if path.Base(path.Dir(m.Member)) == "PIR_second_subtask_dataset" {
			e["label_meaning"] = "zero_based_correct_choice_index"
			choices, _ := v["choice"].([]any)
			index, err := strconv.Atoi(fmt.Sprint(v["label"]))
			if err == nil && index >= 0 && index < len(choices) {
				e["source_selected_choice"] = choices[index]
			}
			if path.Base(m.Member) == "test.jsonl" {
				if other, ok := c.pir[int64(m.Ordinal)]; ok {
					v2, _ := other["value"].(map[string]any)
					targets, _ := v2["correct_turn_number"].([]any)
					supported := false
					for _, target := range targets {
						if fmt.Sprint(target) == fmt.Sprint(v["correct_turn_number"]) {
							supported = true
						}
					}
					if supported && source.ContextGroup(v2["text"], v2["speaker"]) == group {
						e["derived_view_relation"] = map[string]any{"method": "owner-test-order-expanded-turn-count-supported-context-v1", "context_member": other["member"], "context_line_index": other["row"], "target_turn": v["correct_turn_number"]}
					}
				}
			}
		}
		if path.Base(path.Dir(m.Member)) == "NLI_dataset_without_context" {
			if other, ok := c.nli[int64(m.Ordinal)]; ok {
				v2, _ := other["value"].(map[string]any)
				answer, _ := v2["human answer"].(string)
				hypothesis, _ := v["hypothesis"].(string)
				_, statement, has := strings.Cut(answer, ":")
				supported := false
				if turns, ok := v2["dialogue"].([]any); ok {
					for _, turn := range turns {
						if turn == text {
							supported = true
						}
					}
				}
				if has && supported && strings.TrimSpace(statement) == hypothesis {
					groups = []string{source.ContextGroup(v2["dialogue"], v2["speaker"])}
					e["derived_view_relation"] = map[string]any{"method": "paired-position-supported-content-v1", "context_member": other["member"], "context_line_index": m.Ordinal}
				}
			}
		}
	case "DRAL":
		if !sourceDRALProjection(m, run, c, e) {
			return
		}
		m.Value["source_example"] = e
		return
	default:
		return
	}
	if text != "" {
		e["text"] = text
	}
	e["group_ids"] = groups
	m.Value["source_example"] = e
	if text != "" {
		m.Value["corpus_record"] = map[string]any{"text": text, "origin": origin, "group_ids": groups}
		if run.Frozen.Release.Source == "DIPLOMAT" {
			m.Value["corpus_record"].(map[string]any)["native_partition"] = e["native_partition"]
		}
		m.Status = "mapped"
	}
}
