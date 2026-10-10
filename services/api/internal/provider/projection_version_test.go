package provider

import "testing"

const cleanCandidateFixture = `{"schema_version":"1.0.0","blueprint_id":"b1","status":"candidate","failure_reason":null,"utterances":[{"id":"u1","speaker_id":"s1","canonical_text":"It opens tomorrow.","surface_text":"It opens tomorrow."}],"planned_units":[]}`

func TestProjectionCanonicalVersionPositive(t *testing.T) {
	if _, e := ProjectVisible(cleanCandidateFixture, "case-candidate"); e != nil {
		t.Fatal(e)
	}
}
func TestProjectionErrorVersionPositive(t *testing.T) {
	if _, e := ProjectVisible(`{"code":"PROVIDER_FAILURE","message":"Unavailable","request_id":"r1","retryable":true,"object_id":null,"details":[]}`, "error-response"); e != nil {
		t.Fatal(e)
	}
}
func TestProjectionWrongVersionNegative(t *testing.T) {
	if _, e := ProjectVisible(`{"schema_version":"2.0.0","blueprint_id":"b1","status":"candidate","failure_reason":null,"utterances":[],"planned_units":[]}`, "case-candidate"); e == nil {
		t.Fatal("changed candidate contract accepted")
	}
}
func TestProjectionMissingContentNegative(t *testing.T) {
	if _, e := ProjectVisible(`{"schema_version":"1.0.0","blueprint_id":"b1","status":"candidate","failure_reason":null,"utterances":[]}`, "case-candidate"); e == nil {
		t.Fatal("missing plan accepted")
	}
}
