package source

import (
	"archive/tar"
	"archive/zip"
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func mustParse(t *testing.T, member, text, format string) Native {
	t.Helper()
	n, e := Parse(member, []byte(text), Options{Format: format, Encoding: "utf-8"})
	if e != nil {
		t.Fatal(e)
	}
	return n
}
func equal(t *testing.T, want, got any) {
	t.Helper()
	a, _ := json.Marshal(want)
	b, _ := json.Marshal(got)
	if !bytes.Equal(a, b) {
		t.Fatalf("want %s; got %s", a, b)
	}
}
func archiveFixture(t *testing.T, names []string, link bool) *os.File {
	t.Helper()
	f, e := os.CreateTemp("", "source-test-")
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(func() { f.Close(); os.Remove(f.Name()) })
	z := zip.NewWriter(f)
	for _, n := range names {
		h := &zip.FileHeader{Name: n, Method: zip.Deflate}
		h.SetMode(0600)
		if link {
			h.SetMode(os.ModeSymlink | 0777)
		}
		w, e := z.CreateHeader(h)
		if e != nil {
			t.Fatal(e)
		}
		_, _ = w.Write([]byte("ordinary inert $(touch NEVER)"))
	}
	if e = z.Close(); e != nil {
		t.Fatal(e)
	}
	return f
}
func TestSourceArchivePositive(t *testing.T) {
	f := archiveFixture(t, []string{"README.md", "code/run.sh", "data/file.txt"}, false)
	names := []string{}
	e := InspectArchive(context.Background(), f, "zip", DefaultLimits, func(v Entry) error {
		r, e := v.Open()
		if e != nil {
			return e
		}
		b, e := io.ReadAll(r)
		r.Close()
		equal(t, "ordinary inert $(touch NEVER)", string(b))
		names = append(names, v.Name)
		return e
	})
	if e != nil {
		t.Fatal(e)
	}
	equal(t, []string{"README.md", "code/run.sh", "data/file.txt"}, names)
}
func TestSourceArchiveNegative(t *testing.T) {
	for _, names := range [][]string{{"ok", "../escape"}, {"/absolute"}, {"a/./b", "a/b"}, {"C:/escape"}, {"bad\\path"}} {
		f := archiveFixture(t, names, false)
		calls := 0
		e := InspectArchive(context.Background(), f, "zip", DefaultLimits, func(Entry) error { calls++; return nil })
		if e == nil || calls != 0 {
			t.Fatalf("unsafe archive admitted: %v %v %d", names, e, calls)
		}
	}
	f := archiveFixture(t, []string{"link"}, true)
	if e := InspectArchive(context.Background(), f, "zip", DefaultLimits, func(Entry) error { return nil }); e == nil {
		t.Fatal("symlink admitted")
	}
}
func TestSourceArchiveLimitNegative(t *testing.T) {
	f := archiveFixture(t, []string{"one", "two"}, false)
	calls := 0
	e := InspectArchive(context.Background(), f, "zip", Limits{1, 100, 100}, func(Entry) error { calls++; return nil })
	if e == nil || calls != 0 {
		t.Fatal("truncated capacity accepted")
	}
	f2, e := os.CreateTemp("", "source-tar-")
	if e != nil {
		t.Fatal(e)
	}
	defer os.Remove(f2.Name())
	defer f2.Close()
	tw := tar.NewWriter(f2)
	_ = tw.WriteHeader(&tar.Header{Name: "device", Typeflag: tar.TypeChar})
	_ = tw.Close()
	if e = InspectArchive(context.Background(), f2, "tar", DefaultLimits, func(Entry) error { return nil }); e == nil {
		t.Fatal("device accepted")
	}
}
func TestSourceJSONPositive(t *testing.T) {
	n := mustParse(t, "records.json", "[{\"z\":1.2300,\"unknown\":{\"x\":[true,null,\"café\"]},\"a\":2}]", "json")
	r := n.Tables[0].Rows[0]
	v := r["value"].(map[string]any)
	equal(t, json.Number("1.2300"), v["z"])
	entries := r["source_json_tree"].(map[string]any)["entries"].([]any)
	equal(t, "z", entries[0].(map[string]any)["key"])
	equal(t, "a", entries[2].(map[string]any)["key"])
	n = mustParse(t, "rows.jsonl", "{\"x\":1}\n{\"x\":2}\n", "jsonl")
	equal(t, 2, len(n.Tables[0].Rows))
}
func TestSourceJSONNegative(t *testing.T) {
	for _, s := range []string{"{\"x\":", "{} {}"} {
		if _, e := Parse("bad.json", []byte(s), Options{Format: "json"}); e == nil {
			t.Fatal("invalid JSON accepted")
		}
	}
	n := mustParse(t, "dup.json", "{\"x\":1,\"x\":2}", "json")
	equal(t, true, n.Tables[0].Rows[0]["ambiguous_keys"])
	equal(t, 2, len(n.Tables[0].Rows[0]["source_json_tree"].(map[string]any)["entries"].([]any)))
}
func TestSourceDelimitedPositive(t *testing.T) {
	delimiter := ","
	n, e := Parse("a.csv", []byte("id,x,x\nα,\"line\nnext\",7\n"), Options{Format: "csv", Header: true, Delimiter: &delimiter})
	if e != nil {
		t.Fatal(e)
	}
	equal(t, []string{"id", "x", "x"}, n.Tables[0].Rows[0]["header"])
	equal(t, []string{"α", "line\nnext", "7"}, n.Tables[0].Rows[0]["cells"])
	n = mustParse(t, "a.tsv", "id\tvalue\n1\tword", "tsv")
	equal(t, 2, len(n.Tables[0].Rows))
}
func TestSourceDelimitedNegative(t *testing.T) {
	if _, e := Parse("a.csv", []byte("a,b\n1\n"), Options{Format: "csv", Header: true}); e == nil {
		t.Fatal("bad width accepted")
	}
	if _, e := Parse("a.csv", []byte{0xff}, Options{Format: "csv", Encoding: "utf-8"}); e == nil {
		t.Fatal("invalid encoding accepted")
	}
	if _, e := decodeText([]byte{0, 0xd8}, "utf-16le"); e == nil {
		t.Fatal("unpaired surrogate accepted")
	}
}
func TestSourceXMLPositive(t *testing.T) {
	n, e := Parse("a.xml", []byte(`<r xmlns="urn:x" k="v">before<c z="unknown">inside</c>after</r>`), Options{Format: "xml", Selector: "/{urn:x}r"})
	if e != nil {
		t.Fatal(e)
	}
	r := n.Tables[0].Rows[0]
	equal(t, "{urn:x}r", r["name"])
	equal(t, "before", r["text"])
	child := children(r)[0]
	equal(t, "after", child["tail"])
	equal(t, "unknown", attrs(child)[0]["value"])
}
func TestSourceXMLNegative(t *testing.T) {
	for _, s := range []string{`<!DOCTYPE r SYSTEM "https://invalid.example/secret"><r/>`, `<r>&unknown;</r>`, `<r>`} {
		if _, e := Parse("bad.xml", []byte(s), Options{Format: "xml"}); e == nil {
			t.Fatal("unsafe/malformed XML admitted")
		}
	}
}
func workbookBytes(t *testing.T, external bool) []byte {
	t.Helper()
	var b bytes.Buffer
	z := zip.NewWriter(&b)
	rel := `<Relationship Id="r1" Target="worksheets/sheet1.xml"/>`
	if external {
		rel = `<Relationship Id="r1" Target="https://invalid.example/secret" TargetMode="External"/>`
	}
	files := map[string]string{"xl/workbook.xml": `<workbook xmlns:r="urn:r"><sheets><sheet name="Hidden" state="hidden" r:id="r1"/></sheets></workbook>`, "xl/_rels/workbook.xml.rels": `<Relationships>` + rel + `</Relationships>`, "xl/worksheets/sheet1.xml": `<worksheet><sheetData><row r="1" custom="retained"><unknown arbitrary="yes">opaque</unknown><c r="A1" t="inlineStr"><is><t>native</t></is></c><c r="B1"><f>1+2</f><v>3</v></c><c r="C1" t="inlineStr"><is><t>=DANGEROUS()</t></is></c></row></sheetData></worksheet>`}
	for _, name := range sortedKeys(files) {
		w, _ := z.Create(name)
		_, _ = io.WriteString(w, files[name])
	}
	if e := z.Close(); e != nil {
		t.Fatal(e)
	}
	return b.Bytes()
}
func TestSourceWorkbookPositive(t *testing.T) {
	n, e := Parse("a.xlsx", workbookBytes(t, false), Options{Format: "xlsx", Selector: "records"})
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "Hidden", n.Tables[0].Name)
	r := n.Tables[0].Rows[0]
	equal(t, "hidden", r["sheet_state"])
	tree := r["native_xml_row"].(Row)
	equal(t, "retained", xmlAttribute(tree, "custom"))
	equal(t, "opaque", xmlText(xmlChild(tree, "unknown")))
	cells := r["cells"].([]any)
	equal(t, "native", cells[0].(map[string]any)["value"])
	equal(t, "1+2", *cells[1].(map[string]any)["formula"].(*string))
	equal(t, "3", cells[1].(map[string]any)["cached_value"])
	equal(t, "=DANGEROUS()", cells[2].(map[string]any)["value"])
}
func TestSourceWorkbookNegative(t *testing.T) {
	if _, e := Parse("a.xlsx", workbookBytes(t, true), Options{Format: "xlsx"}); e == nil {
		t.Fatal("external workbook relation accepted")
	}
	if _, e := Parse("a.xlsx", []byte("bad"), Options{Format: "xlsx"}); e == nil {
		t.Fatal("bad workbook accepted")
	}
}
func TestSourceM2Positive(t *testing.T) {
	n := mustParse(t, "train.m2", "S café go home\nA 1 2|||R:VERB:SVA|||goes|||REQUIRED|||-NONE-|||0\nA 1 2|||R:VERB:TENSE|||went|||REQUIRED|||-NONE-|||1\n\nS All fine\nA -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n", "m2")
	equal(t, 2, len(n.Tables[0].Rows))
	equal(t, 3, len(n.Tables[1].Rows))
	equal(t, []int{5, 7}, n.Tables[1].Rows[0]["codepoint_span"])
	equal(t, true, n.Tables[1].Rows[2]["noop"])
	views := CorrectionViews(n.Tables[0].Rows[0])
	equal(t, "café goes home", views["0"].(map[string]any)["text"])
	equal(t, "café went home", views["1"].(map[string]any)["text"])
}
func TestSourceM2Negative(t *testing.T) {
	n := mustParse(t, "bad.m2", "S a b\nA -1 0|||noop||||||REQUIRED|||-NONE-|||0\nA 0 3|||R:NOUN|||c|||REQUIRED|||-NONE-|||0\n", "m2")
	equal(t, 2, len(n.Issues))
	equal(t, true, n.Tables[0].Rows[0]["invalid"])
	n = mustParse(t, "overlap.m2", "S a b\nA 0 1|||R:NOUN|||x|||REQUIRED|||-NONE-|||0\nA 0 0|||M:DET|||the|||REQUIRED|||-NONE-|||0\n", "m2")
	equal(t, "ambiguous_native_edit_set", CorrectionViews(n.Tables[0].Rows[0])["0"].(map[string]any)["status"])
}

