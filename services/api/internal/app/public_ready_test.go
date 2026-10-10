package app

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestPublicReadyIdentityPositive(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/health/ready" || r.Method != "GET" || r.Header.Get("Authorization") != "" {
			t.Error("wrong path, method or disclosed credential")
		}
		w.Header().Set("X-Tangerine-Instance", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
		w.WriteHeader(200)
	}))
	defer server.Close()
	if err := CheckPublicReady(context.Background(), server.URL+"/health/ready", "abc"); err != nil {
		t.Fatal(err)
	}
}

func TestPublicReadyForeignOrUnavailableNegative(t *testing.T) {
	for _, row := range []struct {
		name     string
		status   int
		identity string
	}{
		{"foreign", 200, "foreign-installation"}, {"missing", 200, ""},
		{"unavailable", 503, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
		{"redirect", 302, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
	} {
		t.Run(row.name, func(t *testing.T) {
			calls := 0
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				calls++
				if r.Header.Get("Authorization") != "" {
					t.Error("credential disclosed")
				}
				w.Header().Set("X-Tangerine-Instance", row.identity)
				w.Header().Set("Location", "/other")
				w.WriteHeader(row.status)
			}))
			defer server.Close()
			if CheckPublicReady(context.Background(), server.URL+"/health/ready", "abc") == nil {
				t.Fatal("false ready")
			}
			if calls != 1 {
				t.Fatal("redirect followed")
			}
		})
	}
	if CheckPublicReady(context.Background(), "http://127.0.0.1:1", "abc") == nil {
		t.Fatal("unreachable ready")
	}
	if CheckPublicReady(context.Background(), "http://127.0.0.1:1", "") == nil {
		t.Fatal("missing identity accepted")
	}
}
