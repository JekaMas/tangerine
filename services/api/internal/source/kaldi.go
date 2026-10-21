package source

import (
	"bufio"
	"fmt"
	"io"
	"path"
	"strings"
)

func parseKaldi(member, text string) (Native, error) {
	rows := []Row{}
	issues := []Issue{}
	seen := map[string]string{}
	r := bufio.NewReader(strings.NewReader(text))
	line := 0
	for {
		raw, e := r.ReadString('\n')
		line++
		s := strings.TrimSuffix(strings.TrimSuffix(raw, "\n"), "\r")
		if strings.TrimSpace(s) != "" {
			key, rest, ok := strings.Cut(s, " ")
			if !ok {
				key, rest, ok = strings.Cut(s, "\t")
			}
			rest = strings.TrimLeft(rest, " \t")
			row := Row{"member": member, "key": key, "fields": strings.Fields(rest), "value": rest, "raw": s}
			loc := fmt.Sprintf("%s:%d", member, line)
			if !ok || key == "" {
				row["invalid"] = true
				issues = append(issues, Issue{loc, "kaldi_key", "Expected native key and value"})
			}
			if old, ok := seen[key]; ok && old != rest {
				row["invalid"] = true
				issues = append(issues, Issue{loc, "duplicate_key", "Conflicting native key retained"})
			}
			seen[key] = rest
			if path.Base(member) == "utt2spk" && len(strings.Fields(rest)) != 1 {
				row["invalid"] = true
				issues = append(issues, Issue{loc, "utt2spk_cardinality", "Expected one source speaker"})
			}
			rows = append(rows, row)
		}
		if e == io.EOF {
			break
		}
		if e != nil {
			return Native{}, e
		}
	}
	return Native{Tables: []Table{{path.Base(member), member, rows}}, Issues: issues}, nil
}
