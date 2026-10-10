package provider

import (
	"context"
	"encoding/json"
	"testing"
)

// The actual Manager consumes controlled metadata/remote protocol boundaries.
// These tests do not prove PostgreSQL durability or actual hosted admission.
func TestProviderUsageMarkLimitedPositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	if err := f.m.Mark(context.Background(), c.ID, "usage_limited", "subscription_sharing_usage_limit_exceeded"); err != nil {
		t.Fatal(err)
	}
	got := f.repo.rows[c.ID]
	if got.State != "usage_limited" || got.LastError == nil || *got.LastError != "subscription_sharing_usage_limit_exceeded" || f.repo.active != c.ID || got.CredentialRef == nil {
		t.Fatal("valid quota marker lost", got)
	}
}
func TestProviderUsageMarkUnavailablePositive(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	if err := f.m.Mark(context.Background(), c.ID, "unavailable", "subscription_sharing_usage_unavailable"); err != nil {
		t.Fatal(err)
	}
	got := f.repo.rows[c.ID]
	if got.State != "unavailable" || got.LastError == nil || *got.LastError != "subscription_sharing_usage_unavailable" || f.repo.active != c.ID || got.CredentialRef == nil {
		t.Fatal("valid unavailable marker lost", got)
	}
}
func TestProviderUsageMarkDisconnectedNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	f.status = 503
	if _, err := f.m.Disconnect(context.Background(), c.ID); err != nil {
		t.Fatal(err)
	}
	before, _ := json.Marshal(f.repo.rows[c.ID])
	if err := f.m.Mark(context.Background(), c.ID, "usage_limited", "subscription_sharing_usage_limit_exceeded"); err != nil {
		t.Fatal(err)
	}
	after, _ := json.Marshal(f.repo.rows[c.ID])
	if string(after) != string(before) || f.repo.active != "" {
		t.Fatal("late quota overwrote disconnect/revocation warning", string(after))
	}
}
func TestProviderUsageMarkNoUsageNegative(t *testing.T) {
	f := newFixture(t)
	f.connect(t, "", yes())
	c := f.callback(t)
	disabled := false
	if _, err := f.m.Select(context.Background(), c.ID, &disabled); err != nil {
		t.Fatal(err)
	}
	before, _ := json.Marshal(f.repo.rows[c.ID])
	if err := f.m.Mark(context.Background(), c.ID, "unavailable", "subscription_sharing_usage_unavailable"); err != nil {
		t.Fatal(err)
	}
	after, _ := json.Marshal(f.repo.rows[c.ID])
	if string(after) != string(before) || f.repo.active != c.ID {
		t.Fatal("late quota overwrote revoked usage confirmation", string(after))
	}
}
