package lab

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"tangerine.local/api/internal/contracts"
	"time"
)

// Both native tooling entrypoints use the existing canonical JSON rules before
// dispatch. Duplicate fields must not silently choose another action or flag.
func DecodeCommand(input io.Reader, value any) error {
	const limit = 32 * 1024 * 1024
	raw, err := io.ReadAll(io.LimitReader(input, limit+1))
	if err != nil {
		return err
	}
	if len(raw) > limit {
		return errors.New("Lab command exceeds 32 MiB")
	}
	canonical, err := contracts.Canonical(raw)
	if err != nil {
		return err
	}
	d := json.NewDecoder(bytes.NewReader(canonical))
	d.DisallowUnknownFields()
	return d.Decode(value)
}

type Request struct {
	Action       string            `json:"action"`
	Bundle       Bundle            `json:"bundle"`
	Input        map[string]any    `json:"input"`
	Components   map[string]any    `json:"components"`
	Stage        string            `json:"stage"`
	Phase        *string           `json:"phase"`
	Budget       int               `json:"budget"`
	Reserved     int               `json:"reserved"`
	Payload      json.RawMessage   `json:"payload"`
	Secrets      []string          `json:"secrets"`
	Capture      bool              `json:"capture"`
	Join         Join              `json:"join"`
	Cases        []string          `json:"cases"`
	Variants     []string          `json:"variants"`
	Repetitions  int               `json:"repetitions"`
	Trace        TraceSpan         `json:"trace"`
	Dependencies map[string]string `json:"dependencies"`
	Kind         string            `json:"kind"`
}

func Command(input io.Reader, output io.Writer) error {
	var r Request
	if e := DecodeCommand(input, &r); e != nil {
		return e
	}
	var result any
	var e error
	switch r.Action {
	case "contract":
		_, _, e = contracts.Validate(r.Kind, "2.0.0", r.Payload)
		result = map[string]any{"status": "validated"}
	case "inventory":
		e = ValidateInventory(r.Payload, r.Dependencies)
		result = map[string]any{"status": "validated", "provider_calls": 0}
	case "dataset":
		e = ValidateDataset(r.Payload)
		result = map[string]any{"status": "validated", "provider_calls": 0}
	case "otlp":
		result, e = OTLP(r.Trace)
	case "builtins":
		result = Builtins(time.Now())
	case "seal":
		r.Bundle.Seal()
		e = ValidateBundle(r.Bundle)
		result = r.Bundle
	case "validate":
		e = ValidateBundle(r.Bundle)
		result = r.Bundle
	case "prepare":
		result, e = Prepare(r.Bundle, r.Stage, r.Phase, r.Input, r.Components, r.Budget, r.Reserved)
	case "sanitize":
		result, e = Sanitize(r.Payload, r.Secrets, r.Capture)
	case "reconcile":
		result = Reconcile(r.Join)
	case "plan":
		result, e = PlannedRows(r.Cases, r.Variants, r.Repetitions)
	default:
		e = errors.New("unknown Lab action")
	}
	if e != nil {
		return e
	}
	return json.NewEncoder(output).Encode(result)
}
