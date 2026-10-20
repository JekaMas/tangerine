package app

// Publication is the existing render finalizer's atomic transition, not a review gate.
import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
)

func (s *Storage) publishListeningCase(ctx context.Context, tx pgx.Tx, source string, components map[string]any, title, format string) (string, error) {
	var id string
	e := tx.QueryRow(ctx, "SELECT case_version_id FROM listening_case WHERE source_key_id=$1", source).Scan(&id)
	if e == nil {
		return id, nil
	}
	if e != pgx.ErrNoRows {
		return "", e
	}
	var raw []byte
	if e = tx.QueryRow(ctx, "SELECT payload FROM document WHERE id=$1 AND kind='ground-truth'", source).Scan(&raw); e != nil {
		return "", e
	}
	var key map[string]any
	if e = json.Unmarshal(raw, &key); e != nil {
		return "", e
	}
	id = uuid.NewString()
	key["case_version_id"] = id
	key["status"] = "published"
	raw, _ = lab.Canonical(key)
	contract, raw, e := contracts.Validate("ground-truth", "2.0.0", raw)
	if e != nil {
		return "", e
	}
	audio := key["audio"].(map[string]any)
	var count int64
	if e = tx.QueryRow(ctx, "SELECT (byte_count-44)/2 FROM asset_location WHERE asset_id=$1 AND state='linked'", audio["asset_id"]).Scan(&count); e != nil {
		return "", e
	}
	if count < 1 {
		return "", ErrUnavailable
	}
	w := DocumentWrite{ID: id, Kind: "ground-truth", Version: "2.0.0", Scope: "local", Payload: raw}
	d := SavedDocument{ID: id, Kind: w.Kind, Version: w.Version, SchemaSHA: contract.SHA, SHA: contracts.Digest(raw), Payload: raw}
	if e = insertDocument(ctx, tx, w, d); e != nil {
		return "", e
	}
	flags, _ := json.Marshal(components)
	if _, e = tx.Exec(ctx, "INSERT INTO listening_case(case_version_id,source_key_id,audio_asset_id,case_sha256,audio_sha256,sample_count,task_components) VALUES($1,$2,$3,$4,$5,$6,$7)", id, source, audio["asset_id"], key["case_sha256"], audio["sha256"], count, flags); e != nil {
		return "", e
	}
	if title == "" {
		title = "Listening exercise"
	}
	if r := []rune(title); len(r) > 200 {
		title = string(r[:200])
	}
	_, e = tx.Exec(ctx, `INSERT INTO exercise_catalog(id,title,published_at,source_revision,audio_sha256,public_context,duration_ms,format,difficulty,availability) VALUES($1,$2,clock_timestamp(),$3,$4,$5,$6,$7,'unrated','published')`, id, title, source, audio["sha256"], key["public_context"], audio["duration_ms"], format)
	return id, e
}
