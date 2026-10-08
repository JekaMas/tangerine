package app

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"time"

	"github.com/jackc/pgx/v5"
)

const OverallDeadline = 270 * time.Second
const SessionCookie = "tangerine_session"

type Server struct {
	Store     *Storage
	Origin    string
	SpeechURL string
	client    *http.Client
}

func NewServer(store *Storage, origin, speechURL string) *Server {
	return &Server{Store: store, Origin: origin, SpeechURL: speechURL, client: &http.Client{Timeout: 5 * time.Second}}
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}

func DecodeJSON(w http.ResponseWriter, r *http.Request, dst any) error {
	if r.Header.Get("Content-Type") != "application/json" {
		return errors.New("JSON content type required")
	}
	r.Body = http.MaxBytesReader(w, r.Body, 16*1024)
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(dst); err != nil {
		return errors.New("invalid request")
	}
	if err := decoder.Decode(new(any)); err != io.EOF {
		return errors.New("single JSON object required")
	}
	return nil
}

func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health/live", func(w http.ResponseWriter, r *http.Request) { writeJSON(w, 200, map[string]string{"status": "alive"}) })
	mux.HandleFunc("GET /health/ready", s.ready)
	mux.HandleFunc("POST /api/auth/login", s.login)
	mux.HandleFunc("POST /api/auth/logout", s.logout)
	mux.HandleFunc("GET /api/auth/session", s.session)
	mux.HandleFunc("GET /api/exercises", s.exercises)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		if r.Method != "GET" && r.Method != "HEAD" {
			if r.Header.Get("Origin") != s.Origin || r.Header.Get("Sec-Fetch-Site") == "cross-site" {
				writeJSON(w, 403, map[string]string{"error": "origin_denied"})
				return
			}
		}
		ctx, cancel := context.WithTimeout(r.Context(), OverallDeadline)
		defer cancel()
		mux.ServeHTTP(w, r.WithContext(ctx))
	})
}

func (s *Server) ready(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
	defer cancel()
	if s.Store.CheckDatabase(ctx) != nil || s.Store.CheckPrivateMedia(ctx) != nil {
		writeJSON(w, 503, map[string]string{"status": "unavailable"})
		return
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, s.SpeechURL+"/health/ready", nil)
	if err != nil {
		writeJSON(w, 503, map[string]string{"status": "unavailable"})
		return
	}
	res, err := s.client.Do(req)
	if err != nil {
		writeJSON(w, 503, map[string]string{"status": "unavailable"})
		return
	}
	defer res.Body.Close()
	if res.StatusCode != 200 {
		writeJSON(w, 503, map[string]string{"status": "unavailable"})
		return
	}
	writeJSON(w, 200, map[string]string{"status": "ready"})
}

func (s *Server) login(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}
	if DecodeJSON(w, r, &input) != nil || len(input.Email) > 254 || len(input.Password) > 1024 {
		writeJSON(w, 400, map[string]string{"error": "invalid_request"})
		return
	}
	var id, hash string
	err := s.Store.DB.QueryRow(r.Context(), "SELECT id::text,password_hash FROM accounts WHERE email=$1", input.Email).Scan(&id, &hash)
	if err != nil && !errors.Is(err, pgx.ErrNoRows) {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return
	}
	if errors.Is(err, pgx.ErrNoRows) {
		// Equal-cost derivation on account miss, without a fake account row.
		_, _ = HashPassword("unavailable-account-password")
		writeJSON(w, 401, map[string]string{"error": "invalid_credentials"})
		return
	}
	if !VerifyPassword(hash, input.Password) {
		writeJSON(w, 401, map[string]string{"error": "invalid_credentials"})
		return
	}
	token, tokenHash, err := NewSessionToken()
	if err != nil {
		writeJSON(w, 503, map[string]string{"error": "session_unavailable"})
		return
	}
	_, err = s.Store.DB.Exec(r.Context(), "INSERT INTO sessions(token_hash,account_id,expires_at) VALUES($1,$2,now()+interval '12 hours')", tokenHash, id)
	if err != nil {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return
	}
	http.SetCookie(w, &http.Cookie{Name: SessionCookie, Value: token, Path: "/", HttpOnly: true, SameSite: http.SameSiteStrictMode, MaxAge: 12 * 3600})
	writeJSON(w, 200, map[string]string{"status": "authenticated"})
}

func (s *Server) account(r *http.Request) (string, error) {
	c, err := r.Cookie(SessionCookie)
	if err != nil || !ValidSessionToken(c.Value) {
		return "", pgx.ErrNoRows
	}
	var email string
	err = s.Store.DB.QueryRow(r.Context(), "SELECT a.email FROM accounts a JOIN sessions s ON a.id=s.account_id WHERE s.token_hash=$1 AND s.expires_at>now()", TokenHash(c.Value)).Scan(&email)
	return email, err
}

func (s *Server) requireAccount(w http.ResponseWriter, r *http.Request) (string, bool) {
	email, err := s.account(r)
	if errors.Is(err, pgx.ErrNoRows) {
		writeJSON(w, 401, map[string]string{"error": "authentication_required"})
		return "", false
	}
	if err != nil {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return "", false
	}
	return email, true
}

func (s *Server) session(w http.ResponseWriter, r *http.Request) {
	email, ok := s.requireAccount(w, r)
	if !ok {
		return
	}
	writeJSON(w, 200, map[string]string{"email": email})
}

func (s *Server) logout(w http.ResponseWriter, r *http.Request) {
	if _, ok := s.requireAccount(w, r); !ok {
		return
	}
	c, _ := r.Cookie(SessionCookie)
	if _, err := s.Store.DB.Exec(r.Context(), "DELETE FROM sessions WHERE token_hash=$1", TokenHash(c.Value)); err != nil {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return
	}
	http.SetCookie(w, &http.Cookie{Name: SessionCookie, Value: "", Path: "/", HttpOnly: true, SameSite: http.SameSiteStrictMode, MaxAge: -1})
	writeJSON(w, 200, map[string]string{"status": "signed_out"})
}

func (s *Server) exercises(w http.ResponseWriter, r *http.Request) {
	if _, ok := s.requireAccount(w, r); !ok {
		return
	}
	rows, err := s.Store.DB.Query(r.Context(), "SELECT id::text,title,published_at FROM exercise_catalog ORDER BY published_at DESC,id LIMIT 100")
	if err != nil {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return
	}
	defer rows.Close()
	type summary struct {
		ID          string    `json:"id"`
		Title       string    `json:"title"`
		PublishedAt time.Time `json:"published_at"`
	}
	items := make([]summary, 0)
	for rows.Next() {
		var item summary
		if rows.Scan(&item.ID, &item.Title, &item.PublishedAt) != nil {
			writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
			return
		}
		items = append(items, item)
	}
	if rows.Err() != nil {
		writeJSON(w, 503, map[string]string{"error": "storage_unavailable"})
		return
	}
	writeJSON(w, 200, map[string]any{"exercises": items})
}
