package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
	"time"
)

func (s *Storage) SourceImport(ctx context.Context, id string) (SourceRun, error) {
	var run SourceRun
	var raw, frozen []byte
	var binding *string
	e := s.DB.QueryRow(ctx, "SELECT payload,frozen,revision,epoch,coalesce(operation_id,''),phase,coalesce(member_cursor,''),row_cursor,binding_selector FROM source_import WHERE id=$1", id).Scan(&raw, &frozen, &run.Revision, &run.Epoch, &run.Operation, &run.Phase, &run.Member, &run.Row, &binding)
	if e != nil {
		return run, e
	}
	if e = json.Unmarshal(raw, &run.Report); e != nil {
		return run, e
	}
	if e = json.Unmarshal(frozen, &run.Frozen); e != nil {
		return run, e
	}
	if binding != nil {
		run.Binding = *binding
	}
	return run, nil
}
func (s *Storage) createSourceImport(ctx context.Context, release, binding string, permissions []string) (SourceRun, error) {
	var old string
	var bid any
	if binding != "" && binding != "native" && binding != "raw-only" {
		bid = binding
	}
	e := s.DB.QueryRow(ctx, "SELECT id FROM source_import WHERE release_id=$1 AND binding_selector=$2", release, binding).Scan(&old)
	if e == nil {
		saved, e := s.SourceImport(ctx, old)
		if e != nil {
			return saved, e
		}
		if !sourceSameIDs(saved.Frozen.Permissions, permissions) {
			return SourceRun{}, ErrConflict
		}
		return saved, nil
	}
	if !sourceNotFound(e) {
		return SourceRun{}, e
	}
	r, e := s.SourceRelease(ctx, release)
	if e != nil {
		return SourceRun{}, e
	}
	f := SourceFrozen{Release: r, Permissions: permissions, Native: binding == "native"}
	if bid != nil {
		f.Binding, f.Program, e = s.sourceBinding(ctx, binding)
		if e != nil {
			return SourceRun{}, e
		}
		if f.Binding["source_id"] != r.Source || f.Binding["release_version"] != r.Release {
			return SourceRun{}, ErrReference
		}
		if p := f.Program; p != nil && (p.Source != r.Source || p.Release != r.ID || p.Manifest != r.Manifest) {
			return SourceRun{}, ErrReference
		}
		f.Native = f.Binding["record_selector"] == "native"
	}
	if _, e = s.sourceLicence(ctx, r, permissions); e != nil {
		return SourceRun{}, e
	}
	method, _ := contracts.Canonical(sourceBytes(map[string]any{"parser_id": "lossless-source", "parser_version": source.ParserVersion, "binding": f.Binding, "program": f.Program}))
	f.MethodSHA = contracts.Digest(method)
	run := SourceRun{Binding: binding, Phase: "inventory", Row: -1, Frozen: f}
	run.Report = SourceReport{Version: "2.0.0", ID: uuid.NewString(), Release: r.ID, Parser: "lossless-source", ParserVersion: source.ParserVersion, State: "inventory", Observed: "0", Accepted: "0", Quarantined: "0", Rejected: "0", RawOnly: "0", Components: []SourceComponentCount{}, Issues: []source.Issue{}, Manifest: r.Manifest, Started: sourceTime()}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return run, e
	}
	defer tx.Rollback(context.Background())
	_, e = tx.Exec(ctx, "INSERT INTO source_import(id,release_id,binding_id,payload,frozen,binding_selector) VALUES($1,$2,$3,$4,$5,$6) ON CONFLICT DO NOTHING", run.Report.ID, r.ID, bid, sourceBytes(run.Report), sourceBytes(f), binding)
	if e != nil {
		return run, e
	}
	if e = tx.QueryRow(ctx, "SELECT id FROM source_import WHERE release_id=$1 AND binding_selector=$2", release, binding).Scan(&old); e != nil {
		return run, e
	}
	if _, e = tx.Exec(ctx, "INSERT INTO source_import_event(import_id,revision,payload) VALUES($1,0,$2) ON CONFLICT DO NOTHING", old, sourceBytes(run.Report)); e != nil {
		return run, e
	}
	if e = tx.Commit(ctx); e != nil {
		return run, e
	}
	return s.SourceImport(ctx, old)
}
func (s *Storage) acquireSource(ctx context.Context, id, key string, revision int64) (SourceRun, error) {
	req := OperationRequest{Name: "import_source", Key: key, Path: "/api/v1/imports/" + id + ":run", Revision: &revision, Body: json.RawMessage(`{}`)}
	digest, e := operationDigest(req)
	if e != nil {
		return SourceRun{}, ErrInput
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return SourceRun{}, e
	}
	defer tx.Rollback(context.Background())
	op, fresh, e := reserveOperation(ctx, tx, req, digest)
	if e != nil {
		return SourceRun{}, e
	}
	if !fresh {
		var raw []byte
		if e = tx.QueryRow(ctx, "SELECT result FROM source_action WHERE operation_id=$1", op.ID).Scan(&raw); e == nil {
			var run SourceRun
			_ = json.Unmarshal(raw, &run)
			run.Replay = true
			return run, tx.Commit(ctx)
		}
		return SourceRun{}, ErrEvaluationActive
	}
	var current, epoch int64
	var phase string
	var live bool
	if e = tx.QueryRow(ctx, "SELECT revision,epoch,phase,coalesce(clock_timestamp()<deadline_at AND EXISTS(SELECT 1 FROM operation o WHERE o.id=source_import.operation_id AND o.state='running'),false) FROM source_import WHERE id=$1 FOR UPDATE", id).Scan(&current, &epoch, &phase, &live); e != nil {
		return SourceRun{}, e
	}
	if live {
		return SourceRun{}, ErrEvaluationActive
	}
	if revision != current {
		return SourceRun{}, ErrRevision
	}
	if _, e = tx.Exec(ctx, "UPDATE source_import SET epoch=epoch+1,operation_id=$2,deadline_at=clock_timestamp()+interval '270 seconds',phase='running' WHERE id=$1", id, op.ID); e != nil {
		return SourceRun{}, e
	}
	if _, e = tx.Exec(ctx, "UPDATE operation SET state='running',subject_id=$2 WHERE id=$1", op.ID, id); e != nil {
		return SourceRun{}, e
	}
	if e = tx.Commit(ctx); e != nil {
		return SourceRun{}, e
	}
	run, e := s.SourceImport(ctx, id)
	run.Phase = phase
	run.Operation = op.ID
	run.Epoch = epoch + 1
	return run, e
}
func sourceOwned(ctx context.Context, tx pgx.Tx, r SourceRun) error {
	var epoch int64
	var operation string
	var live bool
	e := tx.QueryRow(ctx, "SELECT epoch,coalesce(operation_id,''),clock_timestamp()<deadline_at FROM source_import WHERE id=$1 FOR UPDATE", r.Report.ID).Scan(&epoch, &operation, &live)
	if e != nil {
		return e
	}
	if epoch != r.Epoch || operation != r.Operation || (!live && r.Report.State != "failed") {
		return ErrEvaluationLease
	}
	return nil
}
func (s *Storage) checkpointSource(ctx context.Context, run *SourceRun, finish bool) error {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	if e = sourceOwned(ctx, tx, *run); e != nil {
		return e
	}
	run.Revision++
	if _, e = tx.Exec(ctx, "UPDATE source_import SET revision=$2,payload=$3,phase=$4,member_cursor=$5,row_cursor=$6 WHERE id=$1", run.Report.ID, run.Revision, sourceBytes(run.Report), run.Phase, run.Member, run.Row); e != nil {
		return e
	}
	if _, e = tx.Exec(ctx, "INSERT INTO source_import_event(import_id,revision,payload) VALUES($1,$2,$3)", run.Report.ID, run.Revision, sourceBytes(run.Report)); e != nil {
		return e
	}
	if finish {
		if _, e = tx.Exec(ctx, "INSERT INTO source_action(operation_id,import_id,result) VALUES($1,$2,$3)", run.Operation, run.Report.ID, sourceBytes(run)); e != nil {
			return e
		}
		state := "complete"
		if run.Report.State == "failed" {
			state = "failed"
		}
		if run.Report.State == "cancelled" {
			state = "cancelled"
		}
		if _, e = tx.Exec(ctx, "UPDATE operation SET state=$2,finished_at=clock_timestamp() WHERE id=$1", run.Operation, state); e != nil {
			return e
		}
	}
	return tx.Commit(ctx)
}
func (s *Storage) CancelSource(ctx context.Context, id string, revision int64) (SourceRun, error) {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return SourceRun{}, e
	}
	defer tx.Rollback(context.Background())
	var raw []byte
	var current int64
	var op *string
	if e = tx.QueryRow(ctx, "SELECT payload,revision,operation_id FROM source_import WHERE id=$1 FOR UPDATE", id).Scan(&raw, &current, &op); e != nil {
		return SourceRun{}, e
	}
	if current != revision {
		return SourceRun{}, ErrRevision
	}
	var report SourceReport
	_ = json.Unmarshal(raw, &report)
	if report.State == "complete" {
		return SourceRun{}, ErrConflict
	}
	report.State = "cancelled"
	at := sourceTime()
	report.Finished = &at
	report.Normalized = false
	current++
	if _, e = tx.Exec(ctx, "UPDATE source_import SET epoch=epoch+1,revision=$2,payload=$3 WHERE id=$1", id, current, sourceBytes(report)); e != nil {
		return SourceRun{}, e
	}
	if op != nil {
		if _, e = tx.Exec(ctx, "UPDATE operation SET state='cancelled',finished_at=clock_timestamp() WHERE id=$1 AND state='running'", *op); e != nil {
			return SourceRun{}, e
		}
	}
	if _, e = tx.Exec(ctx, "INSERT INTO source_import_event(import_id,revision,payload) VALUES($1,$2,$3)", id, current, sourceBytes(report)); e != nil {
		return SourceRun{}, e
	}
	if e = tx.Commit(ctx); e != nil {
		return SourceRun{}, e
	}
	return s.SourceImport(ctx, id)
}
func (s *Storage) sourceIssue(ctx context.Context, run SourceRun, issue source.Issue) error {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	if e = sourceOwned(ctx, tx, run); e != nil {
		return e
	}
	_, e = tx.Exec(ctx, "INSERT INTO source_issue(import_id,locator,code,detail) VALUES($1,$2,$3,$4) ON CONFLICT DO NOTHING", run.Report.ID, issue.Locator, issue.Code, issue.Detail)
	if e != nil {
		return e
	}
	return tx.Commit(ctx)
}
func (s *Storage) failSource(run *SourceRun, cause error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	run.Report.State = "failed"

	run.Report.Normalized = false
	at := sourceTime()
	run.Report.Finished = &at
	issue := source.Issue{Locator: run.Member, Code: "import_failed", Detail: sourceError(cause)}
	_ = s.sourceIssue(ctx, *run, issue)
	_ = s.sourceSummary(ctx, run)
	run.Report.Normalized = false
	_ = s.checkpointSource(ctx, run, true)
}
func sourceCursor(m, t string, n int64) string { return string(sourceBytes([]any{m, t, n})) }

func (s *Storage) CommitSourceImport(ctx context.Context, id string) error {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	var phase string
	if e = tx.QueryRow(ctx, "SELECT phase FROM source_import WHERE id=$1 FOR UPDATE", id).Scan(&phase); e != nil {
		return e
	}
	if phase != "complete" {
		return ErrConflict
	}
	if _, e = tx.Exec(ctx, "UPDATE source_import SET published=true WHERE id=$1", id); e != nil {
		return e
	}
	return tx.Commit(ctx)
}

func sourceSameIDs(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	set := map[string]bool{}
	for _, id := range a {
		set[id] = true
	}
	for _, id := range b {
		if !set[id] {
			return false
		}
	}
	return true
}
