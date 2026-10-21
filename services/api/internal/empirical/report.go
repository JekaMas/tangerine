// Package empirical calculates descriptive reports over declared observations.
// It does not infer linguistic labels, missing absence labels or source rights.
package empirical

import (
	"encoding/json"
	"fmt"
	"math/big"
	"reflect"
	"sort"
)

type Fraction struct {
	Numerator   string  `json:"numerator"`
	Denominator string  `json:"denominator"`
	Exact       *Exact  `json:"exact"`
	Missing     *string `json:"missing_reason"`
}

// Unknown arithmetic inputs are JSON null; known zero counts remain "0".
func (f Fraction) MarshalJSON() ([]byte, error) {
	var n, d *string
	if f.Numerator != "" {
		n = &f.Numerator
	}
	if f.Denominator != "" {
		d = &f.Denominator
	}
	return json.Marshal(struct {
		Numerator   *string `json:"numerator"`
		Denominator *string `json:"denominator"`
		Exact       *Exact  `json:"exact"`
		Missing     *string `json:"missing_reason"`
	}{n, d, f.Exact, f.Missing})
}

type Exact struct {
	Numerator   string `json:"numerator"`
	Denominator string `json:"denominator"`
}

func Ratio(n, d int64) Fraction {
	f := Fraction{Numerator: fmt.Sprint(n), Denominator: fmt.Sprint(d)}
	if d == 0 {
		s := "no_inspected_denominator"
		f.Missing = &s
	} else {
		r := big.NewRat(n, d)
		f.Exact = &Exact{r.Num().String(), r.Denom().String()}
	}
	return f
}
func Unavailable(reason string) Fraction { return Fraction{Missing: &reason} }

type Population struct {
	Release   string  `json:"release"`
	View      string  `json:"view"`
	Split     string  `json:"split"`
	Annotator string  `json:"annotator"`
	Window    string  `json:"window"`
	Modality  string  `json:"modality"`
	Taxonomy  string  `json:"taxonomy_version"`
	Crosswalk string  `json:"crosswalk_version"`
	Origin    string  `json:"label_origin"`
	L1        *string `json:"l1"`
	CEFR      *string `json:"cefr"`
	Task      *string `json:"task"`
}
type Event struct {
	ID        string   `json:"id"`
	Native    string   `json:"native_label"`
	Leaf      *string  `json:"leaf_id"`
	Secondary []string `json:"secondary_ids"`
	Control   bool     `json:"control"`
	Excluded  string   `json:"excluded_reason"`
}
type Window struct {
	ID            string           `json:"id"`
	Annotated     bool             `json:"fully_annotated"`
	Tokens        *int64           `json:"native_tokens"`
	Events        []Event          `json:"events"`
	Opportunities map[string]int64 `json:"opportunities"`
}
type Decision struct {
	Reference string `json:"reference"`
	Predicted string `json:"predicted"`
}
type Input struct {
	AnnotatedLeaves []string   `json:"annotated_leaf_ids"`
	Population      Population `json:"population"`
	Windows         []Window   `json:"windows"`
	Decisions       []Decision `json:"decisions"`
	Leaves          []string   `json:"leaves"`
}
type Leaf struct {
	ID          string   `json:"id"`
	Events      int64    `json:"events"`
	Secondary   int64    `json:"secondary_labels"`
	Controls    int64    `json:"controls"`
	Share       Fraction `json:"event_share"`
	Prevalence  Fraction `json:"window_prevalence"`
	Opportunity Fraction `json:"opportunity_rate"`
	Density     Fraction `json:"per_1000_tokens"`
}
type Pair struct {
	A           string   `json:"a"`
	B           string   `json:"b"`
	Count       int64    `json:"distinct_event_windows"`
	Support     Fraction `json:"support"`
	Conditional Fraction `json:"conditional"`
	Lift        Fraction `json:"lift"`
}
type Confusion struct {
	Reference  string   `json:"reference"`
	Predicted  string   `json:"predicted"`
	Count      int64    `json:"count"`
	Proportion Fraction `json:"row_proportion"`
}
type Report struct {
	AnnotatedLeaves     []string         `json:"annotated_leaf_ids"`
	SourceAnnotated     int64            `json:"source_annotated_windows"`
	MappingIncomplete   int64            `json:"mapping_incomplete_windows"`
	UnlistedPairMeaning string           `json:"unlisted_pair_meaning"`
	NativeFrequencies   []Leaf           `json:"native_frequencies"`
	Population          Population       `json:"population"`
	Windows             int64            `json:"observed_windows"`
	Annotated           int64            `json:"annotated_windows"`
	Unannotated         int64            `json:"unannotated_windows"`
	Tokens              *int64           `json:"inspected_native_tokens"`
	Events              int64            `json:"eligible_events"`
	Unmapped            int64            `json:"unmapped_events"`
	Excluded            map[string]int64 `json:"excluded"`
	Native              map[string]int64 `json:"native_label_counts"`
	Leaves              []Leaf           `json:"leaves"`
	Pairs               []Pair           `json:"pairs"`
	Confusion           []Confusion      `json:"confusion"`
}

