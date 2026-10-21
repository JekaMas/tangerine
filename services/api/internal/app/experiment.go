package app

import (
	"context"
	"encoding/json"
	"net/http"
	"tangerine.local/api/internal/experiment"
	"time"
)

// RunQualityExperiment is an explicit foreground batch. Individual native owners
// retain their deadlines; a long batch does not restart a single call's budget.
func (s *Server) RunQualityExperiment(ctx context.Context, id string, resume bool, client *http.Client) (p QualityExperiment, err error) {
	p, err = s.Store.QualityExperiment(ctx, id)
	if err != nil {
		return p, err
	}
	if p.Status == "completed" {
		return p, nil
	}
	if p.Status != "planned" && !resume {
		return p, ErrConflict
	}
	batch, err := s.Store.claimQualityBatch(ctx, id, resume)
	if err != nil {
		return p, err
	}
	p, err = s.Store.QualityExperiment(ctx, id)
	if err != nil {
		return p, err
	}
	defer func() {
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
		defer done()
		_, _ = s.Store.DB.Exec(end, "UPDATE quality_experiment SET active_operation_id=NULL,lease_until=NULL WHERE id=$1 AND active_operation_id=$2", id, batch)
	}()
	frozen, err := s.Store.frozenExperiment(ctx, id)
	if err != nil {
		return p, err
	}
	p.Status = "running"
	p.Finished = nil
	for i := range p.Rows {
		row := &p.Rows[i]
		if row.Status != "not_run" {
			continue
		}
		cancelled, e := s.Store.qualityCancelled(ctx, id)
		if e != nil {
			return p, e
		}
		if cancelled || ctx.Err() != nil {
			p.Status = "cancelled"
			p.Finished = qualityTime()
			end, done := context.WithTimeout(context.WithoutCancel(ctx), 5*time.Second)
			err = s.Store.saveQualityProgress(end, p, batch, true)
			done()
			return p, err
		}
		op, e := s.Store.qualityRowOperation(ctx, id, i)
		if e != nil {
			return p, e
		}
		if e = s.Store.saveQualityProgress(ctx, p, batch, false); e != nil {
			return p, e
		}
		work, stop := context.WithCancel(ctx)
		work = context.WithValue(work, qualityBatchContextKey{}, qualityBatchOwner{id, batch})
		work = qualityContext(work, frozen.Variants[row.Variant])
		work = context.WithValue(work, qualityOperationContextKey{}, op)
		// Cancellation is observed between native operations and by the actual request
		// context. A UI cancel also cancels this active process through a local map.
		work, cancel := context.WithCancel(work)
		s.qualityCancels.Store(id, cancel)
		watchDone := make(chan struct{})
		go func() {
			defer close(watchDone)
			ticker := time.NewTicker(time.Second)
			defer ticker.Stop()
			for {
				select {
				case <-work.Done():
					return
				case <-ticker.C:
					requested, e := s.Store.qualityCancelled(work, id)
					if e == nil && requested {
						cancel()
						return
					}
				}
			}
		}()
		packet, result, e := s.executeQualityRow(work, p, frozen, *row, op, client)
		cancel()
		<-watchDone
		s.qualityCancels.Delete(id)
		stop()
		cleanup, cleanupDone := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
		defer cleanupDone()
		row.Receipts = result.ReceiptIDs
		if row.Receipts == nil {
			row.Receipts = []string{}
		}
		row.Traces = []string{}
		seenTraces := map[string]bool{}
		for _, receiptID := range row.Receipts {
			doc, re := s.Store.ReadDocument(cleanup, receiptID)
			if re != nil {
				return p, re
			}
			var receipt map[string]any
			if re = json.Unmarshal(doc.Payload, &receipt); re != nil {
				return p, re
			}
			if trace, ok := receipt["trace_id"].(string); ok && !seenTraces[trace] {
				seenTraces[trace] = true
				row.Traces = append(row.Traces, trace)
			}
		}
		row.Export = "disabled"
		if frozen.Variants[row.Variant].Configuration["llm_lab_trace_enabled"] == true {
			row.Export = "unexported"
		}
		row.Status = "complete"
		row.Error = nil
		cancelled, _ = s.Store.qualityCancelled(cleanup, id)
		if e != nil {
			row.Status = "failed"
			code, _ := speechPublicFailure(e)
			row.Error = &code
			if cancelled || ctx.Err() != nil {
				row.Status = "cancelled"
			}
		}
		if packet == nil {
			packet = map[string]any{}
		}
		evidence, _ := packet["diagnostic_evidence"].(experiment.Evidence)
		if evidence.Stats == nil {
			evidence.Stats = map[string]string{}
		}
		evidence.Stats["planned"] = "1"
		evidence.Stats["completed"] = "0"
		if row.Status == "complete" {
			evidence.Stats["completed"] = "1"
		}
		packet["diagnostic_evidence"] = evidence
		row.Metrics, err = experiment.Calculate([]experiment.Evidence{evidence})
		if err != nil {
			return p, err
		}
		end, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
		asset, e := s.Store.saveProviderBytes(end, sourceBytes(packet), "export")
		if e == nil {
			row.Output = &asset.ID
			e = s.Store.saveQualityProgress(end, p, batch, false)
		}
		done()
		if e != nil {
			return p, e
		}
		if cancelled || ctx.Err() != nil {
			p.Status = "cancelled"
			break
		}
	}
	if p.Status != "cancelled" {
		p.Status = "completed"
		for _, r := range p.Rows {
			if r.Status != "complete" {
				p.Status = "partial"
			}
		}
	}
	p.Finished = qualityTime()
	aggregateContext, aggregateDone := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer aggregateDone()
	evidence, err := s.Store.qualityEvidence(aggregateContext, p)
	if err != nil {
		return p, err
	}
	p.Aggregates = []QualityAggregate{}
	for _, variant := range p.Variants {
		es := []experiment.Evidence{}
		for _, r := range p.Rows {
			if r.Variant != variant.ID {
				continue
			}
			ev, ok := evidence[experiment.Key(r)]
			if !ok {
				ev = experiment.Evidence{Stats: map[string]string{"planned": "1", "completed": "0"}}
			}
			es = append(es, ev)
		}
		detections := []experiment.Detection{}
		for _, r := range p.Rows {
			if r.Variant != variant.ID {
				continue
			}
			ev := evidence[experiment.Key(r)]
			detections = append(detections, experiment.Detection{Case: r.Case, Variant: r.Variant, Repetition: r.Repetition, Complete: r.Status == "complete", Aligned: ev.Aligned, Events: ev.Detected})
		}
		if len(es) > 0 {
			pairs := experiment.RepetitionEvidence(detections)
			stats := map[string]string{}
			for key, value := range es[0].Stats {
				stats[key] = value
			}
			for key, value := range pairs.Stats {
				stats[key] = value
			}
			es[0].Stats = stats
			if pairs.Missing != nil {
				if es[0].Missing == nil {
					es[0].Missing = map[string]string{}
				}
				for key, value := range pairs.Missing {
					es[0].Missing[key] = value
				}
			}
		}
		metrics, e := experiment.Calculate(es)
		if e != nil {
			return p, e
		}
		for _, m := range metrics {
			p.Aggregates = append(p.Aggregates, QualityAggregate{variant.ID, m})
		}
	}
	comparisons := []experiment.Comparison{}
	if len(p.Variants) > 1 {
		for _, v := range p.Variants[1:] {
			cs, e := experiment.Compare(p.Rows, evidence, p.Variants[0].ID, v.ID)
			if e != nil {
				return p, e
			}
			comparisons = append(comparisons, cs...)
		}
	}
	end, done := context.WithTimeout(context.WithoutCancel(ctx), 15*time.Second)
	defer done()
	asset, err := s.Store.saveProviderBytes(end, sourceBytes(comparisons), "export")
	if err != nil {
		return p, err
	}
	p.Comparison = &asset.ID
	err = s.Store.saveQualityProgress(end, p, batch, true)
	return p, err
}
