package app

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
)

type labAssetRef struct {
	ID  string `json:"asset_id"`
	SHA string `json:"sha256"`
}
type labExpectedExport struct {
	Run      string `json:"run"`
	Artifact string `json:"artifact"`
	SHA      string `json:"sha256"`
}
type developmentPacket struct {
	Join          lab.Join            `json:"join"`
	Artifacts     []labExpectedExport `json:"artifacts"`
	Discrepancies []string            `json:"discrepancies"`
}

// PrepareDevelopmentVerification reads authoritative private assets and actual
// receipts. The SDK edge then downloads and verifies the exact local Lab copies.
// No declared 'observed' flag or exported counter is used as its own oracle.
func (s *Storage) PrepareDevelopmentVerification(ctx context.Context, raw []byte) (developmentPacket, error) {
	p := developmentPacket{Artifacts: []labExpectedExport{}, Discrepancies: []string{}}
	if _, _, e := contracts.Validate("ai-development-run", "2.0.0", raw); e != nil {
		return p, e
	}
	var r struct {
		Properties    []string     `json:"affected_property_ids"`
		Cases         []string     `json:"selected_case_ids"`
		Required      []string     `json:"required_surface_ids"`
		Zero          *string      `json:"zero_call_reason"`
		Inventory     labAssetRef  `json:"inventory_asset"`
		Dispatch      *labAssetRef `json:"dispatch_observer_asset"`
		CasesAsset    *labAssetRef `json:"actual_case_result_asset"`
		Comparison    *labAssetRef `json:"comparison_asset"`
		Runs          []string     `json:"mlflow_run_ids"`
		Artifacts     []string     `json:"mlflow_artifact_refs"`
		Discrepancies []string     `json:"discrepancies"`
		Observations  []struct {
			ID           string       `json:"id"`
			Surface      string       `json:"surface_id"`
			Operation    string       `json:"operation_id"`
			Kind         string       `json:"attempt_kind"`
			Parent       *string      `json:"parent_observation_id"`
			Snapshot     labAssetRef  `json:"snapshot_asset"`
			Redaction    *labAssetRef `json:"redaction_asset"`
			Receipt      string       `json:"receipt_id"`
			Dispatch     *string      `json:"dispatch_observation_id"`
			Outcome      string       `json:"outcome"`
			Run          *string      `json:"mlflow_run_id"`
			Artifacts    []string     `json:"mlflow_artifact_refs"`
			ExportStatus string       `json:"export_status"`
		} `json:"observations"`
	}
	if e := json.Unmarshal(raw, &r); e != nil {
		return p, e
	}
	p.Join.Properties = r.Properties
	p.Join.Cases = r.Cases
	p.Join.RequiredSurfaces = r.Required
	if r.Zero != nil {
		p.Join.ZeroReason = *r.Zero
	}
	p.Discrepancies = append(p.Discrepancies, r.Discrepancies...)
	runs := map[string]bool{}
	for _, id := range r.Runs {
		if id == "" || runs[id] {
			p.Discrepancies = append(p.Discrepancies, "duplicate/empty Lab run")
		}
		runs[id] = true
	}
	expected := map[string]string{}
	expectedRuns := map[string]string{}
	read := func(ref labAssetRef) ([]byte, error) {
		b, e := s.ReadAsset(ctx, ref.ID)
		if e != nil {
			return nil, e
		}
		if contracts.Digest(b) != ref.SHA {
			return nil, errors.New("native development asset mismatch")
		}
		return b, nil
	}
	inventory, e := read(r.Inventory)
	if e != nil {
		return p, e
	}
	if _, _, e = contracts.Validate("ai-surface-inventory", "2.0.0", inventory); e != nil {
		return p, e
	}
	expected["inventory.json"] = r.Inventory.SHA
	var inv struct {
		Unresolved []string `json:"unresolved_paths"`
		Entries    []struct {
			ID    string `json:"id"`
			State string `json:"implementation_state"`
			Stage string `json:"stage"`
		} `json:"entries"`
	}
	if e = json.Unmarshal(inventory, &inv); e != nil {
		return p, e
	}
	p.Discrepancies = append(p.Discrepancies, inv.Unresolved...)
	states := map[string]string{}
	stages := map[string]string{}
	operations := map[string]string{}
	for _, o := range r.Observations {
		operations[o.ID] = o.Operation
	}
	for _, x := range inv.Entries {
		if states[x.ID] != "" {
			p.Discrepancies = append(p.Discrepancies, "duplicate inventory surface")
		}
		states[x.ID] = x.State
		stages[x.ID] = x.Stage
	}
	if r.CasesAsset == nil {
		return p, errors.New("actual selected case-result asset required")
	}
	if _, e = read(*r.CasesAsset); e != nil {
		return p, e
	}
	expected["cases.json"] = r.CasesAsset.SHA
	if r.Dispatch != nil {
		b, e := read(*r.Dispatch)
		if e != nil {
			return p, e
		}
		if e = json.Unmarshal(b, &p.Join.Dispatches); e != nil {
			return p, e
		}
		expected["dispatches.json"] = r.Dispatch.SHA
	} else if len(r.Observations) > 0 {
		return p, errors.New("independent dispatch observer required")
	}
	if r.Comparison != nil {
		if _, e = read(*r.Comparison); e != nil {
			return p, e
		}
		expected["comparison.json"] = r.Comparison.SHA
	}
	for _, o := range r.Observations {
		if states[o.Surface] != "implemented" {
			p.Discrepancies = append(p.Discrepancies, "unimplemented/unregistered observed surface "+o.Surface)
		}
		snapshot, e := read(o.Snapshot)
		if e != nil {
			return p, e
		}
		if e = contracts.ValidateDefinition("ai-development-run", "execution_snapshot", snapshot); e != nil {
			return p, e
		}
		var snap struct {
			Surface string      `json:"surface_id"`
			Wire    labAssetRef `json:"wire_request"`
			Binding labAssetRef `json:"binding_asset"`
			Context *string     `json:"context_snapshot_id"`
			State   string      `json:"reconstruction_status"`
			Limits  []string    `json:"inspection_limits"`
			Parts   []struct {
				Asset labAssetRef `json:"asset"`
			} `json:"input_parts"`
		}
		if e = json.Unmarshal(snapshot, &snap); e != nil {
			return p, e
		}
		if snap.Surface != o.Surface || snap.State != "complete" || len(snap.Limits) > 0 {
			p.Discrepancies = append(p.Discrepancies, "limited/mismatched execution snapshot "+o.ID)
		}
		wire, e := read(snap.Wire)
		if e != nil {
			return p, e
		}
		binding, e := read(snap.Binding)
		if e != nil {
			return p, e
		}
		for _, part := range snap.Parts {
			if _, e = read(part.Asset); e != nil {
				return p, e
			}
		}
		receipt, e := s.ReadDocument(ctx, o.Receipt)
		if e != nil {
			return p, e
		}
		if receipt.Kind != "provider-receipt" {
			return p, errors.New("wrong native receipt kind")
		}
		var dto struct {
			Operation string `json:"operation_id"`
			Stage     string `json:"stage"`
			Outcome   string `json:"outcome"`
			Wire      string `json:"wire_request_asset_id"`
			Binding   string `json:"binding_sha256"`
			Input     string `json:"input_sha256"`
		}
		if e = json.Unmarshal(receipt.Payload, &dto); e != nil {
			return p, e
		}
		operation := o.Operation
		if o.Kind == "cache_reference" && o.Parent != nil {
			operation = operations[*o.Parent]
		}
		if dto.Operation != operation || dto.Stage != stages[o.Surface] || (o.Kind != "cache_reference" && dto.Outcome != o.Outcome) || (o.Kind == "cache_reference" && o.Outcome != "cache_reference") || dto.Wire != snap.Wire.ID {
			p.Discrepancies = append(p.Discrepancies, "native snapshot/receipt correspondence mismatch "+o.ID)
		}
		if snap.Context != nil {
			contextDoc, e := s.ReadDocument(ctx, *snap.Context)
			if e != nil {
				return p, e
			}
			if contextDoc.Kind != "llm-context-snapshot" {
				return p, errors.New("wrong context snapshot kind")
			}
			var bound struct {
				SHA string `json:"binding_sha256"`
			}
			if e = json.Unmarshal(binding, &bound); e != nil {
				return p, e
			}
			var contextDTO struct {
				Operation string `json:"operation_id"`
				Stage     string `json:"stage"`
				Receipt   string `json:"receipt_id"`
				Wire      string `json:"rendered_request_asset_id"`
				Binding   string `json:"binding_sha256"`
				Input     string `json:"input_sha256"`
			}
			if e = json.Unmarshal(contextDoc.Payload, &contextDTO); e != nil {
				return p, e
			}
			actual := lab.Witness{Operation: contextDTO.Operation, Stage: contextDTO.Stage, Binding: contextDTO.Binding, Input: contextDTO.Input, Wire: contextDTO.Wire, Receipt: contextDTO.Receipt}
			expected := lab.Witness{Operation: dto.Operation, Stage: dto.Stage, Binding: bound.SHA, Input: dto.Input, Wire: snap.Wire.ID, Receipt: o.Receipt}
			if dto.Binding != bound.SHA || !lab.MatchWitness(actual, expected) {
				p.Discrepancies = append(p.Discrepancies, "context/receipt binding mismatch "+o.ID)
			}
		}
		n := lab.Observation{ID: o.ID, Surface: o.Surface, RequestSHA: contracts.Digest(wire), Receipt: o.Receipt, Outcome: o.Outcome, Cache: o.Kind == "cache_reference"}
		if o.Dispatch != nil {
			n.Dispatch = *o.Dispatch
		}
		if o.Parent != nil {
			n.Original = *o.Parent
		}
		p.Join.Native = append(p.Join.Native, n)
		snapshotSHA := o.Snapshot.SHA
		if o.Redaction != nil {
			if _, e = read(*o.Redaction); e != nil {
				return p, e
			}
			snapshotSHA = o.Redaction.SHA
		}
		expected["snapshot-"+o.ID+".json"] = snapshotSHA
		expected["receipt-"+o.ID+".json"] = receipt.SHA
		if o.Run != nil && o.ExportStatus == "exported" {
			expectedRuns["snapshot-"+o.ID+".json"] = *o.Run
			expectedRuns["receipt-"+o.ID+".json"] = *o.Run
			for _, name := range []string{"snapshot-" + o.ID + ".json", "receipt-" + o.ID + ".json"} {
				locator := "runs:/" + *o.Run + "/native/" + name
				found := false
				for _, ref := range o.Artifacts {
					if ref == locator {
						found = true
					}
				}
				if !found {
					p.Discrepancies = append(p.Discrepancies, "missing observation Lab correspondence "+locator)
				}
			}
			p.Join.Exports = append(p.Join.Exports, lab.Export{Observation: o.ID, RequestSHA: n.RequestSHA, Receipt: o.Receipt, Run: *o.Run, Artifact: "native/snapshot-" + o.ID + ".json"})
		}
	}
	seen := map[string]bool{}
	for _, ref := range r.Artifacts {
		parts := strings.SplitN(strings.TrimPrefix(ref, "runs:/"), "/", 2)
		if !strings.HasPrefix(ref, "runs:/") || len(parts) != 2 || !runs[parts[0]] {
			p.Discrepancies = append(p.Discrepancies, "unresolved Lab artifact locator "+ref)
			continue
		}
		name := strings.TrimPrefix(parts[1], "native/")
		sha, ok := expected[name]
		if !ok || seen[name] || (expectedRuns[name] != "" && expectedRuns[name] != parts[0]) {
			p.Discrepancies = append(p.Discrepancies, "unexpected/duplicate Lab artifact "+ref)
			continue
		}
		seen[name] = true
		p.Artifacts = append(p.Artifacts, labExpectedExport{parts[0], parts[1], sha})
	}
	for name := range expected {
		if !seen[name] {
			p.Discrepancies = append(p.Discrepancies, fmt.Sprintf("missing required native/Lab artifact %s", name))
		}
	}
	if len(p.Join.Dispatches) == 0 && len(p.Artifacts) > 0 {
		a := p.Artifacts[0]
		p.Join.DeterministicArtifact = &lab.Export{Run: a.Run, Artifact: a.Artifact}
	}
	return p, nil
}
