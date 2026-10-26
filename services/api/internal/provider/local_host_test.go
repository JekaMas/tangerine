package provider

import (
	"context"
	"io"
	"net/http"
	"strings"
	"testing"
)

type hostProbe func(*http.Request) (*http.Response, error)

func (f hostProbe) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }

func observeHost(t *testing.T, endpoint string, want string) {
	t.Helper()
	p := planProfile()
	p.Provider = "local_responses"
	p.Auth = "local_none"
	p.Billing = "local"
	p.Endpoint = endpoint
	p.Stream = false
	client := &http.Client{Transport: hostProbe(func(r *http.Request) (*http.Response, error) {
		if r.Host != want || r.URL.String() != endpoint || r.Header.Get("Authorization") != "" {
			t.Fatalf("host/target/auth changed: %q %s", r.Host, r.URL)
		}
		return &http.Response{StatusCode: 200, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(`{"status":"completed","output":[{"type":"message","content":[{"type":"output_text","text":"{}"}]}]}`))}, nil
	})}
	if _, e := Exchange(context.Background(), client, p, []byte(`{}`), ""); e != nil {
		t.Fatal(e)
	}
}

func TestLocalAliasHostPositive(t *testing.T) {
	for _, alias := range []string{"ollama"} {
		t.Run(alias, func(t *testing.T) { observeHost(t, "http://"+alias+":11434/v1/responses", "localhost:11434") })
	}
}
func TestLocalLoopbackHostNegative(t *testing.T) {
	for _, host := range []string{"127.0.0.1", "localhost", "llm-local"} {
		t.Run(host, func(t *testing.T) { observeHost(t, "http://"+host+":11434/v1/responses", host+":11434") })
	}
}
