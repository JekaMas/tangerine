package contracts

import (
	"strings"
	"testing"
)

// Literal golden fixtures and expectations are independently authored; no model call.
const bindingFixture = `{"adapter_version":"fixture-v1","binding_sha256":"974bc36372d4873a494d5cd02561757d82150535bacc5bf8428de8f83fb88b1b","context_budget_tokens":1000,"credential_ref":"fixture-key-ref","endpoint":"https://fixture.invalid","id":"binding-a","input_schema_sha256":"0000000000000000000000000000000000000000000000000000000000000000","max_output_tokens":100,"model":"fixture-model","output_schema_sha256":"0000000000000000000000000000000000000000000000000000000000000000","prompt_id":"fixture-prompt","prompt_sha256":"0000000000000000000000000000000000000000000000000000000000000000","provider":"fixture","reasoning_effort":null,"schema_version":"2.0.0","stage":"case_generation","store":false,"stream":true,"temperature":null,"timeout_seconds":270,"tools":[],"wire_schema_sha256":"0000000000000000000000000000000000000000000000000000000000000000"}`
const renderFixture = `{"audio_format":"riff_pcm_s16le_24000_mono","blueprint_sha256":"0000000000000000000000000000000000000000000000000000000000000000","case_version_id":"case-a","id":"render-a","plan_sha256":"5e99ef83f828b9eece149b41674d88b0ba8b01dfcd352e6d9c1c520b56422f00","profile_sha256":"0000000000000000000000000000000000000000000000000000000000000000","provider_profile_id":"fixture-speech","required_capabilities":[],"schema_version":"2.0.0","turns":[]}`

func TestOwnedBindingIdentityPositive(t *testing.T) {
	if _, _, err := Validate("effective-binding", "2.0.0", []byte(bindingFixture)); err != nil {
		t.Fatal(err)
	}
	changed := strings.Replace(bindingFixture, "binding-a", "binding-b", 1)
	if _, _, err := Validate("effective-binding", "2.0.0", []byte(changed)); err != nil {
		t.Fatal(err)
	}
}
func TestOwnedRenderIdentityPositive(t *testing.T) {
	if err := verifyOwnedDigest("render-plan", []byte(renderFixture)); err != nil {
		t.Fatal(err)
	}
	changed := strings.Replace(strings.Replace(renderFixture, "render-a", "render-b", 1), "2.0.0", "unhashed-version", 1)
	if err := verifyOwnedDigest("render-plan", []byte(changed)); err != nil {
		t.Fatal(err)
	}
}
func TestOwnedBindingContentNegative(t *testing.T) {
	changed := strings.Replace(bindingFixture, "fixture-model", "changed-model", 1)
	if _, _, err := Validate("effective-binding", "2.0.0", []byte(changed)); err == nil {
		t.Fatal("accepted changed content under original digest")
	}
}
func TestOwnedRenderContentNegative(t *testing.T) {
	changed := strings.Replace(renderFixture, "case-a", "case-b", 1)
	if err := verifyOwnedDigest("render-plan", []byte(changed)); err == nil {
		t.Fatal("accepted changed render lineage under original digest")
	}
}
