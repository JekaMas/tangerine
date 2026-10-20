package provider

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"time"
)

// This owned fragment is versioned with the adapter, and retained in each final
// wire snapshot. It corrects output format/semantics without changing the task.
const RepairInstruction = "The preceding visible reply did not satisfy the supplied output contract. Using the same complete saved input and instructions, return one corrected JSON object. Preserve valid substantive decisions. Do not invent missing evidence or fields. Validation: "

// OutputValidationError keeps a public safe code and private repair guidance.
// Only an owned output validator creates this type; provider error bodies do not.
type OutputValidationError struct{ Detail string }

func (e *OutputValidationError) Error() string            { return "PROVIDER_OUTPUT_INVALID" }
func (e *OutputValidationError) Unwrap() error            { return fail("PROVIDER_OUTPUT_INVALID") }
func (e *OutputValidationError) ValidationDetail() string { return e.Detail }

type Attempt struct {
	Index      int
	Kind       string
	Wire       []byte
	Response   Response
	Projection []byte
	Err        error
}
type ExecuteRequest struct {
	Profile         Profile
	Instructions    string
	Input           []any
	Format          any
	OutputKind      string
	Timeout         time.Duration
	DiagnoseInvalid func([]byte) string
	Validate        func([]byte) error
	Before          func(context.Context, Attempt) error
	After           func(context.Context, Attempt) error
}

func Execute(ctx context.Context, client *http.Client, r ExecuteRequest, credential string) ([]byte, []Attempt, error) {
	if r.Timeout <= 0 || r.Timeout > 270*time.Second {
		return nil, nil, fail("CONSTRAINT_CONFLICT")
	}
	ctx, cancel := context.WithTimeout(ctx, r.Timeout)
	defer cancel()
	attempts := []Attempt{}
	input := append([]any(nil), r.Input...)
	instructions := r.Instructions
	format := r.Format
	kind := "initial"
	retried, fallback, repaired := false, false, false
	for index := 0; index < 5; index++ {
		wire, e := Serialize(r.Profile, instructions, input, format)
		if e != nil {
			return nil, attempts, e
		}
		a := Attempt{Index: index, Kind: kind, Wire: wire}
		if r.Before != nil {
			if e = r.Before(ctx, a); e != nil {
				return nil, attempts, e
			}
		}
		a.Response, e = Exchange(ctx, client, r.Profile, wire, credential)
		if e == nil {
			if r.DiagnoseInvalid == nil {
				a.Projection, e = ProjectVisible(a.Response.Visible, r.OutputKind)
			} else {
				a.Projection, e = projectVisible(a.Response.Visible, r.OutputKind, true)
				if e != nil && len(a.Projection) > 0 {
					if detail := r.DiagnoseInvalid(a.Projection); detail != "" {
						var invalid *OutputValidationError
						if errors.As(e, &invalid) {
							e = &OutputValidationError{Detail: invalid.Detail + "\n" + detail}
						}
					}
				}
			}
			if e == nil && r.Validate != nil {
				e = r.Validate(a.Projection)
			}
			if e != nil {
				a.Response.Outcome = "schema_error"
			}
		}
		a.Err = e
		if e != nil && a.Response.ErrorCode == nil {
			code, _ := SafeError(e)
			a.Response.ErrorCode = &code
		}
		// Native evidence must survive request cancellation, and precede any returned
		// usable result. The reserve is bounded separately from the expired stage.
		if r.After != nil {
			saveCtx, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
			saveErr := r.After(saveCtx, a)
			done()
			if saveErr != nil {
				return nil, append(attempts, a), saveErr
			}
		}
		attempts = append(attempts, a)
		if ctx.Err() != nil {
			return nil, attempts, ctx.Err()
		}
		if e == nil {
			return a.Projection, attempts, nil
		}
		code, providerCode := SafeError(e)
		if code == "LOCAL_BUDGET_EXCEEDED" || a.Response.Outcome == "refusal" || code == "MISSING_CREDENTIALS" {
			return nil, attempts, e
		}
		if format != nil && !fallback && a.Response.HTTPStatus != nil && *a.Response.HTTPStatus == 400 && (providerCode == "unsupported_parameter" || providerCode == "invalid_json_schema" || providerCode == "unsupported_value") {
			format = nil
			fallback = true
			kind = "structured_fallback"
			continue
		}
		if a.Response.Outcome == "transport_error" && !retried && (a.Response.HTTPStatus == nil || *a.Response.HTTPStatus >= 500) {
			retried = true
			kind = "transport_retry"
			continue
		}
		if !repaired && (a.Response.Outcome == "schema_error" || a.Response.Outcome == "incomplete") {
			safe := code
			if safe == "" {
				safe = "PROVIDER_OUTPUT_INVALID"
			}
			repairData := map[string]any{"repair_instruction": RepairInstruction + safe, "validation_code": safe, "raw_visible_output": a.Response.Visible}
			var detail interface{ ValidationDetail() string }
			if errors.As(e, &detail) {
				repairData["validation_detail"] = detail.ValidationDetail()
			}
			payload, _ := json.Marshal(repairData)
			input = append(input, map[string]any{"role": "user", "content": string(payload)})
			repaired = true
			kind = "semantic_repair"
			continue
		}
		return nil, attempts, e
	}
	return nil, attempts, fail("PROVIDER_OUTPUT_INVALID")
}
