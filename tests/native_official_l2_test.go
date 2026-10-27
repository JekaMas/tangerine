package app

// Actual official bytes and production owners; prior admission is reused, no
// corpus hashes are recomputed and no native/projected rows are substituted.
import (
	"archive/zip"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"io"
	"math/big"
	"net/url"
	"os"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"tangerine.local/api/internal/source"
	"testing"
	"time"
)

type officialL2Member struct {
	Path  string `json:"path"`
	SHA   string `json:"sha256"`
	Bytes int64  `json:"bytes"`
}
type officialL2State struct {
	Release           string           `json:"release_id"`
	Import            string           `json:"import_id"`
	Phase             string           `json:"phase"`
	Copied            int64            `json:"copied_members"`
	Resumes           []map[string]any `json:"resumes"`
	Interruption      map[string]any   `json:"interruption"`
	Report            SourceReport     `json:"report"`
	AcceptedStability map[string]any   `json:"accepted_stability"`
	Counts            map[string]any   `json:"counts"`
	Readback          map[string]any   `json:"readback"`
}

func officialL2Open(t *testing.T) *Storage {
	t.Helper()
	s, e := OpenStorage(context.Background(), os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	sourceRequire(t, e)
	sourceRequire(t, s.Migrate(context.Background()))
	sourceRequire(t, s.InitMedia(context.Background()))
	return s
}
func officialL2Save(t *testing.T, v officialL2State) {
	t.Helper()
	b, e := json.MarshalIndent(v, "", "  ")
	sourceRequire(t, e)
	sourceRequire(t, os.WriteFile("/evidence/checkpoint.tmp", b, 0600))
	sourceRequire(t, os.Rename("/evidence/checkpoint.tmp", "/evidence/checkpoint.json"))
}
func officialL2Load() officialL2State {
	var v officialL2State
	b, e := os.ReadFile("/evidence/checkpoint.json")
	if e == nil {
		_ = json.Unmarshal(b, &v)
	}
	return v
}
func officialL2Materialize(t *testing.T, s *Storage, state *officialL2State) {
	t.Helper()
	ctx := context.Background()
	var inv struct {
		Files []officialL2Member `json:"files"`
	}
	b, e := os.ReadFile("/admission/members.json")
	sourceRequire(t, e)
	sourceRequire(t, json.Unmarshal(b, &inv))
	sourceAssert(t, 84295, len(inv.Files))
	admitted := map[string]officialL2Member{}
	for _, m := range inv.Files {
		admitted[m.Path] = m
	}
	existing := map[string]bool{}
	rows, e := s.DB.Query(ctx, "SELECT relative_path FROM source_file")
	sourceRequire(t, e)
	for rows.Next() {
		var p string
		sourceRequire(t, rows.Scan(&p))
		existing[p] = true
	}
	sourceRequire(t, rows.Err())
	rows.Close()
	var copied atomic.Int64
	copied.Store(int64(len(existing)))
	store := func(name string, r io.Reader) error {
		m := source.NewMember(name)
		a, ok := admitted[name]
		if !ok {
			return fmt.Errorf("member not in prior admission: %s", name)
		}
		m.SHA = a.SHA
		m.Bytes = a.Bytes
		if strings.HasSuffix(strings.ToLower(name), ".zip") {
			m.Component = "archive"
		}
		if strings.HasSuffix(strings.ToLower(name), ".wav") {
			data, err := io.ReadAll(r)
			if err != nil {
				return err
			}
			reader := bytes.NewReader(data)
			m.Media, err = source.WaveInfo(reader)
			if err != nil {
				return err
			}
			_, err = reader.Seek(0, 0)
			if err != nil {
				return err
			}
			r = reader
		}
		_, err := s.saveAdmittedSource(ctx, m, r)
		if err == nil {
			n := copied.Add(1)
			if n%1000 == 0 {
				t.Logf("materialized %d admitted source members", n)
			}
		}
		return err
	}
	z, e := zip.OpenReader("/corpus/official-v5-20261026.zip")
	sourceRequire(t, e)
	defer z.Close()
	for _, outer := range z.File {
		if outer.FileInfo().IsDir() {
			continue
		}
		name := outer.Name
		if strings.HasSuffix(strings.ToLower(name), ".zip") {
			complete := existing[name]
			for member := range admitted {
				if strings.HasPrefix(member, name+"/") && !existing[member] {
					complete = false
					break
				}
			}
			if complete {
				t.Logf("reuse stored official component %s without reading bytes", name)
				continue
			}
			reader, err := outer.Open()
			sourceRequire(t, err)
			f, err := os.CreateTemp("", "official-l2-component-")
			sourceRequire(t, err)
			_, err = io.Copy(f, reader)
			_ = reader.Close()
			sourceRequire(t, err)
			stat, err := f.Stat()
			sourceRequire(t, err)
			child, err := zip.NewReader(f, stat.Size())
			sourceRequire(t, err)
			// Bounded workers share only immutable ZIP/metadata; stream and asset owners
			// remain the real application implementation.
			jobs := make(chan *zip.File, len(child.File))
			for _, entry := range child.File {
				if !entry.FileInfo().IsDir() && !existing[name+"/"+entry.Name] {
					jobs <- entry
				}
			}
			close(jobs)
			failures := make(chan error, 4)
			var workers sync.WaitGroup
			for range 4 {
				workers.Add(1)
				go func() {
					defer workers.Done()
					for entry := range jobs {
						rr, err := entry.Open()
						if err == nil {
							err = store(name+"/"+entry.Name, rr)
							_ = rr.Close()
						}
						if err != nil {
							failures <- err
							return
						}
					}
				}()
			}
			workers.Wait()
			close(failures)
			for err := range failures {
				sourceRequire(t, err)
			}
			if !existing[name] {
				_, err = f.Seek(0, 0)
				sourceRequire(t, err)
				sourceRequire(t, store(name, f))
			}
			_ = f.Close()
			_ = os.Remove(f.Name())
		} else if !existing[name] {
			reader, err := outer.Open()
			sourceRequire(t, err)
			err = store(name, reader)
			_ = reader.Close()
			sourceRequire(t, err)
		}
		state.Copied = copied.Load()
		state.Phase = "materializing"
		officialL2Save(t, *state)
		t.Logf("official component %s saved; total %d", name, state.Copied)
	}
	if !existing["official-v5-20261026.zip"] {
		f, err := os.Open("/corpus/official-v5-20261026.zip")
		sourceRequire(t, err)
		m := source.NewMember("official-v5-20261026.zip")
		m.SHA = "490d5a43e48b0af84f6bce8e766ad453e8cd670521d5876bb4d0741cca304fda"
		m.Bytes = 7515454814
		m.Component = "archive"
		_, err = s.saveAdmittedSource(ctx, m, f)
		_ = f.Close()
		sourceRequire(t, err)
		copied.Add(1)
	}
	state.Copied = copied.Load()
	sourceAssert(t, int64(84296), state.Copied)
	officialL2Save(t, *state)
	files := []SourceReleaseFile{}
	docs := []string{}
	rows, e = s.DB.Query(ctx, "SELECT relative_path,sha256,byte_count,asset_id FROM source_file ORDER BY relative_path COLLATE \"C\"")
	sourceRequire(t, e)
	for rows.Next() {
		var name, sha, asset string
		var size int64
		sourceRequire(t, rows.Scan(&name, &sha, &size, &asset))
		m := source.NewMember(name)
		if strings.HasSuffix(strings.ToLower(name), ".zip") {
			m.Component = "archive"
		}
		files = append(files, SourceReleaseFile{name, sha, sourceNumber(size), m.Component, nil, true})
		if m.Component == "documentation" {
			docs = append(docs, asset)
		}
	}
	sourceRequire(t, rows.Err())
	rows.Close()
	sourceAssert(t, 84296, len(files))
	sourceAssert(t, 4, len(docs))
	n := "84296"
	u := "26889"
	body := sourceBytes(map[string]any{"schema_version": "2.0.0", "source_id": "L2-ARCTIC", "source_version": "official-v5-20261026", "origin_uri": "https://psi.engr.tamu.edu/l2-arctic-corpus/", "documentation_asset_ids": docs, "permission_grant_ids": []string{}, "format_profile_id": nil, "format_profile_sha256": nil, "files": files, "expected_counts": []SourceCount{{Unit: "files", Value: &n}, {Unit: "utterances", Value: &u}}, "scope_kind": "full_named_release", "component_expectations": []any{}})
	release, e := s.RegisterSource(ctx, body, "fd85f26a-e0c6-45a9-a733-1835d5fb463b")
	sourceRequire(t, e)
	state.Release = release.ID
	state.Phase = "registered"
	officialL2Save(t, *state)
}
func TestNativeOfficialL2Full(t *testing.T) {
	s := officialL2Open(t)
	defer func() { s.DB.Close() }()
	state := officialL2Load()
	ctx := context.Background()
	if state.Release == "" {
		officialL2Materialize(t, s, &state)
	}
	run, e := s.createSourceImport(ctx, state.Release, "native", nil)
	sourceRequire(t, e)
	// A harness restart only follows removal of its uniquely named writer.
	// Fence that stopped operation through the real cancel owner before resume.
	if run.Phase != "complete" && run.Report.State == "parsing" {
		run, e = s.CancelSource(ctx, run.Report.ID, run.Revision)
		sourceRequire(t, e)
	}
	state.Import = run.Report.ID
	officialL2Save(t, state)
	if state.Interruption == nil {
		callCtx, cancel := context.WithCancel(ctx)
		finished := make(chan struct{})
		go func() {
			defer close(finished)
			tick := time.NewTicker(100 * time.Millisecond)
			defer tick.Stop()
			for {
				select {
				case <-callCtx.Done():
					return
				case <-tick.C:
					var rev int64
					var member string
					if err := s.DB.QueryRow(ctx, "SELECT revision,member_cursor FROM source_import WHERE id=$1", run.Report.ID).Scan(&rev, &member); err == nil && rev >= 5 && strings.Contains(member, ".TextGrid") {
						cancel()
						return
					}
				}
			}
		}()
		_, err := s.RunSourceImport(callCtx, run.Report.ID, uuid.NewString(), run.Revision)
		cancel()
		<-finished
		if !errors.Is(err, context.Canceled) {
			t.Fatalf("expected actual interruption; got %v", err)
		}
		failed, err := s.SourceImport(ctx, run.Report.ID)
		sourceRequire(t, err)
		sourceAssert(t, "failed", failed.Report.State)
		sourceAssert(t, false, failed.Report.Normalized)
		if err = s.CommitSourceImport(ctx, failed.Report.ID); !errors.Is(err, ErrConflict) {
			t.Fatalf("incomplete import committed: %v", err)
		}
		var count int64
		sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID).Scan(&count))
		if count == 0 {
			t.Fatal("no actual staging before interruption")
		}
		state.Interruption = map[string]any{"revision": failed.Revision, "member_cursor": failed.Member, "native_rows": count, "state": failed.Report.State, "normalized_complete": false, "commit_rejected": true}
		officialL2Save(t, state)
		s.DB.Close()
		s = officialL2Open(t)
		run, e = s.SourceImport(ctx, state.Import)
		sourceRequire(t, e)
		sourceAssert(t, failed.Member, run.Member)
		sourceAssert(t, failed.Revision, run.Revision)
		if _, err = s.RunSourceImport(ctx, run.Report.ID, uuid.NewString(), run.Revision-1); !errors.Is(err, ErrRevision) {
			t.Fatalf("stale revision admitted: %v", err)
		}
		var after int64
		sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1", run.Report.ID).Scan(&after))
		sourceAssert(t, count, after)
		state.Interruption["reopened_same_cursor"] = true
		state.Interruption["stale_revision_rejected"] = true
		state.Interruption["stale_revision_no_row_change"] = true
		officialL2Save(t, state)
	}
	for run.Phase != "complete" {
		run, e = s.SourceImport(ctx, state.Import)
		sourceRequire(t, e)
		started := time.Now()
		callCtx, cancel := context.WithTimeout(ctx, OverallDeadline)
		var mappingStop atomic.Bool
		watchDone := make(chan struct{})
		go func() {
			defer close(watchDone)
			if state.AcceptedStability != nil {
				return
			}
			tick := time.NewTicker(200 * time.Millisecond)
			defer tick.Stop()
			for {
				select {
				case <-callCtx.Done():
					return
				case <-tick.C:
					var phase, accepted string
					if qe := s.DB.QueryRow(ctx, "SELECT phase,payload->>'accepted_records' FROM source_import WHERE id=$1", run.Report.ID).Scan(&phase, &accepted); qe == nil && phase == "mapping" && accepted != "0" {
						mappingStop.Store(true)
						cancel()
						return
					}
				}
			}
		}()
		returned, err := s.RunSourceImport(callCtx, run.Report.ID, uuid.NewString(), run.Revision)
		cancel()
		<-watchDone
		// The existing owner deliberately reports ErrEvaluationLease when its
		// database270s window expires before the caller's timer fires. Accept
		// that exact expiry only for the same owner/epoch; a superseded writer
		// remains an error and cannot be silently treated as a timeout.
		expired := false
		if errors.Is(err, ErrEvaluationLease) {
			sourceRequire(t, s.DB.QueryRow(ctx, "SELECT epoch=$2 AND operation_id=$3 AND clock_timestamp()>=deadline_at FROM source_import WHERE id=$1", run.Report.ID, returned.Epoch, returned.Operation).Scan(&expired))
		}
		if err != nil && !expired && !errors.Is(err, context.DeadlineExceeded) && !(mappingStop.Load() && errors.Is(err, context.Canceled)) {
			t.Fatalf("full native conversion failed: %v", err)
		}
		saved, errRead := s.SourceImport(ctx, state.Import)
		sourceRequire(t, errRead)
		state.Resumes = append(state.Resumes, map[string]any{"revision_before": run.Revision, "revision_after": saved.Revision, "member_before": run.Member, "member_after": saved.Member, "phase": saved.Phase, "state": saved.Report.State, "observed": saved.Report.Observed, "accepted": saved.Report.Accepted, "seconds": time.Since(started).Seconds(), "deadline": expired || errors.Is(err, context.DeadlineExceeded), "same_owner_expiry": expired})
		state.Report = saved.Report
		state.Phase = saved.Phase
		if saved.Phase == "mapping" && saved.Report.Accepted != "0" && state.AcceptedStability == nil {
			anchor := officialL2Anchor(t, s, state.Import)
			n, parseErr := strconv.ParseInt(saved.Report.Accepted, 10, 64)
			sourceRequire(t, parseErr)
			state.AcceptedStability = map[string]any{"before": anchor, "accepted_before": n, "revision_before": saved.Revision, "unchanged": false}
			officialL2Save(t, state)
			s.DB.Close()
			s = officialL2Open(t)
		} else if state.AcceptedStability != nil && state.AcceptedStability["unchanged"] != true {
			anchor := officialL2Anchor(t, s, state.Import)
			sourceAssert(t, state.AcceptedStability["before"], anchor)
			state.AcceptedStability["unchanged"] = true
			state.AcceptedStability["revision_after"] = saved.Revision
		}
		officialL2Save(t, state)
		t.Logf("native resume %d: phase=%s member=%s observed=%s accepted=%s raw_only=%s quarantine=%s error=%v", len(state.Resumes), saved.Phase, saved.Member, saved.Report.Observed, saved.Report.Accepted, saved.Report.RawOnly, saved.Report.Quarantined, err)
		run = saved
	}
	sourceAssert(t, "complete", run.Report.State)
	sourceAssert(t, true, run.Report.RawComplete)
	sourceAssert(t, true, run.Report.Normalized)
	sourceAssert(t, "0", run.Report.RawOnly)
	sourceAssert(t, "0", run.Report.Quarantined)
	sourceAssert(t, 0, len(run.Report.FullMissing))
	sourceRequire(t, s.CommitSourceImport(ctx, run.Report.ID))
	state.Report = run.Report
	state.Phase = "committed"
	officialL2Save(t, state)
	officialL2Readback(t, s, &state)
}
func officialL2Anchor(t *testing.T, s *Storage, id string) map[string]any {
	t.Helper()
	var raw []byte
	sourceRequire(t, s.DB.QueryRow(context.Background(), "SELECT jsonb_build_object('member',member,'table',table_name,'ordinal',ordinal,'native_row',native_row,'projection',projection,'raw_record',raw_record,'corpus_record',corpus_record,'transformation',transformation) FROM source_row WHERE import_id=$1 AND state IN ('mapped','metadata') ORDER BY member,table_name,ordinal LIMIT 1", id).Scan(&raw))
	var value map[string]any
	sourceRequire(t, json.Unmarshal(raw, &value))
	return value
}
func officialL2Readback(t *testing.T, s *Storage, state *officialL2State) {
	t.Helper()
	ctx := context.Background()
	// Development-only whole-population assertions. Ordinary readback trusts the
	// admitted rows and stored completion report; it does not repeat these checks.
	queries := map[string]string{
		"rows_by_state":          "SELECT jsonb_object_agg(state,n) FROM (SELECT state,count(*) n FROM source_row WHERE import_id=$1 GROUP BY state) q",
		"tables":                 "SELECT jsonb_object_agg(table_name,n) FROM (SELECT table_name,count(*) n FROM source_row WHERE import_id=$1 GROUP BY table_name) q",
		"speaker_metadata":       "SELECT jsonb_build_object('all',count(*),'l1_groups',count(DISTINCT native_row->>'native_language'),'genders',jsonb_agg(DISTINCT native_row->>'gender')) FROM source_row WHERE import_id=$1 AND table_name='speakers'",
		"transcript_l1":          "SELECT jsonb_object_agg(l1,n) FROM (SELECT corpus_record->>'l1' l1,count(*) n FROM source_row WHERE import_id=$1 AND table_name='transcripts' GROUP BY 1) q",
		"native_tiers":           "SELECT jsonb_object_agg(k,n) FROM (SELECT (projection#>>'{raw_metadata,annotation_origin}')||':'||(native_row->>'tier') k,count(*) n FROM source_row WHERE import_id=$1 AND table_name IN ('intervals','points') GROUP BY 1) q",
		"tier_order":             "SELECT jsonb_build_object('all',count(*),'with_native_order',count(*) FILTER(WHERE native_row->>'tier_index' IS NOT NULL),'label_unchanged',count(*) FILTER(WHERE native_row->>'label'=projection#>>'{raw_metadata,native,label}'),'bounds_unchanged',count(*) FILTER(WHERE native_row->>'start_seconds'=projection#>>'{raw_metadata,native,start_seconds}' AND native_row->>'end_seconds'=projection#>>'{raw_metadata,native,end_seconds}')) FROM source_row WHERE import_id=$1 AND table_name IN ('intervals','points')",
		"transcripts_by_speaker": "SELECT jsonb_object_agg(speaker,n) FROM (SELECT corpus_record->>'speaker_id' speaker,count(*) n FROM source_row WHERE import_id=$1 AND table_name='transcripts' AND lower(member) NOT LIKE '%suitcase%' GROUP BY 1) q",
		"suite_speakers":         "SELECT jsonb_agg(speaker ORDER BY speaker) FROM (SELECT DISTINCT corpus_record->>'speaker_id' speaker FROM source_row WHERE import_id=$1 AND table_name='transcripts' AND lower(member) LIKE '%suitcase%') q",
		"layers":                 "SELECT jsonb_object_agg(layer,n) FROM (SELECT CASE WHEN lower(member) LIKE '%suitcase%' THEN 'suitcase_manual' WHEN member LIKE '%/annotation/%' THEN 'read_manual' ELSE 'read_automatic' END layer,count(DISTINCT member) n FROM source_row WHERE import_id=$1 AND table_name IN ('intervals','points') GROUP BY 1) q",
		"operations":             "SELECT jsonb_object_agg(k,n) FROM (SELECT (CASE WHEN lower(member) LIKE '%suitcase%' THEN 'suitcase_' ELSE 'read_' END)||(projection#>>'{raw_metadata,phone_annotation,operation}') k,count(*) n FROM source_row WHERE import_id=$1 AND projection#>>'{raw_metadata,phone_annotation,operation}' IS NOT NULL GROUP BY 1) q",
		"transcript_joins":       "SELECT jsonb_build_object('all',count(*),'with_audio',count(*) FILTER(WHERE projection#>>'{raw_metadata,audio_asset_id}' IS NOT NULL),'manual',count(*) FILTER(WHERE projection#>>'{raw_metadata,manual_annotation_member}' IS NOT NULL),'auto',count(*) FILTER(WHERE projection#>>'{raw_metadata,automatic_annotation_member}' IS NOT NULL),'read',count(*) FILTER(WHERE lower(member) NOT LIKE '%suitcase%'),'suitcase',count(*) FILTER(WHERE lower(member) LIKE '%suitcase%'),'suite_auto',count(*) FILTER(WHERE lower(member) LIKE '%suitcase%' AND projection#>>'{raw_metadata,automatic_annotation_member}' IS NOT NULL),'precise_pronunciation',count(*) FILTER(WHERE projection#>>'{raw_metadata,observed_pronunciation}' IS NOT NULL)) FROM source_row WHERE import_id=$1 AND table_name='transcripts'",
		"provenance":             "SELECT jsonb_build_object('all',count(*),'raw_asset',count(*) FILTER(WHERE raw_record->>'raw_byte_asset_id'=f.asset_id),'raw_sha',count(*) FILTER(WHERE raw_record->>'file_sha256'=f.sha256),'native_retained',count(*) FILTER(WHERE raw_record->'value' IS NOT NULL),'transform_asset',count(*) FILTER(WHERE transformation->'input_asset_ids'=jsonb_build_array(f.asset_id))) FROM source_row r JOIN source_member m ON m.release_id=(SELECT release_id FROM source_import WHERE id=$1) AND m.relative_path=r.member JOIN source_file f ON f.id=m.file_id WHERE r.import_id=$1",
		"annotation_claims":      "SELECT jsonb_build_object('automatic_phone_claims',count(*) FILTER(WHERE projection#>>'{raw_metadata,annotation_origin}'='source_automatic_alignment' AND projection#>'{raw_metadata,phone_annotation}' IS NOT NULL),'approximate_flag_lost',count(*) FILTER(WHERE projection#>'{raw_metadata,phone_annotation}' IS NOT NULL AND native_row->>'label' LIKE '%*%' AND projection#>'{raw_metadata,phone_annotation,approximate}'<>'true'::jsonb)) FROM source_row WHERE import_id=$1 AND table_name='intervals'",
		"uncertainty":            "SELECT jsonb_build_object('bare_SD',count(*) FILTER(WHERE native_row->>'label' IN ('S','D')),'bare_SD_not_error',count(*) FILTER(WHERE native_row->>'label' IN ('S','D') AND coalesce(projection#>>'{raw_metadata,phone_annotation,operation}','unchanged')='unchanged'),'unknown_perceived',count(*) FILTER(WHERE projection#>'{raw_metadata,phone_annotation,perceived}'='null'::jsonb),'approximate',count(*) FILTER(WHERE native_row->>'label' LIKE '%*%'),'ancillary_unnamed',count(*) FILTER(WHERE native_row->>'tier'='')) FROM source_row WHERE import_id=$1 AND table_name='intervals'",
	}
	state.Counts = map[string]any{}
	for key, q := range queries {
		var raw []byte
		sourceRequire(t, s.DB.QueryRow(ctx, q, state.Import).Scan(&raw))
		var v any
		sourceRequire(t, json.Unmarshal(raw, &v))
		state.Counts[key] = v
		officialL2Save(t, *state)
		t.Logf("actual %s: %s", key, raw)
	}
	var total, waves, linked, clock int64
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*),count(*) FILTER(WHERE lower(f.relative_path) LIKE '%.wav'),count(*) FILTER(WHERE a.state='linked'),count(*) FILTER(WHERE f.media_metadata->>'sample_rate_hz'='44100' AND f.media_metadata->>'channels'='1' AND f.media_metadata->>'bits_per_sample'='16') FROM source_member m JOIN source_file f ON f.id=m.file_id JOIN asset_location a ON a.asset_id=f.asset_id WHERE m.release_id=$1", state.Release).Scan(&total, &waves, &linked, &clock))
	state.Counts["assets"] = map[string]any{"all": total, "wave": waves, "linked": linked, "clock": clock}
	sourceAssert(t, int64(84296), total)
	sourceAssert(t, total, linked)
	sourceAssert(t, int64(26889), waves)
	sourceAssert(t, waves, clock)
	server := NewServer(s, "http://localhost:3000", "http://unused.invalid")
	server.token = "source-owned-token"
	f := sourceNative{s: server}
	read := map[string]any{}
	for key, url := range map[string]string{"release": "/api/v1/source-releases/" + state.Release, "report": "/api/v1/imports/" + state.Import, "progress": "/api/v1/imports/" + state.Import + "/progress", "records": "/api/v1/imports/" + state.Import + "/records?limit=3", "status": "/api/v1/sources"} {
		w := f.request("GET", url, nil, "", "")
		sourceAssert(t, 200, w.Code)
		var value any
		sourceRequire(t, json.Unmarshal(w.Body.Bytes(), &value))
		read[key] = map[string]any{"status": w.Code, "value": value}
		if key == "release" {
			r := value.(map[string]any)
			read[key] = map[string]any{"status": w.Code, "id": r["id"], "source_id": r["source_id"], "source_version": r["source_version"], "origin_uri": r["origin_uri"], "files": len(r["files"].([]any)), "docs": len(r["documentation_asset_ids"].([]any))}
		}
	}
	for key, member := range map[string]string{"transcript": "ABA.zip/ABA/transcript/arctic_a0003.txt", "suitcase_transcript": "suitcase_corpus.zip/suitcase_corpus/transcript/aba.txt", "automatic": "ABA.zip/ABA/textgrid/arctic_a0003.TextGrid"} {
		address := "/api/v1/imports/" + state.Import + "/records?limit=2&cursor=" + url.QueryEscape(sourceCursor(member, "", -1))
		w := f.request("GET", address, nil, "", "")
		sourceAssert(t, 200, w.Code)
		var body map[string]any
		sourceRequire(t, json.Unmarshal(w.Body.Bytes(), &body))
		items := body["items"].([]any)
		if len(items) == 0 {
			t.Fatal("missing native application record")
		}
		sourceAssert(t, member, items[0].(map[string]any)["member"])
		read[key] = map[string]any{"status": w.Code, "value": body}
	}
	bad := f.request("GET", "/api/v1/imports/"+state.Import+"/records?cursor=invalid", nil, "", "")
	sourceAssert(t, 400, bad.Code)
	read["bad_cursor"] = map[string]any{"status": bad.Code}
	var assetID string
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT f.asset_id FROM source_member m JOIN source_file f ON f.id=m.file_id WHERE m.release_id=$1 AND m.relative_path='ABA.zip/ABA/wav/arctic_a0003.wav'", state.Release).Scan(&assetID))
	w := f.request("GET", "/api/v1/sources/assets/"+assetID+"/bytes", nil, "", "")
	sourceAssert(t, 200, w.Code)
	sourceAssert(t, "RIFF", string(w.Body.Bytes()[:4]))
	sourceAssert(t, "WAVE", string(w.Body.Bytes()[8:12]))
	read["audio"] = map[string]any{"status": w.Code, "bytes": w.Body.Len(), "format": "RIFF/WAVE", "content_disposition": w.Header().Get("Content-Disposition"), "asset_id": assetID}
	state.Readback = read
	state.Phase = "verified"
	officialL2Save(t, *state)
	sourceRequire(t, os.WriteFile("/evidence/observations.json", sourceBytes(state), 0600))
}
func TestNativeOfficialL2Readback(t *testing.T) {
	s := officialL2Open(t)
	defer s.DB.Close()
	state := officialL2Load()
	if state.Import == "" {
		t.Fatal("no full import checkpoint")
	}
	officialL2Readback(t, s, &state)
}

