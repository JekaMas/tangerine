package app

// One sample-domain owner for sequential and concurrent delivery. All sources
// are accepted mono PCM16 at 24kHz. No global normalization or model calls.
import (
	"context"
	"encoding/binary"
	"encoding/json"
	"math"
	"sort"
	"tangerine.local/api/internal/provider"
)

type speechWord struct {
	StartCP int `json:"start_cp"`
	EndCP   int `json:"end_cp"`
	Start   int `json:"start"`
	End     int `json:"end"`
}
type speechSource struct {
	ID         string
	Utterance  string
	Text       string
	ScopeStart int
	Count      int
	Gap        int
	Words      []speechWord
}
type speechPlacement struct {
	PieceID     string `json:"piece_id"`
	UtteranceID string `json:"utterance_id"`
	Start       int    `json:"final_start"`
	End         int    `json:"final_end"`
}
type speechTrack struct {
	PieceID     string  `json:"piece_id"`
	SourceStart int     `json:"source_start"`
	SourceEnd   int     `json:"source_end"`
	FinalStart  int     `json:"final_start"`
	Gain        float64 `json:"gain"`
}
type speechOverlap struct {
	UnitID string `json:"unit_id"`
	Kind   string `json:"kind"`
	Target string `json:"target_utterance_id"`
	Other  string `json:"overlapping_utterance_id"`
	Start  int    `json:"final_start"`
	End    int    `json:"final_end"`
}
type speechComposition struct {
	SampleCount int               `json:"sample_count"`
	Pieces      []speechPlacement `json:"pieces"`
	Tracks      []speechTrack     `json:"tracks"`
	Overlaps    []speechOverlap   `json:"overlaps"`
}

func compositionFailure(code string) error { return &provider.Failure{Code: code} }
func compositionValue(c speechComposition) map[string]any {
	raw, _ := json.Marshal(c)
	var v map[string]any
	_ = json.Unmarshal(raw, &v)
	return v
}
func savedComposition(progress map[string]any) (speechComposition, bool) {
	v, ok := progress["composition"]
	if !ok {
		return speechComposition{}, false
	}
	raw, _ := json.Marshal(v)
	var c speechComposition
	_ = json.Unmarshal(raw, &c)
	return c, true
}

type speechSourceRange struct {
	PieceID    string
	Start, End int
}

