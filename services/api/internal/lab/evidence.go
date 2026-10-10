package lab

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"sort"
	"strings"
	"tangerine.local/api/internal/contracts"
	"time"
)

type Redaction struct {
	OriginalSHA string          `json:"original_sha256"`
	SHA         string          `json:"sha256"`
	Bytes       json.RawMessage `json:"bytes"`
	Reasons     []string        `json:"reasons"`
}

// Sanitize operates on a copy; it cannot alter native grading or request bytes.
func Sanitize(raw []byte, secrets []string, capture bool) (Redaction, error) {
	if _, e := Canonical(json.RawMessage(raw)); e != nil {
		return Redaction{}, e
	}
	r := Redaction{OriginalSHA: contracts.Digest(raw), Reasons: []string{}}
	var v any
	if e := json.Unmarshal(raw, &v); e != nil {
		return r, e
	}
	if !capture {
		v = map[string]any{"capture": "disabled", "original_sha256": r.OriginalSHA}
		r.Reasons = append(r.Reasons, "content capture disabled")
	} else {
		var walk func(any) any
		walk = func(v any) any {
			switch x := v.(type) {
			case map[string]any:
				out := map[string]any{}
				for k, val := range x {
					key := strings.ReplaceAll(strings.ToLower(k), "-", "_")
					if strings.Contains(key, "authorization") || strings.Contains(key, "cookie") || strings.Contains(key, "api_key") || strings.Contains(key, "password") || strings.Contains(key, "secret") || key == "access_token" || key == "refresh_token" || key == "id_token" || key == "participant_id" || key == "consent" || key == "vendor_private" || key == "personal_metadata" {
						r.Reasons = append(r.Reasons, "omitted field "+k)
						continue
					}
					out[k] = walk(val)
				}
				return out
			case []any:
				out := make([]any, len(x))
				for i, a := range x {
					out[i] = walk(a)
				}
				return out
			case string:
				out := x
				for _, secret := range secrets {
					if secret != "" && strings.Contains(out, secret) {
						out = strings.ReplaceAll(out, secret, "[redacted]")
						r.Reasons = append(r.Reasons, "identified credential value removed")
					}
				}
				if u, e := url.Parse(out); e == nil && u.IsAbs() {
					if u.User != nil {
						u.User = nil
						r.Reasons = append(r.Reasons, "URL credentials removed")
					}
					q := u.Query()
					for k := range q {
						key := strings.ToLower(k)
						if strings.Contains(key, "token") || strings.Contains(key, "key") || strings.Contains(key, "secret") || strings.Contains(key, "signature") {
							q.Del(k)
							r.Reasons = append(r.Reasons, "secret URL parameter removed")
						}
					}
					u.RawQuery = q.Encode()
					out = u.String()
				}
				return out
			default:
				return v
			}
		}
		v = walk(v)
	}
	b, e := Canonical(v)
	sort.Strings(r.Reasons)
	r.Bytes = b
	r.SHA = contracts.Digest(b)
	return r, e
}

type Dispatch struct {
	ID         string `json:"id"`
	Surface    string `json:"surface"`
	RequestSHA string `json:"request_sha256"`
}
type Observation struct {
	ID         string `json:"id"`
	Dispatch   string `json:"dispatch"`
	Surface    string `json:"surface"`
	RequestSHA string `json:"request_sha256"`
	Receipt    string `json:"receipt"`
	Outcome    string `json:"outcome"`
	Cache      bool   `json:"cache"`
	Original   string `json:"original"`
}
type Export struct {
	Observation string `json:"observation"`
	RequestSHA  string `json:"request_sha256"`
	Receipt     string `json:"receipt"`
	Run         string `json:"run"`
	Artifact    string `json:"artifact"`
	Verified    bool   `json:"verified"`
}
type Join struct {
	Dispatches            []Dispatch    `json:"dispatches"`
	Native                []Observation `json:"native"`
	Exports               []Export      `json:"exports"`
	RequiredSurfaces      []string      `json:"required_surfaces"`
	Properties            []string      `json:"properties"`
	Cases                 []string      `json:"cases"`
	ZeroReason            string        `json:"zero_call_reason"`
	DeterministicArtifact *Export       `json:"deterministic_artifact"`
}
type Coverage struct {
	Status        string   `json:"status"`
	Observed      int      `json:"observed"`
	Matched       int      `json:"matched"`
	Ratio         *string  `json:"ratio"`
	Discrepancies []string `json:"discrepancies"`
}

