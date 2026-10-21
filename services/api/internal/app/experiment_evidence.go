package app

import (
	"context"
	"encoding/json"
	"fmt"
	"tangerine.local/api/internal/experiment"
	"time"
)

type qualityOperationContextKey struct{}

func (s *Storage) linkQualityCall(ctx context.Context, receipt, kind string, delivered, projected bool) error {
	id, ok := ctx.Value(qualityOperationContextKey{}).(string)
	if !ok {
		return nil
	}
	_, e := s.DB.Exec(ctx, "INSERT INTO quality_call(row_operation_id,receipt_id,attempt_kind,delivered,projected) VALUES($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING", id, receipt, kind, delivered, projected)
	return e
}
func (s *Storage) qualityOperationReceipts(ctx context.Context, id string, fallback []string) ([]string, error) {
	rows, e := s.DB.Query(ctx, "SELECT c.receipt_id FROM quality_call c JOIN document d ON d.id=c.receipt_id WHERE row_operation_id=$1 ORDER BY d.payload->>'started_at',c.receipt_id", id)
	if e != nil {
		return nil, e
	}
	defer rows.Close()
	out := []string{}
	for rows.Next() {
		var id string
		if e = rows.Scan(&id); e != nil {
			return nil, e
		}
		out = append(out, id)
	}
	if len(out) == 0 {
		return fallback, rows.Err()
	}
	return out, rows.Err()
}
func (s *Storage) qualityReceiptEvidence(ctx context.Context, ids []string) (experiment.Evidence, error) {
	out := experiment.Evidence{Stats: map[string]string{}, Durations: []string{}, Tokens: []*string{}, Costs: []*string{}}
	calls := map[string]bool{}
	delivered := map[string]bool{}
	repaired := map[string]bool{}
	first := map[string]bool{}
	for _, id := range ids {
		doc, e := s.ReadDocument(ctx, id)
		if e != nil {
			return out, e
		}
		var r map[string]any
		if e = json.Unmarshal(doc.Payload, &r); e != nil {
			return out, e
		}
		start, e := time.Parse(time.RFC3339Nano, fmt.Sprint(r["started_at"]))
		if e != nil {
			return out, e
		}
		end, e := time.Parse(time.RFC3339Nano, fmt.Sprint(r["finished_at"]))
		if e != nil {
			return out, e
		}
		out.Durations = append(out.Durations, fmt.Sprint(end.Sub(start).Milliseconds()))
		for _, name := range []string{"input_tokens", "output_tokens"} {
			var v *string
			if x, ok := r[name].(string); ok {
				v = &x
			}
			out.Tokens = append(out.Tokens, v)
		}
		var cost *string
		if x, ok := r["cost_micro_usd"].(string); ok {
			cost = &x
		}
		out.Costs = append(out.Costs, cost)
		if r["stage"] == "tts" {
			continue
		}
		operation := fmt.Sprint(r["operation_id"])
		calls[operation] = true
		var kind string
		var hasReply, projected bool
		if e = s.DB.QueryRow(ctx, "SELECT attempt_kind,delivered,projected FROM quality_call WHERE receipt_id=$1", id).Scan(&kind, &hasReply, &projected); e != nil {
			return out, e
		}
		if kind == "semantic_repair" {
			repaired[operation] = true
		}
		if hasReply && !delivered[operation] {
			delivered[operation] = true
			if projected && kind != "semantic_repair" {
				first[operation] = true
			}
		}
	}
	out.Stats["initiated_logical_calls"] = fmt.Sprint(len(calls))
	out.Stats["logical_calls_with_delivered_reply"] = fmt.Sprint(len(delivered))
	out.Stats["projected_first_delivered_reply"] = fmt.Sprint(len(first))
	out.Stats["logical_calls_with_semantic_repair"] = fmt.Sprint(len(repaired))
	return out, nil
}