const gridLong = `File type = "ooTextFile"
Object class = "TextGrid"
xmin = 0
xmax = 1
tiers? <exists>
size = 1
item []:
 item [1]:
  class = "IntervalTier"
  name = "phones"
  xmin = 0
  xmax = 1
  intervals: size = 1
  intervals [1]:
   xmin = 0.1250
   xmax = 0.50
   text = "T,D,s"
`

func TestSourceTextGridPositive(t *testing.T) {
	n := mustParse(t, "annotation/a.TextGrid", gridLong, "textgrid")
	equal(t, "0.1250", n.Tables[0].Rows[0]["start_seconds"])
	equal(t, "T,D,s", n.Tables[0].Rows[0]["label"])
	short := "\"ooTextFile\"\n\"TextGrid\"\n0\n1\n<exists>\n1\n\"IntervalTier\"\n\"words\"\n0\n1\n1\n0\n1\n\"say \"\"hello\"\"\"\n"
	n = mustParse(t, "a.TextGrid", short, "textgrid")
	equal(t, `say "hello"`, n.Tables[0].Rows[0]["label"])
	p, e := PhoneLabel("T,err,s")
	if e != nil {
		t.Fatal(e)
	}
	equal(t, nil, p["perceived"])
}
func TestSourceTextGridNegative(t *testing.T) {
	n := mustParse(t, "bad.TextGrid", strings.Replace(gridLong, "xmax = 0.50", "xmax = 0.10", 1), "textgrid")
	equal(t, 1, len(n.Issues))
	if _, e := PhoneLabel("T,D,d"); e == nil {
		t.Fatal("invalid manual deletion admitted")
	}
	if _, e := Parse("bad.TextGrid", []byte(`"unterminated`), Options{Format: "textgrid"}); e == nil {
		t.Fatal("bad grid accepted")
	}
}
func TestSourceKaldiPositive(t *testing.T) {
	n := mustParse(t, "train/text", "u1  KEEP  spacing\nu2\tother\n", "kaldi")
	equal(t, "KEEP  spacing", n.Tables[0].Rows[0]["value"])
	n = mustParse(t, "train/wav.scp", "u1 cat secret |\n", "kaldi")
	equal(t, "cat secret |", n.Tables[0].Rows[0]["value"])
}
func TestSourceKaldiNegative(t *testing.T) {
	n := mustParse(t, "utt2spk", "u1 s1 s2\nu2 s1\nu2 s3\n", "kaldi")
	equal(t, 2, len(n.Issues))
	equal(t, true, n.Tables[0].Rows[0]["invalid"])
	equal(t, true, n.Tables[0].Rows[2]["invalid"])
}
func programFixture() Program {
	return Program{Source: "MOODRICK-DATA", Release: "r1", Manifest: strings.Repeat("a", 64), Record: "r", Identity: Locator{"r", "/value/id"}, Origin: "zero_based_half_open", Rate: 16000, Joins: []Join{{"r", "/value/id", "a", "/value/record", "many", true}}, Projections: []Projection{{Locator{"r", "/value/text"}, "/corpus_record/text", "identity", nil, true}, {Locator{"r", "/value/score"}, "/raw_metadata/score", "decimal", nil, false}}, Repeated: []Repeated{{"a", "/raw_metadata/annotations", []Projection{{Locator{"a", "/value/label"}, "/label", "identity", nil, true}}}}}
}
func mappingTables() map[string][]Row {
	return map[string][]Row{"r": {{"member": "a.jsonl", "value": map[string]any{"id": "Case", "text": "A café opens.", "score": "0.12500"}}}, "a": {{"member": "labels.jsonl", "value": map[string]any{"record": "Case", "label": "native-one"}}, {"member": "labels.jsonl", "value": map[string]any{"record": "Case", "label": "native-two"}}}}
}
func TestSourceMappingPositive(t *testing.T) {
	out, e := Project(programFixture(), mappingTables())
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "mapped", out[0].Status)
	v, _ := Pointer(out[0].Value, "/raw_metadata/annotations")
	equal(t, 2, len(v.([]any)))
	v, _ = Pointer(out[0].Value, "/raw_metadata/score")
	equal(t, json.Number("0.12500"), v)
	equal(t, "A café opens.", out[0].Value["corpus_record"].(map[string]any)["text"])
}
func TestSourceMappingNegative(t *testing.T) {
	p := programFixture()
	p.Joins[0].Cardinality = "one"
	out, e := Project(p, mappingTables())
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "unmapped", out[0].Status)
	p = programFixture()
	p.Projections = append(p.Projections, Projection{Locator{"a", "/value/label"}, "/raw_metadata/one", "identity", nil, true})
	out, e = Project(p, mappingTables())
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "unmapped", out[0].Status)
	p = programFixture()
	p.Projections = append(p.Projections, p.Projections[0])
	out, e = Project(p, mappingTables())
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "unmapped", out[0].Status)
	tables := mappingTables()
	tables["a"][0]["value"].(map[string]any)["record"] = "case"
	tables["a"] = tables["a"][:1]
	out, e = Project(programFixture(), tables)
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "unmapped", out[0].Status)
}
func TestSourceSpanPositive(t *testing.T) {
	p := Program{Origin: "one_based_inclusive", Rate: 16000}
	v, e := Convert([]any{json.Number("2"), json.Number("2")}, "token_span", p, Row{"text": "A café opens"})
	if e != nil {
		t.Fatal(e)
	}
	equal(t, []int{2, 6}, v)
	v, e = Convert("0.00003125", "seconds_to_samples", p, nil)
	if e != nil {
		t.Fatal(e)
	}
	equal(t, json.Number("1"), v)
	v, e = Convert("99999999999999999999999.0000", "decimal", p, nil)
	if e != nil {
		t.Fatal(e)
	}
	equal(t, json.Number("99999999999999999999999.0000"), v)
}
func TestSourceSpanNegative(t *testing.T) {
	for _, x := range []struct {
		v any
		k string
	}{{"1.5", "integer"}, {"-1", "seconds_to_samples"}, {"1e-3", "decimal"}, {[]any{json.Number("0"), json.Number("9")}, "codepoint_span"}, {[]any{json.Number("3"), json.Number("2")}, "token_span"}} {
		if _, e := Convert(x.v, x.k, Program{Rate: 16000, Origin: "zero_based_half_open"}, Row{"text": "abc"}); e == nil {
			t.Fatalf("invalid %v %s accepted", x.v, x.k)
		}
	}
}
func TestSourceIdentityPositive(t *testing.T) {
	a, e := Project(programFixture(), mappingTables())
	if e != nil {
		t.Fatal(e)
	}
	b, e := Project(programFixture(), mappingTables())
	if e != nil {
		t.Fatal(e)
	}
	equal(t, a[0].ID, b[0].ID)
	tables := mappingTables()
	tables["r"] = append(tables["r"], Row{"member": "b.jsonl", "value": tables["r"][0]["value"]})
	b, e = Project(programFixture(), tables)
	if e != nil {
		t.Fatal(e)
	}
	if b[0].ID == b[1].ID {
		t.Fatal("member identities merged")
	}
}
func TestSourceIdentityNegative(t *testing.T) {
	p := programFixture()
	p.Identity.Table = "a"
	if _, e := Project(p, mappingTables()); e == nil {
		t.Fatal("joined identity silently substituted")
	}
	p = programFixture()
	p.Projections[0].From.Table = "unrelated"
	if _, e := Project(p, mappingTables()); e == nil {
		t.Fatal("unconnected source data admitted")
	}
}
func TestSourceSourcesPositive(t *testing.T) {
	equal(t, 11, len(IDs))
	for _, id := range []string{"EFCAMDAT-R2", "EFCAMDAT-SHATZ2020", "EFCAMDAT-OKSUZ2025", "MOODRICK-DATA", "NIR-DATA"} {
		equal(t, true, Known(id))
	}
	equal(t, false, Known("ICNALE"))
}
func TestSourceSourcesNegative(t *testing.T) {
	for _, id := range []string{"MOODRICK-NIR", "EFCAMDAT", "oksuz-public-companion"} {
		if Known(id) {
			t.Fatal("source substitution accepted")
		}
	}
}
func TestSourcePublicPositive(t *testing.T) {
	o, name, ok := NativePlan("FCE-2.1", Member{Path: "fce/json/fce.train.json"})
	equal(t, true, ok)
	equal(t, "jsonl", o.Format)
	equal(t, "essays", name)
	p, e := PhoneLabel("sil,D,a")
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "a", p["operation"])
	p, e = PhoneLabel("T*,D,s")
	if e != nil {
		t.Fatal(e)
	}
	equal(t, true, p["approximate"])
}
func TestSourcePublicNegative(t *testing.T) {
	m := NativeRecord("WILOCNESS-2.1", "r", "test.orig", "withheld", 0, Row{"text": "I go.", "row": 0})
	v, _ := Pointer(m.Value, "/raw_metadata/labels_state")
	equal(t, "labels_not_supplied", v)
	if _, e := PhoneLabel("T,D,unknown"); e == nil {
		t.Fatal("invented phone operation")
	}
}
func TestSourceCompletenessPositive(t *testing.T) {
	members := []Member{{Path: "fce/train.m2"}, {Path: "fce/dev.m2"}, {Path: "fce/test.m2"}, {Path: "licence.txt"}}
	equal(t, 0, len(MissingNative("FCE-2.1", members)))
}
func TestSourceCompletenessNegative(t *testing.T) {
	missing := MissingNative("EFCAMDAT-OKSUZ2025", []Member{{Path: "ef2_def_analyse.csv"}, {Path: "ef2_indef_analyse.csv"}})
	equal(t, []string{"complete original workbook", "native dictionary"}, missing)
	if len(MissingNative("L2-ARCTIC", []Member{{Path: "ABA/wav/a.wav"}})) == 0 {
		t.Fatal("single speaker accepted as full source")
	}
}
func remoteFixture(endpoint string) RemoteSpec {
	return RemoteSpec{Endpoint: endpoint, Method: "GET", Query: map[string]string{}, Headers: map[string]string{}, Body: map[string]any{}, CursorField: "cursor", CursorLocation: "query", RecordsPointer: "/records", NextPointer: "/next", EndPointer: "/done", EndValue: true, DatasetVersion: "fixture-v1", CountUnit: "native_records"}
}
func TestSourceRemotePositive(t *testing.T) {
	var calls atomic.Int32
	server := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if calls.Add(1) == 1 {
			w.WriteHeader(503)
			return
		}
		equal(t, "", r.URL.Query().Get("cursor"))
		_, _ = io.WriteString(w, `{"records":[{"id":"a","unknown":17}],"next":null,"done":true}`)
	}))
	defer server.Close()
	p, e := FetchPage(context.Background(), server.Client(), remoteFixture(server.URL), []string{"127.0.0.1"}, nil, "")
	if e != nil {
		t.Fatal(e)
	}
	equal(t, 2, int(calls.Load()))
	equal(t, true, p.End)
	equal(t, nil, p.Next)
	equal(t, 1, len(p.Records))
}
func TestSourceRemoteNegative(t *testing.T) {
	var calls atomic.Int32
	server := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls.Add(1)
		_, _ = io.WriteString(w, `{"records":[],"something":"not EOF"}`)
	}))
	defer server.Close()
	spec := remoteFixture(server.URL)
	if _, e := FetchPage(context.Background(), server.Client(), spec, []string{"127.0.0.1"}, nil, ""); e == nil {
		t.Fatal("missing marker interpreted as completion")
	}
	if e := ValidateRemote(spec, []string{"wrong.example"}); e == nil {
		t.Fatal("wrong host accepted")
	}
	spec.AuthHeader = "Authorization"
	if _, e := FetchPage(context.Background(), server.Client(), spec, []string{"127.0.0.1"}, nil, ""); e == nil {
		t.Fatal("missing credential accepted")
	}
	equal(t, 1, int(calls.Load()))
	ctx, cancel := context.WithTimeout(context.Background(), time.Nanosecond)
	defer cancel()
	if _, e := FetchPage(ctx, server.Client(), remoteFixture(server.URL), []string{"127.0.0.1"}, nil, ""); e == nil {
		t.Fatal("cancelled request succeeded")
	}
}

