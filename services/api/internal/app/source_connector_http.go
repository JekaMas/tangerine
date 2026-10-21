package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"net/http"
	"strconv"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
)

func (s *Server) sourceConnectorPut(w http.ResponseWriter, r *http.Request) {
	body, e := sourceBody(w, r)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	var input map[string]any
	if json.Unmarshal(body, &input) != nil {
		sourceHTTPError(w, ErrInput)
		return
	}
	requestSHA := contracts.Digest(sourceBytes(input))
	secret, _ := input["credential_value"].(string)
	delete(input, "credential_value")
	_, b, e := contracts.Validate("connector-request", "2.0.0", sourceBytes(input))
	if e != nil {
		sourceHTTPError(w, ErrInput)
		return
	}
	_ = json.Unmarshal(b, &input)
	id := r.PathValue("id")
	if _, e = uuid.Parse(id); e != nil {
		sourceHTTPError(w, ErrInput)
		return
	}
	if !source.Known(input["source_id"].(string)) {
		sourceHTTPError(w, ErrInput)
		return
	}
	if value := input["remote_spec"]; value != nil {
		var p source.RemoteSpec
		if e = json.Unmarshal(sourceBytes(value), &p); e != nil {
			sourceHTTPError(w, ErrInput)
			return
		}
		hosts := []string{}
		for _, v := range input["allowed_hosts"].([]any) {
			hosts = append(hosts, v.(string))
		}
		if e = source.ValidateRemote(p, hosts); e != nil {
			sourceHTTPError(w, e)
			return
		}
	}
	revision := int64(0)
	if h := r.Header.Get("If-Match"); h != "" {
		revision, e = strconv.ParseInt(strings.Trim(h, "\""), 10, 64)
		if e != nil {
			sourceHTTPError(w, ErrRevision)
			return
		}
	}
	conn, e := s.Store.DB.Acquire(r.Context())
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	defer conn.Release()
	tx, e := beginWriteOn(r.Context(), conn)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	defer tx.Rollback(context.Background())
	var acquired bool
	if e = tx.QueryRow(r.Context(), "SELECT pg_try_advisory_xact_lock(hashtextextended($1,79004771))", id).Scan(&acquired); e != nil || !acquired {
		sourceHTTPError(w, ErrEvaluationActive)
		return
	}
	var current int64
	var previousSHA *string
	exists := false
	e = tx.QueryRow(r.Context(), "SELECT revision,request_sha256 FROM source_connector WHERE id=$1 FOR UPDATE", id).Scan(&current, &previousSHA)
	exists = e == nil
	if e == nil && previousSHA != nil && *previousSHA == requestSHA {
		if e = tx.Commit(r.Context()); e != nil {
			sourceHTTPError(w, e)
			return
		}
		w.Header().Set("ETag", strconv.FormatInt(current, 10))
		writeJSON(w, 200, sourceStatusBase(input["source_id"].(string)))
		return
	}
	if e == nil && current != revision {
		sourceHTTPError(w, ErrRevision)
		return
	}
	if e != nil && !sourceNotFound(e) {
		sourceHTTPError(w, e)
		return
	}
	if secret != "" {
		ref, err := s.saveSourceCredential(id, secret)
		if err != nil {
			sourceHTTPError(w, err)
			return
		}
		input["credential_ref"] = ref
	}
	if ref, ok := input["credential_ref"].(string); ok {
		if _, e = sourceCredentialName(id, ref); e != nil {
			sourceHTTPError(w, e)
			return
		}
	}

	tag, e := tx.Exec(r.Context(), "INSERT INTO source_connector(id,source_id,payload,revision,request_sha256) VALUES($1,$2,$3,0,$5) ON CONFLICT(id) DO UPDATE SET source_id=excluded.source_id,payload=excluded.payload,revision=source_connector.revision+1,export_progress=NULL,request_sha256=excluded.request_sha256 WHERE source_connector.revision=$4", id, input["source_id"], sourceBytes(input), revision, requestSHA)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	if tag.RowsAffected() != 1 {
		sourceHTTPError(w, ErrRevision)
		return
	}
	if e = tx.Commit(r.Context()); e != nil {
		sourceHTTPError(w, e)
		return
	}
	if exists {
		w.Header().Set("ETag", strconv.FormatInt(current+1, 10))
	} else {
		w.Header().Set("ETag", "0")
	}
	result := sourceStatusBase(input["source_id"].(string))
	result["reasons"] = []string{"Documented connector saved; export bytes remain a separate explicit fetch."}
	writeJSON(w, 200, result)
}
func (s *Server) sourceConnectorFetch(w http.ResponseWriter, r *http.Request) {
	id, ok := strings.CutSuffix(r.PathValue("action"), ":fetch")
	if !ok {
		sourceHTTPError(w, ErrInput)
		return
	}
	p, e := s.FetchSourceExport(r.Context(), id, s.client)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, map[string]any{"files": p.Files, "pages": p.Pages, "observed_records": sourceNumber(p.Count), "expected_records": p.Expected, "complete": p.Complete, "conflicts": p.Conflicts})
}