// Development-only correction of projections rejected by the demonstrated
// endpoint serialization bug. Accepted rows and admitted/native data are trusted.
func TestNativeOfficialL2RepairClock(t *testing.T) {
	s := officialL2Open(t)
	defer s.DB.Close()
	ctx := context.Background()
	state := officialL2Load()
	run, e := s.SourceImport(ctx, state.Import)
	sourceRequire(t, e)
	_, e = s.CancelSource(ctx, run.Report.ID, run.Revision)
	sourceRequire(t, e)
	var acceptedBefore int64
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND state IN ('mapped','metadata')", state.Import).Scan(&acceptedBefore))
	before := officialL2Anchor(t, s, state.Import)
	rows, e := s.DB.Query(ctx, "SELECT r.member,r.table_name,r.ordinal,r.native_row->>'end_seconds',f.media_metadata->>'sample_count',f.media_metadata->>'sample_rate_hz',r.issues FROM source_row r JOIN source_file f ON f.asset_id=r.projection#>>'{raw_metadata,audio_asset_id}' WHERE r.import_id=$1 AND r.state='quarantined' AND jsonb_array_length(r.issues)=1 AND r.issues->0->>'code'='source_audio_bounds' ORDER BY r.member,r.table_name,r.ordinal", state.Import)
	sourceRequire(t, e)
	type rejected struct {
		Member, Table, End, Frames, Rate string
		Ordinal                          int64
		Issues                           json.RawMessage
	}
	retry := []rejected{}
	locators := []string{}
	for rows.Next() {
		var r rejected
		sourceRequire(t, rows.Scan(&r.Member, &r.Table, &r.Ordinal, &r.End, &r.Frames, &r.Rate, &r.Issues))
		end, _ := new(big.Rat).SetString(r.End)
		frames, _ := new(big.Rat).SetString(r.Frames)
		rate, _ := new(big.Rat).SetString(r.Rate)
		within, serialized := sourceWaveEnd(end, frames, rate)
		if within && serialized {
			retry = append(retry, r)
			locators = append(locators, fmt.Sprintf("%s:%d", r.Member, r.Ordinal))
		}
	}
	sourceRequire(t, rows.Err())
	rows.Close()
	if len(retry) == 0 {
		t.Fatal("no demonstrated rejected endpoints to repair")
	}
	sourceRequire(t, os.WriteFile("/evidence/clock-rejected-original.json", sourceBytes(retry), 0600))
	tx, e := beginWrite(ctx, s)
	sourceRequire(t, e)
	defer tx.Rollback(ctx)
	for _, r := range retry {
		tag, err := tx.Exec(ctx, "UPDATE source_row SET state='staged' WHERE import_id=$1 AND member=$2 AND table_name=$3 AND ordinal=$4 AND state='quarantined'", state.Import, r.Member, r.Table, r.Ordinal)
		sourceRequire(t, err)
		sourceAssert(t, int64(1), tag.RowsAffected())
	}
	// Superseded false findings are retained in the actual saved diagnostic file
	// and immutable import events; they are no longer active source problems.
	_, e = tx.Exec(ctx, "DELETE FROM source_issue i WHERE i.import_id=$1 AND i.code='source_audio_bounds' AND i.locator=ANY($2) AND NOT EXISTS(SELECT 1 FROM source_row r WHERE r.import_id=i.import_id AND r.state='quarantined' AND r.issues @> jsonb_build_array(jsonb_build_object('source_locator',i.locator,'code',i.code)))", state.Import, locators)
	sourceRequire(t, e)
	sourceRequire(t, tx.Commit(ctx))
	var acceptedAfter int64
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND state IN ('mapped','metadata')", state.Import).Scan(&acceptedAfter))
	sourceAssert(t, acceptedBefore, acceptedAfter)
	sourceAssert(t, before, officialL2Anchor(t, s, state.Import))
	sourceRequire(t, os.WriteFile("/evidence/clock-repair.json", sourceBytes(map[string]any{"requeued_false_projections": len(retry), "accepted_before": acceptedBefore, "accepted_after": acceptedAfter, "accepted_anchor_unchanged": true, "source_bytes_read": 0, "native_rows_rewritten": 0, "prior_diagnostics": "clock-rejected-original.json"}), 0600))
}

