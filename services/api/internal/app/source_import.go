package app

import (
	"context"
)

func (s *Storage) RunSourceImport(ctx context.Context, id, key string, revision int64) (run SourceRun, err error) {
	run, err = s.acquireSource(ctx, id, key, revision)
	if err != nil || run.Replay {
		return run, err
	}
	if run.Report.State == "complete" || run.Report.State == "quarantined" {
		run.Phase = "complete"
		err = s.checkpointSource(ctx, &run, true)
		return run, err
	}
	defer func() {
		if err != nil {
			s.failSource(&run, err)
		}
	}()
	members, e := s.sourceMembers(ctx, run.Report.Release)
	if e != nil {
		return run, e
	}
	run.Report.State = "parsing"
	run.Report.Finished = nil
	run.Report.RawComplete = true
	if run.Phase != "mapping" {
		run.Phase = "parsing"
		if e = s.stageSource(ctx, &run, members); e != nil {
			return run, e
		}
		run.Phase = "mapping"
		run.Member = ""
		run.Row = -1
		if e = s.checkpointSource(ctx, &run, false); e != nil {
			return run, e
		}
	}
	if e = s.projectSource(ctx, &run, members); e != nil {
		return run, e
	}
	if e = s.sourceSummary(ctx, &run); e != nil {
		return run, e
	}
	if e = s.sourceIssueAsset(ctx, &run); e != nil {
		return run, e
	}
	at := sourceTime()
	run.Report.Finished = &at
	run.Report.State = "complete"
	if run.Report.Quarantined != "0" || run.Report.Rejected != "0" {
		run.Report.State = "quarantined"
	}
	run.Phase = "complete"
	err = s.checkpointSource(ctx, &run, true)
	return run, err
}
