package app

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"time"
)

func (s *Server) qualityList(w http.ResponseWriter, r *http.Request) {
	items, e := s.Store.QualityExperiments(r.Context())
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, items)
}
func (s *Server) qualityCreate(w http.ResponseWriter, r *http.Request) {
	var input QualitySubmission
	if e := decodeQualityInput(w, r, &input); e != nil {
		sourceHTTPError(w, ErrInput)
		return
	}
	p, e := s.Store.AdmitExperiment(r.Context(), input)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 201, p)
}
func (s *Server) qualityGet(w http.ResponseWriter, r *http.Request) {
	p, e := s.Store.QualityExperiment(r.Context(), r.PathValue("id"))
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, p)
}
func (s *Server) qualityAction(w http.ResponseWriter, r *http.Request) {
	id, action, ok := strings.Cut(r.PathValue("action"), ":")
	if !ok {
		sourceHTTPError(w, ErrInput)
		return
	}
	if action == "cancel" {
		e := s.Store.CancelQualityExperiment(r.Context(), id)
		if cancel, ok := s.qualityCancels.Load(id); ok {
			cancel.(context.CancelFunc)()
		}
		if e != nil {
			sourceHTTPError(w, e)
			return
		}
		writeJSON(w, 200, map[string]any{"cancel_requested": true})
		return
	}
	if action != "run" && action != "resume" {
		sourceHTTPError(w, ErrInput)
		return
	}
	// A batch can include many separately bounded native operations. Its response
	// remains a foreground request and client disconnect cancels active work.
	_ = http.NewResponseController(w).SetWriteDeadline(time.Time{})
	p, e := s.RunQualityExperiment(r.Context(), id, action == "resume", nil)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, p)
}
func (s *Server) empiricalList(w http.ResponseWriter, r *http.Request) {
	items, e := s.Store.EmpiricalReports(r.Context())
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, items)
}
func (s *Server) empiricalCreate(w http.ResponseWriter, r *http.Request) {
	var input EmpiricalSubmission
	if e := decodeQualityInput(w, r, &input); e != nil {
		sourceHTTPError(w, ErrInput)
		return
	}
	p, e := s.Store.CreateEmpiricalReport(r.Context(), input)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 201, p)
}
func (s *Server) empiricalGet(w http.ResponseWriter, r *http.Request) {
	p, e := s.Store.EmpiricalReport(r.Context(), r.PathValue("id"))
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, p)
}
func (s *Server) qualityAsset(w http.ResponseWriter, r *http.Request) {
	b, e := s.Store.ReadAsset(r.Context(), r.PathValue("id"))
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	_, _ = w.Write(b)
}
func (s *Server) qualityDefaults(w http.ResponseWriter, r *http.Request) {
	c, _, e := s.Store.Configuration(r.Context())
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	b, e := s.Store.ActiveLabBundle(r.Context())
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, map[string]any{"configuration": c, "bundle": b, "taxonomy_ids": taxonomyLeafIDs()})
}

// QualityCommand is the same foreground owner used by the local UI. It does not
// contain an inference SDK, second scorer or mutable workspace activation.
func (s *Server) QualityCommand(ctx context.Context, input io.Reader, output io.Writer) error {
	var r struct {
		ExportReceipt QualityExportReceipt `json:"export_receipt"`
		Action        string               `json:"action"`
		ID            string               `json:"id"`
		Resume        bool                 `json:"resume"`
		Submission    QualitySubmission    `json:"submission"`
		Report        EmpiricalSubmission  `json:"report"`
	}
	if e := lab.DecodeCommand(input, &r); e != nil {
		return e
	}
	var result any
	var e error
	switch r.Action {
	case "admit":
		result, e = s.Store.AdmitExperiment(ctx, r.Submission)
	case "eval":
		result, e = s.RunQualityExperiment(ctx, r.ID, r.Resume, nil)
	case "read":
		result, e = s.Store.QualityExperiment(ctx, r.ID)
	case "list":
		result, e = s.Store.QualityExperiments(ctx)
	case "cancel":
		e = s.Store.CancelQualityExperiment(ctx, r.ID)
		result = map[string]any{"cancel_requested": e == nil}
	case "report":
		result, e = s.Store.CreateEmpiricalReport(ctx, r.Report)
	case "report-read":
		result, e = s.Store.EmpiricalReport(ctx, r.ID)
	case "export":
		result, e = s.Store.QualityDiagnostic(ctx, r.ID)
	case "export-ack":
		e = s.Store.AcknowledgeQualityExport(ctx, r.ExportReceipt)
		result = map[string]any{"export_acknowledged": e == nil}
	default:
		return ErrInput
	}
	if e != nil {
		return e
	}
	return json.NewEncoder(output).Encode(result)
}

func decodeQualityInput(w http.ResponseWriter, r *http.Request, value any) error {
	raw, e := sourceBody(w, r)
	if e != nil {
		return e
	}
	raw, e = contracts.Canonical(raw)
	if e != nil {
		return e
	}
	return json.Unmarshal(raw, value)
}
