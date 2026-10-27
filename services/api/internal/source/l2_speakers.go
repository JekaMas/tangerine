package source

import (
	"strconv"
	"strings"
)

// L2ParserVersion identifies the additive official speaker/tier conversion.
// Previously accepted v1 rows remain trusted under their original provenance.
const L2ParserVersion = "source-native-l2-v5-v2"

// parseL2Speakers reads only the documented official README table. Source gender
// and L1 are declarations, not pronunciation judgments or inferred nationality.
func parseL2Speakers(member, text string) (Native, error) {
	rows := []Row{}
	active := false
	for lineNumber, line := range strings.Split(text, "\n") {
		line = strings.TrimSuffix(line, "\r")
		trim := strings.TrimSpace(line)
		if trim == "|Speaker|Gender|Native Language|# Wav Files|# Annotations|" {
			active = true
			continue
		}
		if !active {
			continue
		}
		if !strings.HasPrefix(trim, "|") {
			break
		}
		cells := strings.Split(strings.Trim(trim, "|"), "|")
		if len(cells) != 5 {
			return Native{}, Failure(member, "l2_speaker_table", "Incomplete documented speaker row")
		}
		for i := range cells {
			cells[i] = strings.TrimSpace(cells[i])
		}
		if strings.HasPrefix(cells[0], "---") || strings.HasPrefix(cells[0], "**Total**") {
			continue
		}
		for _, c := range cells[3:] {
			if n, e := strconv.ParseInt(c, 10, 64); e != nil || n < 0 {
				return Native{}, Failure(member, "l2_speaker_table", "Source speaker count is not a nonnegative integer")
			}
		}
		rows = append(rows, Row{"member": member, "row": lineNumber, "key": cells[0], "speaker": cells[0], "gender": cells[1], "native_language": cells[2], "read_wav_files": cells[3], "read_annotation_files": cells[4], "source_line": line})
	}
	if !active {
		return Native{}, Failure(member, "l2_speaker_table", "Documented speaker table absent; no metadata invented")
	}
	return Native{Tables: []Table{{Name: "speakers", Member: member, Rows: rows}}}, nil
}
