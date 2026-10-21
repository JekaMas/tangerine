package app

import (
	"context"
	"encoding/json"
	"fmt"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/source"
	"time"
)

func (s *Storage) RegisterSourcePermission(ctx context.Context, body []byte) (map[string]any, error) {
	_, b, e := contracts.Validate("grant-request", "2.0.0", body)
	if e != nil {
		return nil, ErrInput
	}
	var p map[string]any
	_ = json.Unmarshal(b, &p)
	src := p["source_id"].(string)
	if !source.Known(src) {
		return nil, ErrInput
	}
	docs := []string{}
	for _, v := range p["scope_document_asset_ids"].([]any) {
		docs = append(docs, v.(string))
	}
	if e = s.sourceAssetsExist(ctx, docs); e != nil {
		return nil, e
	}
	if p["status"] == "permitted" && len(docs) == 0 {
		return nil, fmt.Errorf("%w: actual source terms required", ErrReference)
	}
	for _, v := range p["release_ids"].([]any) {
		r, e := s.SourceRelease(ctx, v.(string))
		if e != nil || r.Source != src {
			return nil, ErrReference
		}
	}
	p["id"] = source.StableID("source-permission", string(b))
	p["created_at"] = sourceTime()
	_, e = s.DB.Exec(ctx, "INSERT INTO source_permission(id,source_id,payload,revoked_at) VALUES($1,$2,$3,$4) ON CONFLICT(id) DO NOTHING", p["id"], src, sourceBytes(p), p["revoked_at"])
	if e != nil {
		return nil, e
	}
	var saved []byte
	if e = s.DB.QueryRow(ctx, "SELECT payload FROM source_permission WHERE id=$1", p["id"]).Scan(&saved); e != nil {
		return nil, e
	}
	_ = json.Unmarshal(saved, &p)
	return p, nil
}
func (s *Storage) RevokeSourcePermission(ctx context.Context, id, notice string) error {
	if e := s.sourceAssetsExist(ctx, []string{notice}); e != nil {
		return e
	}
	tag, e := s.DB.Exec(ctx, "UPDATE source_permission SET revoked_notice_asset_id=$2,revoked_at=coalesce(revoked_at,clock_timestamp()) WHERE id=$1", id, notice)
	if e != nil {
		return e
	}
	if tag.RowsAffected() != 1 {
		return ErrReference
	}
	return nil
}

// Selected-use metadata is evaluated at the consumer's explicit action, never a
// startup/import gate. It cannot promote mere provider/API access into a licence.
func (s *Storage) sourceLicence(ctx context.Context, release SourceRelease, ids []string) (map[string]any, error) {
	result := map[string]any{"source_id": release.Source, "source_record_id": nil, "rights_approval_id": nil, "uses": []string{}, "status": "pending", "licence_evidence_hash": nil}
	now := time.Now().UTC()
	uses := map[string]bool{}
	for _, id := range ids {
		var raw []byte
		var revoked *time.Time
		e := s.DB.QueryRow(ctx, "SELECT payload,revoked_at FROM source_permission WHERE id=$1 AND source_id=$2", id, release.Source).Scan(&raw, &revoked)
		if e != nil {
			return nil, ErrReference
		}
		var p map[string]any
		_ = json.Unmarshal(raw, &p)
		releases := p["release_ids"].([]any)
		matches := len(releases) == 0
		for _, v := range releases {
			if v == release.ID {
				matches = true
			}
		}
		if !matches {
			return nil, ErrReference
		}
		if revoked != nil || p["status"] == "revoked" {
			continue
		}
		if p["status"] != "permitted" {
			continue
		}
		valid, _ := time.Parse(time.RFC3339Nano, p["valid_from"].(string))
		if valid.After(now) {
			continue
		}
		if until, ok := p["valid_until"].(string); ok {
			expires, _ := time.Parse(time.RFC3339Nano, until)
			if !expires.After(now) {
				continue
			}
		}
		docs := p["scope_document_asset_ids"].([]any)
		if len(docs) == 0 {
			continue
		}
		var sha string
		if e = s.DB.QueryRow(ctx, "SELECT sha256 FROM asset_location WHERE asset_id=$1 AND state='linked'", docs[0]).Scan(&sha); e != nil {
			return nil, e
		}
		uses = map[string]bool{}
		for _, v := range p["uses"].([]any) {
			uses[v.(string)] = true
		}
		result["rights_approval_id"] = id
		result["licence_evidence_hash"] = sha
		result["status"] = "approved"
	}
	allowed := []string{}
	for _, name := range []string{"local_analysis", "commercial_evaluation", "derivative_exercises", "distribution", "model_training", "external_api_transfer", "voice_use"} {
		if uses[name] {
			allowed = append(allowed, name)
		}
	}
	result["uses"] = allowed
	return result, nil
}
func (s *Storage) SourceUse(ctx context.Context, release string, ids []string, use string) error {
	r, e := s.SourceRelease(ctx, release)
	if e != nil {
		return e
	}
	for _, id := range ids {
		licence, e := s.sourceLicence(ctx, r, []string{id})
		if e != nil {
			return e
		}
		for _, v := range licence["uses"].([]string) {
			if v == use {
				return nil
			}
		}
	}
	return source.Failure(release, "rights_missing", "Selected use is absent from actual current source terms")
}
