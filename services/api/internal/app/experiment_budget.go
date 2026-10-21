package app

import (
	"context"
	"time"
)

type qualityBatchContextKey struct{}
type qualityBatchOwner struct{ Experiment, Operation string }

// Lab composes separately bounded native operations. It does not impose a new
// 270-second cap over a whole generate→mutate→render→judge experiment row.
func (s *Storage) qualityOwnerContext(ctx context.Context) (context.Context, context.CancelFunc, error) {
	if owner, ok := ctx.Value(qualityBatchContextKey{}).(qualityBatchOwner); ok {
		tag, e := s.DB.Exec(ctx, "UPDATE quality_experiment SET lease_until=clock_timestamp()+interval '270 seconds' WHERE id=$1 AND active_operation_id=$2", owner.Experiment, owner.Operation)
		if e != nil {
			return nil, nil, e
		}
		if tag.RowsAffected() != 1 {
			return nil, nil, ErrEvaluationLease
		}
	}
	work, cancel := context.WithTimeout(ctx, 270*time.Second)
	return work, cancel, nil
}
