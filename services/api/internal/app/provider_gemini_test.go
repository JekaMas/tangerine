package app

import (
	"context"
	"tangerine.local/api/internal/provider"
	"testing"
)

func TestGeminiCredentialPositive(t *testing.T) {
	t.Setenv("GEMINI_API_KEY", "synthetic-free-project-key")
	p := provider.Profile{Provider: "gemini_interactions", Endpoint: provider.GeminiEndpoint, Auth: "api_key", Billing: "free_tier", CredentialRef: "GEMINI_API_KEY"}
	value, err := providerCredential(context.Background(), nil, p, p.CredentialRef)
	if err != nil || value != "synthetic-free-project-key" {
		t.Fatal("admitted free-project credential did not resolve", err)
	}
}

func TestGeminiCredentialNegative(t *testing.T) {
	t.Setenv("GEMINI_API_KEY", "")
	p := provider.Profile{Provider: "gemini_interactions", Endpoint: provider.GeminiEndpoint, Auth: "api_key", Billing: "free_tier", CredentialRef: "GEMINI_API_KEY"}
	if value, err := providerCredential(context.Background(), nil, p, p.CredentialRef); err == nil || value != "" {
		t.Fatal("absent key resolved")
	}
	t.Setenv("GEMINI_API_KEY", "synthetic-key")
	p.Billing = "metered"
	if value, err := providerCredential(context.Background(), nil, p, p.CredentialRef); err == nil || value != "" {
		t.Fatal("non-free profile resolved a credential")
	}
}
