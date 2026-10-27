package app

import (
	"context"
	"fmt"
	"github.com/google/uuid"
	"strings"
	"testing"
)

func sourceCursorFixture(t *testing.T) (*sourceNative, SourceRun) {
	t.Helper()
	f := sourceFixture(t)
	var b strings.Builder
	b.WriteString("id,text\n")
	for i := 0; i < 257; i++ {
		fmt.Fprintf(&b, "r%d,native row %d\n", i, i)
	}
	f.upload(t, "records.csv", b.String())
	f.register(t, "MOODRICK-DATA", "partial_export")
	run, e := f.s.Store.createSourceImport(context.Background(), f.release.ID, "native", nil)
	sourceRequire(t, e)
	return f, run
}
func TestNativeSourceMappingCursorPositive(t *testing.T) {
	f, run := sourceCursorFixture(t)
	ctx := context.Background()
	run, e := f.s.Store.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision)
	sourceRequire(t, e)
	sourceAssert(t, "257", run.Report.Observed)
	sourceAssert(t, "257", run.Report.Accepted)
	sourceAssert(t, "257", run.Report.RawOnly)
	var n, distinct int
	var first, last int64
	sourceRequire(t, f.s.Store.DB.QueryRow(ctx, "SELECT count(*),count(DISTINCT ordinal),min(ordinal),max(ordinal) FROM source_row WHERE import_id=$1", run.Report.ID).Scan(&n, &distinct, &first, &last))
	sourceAssert(t, 257, n)
	sourceAssert(t, n, distinct)
	sourceAssert(t, int64(0), first)
	sourceAssert(t, int64(256), last)
}
func TestNativeSourceMappingCursorNegative(t *testing.T) {
	f, run := sourceCursorFixture(t)
	ctx := context.Background()
	run, e := f.s.Store.acquireSource(ctx, run.Report.ID, uuid.NewString(), run.Revision)
	sourceRequire(t, e)
	sourceRequire(t, f.s.Store.stageSource(ctx, &run, f.files))
	first, e := f.s.Store.sourceProjectionBatch(ctx, run.Report.ID, stagedSourceRow{Ordinal: -1})
	sourceRequire(t, e)
	sourceAssert(t, 64, len(first))
	sourceAssert(t, int64(0), first[0].Ordinal)
	cursor := first[63]
	// Read-owner fixture: a sparse already accepted interval is independent setup.
	_, e = f.s.Store.DB.Exec(ctx, "UPDATE source_row SET state='metadata' WHERE import_id=$1 AND ordinal>=64 AND ordinal<128", run.Report.ID)
	sourceRequire(t, e)
	next, e := f.s.Store.sourceProjectionBatch(ctx, run.Report.ID, cursor)
	sourceRequire(t, e)
	sourceAssert(t, 64, len(next))
	sourceAssert(t, int64(128), next[0].Ordinal)
	sourceAssert(t, int64(191), next[63].Ordinal)
	none, e := f.s.Store.sourceProjectionBatch(ctx, run.Report.ID, stagedSourceRow{Member: cursor.Member, Table: cursor.Table, Ordinal: 256})
	sourceRequire(t, e)
	sourceAssert(t, 0, len(none))
	foreign, e := f.s.Store.sourceProjectionBatch(ctx, uuid.NewString(), cursor)
	sourceRequire(t, e)
	sourceAssert(t, 0, len(foreign))
}
func TestNativeSourceMappingMemberTablePositive(t *testing.T) {
	f := sourceFixture(t)
	body := strings.Repeat("S He go home\nA 1 2|||R:VERB:SVA|||goes|||REQUIRED|||-NONE-|||0\n\n", 34)
	f.upload(t, "fce/readme.txt", "Constructed two-member/two-table traversal fixture.")
	f.upload(t, "fce/licence.txt", "Constructed local fixture notice.")
	f.upload(t, "fce/dev.m2", body)
	f.upload(t, "fce/train.m2", body)
	f.register(t, "FCE-2.1", "partial_export")
	run := f.run(t, "native", nil)
	sourceAssert(t, "136", run.Report.Observed)
	sourceAssert(t, "136", run.Report.Accepted)
	sourceAssert(t, "0", run.Report.RawOnly)
	rows, e := f.s.Store.DB.Query(context.Background(), "SELECT member,table_name,count(*) FROM source_row WHERE import_id=$1 GROUP BY member,table_name", run.Report.ID)
	sourceRequire(t, e)
	defer rows.Close()
	groups := map[string]int64{}
	for rows.Next() {
		var member, table string
		var n int64
		sourceRequire(t, rows.Scan(&member, &table, &n))
		groups[member+":"+table] = n
	}
	sourceRequire(t, rows.Err())
	sourceAssert(t, map[string]int64{"fce/dev.m2:sentences": 34, "fce/dev.m2:edits": 34, "fce/train.m2:sentences": 34, "fce/train.m2:edits": 34}, groups)
}
