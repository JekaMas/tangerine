package app

import (
	"context"
	"crypto/subtle"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"tangerine.local/api/internal/provider"
	"time"
)

const OverallDeadline = 270 * time.Second
const ReleaseID = "0.1.0-foundation"

type Server struct {
	qualityCancels sync.Map
	Store          *Storage
	Origin         string
	SpeechURL      string
	client         *http.Client
	token          string
	speechToken    string
	Providers      *provider.Manager
}

func NewServer(store *Storage, origin, speechURL string) *Server {
	return &Server{Store: store, Origin: origin, SpeechURL: speechURL, client: &http.Client{Timeout: 5 * time.Second}, token: os.Getenv("API_INTERNAL_TOKEN"), speechToken: os.Getenv("SPEECH_INTERNAL_TOKEN"), Providers: newProviderManager(store)}
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
	mux.HandleFunc("GET /api/v1/audio-diagnostics/defaults", func(w http.ResponseWriter, r *http.Request) { writeJSON(w, 200, audioDiagnosticDefaults()) })
	mux.HandleFunc("GET /api/v1/cases/{id}/measurements", s.audioDiagnosticList)
	mux.HandleFunc("POST /api/v1/cases/{id}/measurements", s.audioDiagnosticCreate)
	mux.HandleFunc("POST /api/v1/deletions", s.deletionCreate)
	mux.HandleFunc("POST /api/v1/deletions/{action}", s.deletionApply)
	mux.HandleFunc("GET /api/v1/lab/experiments", s.qualityList)
	mux.HandleFunc("POST /api/v1/lab/experiments", s.qualityCreate)
	mux.HandleFunc("GET /api/v1/lab/experiments/{id}", s.qualityGet)
	mux.HandleFunc("POST /api/v1/lab/experiments/{action}", s.qualityAction)
	mux.HandleFunc("GET /api/v1/lab/defaults", s.qualityDefaults)
	mux.HandleFunc("GET /api/v1/lab/assets/{id}", s.qualityAsset)
	mux.HandleFunc("GET /api/v1/reports/empirical", s.empiricalList)
	mux.HandleFunc("POST /api/v1/reports/empirical", s.empiricalCreate)
	mux.HandleFunc("GET /api/v1/reports/empirical/{id}", s.empiricalGet)
	mux.HandleFunc("GET /api/v1/sources", s.sourcesGet)
	mux.HandleFunc("PUT /api/v1/connectors/{id}", s.sourceConnectorPut)
	mux.HandleFunc("POST /api/v1/connectors/{action}", s.sourceConnectorFetch)
	mux.HandleFunc("POST /api/v1/source-files", s.sourceUpload)
	mux.HandleFunc("GET /api/v1/sources/assets/{id}/bytes", s.sourceFileGet)
	mux.HandleFunc("POST /api/v1/source-releases", s.sourceReleaseCreate)
	mux.HandleFunc("GET /api/v1/source-releases/{id}", s.sourceReleaseGet)
	mux.HandleFunc("POST /api/v1/source-releases/{action}", s.sourceReleaseAction)
	mux.HandleFunc("POST /api/v1/source-formats", s.sourceFormatCreate)
	mux.HandleFunc("POST /api/v1/permissions", s.sourcePermissionCreate)
	mux.HandleFunc("POST /api/v1/permissions/{action}", s.sourcePermissionRevoke)
	mux.HandleFunc("GET /api/v1/imports/{id}", s.sourceImportGet)
	mux.HandleFunc("GET /api/v1/imports/{id}/progress", s.sourceProgressGet)
	mux.HandleFunc("GET /api/v1/imports/{id}/records", s.sourceRowsGet)
	mux.HandleFunc("GET /api/v1/imports/{id}/corrections", s.sourceCorrectionsGet)
	mux.HandleFunc("GET /api/v1/imports/{id}/issues", s.sourceIssuesGet)
	mux.HandleFunc("POST /api/v1/imports/{action}", s.sourceImportAction)
	mux.HandleFunc("POST /api/v1/reviews", s.reviewCreate)
	mux.HandleFunc("GET /api/v1/reviews", s.reviewList)
	mux.HandleFunc("GET /api/v1/reviews/{id}", s.reviewGet)
	mux.HandleFunc("POST /api/v1/reviews/{action}", s.reviewRun)
	mux.HandleFunc("POST /api/v1/attempts", s.attemptStart)
	mux.HandleFunc("GET /api/v1/attempts", s.attemptList)
	mux.HandleFunc("GET /api/v1/attempts/{id}", s.attemptGet)
	mux.HandleFunc("PUT /api/v1/attempts/{id}/answer", func(w http.ResponseWriter, r *http.Request) { s.attemptAnswer(w, r, false) })
	mux.HandleFunc("POST /api/v1/attempts/{action}", func(w http.ResponseWriter, r *http.Request) {
		if id, ok := strings.CutSuffix(r.PathValue("action"), ":retry-feedback"); ok {
			r.SetPathValue("id", id)
			s.attemptInterpretationRetry(w, r)
			return
		}
		if id, ok := strings.CutSuffix(r.PathValue("action"), ":retry"); ok {
			r.SetPathValue("id", id)
			s.attemptInterpretationRetry(w, r)
			return
		}
		id, ok := strings.CutSuffix(r.PathValue("action"), ":submit")
		if !ok {
			preparationHTTPError(w, 404, "NOT_FOUND")
			return
		}
		r.SetPathValue("id", id)
		s.attemptAnswer(w, r, true)
	})
	mux.HandleFunc("POST /api/v1/attempts/{id}/playback", s.attemptPlaybackEvent)
	mux.HandleFunc("GET /api/v1/attempts/{id}/audio", s.attemptAudio)
	mux.HandleFunc("GET /api/v1/attempts/{id}/results", s.attemptResults)
	mux.HandleFunc("GET /api/v1/preparations", s.preparationList)
	mux.HandleFunc("GET /api/v1/preparation-options", s.preparationOptions)
	mux.HandleFunc("POST /api/v1/candidates:generate", s.generateExercise)
	mux.HandleFunc("POST /api/v1/preparations/{action}", func(w http.ResponseWriter, r *http.Request) {
		if id, ok := strings.CutSuffix(r.PathValue("action"), ":resume"); ok {
			r.SetPathValue("id", id)
			s.resumeExercise(w, r)
			return
		}
		id, ok := strings.CutSuffix(r.PathValue("action"), ":render")
		if !ok {
			preparationHTTPError(w, 404, "NOT_FOUND")
			return
		}
		r.SetPathValue("id", id)
		s.speechRender(w, r)
	})
	mux.HandleFunc("GET /api/v1/preparations/{id}/audio", s.speechPlayback)
	mux.HandleFunc("POST /api/v1/blueprints", s.blueprintWrite)
	mux.HandleFunc("GET /api/v1/blueprints/{id}", s.blueprintGet)
	mux.HandleFunc("GET /api/v1/configuration", s.configurationGet)
	mux.HandleFunc("PUT /api/v1/configuration", s.configurationPut)
	mux.HandleFunc("GET /api/v1/provider-connections", s.providerConnections)
	mux.HandleFunc("POST /api/v1/provider-connections:action", s.providerAction)
	mux.HandleFunc("GET /auth/callback", s.providerCallback)
	mux.HandleFunc("GET /api/v1/prepare/assets/{id}/bytes", s.providerModelBytes)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		alternate := strings.Replace(s.Origin, "localhost", "127.0.0.1", 1)
		if alternate == s.Origin {
			alternate = strings.Replace(s.Origin, "127.0.0.1", "localhost", 1)
		}
		if r.Method != "GET" && r.Method != "HEAD" && ((r.Header.Get("Origin") != s.Origin && r.Header.Get("Origin") != alternate) || r.Header.Get("Sec-Fetch-Site") == "cross-site") {
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

	type dependencyResult struct {
		name   string
		status string
	}
	results := make(chan dependencyResult, 4)
	go func() { results <- dependencyResult{"provider_configuration", s.providerReadiness(ctx)} }()
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
	for range 4 {
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
	ID            string     `json:"id"`
	Title         string     `json:"title"`
	PublicContext string     `json:"public_context"`
	DurationMS    int        `json:"duration_ms"`
	Format        string     `json:"format"`
	Difficulty    string     `json:"difficulty"`
	Availability  string     `json:"availability"`
	CaseSHA256    *string    `json:"case_sha256,omitempty"`
	AudioSHA256   *string    `json:"audio_sha256,omitempty"`
	CreatedAt     *time.Time `json:"created_at,omitempty"`
}

func (s *Server) library(w http.ResponseWriter, r *http.Request) {
	rows, err := s.Store.DB.Query(r.Context(), `SELECT c.id::text,c.title,c.public_context,c.duration_ms,c.format,c.difficulty,c.availability,l.case_sha256,l.audio_sha256,d.created_at FROM exercise_catalog c LEFT JOIN listening_case l ON l.case_version_id=c.id::text LEFT JOIN document d ON d.id=c.id::text WHERE public_context IS NOT NULL AND duration_ms IS NOT NULL AND format IS NOT NULL AND difficulty IS NOT NULL AND availability IN ('published','retired','quarantined','rights_restricted') ORDER BY published_at DESC,c.id`)
	if err != nil {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return
	}
	defer rows.Close()
	items := make([]LibraryItem, 0)
	for rows.Next() {
		var x LibraryItem
		if rows.Scan(&x.ID, &x.Title, &x.PublicContext, &x.DurationMS, &x.Format, &x.Difficulty, &x.Availability, &x.CaseSHA256, &x.AudioSHA256, &x.CreatedAt) != nil {
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
