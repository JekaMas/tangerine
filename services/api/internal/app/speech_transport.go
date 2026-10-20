package app

import (
	"bytes"
	"context"
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
	deadline, _ := ctx.Deadline()
	timeout := time.Until(deadline).Seconds()
	request := map[string]any{"profile": profile, "turn": turn, "timeout_seconds": timeout}
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
	result, response, status, callErr := s.speechExchange(ctx, "/internal/v1/piece", request, client)
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
	receipt, e := s.saveSpeechEvidence(evidenceCtx, child, profile, settings["configuration"].(map[string]any), inputAsset, responseAsset, started, finished, status, callErr)
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
