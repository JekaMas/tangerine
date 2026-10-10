package contracts

import (
	"encoding/json"
	"errors"
)

// verifyOwnedDigest implements only the hash definition owned by this kind;
// foreign audio/input/binding hashes are never confused with a self digest.
func verifyOwnedDigest(kind string, b []byte) error {
	fields := map[string]string{"ai-surface-inventory": "inventory_sha256", "configuration": "configuration_sha256", "effective-binding": "binding_sha256", "mutation-manifest": "manifest_sha256", "prompt-bundle": "bundle_sha256", "llm-quality-dataset": "dataset_sha256", "render-plan": "plan_sha256"}
	field, ok := fields[kind]
	if !ok {
		return nil
	}
	var payload map[string]json.RawMessage
	if err := json.Unmarshal(b, &payload); err != nil {
		return err
	}
	raw, exists := payload[field]
	if !exists {
		return nil
	}
	var supplied string
	if err := json.Unmarshal(raw, &supplied); err != nil {
		return err
	}
	delete(payload, field)
	if kind == "effective-binding" {
		delete(payload, "id")
	}
	if kind == "render-plan" {
		delete(payload, "id")
		delete(payload, "schema_version")
	}
	candidate, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	canonical, err := Canonical(candidate)
	if err != nil {
		return err
	}
	if Digest(canonical) != supplied {
		return errors.New("owned digest mismatch")
	}
	return nil
}
