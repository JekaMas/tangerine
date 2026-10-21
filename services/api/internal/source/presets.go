package source

import (
	"fmt"
	"path"
	"strings"
)

// NativePlan selects documented public representations. Private export headers
// are intentionally absent: their actual supplied binding drives normalization.
func NativePlan(id string, m Member) (Options, string, bool) {
	n := strings.ToLower(m.Path)
	base := strings.ToLower(path.Base(m.Path))
	o := Options{Encoding: "utf-8", Selector: "records"}
	if strings.HasSuffix(n, ".m2") {
		o.Format = "m2"
		return o, "m2", true
	}
	if strings.HasSuffix(n, ".textgrid") {
		o.Format = "textgrid"
		return o, "textgrid", true
	}
	switch id {
	case "SPEECHOCEAN762":
		if base == "scores.json" || base == "scores-detail.json" {
			o.Format = "json"
			o.Selector = "keyed_records"
			return o, base, true
		}
		switch base {
		case "text", "utt2spk", "spk2utt", "wav.scp", "spk2age", "spk2gender", "text-phone", "lexicon.txt":
			o.Format = "kaldi"
			return o, base, true
		}
	case "L2-ARCTIC":
		if strings.Contains(n, "/transcript/") && strings.HasSuffix(n, ".txt") {
			o.Format = "lines"
			return o, "transcripts", true
		}
	case "WILOCNESS-2.1", "FCE-2.1":
		if strings.HasSuffix(n, ".json") {
			o.Format = "jsonl"
			return o, "essays", true
		}
		if strings.HasSuffix(n, ".orig") {
			o.Format = "lines"
			return o, "withheld", true
		}
	case "EFCAMDAT-R2":
		if strings.HasSuffix(n, ".xml") {
			o.Format = "xml"
			o.Selector = "/selection/writings/writing"
			return o, "writings", true
		}
	}
	switch {
	case strings.HasSuffix(n, ".jsonl"), strings.HasSuffix(n, ".ndjson"):
		o.Format = "jsonl"
	case strings.HasSuffix(n, ".json"):
		o.Format = "json"
	case strings.HasSuffix(n, ".csv"):
		o.Format = "csv"
		o.Header = true
	case strings.HasSuffix(n, ".tsv"):
		o.Format = "tsv"
		o.Header = true
	case strings.HasSuffix(n, ".xlsx"):
		o.Format = "xlsx"
	case strings.HasSuffix(n, ".xml"):
		o.Format = "xml"
	default:
		return o, "ancillary", false
	}
	return o, "raw", true
}
func BaseProjection(id, release, member, table string, ordinal int, row Row) Mapped {
	native := any(nil)
	for _, k := range []string{"key", "id", "sentence_index", "row", "index"} {
		if v, ok := row[k]; ok {
			native = v
			break
		}
	}
	return Mapped{ID: StableID(id, release, member, table, fmt.Sprint(native), fmt.Sprint(ordinal)), Member: member, Table: table, Ordinal: ordinal, Identity: native, Raw: row, Value: map[string]any{"raw_metadata": map[string]any{"native": row}}, Status: "unmapped", Issues: []Issue{}}
}
func NativeRecord(id, release, member, table string, ordinal int, row Row) Mapped {
	m := BaseProjection(id, release, member, table, ordinal, row)
	raw := m.Value["raw_metadata"].(map[string]any)
	record := map[string]any{}
	text := ""
	origin := "external_written"
	groups := []string{}
	labels := "labels_not_supplied"
	switch id {
	case "WILOCNESS-2.1", "FCE-2.1":
		if table == "sentences" || table == "withheld" {
			text, _ = row["text"].(string)
			if table == "sentences" {
				labels = "labels_supplied"
			}
			raw["annotations"] = row["edits"]
			raw["alternative_annotators_are_not_simultaneous"] = true
			raw["reconstruction"] = "not_requested"
			raw["representation_group"] = StableID(id, fmt.Sprint(Partition(member)), text)
			raw["group_basis"] = "possible_duplicate_text_not_learner_identity"
		}
		if table == "essays" {
			if v, ok := row["value"].(map[string]any); ok {
				text, _ = v["text"].(string)
				labels = "native_pedagogical_edits"
				raw["annotations"] = v["edits"]
				if id, ok := v["id"].(string); ok {
					groups = append(groups, StableID("native-essay", id))
				}
				if l1, ok := v["l1"].(string); ok {
					record["l1"] = l1
				}
			}
		}
	case "SPEECHOCEAN762":
		if table == "scores.json" {
			if v, ok := row["value"].(map[string]any); ok {
				text, _ = v["text"].(string)
				origin = "external_human_speech"
				labels = "source_scalar_ratings_not_localized_error_gold"
				raw["aggregate_scores"] = v
				record["source_score_scale"] = "SpeechOcean native sentence/word0..10, phone0..2; aggregate completeness0..10, individual0..1"
				raw["scale_definition"] = map[string]any{"sentence": "0..10 native dimensions", "phone_accuracy": "0..2", "word": "0..10", "completeness": "aggregate 0..10; individual 0..1"}
				raw["observed_phone_substitution"] = nil
			}
		}
	case "L2-ARCTIC":
		if table == "transcripts" {
			text, _ = row["text"].(string)
			origin = "external_human_speech"
			speaker, utterance := L2Identity(member)
			record["speaker_id"] = speaker
			groups = append(groups, StableID("l2-speaker", speaker), StableID("cmu-prompt", utterance))
			raw["speaker"] = speaker
			raw["utterance"] = utterance
			labels = "linked_native_annotations"
		}
	case "EFCAMDAT-R2":
		if table == "writings" {
			for _, v := range children(row) {
				name, _ := v["name"].(string)
				if name == "text" {
					text = originalXML(v)
				}
				if name == "learner" {
					for _, a := range attrs(v) {
						if a["name"] == "id" {
							groups = append(groups, StableID("efcamdat-learner", fmt.Sprint(a["value"])))
						}
						if a["name"] == "nationality" {
							raw["nationality"] = a["value"]
							raw["l1"] = nil
						}
					}
				}
			}
			labels = "source_teacher_feedback_not_exhaustive_gold"
			raw["original_projection"] = "xml-mixed-selection-v1"
		}
	}
	if text != "" {
		record["text"] = text
		record["origin"] = origin
		record["group_ids"] = groups
		m.Value["corpus_record"] = record
		raw["labels_state"] = labels
		m.Status = "mapped"
	}
	if row["invalid"] == true || row["ambiguous_keys"] == true {
		m.Status = "quarantined"
		m.Issues = append(m.Issues, Issue{member, "native_invalid", "Native row retained with invalid source annotation"})
	}
	return m
}
func children(r Row) []Row {
	a := []Row{}
	for _, v := range asArray(r["children"]) {
		switch n := v.(type) {
		case Row:
			a = append(a, n)
		case map[string]any:
			a = append(a, Row(n))
		}
	}
	return a
}
func attrs(r Row) []map[string]any {
	a := []map[string]any{}
	for _, v := range asArray(r["attributes"]) {
		if m, ok := v.(map[string]any); ok {
			a = append(a, m)
		}
	}
	return a
}
func asArray(v any) []any { a, _ := v.([]any); return a }
func originalXML(r Row) string {
	s, _ := r["text"].(string)
	for _, v := range children(r) {
		name, _ := v["name"].(string)
		if name == "change" {
			for _, c := range children(v) {
				if c["name"] == "selection" {
					s += originalXML(c)
				}
			}
		} else if name != "tag" && name != "correct" {
			s += originalXML(v)
		}
		tail, _ := v["tail"].(string)
		s += tail
	}
	return s
}
func L2Identity(member string) (string, string) {
	p := strings.Split(member, "/")
	speaker := ""
	for i, v := range p {
		if v == "transcript" || v == "annotation" || v == "textgrid" || v == "wav" {
			if i > 0 {
				speaker = p[i-1]
			}
			break
		}
	}
	stem := strings.TrimSuffix(path.Base(member), path.Ext(member))
	if strings.Contains(strings.ToLower(member), "suitcase") {
		speaker = strings.ToUpper(strings.Split(stem, "_")[0])
	}
	return speaker, stem
}
func PhoneLabel(label string) (map[string]any, error) {
	p := strings.Split(label, ",")
	if len(p) == 1 {
		return map[string]any{"raw": label, "canonical": label, "perceived": label, "operation": "unchanged", "approximate": strings.Contains(label, "*")}, nil
	}
	if len(p) != 3 {
		return nil, fmt.Errorf("malformed L2 phone tuple")
	}
	for i := range p {
		p[i] = strings.TrimSpace(p[i])
	}
	nativeOperation := p[2]
	p[2] = strings.ToLower(p[2])
	if p[0] == "" || p[1] == "" || (p[2] != "s" && p[2] != "d" && p[2] != "a") || p[2] == "d" && !strings.EqualFold(p[1], "sil") || p[2] == "a" && !strings.EqualFold(p[0], "sil") {
		return nil, fmt.Errorf("invalid L2 phone operation")
	}
	var perceived any = p[1]
	if strings.EqualFold(p[1], "err") {
		perceived = nil
	}
	return map[string]any{"raw": label, "canonical": p[0], "perceived": perceived, "operation": p[2], "native_operation": nativeOperation, "approximate": strings.Contains(label, "*")}, nil
}

