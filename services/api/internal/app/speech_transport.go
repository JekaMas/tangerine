package app

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"github.com/google/uuid"
	"io"
	"net/http"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
	"time"
)

func (s *Server) speechCall(ctx context.Context, path string, packet any, client *http.Client) (map[string]any, error) {
	output, _, _, err := s.speechExchange(ctx, path, packet, client)
	return output, err
}

// speechQuality is advisory. A failed diagnostic is an unknown observation,
// while cancellation still terminates the foreground operation.
func (s *Server) speechQuality(ctx context.Context, pcm []byte, pauses []any, client *http.Client) (map[string]any, error) {
	result, err := s.speechCall(ctx, "/internal/v1/quality", map[string]any{"pcm_base64": base64.StdEncoding.EncodeToString(pcm), "planned_pause_intervals": pauses}, client)
	if ctx.Err() != nil {
		return nil, ctx.Err()
	}
	if err != nil {
		code, _ := provider.SafeError(err)
		return map[string]any{"state": "not_measurable", "error_code": code, "warnings": []any{"quality_unavailable"}, "integrated_lufs": nil, "true_peak_dbtp": nil, "observed_accent": nil, "speech_intelligibility": nil}, nil
	}
	return result, nil
}

func (s *Server) speechExchange(ctx context.Context, path string, packet any, client *http.Client) (map[string]any, []byte, int, error) {
	if client == nil {
		client = &http.Client{Timeout: OverallDeadline, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	}
	var raw []byte
	var e error
	method := http.MethodGet
	if packet != nil {
		raw, e = lab.Canonical(packet)
		if e != nil {
			return nil, nil, 0, e
		}
		method = http.MethodPost
	}
	request, e := http.NewRequestWithContext(ctx, method, s.SpeechURL+path, bytes.NewReader(raw))
	if e != nil {
		return nil, nil, 0, e
	}
	request.Header.Set("Authorization", "Bearer "+s.speechToken)
	request.Header.Set("Content-Type", "application/json")
	response, e := client.Do(request)
	if e != nil {
		if ctx.Err() != nil {
			return nil, nil, 0, ctx.Err()
		}
		return nil, nil, 0, &provider.Failure{Code: "SPEECH_UNAVAILABLE"}
	}
	defer response.Body.Close()
	body, e := io.ReadAll(response.Body)
	if e != nil {
		return nil, body, response.StatusCode, &provider.Failure{Code: "SPEECH_UNAVAILABLE"}
	}
	var output map[string]any
	if e = json.Unmarshal(body, &output); e != nil {
		return nil, body, response.StatusCode, &provider.Failure{Code: "SPEECH_UNAVAILABLE"}
	}
	if response.StatusCode != 200 {
		code, _ := output["error"].(string)
		if code == "" {
			code = "SPEECH_UNAVAILABLE"
		}
		return output, body, response.StatusCode, &provider.Failure{Code: code}
	}
	return output, body, response.StatusCode, nil
}

func (s *Server) dispatchSpeechPiece(ctx context.Context, p, piece, profile, settings map[string]any, turn any, client *http.Client) (map[string]any, string, error) {
	request := map[string]any{"profile": profile, "turn": turn, "piece_id": piece["id"]}
	return s.dispatchSpeechStage(ctx, p, piece, profile, settings, "/internal/v1/piece", request, client)
}

func (s *Server) dispatchSpeechStage(ctx context.Context, p, piece, profile, settings map[string]any, path string, request map[string]any, client *http.Client) (map[string]any, string, error) {
	deadline, _ := ctx.Deadline()
	request["timeout_seconds"] = time.Until(deadline).Seconds()
	request["preparation_id"] = p["id"]
	request["execution_id"] = piece["id"]
	request["render_plan_asset_id"] = p["render_plan_asset_id"]
	request["mutation_manifest_asset_id"] = p["mutation_manifest_asset_id"]
	input, _ := lab.Canonical(request)
	inputAsset, e := s.Store.saveProviderBytes(ctx, input, "provider_input")
	if e != nil {
		return nil, "", e
	}
	child, e := s.Store.ReserveOperation(ctx, OperationRequest{Name: "speech-inference", Key: uuid.NewString(), Path: "/speech/piece", Body: input})
	if e != nil {
		return nil, "", e
	}
	if e = s.Store.startSpeechPiece(ctx, child.ID, piece["id"].(string)); e != nil {
		return nil, "", e
	}
	started := time.Now().UTC()
	result, response, status, callErr := s.speechExchange(ctx, path, request, client)
	finished := time.Now().UTC()
	// A transport failure has no response body; the explicit null placeholder
	// is retained with unknown HTTP status and the failed outcome.
	if len(response) == 0 {
		response = []byte("null")
	}
	evidenceCtx, evidenceDone := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer evidenceDone()
	responseAsset, e := s.Store.saveProviderBytes(evidenceCtx, response, "provider_output")
	if e != nil {
		return nil, "", e
	}
	receipt, e := s.saveSpeechEvidence(evidenceCtx, child, profile, settings["configuration"].(map[string]any), inputAsset, responseAsset, started, finished, status, callErr, map[string]any{"preparation_id": p["id"], "case_version_id": uuid.NewSHA1(uuid.NameSpaceOID, []byte(p["id"].(string)+":speech-case")).String(), "piece_id": request["piece_id"], "execution_id": piece["id"], "render_plan_asset_id": p["render_plan_asset_id"], "mutation_manifest_asset_id": p["mutation_manifest_asset_id"]})
	if e != nil {
		return nil, "", e
	}

	childState := "complete"
	if callErr != nil {
		childState = "failed"
	}
	if e = s.Store.finishSpeechPiece(evidenceCtx, child.ID, childState, receipt); e != nil {
		return nil, "", e
	}

	return result, receipt, callErr
}