func TestSourceTextGridMultilinePositive(t *testing.T) {
	text := strings.Replace(gridLong, "T,D,s", "θ,t,s\n", 1)
	n := mustParse(t, "native-shape.TextGrid", text, "textgrid")
	equal(t, "θ,t,s\n", n.Tables[0].Rows[0]["label"])
	phone, e := PhoneLabel(n.Tables[0].Rows[0]["label"].(string))
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "s", phone["operation"])
}

func TestSourcePhoneCasePositive(t *testing.T) {
	for _, label := range []string{"R,L,S", "D,SIL,D", "sil,D,a"} {
		p, e := PhoneLabel(label)
		if e != nil {
			t.Fatal(e)
		}
		if p["operation"] == "unchanged" {
			t.Fatal("actual tuple ignored")
		}
		equal(t, label, p["raw"])
	}
	p, e := PhoneLabel("S")
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "unchanged", p["operation"])
	p, e = PhoneLabel("D")
	if e != nil {
		t.Fatal(e)
	}
	equal(t, "unchanged", p["operation"])
}
func TestSourcePhoneCaseNegative(t *testing.T) {
	if _, e := PhoneLabel("D,SIL,word"); e == nil {
		t.Fatal("unknown operation accepted")
	}
	p, e := PhoneLabel("DH,ERR,S")
	if e != nil {
		t.Fatal(e)
	}
	equal(t, nil, p["perceived"])
}

