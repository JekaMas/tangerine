package app

import (
	"context"
	"fmt"
	"strings"
	"tangerine.local/api/internal/source"
)

// Full named-source status is stronger than lossless intake or a working parser.
// In particular, three constructed sentences cannot certify a complete BEA bank.
func (s *Storage) sourceFullMissing(ctx context.Context, release SourceRelease, importID string, members []source.Member) ([]string, error) {
	missing := source.MissingNative(release.Source, members)
	requireRows := func(label, table, suffix string, want int64) error {
		var n int64
		e := s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND table_name=$2 AND ($3='' OR member=$3 OR right(member,length($3)+1)='/'||$3)", importID, table, suffix).Scan(&n)
		if e != nil {
			return e
		}
		if n != want {
			missing = append(missing, fmt.Sprintf("%s: expected %d, observed %d", label, want, n))
		}
		return nil
	}
	requireMember := func(label, suffix string) {
		for _, m := range members {
			if strings.HasSuffix(strings.ToLower(m.Path), strings.ToLower(suffix)) {
				return
			}
		}
		missing = append(missing, label)
	}
	switch release.Source {
	case "JFLEG":
		for part, count := range map[string]int64{"dev": 754, "test": 747} {
			for _, pair := range [][2]string{{"jfleg_source", ".src"}, {"jfleg_ref0", ".ref0"}, {"jfleg_ref1", ".ref1"}, {"jfleg_ref2", ".ref2"}, {"jfleg_ref3", ".ref3"}, {"jfleg_spellchecked", ".spellchecked.src"}} {
				if e := requireRows(part+pair[1], pair[0], part+"/"+part+pair[1], count); e != nil {
					return nil, e
				}
			}
		}
		for _, item := range []struct {
			table, suffix string
			count         int64
		}{
			{"sentences", "EACL_exp/m2converter/dev.ref.m2", 754},
			{"edits", "EACL_exp/m2converter/dev.ref.m2", 11611},
			{"sentences", "EACL_exp/m2converter/test.ref.m2", 747},
			{"edits", "EACL_exp/m2converter/test.ref.m2", 10938},
			{"records", "EACL_exp/manual_eval/coded_sentences.csv", 100},
			{"records", "EACL_exp/mturk/pairwise.csv", 1629},
			{"records", "EACL_exp/mturk/sample.csv", 4},
		} {
			label := item.suffix[strings.LastIndex(item.suffix, "/")+1:]
			if item.table != "records" {
				label += " " + item.table
			}
			if e := requireRows(label, item.table, item.suffix, item.count); e != nil {
				return nil, e
			}
		}
	case "FCE-2.1":
		for suffix, count := range map[string]int64{"fce.train.gold.bea19.m2": 28350, "fce.dev.gold.bea19.m2": 2191, "fce.test.gold.bea19.m2": 2695} {
			if e := requireRows(suffix, "sentences", suffix, count); e != nil {
				return nil, e
			}
		}
		for _, suffix := range []string{"fce.train.json", "fce.dev.json", "fce.test.json", "json_to_m2.py", "readme.txt", "licence.txt"} {
			requireMember("native "+suffix, suffix)
		}
	case "WILOCNESS-2.1":
		for suffix, count := range map[string]int64{"A.train.gold.bea19.m2": 10493, "B.train.gold.bea19.m2": 13032, "C.train.gold.bea19.m2": 10783, "ABC.train.gold.bea19.m2": 34308, "A.dev.gold.bea19.m2": 1037, "B.dev.gold.bea19.m2": 1290, "C.dev.gold.bea19.m2": 1069, "N.dev.gold.bea19.m2": 988, "ABCN.dev.gold.bea19.m2": 4384} {
			if e := requireRows(suffix, "sentences", suffix, count); e != nil {
				return nil, e
			}
		}
		if e := requireRows("withheld native test originals", "withheld", "ABCN.test.bea19.orig", 4477); e != nil {
			return nil, e
		}
		for _, suffix := range []string{"A.train.json", "B.train.json", "C.train.json", "A.dev.json", "B.dev.json", "C.dev.json", "N.dev.json", "json_to_m2.py", "licence.wi.txt", "license.locness.txt"} {
			requireMember("native "+suffix, suffix)
		}
	case "SPEECHOCEAN762":
		var recordings int
		for _, member := range members {
			if strings.HasSuffix(strings.ToLower(member.Path), ".wav") {
				recordings++
			}
		}
		if recordings != 5245 {
			missing = append(missing, fmt.Sprintf("Complete native WAVE files: expected 5245, observed %d; includes 245 unrated recordings", recordings))
		}
		if e := requireRows("aggregate scored utterances", "scores.json", "", 5000); e != nil {
			return nil, e
		}
		if e := requireRows("five-rater utterances", "scores-detail.json", "", 5000); e != nil {
			return nil, e
		}
		for _, part := range []string{"train", "test"} {
			if e := requireRows(part+" texts", "text", part+"/text", 2500); e != nil {
				return nil, e
			}
		}
		var speakers int64
		if e := s.DB.QueryRow(ctx, "SELECT count(DISTINCT native_row->>'value') FROM source_row WHERE import_id=$1 AND table_name='utt2spk'", importID).Scan(&speakers); e != nil {
			return nil, e
		}
		if speakers != 250 {
			missing = append(missing, fmt.Sprintf("250 native speakers; observed %d", speakers))
		}
	case "L2-ARCTIC":
		var read, suit int64
		if e := s.DB.QueryRow(ctx, "SELECT count(*) FILTER(WHERE lower(member) NOT LIKE '%suitcase%'),count(*) FILTER(WHERE lower(member) LIKE '%suitcase%') FROM source_row WHERE import_id=$1 AND table_name='transcripts'", importID).Scan(&read, &suit); e != nil {
			return nil, e
		}
		if read != 26867 || suit != 22 {
			missing = append(missing, fmt.Sprintf("Complete read/suitcase utterances: expected 26867/22; observed %d/%d", read, suit))
		}
	case "TET-GOLD-1":
		goldMissing, e := s.sourceGoldMissing(ctx, importID, members)
		if e != nil {
			return nil, e
		}
		missing = append(missing, goldMissing...)

	case "EFCAMDAT-R2", "EFCAMDAT-SHATZ2020", "EFCAMDAT-OKSUZ2025", "DOUBAO-STUDY-RECORDS", "MOODRICK-DATA", "NIR-DATA":
		if len(release.Components) == 0 || len(release.Docs) == 0 {
			missing = append(missing, "actual documented complete owner component/population manifest")
		}
	}
	return missing, nil
}
