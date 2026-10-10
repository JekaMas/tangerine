package app

import (
	"context"
	"errors"
	"io"
	"net"
	"net/http"
	"strconv"
	"strings"
	"time"
)

// Host-native probe, built by Docker. Normal users need no host language runtime.
func CheckLabPublic(ctx context.Context, port string, available bool) error {
	n, e := strconv.Atoi(port)
	if e != nil || n < 1024 || n > 65535 {
		return errors.New("LAB_PORT_INVALID")
	}
	address := net.JoinHostPort("127.0.0.1", port)
	if available {
		listener, e := net.Listen("tcp", address)
		if e != nil {
			return errors.New("LAB_PORT_OCCUPIED")
		}
		return listener.Close()
	}
	client := http.Client{Timeout: 6 * time.Second, Transport: &http.Transport{Proxy: nil}, CheckRedirect: func(*http.Request, []*http.Request) error { return errors.New("redirected local Lab") }}
	req, e := http.NewRequestWithContext(ctx, "GET", "http://"+address+"/version", nil)
	if e != nil {
		return e
	}
	res, e := client.Do(req)
	if e != nil {
		return errors.New("LAB_UNAVAILABLE")
	}
	defer res.Body.Close()
	body, e := io.ReadAll(io.LimitReader(res.Body, 256))
	if e != nil || res.StatusCode != 200 || strings.TrimSpace(string(body)) != "3.17.0" {
		return errors.New("LAB_WRONG_SERVICE")
	}
	return nil
}
