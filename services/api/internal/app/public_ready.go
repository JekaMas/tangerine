package app

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
	"time"
)

// CheckPublicReady correlates the public listener without disclosing credentials.
func CheckPublicReady(ctx context.Context, url, token string) error {
	if token == "" {
		return fmt.Errorf("public readiness identity unavailable")
	}
	client := http.Client{Timeout: 8 * time.Second, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return fmt.Errorf("public readiness request unavailable")
	}
	res, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("public listener unavailable")
	}
	defer res.Body.Close()
	digest := sha256.Sum256([]byte(token))
	if res.StatusCode != http.StatusOK || res.Header.Get("X-Tangerine-Instance") != hex.EncodeToString(digest[:]) {
		return fmt.Errorf("public listener does not identify this ready installation")
	}
	return nil
}
