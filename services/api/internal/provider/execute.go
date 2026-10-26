package provider

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"strconv"
	"strings"
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
	Repair     *RepairMessage
}

// The shared execution owner constructs this message before provider-specific
// serialization. Observers retain it without reverse-parsing a wire dialect.
type RepairMessage struct{ Instruction, Content string }
type ExecuteRequest struct {
	NormalizeProjection func(any) any
	AllowTransportRetry func() bool
	Profile             Profile
	Instructions        string
	Input               []any
	Format              any
	OutputKind          string
	Timeout             time.Duration
	DiagnoseInvalid     func([]byte) string
	Validate            func([]byte) error
	Before              func(context.Context, Attempt) error
	After               func(context.Context, Attempt) error
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
	var repairMessage *RepairMessage
	for index := 0; index < 5; index++ {
		wire, e := Serialize(r.Profile, instructions, input, format)
		if e != nil {
			return nil, attempts, e
		}
		a := Attempt{Index: index, Kind: kind, Wire: wire, Repair: repairMessage}
		if r.Before != nil {
			if e = r.Before(ctx, a); e != nil {
				return nil, attempts, e
			}
		}
		a.Response, e = Exchange(ctx, client, r.Profile, wire, credential)
		if e == nil {
			if r.DiagnoseInvalid == nil {
				a.Projection, e = projectStageVisible(a.Response.Visible, r.OutputKind, false, r.NormalizeProjection)
			} else {
				a.Projection, e = projectStageVisible(a.Response.Visible, r.OutputKind, true, r.NormalizeProjection)
				if e != nil {
					if detail := r.DiagnoseInvalid(a.Projection); detail != "" {
						var invalid *OutputValidationError
						if errors.As(e, &invalid) {
							e = &OutputValidationError{Detail: invalid.Detail + "\n" + detail}
						} else if code, _ := SafeError(e); code == "PROVIDER_OUTPUT_INVALID" {
							// An empty reply has no candidate, but still needs
							// the stage's actual task guidance in its one repair.
							e = &OutputValidationError{Detail: detail}
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
		if a.Response.Outcome == "transport_error" && !retried && retryableTransport(a.Response, r.AllowTransportRetry != nil) && (r.AllowTransportRetry == nil || r.AllowTransportRetry()) {
			if r.AllowTransportRetry != nil {
				delay := transportRetryDelay(a.Response.RetryAfter, time.Now())
				deadline, _ := ctx.Deadline()
				if time.Until(deadline) < delay+5*time.Second {
					return nil, attempts, e
				}
				timer := time.NewTimer(delay)
				select {
				case <-ctx.Done():
					timer.Stop()
					return nil, attempts, ctx.Err()
				case <-timer.C:
				}
			}
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
			repairMessage = &RepairMessage{Instruction: RepairInstruction + safe, Content: string(payload)}
			input = append(input, map[string]any{"role": "user", "content": string(payload)})
			repaired = true
			kind = "semantic_repair"
			continue
		}
		return nil, attempts, e
	}
	return nil, attempts, fail("PROVIDER_OUTPUT_INVALID")
}

// Existing standalone callers retain their adapter retry policy. Foreground
// evaluation shares one retry and follows its narrower saved runtime contract.
func retryableTransport(r Response, foreground bool) bool {
	if r.HTTPStatus == nil {
		return len(r.Raw) == 0
	}
	if !foreground {
		return *r.HTTPStatus >= 500
	}
	switch *r.HTTPStatus {
	case 408, 429, 502, 503, 504:
		return true
	}
	return false
}
func transportRetryDelay(value string, now time.Time) time.Duration {
	value = strings.TrimSpace(value)
	if seconds, e := strconv.ParseInt(value, 10, 32); e == nil && seconds >= 0 {
		return time.Duration(seconds) * time.Second
	}
	if at, e := http.ParseTime(value); e == nil && !at.Before(now) {
		return at.Sub(now)
	}
	return time.Second
}
