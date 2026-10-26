package app

// Every event and participant-shaped row in this file is constructed. The
// eligibility tests do not establish an acquired corpus or genuine participants.
import (
	"context"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
	"tangerine.local/api/internal/empirical"
	"tangerine.local/api/internal/experiment"
)

func savedRequire(t *testing.T, err error) {
	t.Helper()
	if err != nil {
		t.Fatal(err)
	}
}
func savedEqual(t *testing.T, want, got any) {
	t.Helper()
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("want %#v; got %#v", want, got)
	}
}
func savedStore(t *testing.T) *Storage {
	t.Helper()
	ctx := context.Background()
	admin, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	savedRequire(t, e)
	schema := "saved_" + strings.ReplaceAll(uuid.NewString(), "-", "")
	_, e = admin.DB.Exec(ctx, "CREATE SCHEMA "+schema)
	savedRequire(t, e)
	u, e := url.Parse(os.Getenv("DATABASE_URL"))
	savedRequire(t, e)
	q := u.Query()
	q.Set("search_path", schema)
	u.RawQuery = q.Encode()
	s, e := OpenStorage(ctx, u.String(), "minio:9000", os.Getenv("MINIO_ROOT_USER"), os.Getenv("MINIO_ROOT_PASSWORD"), "regressions")
	savedRequire(t, e)
	t.Cleanup(func() { s.DB.Close(); _, _ = admin.DB.Exec(ctx, "DROP SCHEMA "+schema+" CASCADE"); admin.DB.Close() })
	savedRequire(t, s.Migrate(ctx))
	savedRequire(t, s.InitMedia(ctx))
	return s
}
func savedInput() EmpiricalSubmission {
	a := "grammar.verbs.subject_verb_agreement"
	in := empirical.Input{Population: empirical.Population{Release: "constructed-ten-exposures-v1", View: "ten-authored-sentences", Split: "development", Annotator: "independent-authored-reference", Window: "sentence", Modality: "text", Taxonomy: "v1", Crosswalk: "identity", Origin: "constructed"}, Leaves: []string{a}, AnnotatedLeaves: []string{a}, Windows: []empirical.Window{}, Decisions: []empirical.Decision{}}
	for i := 1; i <= 10; i++ {
		n := int64(5)
		in.Windows = append(in.Windows, empirical.Window{ID: fmt.Sprintf("E%02d", i), Annotated: true, Tokens: &n, Events: []empirical.Event{{ID: fmt.Sprintf("event-%02d", i), Native: "R:VERB:SVA", Leaf: &a, Secondary: []string{}, Control: i > 2}}, Opportunities: map[string]int64{a: 1}})
	}
	return EmpiricalSubmission{Title: "Constructed: two mistakes in ten exposures", Input: in, Attempts: []empirical.Attempt{}}
}
func savedCreate(t *testing.T, s *Storage, in EmpiricalSubmission) map[string]any {
	t.Helper()
	v, e := s.CreateEmpiricalReport(context.Background(), in)
	savedRequire(t, e)
	return v
}
func savedFraction(t *testing.T, value empirical.Fraction, n, d, rn, rd string) {
	t.Helper()
	savedEqual(t, n, value.Numerator)
	savedEqual(t, d, value.Denominator)
	if rn == "" {
		if value.Exact != nil || value.Missing == nil {
			t.Fatal(value)
		}
		return
	}
	savedEqual(t, &empirical.Exact{Numerator: rn, Denominator: rd}, value.Exact)
	if value.Missing != nil {
		t.Fatal(value)
	}
}
func savedEmit(t *testing.T, name string, value any) {
	t.Helper()
	if dir := os.Getenv("TANGERINE_SAVED_REPORT_EVIDENCE"); dir != "" {
		savedRequire(t, os.WriteFile(filepath.Join(dir, name), sourceBytes(value), 0600))
	}
}
func TestNativeSavedReportExposurePositive(t *testing.T) {
	s := savedStore(t)
	v := savedCreate(t, s, savedInput())
	r := v["report"].(empirical.Report)
	savedEqual(t, int64(10), r.Annotated)
	savedEqual(t, int64(50), *r.Tokens)
	savedEqual(t, int64(2), r.Events)
	savedEqual(t, 122, len(r.Leaves))
	for _, leaf := range r.Leaves {
		if leaf.ID == "grammar.verbs.subject_verb_agreement" {
			savedEqual(t, int64(8), leaf.Controls)
			savedFraction(t, leaf.Share, "2", "2", "1", "1")
			savedFraction(t, leaf.Prevalence, "2", "10", "1", "5")
			savedFraction(t, leaf.Opportunity, "2", "10", "1", "5")
			savedFraction(t, leaf.Density, "2000", "50", "40", "1")
		}
	}
	savedEqual(t, "constructed", r.Population.Origin)
	savedEmit(t, "exposure-report.json", v)
}
func TestNativeSavedReportMissingNegative(t *testing.T) {
	in := savedInput()
	in.Input.Windows = nil
	in.Input.AnnotatedLeaves = []string{}
	r := savedCreate(t, savedStore(t), in)["report"].(empirical.Report)
	savedEqual(t, int64(0), r.Windows)
	savedEqual(t, 0, len(r.AnnotatedLeaves))
	for _, leaf := range r.Leaves {
		if leaf.Prevalence.Exact != nil || leaf.Opportunity.Exact != nil || leaf.Density.Exact != nil {
			t.Fatal("invented exposure", leaf)
		}
	}
	savedEmit(t, "missing-report.json", r)
}
func TestNativeSavedReportZeroDenominatorNegative(t *testing.T) {
	in := savedInput()
	in.Input.Windows = in.Input.Windows[:1]
	in.Input.Windows[0].Opportunities["grammar.verbs.subject_verb_agreement"] = 0
	r := savedCreate(t, savedStore(t), in)["report"].(empirical.Report)
	for _, leaf := range r.Leaves {
		if leaf.ID == "grammar.verbs.subject_verb_agreement" {
			savedFraction(t, leaf.Opportunity, "1", "0", "", "")
		}
	}
}
func TestNativeSavedReportMappingNegative(t *testing.T) {
	in := savedInput()
	in.Input.Windows = in.Input.Windows[:1]
	in.Input.Windows[0].Events[0].Leaf = nil
	r := savedCreate(t, savedStore(t), in)["report"].(empirical.Report)
	savedEqual(t, int64(1), r.Unmapped)
	savedEqual(t, int64(1), r.MappingIncomplete)
	savedEqual(t, int64(0), r.Annotated)
	savedEqual(t, int64(1), r.SourceAnnotated)
	savedEqual(t, "R:VERB:SVA", r.NativeFrequencies[0].ID)
	savedFraction(t, r.NativeFrequencies[0].Prevalence, "1", "1", "1", "1")
	for _, leaf := range r.Leaves {
		if leaf.Prevalence.Exact != nil {
			t.Fatal("unmapped native annotation became project absence", leaf)
		}
	}
}
func TestNativeSavedReportRelationshipsPositive(t *testing.T) {
	in := savedInput()
	a := "grammar.verbs.subject_verb_agreement"
	b := "lexis.collocation"
	in.Input.AnnotatedLeaves = []string{a, b}
	in.Input.Windows = in.Input.Windows[:4]
	for i := range in.Input.Windows {
		w := &in.Input.Windows[i]
		w.Events = nil
		w.Opportunities = map[string]int64{a: 1, b: 1}
		if i < 2 {
			w.Events = append(w.Events, empirical.Event{ID: fmt.Sprint("a", i), Native: "A", Leaf: &a})
		}
		if i == 0 || i == 2 {
			w.Events = append(w.Events, empirical.Event{ID: fmt.Sprint("b", i), Native: "B", Leaf: &b})
		}
	}
	in.Input.Decisions = []empirical.Decision{{Reference: a, Predicted: a}, {Reference: a, Predicted: a}, {Reference: a, Predicted: "unknown"}}
	r := savedCreate(t, savedStore(t), in)["report"].(empirical.Report)
	savedEqual(t, 2, len(r.Pairs))
	for _, pair := range r.Pairs {
		savedEqual(t, int64(1), pair.Count)
		savedFraction(t, pair.Support, "1", "4", "1", "4")
		savedFraction(t, pair.Conditional, "1", "2", "1", "2")
		savedFraction(t, pair.Lift, "4", "4", "1", "1")
	}
	savedEqual(t, 2, len(r.Confusion))
	for _, row := range r.Confusion {
		if row.Predicted == a {
			savedFraction(t, row.Proportion, "2", "3", "2", "3")
		} else {
			savedFraction(t, row.Proportion, "1", "3", "1", "3")
		}
	}
	savedEmit(t, "relationships-report.json", r)
}
func TestNativeSavedReportSecondaryNegative(t *testing.T) {
	in := savedInput()
	in.Input.Windows = in.Input.Windows[:1]
	in.Input.Windows[0].Events[0].Secondary = []string{"lexis.collocation"}
	r := savedCreate(t, savedStore(t), in)["report"].(empirical.Report)
	savedEqual(t, 0, len(r.Pairs))
	savedEqual(t, int64(1), r.Events)
	for _, leaf := range r.Leaves {
		if leaf.ID == "lexis.collocation" {
			savedEqual(t, int64(1), leaf.Secondary)
			savedEqual(t, int64(0), leaf.Events)
			if leaf.Prevalence.Exact != nil {
				t.Fatal("secondary label became annotation scope")
			}
		}
	}
}
func TestNativeSavedReportAttemptOriginsNegative(t *testing.T) {
	in := savedInput()
	yes := true
	in.Attempts = []empirical.Attempt{{ID: "model", Actor: "generated", Origin: "model", Case: "c", Policy: "p", First: true, Success: &yes}, {ID: "constructed", Actor: "authored", Origin: "constructed", Case: "c", Policy: "p", First: true, Success: &yes}}
	d := savedCreate(t, savedStore(t), in)["difficulty"].(empirical.Difficulty)
	savedEqual(t, int64(0), d.Trials)
	savedEqual(t, "unrated", d.Rating)
	savedEqual(t, 2, d.Excluded["not_genuine_teacher"])
	if d.Lower != nil || d.Followup.Exact != nil {
		t.Fatal(d)
	}
}
func TestNativeSavedReportDifficultyPositive(t *testing.T) {
	in := savedInput()
	yes, no := true, false
	before := "a"
	in.Attempts = []empirical.Attempt{{ID: "a", Actor: "constructed-person-1", Origin: "genuine_teacher", Case: "c", Policy: "p", First: true, Success: &no}, {ID: "b", Actor: "constructed-person-2", Origin: "genuine_teacher", Case: "c", Policy: "p", First: true, Success: &yes}, {ID: "follow", Actor: "constructed-person-1", Origin: "genuine_teacher", Case: "c", Policy: "p", Success: &yes, Before: &before}}
	d := savedCreate(t, savedStore(t), in)["difficulty"].(empirical.Difficulty)
	savedEqual(t, int64(2), d.Trials)
	savedEqual(t, int64(1), d.Successes)
	savedEqual(t, "unrated", d.Rating)
	savedEqual(t, "insufficient_sample", *d.Missing)
	savedEqual(t, 1, d.Excluded["not_first_exposure"])
	savedFraction(t, d.Followup, "1", "1", "1", "1")
	savedEmit(t, "difficulty-fixture.json", d)
}
func TestNativeSavedReportSelfFollowupNegative(t *testing.T) {
	self := "one"
	yes := true
	d, e := empirical.DifficultyReport([]empirical.Attempt{{ID: self, Actor: "constructed-person", Origin: "genuine_teacher", Case: "c", Policy: "p", First: true, Success: &yes, Before: &self}})
	savedRequire(t, e)
	if d.Followup.Exact != nil {
		t.Fatal("one observation became an independent before/after pair", d.Followup)
	}
}
func TestNativeSavedReportFollowupOriginsNegative(t *testing.T) {
	yes, no := true, false
	before := "before"
	for _, name := range []string{"constructed_before", "other_participant", "missing_before", "unknown_outcome"} {
		t.Run(name, func(t *testing.T) {
			base := empirical.Attempt{ID: before, Actor: "constructed-person", Origin: "genuine_teacher", Case: "c", Policy: "p", First: true, Success: &no}
			after := empirical.Attempt{ID: "after", Actor: "constructed-person", Origin: "genuine_teacher", Case: "c", Policy: "p", Success: &yes, Before: &before}
			switch name {
			case "constructed_before":
				base.Origin = "constructed"
			case "other_participant":
				base.Actor = "another-constructed-person"
			case "missing_before":
				base.ID = "different"
			case "unknown_outcome":
				base.Success = nil
			}
			d, err := empirical.DifficultyReport([]empirical.Attempt{base, after})
			savedRequire(t, err)
			if d.Followup.Exact != nil {
				t.Fatal("unsupported follow-up population", d)
			}
		})
	}
}
func TestNativeSavedReportPersistencePositive(t *testing.T) {
	s := savedStore(t)
	in := savedInput()
	v := savedCreate(t, s, in)
	id := v["id"].(string)
	inputAsset := v["source_input_asset_id"].(string)
	raw, e := s.ReadAsset(context.Background(), inputAsset)
	savedRequire(t, e)
	var original EmpiricalSubmission
	savedRequire(t, json.Unmarshal(raw, &original))
	savedEqual(t, in.Title, original.Title)
	savedEqual(t, 10, len(original.Input.Windows))
	in.Input.Windows = nil
	in.Input.Population.Origin = "model" // only the caller's mutable input changes
	read, e := s.EmpiricalReport(context.Background(), id)
	savedRequire(t, e)
	var persisted map[string]any
	savedRequire(t, json.Unmarshal(read, &persisted))
	var expected map[string]any
	savedRequire(t, json.Unmarshal(sourceBytes(v), &expected))
	savedEqual(t, expected, persisted)
	list, e := s.EmpiricalReports(context.Background())
	savedRequire(t, e)
	savedEqual(t, 1, len(list))
	savedEqual(t, id, list[0]["id"])
}
func TestNativeSavedReportExistingReplayPositive(t *testing.T) {
	path := filepath.Join(os.Getenv("TANGERINE_SAVED_REPORT_EVIDENCE"), "saved-fadbb119-258f-4045-810b-a0abab20f26a.json")
	raw, e := os.ReadFile(path)
	savedRequire(t, e)
	var old struct {
		Submission EmpiricalSubmission `json:"submission"`
		Report     struct {
			Report     empirical.Report     `json:"report"`
			Difficulty empirical.Difficulty `json:"difficulty"`
		} `json:"report"`
	}
	savedRequire(t, json.Unmarshal(raw, &old))
	v := savedCreate(t, savedStore(t), old.Submission)
	savedEqual(t, old.Report.Report, v["report"].(empirical.Report))
	savedEqual(t, old.Report.Difficulty, v["difficulty"].(empirical.Difficulty))
	savedEmit(t, "reproduced-existing-report.json", v)
}
func TestNativeSavedCoveragePositive(t *testing.T) {
	a := "grammar.verbs.subject_verb_agreement"
	dataset := QualityDataset{Cases: []QualityCase{{ID: "p", Polarity: "positive", Taxonomy: []string{a}}, {ID: "n", Polarity: "negative", Taxonomy: []string{a}}}}
	p := QualityExperiment{Rows: []experiment.Row{{Case: "p", Status: "complete"}, {Case: "p", Status: "failed"}, {Case: "n", Status: "complete"}, {Case: "n", Status: "cancelled"}, {Case: "n", Status: "not_run"}}}
	rows := qualityCoverage(p, dataset)
	savedEqual(t, 122, len(rows))
	for _, row := range rows {
		if row["taxonomy_id"] == a {
			savedEqual(t, 1, row["positive_cases"])
			savedEqual(t, 1, row["negative_cases"])
			savedEqual(t, 2, row["completed_rows"])
			savedEqual(t, false, row["missing"])
		}
	}
	savedEmit(t, "constructed-quality-coverage.json", rows)
}
func TestNativeSavedCoveragePlannedNegative(t *testing.T) {
	dir := os.Getenv("TANGERINE_SAVED_REPORT_EVIDENCE")
	raw, e := os.ReadFile(filepath.Join(dir, "experiment-50093925-98f6-4476-adae-541a0b1724be.json"))
	savedRequire(t, e)
	var saved struct {
		Experiment QualityExperiment `json:"experiment"`
		Dataset    QualityDataset    `json:"dataset"`
	}
	savedRequire(t, json.Unmarshal(raw, &saved))
	savedEqual(t, "planned", saved.Experiment.Status)
	rows := qualityCoverage(saved.Experiment, saved.Dataset)
	savedEqual(t, 122, len(rows))
	for _, row := range rows {
		savedEqual(t, 0, row["completed_rows"])
		savedEqual(t, true, row["missing"])
	}
	savedEmit(t, "saved-planned-coverage.json", rows)
}
func TestNativeSavedReportZeroDispatchNegative(t *testing.T) {
	s := savedStore(t)
	v := savedCreate(t, s, savedInput())
	_, e := s.EmpiricalReport(context.Background(), v["id"].(string))
	savedRequire(t, e)
	var receipts, operations int
	savedRequire(t, s.DB.QueryRow(context.Background(), "SELECT count(*) FROM document WHERE kind='provider-receipt'").Scan(&receipts))
	savedRequire(t, s.DB.QueryRow(context.Background(), "SELECT count(*) FROM operation WHERE operation_name LIKE 'llm-%' OR operation_name LIKE 'speech-%'").Scan(&operations))
	savedEqual(t, 0, receipts)
	savedEqual(t, 0, operations)
	savedEmit(t, "zero-dispatch.json", map[string]any{"provider_receipts": receipts, "llm_or_speech_operations": operations})
}

