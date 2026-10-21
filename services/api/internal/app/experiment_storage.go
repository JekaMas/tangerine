package app

import (
	"context"
	"encoding/json"
	"github.com/google/uuid"
	"tangerine.local/api/internal/experiment"
	"time"
)

func (s *Storage) QualityExperiment(ctx context.Context, id string) (QualityExperiment, error) {
	var raw []byte
	var p QualityExperiment
	e := s.DB.QueryRow(ctx, "SELECT payload FROM quality_experiment WHERE id=$1", id).Scan(&raw)
	if e == nil {
		e = json.Unmarshal(raw, &p)
		if e == nil {
			e = s.qualityExportStatus(ctx, &p)
		}
	}
	return p, e
}
func (s *Storage) QualityExperiments(ctx context.Context) ([]QualityExperiment, error) {
	rows, e := s.DB.Query(ctx, "SELECT payload FROM quality_experiment ORDER BY created_at DESC,id")
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	out := []QualityExperiment{}
	for rows.Next() {
		var raw []byte
		var p QualityExperiment
		if e = rows.Scan(&raw); e != nil {
			return nil, e
		}
		if e = json.Unmarshal(raw, &p); e != nil {
			return nil, e
		}
		out = append(out, p)
	}
	return out, rows.Err()
}
func (s *Storage) frozenExperiment(ctx context.Context, id string) (qualityFrozen, error) {
	var asset string
	var f qualityFrozen
	e := s.DB.QueryRow(ctx, "SELECT frozen_asset_id FROM quality_experiment WHERE id=$1", id).Scan(&asset)
	if e != nil {
		return f, e
	}
	raw, e := s.ReadAsset(ctx, asset)
	if e == nil {
		e = json.Unmarshal(raw, &f)
	}
	return f, e
}
func (s *Storage) claimQualityBatch(ctx context.Context, id string, resume bool) (string, error) {
	op, e := s.ReserveOperation(ctx, OperationRequest{Name: "quality_batch", Key: uuid.NewString(), Path: "/lab/eval", Body: sourceBytes(map[string]any{"experiment_id": id})})
	if e != nil {
		return "", e
	}
	tag, e := s.DB.Exec(ctx, "UPDATE quality_experiment SET active_operation_id=$2,lease_until=clock_timestamp()+interval '270 seconds',cancel_requested=CASE WHEN $3 THEN false ELSE cancel_requested END,revision=revision+1 WHERE id=$1 AND (active_operation_id IS NULL OR lease_until<clock_timestamp())", id, op.ID, resume)
	if e != nil {
		return "", e
	}
	if tag.RowsAffected() != 1 {
		return "", ErrEvaluationActive
	}
	return op.ID, nil
}
func (s *Storage) qualityRowOperation(ctx context.Context, id string, index int) (string, error) {
	op, e := s.ReserveOperation(ctx, OperationRequest{Name: "quality_row", Key: qualityKey(id, index, "row"), Path: "/lab/eval/row", Body: sourceBytes(map[string]any{"experiment_id": id, "row": index})})
	return op.ID, e
}
func (s *Storage) saveQualityProgress(ctx context.Context, p QualityExperiment, operation string, finish bool) error {
	tx, e := beginWrite(ctx, s)
	if e != nil {
		return e
	}
	defer tx.Rollback(context.Background())
	var revision int64
	e = tx.QueryRow(ctx, "UPDATE quality_experiment SET payload=$2,revision=revision+1,active_operation_id=CASE WHEN $4 THEN NULL ELSE active_operation_id END,lease_until=CASE WHEN $4 THEN NULL ELSE clock_timestamp()+interval '270 seconds' END WHERE id=$1 AND active_operation_id=$3 RETURNING revision", p.ID, sourceBytes(p), operation, finish).Scan(&revision)
	if e != nil {
		return ErrEvaluationLease
	}
	if _, e = tx.Exec(ctx, "INSERT INTO quality_experiment_event(experiment_id,revision,payload) VALUES($1,$2,$3)", p.ID, revision, sourceBytes(p)); e != nil {
		return e
	}
	if finish {
		if _, e = tx.Exec(ctx, "UPDATE operation SET state='complete',finished_at=clock_timestamp() WHERE id=$1", operation); e != nil {
			return e
		}
	}
	return tx.Commit(ctx)
}
func (s *Storage) CancelQualityExperiment(ctx context.Context, id string) error {
	tag, e := s.DB.Exec(ctx, "UPDATE quality_experiment SET cancel_requested=true,revision=revision+1 WHERE id=$1", id)
	if e == nil && tag.RowsAffected() == 0 {
		return ErrReference
	}
	return e
}
func (s *Storage) qualityCancelled(ctx context.Context, id string) (bool, error) {
	var v bool
	e := s.DB.QueryRow(ctx, "SELECT cancel_requested FROM quality_experiment WHERE id=$1", id).Scan(&v)
	return v, e
}
func (s *Storage) qualityEvidence(ctx context.Context, p QualityExperiment) (map[string]experiment.Evidence, error) {
	out := map[string]experiment.Evidence{}
	for _, row := range p.Rows {
		if row.Output == nil {
			continue
		}
		raw, e := s.ReadAsset(ctx, *row.Output)
		if e != nil {
			return nil, e
		}
		var packet struct {
			Evidence experiment.Evidence `json:"diagnostic_evidence"`
		}
		if e = json.Unmarshal(raw, &packet); e != nil {
			return nil, e
		}
		out[experiment.Key(row)] = packet.Evidence
	}
	return out, nil
}
func qualityTime() *string { s := time.Now().UTC().Format(time.RFC3339Nano); return &s }
func qualityKey(id string, row int, stage string) string {
	return interpretationCallKey(id, stage+":"+uuid.NewSHA1(uuid.NameSpaceOID, sourceBytes(row)).String())
}
