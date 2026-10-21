package source

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"math/big"
	"path"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"
)

type Locator struct {
	Table   string `json:"table"`
	Pointer string `json:"pointer"`
}
type Projection struct {
	From       Locator  `json:"from"`
	To         string   `json:"to"`
	Conversion string   `json:"conversion"`
	Nulls      []string `json:"null_values"`
	Required   bool     `json:"required"`
}
type Join struct {
	Left         string `json:"left_table"`
	LeftPointer  string `json:"left_pointer"`
	Right        string `json:"right_table"`
	RightPointer string `json:"right_pointer"`
	Cardinality  string `json:"cardinality"`
	Required     bool   `json:"required"`
}
type TableSpec struct {
	Name string `json:"name"`
	Glob string `json:"member_glob"`
	Options
}
type Repeated struct {
	Table  string       `json:"table"`
	To     string       `json:"to"`
	Fields []Projection `json:"fields"`
}
type Program struct {
	Version      string       `json:"schema_version"`
	ID           string       `json:"id"`
	Source       string       `json:"source_id"`
	Release      string       `json:"release_id"`
	Manifest     string       `json:"raw_manifest_sha256"`
	Dictionaries []string     `json:"dictionary_asset_ids"`
	Tables       []TableSpec  `json:"tables"`
	Record       string       `json:"record_table"`
	Identity     Locator      `json:"identity"`
	Joins        []Join       `json:"joins"`
	Projections  []Projection `json:"projections"`
	Origin       string       `json:"span_origin"`
	Rate         int          `json:"sample_rate_hz"`
	Unmapped     string       `json:"unmapped_fields"`
	Repeated     []Repeated   `json:"repeated_projections"`
}
type Mapped struct {
	ID       string         `json:"id"`
	Member   string         `json:"member"`
	Table    string         `json:"table"`
	Ordinal  int            `json:"ordinal"`
	Identity any            `json:"native_identity"`
	Raw      Row            `json:"raw"`
	Value    map[string]any `json:"projection"`
	Status   string         `json:"status"`
	Issues   []Issue        `json:"issues"`
}

func sortedKeys[V any](m map[string]V) []string {
	k := make([]string, 0, len(m))
	for s := range m {
		k = append(k, s)
	}
	sort.Strings(k)
	return k
}
func jsonNumber(s string) json.Number { return json.Number(s) }
func StableID(parts ...string) string {
	h := sha256.Sum256([]byte(strings.Join(parts, "\x00")))
	return "src-" + hex.EncodeToString(h[:])
}
func Pointer(v any, p string) (any, bool) {
	if p == "" {
		return v, true
	}
	if !strings.HasPrefix(p, "/") {
		return nil, false
	}
	parts := strings.Split(p[1:], "/")
	for i, s := range parts {
		s = strings.ReplaceAll(strings.ReplaceAll(s, "~1", "/"), "~0", "~")
		var ok bool
		switch x := v.(type) {
		case map[string]any:
			v, ok = x[s]
			if !ok {
				return nil, false
			}
		case Row:
			v, ok = x[s]
			if !ok {
				return nil, false
			}
		case []any:
			n, e := strconv.Atoi(s)
			if e != nil || n < 0 || n >= len(x) {
				return nil, false
			}
			v = x[n]
		case []string:
			n, e := strconv.Atoi(s)
			if e != nil || n < 0 || n >= len(x) {
				return nil, false
			}
			v = x[n]
		default:
			return nil, false
		}
		if v == nil && i < len(parts)-1 {
			return nil, false
		}
	}
	return v, true
}

func writePointer(dst map[string]any, p string, v any) error {
	if !strings.HasPrefix(p, "/") {
		return fmt.Errorf("invalid target pointer")
	}
	tokens := strings.Split(p[1:], "/")
	m := dst
	for i, k := range tokens {
		k = strings.ReplaceAll(strings.ReplaceAll(k, "~1", "/"), "~0", "~")
		if k == "" {
			return fmt.Errorf("empty target key")
		}
		if i == len(tokens)-1 {
			if _, exists := m[k]; exists {
				return fmt.Errorf("conflicting output pointer %s", p)
			}
			m[k] = v
			return nil
		}
		child, ok := m[k]
		if !ok {
			n := map[string]any{}
			m[k] = n
			m = n
		} else {
			n, ok := child.(map[string]any)
			if !ok {
				return fmt.Errorf("conflicting target container")
			}
			m = n
		}
	}
	return nil
}

