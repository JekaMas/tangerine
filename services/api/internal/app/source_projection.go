package app

import (
	"fmt"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
)

func sourceCorpus(run SourceRun, m source.Mapped, member source.Member, cp, licence map[string]any) (map[string]any, error) {
	text, ok := cp["text"].(string)
	if !ok {
		return nil, fmt.Errorf("actual source text absent")
	}
	origin, _ := cp["origin"].(string)
	if origin == "" {
		origin = "external_written"
	}
	groups := []string{source.StableID("source-record", m.ID)}
	if a, ok := cp["group_ids"].([]string); ok {
		groups = append(groups, a...)
	}
	if a, ok := cp["group_ids"].([]any); ok {
		for _, g := range a {
			groups = append(groups, fmt.Sprint(g))
		}
	}
	split := "quarantine"
	if member.Partition != nil {
		switch *member.Partition {
		case "train":
			split = "source_train"
		case "test":
			split = "source_test"
		case "dev":
			split = "dev"
		case "calibration":
			split = "calibration"
		case "holdout":
			split = "holdout"
		}
	}
	parserVersion := run.Report.ParserVersion
	if parserVersion == "" {
		parserVersion = source.ParserVersion
	} // Preserve legacy internal callers.
	lic := map[string]any{}
	for k, v := range licence {
		lic[k] = v
	}
	lic["source_record_id"] = m.ID
	c := map[string]any{"schema_version": "1.0.0", "id": m.ID, "source_id": run.Frozen.Release.Source, "release_id": run.Report.Release, "source_uri": run.Frozen.Release.Origin + "#" + m.Member, "raw_asset_sha256": member.SHA, "licence": lic, "split": split, "group_ids": groups, "origin": origin, "text": text, "speaker_id": nil, "l1": nil, "age_group": "unknown", "raw_annotations_asset_id": member.AssetID, "normalized_case_version_id": nil, "parser_version": parserVersion, "transform_ids": []string{m.ID + "-parse"}, "quality_status": "not_reviewed", "source_score_scale": nil}
	for _, k := range []string{"speaker_id", "l1", "age_group", "source_score_scale"} {
		if v, ok := cp[k]; ok {
			c[k] = v
		}
	}
	if _, _, e := contracts.Validate("corpus-record", "1.0.0", sourceBytes(c)); e != nil {
		return nil, e
	}
	return c, nil
}
