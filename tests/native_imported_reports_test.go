package app

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"os"
	"path/filepath"
	"strings"
	"tangerine.local/api/internal/empirical"
	"testing"
	"time"
)

const i38Writing = `S He buy book .
A 1 2|||R:VERB:SVA|||buys|||REQUIRED|||-NONE-|||0
A 2 2|||M:DET|||a|||REQUIRED|||-NONE-|||0
A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||1

S She walk .
A 1 2|||R:VERB:SVA|||walks|||REQUIRED|||-NONE-|||0

S I see dog .
A 2 2|||M:DET|||a|||REQUIRED|||-NONE-|||0

S We go home .
A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0

`

func i38Fixture(t *testing.T) (*sourceNative, SourceRun) {
	t.Helper()
	f := sourceFixture(t)
	f.upload(t, "fce/readme.txt", "Constructed I38 source fixture; not an acquired corpus.")
	f.upload(t, "fce/licence.txt", "Constructed local fixture notice")
	for _, part := range []string{"train", "dev", "test"} {
		f.upload(t, "fce/m2/fce."+part+".gold.bea19.m2", i38Writing)
	}
	f.register(t, "FCE-2.1", "full_named_release")
	run := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), run.Report.ID))
	return f, run
}
func i38Report(t *testing.T, f *sourceNative, run SourceRun, annotator string) map[string]any {
	t.Helper()
	out, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Constructed four-sentence contrast", Source: &EmpiricalSource{Import: run.Report.ID, Basis: "m2", Member: "fce/m2/fce.train.gold.bea19.m2", Table: "sentences", Annotator: annotator}})
	sourceRequire(t, e)
	return out
}
func i38Evidence(t *testing.T, name string, v any) {
	t.Helper()
	if d := os.Getenv("I38_EVIDENCE"); d != "" {
		sourceRequire(t, os.WriteFile(filepath.Join(d, name+".json"), sourceBytes(v), 0600))
	}
}
func TestImportedCataloguePositive(t *testing.T) {
	f, run := i38Fixture(t)
	choices, e := f.s.Store.EmpiricalPopulations(context.Background())
	sourceRequire(t, e)
	sourceAssert(t, 3, len(choices))
	for _, c := range choices {
		sourceAssert(t, run.Report.ID, c.Source.Import)
		sourceAssert(t, "m2", c.Source.Basis)
		if strings.Contains(c.Title, "/") {
			t.Fatal("Technical path shown as a source name", c)
		}
	}
	repeated := f.run(t, "native", nil)
	sourceRequire(t, f.s.Store.CommitSourceImport(context.Background(), repeated.Report.ID))
	choices, e = f.s.Store.EmpiricalPopulations(context.Background())
	sourceRequire(t, e)
	sourceAssert(t, 3, len(choices))
	for _, c := range choices {
		sourceAssert(t, repeated.Report.ID, c.Source.Import)
		sourceAssert(t, "constructed", c.DataOrigin)
	}
}
func TestImportedCatalogueNegative(t *testing.T) {
	f, run := i38Fixture(t)
	_, e := f.s.Store.DB.Exec(context.Background(), "UPDATE source_import SET published=false WHERE id=$1", run.Report.ID)
	sourceRequire(t, e)
	choices, e := f.s.Store.EmpiricalPopulations(context.Background())
	sourceRequire(t, e)
	sourceAssert(t, 0, len(choices))
	_, e = f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Not published", Source: &EmpiricalSource{Import: run.Report.ID, Basis: "m2", Member: "fce/m2/fce.train.gold.bea19.m2", Table: "sentences"}})
	if e == nil {
		t.Fatal("Unpublished import used")
	}
	sourceAssert(t, 0, len(mustI38Reports(t, f.s.Store)))
}
func mustI38Reports(t *testing.T, s *Storage) []map[string]any {
	t.Helper()
	v, e := s.EmpiricalReports(context.Background())
	sourceRequire(t, e)
	return v
}
func TestImportedWritingPositive(t *testing.T) {
	f, run := i38Fixture(t)
	out := i38Report(t, f, run, "")
	r := out["report"].(empirical.Report)
	sourceAssert(t, int64(4), r.Windows)
	sourceAssert(t, int64(4), r.NativePopulation.Annotated)
	sourceAssert(t, int64(15), *r.NativePopulation.Tokens)
	sourceAssert(t, int64(4), r.NativePopulation.Events)
	sourceAssert(t, int64(4), r.Events)
	sourceAssert(t, int64(2), r.Native["R:VERB:SVA"])
	sourceAssert(t, int64(2), r.Native["M:DET"])
	sourceAssert(t, int64(1), r.Excluded["noop"])
	for _, leaf := range r.Leaves {
		if leaf.Prevalence.Exact != nil {
			t.Fatal("Derived mapping claimed category absence", leaf)
		}
	}
	sourceAssert(t, 122, len(r.Leaves))
	sourceAssert(t, 2, len(r.NativePairs))
	sourceAssert(t, "1", r.NativePairs[0].Support.Exact.Numerator)
	sourceAssert(t, "4", r.NativePairs[0].Support.Exact.Denominator)
	i38Evidence(t, "writing-contrast", out)
}
func TestImportedWritingNegative(t *testing.T) {
	f, run := i38Fixture(t)
	r := i38Report(t, f, run, "9")["report"].(empirical.Report)
	sourceAssert(t, int64(4), r.Windows)
	sourceAssert(t, int64(0), r.NativePopulation.Annotated)
	sourceAssert(t, int64(0), r.NativePopulation.Events)
	for _, v := range r.NativeFrequencies {
		if v.Prevalence.Exact != nil {
			t.Fatal("Absent annotator borrowed annotations")
		}
	}
	_, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Wrong member", Source: &EmpiricalSource{Import: run.Report.ID, Basis: "m2", Member: "fce/m2/absent.m2", Table: "sentences"}})
	if e == nil {
		t.Fatal("Missing member silently became an empty report")
	}
}
func TestImportedPersistencePositive(t *testing.T) {
	f, run := i38Fixture(t)
	out := i38Report(t, f, run, "")
	id := out["id"].(string)
	before, e := f.s.Store.EmpiricalReport(context.Background(), id)
	sourceRequire(t, e)
	var asset string
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT input_asset_id FROM empirical_report WHERE id=$1", id).Scan(&asset))
	raw, e := f.s.Store.ReadAsset(context.Background(), asset)
	sourceRequire(t, e)
	var input EmpiricalSubmission
	sourceRequire(t, json.Unmarshal(raw, &input))
	sourceAssert(t, run.Report.ID, input.Source.Import)
	sourceAssert(t, "native-context-1", input.Input.Population.Crosswalk)
	sourceAssert(t, "verb-agreement", input.Input.Windows[0].Events[0].Rule)
	_, e = f.s.Store.DB.Exec(context.Background(), "UPDATE source_row SET native_row='{}'::jsonb WHERE import_id=$1 AND table_name='sentences'", run.Report.ID)
	sourceRequire(t, e)
	after, e := f.s.Store.EmpiricalReport(context.Background(), id)
	sourceRequire(t, e)
	sourceAssert(t, string(before), string(after))
	copied, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Same frozen observations", ReuseInput: asset})
	sourceRequire(t, e)
	sourceAssert(t, int64(4), copied["report"].(empirical.Report).NativePopulation.Events)
	sourceAssert(t, int64(4), copied["report"].(empirical.Report).Windows)
	sourceAssert(t, true, copied["source_summary"].(*EmpiricalSourceSummary).Constructed)
	var calls int
	sourceRequire(t, f.s.Store.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='provider-receipt'").Scan(&calls))
	sourceAssert(t, 0, calls)
	i38Evidence(t, "persistence", map[string]any{"saved_read_unchanged": true, "provider_calls": calls, "report_id": id})
}
func TestImportedPersistenceNegative(t *testing.T) {
	f, run := i38Fixture(t)
	good := i38Report(t, f, run, "")
	_, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Unsupported basis", Source: &EmpiricalSource{Import: run.Report.ID, Basis: "invent-frequency", Table: "sentences"}})
	if e == nil {
		t.Fatal("Unsupported source basis accepted")
	}
	_, e = f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Missing saved observations", ReuseInput: "missing-owned-input"})
	if e == nil {
		t.Fatal("Missing saved input became a fresh empty report")
	}
	sourceAssert(t, 1, len(mustI38Reports(t, f.s.Store)))
	_, e = f.s.Store.EmpiricalReport(context.Background(), good["id"].(string))
	sourceRequire(t, e)
}

// Retained actual imports use the production intake/import finalizers once.
// These stores are test-owned and contain no credentials for an AI service.
func i38RetainedStore(t *testing.T) *Storage {
	t.Helper()
	s, e := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	sourceRequire(t, e)
	t.Cleanup(s.DB.Close)
	sourceRequire(t, s.Migrate(context.Background()))
	sourceRequire(t, s.InitMedia(context.Background()))
	return s
}
func TestImportedAcquireAvailable(t *testing.T) {
	s := i38RetainedStore(t)
	ctx := context.Background()
	id := os.Getenv("I38_SOURCE")
	name, dir, origin := "fce_v2.1.bea19.tar.gz", "bea", "https://www.cl.cam.ac.uk/research/nl/bea2019st/data/fce_v2.1.bea19.tar.gz"
	if id == "WILOCNESS-2.1" {
		name = "wi+locness_v2.1.bea19.tar.gz"
		origin = "https://www.cl.cam.ac.uk/research/nl/bea2019st/data/wi+locness_v2.1.bea19.tar.gz"
	}
	if id == "SPEECHOCEAN762" {
		name = "owner-613968e3b0b789fc33936fb5eba1973176ba7d11.tar.gz"
		dir = "speechocean762"
		origin = "https://github.com/jimbozhang/speechocean762/tree/613968e3b0b789fc33936fb5eba1973176ba7d11"
	}
	var old string
	e := s.DB.QueryRow(ctx, "SELECT i.id FROM source_import i JOIN source_release r ON r.id=i.release_id WHERE r.source_id=$1 ORDER BY i.created_at DESC LIMIT 1", id).Scan(&old)
	var run SourceRun
	if e == nil {
		run, e = s.SourceImport(ctx, old)
		sourceRequire(t, e)
	} else {
		file, e := os.Open(filepath.Join("/corpora", dir, name))
		sourceRequire(t, e)
		defer file.Close()
		members, e := s.IntakeArchive(ctx, name, "tar.gz", file)
		sourceRequire(t, e)
		files := []SourceReleaseFile{}
		docs := []string{}
		for _, m := range members {
			files = append(files, SourceReleaseFile{m.Path, m.SHA, sourceNumber(m.Bytes), m.Component, m.Partition, true})
			if m.Component == "documentation" {
				docs = append(docs, m.AssetID)
			}
		}
		version := "BEA-v2.1"
		if id == "SPEECHOCEAN762" {
			version = "owner-613968e3b0b789fc33936fb5eba1973176ba7d11"
		}
		release, e := s.RegisterSource(ctx, sourceBytes(map[string]any{"schema_version": "2.0.0", "source_id": id, "source_version": version, "origin_uri": origin, "documentation_asset_ids": docs, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": files, "expected_counts": []any{}, "scope_kind": "full_named_release", "component_expectations": []any{}}), uuid.NewString())
		sourceRequire(t, e)
		run, e = s.createSourceImport(ctx, release.ID, "native", nil)
		sourceRequire(t, e)
	}
	for turn := 0; run.Phase != "complete" && turn < 12; turn++ {
		bounded, cancel := context.WithTimeout(ctx, OverallDeadline)
		_, err := s.RunSourceImport(bounded, run.Report.ID, uuid.NewString(), run.Revision)
		cancel()
		run, e = s.SourceImport(ctx, run.Report.ID)
		sourceRequire(t, e)
		if err != nil {
			t.Logf("Saved partial progress after %s", fmt.Sprint(err))
		}
	}
	sourceAssert(t, "complete", run.Phase)
	sourceRequire(t, s.CommitSourceImport(ctx, run.Report.ID))
	i38Evidence(t, id+"-import", map[string]any{"import_id": run.Report.ID, "report": run.Report, "release": run.Frozen.Release.ID, "at": time.Now().UTC()})
}
func TestImportedActualReports(t *testing.T) {
	s := i38RetainedStore(t)
	ctx := context.Background()
	choices, e := s.EmpiricalPopulations(ctx)
	sourceRequire(t, e)
	if len(choices) == 0 {
		t.Fatal("Actual completed source populations are absent")
	}
	for _, c := range choices {
		if c.DataOrigin == "constructed" {
			continue
		}
		if selected := os.Getenv("I38_SOURCE"); selected != "" && c.SourceName != empiricalSourceName(selected) {
			continue
		}
		out, e := s.CreateEmpiricalReport(ctx, EmpiricalSubmission{Title: c.Title, Source: &c.Source})
		sourceRequire(t, e)
		r := out["report"].(empirical.Report)
		if len(r.Leaves) != 122 {
			t.Fatal("Category coverage lost")
		}
		id := out["id"].(string)
		read, e := s.EmpiricalReport(ctx, id)
		sourceRequire(t, e)
		sourceAssert(t, string(sourceBytes(out)), string(read))
		i38Evidence(t, "report-"+id, out)
	}
	i38Evidence(t, "catalogue", choices)
}

// Controlled row projections isolate the new report consumer, not source import.
// Actual complete L2/JFLEG/ratings/dialogue populations are tested separately.
func i38Rows(t *testing.T, id string, records []map[string]any) (*sourceNative, SourceRun) {
	t.Helper()
	f := sourceFixture(t)
	ctx := context.Background()
	f.upload(t, "fixture/README.md", "Constructed persisted projections for report-consumer testing only.")
	f.register(t, id, "full_named_release")
	run, e := f.s.Store.createSourceImport(ctx, f.release.ID, "native", nil)
	sourceRequire(t, e)
	_, e = f.s.Store.DB.Exec(ctx, "UPDATE source_import SET phase='complete',published=true WHERE id=$1", run.Report.ID)
	sourceRequire(t, e)
	for i, row := range records {
		_, e = f.s.Store.DB.Exec(ctx, "INSERT INTO source_row(import_id,member,table_name,ordinal,native_row,projection,state) VALUES($1,$2,$3,$4,$5,$6,'accepted')", run.Report.ID, row["member"], row["table"], i, sourceBytes(row["native"]), sourceBytes(row["projection"]))
		sourceRequire(t, e)
	}
	return f, run
}
func i38PhoneRows() []map[string]any {
	out := []map[string]any{}
	for _, v := range []struct {
		member, tier, origin, op, canonical, perceived string
		approx                                         bool
	}{
		{"ABA/annotation/one.TextGrid", "phones", "source_manual", "s", "TH", "S", false},
		{"ABA/annotation/one.TextGrid", "phones", "source_manual", "unchanged", "IH", "IH", false},
		{"ABA/annotation/two.TextGrid", "phones", "source_manual", "d", "IY", "sil", false},
		{"ABA/annotation/two.TextGrid", "phones", "source_manual", "s", "TH*", "S", true},
		{"ABA/textgrid/one.TextGrid", "phones", "source_automatic_alignment", "s", "TH", "S", false},
		{"ABA/annotation/one.TextGrid", "words", "source_manual", "s", "TH", "S", false},
		{"suitcase/ABA/annotation/story.TextGrid", "phones", "source_manual", "a", "sil", "T", false},
	} {
		out = append(out, map[string]any{"member": v.member, "table": "intervals", "native": map[string]any{"tier": v.tier}, "projection": map[string]any{"raw_metadata": map[string]any{"annotation_origin": v.origin, "phone_annotation": map[string]any{"operation": v.op, "canonical": v.canonical, "perceived": v.perceived, "approximate": v.approx}}}})
	}
	return out
}
func TestImportedSpeechPositive(t *testing.T) {
	f, run := i38Rows(t, "L2-ARCTIC", i38PhoneRows())
	out, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Constructed phone contrasts", Source: &EmpiricalSource{Import: run.Report.ID, Basis: "manual_phones_read", Table: "intervals"}})
	sourceRequire(t, e)
	r := out["report"].(empirical.Report)
	sourceAssert(t, int64(2), r.Windows)
	sourceAssert(t, int64(3), r.NativePopulation.Events)
	sourceAssert(t, int64(1), r.Events)
	sourceAssert(t, int64(2), r.Unmapped)
	sourceAssert(t, (*int64)(nil), r.NativePopulation.Tokens)
	sourceAssert(t, int64(2), r.Native["s"])
	sourceAssert(t, int64(1), r.Native["d"])
	summary := out["source_summary"].(*EmpiricalSourceSummary)
	sourceAssert(t, int64(4), summary.Coverage[0].Count)
	sourceAssert(t, int64(1), summary.Coverage[1].Count)
	sourceAssert(t, true, summary.Constructed)
}
func TestImportedSpeechNegative(t *testing.T) {
	f, run := i38Rows(t, "L2-ARCTIC", i38PhoneRows())
	out, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Constructed separate story", Source: &EmpiricalSource{Import: run.Report.ID, Basis: "manual_phones_suitcase", Table: "intervals"}})
	sourceRequire(t, e)
	r := out["report"].(empirical.Report)
	sourceAssert(t, int64(1), r.Windows)
	sourceAssert(t, int64(1), r.NativePopulation.Events)
	sourceAssert(t, int64(1), r.Native["a"])
	sourceAssert(t, int64(0), r.Native["s"])
	for _, l := range r.Leaves {
		if l.Opportunity.Exact != nil || l.Prevalence.Exact != nil {
			t.Fatal("Phone operations invented word/absence exposure")
		}
	}
}
func TestImportedCoveragePositive(t *testing.T) {
	f, run := i38Rows(t, "JFLEG", []map[string]any{{"member": "dev/dev.src", "table": "jfleg_source", "native": map[string]any{"text": "I goes ."}, "projection": map[string]any{"written_correction_example": map[string]any{"references": []string{"I go .", "I am going .", "I go .", "I do go ."}}}}})
	out, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Constructed alternatives", Source: &EmpiricalSource{Import: run.Report.ID, Basis: "coverage", Member: "dev/dev.src", Table: "jfleg_source"}})
	sourceRequire(t, e)
	r := out["report"].(empirical.Report)
	sourceAssert(t, int64(1), r.Windows)
	sourceAssert(t, int64(0), r.NativePopulation.Events)
	sourceAssert(t, int64(0), r.NativePopulation.Annotated)
	summary := out["source_summary"].(*EmpiricalSourceSummary)
	sourceAssert(t, int64(4), summary.Coverage[1].Count)
}
func TestImportedCoverageNegative(t *testing.T) {
	for _, c := range []struct{ id, table string }{{"ELRD", "sp_elrd_turns"}, {"DIPLOMAT", "sp_diplomat"}, {"DRAL", "sp_dral_fragments_long"}, {"SPEECHOCEAN762", "scores.json"}} {
		f, run := i38Rows(t, c.id, []map[string]any{{"member": "source/data.json", "table": c.table, "native": map[string]any{"label": 1, "accent": "Indian English", "asr": "He goes .", "rating": 3}, "projection": map[string]any{"source_example": map[string]any{"text": "He goes ."}}}})
		out, e := f.s.Store.CreateEmpiricalReport(context.Background(), EmpiricalSubmission{Title: "Constructed coverage", Source: &EmpiricalSource{Import: run.Report.ID, Basis: "coverage", Member: "source/data.json", Table: c.table}})
		sourceRequire(t, e)
		r := out["report"].(empirical.Report)
		sourceAssert(t, map[string]string{"ELRD": "conversation turns", "DIPLOMAT": "dialogue task examples", "DRAL": "audio-fragment records", "SPEECHOCEAN762": "rated utterances"}[c.id], out["source_summary"].(*EmpiricalSourceSummary).Unit)
		sourceAssert(t, "not-supplied", r.Population.Crosswalk)
		sourceAssert(t, int64(0), r.NativePopulation.Annotated)
		sourceAssert(t, int64(0), r.Events)
		sourceAssert(t, 0, len(r.NativeFrequencies))
		sourceAssert(t, 0, len(r.NativePairs))
		sourceAssert(t, (*int64)(nil), r.NativePopulation.Tokens)
		for _, l := range r.Leaves {
			if l.Prevalence.Exact != nil || l.Opportunity.Exact != nil {
				t.Fatal(c.id, "manufactured absence/rate")
			}
		}
	}
}
