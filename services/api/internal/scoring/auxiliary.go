package scoring

import (
	"math/big"
	"strings"
)

type Observation struct {
	Status   string   `json:"status"`
	Exact    *Exact   `json:"exact"`
	Decimal  *string  `json:"decimal_value"`
	Unit     string   `json:"unit"`
	Method   string   `json:"method_id"`
	Evidence []string `json:"evidence_ids"`
	Reason   *string  `json:"reason_code"`
	Display  *string  `json:"display"`
}

// A population is supplied only by the owner that actually observed it.
// In particular, generated speech is not a measurement of the listener's speech.
type Population struct {
	Numerator, Denominator *big.Rat
	Method                 string
	Evidence               []string
}

var AuxiliaryUnits = map[string]string{
	"annotation.agreement": "ratio", "annotation.cohen_kappa": "ratio", "verification.wer": "ratio",
	"audio.speech_rate_wpm": "words_per_minute", "audio.articulation_rate_wpm": "words_per_minute", "audio.pause_ratio": "ratio", "audio.disfluency_density": "events_per_100_words",
	"evaluation.coverage": "ratio", "evaluation.exact_mapping_agreement": "ratio", "telemetry.elapsed_seconds": "seconds", "telemetry.replay_count": "count",
	"teacher.talk_time": "ratio", "teacher.pronunciation": "ratio", "teacher.classroom_management": "ratio", "teacher.engagement": "ratio",
}

func Auxiliary(populations map[string]Population) (map[string]Observation, error) {
	out := map[string]Observation{}
	for name, unit := range AuxiliaryUnits {
		reason := "NOT_RUN"
		status := "not_run"
		if strings.HasPrefix(name, "teacher.") {
			reason = "not_observable_in_this_mode"
			status = "not_observable"
		}
		o := Observation{Status: status, Unit: unit, Method: "listening-v2", Reason: &reason, Evidence: []string{}}
		if p, ok := populations[name]; ok && !strings.HasPrefix(name, "teacher.") {
			o.Method = p.Method
			o.Evidence = p.Evidence
			if p.Denominator.Sign() == 0 {
				reason = "no_opportunities"
				o.Status = "not_applicable"
			} else {
				value := new(big.Rat).Quo(p.Numerator, p.Denominator)
				var err error
				o.Exact, err = exact(value)
				if err != nil {
					return nil, err
				}
				display := Display(value, false)
				if unit == "ratio" {
					display = Display(value, true) + "%"
				}
				if unit == "count" {
					display = value.RatString()
				}
				o.Display = &display
				o.Status = "observed"
				o.Reason = nil
			}
		}
		out[name] = o
	}
	return out, nil
}

// Agreement excludes unpaired records, and uses the two actual marginal label
// populations before any adjudication. Empty strings are absent, not labels.
func Agreement(pairs [][2]string) (Population, Population) {
	a, b := map[string]int64{}, map[string]int64{}
	n, same := int64(0), int64(0)
	for _, p := range pairs {
		if p[0] == "" || p[1] == "" {
			continue
		}
		n++
		a[p[0]]++
		b[p[1]]++
		if p[0] == p[1] {
			same++
		}
	}
	raw := Population{fraction(same, 1), fraction(n, 1), "paired-nominal-v1", []string{}}
	k := Population{new(big.Rat), new(big.Rat), "cohen-kappa-v1", []string{}}
	if n == 0 {
		return raw, k
	}
	pe := new(big.Rat)
	for label, count := range a {
		pe.Add(pe, fraction(count*b[label], n*n))
	}
	k.Numerator = new(big.Rat).Sub(fraction(same, n), pe)
	k.Denominator = new(big.Rat).Sub(fraction(1, 1), pe)
	return raw, k
}

// WordError counts unconstrained unit-cost edit distance over already normalized
// word sequences. Token normalization belongs to the declared observation method.
func WordError(reference, heard []string) Population {
	prev := make([]int64, len(heard)+1)
	for j := range prev {
		prev[j] = int64(j)
	}
	for i, a := range reference {
		row := make([]int64, len(heard)+1)
		row[0] = int64(i + 1)
		for j, b := range heard {
			cost := int64(0)
			if a != b {
				cost = 1
			}
			row[j+1] = min(prev[j+1]+1, row[j]+1, prev[j]+cost)
		}
		prev = row
	}
	return Population{fraction(prev[len(heard)], 1), fraction(int64(len(reference)), 1), "word-edit-distance-v1", []string{}}
}

// SpeechPopulations requires measured intervals supplied by the acoustic owner.
// Passing generated text length or intended pauses as observations is not valid.
func SpeechPopulations(words, spanMillis, activeMillis, silentMillis, disfluencies int64, method string, evidence []string) map[string]Population {
	return map[string]Population{
		"audio.speech_rate_wpm":       {fraction(60000*words, 1), fraction(spanMillis, 1), method, evidence},
		"audio.articulation_rate_wpm": {fraction(60000*words, 1), fraction(activeMillis, 1), method, evidence},
		"audio.pause_ratio":           {fraction(silentMillis, 1), fraction(spanMillis, 1), method, evidence},
		"audio.disfluency_density":    {fraction(100*disfluencies, 1), fraction(words, 1), method, evidence},
	}
}
