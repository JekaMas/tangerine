package provider

import (
	"strings"
	"testing"
)

// Constructed remote protocol bytes exercise the actual stream parser. They do
// not establish hosted entitlement or model quality.
func TestProviderStreamTailEOFPositive(t *testing.T) {
	r, err, seen := send(t, 200, strings.TrimRight(completed, "\n"))
	if err != nil || r.Outcome != "complete" || r.Visible != `{"answer_text":"ok","requested_language":"en"}` || seen.Calls != 1 || string(r.Raw) != strings.TrimRight(completed, "\n") {
		t.Fatal("terminal event at EOF lost", err, r, seen)
	}
}

func TestProviderStreamTailMetadataPositive(t *testing.T) {
	body := completed + "data: {\"type\":\"fixture.metadata\",\"note\":\"after terminal\"}\n\n"
	r, err, seen := send(t, 200, body)
	if err != nil || r.Outcome != "complete" || r.Visible != `{"answer_text":"ok","requested_language":"en"}` || seen.Calls != 1 || string(r.Raw) != body {
		t.Fatal("complete stream metadata not retained", err, r, seen)
	}
}

func TestProviderStreamTailQuotaNegative(t *testing.T) {
	body := completed + "data: {\"type\":\"error\",\"code\":\"subscription_sharing_usage_limit_exceeded\"}\n\n"
	r, err, seen := send(t, 200, body)
	code, native := SafeError(err)
	if code != "LOCAL_BUDGET_EXCEEDED" || native != "subscription_sharing_usage_limit_exceeded" || r.Outcome == "complete" || seen.Calls != 1 || !strings.Contains(string(r.Raw), native) {
		t.Fatal("post-completion quota promoted", err, r, seen)
	}
}

func TestProviderStreamTailDuplicateNegative(t *testing.T) {
	body := completed + "data: {\"type\":\"response.completed\",\"response\":{\"status\":\"completed\",\"output\":[]}}\n\n"
	r, err, seen := send(t, 200, body)
	code, _ := SafeError(err)
	if code != "PROVIDER_INCOMPLETE" || r.Outcome == "complete" || seen.Calls != 1 || string(r.Raw) != body {
		t.Fatal("contradictory terminals promoted", err, r, seen)
	}
}
