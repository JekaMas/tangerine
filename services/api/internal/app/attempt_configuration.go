package app

// Attempt entry freezes already admitted settings and their effective stage bindings.
import (
	"context"
	"encoding/json"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/provider"
)

func configurationInTransaction(ctx context.Context, tx pgx.Tx) (map[string]any, lab.Bundle, []any, error) {
	var raw []byte
	c := DefaultConfiguration()
	bundle := lab.Shipped()
	e := tx.QueryRow(ctx, "SELECT d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id='local-configuration' FOR SHARE OF h").Scan(&raw)
	if e != nil && e != pgx.ErrNoRows {
		return nil, bundle, nil, e
	}
	if e == nil {
		_ = json.Unmarshal(raw, &c)
	}
	if id, ok := c["active_prompt_bundle_id"].(string); ok {
		if e = tx.QueryRow(ctx, "SELECT payload FROM document WHERE id=$1 AND kind='prompt-bundle'", id).Scan(&raw); e != nil {
			return nil, bundle, nil, e
		}
		if e = json.Unmarshal(raw, &bundle); e != nil {
			return nil, bundle, nil, e
		}
	}
	if frozen, ok := frozenQuality(ctx); ok {
		c = frozen.Configuration
		bundle = frozen.Bundle
	}
	// Configuration/profile-role references were admitted by PutConfiguration.
	// Select trusted snapshots here rather than repeat its whole-profile validation.
	profilesRaw, _ := json.Marshal(c["llm_profiles"])
	var profiles []provider.Profile
	_ = json.Unmarshal(profilesRaw, &profiles)
	bindings := []any{}
	for _, role := range []string{"blind_claim_extraction", "claim_mapping", "mapping_audit", "feedback", "adjudication"} {
		selected := c["llm_profile"].(string)
		if override, ok := c["stage_profiles"].(map[string]any)[role].(string); ok {
			selected = override
		}
		var p provider.Profile
		for _, profile := range profiles {
			if profile.ID == selected {
				p = profile
				break
			}
		}
		if p.ID == "" {
			return nil, bundle, nil, ErrReference
		}
		// Only the ordinary semantic checking stages are entry prerequisites.
		// Optional diagnostics/feedback are frozen honestly, then admitted on use.
		if role == "blind_claim_extraction" || role == "claim_mapping" {
			if p.Model == "unselected" {
				return nil, bundle, nil, &provider.Failure{Code: "CONSTRAINT_CONFLICT"}
			}
			if e = provider.Included(p); e != nil {
				return nil, bundle, nil, e
			}
		}
		for _, binding := range bundle.Bindings {
			if binding.Stage == role {
				bindings = append(bindings, map[string]any{"stage": role, "profile": p, "prompt_binding": binding, "prompt_bundle_sha256": bundle.SHA})
			}
		}
	}
	return c, bundle, bindings, nil
}