// Reconvert only previously rejected, structurally valid native extent data.
func TestNativeOfficialL2RepairExtents(t *testing.T) {
	s := officialL2Open(t)
	defer s.DB.Close()
	ctx := context.Background()
	state := officialL2Load()
	run, e := s.SourceImport(ctx, state.Import)
	sourceRequire(t, e)
	_, e = s.CancelSource(ctx, run.Report.ID, run.Revision)
	sourceRequire(t, e)
	var acceptedBefore int64
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND state IN ('mapped','metadata')", state.Import).Scan(&acceptedBefore))
	before := officialL2Anchor(t, s, state.Import)
	rows, e := s.DB.Query(ctx, "SELECT r.member,r.table_name,r.ordinal,r.native_row->>'end_seconds',f.media_metadata->>'sample_count',f.media_metadata->>'sample_rate_hz',r.issues FROM source_row r JOIN source_file f ON f.asset_id=r.projection#>>'{raw_metadata,audio_asset_id}' WHERE r.import_id=$1 AND r.state='quarantined' AND jsonb_array_length(r.issues)=1 AND r.issues->0->>'code'='source_audio_bounds' ORDER BY r.member,r.table_name,r.ordinal", state.Import)
	sourceRequire(t, e)
	type rejected struct {
		Member, Table, End, Frames, Rate string
		Ordinal                          int64
		Issues                           json.RawMessage
	}
	retry := []rejected{}
	locators := []string{}
	for rows.Next() {
		var r rejected
		sourceRequire(t, rows.Scan(&r.Member, &r.Table, &r.Ordinal, &r.End, &r.Frames, &r.Rate, &r.Issues))
		end, _ := new(big.Rat).SetString(r.End)
		frames, _ := new(big.Rat).SetString(r.Frames)
		rate, _ := new(big.Rat).SetString(r.Rate)
		within, serialized := sourceWaveEnd(end, frames, rate)
		if end != nil && frames != nil && rate != nil && rate.Sign() > 0 && !within && !serialized {
			retry = append(retry, r)
			locators = append(locators, fmt.Sprintf("%s:%d", r.Member, r.Ordinal))
		}
	}
	sourceRequire(t, rows.Err())
	rows.Close()
	if len(retry) == 0 {
		t.Fatal("no demonstrated rejected endpoints to repair")
	}
	sourceRequire(t, os.WriteFile("/evidence/extent-rejected-original.json", sourceBytes(retry), 0600))
	tx, e := beginWrite(ctx, s)
	sourceRequire(t, e)
	defer tx.Rollback(ctx)
	for _, r := range retry {
		tag, err := tx.Exec(ctx, "UPDATE source_row SET state='staged' WHERE import_id=$1 AND member=$2 AND table_name=$3 AND ordinal=$4 AND state='quarantined'", state.Import, r.Member, r.Table, r.Ordinal)
		sourceRequire(t, err)
		sourceAssert(t, int64(1), tag.RowsAffected())
	}
	// Superseded false findings are retained in the actual saved diagnostic file
	// and immutable import events; they are no longer active source problems.
	_, e = tx.Exec(ctx, "DELETE FROM source_issue i WHERE i.import_id=$1 AND i.code='source_audio_bounds' AND i.locator=ANY($2) AND NOT EXISTS(SELECT 1 FROM source_row r WHERE r.import_id=i.import_id AND r.state='quarantined' AND r.issues @> jsonb_build_array(jsonb_build_object('source_locator',i.locator,'code',i.code)))", state.Import, locators)
	sourceRequire(t, e)
	sourceRequire(t, tx.Commit(ctx))
	var acceptedAfter int64
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT count(*) FROM source_row WHERE import_id=$1 AND state IN ('mapped','metadata')", state.Import).Scan(&acceptedAfter))
	sourceAssert(t, acceptedBefore, acceptedAfter)
	sourceAssert(t, before, officialL2Anchor(t, s, state.Import))
	sourceRequire(t, os.WriteFile("/evidence/extent-repair.json", sourceBytes(map[string]any{"requeued_native_extent_projections": len(retry), "accepted_before": acceptedBefore, "accepted_after": acceptedAfter, "accepted_anchor_unchanged": true, "source_bytes_read": 0, "native_rows_rewritten": 0, "prior_diagnostics": "extent-rejected-original.json"}), 0600))
}

