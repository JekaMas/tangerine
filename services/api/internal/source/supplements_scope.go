package source

import (
	"fmt"
	"path"
	"strings"
)

func SupplementMissing(id string, members []Member) []string {
	missing := []string{}
	names := map[string]bool{}
	waves := 0
	for _, m := range members {
		n := strings.ToLower(m.Path)
		names[n] = true
		if strings.HasSuffix(n, ".wav") && !HistoricalSupplementMember(n) {
			waves++
		}
	}
	need := func(suffix string) {
		for n := range names {
			if n == suffix || strings.HasSuffix(n, "/"+suffix) {
				return
			}
		}
		missing = append(missing, suffix)
	}
	count := func(label string, got, want int) {
		if got != want {
			missing = append(missing, fmt.Sprintf("%s: expected %d, observed %d", label, want, got))
		}
	}
	switch id {
	case "EDACC":
		for _, part := range []string{"dev", "test"} {
			for _, base := range []string{"text", "segments", "utt2spk", "stm", "stm.filt", "company.ctm", "conv.list"} {
				need(part + "/" + base)
			}
		}
		for _, name := range []string{"linguistic_background.csv", "readme.txt", "evaluate.sh", "glm", "cc_by_sa_license_text.txt"} {
			need(name)
		}
		count("Selected EdAcc WAVE members", waves, 76)
	case "ELRD":
		transcripts := 0
		pairs := 0
		for n := range names {
			if strings.Contains(n, "/diarized_transcripts/") && strings.HasSuffix(n, ".jsonl") {
				transcripts++
				audio := path.Join(path.Dir(path.Dir(n)), "audios", strings.TrimSuffix(path.Base(n), ".jsonl")+".wav")
				if names[audio] {
					pairs++
				}
			}
		}
		count("ELRD WAVE members", waves, 15)
		count("ELRD transcripts", transcripts, 15)
		count("ELRD same-dialogue pairs", pairs, 15)
		for _, name := range []string{"readme.md", "license.md", "audios/license", "diarized_transcripts/license", "roleplay-descriptions.md"} {
			need(name)
		}
	case "DIPLOMAT":
		for _, folder := range []string{"cqa_task_dataset", "pir_first_subtask_dataset", "pir_second_subtask_dataset"} {
			for _, part := range []string{"train", "val", "test"} {
				need(folder + "/" + part + ".jsonl")
			}
			need(folder + "/.gitattributes")
		}
		for _, folder := range []string{"nli_task_dataset", "nli_dataset_without_context"} {
			need(folder + "/dataset.json")
			need(folder + "/.gitattributes")
		}
		for _, name := range []string{"readme.md", "diplomat.py", ".gitattributes"} {
			need(name)
		}
	case "DRAL":
		increment := false
		for n := range names {
			if strings.Contains(n, "dral-8.0/") {
				increment = true
				break
			}
		}
		if increment {
			count("DRAL8.0increment WAVE members", waves, 3076)
			for _, name := range []string{"conversation.csv", "participant.csv", "producer.csv", "fragments-short.csv", "fragments-long.csv", "fragments-short-sets.csv", "fragments-long-sets.csv", "changelog-releases.md", "stats.txt"} {
				need("dral-8.0/" + name)
			}
		} else {
			count("DRAL16kHzbase WAVE members", waves, 10490)
			for _, name := range []string{"conversation.csv", "participant.csv", "producer.csv", "fragments-short.csv", "fragments-long.csv"} {
				need("dral16khz/metadata/" + name)
			}
			need("dral16khz/dral-techreport2-final.pdf")
			need("dral16khz/dral-16khz.tgz")
		}
	}
	return missing
}
