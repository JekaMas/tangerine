package app

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestOriginAcceptsLocalOrigin(t *testing.T) {
	if ValidateOrigin("http://localhost:3000") != nil {
		t.Fatal("configured origin rejected")
	}
}
func TestOriginRejectsForeignOrigin(t *testing.T) {
	for _, input := range []string{"", "http://localhost:3000.attacker.invalid", "http://user@localhost:3000", "http://localhost:3000/path", "http://localhost:3000?x=y", "https://localhost:3000"} {
		if ValidateOrigin(input) == nil {
			t.Fatal("invalid origin accepted")
		}
	}
}
func TestJSONAcceptsClosedSingleObject(t *testing.T) {
	r := httptest.NewRequest(http.MethodPost, "/api/v1/unknown", strings.NewReader(`{"email":"input@example.invalid"}`))
	r.Header.Set("Content-Type", "application/json")
	var value struct {
		Email string `json:"email"`
	}
	if DecodeJSON(httptest.NewRecorder(), r, &value) != nil || value.Email != "input@example.invalid" {
		t.Fatal("valid protocol input rejected")
	}
}
func TestJSONRejectsTrailingAndOversizedInput(t *testing.T) {
	for _, body := range []string{`{} {}`, `{"email":"` + strings.Repeat("a", 17000) + `"}`, `not-json`} {
		r := httptest.NewRequest(http.MethodPost, "/api/v1/unknown", strings.NewReader(body))
		r.Header.Set("Content-Type", "application/json")
		var value struct {
			Email string `json:"email"`
		}
		if DecodeJSON(httptest.NewRecorder(), r, &value) == nil {
			t.Fatal("invalid body accepted")
		}
	}
}
func TestLivenessWithoutSubstituteStorage(t *testing.T) {
	s := NewServer(nil, "http://localhost:3000", "")
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/health/live", nil))
	if w.Code != 200 || !strings.Contains(w.Body.String(), "alive") {
		t.Fatal("liveness failed")
	}
}
func TestCrossOriginMutationDeniedBeforeStorage(t *testing.T) {
	s := NewServer(nil, "http://localhost:3000", "")
	w := httptest.NewRecorder()
	r := httptest.NewRequest(http.MethodPost, "/api/v1/unknown", strings.NewReader("{}"))
	r.Header.Set("Origin", "http://foreign.invalid")
	s.Handler().ServeHTTP(w, r)
	if w.Code != 403 || !strings.Contains(w.Body.String(), "origin_denied") {
		t.Fatal("cross-origin mutation reached storage")
	}
}
func TestMissingInternalCredentialDenied(t *testing.T) {
	s := NewServer(nil, "http://localhost:3000", "")
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/api/v1/library", nil))
	if w.Code != 403 {
		t.Fatal("internal credential boundary admitted an untrusted caller")
	}
}
func TestJSONAcceptsAdditiveFields(t *testing.T) {
	r := httptest.NewRequest(http.MethodPost, "/api/v1/unknown", strings.NewReader(`{"known":"ok","future":1}`))
	r.Header.Set("Content-Type", "application/json")
	var value struct {
		Known string `json:"known"`
	}
	if DecodeJSON(httptest.NewRecorder(), r, &value) != nil || value.Known != "ok" {
		t.Fatal("additive fields rejected")
	}
}
