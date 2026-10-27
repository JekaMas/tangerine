package source

import (
	"encoding/json"
	"math/big"
	"path"
	"strings"
)

const SupplementParserVersion = "source-native-supplements-v1"

func SpeechSupplement(id string) bool {
	return id == "EDACC" || id == "ELRD" || id == "DIPLOMAT" || id == "DRAL"
}

func SupplementPlan(id string, m Member) (Options, string, bool) {
	o := Options{Encoding: "utf-8", Selector: "records"}
	// DRAL bundles an older archive as documentation. Its expanded contents are
	// a historical view, not extra members of the selected native population.
	if id == "DRAL" && HistoricalSupplementMember(m.Path) {
		return o, "ancillary", false
	}
	base := strings.ToLower(path.Base(m.Path))
	switch id {
	case "EDACC":
		switch base {
		case "segments", "text", "utt2spk", "conv.list", "stm", "stm.filt", "company.ctm", "glm":
			o.Format = "lines"
			return o, "sp_edacc_" + strings.ReplaceAll(base, ".", "_"), true
		case "linguistic_background.csv":
			o.Format, o.Header = "csv", true
			return o, "sp_edacc_background", true
		}
	case "ELRD":
		if strings.Contains(m.Path, "/diarized_transcripts/") && strings.HasSuffix(base, ".jsonl") {
			o.Format = "jsonl"
			return o, "sp_elrd_turns", true
		}
	case "DIPLOMAT":
		if strings.HasSuffix(base, ".jsonl") || base == "dataset.json" {
			o.Format = "jsonl"
			return o, "sp_diplomat", true
		}
	case "DRAL":
		if strings.HasSuffix(base, ".csv") {
			o.Format, o.Header = "csv", true
			return o, "sp_dral_" + strings.ReplaceAll(strings.TrimSuffix(base, ".csv"), "-", "_"), true
		}
	}
	return o, "ancillary", false
}

func HistoricalSupplementMember(name string) bool {
	for _, part := range strings.Split(strings.ToLower(name), "/") {
		if strings.HasSuffix(part, ".tgz") || strings.HasSuffix(part, ".tar.gz") || strings.HasSuffix(part, ".tar") || strings.HasSuffix(part, ".zip") {
			return true
		}
	}
	return false
}

// Native clock conversion retains the original spelling and an exact rational
// number of seconds. Unknown/invalid native clocks stay unknown, not guessed.
func SourceSeconds(native string) *big.Rat {
	s := strings.TrimSpace(native)
	if strings.Contains(s, " days ") {
		parts := strings.SplitN(s, " days ", 2)
		if parts[0] != "0" {
			return nil
		}
		s = parts[1]
	}
	parts := strings.Split(s, ":")
	if len(parts) != 1 && len(parts) != 3 {
		return nil
	}
	total := new(big.Rat)
	for _, part := range parts {
		v, ok := new(big.Rat).SetString(part)
		if !ok || v.Sign() < 0 {
			return nil
		}
		total.Mul(total, big.NewRat(60, 1)).Add(total, v)
	}
	return total
}

func SourceClock(start, end string) map[string]any {
	a, b := SourceSeconds(start), SourceSeconds(end)
	out := map[string]any{"native_start": start, "native_end": end, "unit": "seconds", "start": nil, "end": nil}
	if a != nil && b != nil && a.Cmp(b) <= 0 {
		out["start"] = a.RatString()
		out["end"] = b.RatString()
	}
	return out
}

func NativeCSV(row Row) map[string]string {
	header, cells := stringArray(row["header"]), stringArray(row["cells"])
	out := map[string]string{}
	for i, key := range header {
		if i < len(cells) {
			out[key] = cells[i]
		}
	}
	return out
}
func stringArray(value any) []string {
	if v, ok := value.([]string); ok {
		return v
	}
	out := []string{}
	if values, ok := value.([]any); ok {
		for _, v := range values {
			if s, ok := v.(string); ok {
				out = append(out, s)
			}
		}
	}
	return out
}

func ContextGroup(text, speakers any) string {
	// Exact context equivalence only; no claim of unique original conversation.
	raw, _ := json.Marshal([]any{text, speakers})
	return StableID("supplement-context", string(raw))
}
