package app

// Explicit advisory work over a saved case; core grading never depends on it.
import (
	"context"
	"encoding/base64"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"net/http"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

func (s *Server) MeasureCase(ctx context.Context, r AudioMeasureRequest, key string, client *http.Client) (map[string]any, error) {
	ctx, cancel := context.WithTimeout(ctx, OverallDeadline)
	defer cancel()
	raw, _ := lab.Canonical(r)
	if _, _, err := contracts.Validate("measure-request", "2.0.0", raw); err != nil {
		return nil, ErrInput
	}
	for _, method := range r.Methods {
		if !diagnosticMethod(method) {
			return nil, &provider.Failure{Code: "CAPABILITY_UNAVAILABLE"}
		}
	}
	op, err := s.Store.ReserveOperation(ctx, OperationRequest{Name: "speech_measure", Key: key, Path: "/api/v1/cases/" + r.Case + "/measurements", Body: raw})
	if err != nil {
		return nil, err
	}
	if op.Result != nil {
		view, e := s.Store.readAudioDiagnostic(ctx, *op.Result)
		if e == nil {
			run := view["run"].(map[string]any)
			if run["status"] == "failed" {
				e = &provider.Failure{Code: run["failure_code"].(string)}
			}
		}
		return view, e
	}
	if op.State != "reserved" {
		return nil, &provider.Failure{Code: "LEASE_ACTIVE"}
	}
	f, err := s.Store.diagnosticInputs(ctx, r)
	if err != nil {
		return nil, err
	}
	if err = s.Store.claimInference(ctx, op.ID); err != nil {
		return nil, err
	}
	defer func() {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer done()
		s.Store.releaseInference(end, op.ID)
	}()
	if _, err = s.Store.DB.Exec(ctx, "UPDATE operation SET subject_id=$2 WHERE id=$1", op.ID, r.Case); err != nil {
		return nil, err
	}
	frozen, err := s.Store.saveProviderBytes(ctx, sourceBytes(map[string]any{"request": r, "configuration": f.Configuration, "key": f.Key, "mutation_manifest": f.Manifest}), "provider_input")
	if err != nil {
		return nil, err
	}
	run := map[string]any{"schema_version": "2.0.0", "id": uuid.NewString(), "case_version_id": r.Case, "operation_id": op.ID, "status": "complete", "method_ids": r.Methods, "input_asset_id": frozen.ID, "output_asset_ids": []any{}, "support_asset_ids": []any{}, "receipt_ids": []any{}, "measurement_ids": []any{}, "failure_code": nil}
	measurements := []map[string]any{}
	for _, method := range r.Methods {
		profile, e := diagnosticProfile(f.Configuration, method)
		if e != nil {
			err = e
			break
		}
		packets, e := s.diagnosticPackets(ctx, f, method, profile, client)
		if e != nil {
			err = e
			break
		}
		for _, packet := range packets {
			if input, ok := packet["input"].(map[string]any); ok {
				run["support_asset_ids"] = append(run["support_asset_ids"].([]any), input["clip_asset_id"])
				if reference, ok := input["reference_clip_asset_id"].(string); ok {
					run["support_asset_ids"] = append(run["support_asset_ids"].([]any), reference)
				}
			}
			result, response, receipt, e := s.callAudioDiagnostic(ctx, r.Case, method, profile, f.Configuration, packet, client)
			if response != "" {
				run["output_asset_ids"] = append(run["output_asset_ids"].([]any), response)
			}
			if receipt != "" {
				run["receipt_ids"] = append(run["receipt_ids"].([]any), receipt)
			}
			if e != nil {
				err = e
				break
			}
			rows, ok := result["measurements"].([]any)
			if !ok {
				err = &provider.Failure{Code: "DIAGNOSTIC_OUTPUT_INVALID"}
				break
			}
			for _, v := range rows {
				row, ok := v.(map[string]any)
				if !ok || row["audio_sha256"] != r.AudioSHA || row["method_id"] != method {
					err = ErrReference
					break
				}
				interval, ok := row["interval"].(map[string]any)
				if !ok {
					err = ErrInput
					break
				}
				count := float64(f.Samples)
				a, aok := interval["start"].(float64)
				b, bok := interval["end"].(float64)
				if !aok || !bok || a < 0 || b <= a || b > count || interval["sample_rate_hz"] != float64(24000) {
					err = ErrReference
					break
				}
				if row["status"] != "observed" && (row["numeric_value"] != nil || row["categorical_value"] != nil) {
					err = ErrInput
					break
				}
				if row["status"] == "observed" && row["numeric_value"] == nil && row["categorical_value"] == nil {
					err = ErrInput
					break
				}
				row["evidence_asset_ids"] = []any{response}
				measurements = append(measurements, row)
			}
			if err != nil {
				break
			}
		}
		if err != nil {
			break
		}
	}
	if ctx.Err() != nil {
		err = ctx.Err()
	}
	if err != nil {
		code, _ := provider.SafeError(err)
		if errors.Is(err, context.DeadlineExceeded) {
			code = "DEADLINE_EXCEEDED"
		}
		if errors.Is(err, context.Canceled) {
			code = "CANCELLED"
		}
		run["status"], run["failure_code"] = "failed", code
	}
	end, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer done()
	view, saveErr := s.Store.finishAudioDiagnostic(end, op, run, measurements)
	if saveErr != nil {
		return nil, saveErr
	}
	return view, err
}

func (s *Server) diagnosticPackets(ctx context.Context, f diagnosticFrozen, method string, profile map[string]any, client *http.Client) ([]map[string]any, error) {
	base := map[string]any{"method_id": method, "audio_base64": base64.StdEncoding.EncodeToString(f.Audio), "audio_sha256": f.Key["audio"].(map[string]any)["sha256"], "reference_text": f.Surface}
	if method != "qwen25-omni-audio-v1" && method != "gemini-audio-v1" {
		return []map[string]any{base}, nil
	}
	prompt, err := s.Store.ReadAsset(ctx, profile["prompt_asset_id"].(string))
	if err != nil {
		return nil, err
	}
	intervals := []any{}
	for _, v := range f.Key["units"].([]any) {
		for _, v := range v.(map[string]any)["audio_intervals"].([]any) {
			a := v.(map[string]any)
			intervals = append(intervals, map[string]any{"start": a["start_ms"].(float64) * 24, "end": a["end_ms"].(float64) * 24})
		}
	}
	// Millisecond key bounds may round the final sample upward. Use the actual
	// containing file boundary for clip extraction, never a fabricated phone end.
	count := float64(f.Samples)
	for _, v := range intervals {
		a := v.(map[string]any)
		if a["end"].(float64) > count {
			a["end"] = count
		}
	}
	plan, err := s.speechCall(ctx, "/internal/v1/measure-plan", map[string]any{"audio_base64": base["audio_base64"], "intervals": intervals, "max_clip_seconds": profile["max_clip_seconds"]}, client)
	if err != nil {
		return nil, err
	}
	packets := []map[string]any{}
	for _, v := range plan["clips"].([]any) {
		clip := v.(map[string]any)
		raw, err := base64.StdEncoding.DecodeString(clip["audio_base64"].(string))
		if err != nil {
			return nil, err
		}
		asset, err := s.saveAudioBytes(ctx, raw)
		if err != nil {
			return nil, err
		}
		input := diagnosticIntent(f, clip["source_interval"].(map[string]any))
		input["clip_asset_id"], input["clip_sha256"], input["profile"] = asset.ID, asset.SHA, profile
		packet := map[string]any{"method_id": method, "profile": profile, "prompt": string(prompt), "input": input, "audio_base64": clip["audio_base64"]}
		if err = s.diagnosticReference(ctx, f, input, packet, client); err != nil {
			return nil, err
		}
		packets = append(packets, packet)
	}
	return packets, nil
}

func (s *Server) callAudioDiagnostic(ctx context.Context, caseID, method string, profile, configuration, packet map[string]any, client *http.Client) (map[string]any, string, string, error) {
	deadline, _ := ctx.Deadline()
	packet["timeout_seconds"] = max(1, time.Until(deadline).Seconds()-2)
	input, err := s.Store.saveProviderBytes(ctx, sourceBytes(packet), "provider_input")
	if err != nil {
		return nil, "", "", err
	}
	child, err := s.Store.ReserveOperation(ctx, OperationRequest{Name: "audio-diagnostic-call", Key: uuid.NewString(), Path: "/speech/measure", Body: sourceBytes(packet)})
	if err != nil {
		return nil, "", "", err
	}
	if err = s.Store.claimSpeech(ctx, child.ID, caseID); err != nil {
		return nil, "", "", err
	}
	started := time.Now().UTC()
	result, raw, status, callErr := s.speechExchange(ctx, "/internal/v1/measure", packet, client)
	finished := time.Now().UTC()
	if len(raw) == 0 {
		raw = []byte("null")
	}
	end, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer done()
	output, err := s.Store.saveProviderBytes(end, raw, "provider_output")
	if err != nil {
		return result, "", "", err
	}
	stage := "audio_measurement"
	if method == "faster-whisper-local-en-v1" {
		stage = "asr"
	}
	if method == "qwen25-omni-audio-v1" || method == "gemini-audio-v1" {
		stage = "audio_judge"
	}
	receipt, err := s.saveSpeechEvidence(end, child, profile, configuration, input, output, started, finished, status, callErr, map[string]any{"case_version_id": caseID, "method_id": method, "stage": stage})
	if err != nil {
		return result, output.ID, "", err
	}
	state := "complete"
	if callErr != nil {
		state = "failed"
	}
	if err = s.Store.finishSpeechPiece(end, child.ID, state, receipt); err != nil {
		return result, output.ID, receipt, err
	}
	return result, output.ID, receipt, callErr
}

func diagnosticArrayIDs(value any) []string {
	out := []string{}
	if ids, ok := value.([]string); ok {
		return ids
	}
	for _, v := range value.([]any) {
		out = append(out, fmt.Sprint(v))
	}
	return out
}
