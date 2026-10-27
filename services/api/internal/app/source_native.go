package app

import (
	"context"
	"fmt"
	"math/big"
	"path"
	"strings"
	"tangerine.local/api/internal/source"
)

func (s *Storage) sourceKeyRows(ctx context.Context, id, table, key string) ([]source.Row, error) {
	rows, e := s.DB.Query(ctx, "SELECT native_row FROM source_row WHERE import_id=$1 AND table_name=$2 AND join_key=$3 ORDER BY member,ordinal", id, table, key)
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	out := []source.Row{}
	for rows.Next() {
		var raw []byte
		if e = rows.Scan(&raw); e != nil {
			return nil, e
		}
		var r source.Row
		if e = source.Decode(raw, &r); e != nil {
			return nil, e
		}
		out = append(out, r)
	}
	return out, rows.Err()
}
func (s *Storage) enrichNative(ctx context.Context, run SourceRun, m *source.Mapped, members map[string]source.Member) error {
	fail := func(code, detail string) {
		m.Status = "quarantined"
		m.Issues = append(m.Issues, source.Issue{Locator: m.Member + ":" + fmt.Sprint(m.Ordinal), Code: code, Detail: detail})
	}
	raw := m.Value["raw_metadata"].(map[string]any)
	switch run.Frozen.Release.Source {
	case "WILOCNESS-2.1", "FCE-2.1":
		if m.Table == "sentences" {
			raw["corrected_views"] = source.CorrectionViews(m.Raw)
		}
	case "SPEECHOCEAN762":
		if m.Table != "scores.json" {
			if m.Table == "text" {
				key, _ := m.Raw["key"].(string)
				rows, e := s.sourceKeyRows(ctx, run.Report.ID, "scores.json", key)
				if e != nil {
					return e
				}
				if len(rows) != 1 {
					fail("missing_score", "Selected text has no unambiguous native aggregate score")
				}
			}
			return nil
		}
		key, _ := m.Raw["key"].(string)
		linked := map[string]source.Row{}
		for _, table := range []string{"text", "utt2spk", "wav.scp", "scores-detail.json"} {
			rows, e := s.sourceKeyRows(ctx, run.Report.ID, table, key)
			if e != nil {
				return e
			}
			if len(rows) != 1 {
				fail("speechocean_join", table+" missing, duplicate or cross-split alias")
				continue
			}
			linked[table] = rows[0]
			raw[table] = rows[0]
		}
		if detail := linked["scores-detail.json"]; detail != nil {
			v, ok := detail["value"].(map[string]any)
			if !ok {
				fail("speechocean_detail", "Native five-rater value is not an object")
			} else {
				for _, dimension := range []string{"accuracy", "fluency", "prosodic", "completeness", "total"} {
					values, ok := v[dimension].([]any)
					if !ok || len(values) != 5 {
						fail("speechocean_raters", dimension+" does not retain five native ratings")
					}
				}
			}
		}
		cp, _ := m.Value["corpus_record"].(map[string]any)
		if utt := linked["utt2spk"]; utt != nil && cp != nil {
			speaker, _ := utt["value"].(string)
			if speaker != "" {
				cp["speaker_id"] = speaker
				cp["group_ids"] = []string{source.StableID("speechocean-speaker", speaker)}
				for _, table := range []string{"spk2age", "spk2gender", "spk2utt"} {
					rows, e := s.sourceKeyRows(ctx, run.Report.ID, table, speaker)
					if e != nil {
						return e
					}
					raw[table] = rows
					if table == "spk2utt" && len(rows) > 0 {
						found := false
						for _, row := range rows {
							for _, id := range strings.Fields(fmt.Sprint(row["value"])) {
								found = found || id == key
							}
						}
						if !found {
							fail("speaker_membership", "Native spk2utt does not contain the selected utterance")
						}
					}
					if table == "spk2age" && len(rows) == 1 {
						age, _ := rows[0]["value"].(string)
						switch age {
						case "child":
							cp["age_group"] = "child"
						case "adult":
							cp["age_group"] = "adult"
						}
					}
				}
			}
		}
		if wav := linked["wav.scp"]; wav != nil {
			locator, _ := wav["value"].(string)
			member, _ := wav["member"].(string)
			if _, e := source.SafePath(locator); e != nil || strings.ContainsAny(locator, "|\n\r") {
				fail("unsafe_audio_locator", "Native locator remains inert; supply a documented relocation")
			} else {
				root := path.Dir(path.Dir(member))
				name := path.Join(root, locator)
				if asset, ok := members[name]; ok {
					raw["audio_member"] = name
					raw["audio_asset_id"] = asset.AssetID
					raw["source_clock_hz"] = asset.Media["sample_rate_hz"]
					if fmt.Sprint(asset.Media["sample_rate_hz"]) != "16000" || fmt.Sprint(asset.Media["channels"]) != "1" {
						fail("source_audio_clock", "Actual accepted WAVE does not match source16kHz mono")
					}
				} else {
					fail("missing_audio", name)
				}
			}
		}
	case "L2-ARCTIC":
		origin := "source_unknown"
		if strings.Contains(strings.ToLower(m.Member), "/annotation/") {
			origin = "source_manual"
		}
		if strings.Contains(strings.ToLower(m.Member), "/textgrid/") {
			origin = "source_automatic_alignment"
		}
		raw["annotation_origin"] = origin
		raw["documented_source_clock_hz"] = 44100
		if m.Table == "intervals" || m.Table == "points" {
			_, stem := source.L2Identity(m.Member)
			wav := path.Join(path.Dir(path.Dir(m.Member)), "wav", stem+".wav")
			if asset, ok := members[wav]; ok {
				raw["audio_asset_id"] = asset.AssetID
				raw["source_clock_hz"] = asset.Media["sample_rate_hz"]
				end, valid := new(big.Rat).SetString(fmt.Sprint(m.Raw["end_seconds"]))
				frames, fok := new(big.Rat).SetString(fmt.Sprint(asset.Media["sample_count"]))
				rate, rok := new(big.Rat).SetString(fmt.Sprint(asset.Media["sample_rate_hz"]))
				within, serialized := sourceWaveEnd(end, frames, rate)
				if !valid || !fok || !rok || rate.Sign() <= 0 {
					fail("source_audio_bounds", "Native interval or source media clock cannot be interpreted")
				} else if !within && run.Report.ParserVersion != source.L2ParserVersion {
					fail("source_audio_bounds", "Native interval extends beyond the actual accepted source recording")
				} else if !within {
					// Both native clocks are valid data. A source annotation may
					// have a different extent from the supplied recording; retain
					// that uncertainty without inventing resampling or retiming it.
					raw["clock_bound_relation"] = "native_extent_exceeds_media"
					raw["clock_alignment_status"] = "unverified"
					raw["media_duration_seconds_rational"] = new(big.Rat).Quo(frames, rate).RatString()
					raw["annotation_processing_rate_hz"] = nil
				} else if serialized {
					raw["clock_bound_relation"] = "same_binary64_endpoint"
				}
			} else {
				fail("missing_audio", wav)
			}
		}
		if m.Table == "intervals" && strings.ToLower(fmt.Sprint(m.Raw["tier"])) == "phones" && origin == "source_manual" {
			label, _ := m.Raw["label"].(string)
			parsed, e := source.PhoneLabel(label)
			if e != nil {
				fail("l2_phone_tuple", e.Error())
			} else {
				raw["phone_annotation"] = parsed
			}
		}
		if m.Table == "intervals" || m.Table == "points" {
			// The official v5 README defines words/phones plus ancillary
			// annotator comments. Preserve even an unnamed comment structurally;
			// its text does not establish narrow IPA or a scored phone event.
			switch strings.ToLower(fmt.Sprint(m.Raw["tier"])) {
			case "words":
				raw["tier_role"] = "words"
			case "phones":
				raw["tier_role"] = "phones"
			default:
				raw["tier_role"] = "ancillary_comment"
				raw["linguistic_interpretation"] = nil
			}
			kind, _ := m.Raw["kind"].(string)
			if kind != "interval" && kind != "point" && m.Status != "quarantined" {
				m.Status = "unmapped"
				m.Issues = append(m.Issues, source.Issue{Locator: m.Member, Code: "tier_unbound", Detail: "Undocumented native tier structure retained without guessed meaning"})
			}
		}
		if m.Table == "transcripts" {
			speaker, stem := source.L2Identity(m.Member)
			root := path.Dir(path.Dir(m.Member))
			wav := path.Join(root, "wav", stem+".wav")
			if a, ok := members[wav]; ok {
				raw["audio_member"] = wav
				raw["audio_asset_id"] = a.AssetID
				raw["source_clock_hz"] = a.Media["sample_rate_hz"]
				if fmt.Sprint(a.Media["sample_rate_hz"]) != "44100" || fmt.Sprint(a.Media["channels"]) != "1" {
					fail("source_audio_clock", "Actual accepted WAVE does not match source44.1kHz mono")
				}
			} else {
				fail("missing_audio", wav)
			}
			raw["speaker"] = speaker
			raw["manual_annotation_member"] = nil
			raw["automatic_annotation_member"] = nil
			for _, kind := range []string{"annotation", "textgrid"} {
				name := path.Join(root, kind, stem+".TextGrid")
				if _, ok := members[name]; ok {
					if kind == "annotation" {
						raw["manual_annotation_member"] = name
					} else {
						raw["automatic_annotation_member"] = name
					}
				}
			}
			raw["observed_pronunciation"] = nil
		}
	}
	return nil
}