// IdentityKey keeps source scalar types and exact numeric values distinct.
func IdentityKey(v any) string { return exactKey(v) }
func exactKey(v any) string {
	switch x := v.(type) {
	case nil:
		return ""
	case json.Number:
		r, ok := new(big.Rat).SetString(string(x))
		if ok {
			return "n:" + r.RatString()
		}
	case int:
		return "n:" + strconv.Itoa(x)
	case string:
		return "s:" + x
	case bool:
		return "b:" + strconv.FormatBool(x)
	}
	return ""
}
func LoadTables(ctx context.Context, p Program, members []Member, open Open) (map[string][]Row, []Issue, error) {
	tables := map[string][]Row{}
	issues := []Issue{}
	members = append([]Member(nil), members...)
	sort.Slice(members, func(i, j int) bool { return members[i].Path < members[j].Path })
	for _, spec := range p.Tables {
		if _, ok := tables[spec.Name]; ok {
			return nil, nil, fmt.Errorf("duplicate mapping table")
		}
		tables[spec.Name] = []Row{}
		for _, m := range members {
			matches, e := path.Match(spec.Glob, m.Path)
			if e != nil {
				return nil, nil, e
			}
			if !matches {
				continue
			}
			if e = ctx.Err(); e != nil {
				return nil, nil, e
			}
			r, e := open(ctx, m.Path)
			if e != nil {
				return nil, nil, e
			}
			b, e := io.ReadAll(r)
			ce := r.Close()
			if e != nil {
				return nil, nil, e
			}
			if ce != nil {
				return nil, nil, ce
			}
			n, e := Parse(m.Path, b, spec.Options)
			if e != nil {
				issues = append(issues, Issue{m.Path, "parse_failed", e.Error()})
				continue
			}
			issues = append(issues, n.Issues...)
			for _, t := range n.Tables {
				if spec.Selector == "" || spec.Selector == "records" || spec.Selector == t.Name {
					tables[spec.Name] = append(tables[spec.Name], t.Rows...)
				}
			}
		}
	}
	return tables, issues, nil
}
func Project(p Program, tables map[string][]Row) ([]Mapped, error) {
	if p.Identity.Table != p.Record {
		return nil, fmt.Errorf("identity must select the native record table")
	}
	if _, ok := tables[p.Record]; !ok {
		return nil, fmt.Errorf("record table absent")
	}
	// Joins are an explicit directed graph rooted at the record table. No Cartesian
	// fallback or cyclic traversal can supply unrelated annotation data.
	connected := map[string]bool{p.Record: true}
	remaining := append([]Join(nil), p.Joins...)
	ordered := []Join{}
	for len(remaining) > 0 {
		next := []Join{}
		changed := false
		for _, j := range remaining {
			if !connected[j.Left] {
				next = append(next, j)
				continue
			}
			if connected[j.Right] || j.Cardinality != "one" && j.Cardinality != "many" {
				return nil, fmt.Errorf("cyclic/duplicate/invalid join")
			}
			if _, ok := tables[j.Right]; !ok {
				return nil, fmt.Errorf("join table absent")
			}
			connected[j.Right] = true
			ordered = append(ordered, j)
			changed = true
		}
		if !changed {
			return nil, fmt.Errorf("unconnected mapping tables")
		}
		remaining = next
	}
	for _, v := range p.Projections {
		if !connected[v.From.Table] {
			return nil, fmt.Errorf("unrelated scalar table")
		}
		if !allowedTarget(v.To) {
			return nil, fmt.Errorf("invalid projection root")
		}
	}
	for _, v := range p.Repeated {
		if !connected[v.Table] || !allowedTarget(v.To) {
			return nil, fmt.Errorf("unrelated repeated table or target")
		}
		for _, f := range v.Fields {
			if f.From.Table != v.Table {
				return nil, fmt.Errorf("repeated field must select its actual joined row")
			}
		}
	}
	indexes := map[string]map[string][]Row{}
	for _, j := range ordered {
		k := j.Right + "\x00" + j.RightPointer
		index := map[string][]Row{}
		for _, r := range tables[j.Right] {
			v, _ := Pointer(r, j.RightPointer)
			if key := exactKey(v); key != "" {
				index[key] = append(index[key], r)
			}
		}
		indexes[k] = index
	}
	out := []Mapped{}
	for ordinal, record := range tables[p.Record] {
		member, _ := record["member"].(string)
		id, ok := Pointer(record, p.Identity.Pointer)
		encoded, _ := json.Marshal(id)
		m := Mapped{ID: StableID(p.Source, p.Release, member, p.Record, string(encoded), strconv.Itoa(ordinal)), Member: member, Table: p.Record, Ordinal: ordinal, Identity: id, Raw: record, Value: map[string]any{}, Status: "mapped", Issues: []Issue{}}
		fail := func(code, detail string) {
			m.Status = "unmapped"
			m.Issues = append(m.Issues, Issue{member + ":" + strconv.Itoa(ordinal), code, detail})
		}
		if !ok || id == nil {
			fail("identity_missing", "Native identity is absent; no learner/record identity invented")
		}
		if record["invalid"] == true || record["ambiguous_keys"] == true {
			fail("native_invalid", "Native record has an explicit parser finding")
		}
		selected := map[string][]Row{p.Record: {record}}
		for _, j := range ordered {
			matches := []Row{}
			seen := map[RowKey]bool{}
			for _, left := range selected[j.Left] {
				v, _ := Pointer(left, j.LeftPointer)
				key := exactKey(v)
				if key == "" {
					continue
				}
				for _, r := range indexes[j.Right+"\x00"+j.RightPointer][key] {
					rk := rowKey(r)
					if !seen[rk] {
						matches = append(matches, r)
						seen[rk] = true
					}
				}
			}
			selected[j.Right] = matches
			if j.Required && len(matches) == 0 {
				fail("join_missing", j.Right)
			}
			if j.Cardinality == "one" && len(matches) > 1 {
				fail("join_ambiguous", j.Right)
			}
		}
		project := func(f Projection, rows []Row, dst map[string]any) {
			var v any
			if len(rows) == 1 {
				v, _ = Pointer(rows[0], f.From.Pointer)
			} else if len(rows) > 1 {
				fail("scalar_many", "A scalar cannot select the first of multiple rows")
				return
			}
			for _, n := range f.Nulls {
				if s, ok := v.(string); ok && s == n {
					v = nil
				}
			}
			if v == nil && f.Required {
				fail("required_missing", f.From.Pointer)
				return
			}
			if f.Conversion == "raw_only" {
				return
			}
			converted, e := Convert(v, f.Conversion, p, record)
			if e != nil {
				fail("conversion_failed", e.Error())
				return
			}
			if e = writePointer(dst, f.To, converted); e != nil {
				fail("projection_conflict", e.Error())
			}
		}
		for _, f := range p.Projections {
			project(f, selected[f.From.Table], m.Value)
		}
		for _, repeat := range p.Repeated {
			a := []any{}
			for _, r := range selected[repeat.Table] {
				v := map[string]any{}
				for _, f := range repeat.Fields {
					project(f, []Row{r}, v)
				}
				a = append(a, v)
			}
			if e := writePointer(m.Value, repeat.To, a); e != nil {
				fail("projection_conflict", e.Error())
			}
		}
		out = append(out, m)
	}
	return out, nil
}

