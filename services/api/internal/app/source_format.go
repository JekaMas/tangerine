package app

import (
	"context"
	"encoding/json"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
)

func (s *Storage) RegisterFormat(ctx context.Context, body []byte) (map[string]any, error) {
	var input map[string]any
	if e := json.Unmarshal(body, &input); e != nil {
		return nil, ErrInput
	}
	for _, field := range []string{"id", "review_person_id", "reviewed_at", "origin", "provider_receipt_ids", "input_modality"} {
		delete(input, field)
	}
	bindingID := source.StableID("source-format", string(sourceBytes(input)))
	if old, _, err := s.sourceBinding(ctx, bindingID); err == nil {
		return old, nil
	} else if !sourceNotFound(err) {
		return nil, err
	}
	programRaw := input["mapping_program"]
	delete(input, "mapping_program")
	_, b, e := contracts.Validate("format-binding-request", "2.0.0", sourceBytes(input))
	if e != nil {
		return nil, ErrInput
	}
	_ = json.Unmarshal(b, &input)
	id := bindingID
	input["id"] = id
	input["review_person_id"] = nil
	input["reviewed_at"] = sourceTime()
	input["origin"] = "source_import"
	input["provider_receipt_ids"] = []string{}
	input["input_modality"] = "native_annotation"
	src, _ := input["source_id"].(string)
	if !source.Known(src) {
		return nil, ErrInput
	}
	docs := []string{}
	for _, v := range input["documentation_asset_ids"].([]any) {
		docs = append(docs, v.(string))
	}
	if e = s.sourceAssetsExist(ctx, docs); e != nil {
		return nil, e
	}
	var program any
	var assetID any
	if programRaw != nil {
		_, p, e := contracts.Validate("source-mapping-program", "2.0.0", sourceBytes(programRaw))
		if e != nil {
			return nil, ErrInput
		}
		var value source.Program
		if e = json.Unmarshal(p, &value); e != nil {
			return nil, e
		}
		r, e := s.SourceRelease(ctx, value.Release)
		if e != nil || value.Source != src || r.Source != src || r.Manifest != value.Manifest {
			return nil, ErrReference
		}
		if e = s.sourceAssetsExist(ctx, value.Dictionaries); e != nil {
			return nil, e
		}
		program = value
		a, e := s.saveProviderBytes(ctx, p, "canonical_json")
		if e != nil {
			return nil, e
		}
		assetID = a.ID
	} else if existing, ok := input["binding_program_asset_id"].(string); ok {
		var p []byte
		e = s.DB.QueryRow(ctx, "SELECT program FROM source_format WHERE payload->>'binding_program_asset_id'=$1 AND program IS NOT NULL LIMIT 1", existing).Scan(&p)
		if sourceNotFound(e) {
			raw, err := s.ReadAsset(ctx, existing)
			if err != nil {
				return nil, err
			}
			_, p, e = contracts.Validate("source-mapping-program", "2.0.0", raw)
		}
		if e != nil {
			return nil, ErrInput
		}

		var value source.Program
		if e = json.Unmarshal(p, &value); e != nil {
			return nil, e
		}
		r, e := s.SourceRelease(ctx, value.Release)
		if e != nil || value.Source != src || r.Manifest != value.Manifest {
			return nil, ErrReference
		}
		program = value
		assetID = existing
	}
	input["binding_program_asset_id"] = assetID
	_, e = s.DB.Exec(ctx, "INSERT INTO source_format(id,source_id,payload,program) VALUES($1,$2,$3,$4)", id, src, sourceBytes(input), nullableJSON(program))
	return input, e
}
func nullableJSON(v any) any {
	if v == nil {
		return nil
	}
	return sourceBytes(v)
}
func (s *Storage) sourceBinding(ctx context.Context, id string) (map[string]any, *source.Program, error) {
	var raw, pr []byte
	var binding map[string]any
	e := s.DB.QueryRow(ctx, "SELECT payload,program FROM source_format WHERE id=$1", id).Scan(&raw, &pr)
	if e != nil {
		return nil, nil, e
	}
	if e = json.Unmarshal(raw, &binding); e != nil {
		return nil, nil, e
	}
	var p *source.Program
	if len(pr) > 0 {
		p = &source.Program{}
		e = json.Unmarshal(pr, p)
	}
	return binding, p, e
}