func speechSourceRanges(sources []speechSource, turn string, a, b int) ([]speechSourceRange, error) {
	ranges := []speechSourceRange{}
	for _, s := range sources {
		if s.Utterance != turn {
			continue
		}
		length := len([]rune(s.Text))
		x, y := max(0, a-s.ScopeStart), min(length, b-s.ScopeStart)
		if y <= x {
			continue
		}
		start, end := -1, -1
		if x == 0 {
			start = 0
		}
		if y == length {
			end = s.Count
		}
		for _, w := range s.Words {
			if w.StartCP == x {
				start = w.Start
			}
			if w.EndCP == y {
				end = w.End
			}
		}
		if start < 0 || end <= start {
			return nil, compositionFailure("ALIGNMENT_UNAVAILABLE")
		}
		ranges = append(ranges, speechSourceRange{s.ID, start, end})
	}
	if len(ranges) == 0 {
		return nil, compositionFailure("ALIGNMENT_UNAVAILABLE")
	}
	return ranges, nil
}
func planSpeechComposition(sources []speechSource, intents []any) (speechComposition, error) {
	c := speechComposition{Pieces: []speechPlacement{}, Tracks: []speechTrack{}, Overlaps: []speechOverlap{}}
	byOther := map[string]map[string]any{}
	for _, v := range intents {
		x := v.(map[string]any)
		id := x["overlapping_utterance_id"].(string)
		if byOther[id] != nil {
			return c, compositionFailure("CONSTRAINT_CONFLICT")
		}
		byOther[id] = x
	}
	starts := map[string]int{}
	offsets := map[string]int{}
	tail := 0
	previous := ""
	for _, s := range sources {
		if s.Utterance != previous {
			start := tail
			if intent := byOther[s.Utterance]; intent != nil {
				scope := intent["target_scope"].(map[string]any)
				ranges, e := speechSourceRanges(sources, intent["target_utterance_id"].(string), int(scope["start_cp"].(float64)), int(scope["end_cp"].(float64)))
				if e != nil {
					return c, e
				}
				first, last := ranges[0], ranges[len(ranges)-1]
				offset, ok := offsets[first.PieceID]
				if !ok {
					return c, compositionFailure("CONSTRAINT_CONFLICT")
				}
				start = offset + first.Start
				c.Overlaps = append(c.Overlaps, speechOverlap{intent["unit_id"].(string), intent["kind"].(string), intent["target_utterance_id"].(string), s.Utterance, start, offsets[last.PieceID] + last.End})
			}
			starts[s.Utterance] = start
		}
		start := starts[s.Utterance]
		if s.Utterance == previous {
			start = offsets[sources[len(c.Pieces)-1].ID] + sources[len(c.Pieces)-1].Count
		}
		end := start + s.Count
		c.Pieces = append(c.Pieces, speechPlacement{s.ID, s.Utterance, start, end})
		offsets[s.ID] = start
		if end+s.Gap > tail {
			tail = end + s.Gap
		}
		if end > c.SampleCount {
			c.SampleCount = end
		}
		previous = s.Utterance
	}
	c.SampleCount = tail
	for i := range c.Overlaps {
		o := &c.Overlaps[i]
		last := 0
		for _, p := range c.Pieces {
			if p.UtteranceID == o.Other && p.End > last {
				last = p.End
			}
		}
		if last < o.End {
			o.End = last
		}
		if o.End <= o.Start {
			return c, compositionFailure("CONSTRAINT_CONFLICT")
		}
	}
	for i, s := range sources {
		p := c.Pieces[i]
		cuts := []int{0, s.Count}
		gains := []struct {
			a, b int
			gain float64
		}{}
		for _, v := range intents {
			x := v.(map[string]any)
			if s.Utterance == x["overlapping_utterance_id"] {
				gains = append(gains, struct {
					a, b int
					gain float64
				}{0, s.Count, x["overlapping_gain"].(float64)})
			}
			if s.Utterance == x["target_utterance_id"] {
				scope := x["target_scope"].(map[string]any)
				ranges, e := speechSourceRanges(sources, s.Utterance, int(scope["start_cp"].(float64)), int(scope["end_cp"].(float64)))
				if e != nil {
					return c, e
				}
				for _, r := range ranges {
					if r.PieceID == s.ID {
						cuts = append(cuts, r.Start, r.End)
						gains = append(gains, struct {
							a, b int
							gain float64
						}{r.Start, r.End, x["target_gain"].(float64)})
					}
				}
			}
		}
		// Ordered split points keep untouched source ranges bit-identical.
		sort.Ints(cuts)
		for j := 1; j < len(cuts); j++ {
			a, b := cuts[j-1], cuts[j]
			if a == b {
				continue
			}
			gain := 1.0
			for _, g := range gains {
				if a >= g.a && b <= g.b {
					gain *= g.gain
				}
			}
			c.Tracks = append(c.Tracks, speechTrack{s.ID, a, b, p.Start + a, gain})
		}
	}
	return c, nil
}
func composeSpeechPCM(ctx context.Context, c speechComposition, sources map[string][]byte) ([]byte, error) {
	if e := ctx.Err(); e != nil {
		return nil, e
	}
	sums := make([]float64, c.SampleCount)
	for _, t := range c.Tracks {
		raw := sources[t.PieceID]
		for i := t.SourceStart; i < t.SourceEnd; i++ {
			if i%24000 == 0 {
				if e := ctx.Err(); e != nil {
					return nil, e
				}
			}
			sums[t.FinalStart+i-t.SourceStart] += float64(int16(binary.LittleEndian.Uint16(raw[i*2:]))) * t.Gain
		}
	}
	pcm := make([]byte, c.SampleCount*2)
	for i, v := range sums {
		n := math.Round(v)
		if n < -32768 || n > 32767 {
			return nil, compositionFailure("AUDIO_CLIPPING")
		}
		binary.LittleEndian.PutUint16(pcm[i*2:], uint16(int16(n)))
	}
	return pcm, nil
}

// Intersect each actual source correspondence with its local gain ranges.
// Concurrent rows remain independent; source clocks never become final clocks.
func compositionRows(rows []any, p speechPlacement, tracks []speechTrack) []any {
	out := []any{}
	for _, v := range rows {
		row := v.(map[string]any)
		a, b := sampleNumber(row["final_start"]), sampleNumber(row["final_end"])
		for _, t := range tracks {
			if t.PieceID != p.PieceID {
				continue
			}
			lo, hi := max(a, t.SourceStart), min(b, t.SourceEnd)
			if hi <= lo {
				continue
			}
			r := map[string]any{}
			for k, v := range row {
				r[k] = v
			}
			x, y := sampleNumber(row["source_start"]), sampleNumber(row["source_end"])
			if b > a {
				r["source_start"] = x + int(math.Round(float64(lo-a)*float64(y-x)/float64(b-a)))
				r["source_end"] = x + int(math.Round(float64(hi-a)*float64(y-x)/float64(b-a)))
			}
			r["final_start"], r["final_end"] = p.Start+lo, p.Start+hi
			r["mix_gain"] = t.Gain
			out = append(out, r)
		}
	}
	return out
}
func sampleNumber(v any) int {
	switch n := v.(type) {
	case int:
		return n
	case float64:
		return int(n)
	}
	return 0
}
