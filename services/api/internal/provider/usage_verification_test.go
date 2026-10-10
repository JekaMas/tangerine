package provider

import (
	"strings"
	"testing"
)

// Literal remote usage fields exercise the real parser, never account billing.
func TestProviderUsageZeroPositive(t *testing.T) {
	body := strings.NewReplacer(`"input_tokens":17`, `"input_tokens":0`, `"output_tokens":5`, `"output_tokens":0`, `"cached_tokens":3`, `"cached_tokens":0`, `"reasoning_tokens":2`, `"reasoning_tokens":0`).Replace(completed)
	r, err, seen := send(t, 200, body)
	for _, key := range []string{"input_tokens", "output_tokens", "cached_tokens", "reasoning_tokens"} {
		if err != nil || r.Usage[key] == nil || *r.Usage[key] != 0 || seen.Calls != 1 {
			t.Fatal("real zero lost", key, err, r.Usage)
		}
	}
}

func TestProviderUsageKnownPositive(t *testing.T) {
	body := strings.Replace(completed, `"cached_tokens":3`, `"cached_tokens":3,"provider_extra":"ignored"`, 1)
	r, err, seen := send(t, 200, body)
	for key, expected := range map[string]int64{"input_tokens": 17, "output_tokens": 5, "cached_tokens": 3, "reasoning_tokens": 2} {
		if err != nil || r.Usage[key] == nil || *r.Usage[key] != expected || seen.Calls != 1 {
			t.Fatal("observed count changed", key, err, r.Usage)
		}
	}
}

func TestProviderUsageNullNegative(t *testing.T) {
	body := strings.NewReplacer(`"input_tokens":17`, `"input_tokens":null`, `"output_tokens":5`, `"output_tokens":null`).Replace(completed)
	r, err, seen := send(t, 200, body)
	if err != nil || r.Usage["input_tokens"] != nil || r.Usage["output_tokens"] != nil || seen.Calls != 1 || string(r.Raw) != body {
		t.Fatal("unknown flat usage fabricated as zero", err, r.Usage)
	}
}

func TestProviderUsageDetailsNullNegative(t *testing.T) {
	body := strings.NewReplacer(`"cached_tokens":3`, `"cached_tokens":null`, `"reasoning_tokens":2`, `"reasoning_tokens":null`).Replace(completed)
	r, err, seen := send(t, 200, body)
	if err != nil || r.Usage["cached_tokens"] != nil || r.Usage["reasoning_tokens"] != nil || seen.Calls != 1 || string(r.Raw) != body {
		t.Fatal("unknown detail usage fabricated as zero", err, r.Usage)
	}
}
