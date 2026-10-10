package lab

import (
	"encoding/binary"
	"encoding/hex"
	"errors"
	"sort"
	"time"
)

// This narrow OTLP encoder implements the published protobuf Span fields. The
// native MLflow test decodes/ingests these exact bytes independently.
func varint(v uint64) []byte { return binary.AppendUvarint(nil, v) }
func field(n int, b []byte) []byte {
	p := varint(uint64(n<<3 | 2))
	p = append(p, varint(uint64(len(b)))...)
	return append(p, b...)
}
func fixed(n int, v uint64) []byte {
	p := varint(uint64(n<<3 | 1))
	return binary.LittleEndian.AppendUint64(p, v)
}

type TraceSpan struct {
	Trace      string
	Span       string
	Parent     string
	Name       string
	Start      time.Time
	End        time.Time
	Attributes map[string]string
	Error      bool
}

func OTLP(s TraceSpan) ([]byte, error) {
	trace, e := hex.DecodeString(s.Trace)
	if e != nil || len(trace) != 16 {
		return nil, errors.New("invalid trace identity")
	}
	span, e := hex.DecodeString(s.Span)
	if e != nil || len(span) != 8 {
		return nil, errors.New("invalid span identity")
	}
	if s.Name == "" || s.Start.IsZero() || s.End.Before(s.Start) {
		return nil, errors.New("invalid actual span interval")
	}
	p := append(field(1, trace), field(2, span)...)
	if s.Parent != "" {
		parent, e := hex.DecodeString(s.Parent)
		if e != nil || len(parent) != 8 {
			return nil, errors.New("invalid span parent")
		}
		p = append(p, field(4, parent)...)
	}
	p = append(p, field(5, []byte(s.Name))...)
	p = append(p, byte(6<<3), 1)
	p = append(p, fixed(7, uint64(s.Start.UnixNano()))...)
	p = append(p, fixed(8, uint64(s.End.UnixNano()))...)
	allowed := map[string]bool{}
	for _, k := range []string{"tangerine.operation_id", "stage", "phase", "receipt_id", "context_snapshot_id", "bundle_sha256", "binding_sha256", "input_sha256", "case_sha256", "audio_sha256", "answer_sha256", "cache_hit", "attempt_kind", "attempt_index", "requested_model", "returned_model", "error", "duration_ms", "input_tokens", "output_tokens", "reported_cost"} {
		allowed[k] = true
	}
	keys := []string{}
	for k := range s.Attributes {
		if !allowed[k] {
			return nil, errors.New("unsafe/unregistered span attribute")
		}
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		a := append(field(1, []byte(k)), field(2, field(1, []byte(s.Attributes[k])))...)
		p = append(p, field(9, a)...)
	}
	status := []byte{byte(3 << 3), 1}
	if s.Error {
		status[1] = 2
	}
	p = append(p, field(15, status)...)
	scope := field(2, p)
	resource := field(2, scope)
	return field(1, resource), nil
}