func TestSourceDecimalSyntaxPositive(t *testing.T) {
	for _, pair := range [][2]string{{"+01.2300", "1.2300"}, {".5", "0.5"}, {"-0", "0"}} {
		v, e := Convert(pair[0], "decimal", Program{}, nil)
		if e != nil {
			t.Fatal(e)
		}
		equal(t, json.Number(pair[1]), v)
		if _, e = json.Marshal(v); e != nil {
			t.Fatal("conversion emitted invalid JSON")
		}
	}
}
func TestSourceDecimalSyntaxNegative(t *testing.T) {
	for _, s := range []string{"0x10", "1/2", "1e3", "NaN", " 1"} {
		if _, e := Convert(s, "decimal", Program{}, nil); e == nil {
			t.Fatal("non-decimal source representation accepted")
		}
	}
}

func TestSourceEncodingPositive(t *testing.T) {
	for _, encoding := range []string{"utf-16le", "utf-16be"} {
		var b bytes.Buffer
		for _, u := range []uint16{0xfeff, 'i', 'd', ',', 't', 'e', 'x', 't', '\n', '1', ',', 0xd83c, 0xdf4a, '\n'} {
			if encoding == "utf-16le" {
				b.WriteByte(byte(u))
				b.WriteByte(byte(u >> 8))
			} else {
				b.WriteByte(byte(u >> 8))
				b.WriteByte(byte(u))
			}
		}
		var rows []Row
		e := Walk(context.Background(), "native.csv", &b, Options{Format: "csv", Encoding: encoding, Header: true}, func(_ string, r Row) error { rows = append(rows, r); return nil })
		if e != nil {
			t.Fatal(e)
		}
		equal(t, "🍊", rows[0]["cells"].([]string)[1])
	}
	text := strings.Repeat("a", 32767) + "é\n"
	reader, _ := textReader(strings.NewReader(text), "utf-8")
	out, e := io.ReadAll(reader)
	if e != nil {
		t.Fatal(e)
	}
	equal(t, text, string(out))
}
func TestSourceEncodingNegative(t *testing.T) {
	for _, c := range []struct {
		enc string
		b   []byte
	}{{"utf-8", []byte{'x', 0xff}}, {"utf-16le", []byte{1}}, {"utf-16be", []byte{0xd8, 0}}, {"utf-16le", []byte{0, 0xdc}}} {
		e := Walk(context.Background(), "bad.csv", bytes.NewReader(c.b), Options{Format: "csv", Encoding: c.enc}, func(_ string, _ Row) error { return nil })
		if e == nil {
			t.Fatalf("invalid native encoding accepted%v", c)
		}
	}
}
func TestSourceLearnerGroupPositive(t *testing.T) {
	equal(t, StableID("efcamdat-learner", "actual-r2-id"), learnerGroup("EFCAMDAT-SHATZ2020", "actual-r2-id"))
	equal(t, learnerGroup("EFCAMDAT-R2", "actual-r2-id"), learnerGroup("EFCAMDAT-OKSUZ2025", "actual-r2-id"))
}
func TestSourceLearnerGroupNegative(t *testing.T) {
	if learnerGroup("MOODRICK-DATA", "17") == learnerGroup("NIR-DATA", "17") {
		t.Fatal("unrelated native learner IDs merged")
	}
}
