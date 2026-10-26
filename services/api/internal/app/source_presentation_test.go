package app

import (
	"bytes"
	"errors"
	"log"
	"net/http/httptest"
	"strings"
	"tangerine.local/api/internal/source"
	"testing"
)

func TestSourceHTTPFailureLoggingPositive(t *testing.T) {
	var output bytes.Buffer
	previous := log.Writer()
	log.SetOutput(&output)
	t.Cleanup(func() { log.SetOutput(previous) })
	response := httptest.NewRecorder()
	sourceHTTPError(response, errors.New("constructed internal database cause"))
	if response.Code != 503 || strings.TrimSpace(response.Body.String()) != `{"error":"source_unavailable"}` {
		t.Fatalf("unexpected public failure: %d %s", response.Code, response.Body.String())
	}
	if !strings.Contains(output.String(), "constructed internal database cause") {
		t.Fatal("the original diagnostic cause was not logged")
	}
}

func TestSourceHTTPFailureMessageNegative(t *testing.T) {
	response := httptest.NewRecorder()
	sourceHTTPError(response, source.Issue{Code: "unsafe_path", Locator: "../constructed", Detail: "private native diagnostic"})
	if response.Code != 400 || strings.TrimSpace(response.Body.String()) != `{"error":"unsafe_path"}` {
		t.Fatalf("unsafe archive must retain its typed response without exposing diagnostics: %d %s", response.Code, response.Body.String())
	}
}
