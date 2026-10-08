package app

import (
	"context"
	"testing"
)

// Configuration admission before network I/O does not prove that storage exists.
func TestStorageConfigurationPositive(t *testing.T) {
	store, err := OpenStorage(context.Background(), "postgres://tangerine:local-secret@postgres:5432/tangerine", "minio:9000", "local-access", "local-secret", "tangerine-audio")
	if err != nil {
		t.Fatalf("valid local configuration rejected: %v", err)
	}
	defer store.DB.Close()
	if store.Bucket != "tangerine-audio" || store.DB.Config().MaxConns != 10 {
		t.Fatal("configured bucket or connection bound changed")
	}
}

func TestStorageConfigurationNegative(t *testing.T) {
	for _, databaseURL := range []string{"", "postgres://%"} {
		if _, err := OpenStorage(context.Background(), databaseURL, "minio:9000", "local-access", "local-secret", "tangerine-audio"); err == nil {
			t.Fatal("missing or malformed storage configuration accepted")
		}
	}
	// Invalid input must fail before storage access. Nil never simulates success.
	var store *Storage
	for _, input := range [][2]string{{"invalid-address", "long-local-password"}, {"owner@localhost", "short"}} {
		if err := store.InitializeAccount(context.Background(), input[0], input[1]); err == nil {
			t.Fatal("invalid initial account accepted")
		}
	}
}