// Required native components identify missingness, not an approval gate. Private
// dictionaries may add their genuine component set; a public companion never
// changes the identity or completeness of a missing original release.
func MissingNative(id string, members []Member) []string {
	names := []string{}
	for _, m := range members {
		names = append(names, strings.ToLower(m.Path))
	}
	missing := []string{}
	need := func(label string, match func(string) bool) {
		for _, n := range names {
			if match(n) {
				return
			}
		}
		missing = append(missing, label)
	}
	suffix := func(s string) func(string) bool { return func(n string) bool { return strings.HasSuffix(n, s) } }
	switch id {
	case "SPEECHOCEAN762":
		for _, s := range []string{"scores.json", "scores-detail.json", "train/text", "test/text", "train/utt2spk", "test/utt2spk", "train/wav.scp", "test/wav.scp"} {
			need(s, suffix(s))
		}
		need("all selected WAVE", suffix(".wav"))
	case "WILOCNESS-2.1", "FCE-2.1":
		for _, part := range []string{"train", "dev", "test"} {
			part := part
			need(part, func(n string) bool {
				return strings.Contains(n, part) && (strings.HasSuffix(n, ".m2") || strings.HasSuffix(n, ".orig"))
			})
		}
		need("source license", func(n string) bool { return strings.Contains(n, "licen") })
	case "L2-ARCTIC":
		for _, d := range []string{"readme", "license", "prompts", "suitcase"} {
			d := d
			need(d, func(n string) bool { return strings.Contains(n, d) })
		}
		for _, speaker := range []string{"ABA", "ASI", "BWC", "EBVS", "ERMS", "HKK", "NJS", "HQTV", "SKA", "YDCK", "TNI", "PNV", "HJK", "NCC", "MBMPS", "LXC", "TLV", "SVBI", "YBAA", "YKWK", "ZHAA", "RRBI", "THV", "TXHC"} {
			s := strings.ToLower(speaker) + "/"
			need(speaker, func(n string) bool { return strings.Contains(n, s) })
		}
	case "EFCAMDAT-R2":
		need("full XML", suffix(".xml"))
		need("actual source dictionary and use terms", func(n string) bool { return strings.Contains(n, "dictionary") || strings.Contains(n, "guide") })
	case "EFCAMDAT-SHATZ2020", "EFCAMDAT-OKSUZ2025":
		need("complete original workbook", suffix(".xlsx"))
		need("native dictionary", func(n string) bool { return strings.Contains(n, "dictionary") || strings.Contains(n, "glossary") })
	case "DOUBAO-STUDY-RECORDS", "MOODRICK-DATA", "NIR-DATA":
		need("actual native export dictionary", func(n string) bool { return strings.Contains(n, "dictionary") })
		need("actual source use terms", func(n string) bool { return strings.Contains(n, "terms") || strings.Contains(n, "agreement") })
	case "TET-GOLD-1":
		need("original versioned JSONL", suffix(".jsonl"))
		need("content-addressed WAV", suffix(".wav"))
		for _, s := range []string{"dev", "calibration", "holdout"} {
			s := s
			need(s, func(n string) bool { return strings.Contains(n, s) })
		}
	}
	return missing
}
