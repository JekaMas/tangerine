package app

import (
	"encoding/json"
	"errors"
	"github.com/minio/minio-go/v7"
	"io"
	"log"
	"net/http"
	"strconv"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
)

func sourceBody(w http.ResponseWriter, r *http.Request) ([]byte, error) {
	r.Body = http.MaxBytesReader(w, r.Body, 512*1024*1024)
	b, e := io.ReadAll(r.Body)
	if e != nil {
		return nil, ErrInput
	}
	return b, nil
}
func sourceHTTPError(w http.ResponseWriter, e error) {
	status := 503
	code := sourceError(e)
	if errors.Is(e, ErrInput) || errors.Is(e, ErrReference) {
		status = 400
		code = "source_input_invalid"
	}
	if errors.Is(e, ErrConflict) || errors.Is(e, ErrRevision) || errors.Is(e, ErrEvaluationActive) || errors.Is(e, ErrEvaluationLease) {
		status = 409
		code = "source_action_conflict"
	}
	var issue source.Issue
	if errors.As(e, &issue) {
		switch issue.Code {
		case "unsafe_path", "unsafe_member", "duplicate_path", "archive_format", "archive_member", "archive_duplicate", "archive_link", "archive_type", "xlsx_member", "interface_missing", "host_denied", "remote_format":
			status = 400
		case "intake_limit":
			status = 413
		}
	}
	if sourceNotFound(e) {
		status = 404
		code = "source_not_found"
	}
	log.Printf("source request failed: code=%s cause=%v", code, e)
	writeJSON(w, status, map[string]string{"error": code})
}
func (s *Server) sourcesGet(w http.ResponseWriter, r *http.Request) {
	items, e := s.Store.SourceStatuses(r.Context())
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, items)
}
func (s *Server) sourceUpload(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	if r.URL.Query().Get("archive") == "true" || sourceKind(name) != "" && r.URL.Query().Get("archive") != "false" {
		files, e := s.Store.IntakeArchive(r.Context(), name, sourceKind(name), r.Body)
		if e != nil {
			sourceHTTPError(w, e)
			return
		}
		writeJSON(w, 201, files)
		return
	}
	m, e := s.Store.saveSourceStream(r.Context(), name, r.Body)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 201, []any{m})
}
func (s *Server) sourceReleaseCreate(w http.ResponseWriter, r *http.Request) {
	b, e := sourceBody(w, r)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	release, e := s.Store.RegisterSource(r.Context(), b, r.Header.Get("Idempotency-Key"))
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 201, release)
}
func (s *Server) sourceReleaseGet(w http.ResponseWriter, r *http.Request) {
	release, e := s.Store.SourceRelease(r.Context(), r.PathValue("id"))
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, release)
}
func (s *Server) sourceFormatCreate(w http.ResponseWriter, r *http.Request) {
	b, e := sourceBody(w, r)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	binding, e := s.Store.RegisterFormat(r.Context(), b)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 201, binding)
}
func (s *Server) sourcePermissionCreate(w http.ResponseWriter, r *http.Request) {
	b, e := sourceBody(w, r)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	p, e := s.Store.RegisterSourcePermission(r.Context(), b)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 201, p)
}
func (s *Server) sourcePermissionRevoke(w http.ResponseWriter, r *http.Request) {
	id, ok := strings.CutSuffix(r.PathValue("action"), ":revoke")
	if !ok {
		sourceHTTPError(w, ErrInput)
		return
	}
	var input struct {
		Notice string `json:"notice_asset_id"`
	}
	if e := DecodeJSON(w, r, &input); e != nil {
		sourceHTTPError(w, ErrInput)
		return
	}
	if e := s.Store.RevokeSourcePermission(r.Context(), id, input.Notice); e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, map[string]any{"state": "complete", "permission_id": id})
}
func (s *Server) sourceReleaseAction(w http.ResponseWriter, r *http.Request) {
	action := r.PathValue("action")
	id, preview := strings.CutSuffix(action, ":preview")
	if !preview {
		var ok bool
		id, ok = strings.CutSuffix(action, ":import")
		if !ok {
			sourceHTTPError(w, ErrInput)
			return
		}
	}
	b, e := sourceBody(w, r)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	_, b, e = contracts.Validate("import-request", "2.0.0", b)
	if e != nil {
		sourceHTTPError(w, ErrInput)
		return
	}
	var input struct {
		Release     string   `json:"release_id"`
		Binding     string   `json:"format_binding_id"`
		Permissions []string `json:"permission_ids"`
		Cursor      *string  `json:"continue_after_record"`
	}
	_ = json.Unmarshal(b, &input)
	if input.Release != id {
		sourceHTTPError(w, ErrReference)
		return
	}
	run, e := s.Store.createSourceImport(r.Context(), id, input.Binding, input.Permissions)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	revision := run.Revision
	if header := r.Header.Get("If-Match"); header != "" {
		revision, e = strconv.ParseInt(strings.Trim(header, "\""), 10, 64)
		if e != nil {
			sourceHTTPError(w, ErrRevision)
			return
		}
	}
	if input.Cursor != nil && *input.Cursor != sourceCursor(run.Member, run.Phase, run.Row) {
		sourceHTTPError(w, ErrRevision)
		return
	}
	run, e = s.Store.RunSourceImport(r.Context(), run.Report.ID, r.Header.Get("Idempotency-Key"), revision)
	if e != nil {
		w.Header().Set("X-Tangerine-Import-ID", run.Report.ID)
		sourceHTTPError(w, e)
		return
	}
	if !preview {
		if e = s.Store.CommitSourceImport(r.Context(), run.Report.ID); e != nil {
			sourceHTTPError(w, e)
			return
		}
	}
	sourceRunHeaders(w, run)
	writeJSON(w, 200, run.Report)
}
func (s *Server) sourceImportGet(w http.ResponseWriter, r *http.Request) {
	run, e := s.Store.SourceImport(r.Context(), r.PathValue("id"))
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	sourceRunHeaders(w, run)
	writeJSON(w, 200, run.Report)
}
func sourceRunHeaders(w http.ResponseWriter, run SourceRun) {
	w.Header().Set("X-Tangerine-Revision", strconv.FormatInt(run.Revision, 10))
	w.Header().Set("X-Tangerine-Import-ID", run.Report.ID)
	w.Header().Set("X-Tangerine-Import-Cursor", sourceCursor(run.Member, run.Phase, run.Row))
}
func (s *Server) sourceProgressGet(w http.ResponseWriter, r *http.Request) {
	run, e := s.Store.SourceImport(r.Context(), r.PathValue("id"))
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	sourceRunHeaders(w, run)
	writeJSON(w, 200, run)
}
func (s *Server) sourceImportAction(w http.ResponseWriter, r *http.Request) {
	id, ok := strings.CutSuffix(r.PathValue("action"), ":cancel")
	if !ok {
		sourceHTTPError(w, ErrInput)
		return
	}
	revision, e := strconv.ParseInt(strings.Trim(r.Header.Get("If-Match"), "\""), 10, 64)
	if e != nil {
		sourceHTTPError(w, ErrRevision)
		return
	}
	run, e := s.Store.CancelSource(r.Context(), id, revision)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	sourceRunHeaders(w, run)
	writeJSON(w, 200, run.Report)
}
func (s *Server) sourceRowsGet(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if _, e := s.Store.SourceImport(r.Context(), id); e != nil {
		sourceHTTPError(w, e)
		return
	}
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	rows, next, e := s.Store.SourceRows(r.Context(), id, r.URL.Query().Get("cursor"), limit)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, map[string]any{"items": rows, "next_cursor": next})
}
func (s *Server) sourceIssuesGet(w http.ResponseWriter, r *http.Request) {
	items, next, e := s.Store.SourceIssues(r.Context(), r.PathValue("id"), r.URL.Query().Get("cursor"))
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, map[string]any{"items": items, "next_cursor": next})
}
func (s *Server) sourceFileGet(w http.ResponseWriter, r *http.Request) {
	var key string
	e := s.Store.DB.QueryRow(r.Context(), "SELECT a.storage_key FROM source_file f JOIN asset_location a ON a.asset_id=f.asset_id WHERE f.asset_id=$1 LIMIT 1", r.PathValue("id")).Scan(&key)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	object, e := s.Store.Media.GetObject(r.Context(), s.Store.Bucket, key, minio.GetObjectOptions{})
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	defer object.Close()
	first := make([]byte, 32768)
	n, readErr := object.Read(first)
	if readErr != nil && readErr != io.EOF {
		sourceHTTPError(w, readErr)
		return
	}
	w.Header().Set("Content-Type", "application/octet-stream")
	w.Header().Set("Content-Disposition", "attachment")
	w.Header().Set("Content-Security-Policy", "sandbox")
	if n > 0 {
		_, _ = w.Write(first[:n])
	}
	_, _ = io.Copy(w, object)
}
