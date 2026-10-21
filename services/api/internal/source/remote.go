package source

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

type RemoteSpec struct {
	Endpoint        string            `json:"endpoint"`
	Method          string            `json:"method"`
	Headers         map[string]string `json:"headers"`
	Query           map[string]string `json:"query"`
	Body            map[string]any    `json:"body"`
	CursorField     string            `json:"cursor_field"`
	CursorLocation  string            `json:"cursor_location"`
	InitialCursor   *string           `json:"initial_cursor"`
	RecordsPointer  string            `json:"records_pointer"`
	NextPointer     string            `json:"next_cursor_pointer"`
	EndPointer      string            `json:"end_pointer"`
	EndValue        any               `json:"end_value"`
	EmptyIsEnd      bool              `json:"empty_page_is_end"`
	TotalPointer    string            `json:"total_pointer"`
	AuthHeader      string            `json:"auth_header"`
	AuthPrefix      string            `json:"auth_prefix"`
	DatasetVersion  string            `json:"dataset_version"`
	CountUnit       string            `json:"count_unit"`
	IdentityPointer string            `json:"record_identity_pointer,omitempty"`
}
type Page struct {
	Bytes   []byte
	Records []any
	Next    *string
	End     bool
	Total   *json.Number
	Cursor  *string
}

func ValidateRemote(p RemoteSpec, hosts []string) error {
	u, e := url.Parse(p.Endpoint)
	if e != nil || u.Scheme != "https" || u.User != nil || u.Fragment != "" {
		return Failure("connector", "interface_missing", "Exact HTTPS endpoint without inline credentials required")
	}
	allowed := false
	for _, h := range hosts {
		if h == u.Hostname() {
			allowed = true
		}
	}
	if !allowed {
		return Failure("connector", "host_denied", "Endpoint host is outside the saved adapter")
	}
	if p.Method != "GET" && p.Method != "POST" || p.DatasetVersion == "" || p.CountUnit == "" || p.RecordsPointer == "" || p.NextPointer == "" && p.EndPointer == "" && !p.EmptyIsEnd {
		return Failure("connector", "interface_missing", "Documented method/version/count unit/records/completion required")
	}
	if p.CursorLocation != "query" && p.CursorLocation != "body" {
		return Failure("connector", "interface_missing", "Documented cursor location required")
	}
	return nil
}
func FetchPage(ctx context.Context, client *http.Client, p RemoteSpec, hosts []string, cursor *string, secret string) (Page, error) {
	if p.AuthHeader != "" && secret == "" {
		return Page{}, Failure("connector", "credentials_missing", "Selected export credential is unavailable")
	}
	var data []byte
	for attempt := 0; attempt < 2; attempt++ {
		u, _ := url.Parse(p.Endpoint)
		q := u.Query()
		for k, v := range p.Query {
			q.Set(k, v)
		}
		body := map[string]any{}
		for k, v := range p.Body {
			body[k] = v
		}
		if cursor != nil {
			if p.CursorLocation == "query" {
				q.Set(p.CursorField, *cursor)
			} else {
				body[p.CursorField] = *cursor
			}
		}
		u.RawQuery = q.Encode()
		var reader io.Reader
		if p.Method == "POST" {
			b, _ := json.Marshal(body)
			reader = bytes.NewReader(b)
		}
		req, e := http.NewRequestWithContext(ctx, p.Method, u.String(), reader)
		if e != nil {
			return Page{}, e
		}
		for k, v := range p.Headers {
			req.Header.Set(k, v)
		}
		if p.AuthHeader != "" {
			req.Header.Set(p.AuthHeader, p.AuthPrefix+secret)
		}
		if reader != nil {
			req.Header.Set("Content-Type", "application/json")
		}
		// Never follow a redirect with a source credential, even to another allowed host.
		local := *client
		local.CheckRedirect = func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }
		res, e := local.Do(req)
		retry := e != nil
		wait := time.Duration(0)
		if e == nil {
			retry = res.StatusCode == 408 || res.StatusCode == 429 || res.StatusCode == 502 || res.StatusCode == 503 || res.StatusCode == 504
			if v := res.Header.Get("Retry-After"); v != "" {
				if n, err := strconv.Atoi(v); err == nil && n >= 0 {
					wait = time.Duration(n) * time.Second
				} else if at, err := http.ParseTime(v); err == nil {
					wait = time.Until(at)
					if wait < 0 {
						wait = 0
					}
				}
			}
			if res.StatusCode >= 200 && res.StatusCode < 300 {
				data, e = io.ReadAll(io.LimitReader(res.Body, sourcePageLimit+1))
				res.Body.Close()
				if e != nil {
					return Page{}, e
				}
				if len(data) > sourcePageLimit {
					return Page{}, Failure("connector", "intake_limit", "Page exceeds declared adapter capacity")
				}
				break
			}
			res.Body.Close()
		}
		if !retry || attempt == 1 {
			return Page{}, Failure("connector", "remote_failed", "Documented export request failed; authentication/format are never guessed")
		}
		if deadline, ok := ctx.Deadline(); ok && time.Until(deadline) <= wait {
			return Page{}, context.DeadlineExceeded
		}
		select {
		case <-ctx.Done():
			return Page{}, ctx.Err()
		case <-time.After(wait):
		}
	}
	var v any
	if e := Decode(data, &v); e != nil {
		return Page{}, Failure("connector", "remote_format", "Expected documented JSON response")
	}
	r, ok := Pointer(v, p.RecordsPointer)
	a, valid := r.([]any)
	if !ok || !valid {
		return Page{}, Failure("connector", "remote_format", "Documented records array absent")
	}
	page := Page{Bytes: data, Records: a, Cursor: cursor}
	next, present := Pointer(v, p.NextPointer)
	if p.NextPointer != "" && present {
		if s, ok := next.(string); ok && s != "" {
			page.Next = &s
		} else if next != nil {
			return Page{}, Failure("connector", "remote_format", "Cursor is not documented text/null")
		}
	}
	if p.EndPointer != "" {
		end, present := Pointer(v, p.EndPointer)
		if present {
			b, _ := json.Marshal(end)
			expected, _ := json.Marshal(p.EndValue)
			page.End = bytes.Equal(b, expected)
		}
	}
	if p.EmptyIsEnd && len(a) == 0 {
		page.End = true
	}
	if p.NextPointer != "" && present && next == nil {
		page.End = true
	}
	if !page.End && page.Next == nil {
		return Page{}, Failure("connector", "incomplete_export", "No declared completion or continuation marker")
	}
	if p.TotalPointer != "" {
		if total, ok := Pointer(v, p.TotalPointer); ok {
			n, ok := total.(json.Number)
			if !ok {
				return Page{}, Failure("connector", "remote_format", "Declared total is not an integer")
			}
			count, err := n.Int64()
			if err != nil || count < 0 {
				return Page{}, Failure("connector", "remote_format", "Declared total is not a nonnegative integer")
			}
			page.Total = &n
		}
	}
	return page, nil
}

const sourcePageLimit = 64 * 1024 * 1024

func CursorKey(cursor *string) string {
	if cursor == nil {
		return "null"
	}
	return "cursor:" + *cursor
}
func RemotePageName(id string, page int) string {
	return fmt.Sprintf("export/%s/page-%09d.json", strings.ReplaceAll(id, "/", "_"), page)
}
