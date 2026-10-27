package app

import (
	"fmt"
	"math/big"
	"tangerine.local/api/internal/source"
)

func observedDuration(media supplementMedia) *big.Rat {
	a, aok := new(big.Rat).SetString(fmt.Sprint(media.Member.Media["sample_count"]))
	b, bok := new(big.Rat).SetString(fmt.Sprint(media.Member.Media["sample_rate_hz"]))
	if !aok || !bok || b.Sign() <= 0 {
		return nil
	}
	return a.Quo(a, b)
}

func sourceDRALProjection(m *source.Mapped, run SourceRun, c supplementContext, e map[string]any) bool {
	fields := source.NativeCSV(m.Raw)
	id := fields["id"]
	kind := ""
	switch m.Table {
	case "sp_dral_conversation":
		kind = "recordings"
	case "sp_dral_fragments_short":
		kind = "fragments-short"
	case "sp_dral_fragments_long":
		kind = "fragments-long"
	default:
		return false
	}
	if id == "" {
		return false
	}
	conversation := fields["conv_id"]
	if conversation == "" {
		conversation = id
	}
	partner := fields["trans_id"]
	conversationPartner := ""
	conversations := c.csv["sp_dral_conversation"][conversation]
	if len(conversations) == 1 {
		conversationPartner = source.NativeCSV(conversations[0])["trans_id"]
	}
	speakers := []string{}
	for _, key := range []string{"participant_id", "participant_id_left", "participant_id_right"} {
		if fields[key] != "" {
			speakers = append(speakers, fields[key])
		}
	}
	e["kind"], e["native_id"], e["session"], e["text_origin"] = kind, id, conversation, "not_supplied"
	e["speakers"] = speakers
	e["native_fields"] = fields
	e["language"] = fields["lang_code"]
	e["source_role"] = fields["original_or_reenacted"]
	e["translation_partner_id"] = partner
	e["source_terms"] = "CC0"
	if media, ok := c.media[kind+"/"+partner+".wav"]; ok {
		e["translation_partner_media"] = mediaView(media)
	}
	e["group_ids"] = []string{source.StableID("dral-native-view", kind, id), pairGroup("dral-view-translation", kind+"/"+id, kind+"/"+partner), pairGroup("dral-conversation-family", conversation, conversationPartner)}
	e["group_method"] = "native_conversation_translation_and_versioned_view_ids_not_independent_populations"
	e["participant_fields_version"] = run.Frozen.Release.Release
	participants := []map[string]any{}
	for _, speaker := range speakers {
		for _, row := range c.csv["sp_dral_participant"][speaker] {
			participants = append(participants, map[string]any{"member": row["member"], "line_index": row["row"], "native_fields": source.NativeCSV(row)})
		}
	}
	e["participant_metadata"] = participants
	if kind != "recordings" {
		e["source_clock"] = source.SourceClock(fields["time_start"], fields["time_end"])
	}
	if media, ok := c.media[kind+"/"+id+".wav"]; ok {
		e["media"] = mediaView(media)
		if duration := observedDuration(media); duration != nil {
			e["local_clock"] = source.SourceClock("0", duration.RatString())
			if kind == "recordings" {
				e["source_clock"] = e["local_clock"]
			}
		}
		if media.Release != run.Report.Release {
			e["base_release_dependency"] = media.Release
		}
	} else {
		e["media_state"] = "not_present_in_selected_release_or_compatible_base"
		// Some acquired metadata supplies a fragment window without a separate
		// fragment file. Use the actual complete recording and its clock; do not
		// manufacture a clip or pretend that its local clock begins at zero.
		if recording, ok := c.media["recordings/"+conversation+".wav"]; ok && kind != "recordings" {
			start, end := source.SourceSeconds(fields["time_start"]), source.SourceSeconds(fields["time_end"])
			length := observedDuration(recording)
			if start != nil && end != nil && length != nil && start.Cmp(end) < 0 && end.Cmp(length) <= 0 {
				e["media"] = mediaView(recording)
				e["local_clock"] = e["source_clock"]
				e["media_representation"] = "native_recording_window"
				e["native_fragment_file"] = "not_supplied_in_selected_assets"
				e["media_state"] = "source_recording_available"
				if recording.Release != run.Report.Release {
					e["base_release_dependency"] = recording.Release
				}
			}
		}
	}
	setTable := "sp_dral_fragments_short_sets"
	if kind == "fragments-long" {
		setTable = "sp_dral_fragments_long_sets"
	}
	sets := c.csv[setTable][id]
	if len(sets) == 1 {
		e["native_partition"] = source.NativeCSV(sets[0])["set"]
	}
	return true
}
