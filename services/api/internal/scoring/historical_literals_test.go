package scoring

// Literal constructed populations, not acquired annotations or measured speech.
import (
	"encoding/json"
	"fmt"
	"math/big"
	"os"
	"strings"
	"testing"
)

type historicalAuxiliary struct {
	CaseID string `json:"case_id"`
	Metric string `json:"metric"`
	Input  struct {
		Inputs        map[string]any `json:"inputs"`
		InputsMissing bool           `json:"inputs_missing"`
		Invented      int64          `json:"invented_value"`
	} `json:"input"`
	Expected struct {
		Exact *string `json:"exact"`
	} `json:"expected"`
}

func historicalAuxiliaryRows(t *testing.T) []historicalAuxiliary {
	t.Helper()
	raw, err := os.ReadFile("testdata/historical-auxiliary.json")
	if err != nil {
		t.Fatal(err)
	}
	var rows []historicalAuxiliary
	if err = json.Unmarshal(raw, &rows); err != nil || len(rows) != 52 {
		t.Fatal(err, len(rows))
	}
	return rows
}

func historicalNumber(m map[string]any, key string) int64 { return int64(m[key].(float64)) }

func historicalPopulation(row historicalAuxiliary) Population {
	x := row.Input.Inputs
	method, evidence := "constructed-historical-literal", []string{row.CaseID}
	pair := func(n, d string) Population {
		return Population{fraction(historicalNumber(x, n), 1), fraction(historicalNumber(x, d), 1), method, evidence}
	}
	switch row.Metric {
	case "annotation.agreement":
		var pairs [][2]string
		for n := int64(0); n < historicalNumber(x, "N"); n++ {
			b := "yes"
			if n >= historicalNumber(x, "agreements") {
				b = "no"
			}
			pairs = append(pairs, [2]string{"yes", b})
		}
		raw, _ := Agreement(pairs)
		return raw
	case "annotation.cohen_kappa":
		var pairs [][2]string
		for key, n := range x["confusion"].(map[string]any) {
			labels := strings.Split(key, "_")
			for i := 0; i < int(n.(float64)); i++ {
				pairs = append(pairs, [2]string{labels[0], labels[1]})
			}
		}
		_, k := Agreement(pairs)
		return k
	case "verification.wer":
		var reference, heard []string
		subs, del, ins := historicalNumber(x, "substitutions"), historicalNumber(x, "deletions"), historicalNumber(x, "insertions")
		for n := int64(0); n < historicalNumber(x, "reference_word_count"); n++ {
			word := fmt.Sprint("reference", n)
			reference = append(reference, word)
			if n < subs {
				heard = append(heard, fmt.Sprint("replacement", n))
			} else if n >= subs+del {
				heard = append(heard, word)
			}
		}
		for n := int64(0); n < ins; n++ {
			heard = append(heard, fmt.Sprint("inserted", n))
		}
		return WordError(reference, heard)
	case "evaluation.coverage":
		return pair("resolved_decisions", "eligible_decisions")
	case "evaluation.exact_mapping_agreement":
		return pair("identical_claim_to_unit_decisions", "eligible_gold_decisions")
	}
	if strings.HasPrefix(row.Metric, "audio.") {
		get := func(k string) int64 {
			if x[k] == nil {
				return 0
			}
			return historicalNumber(x, k)
		}
		return SpeechPopulations(get("spoken_token_count"), 1000*get("elapsed_speech_span_seconds"), 1000*get("active_speech_seconds"), 1000*get("internal_silent_seconds"), get("reviewed_disfluency_events"), method, evidence)[row.Metric]
	}
	return Population{big.NewRat(100, 1), big.NewRat(1, 1), "invented-not-observable", nil}
}

func TestHistoricalAuxiliaryPositive(t *testing.T) {
	seen := 0
	for _, row := range historicalAuxiliaryRows(t) {
		if !strings.HasSuffix(row.CaseID, ".POSITIVE") {
			continue
		}
		seen++
		t.Run(row.CaseID, func(t *testing.T) {
			out, err := Auxiliary(map[string]Population{row.Metric: historicalPopulation(row)})
			if err != nil {
				t.Fatal(err)
			}
			got := out[row.Metric]
			if row.Expected.Exact == nil {
				if got.Exact != nil || got.Status != "not_observable" {
					t.Fatal(got)
				}
			} else {
				want, _ := new(big.Rat).SetString(*row.Expected.Exact)
				if got.Exact == nil || got.Status != "observed" || got.Exact.Numerator != want.Num().String() || got.Exact.Denominator != want.Denom().String() {
					t.Fatal(row.CaseID, got, "want", *row.Expected.Exact)
				}
			}
			for name, observed := range out {
				if strings.HasPrefix(name, "teacher.") && (observed.Exact != nil || observed.Status != "not_observable") {
					t.Fatal(name, observed)
				}
			}
		})
	}
	if seen != 26 {
		t.Fatal(seen)
	}
}

func TestHistoricalAuxiliaryNegative(t *testing.T) {
	seen := 0
	for _, row := range historicalAuxiliaryRows(t) {
		if !strings.HasSuffix(row.CaseID, ".NEGATIVE") {
			continue
		}
		seen++
		t.Run(row.CaseID, func(t *testing.T) {
			if !row.Input.InputsMissing || row.Input.Invented != 100 {
				t.Fatal("wrong historical input", row.CaseID)
			}
			populations := map[string]Population{}
			if strings.HasPrefix(row.Metric, "teacher.") {
				populations[row.Metric] = historicalPopulation(row)
			}
			out, err := Auxiliary(populations)
			if err != nil {
				t.Fatal(err)
			}
			got := out[row.Metric]
			if got.Exact != nil || (got.Status != "not_run" && got.Status != "not_observable") {
				t.Fatal("unsupported invented observation accepted", got)
			}
		})
	}
	if seen != 26 {
		t.Fatal(seen)
	}
}