// Build accepts a single explicit population. Different source/view/origin strata
// are separate reports. Multiple labels on one event never become event pairs.
func Build(in Input) (Report, error) {
	r, e := build(in)
	if e != nil {
		return r, e
	}
	native := in
	native.Leaves = []string{}
	native.Windows = make([]Window, len(in.Windows))
	seen := map[string]bool{}
	for i, w := range in.Windows {
		native.Windows[i] = w
		native.Windows[i].Events = make([]Event, len(w.Events))
		for j, event := range w.Events {
			event.Secondary = []string{}
			label := event.Native
			if label == "" {
				label = "[native_label_unknown]"
			}
			event.Leaf = &label
			native.Windows[i].Events[j] = event
			if !seen[label] {
				seen[label] = true
				native.Leaves = append(native.Leaves, label)
			}
		}
	}
	native.Decisions = nil
	native.AnnotatedLeaves = append([]string{}, native.Leaves...)
	n, e := build(native)
	if e != nil {
		return r, e
	}
	r.NativeFrequencies = n.Leaves
	return r, nil
}
func build(in Input) (Report, error) {
	p := in.Population
	if p.Release == "" || p.View == "" || p.Window == "" || p.Origin == "" {
		return Report{}, fmt.Errorf("named population required")
	}
	r := Report{Population: p, Windows: int64(len(in.Windows)), Excluded: map[string]int64{}, Native: map[string]int64{}, Leaves: []Leaf{}, Pairs: []Pair{}, Confusion: []Confusion{}}
	scope := in.AnnotatedLeaves
	if scope == nil {
		scope = in.Leaves
	}
	r.AnnotatedLeaves = append([]string{}, scope...)
	covered := map[string]bool{}
	for _, id := range scope {
		covered[id] = true
	}
	leaf := map[string]*Leaf{}
	presence := map[string]int64{}
	pairs := map[[2]string]int64{}
	annotatedEvents := map[string]int64{}
	opp := map[string]int64{}
	oppKnown := map[string]bool{}
	tokens := int64(0)
	tokensKnown := true
	windowIDs := map[string]bool{}
	globalEvents := map[string]Event{}
	annotatedEventSeen := map[string]bool{}
	for _, id := range in.Leaves {
		if id == "" || leaf[id] != nil {
			return r, fmt.Errorf("duplicate leaf")
		}
		leaf[id] = &Leaf{ID: id}
		oppKnown[id] = true
	}
	for _, id := range scope {
		if leaf[id] == nil {
			return r, fmt.Errorf("unknown annotation scope leaf")
		}
	}
	for _, w := range in.Windows {
		if w.ID == "" || windowIDs[w.ID] {
			return r, fmt.Errorf("duplicate window identity")
		}
		windowIDs[w.ID] = true
		if w.Annotated {
			r.SourceAnnotated++
			complete := true
			for _, event := range w.Events {
				if event.Excluded == "unresolved_native_label" || event.Excluded == "invalid" || event.Excluded == "" && event.Leaf == nil {
					complete = false
				}
			}
			if !complete {
				r.MappingIncomplete++
				w.Annotated = false
			}
		}

		if w.Annotated {
			r.Annotated++
			if w.Tokens == nil {
				tokensKnown = false
			} else if *w.Tokens < 0 {
				return r, fmt.Errorf("negative token count")
			} else {
				tokens += *w.Tokens
			}
			for id := range leaf {
				n, ok := w.Opportunities[id]
				if !ok {
					oppKnown[id] = false
				} else if n < 0 {
					return r, fmt.Errorf("negative opportunities")
				} else {
					opp[id] += n
				}
			}
		} else {
			r.Unannotated++
		}
		counts := map[string]int64{}
		events := map[string]bool{}
		for _, e := range w.Events {
			if e.ID == "" || events[e.ID] {
				return r, fmt.Errorf("duplicate event identity")
			}
			events[e.ID] = true
			previous, seen := globalEvents[e.ID]
			if seen && !reflect.DeepEqual(previous, e) {
				return r, fmt.Errorf("conflicting repeated event identity")
			}
			if !seen {
				globalEvents[e.ID] = e
			}

			if e.Excluded != "" {
				if !seen {
					r.Excluded[e.Excluded]++
				}
				continue
			}
			if !seen {
				r.Native[e.Native]++
			}
			if e.Leaf == nil {
				if !seen {
					r.Unmapped++
				}
				continue
			}
			l := leaf[*e.Leaf]
			if l == nil {
				return r, fmt.Errorf("unknown mapped leaf")
			}
			secondarySeen := map[string]bool{}
			for _, s := range e.Secondary {
				if secondarySeen[s] {
					continue
				}
				secondarySeen[s] = true
				if v := leaf[s]; v != nil {
					if !seen {
						v.Secondary++
					}
				} else {
					return r, fmt.Errorf("unknown secondary leaf")
				}
			}
			if e.Control {
				if !seen {
					l.Controls++
				}
				continue
			}
			if !seen {
				l.Events++
				r.Events++
			}
			if w.Annotated {
				counts[l.ID]++
				if !annotatedEventSeen[e.ID] {
					annotatedEvents[l.ID]++
					annotatedEventSeen[e.ID] = true
				}
			}
		}
		ids := []string{}
		for id, n := range counts {
			if n > 0 {
				presence[id]++
				ids = append(ids, id)
			}
		}
		sort.Strings(ids)
		for i, a := range ids {
			for j := i; j < len(ids); j++ {
				b := ids[j]
				if a == b && counts[a] < 2 {
					continue
				}
				pairs[[2]string{a, b}]++
			}
		}
	}
	if tokensKnown {
		r.Tokens = &tokens
	}
	ids := []string{}
	for id := range leaf {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	for _, id := range ids {
		l := leaf[id]
		l.Share = Ratio(l.Events, r.Events)
		l.Prevalence = Ratio(presence[id], r.Annotated)
		if !covered[id] {
			l.Prevalence = Unavailable("leaf_annotation_scope_not_declared")
		}
		l.Opportunity = Unavailable("correct_opportunity_annotations_absent")
		if covered[id] && oppKnown[id] && r.Annotated > 0 {
			l.Opportunity = Ratio(annotatedEvents[id], opp[id])
		}
		l.Density = Unavailable("native_token_exposure_unknown")
		if covered[id] && r.Tokens != nil {
			l.Density = Ratio(1000*annotatedEvents[id], *r.Tokens)
		}
		r.Leaves = append(r.Leaves, *l)
	}
	// All observed leaf pairs, both directions for conditional association. Missing
	// leaves retain coverage above rather than a fabricated zero-strength graph.
	keys := [][2]string{}
	for k := range pairs {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool {
		if keys[i][0] != keys[j][0] {
			return keys[i][0] < keys[j][0]
		}
		return keys[i][1] < keys[j][1]
	})
	for _, k := range keys {
		n := pairs[k]
		if !covered[k[0]] || !covered[k[1]] {
			r.Pairs = append(r.Pairs, Pair{k[0], k[1], n, Unavailable("pair_annotation_scope_not_declared"), Unavailable("pair_annotation_scope_not_declared"), Unavailable("pair_annotation_scope_not_declared")})
			continue
		}
		r.Pairs = append(r.Pairs, Pair{k[0], k[1], n, Ratio(n, r.Annotated), Ratio(n, presence[k[0]]), Ratio(n*r.Annotated, presence[k[0]]*presence[k[1]])})
		if k[0] != k[1] {
			r.Pairs = append(r.Pairs, Pair{k[1], k[0], n, Ratio(n, r.Annotated), Ratio(n, presence[k[1]]), Ratio(n*r.Annotated, presence[k[0]]*presence[k[1]])})
		}
	}
	conf := map[[2]string]int64{}
	totals := map[string]int64{}
	for _, d := range in.Decisions {
		if d.Reference == "" || d.Predicted == "" {
			return r, fmt.Errorf("explicit confusion labels including unknown required")
		}
		conf[[2]string{d.Reference, d.Predicted}]++
		totals[d.Reference]++
	}
	keys = nil
	for k := range conf {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool {
		if keys[i][0] != keys[j][0] {
			return keys[i][0] < keys[j][0]
		}
		return keys[i][1] < keys[j][1]
	})
	for _, k := range keys {
		r.Confusion = append(r.Confusion, Confusion{k[0], k[1], conf[k], Ratio(conf[k], totals[k[0]])})
	}
	r.UnlistedPairMeaning = "zero distinct-event windows in the declared fully inspected mapped population; conditional/lift require nonzero leaf counts"
	if r.Annotated == 0 {
		r.UnlistedPairMeaning = "unavailable: no fully inspected mapped window population"
	}
	return r, nil
}
