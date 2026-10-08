package app

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// NO_TEST_DOUBLE: controlled inputs exercise real password/token/parser owners.
// These tests do not establish DB persistence, browser or provider acceptance.
func TestPasswordAcceptsCorrectSecret(t *testing.T) {
	password := "controlled-infrastructure-password"
	hash, err := HashPassword(password)
	if err != nil {
		t.Fatal(err)
	}
	if !VerifyPassword(hash, password) {
		t.Fatal("correct password rejected")
	}
	second, err := HashPassword(password)
	if err != nil {
		t.Fatal(err)
	}
	if hash == second {
		t.Fatal("password salts reused")
	}
}
func TestPasswordRejectsWrongAndMalformedSecret(t *testing.T) {
	hash, err := HashPassword("controlled-infrastructure-password")
	if err != nil {
		t.Fatal(err)
	}
	if VerifyPassword(hash, "different-infrastructure-password") {
		t.Fatal("wrong password accepted")
	}
	for _, input := range []string{"", "pbkdf2-sha256:1:x:y", "pbkdf2-sha256:600000:eA:eQ"} {
		if VerifyPassword(input, "any") {
			t.Fatal("invalid stored hash accepted")
		}
	}
	if _, err := HashPassword("short"); err == nil {
		t.Fatal("weak initial secret accepted")
	}
}
func TestTokenAcceptsCanonicalRandomToken(t *testing.T) {
	token, hash, err := NewSessionToken()
	if err != nil {
		t.Fatal(err)
	}
	if !ValidSessionToken(token) || hash != TokenHash(token) || len(hash) != 64 {
		t.Fatal("token contract violated")
	}
	second, _, err := NewSessionToken()
	if err != nil || token == second {
		t.Fatal("random token not distinct")
	}
}
func TestTokenRejectsInvalidOrChangedToken(t *testing.T) {
	for _, input := range []string{"", "abc", strings.Repeat("A", 44), strings.Repeat("A", 43) + "="} {
		if ValidSessionToken(input) {
			t.Fatal("invalid token accepted")
		}
	}
	if TokenHash("first") == TokenHash("second") {
		t.Fatal("changed token retained identity")
	}
}
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
	r := httptest.NewRequest(http.MethodPost, "/api/auth/login", strings.NewReader(`{"email":"input@example.invalid"}`))
	r.Header.Set("Content-Type", "application/json")
	var value struct {
		Email string `json:"email"`
	}
	if DecodeJSON(httptest.NewRecorder(), r, &value) != nil || value.Email != "input@example.invalid" {
		t.Fatal("valid protocol input rejected")
	}
}
func TestJSONRejectsUnknownTrailingAndOversizedInput(t *testing.T) {
	for _, body := range []string{`{"extra":1}`, `{} {}`, `{"email":"` + strings.Repeat("a", 17000) + `"}`, `not-json`} {
		r := httptest.NewRequest(http.MethodPost, "/api/auth/login", strings.NewReader(body))
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
	r := httptest.NewRequest(http.MethodPost, "/api/auth/login", strings.NewReader("{}"))
	r.Header.Set("Origin", "http://foreign.invalid")
	s.Handler().ServeHTTP(w, r)
	if w.Code != 403 || !strings.Contains(w.Body.String(), "origin_denied") {
		t.Fatal("cross-origin mutation reached storage")
	}
}
func TestUnauthenticatedLibraryDenied(t *testing.T) {
	s := NewServer(nil, "http://localhost:3000", "")
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/api/exercises", nil))
	if w.Code != 401 {
		t.Fatal("unauthenticated library access admitted")
	}
}
