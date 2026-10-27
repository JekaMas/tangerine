package app

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"io"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
)

// LabCommand is internal maintenance tooling. It uses the same immutable document
// transaction and CAS configuration head as Settings; no model call is possible.
func (s *Storage) LabCommand(ctx context.Context, input io.Reader, output io.Writer) error {
	var r struct {
		Action        string          `json:"action"`
		Bundle        lab.Bundle      `json:"bundle"`
		Configuration json.RawMessage `json:"configuration"`
		Document      *DocumentWrite  `json:"document"`
		ID            string          `json:"id"`
		Payload       json.RawMessage `json:"payload"`
		Key           string          `json:"key"`
	}
	if e := lab.DecodeCommand(input, &r); e != nil {
		return e
	}
	var result any
	var err error
	switch r.Action {
	case "source-correction-evaluate":
		result, err = s.EvaluateSourceCorrections(ctx, r.Payload)
	case "development-prepare":
		result, err = s.PrepareDevelopmentVerification(ctx, r.Payload)
	case "diagnostic-save":
		raw, e := contracts.Canonical(r.Payload)
		if e != nil {
			return e
		}
		if r.Key == "" {
			var packet struct {
				Operation string `json:"operation"`
			}
			if e = json.Unmarshal(raw, &packet); e != nil {
				return e
			}
			if id, e := uuid.Parse(packet.Operation); e != nil || id.Version() != 4 {
				return errors.New("diagnostic operation UUIDv4 required")
			}
			r.Key = packet.Operation
		}
		a, e := s.ReserveAsset(ctx, AssetRequest{Operation: OperationRequest{Name: "lab-diagnostic", Key: r.Key, Path: "/lab/diagnostic", Body: raw}, SHA: contracts.Digest(raw), Size: int64(len(raw)), Purpose: "export", MIME: "application/json"})
		if e != nil {
			return e
		}
		if a.State != "linked" {
			if _, e = s.UploadAsset(ctx, a.ID, raw); e != nil {
				return e
			}
			if a, e = s.LinkAsset(ctx, a.ID, nil); e != nil {
				return e
			}
		}
		result = a
	case "diagnostic-read":
		id := r.ID
		var assetID string
		e := s.DB.QueryRow(ctx, "SELECT a.asset_id FROM asset_location a JOIN operation o ON o.id=a.operation_id WHERE o.operation_name='lab-diagnostic' AND (a.asset_id=$1 OR o.id=$1 OR o.idempotency_key::text=$1)", id).Scan(&assetID)
		if e == nil {
			id = assetID
		}
		raw, e := s.ReadAsset(ctx, id)
		if e != nil {
			return e
		}
		result = json.RawMessage(raw)
	case "active":
		result, err = s.ActiveLabBundle(ctx)
	case "activate":
		result, err = s.ActivateLabBundle(ctx, r.Bundle, r.Configuration)
	case "record":
		if r.Document == nil {
			return ErrReference
		}
		result, err = s.WriteDocuments(ctx, []DocumentWrite{*r.Document})
	case "read":
		result, err = s.ReadDocument(ctx, r.ID)
	default:
		return ErrConflict
	}
	if err != nil {
		return err
	}
	return json.NewEncoder(output).Encode(result)
}
func (s *Storage) ActiveLabBundle(ctx context.Context) (lab.Bundle, error) {
	if b, ok := frozenQuality(ctx); ok {
		return b.Bundle, nil
	}
	var config []byte
	err := s.DB.QueryRow(ctx, "SELECT d.payload FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id='local-configuration' AND h.kind='configuration'").Scan(&config)
	if errors.Is(err, pgx.ErrNoRows) {
		return lab.Shipped(), nil
	}
	if err != nil {
		return lab.Bundle{}, err
	}
	var c struct {
		ID *string `json:"active_prompt_bundle_id"`
	}
	if err = json.Unmarshal(config, &c); err != nil {
		return lab.Bundle{}, err
	}
	if c.ID == nil {
		return lab.Shipped(), nil
	}
	doc, err := s.ReadDocument(ctx, *c.ID)
	if err != nil || doc.Kind != "prompt-bundle" {
		return lab.Bundle{}, ErrUnavailable
	}
	var b lab.Bundle
	err = json.Unmarshal(doc.Payload, &b)
	return b, err
}
func (s *Storage) ActivateLabBundle(ctx context.Context, b lab.Bundle, initial json.RawMessage) (any, error) {
	if err := lab.ValidateBundle(b); err != nil {
		return nil, err
	}
	var config json.RawMessage
	var revision int64
	err := s.DB.QueryRow(ctx, "SELECT d.payload,h.revision FROM entity_head h JOIN document d ON d.id=h.document_id WHERE h.id='local-configuration' AND h.kind='configuration'").Scan(&config, &revision)
	var expected *int64
	if errors.Is(err, pgx.ErrNoRows) {
		config = initial
		if len(config) == 0 {
			return nil, errors.New("initial complete configuration required")
		}
	} else if err != nil {
		return nil, err
	} else {
		expected = &revision
	}
	var c map[string]any
	if err = json.Unmarshal(config, &c); err != nil {
		return nil, err
	}
	c["active_prompt_bundle_id"] = b.ID
	delete(c, "configuration_sha256")
	c["configuration_sha256"] = lab.Hash(c)
	cb, err := lab.Canonical(c)
	if err != nil {
		return nil, err
	}
	raw, err := lab.Canonical(b)
	if err != nil {
		return nil, err
	}
	scope := "local"
	bundleWrite := DocumentWrite{ID: b.ID, Kind: "prompt-bundle", Version: "2.0.0", Scope: scope, Payload: raw}
	id := uuid.NewString()
	configWrite := DocumentWrite{ID: id, Kind: "configuration", Version: "2.0.0", Scope: scope, Payload: cb, Head: &HeadWrite{ID: "local-configuration", Expected: expected, State: "active"}, References: []Reference{{Pointer: "/active_prompt_bundle_id", ID: b.ID, Scope: scope, Kind: "prompt-bundle", SHA: contracts.Digest(raw), Relation: "active-prompt-bundle"}}}
	existing, readErr := s.ReadDocument(ctx, b.ID)
	if readErr == nil {
		if existing.Kind != "prompt-bundle" || existing.SHA != contracts.Digest(raw) {
			return nil, ErrConflict
		}
		return s.WriteDocuments(ctx, []DocumentWrite{configWrite})
	}
	if !errors.Is(readErr, pgx.ErrNoRows) {
		return nil, readErr
	}
	return s.WriteDocuments(ctx, []DocumentWrite{bundleWrite, configWrite})
}
