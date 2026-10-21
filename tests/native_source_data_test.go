package source

// These tests read complete previously acquired public packages. Literal counts
// come from the independent 2026-10-09 native inventory, not this parser's output.
// They do not certify unavailable private releases or publish source records.
import (
	"archive/tar"
	"archive/zip"
	"compress/gzip"
	"context"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func acquiredRoot(t *testing.T) string {
	t.Helper()
	root := os.Getenv("TANGERINE_CORPUS_DATA")
	if root == "" {
		t.Fatal("complete acquired corpus mount required")
	}
	return root
}
func acquiredTar(t *testing.T, name string, visit func(*tar.Header, io.Reader)) {
	t.Helper()
	f, e := os.Open(name)
	if e != nil {
		t.Fatal(e)
	}
	defer f.Close()
	gz, e := gzip.NewReader(f)
	if e != nil {
		t.Fatal(e)
	}
	defer gz.Close()
	r := tar.NewReader(gz)
	for {
		h, e := r.Next()
		if e == io.EOF {
			return
		}
		if e != nil {
			t.Fatal(e)
		}
		if h.Typeflag == tar.TypeReg {
			visit(h, r)
		}
	}
}
func TestAcquiredSourceBEAPositive(t *testing.T) {
	root := acquiredRoot(t)
	expected := map[string]int{"fce.train.gold.bea19.m2": 28350, "fce.dev.gold.bea19.m2": 2191, "fce.test.gold.bea19.m2": 2695, "A.train.gold.bea19.m2": 10493, "B.train.gold.bea19.m2": 13032, "C.train.gold.bea19.m2": 10783, "ABC.train.gold.bea19.m2": 34308, "A.dev.gold.bea19.m2": 1037, "B.dev.gold.bea19.m2": 1290, "C.dev.gold.bea19.m2": 1069, "N.dev.gold.bea19.m2": 988, "ABCN.dev.gold.bea19.m2": 4384}
	observed := map[string]int{}
	essays, annotators, noop := 0, map[string]bool{}, 0
	for _, name := range []string{"fce_v2.1.bea19.tar.gz", "wi+locness_v2.1.bea19.tar.gz"} {
		id := "FCE-2.1"
		if strings.HasPrefix(name, "wi+") {
			id = "WILOCNESS-2.1"
		}
		acquiredTar(t, filepath.Join(root, "bea", name), func(h *tar.Header, r io.Reader) {
			o, _, ok := NativePlan(id, Member{Path: h.Name})
			if !ok {
				return
			}
			e := Walk(context.Background(), h.Name, r, o, func(table string, row Row) error {
				if row["invalid"] == true {
					t.Fatalf("invalid native %s %v", h.Name, row["sentence_index"])
				}
				if table == "sentences" && o.Format == "m2" {
					observed[filepath.Base(h.Name)]++
				}
				if table == "edits" {
					annotators[fmt.Sprint(row["annotator"])] = true
					if row["noop"] == true {
						noop++
					}
				}
				if o.Format == "jsonl" {
					essays++
					v, ok := row["value"].(map[string]any)
					if !ok || v["text"] == nil || v["id"] == nil {
						t.Fatal("native essay fields lost")
					}
				}
				return nil
			})
			if e != nil {
				t.Fatal(e)
			}
		})
	}
	for name, count := range expected {
		if observed[name] != count {
			t.Fatalf("%s expected%d got%d", name, count, observed[name])
		}
	}
	if len(observed) != 12 || essays == 0 || len(annotators) < 1 || noop == 0 {
		t.Fatal("native representation omitted")
	}
	t.Logf("full12M2 views=%v; all native JSON-lines essays=%d; noops=%d", observed, essays, noop)
}
func TestAcquiredSourceSpeechPositive(t *testing.T) {
	root := acquiredRoot(t)
	scores, details, train, test := 0, 0, 0, 0
	rates := map[string]bool{}
	selected := map[string]bool{}
	waves := map[string]bool{}
	acquiredTar(t, filepath.Join(root, "speechocean762", "owner-613968e3b0b789fc33936fb5eba1973176ba7d11.tar.gz"), func(h *tar.Header, r io.Reader) {
		if strings.HasSuffix(strings.ToLower(h.Name), ".wav") {
			waves[strings.TrimSuffix(filepath.Base(h.Name), filepath.Ext(h.Name))] = true
			return
		}
		o, name, ok := NativePlan("SPEECHOCEAN762", Member{Path: h.Name})
		if !ok {
			return
		}
		e := Walk(context.Background(), h.Name, r, o, func(_ string, row Row) error {
			switch name {
			case "scores.json":
				scores++
				selected[row["key"].(string)] = true
				v := row["value"].(map[string]any)
				if v["words"] == nil || v["accuracy"] == nil || v["completeness"] == nil {
					t.Fatal("aggregate native fields lost")
				}
			case "scores-detail.json":
				details++
				v := row["value"].(map[string]any)
				for _, key := range []string{"accuracy", "total", "fluency", "prosodic", "completeness"} {
					a, ok := v[key].([]any)
					if !ok || len(a) != 5 {
						t.Fatalf("five source raters lost %s", key)
					}
				}
				rates["individual-completeness-native-scale-retained"] = true
			case "text":
				if strings.Contains(h.Name, "/train/") {
					train++
				} else if strings.Contains(h.Name, "/test/") {
					test++
				}
			}
			return nil
		})
		if e != nil {
			t.Fatal(e)
		}
	})
	if scores != 5000 || details != 5000 || train != 2500 || test != 2500 || len(waves) != 5245 || len(rates) != 1 {
		t.Fatalf("native totals scores%d details%d train%d test%d wave%d", scores, details, train, test, len(waves))
	}
	for id := range selected {
		if !waves[id] {
			t.Fatal("selected native audio missing")
		}
	}
	t.Log("Complete5000 aggregate/five-rater records;2500+2500 split texts;5245wave representations retained with245unselected.")
}
func TestAcquiredSourceL2Positive(t *testing.T) {
	root := acquiredRoot(t)
	names, e := filepath.Glob(filepath.Join(root, "l2-arctic/mirror/*.zip"))
	if e != nil {
		t.Fatal(e)
	}
	if len(names) != 25 {
		t.Fatalf("need25complete acquired archives got%d", len(names))
	}
	readWAV, manual, suitcase := 0, 0, 0
	readOps := map[string]int{"s": 0, "d": 0, "a": 0}
	suitOps := map[string]int{"s": 0, "d": 0, "a": 0}
	unnamed := 0
	for _, name := range names {
		z, e := zip.OpenReader(name)
		if e != nil {
			t.Fatal(e)
		}
		isSuit := strings.Contains(name, "suitcase")
		for _, file := range z.File {
			if strings.HasSuffix(strings.ToLower(file.Name), ".wav") {
				if isSuit {
					suitcase++
				} else {
					readWAV++
				}
			}
			if !strings.Contains(strings.ToLower(file.Name), "annotation/") || !strings.HasSuffix(strings.ToLower(file.Name), ".textgrid") {
				continue
			}
			if !isSuit {
				manual++
			}
			r, e := file.Open()
			if e != nil {
				t.Fatal(e)
			}
			e = Walk(context.Background(), file.Name, r, Options{Format: "textgrid", Encoding: "utf-8"}, func(table string, row Row) error {
				if table != "intervals" {
					return nil
				}
				if row["tier"] == "" {
					unnamed++
				}
				if row["tier"] != "phones" {
					return nil
				}
				parts := strings.Split(fmt.Sprint(row["label"]), ",")
				if len(parts) == 3 {
					operation := strings.ToLower(strings.TrimSpace(parts[2]))
					counts := readOps
					if isSuit {
						counts = suitOps
					}
					if _, ok := counts[operation]; ok {
						counts[operation]++
					}
				}
				return nil
			})
			r.Close()
			if e != nil {
				t.Fatalf("%s:%v", file.Name, e)
			}
		}
		z.Close()
	}
	if readWAV != 26867 || manual != 3599 || suitcase != 22 {
		t.Fatalf("read%d manual%d suitcase%d", readWAV, manual, suitcase)
	}
	equal(t, map[string]int{"s": 14098, "d": 3420, "a": 1092}, readOps)
	equal(t, map[string]int{"s": 1673, "d": 456, "a": 90}, suitOps)
	if unnamed == 0 {
		t.Fatal("actual unnamed ancillary tier omitted")
	}
	t.Logf("Pinned mirror actualread=%v suitcase=%v unnamedintervals%d; official equivalence remains unknown", readOps, suitOps, unnamed)
}
func TestAcquiredSourceNegative(t *testing.T) {
	root := acquiredRoot(t)
	sentences := 0
	withheldGold := false
	acquiredTar(t, filepath.Join(root, "bea/wi+locness_v2.1.bea19.tar.gz"), func(h *tar.Header, r io.Reader) {
		if strings.Contains(h.Name, "test") && strings.HasSuffix(h.Name, ".m2") {
			withheldGold = true
		}
		if strings.HasSuffix(h.Name, "ABCN.test.bea19.orig") {
			e := Walk(context.Background(), h.Name, r, Options{Format: "lines"}, func(_ string, row Row) error {
				m := NativeRecord("WILOCNESS-2.1", "native-v2.1", h.Name, "withheld", sentences, row)
				value, _ := Pointer(m.Value, "/raw_metadata/labels_state")
				if value != "labels_not_supplied" {
					t.Fatal("fabricated heldout label")
				}
				sentences++
				return nil
			})
			if e != nil {
				t.Fatal(e)
			}
		}
	})
	if sentences != 4477 || withheldGold {
		t.Fatal("withheld gold invented or originals omitted")
	}
	missing := MissingNative("EFCAMDAT-OKSUZ2025", []Member{{Path: "ef2_def_analyse.csv"}, {Path: "ef2_indef_analyse.csv"}})
	if len(missing) == 0 {
		t.Fatal("public companion substituted for restricted original")
	}
}