// Same native report owners, served for actual browser interactions. All records
// live in a disposable schema; production user records and settings are untouched.
func TestSavedReportsBrowserFixture(t *testing.T) {
	s := savedStore(t)
	ctx := context.Background()
	dir := os.Getenv("TANGERINE_SAVED_REPORT_EVIDENCE")
	full := savedCreate(t, s, savedInput())
	missing := savedInput()
	missing.Title = "Unknown exposures: no annotated population"
	missing.Input.Windows = nil
	missing.Input.AnnotatedLeaves = []string{}
	unknown := savedCreate(t, s, missing)
	var schema string
	savedRequire(t, s.DB.QueryRow(ctx, "SELECT current_schema()").Scan(&schema))
	savedEmit(t, "browser-fixture.json", map[string]any{"schema": schema, "report": full, "unknown": unknown, "origin": "constructed native PostgreSQL/MinIO report fixtures"})
	server := NewServer(s, "http://localhost:3000", "http://unused.invalid")
	server.token = "saved-report-test-token"
	listener, e := net.Listen("tcp", ":8080")
	savedRequire(t, e)
	httpServer := &http.Server{Handler: server.Handler(), ReadHeaderTimeout: 5 * time.Second}
	go func() { _ = httpServer.Serve(listener) }()
	defer httpServer.Close()
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	deadline := time.After(45 * time.Minute)
	for {
		select {
		case <-deadline:
			t.Fatal("browser fixture deadline")
		case <-ticker.C:
			if _, e := os.Stat(filepath.Join(dir, "browser-done")); e != nil {
				continue
			}
			var count int
			savedRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM document WHERE kind='provider-receipt'").Scan(&count))
			savedEqual(t, 0, count)
			reports, e := s.EmpiricalReports(ctx)
			savedRequire(t, e)
			savedEmit(t, "browser-final.json", map[string]any{"provider_receipts": count, "reports": reports})
			return
		}
	}
}
