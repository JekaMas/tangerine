package app

import (
	"context"
	"encoding/json"
	"tangerine.local/api/internal/source"
)

func (s *Storage) correctionRun(ctx context.Context, id string) (SourceRun, error) {
	run, e := s.SourceImport(ctx, id)
	if e != nil {
		return run, e
	}
	if run.Frozen.Release.Source != "JFLEG" {
		return run, ErrInput
	}
	return run, nil
}
func correctionPartition(partition string) bool {
	return partition == "" || partition == "dev" || partition == "test"
}

// Saved normalized examples are trusted. This read does not reparse source
// files, derive alignments, recount the release or validate saved schemas/hashes.
func (s *Storage) correctionPage(ctx context.Context, id, cursor, partition string, limit int) ([]source.CorrectionExample, string, error) {
	if !correctionPartition(partition) {
		return nil, "", ErrInput
	}
	if limit < 1 || limit > 200 {
		limit = 20
	}
	member := ""
	ordinal := int64(-1)
	if cursor != "" {
		var position struct {
			Member  string `json:"member"`
			Ordinal int64  `json:"ordinal"`
		}
		if json.Unmarshal([]byte(cursor), &position) != nil {
			return nil, "", ErrInput
		}
		member, ordinal = position.Member, position.Ordinal
	}
	rows, e := s.DB.Query(ctx, "SELECT member,ordinal,projection->'written_correction_example' FROM source_row WHERE import_id=$1 AND table_name='jfleg_source' AND state='mapped' AND (member,ordinal)>($2,$3) AND ($4='' OR projection->'written_correction_example'->>'source_partition'=$4) ORDER BY member,ordinal LIMIT $5", id, member, ordinal, partition, limit+1)
	if e != nil {
		return nil, "", e
	}
	defer rows.Close()
	out := []source.CorrectionExample{}
	next := ""
	for rows.Next() {
		var current string
		var index int64
		var raw []byte
		if e = rows.Scan(&current, &index, &raw); e != nil {
			return nil, "", e
		}
		if len(out) == limit {
			next = string(sourceBytes(map[string]any{"member": member, "ordinal": ordinal}))
			break
		}
		var example source.CorrectionExample
		if e = json.Unmarshal(raw, &example); e != nil {
			return nil, "", e
		}
		out = append(out, example)
		member, ordinal = current, index
	}
	return out, next, rows.Err()
}
func (s *Storage) SourceCorrectionExamples(ctx context.Context, id, cursor, partition string, limit int) ([]source.CorrectionExample, string, error) {
	if _, e := s.correctionRun(ctx, id); e != nil {
		return nil, "", e
	}
	return s.correctionPage(ctx, id, cursor, partition, limit)
}
func (s *Storage) SourceCorrectionDataset(ctx context.Context, id, partition string) (source.CorrectionDataset, error) {
	run, e := s.correctionRun(ctx, id)
	if e != nil {
		return source.CorrectionDataset{}, e
	}
	d := source.CorrectionDataset{Version: "2.0.0", Kind: "written_correction_references", Source: "JFLEG", Release: run.Report.Release, SourceVersion: run.Frozen.Release.Release, SourceURI: run.Frozen.Release.Origin, SourceManifest: run.Report.Manifest, Partition: partition, ScorerVersion: source.CorrectionScorerVersion, Licence: "CC-BY-NC-SA-4.0", Attribution: "Napoles, Sakaguchi and Tetreault (2017), JFLEG: A Fluency Corpus and Benchmark for Grammatical Error Correction; Heilman, Cahill, Madnani, Lopez, Mulholland and Tetreault (2014), Predicting Grammaticality on an Ordinal Scale. Preserve the acquired owner README and source terms.", Examples: []source.CorrectionExample{}}
	cursor := ""
	for {
		items, next, e := s.correctionPage(ctx, id, cursor, partition, 200)
		if e != nil {
			return d, e
		}
		d.Examples = append(d.Examples, items...)
		if next == "" {
			return d, nil
		}
		cursor = next
	}
}
