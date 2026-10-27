package app

type supplementCount struct {
	table, suffix string
	count         int64
}

func supplementExpectedRows(release SourceRelease) []supplementCount {
	rows := []supplementCount{}
	switch release.Source {
	case "EDACC":
		for _, part := range []struct {
			name                      string
			count, ctm, conversations int64
		}{{"dev", 9848, 137020, 36}, {"test", 9289, 145396, 40}} {
			for _, table := range []string{"segments", "text", "utt2spk", "stm", "stm_filt"} {
				suffix := table
				if table == "stm_filt" {
					suffix = "stm.filt"
				}
				rows = append(rows, supplementCount{"sp_edacc_" + table, part.name + "/" + suffix, part.count})
			}
			rows = append(rows, supplementCount{"sp_edacc_company_ctm", part.name + "/company.ctm", part.ctm}, supplementCount{"sp_edacc_conv_list", part.name + "/conv.list", part.conversations})
		}
		rows = append(rows, supplementCount{"sp_edacc_background", "", 122})
	case "ELRD":
		rows = append(rows, supplementCount{"sp_elrd_turns", "", 589})
	case "DIPLOMAT":
		for _, item := range []struct {
			folder string
			counts []int64
		}{{"CQA_task_dataset", []int64{15585, 1559, 2338}}, {"PIR_first_subtask_dataset", []int64{3341, 168, 668}}, {"PIR_second_subtask_dataset", []int64{5188, 244, 1062}}} {
			for i, part := range []string{"train", "val", "test"} {
				rows = append(rows, supplementCount{"sp_diplomat", item.folder + "/" + part + ".jsonl", item.counts[i]})
			}
		}
		for _, folder := range []string{"NLI_task_dataset", "NLI_dataset_without_context"} {
			rows = append(rows, supplementCount{"sp_diplomat", folder + "/dataset.json", 2551})
		}
	case "DRAL":
		counts := []int64{208, 205, 4496, 5786, 2}
		if release.Release == "8.0-fixes-plus-testdata" {
			counts = []int64{272, 272, 5692, 7632, 2}
		}
		for i, table := range []string{"conversation", "participant", "fragments_long", "fragments_short", "producer"} {
			rows = append(rows, supplementCount{"sp_dral_" + table, "", counts[i]})
		}
		if release.Release == "8.0-fixes-plus-testdata" {
			rows = append(rows, supplementCount{"sp_dral_fragments_long_sets", "", 5692}, supplementCount{"sp_dral_fragments_short_sets", "", 7632})
		}
	}
	return rows
}
