package app

import (
	"net/http"
	"strconv"
)

func (s *Server) sourceCorrectionsGet(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	partition := r.URL.Query().Get("partition")
	if r.URL.Query().Get("format") == "dataset" {
		dataset, e := s.Store.SourceCorrectionDataset(r.Context(), id, partition)
		if e != nil {
			sourceHTTPError(w, e)
			return
		}
		w.Header().Set("Content-Disposition", "attachment; filename=\"jfleg-corrections.json\"")
		writeJSON(w, 200, dataset)
		return
	}
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	items, next, e := s.Store.SourceCorrectionExamples(r.Context(), id, r.URL.Query().Get("cursor"), partition, limit)
	if e != nil {
		sourceHTTPError(w, e)
		return
	}
	writeJSON(w, 200, map[string]any{"items": items, "next_cursor": next})
}