type RowKey string

func rowKey(r Row) RowKey { b, _ := json.Marshal(r); return RowKey(b) }
func allowedTarget(p string) bool {
	for _, r := range []string{"/corpus_record/", "/case_candidate/", "/raw_metadata/"} {
		if strings.HasPrefix(p, r) {
			return true
		}
	}
	return false
}
func Convert(v any, kind string, p Program, row Row) (any, error) {
	if v == nil {
		return nil, nil
	}
	switch kind {
	case "identity":
		return v, nil
	case "raw_only":
		return nil, nil
	case "decimal", "integer", "seconds_to_samples":
		var s string
		switch x := v.(type) {
		case string:
			s = x
		case json.Number:
			s = string(x)
		case int:
			s = strconv.Itoa(x)
		default:
			return nil, fmt.Errorf("expected native number or documented decimal string")
		}
		if !sourceDecimalPattern.MatchString(s) {
			return nil, fmt.Errorf("expected plain decimal")
		}
		r, ok := new(big.Rat).SetString(s)
		if !ok {
			return nil, fmt.Errorf("invalid exact decimal")
		}
		if kind == "integer" {
			if !r.IsInt() {
				return nil, fmt.Errorf("fractional integer")
			}
			return json.Number(r.Num().String()), nil
		}
		if kind == "seconds_to_samples" {
			if r.Sign() < 0 || p.Rate <= 0 {
				return nil, fmt.Errorf("negative seconds or missing source rate")
			}
			r.Mul(r, new(big.Rat).SetInt64(int64(p.Rate)))
			q := new(big.Int).Quo(r.Num(), r.Denom())
			rem := new(big.Int).Mod(r.Num(), r.Denom())
			if rem.Lsh(rem, 1).Cmp(r.Denom()) >= 0 {
				q.Add(q, big.NewInt(1))
			}
			return json.Number(q.String()), nil
		}
		scale := 0
		if at := strings.IndexByte(s, '.'); at >= 0 {
			scale = len(s) - at - 1
		}
		return json.Number(r.FloatString(scale)), nil
	case "token_span", "codepoint_span":
		var a []any
		switch x := v.(type) {
		case []any:
			a = x
		case []int:
			for _, n := range x {
				a = append(a, json.Number(strconv.Itoa(n)))
			}
		}
		if len(a) != 2 {
			return nil, fmt.Errorf("expected two source offsets")
		}
		vals := []int{}
		for _, x := range a {
			n, e := Convert(x, "integer", p, row)
			if e != nil {
				return nil, e
			}
			i, e := strconv.Atoi(string(n.(json.Number)))
			if e != nil {
				return nil, e
			}
			vals = append(vals, i)
		}
		if p.Origin == "one_based_inclusive" {
			vals[0]--
		}
		if vals[0] < 0 || vals[1] < vals[0] {
			return nil, fmt.Errorf("invalid source span")
		}
		text, _ := row["text"].(string)
		if text == "" {
			if v, ok := Pointer(row, "/value/text"); ok {
				text, _ = v.(string)
			}
		}
		if kind == "token_span" {
			return TokenSpan(text, vals[0], vals[1])
		}
		if vals[1] > utf8.RuneCountInString(text) {
			return nil, fmt.Errorf("codepoint span outside source text")
		}
		return vals, nil
	}
	return nil, fmt.Errorf("unknown conversion %s", kind)
}

var sourceDecimalPattern = regexp.MustCompile(`^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$`)
