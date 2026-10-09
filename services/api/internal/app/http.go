package app

import (
	"context"
	"crypto/subtle"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"os"
	"time"
)

const OverallDeadline = 270 * time.Second
const ReleaseID = "0.1.0-foundation"

type Server struct {
	Store       *Storage
	Origin      string
	SpeechURL   string
	client      *http.Client
	token       string
	speechToken string
}

func NewServer(store *Storage, origin, speechURL string) *Server {
	return &Server{Store: store, Origin: origin, SpeechURL: speechURL, client: &http.Client{Timeout: 5 * time.Second}, token: os.Getenv("API_INTERNAL_TOKEN"), speechToken: os.Getenv("SPEECH_INTERNAL_TOKEN")}
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}

// Decode a single bounded transport object; harmless additive fields are ignored.
func DecodeJSON(w http.ResponseWriter, r *http.Request, dst any) error {
	if r.Header.Get("Content-Type") != "application/json" {
		return errors.New("JSON content type required")
	}
	r.Body = http.MaxBytesReader(w, r.Body, 16*1024)
	d := json.NewDecoder(r.Body)
	if err := d.Decode(dst); err != nil {
		return errors.New("invalid request")
	}
	if err := d.Decode(new(any)); err != io.EOF {
		return errors.New("single JSON object required")
	}
	return nil
}

func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health/live", func(w http.ResponseWriter, r *http.Request) { writeJSON(w, 200, map[string]string{"status": "alive"}) })
	mux.HandleFunc("GET /health/ready", s.ready)
	mux.HandleFunc("GET /api/v1/health", s.ready)
	mux.HandleFunc("GET /api/v1/library", s.library)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		if r.Method != "GET" && r.Method != "HEAD" && (r.Header.Get("Origin") != s.Origin || r.Header.Get("Sec-Fetch-Site") == "cross-site") {
			writeJSON(w, 403, map[string]string{"error": "origin_denied"})
			return
		}
		if r.URL.Path != "/health/live" && (s.token == "" || subtle.ConstantTimeCompare([]byte(r.Header.Get("Authorization")), []byte("Bearer "+s.token)) != 1) {
			writeJSON(w, 403, map[string]string{"error": "internal_access_required"})
			return
		}
		ctx, cancel := context.WithTimeout(r.Context(), OverallDeadline)
		defer cancel()
		mux.ServeHTTP(w, r.WithContext(ctx))
	})
}

func (s *Server) ready(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()
	h := map[string]string{"status": "ok", "database": "ready", "storage": "ready", "speech": "ready", "provider_configuration": "missing_credentials", "release_id": ReleaseID}
	if os.Getenv("DEEPSEEK_API_KEY") != "" || os.Getenv("OPENAI_API_KEY") != "" {
		h["provider_configuration"] = "ready"
	}
	type dependencyResult struct {
		name   string
		status string
	}
	results := make(chan dependencyResult, 3)
	go func() {
		status := "ready"
		if err := s.Store.CheckDatabase(ctx); err != nil {
			status = "unavailable"
			if errors.Is(err, ErrMigrationRequired) {
				status = "migration_required"
			}
		}
		results <- dependencyResult{"database", status}
	}()
	go func() {
		status := "ready"
		if s.Store.CheckPrivateMedia(ctx) != nil {
			status = "unavailable"
		}
		results <- dependencyResult{"storage", status}
	}()
	go func() {
		status := "unavailable"
		req, err := http.NewRequestWithContext(ctx, http.MethodGet, s.SpeechURL+"/health/ready", nil)
		if err == nil {
			req.Header.Set("Authorization", "Bearer "+s.speechToken)
			if res, e := s.client.Do(req); e == nil {
				res.Body.Close()
				if res.StatusCode == 200 {
					status = "ready"
				}
			}
		}
		results <- dependencyResult{"speech", status}
	}()
	for range 3 {
		result := <-results
		h[result.name] = result.status
	}
	code := 200
	if h["database"] != "ready" || h["storage"] != "ready" || h["speech"] != "ready" {
		code = 503
		h["status"] = "not_ready"
	}
	writeJSON(w, code, h)
}

type LibraryItem struct {
	ID            string `json:"id"`
	Title         string `json:"title"`
	PublicContext string `json:"public_context"`
	DurationMS    int    `json:"duration_ms"`
	Format        string `json:"format"`
	Difficulty    string `json:"difficulty"`
	Availability  string `json:"availability"`
}

func (s *Server) library(w http.ResponseWriter, r *http.Request) {
	rows, err := s.Store.DB.Query(r.Context(), `SELECT id::text,title,public_context,duration_ms,format,difficulty,availability FROM exercise_catalog WHERE public_context IS NOT NULL AND duration_ms IS NOT NULL AND format IS NOT NULL AND difficulty IS NOT NULL AND availability IN ('published','retired','quarantined','rights_restricted') ORDER BY published_at DESC,id`)
	if err != nil {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return
	}
	defer rows.Close()
	items := make([]LibraryItem, 0)
	for rows.Next() {
		var x LibraryItem
		if rows.Scan(&x.ID, &x.Title, &x.PublicContext, &x.DurationMS, &x.Format, &x.Difficulty, &x.Availability) != nil {
			writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
			return
		}
		items = append(items, x)
	}
	if rows.Err() != nil {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return
	}
	writeJSON(w, 200, items)
}