func TestNativeOfficialL2QualityReadback(t *testing.T) {
	s := officialL2Open(t)
	defer s.DB.Close()
	ctx := context.Background()
	state := officialL2Load()
	var raw []byte
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT jsonb_build_object('native_extent_rows',count(*) FILTER(WHERE projection#>>'{raw_metadata,clock_bound_relation}'='native_extent_exceeds_media'),'extent_unverified',count(*) FILTER(WHERE projection#>>'{raw_metadata,clock_bound_relation}'='native_extent_exceeds_media' AND projection#>>'{raw_metadata,clock_alignment_status}'='unverified'),'processing_rate_unknown',count(*) FILTER(WHERE projection#>>'{raw_metadata,clock_bound_relation}'='native_extent_exceeds_media' AND projection#>'{raw_metadata,annotation_processing_rate_hz}'='null'::jsonb),'serialized_endpoints',count(*) FILTER(WHERE projection#>>'{raw_metadata,clock_bound_relation}'='same_binary64_endpoint')) FROM source_row WHERE import_id=$1 AND table_name='intervals'", state.Import).Scan(&raw))
	var counts map[string]any
	sourceRequire(t, json.Unmarshal(raw, &counts))
	if counts["native_extent_rows"].(float64) == 0 {
		t.Fatal("actual native extent uncertainty disappeared")
	}
	sourceAssert(t, counts["native_extent_rows"], counts["extent_unverified"])
	sourceAssert(t, counts["native_extent_rows"], counts["processing_rate_unknown"])
	var member, table string
	var ordinal int64
	sourceRequire(t, s.DB.QueryRow(ctx, "SELECT member,table_name,ordinal FROM source_row WHERE import_id=$1 AND projection#>>'{raw_metadata,clock_bound_relation}'='native_extent_exceeds_media' ORDER BY member,table_name,ordinal LIMIT 1", state.Import).Scan(&member, &table, &ordinal))
	server := NewServer(s, "http://localhost:3000", "http://unused.invalid")
	server.token = "source-owned-token"
	f := sourceNative{s: server}
	w := f.request("GET", "/api/v1/imports/"+state.Import+"/records?limit=1&cursor="+url.QueryEscape(sourceCursor(member, table, ordinal-1)), nil, "", "")
	sourceAssert(t, 200, w.Code)
	var body map[string]any
	sourceRequire(t, json.Unmarshal(w.Body.Bytes(), &body))
	item := body["items"].([]any)[0].(map[string]any)
	sourceAssert(t, member, item["member"])
	metadata := item["projection"].(map[string]any)["raw_metadata"].(map[string]any)
	sourceAssert(t, "unverified", metadata["clock_alignment_status"])
	sourceAssert(t, nil, metadata["annotation_processing_rate_hz"])
	sourceRequire(t, os.WriteFile("/evidence/quality-readback.json", sourceBytes(map[string]any{"counts": counts, "record": item, "http_status": w.Code}), 0600))
}