func Reconcile(j Join) Coverage {
	c := Coverage{Status: "observed", Observed: len(j.Dispatches), Discrepancies: []string{}}
	issue := func(s string) { c.Discrepancies = append(c.Discrepancies, s); c.Status = "incomplete" }
	if len(j.Properties) == 0 || len(j.Cases) == 0 {
		issue("empty selected property/case scope")
	}
	ds := map[string]Dispatch{}
	for _, d := range j.Dispatches {
		if d.ID == "" || ds[d.ID].ID != "" {
			issue("duplicate/empty dispatch identity " + d.ID)
		}
		ds[d.ID] = d
	}
	ns := map[string]Observation{}
	bydispatch := map[string]int{}
	surfaces := map[string]bool{}
	for _, n := range j.Native {
		if n.ID == "" || ns[n.ID].ID != "" {
			issue("duplicate/empty native observation " + n.ID)
		}
		ns[n.ID] = n
	}
	es := map[string]Export{}
	locators := map[string]bool{}
	for _, e := range j.Exports {
		if _, ok := es[e.Observation]; ok {
			issue("duplicate export link " + e.Observation)
		}
		if e.Run == "" || e.Artifact == "" || !e.Verified {
			issue("unverified Lab export " + e.Observation)
		}
		locator := e.Run + ":" + e.Artifact
		if locators[locator] {
			issue("reused Lab artifact " + locator)
		}
		locators[locator] = true
		es[e.Observation] = e
	}
	for _, n := range j.Native {
		if n.Cache {
			original, exists := ns[n.Original]
			if !exists || n.Receipt == "" || n.Dispatch != "" || original.Receipt != n.Receipt || n.Original == n.ID || original.Cache {
				issue("invalid cache reference " + n.ID)
			}
			continue
		}
		if n.Outcome == "preparation_failed" {
			e, ok := es[n.ID]
			if n.Dispatch != "" || n.RequestSHA == "" || n.Receipt == "" || !ok || !e.Verified || e.RequestSHA != n.RequestSHA || e.Receipt != n.Receipt {
				issue("unsupported preparation-failed evidence " + n.ID)
			}
			continue
		}
		d, ok := ds[n.Dispatch]
		if !ok {
			issue("native record without independent dispatch " + n.ID)
			continue
		}
		bydispatch[d.ID]++
		e, ok := es[n.ID]
		if n.RequestSHA == "" || n.Receipt == "" || n.Outcome == "" || n.RequestSHA != d.RequestSHA || n.Surface != d.Surface {
			issue("native request/receipt mismatch " + n.ID)
			continue
		}
		if !ok || e.RequestSHA != n.RequestSHA || e.Receipt != n.Receipt || !e.Verified {
			issue("missing/mismatched export " + n.ID)
			continue
		}
		c.Matched++
		surfaces[n.Surface] = true
	}
	for id := range ds {
		if bydispatch[id] != 1 {
			issue("orphan or duplicate dispatch " + id)
		}
	}
	for id := range es {
		if ns[id].ID == "" {
			issue("orphan Lab export " + id)
		}
	}
	for _, s := range j.RequiredSurfaces {
		if !surfaces[s] {
			issue("unexercised required surface " + s)
		}
	}
	if c.Observed == 0 {
		if j.ZeroReason == "" || j.DeterministicArtifact == nil || !j.DeterministicArtifact.Verified || j.DeterministicArtifact.Run == "" || j.DeterministicArtifact.Artifact == "" {
			issue("zero-call reason or actual Lab artifact missing")
		}
	} else {
		x := fmt.Sprintf("%d/%d", c.Matched, c.Observed)
		c.Ratio = &x
	}
	return c
}

type Row struct {
	Case       string `json:"case"`
	Variant    string `json:"variant"`
	Repetition int    `json:"repetition"`
	Status     string `json:"status"`
}

func PlannedRows(cases, variants []string, repetitions int) ([]Row, error) {
	if len(cases) == 0 || len(variants) == 0 || repetitions < 1 {
		return nil, errors.New("empty frozen experiment population")
	}
	unique := func(rows []string) bool {
		seen := map[string]bool{}
		for _, s := range rows {
			if s == "" || seen[s] {
				return false
			}
			seen[s] = true
		}
		return true
	}
	if !unique(cases) || !unique(variants) {
		return nil, errors.New("duplicate case/variant identity")
	}
	rows := []Row{}
	for _, c := range cases {
		for _, v := range variants {
			for i := 1; i <= repetitions; i++ {
				rows = append(rows, Row{c, v, i, "not_run"})
			}
		}
	}
	return rows, nil
}

// ExportJSON only exports existing diagnostics. Its budget includes request and
// response; it never retries, queues or invokes any inference owner.
func ExportJSON(ctx context.Context, client *http.Client, endpoint string, payload []byte, experiment string, reserve time.Duration) (string, error) {
	deadline, ok := ctx.Deadline()
	budget := time.Second
	if ok {
		remaining := time.Until(deadline) - reserve
		if remaining < budget {
			budget = remaining
		}
	}
	if budget <= 0 {
		return "unexported", errors.New("export budget unavailable")
	}
	ctx, cancel := context.WithTimeout(ctx, budget)
	defer cancel()
	req, e := http.NewRequestWithContext(ctx, "POST", endpoint, bytes.NewReader(payload))
	if e != nil {
		return "unexported", e
	}
	req.Header.Set("Content-Type", "application/x-protobuf")
	req.Header.Set("x-mlflow-experiment-id", experiment)
	res, e := client.Do(req)
	if e != nil {
		return "unexported", e
	}
	defer res.Body.Close()
	_, e = io.Copy(io.Discard, io.LimitReader(res.Body, 1024*1024))
	if e != nil || res.StatusCode < 200 || res.StatusCode >= 300 {
		return "unexported", errors.New("Lab trace export unavailable")
	}
	return "exported", nil
}

// Witness joins independently retained identities; a matching declaration alone
// cannot replace the native binding, context, wire and receipt records.
type Witness struct{ Operation, Stage, Binding, Input, Wire, Receipt string }

func MatchWitness(actual, expected Witness) bool {
	return actual.Operation != "" && actual.Stage != "" && actual.Binding != "" && actual.Input != "" && actual.Wire != "" && actual.Receipt != "" && actual == expected
}
