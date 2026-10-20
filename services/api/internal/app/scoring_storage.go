package app

// Result documents are immutable. The interpretation transaction alone links
// their latest pointer, so an expired worker cannot publish an orphan result.
import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"math/big"
	"tangerine.local/api/internal/contracts"
	"tangerine.local/api/internal/lab"
	"tangerine.local/api/internal/scoring"
	"time"
)

func (s *Storage) saveScoringResult(ctx context.Context, envelope map[string]any, previous *string) (string, error) {
	id := uuid.NewString()
	envelope["result_id"] = id
	history := []any{}
	if old, ok := envelope["result_revision_ids"].([]any); ok {
		history = append(history, old...)
	}
	if previous != nil {
		history = append(history, *previous)
	}
	envelope["result_revision_ids"] = history
	raw, e := lab.Canonical(envelope)
	if e != nil {
		return "", e
	}
	// This is a derived application projection, not a new external document import.
	// Admit its DTO once; accepted semantic IDs inside the projection stay local
	// values, rather than manufacturing a second object graph for every label.
	contract, raw, e := contracts.Validate("result-envelope", "2.0.0", raw)
	if e != nil {
		return "", e
	}
	w := DocumentWrite{ID: id, Kind: "result-envelope", Version: "2.0.0", Scope: "local", Payload: raw}
	for pointer, subject := range map[string]string{"/attempt_id": envelope["attempt_id"].(string), "/score/case_version_id": envelope["score"].(map[string]any)["case_version_id"].(string)} {
		var sha, kind string
		if e = s.DB.QueryRow(ctx, "SELECT payload_sha256,kind FROM document WHERE id=$1", subject).Scan(&sha, &kind); e != nil {
			return "", e
		}
		w.References = append(w.References, Reference{Pointer: pointer, ID: subject, Scope: "local", Kind: kind, SHA: sha, Relation: "scoring-input"})
	}
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return "", e
	}
	defer tx.Rollback(context.Background())
	e = insertDocument(ctx, tx, w, SavedDocument{ID: id, Kind: w.Kind, Version: w.Version, SchemaSHA: contract.SHA, SHA: contracts.Digest(raw), Payload: raw})
	if e != nil {
		return "", e
	}
	return id, tx.Commit(ctx)
}
func (s *Storage) readScoringResult(ctx context.Context, id string) (map[string]any, error) {
	d, e := s.ReadDocument(ctx, id)
	if e != nil {
		return nil, e
	}
	var out map[string]any
	e = json.Unmarshal(d.Payload, &out)
	return out, e
}
func (s *Storage) scoringAuxiliary(ctx context.Context, a map[string]any) (map[string]any, error) {
	start, e := time.Parse(time.RFC3339Nano, a["started_at"].(string))
	if e != nil {
		return nil, e
	}
	end, e := time.Parse(time.RFC3339Nano, a["submitted_at"].(string))
	if e != nil {
		return nil, e
	}
	var plays int64
	e = s.DB.QueryRow(ctx, `SELECT count(*) FROM playback_index p JOIN document d ON d.id=p.event_id WHERE p.attempt_id=$1 AND d.payload->>'kind'='play' AND p.received_at<=$2`, a["attempt_id"], end).Scan(&plays)
	if e != nil {
		return nil, e
	}
	measurements, e := scoring.Auxiliary(map[string]scoring.Population{
		"telemetry.elapsed_seconds": {Numerator: new(big.Rat).SetInt64(end.Sub(start).Nanoseconds()), Denominator: new(big.Rat).SetInt64(1000000000), Method: "saved-wall-clock-v1", Evidence: []string{a["attempt_id"].(string)}},
		"telemetry.replay_count":    {Numerator: new(big.Rat).SetInt64(plays), Denominator: new(big.Rat).SetInt64(1), Method: "accepted-play-events-v1", Evidence: []string{a["attempt_id"].(string)}},
	})
	if e != nil {
		return nil, e
	}
	return map[string]any{"schema_version": "2.0.0", "attempt_id": a["attempt_id"], "case_version_id": a["case_version_id"], "measurements": measurements}, nil
}
