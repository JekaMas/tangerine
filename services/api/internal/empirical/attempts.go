package empirical

import (
	"fmt"
	"math"
	"strconv"
)

type Attempt struct {
	ID      string  `json:"id"`
	Actor   string  `json:"participant_id"`
	Origin  string  `json:"origin"`
	Case    string  `json:"case_version_id"`
	Unit    *string `json:"unit_id"`
	Policy  string  `json:"scoring_policy_version"`
	First   bool    `json:"first_exposure"`
	Success *bool   `json:"success"`
	Before  *string `json:"followup_of"`
	Score   *string `json:"score_percent"`
}
type Difficulty struct {
	Trials    int64          `json:"trials"`
	Successes int64          `json:"successes"`
	Lower     *string        `json:"lower_bound"`
	Upper     *string        `json:"upper_bound"`
	Rating    string         `json:"rating"`
	Missing   *string        `json:"missing_reason"`
	Eligible  []string       `json:"eligible_teacher_answer_ids"`
	Excluded  map[string]int `json:"excluded"`
	Followup  Fraction       `json:"paired_success_change"`
}

func DifficultyReport(rows []Attempt) (Difficulty, error) {
	r := Difficulty{Rating: "unrated", Eligible: []string{}, Excluded: map[string]int{}, Followup: Unavailable("no_genuine_paired_followup")}
	seen := map[string]bool{}
	participants := map[string]bool{}
	var population string
	byID := map[string]Attempt{}
	for _, a := range rows {
		if a.ID == "" || seen[a.ID] {
			return r, fmt.Errorf("duplicate attempt")
		}
		seen[a.ID] = true
		byID[a.ID] = a
	}
	var paired, change int64
	for _, a := range rows {
		if a.Origin != "genuine_teacher" {
			r.Excluded["not_genuine_teacher"]++
			continue
		}
		if a.Actor == "" {
			r.Excluded["participant_unknown"]++
			continue
		}
		key := a.Case + "/" + a.Policy + "/"
		if a.Unit != nil {
			key += *a.Unit
		}
		if population == "" {
			population = key
		} else if key != population {
			return r, fmt.Errorf("different key/policy/unit population")
		}
		if a.Before != nil {
			b, ok := byID[*a.Before]
			if ok && b.ID != a.ID && b.Origin == "genuine_teacher" && b.Actor == a.Actor && b.Case == a.Case && b.Policy == a.Policy && a.Success != nil && b.Success != nil {
				paired++
				if *a.Success {
					change++
				}
				if *b.Success {
					change--
				}
			}
		}
		if !a.First {
			r.Excluded["not_first_exposure"]++
			continue
		}
		if participants[a.Actor] {
			r.Excluded["duplicate_participant_exposure"]++
			continue
		}
		participants[a.Actor] = true
		if a.Success == nil {
			r.Excluded["success_unknown"]++
			continue
		}
		r.Trials++
		if *a.Success {
			r.Successes++
		}
		r.Eligible = append(r.Eligible, a.ID)
	}
	if paired > 0 {
		r.Followup = Ratio(change, paired)
	}
	if r.Trials == 0 {
		s := "insufficient_population"
		r.Missing = &s
		return r, nil
	}
	n, p, z := float64(r.Trials), float64(r.Successes)/float64(r.Trials), 1.959963984540054
	den := 1 + z*z/n
	center := (p + z*z/(2*n)) / den
	margin := z * math.Sqrt(p*(1-p)/n+z*z/(4*n*n)) / den
	lower, upper := math.Max(0, center-margin), math.Min(1, center+margin)
	lo, hi := strconv.FormatFloat(lower, 'f', 17, 64), strconv.FormatFloat(upper, 'f', 17, 64)
	r.Lower = &lo
	r.Upper = &hi
	if r.Trials < 100 {
		s := "insufficient_sample"
		r.Missing = &s
		return r, nil
	}
	switch {
	case lower >= .8:
		r.Rating = "easy"
	case lower >= .5 && upper < .8:
		r.Rating = "medium"
	case lower >= .2 && upper < .5:
		r.Rating = "hard"
	case upper < .2:
		r.Rating = "expert"
	default:
		s := "interval_crosses_band"
		r.Missing = &s
	}
	return r, nil
}
