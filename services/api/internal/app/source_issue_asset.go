package app

import (
	"context"
	"encoding/json"
	"os"
	"tangerine.local/api/internal/source"
)

func (s *Storage) sourceIssueAsset(ctx context.Context, run *SourceRun) error {
	if len(run.Report.Issues) < 1000 {
		return nil
	}
	f, e := os.CreateTemp("", "tangerine-source-issues-")
	if e != nil {
		return e
	}
	defer os.Remove(f.Name())
	defer f.Close()
	rows, e := s.DB.Query(ctx, "SELECT locator,code,detail FROM source_issue WHERE import_id=$1 ORDER BY locator,code", run.Report.ID)
	if e != nil {
		return e
	}
	encoder := json.NewEncoder(f)
	for rows.Next() {
		var issue source.Issue
		if e = rows.Scan(&issue.Locator, &issue.Code, &issue.Detail); e != nil {
			rows.Close()
			return e
		}
		if e = encoder.Encode(issue); e != nil {
			rows.Close()
			return e
		}
	}
	rows.Close()
	if e = rows.Err(); e != nil {
		return e
	}
	if _, e = f.Seek(0, 0); e != nil {
		return e
	}
	m, e := s.saveSourceStream(ctx, "import-issues/"+run.Report.ID+".jsonl", f)
	if e != nil {
		return e
	}
	run.Report.FullIssues = &m.AssetID
	return nil
}
