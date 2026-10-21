package app

import (
	"context"
	"encoding/json"
	"fmt"
	"tangerine.local/api/internal/experiment"
)

type QualityExportReceipt struct {
	Experiment    string            `json:"experiment_id"`
	Run           string            `json:"run"`
	Rows          []experiment.Row  `json:"rows"`
	Artifacts     []json.RawMessage `json:"artifacts"`
	ProviderCalls int               `json:"provider_calls"`
	NativeExports []struct {
		ProviderCalls int `json:"provider_calls"`
		Traces        []struct {
			State string `json:"state"`
		} `json:"trace_exports"`
	} `json:"native_exports"`
}

func (s *Storage) AcknowledgeQualityExport(ctx context.Context, receipt QualityExportReceipt) error {
	if receipt.Experiment == "" || receipt.Run == "" || len(receipt.Artifacts) == 0 || receipt.ProviderCalls != 0 {
		return ErrInput
	}
	for _, native := range receipt.NativeExports {
		if native.ProviderCalls != 0 {
			return ErrInput
		}
		for _, trace := range native.Traces {
			if trace.State != "exported" {
				return fmt.Errorf("native trace export remains incomplete")
			}
		}
	}
	asset, e := s.saveProviderBytes(ctx, sourceBytes(receipt), "export")
	if e != nil {
		return e
	}
	_, e = s.DB.Exec(ctx, "INSERT INTO quality_export(experiment_id,asset_id,payload) VALUES($1,$2,$3) ON CONFLICT DO NOTHING", receipt.Experiment, asset.ID, sourceBytes(receipt))
	return e
}
func (s *Storage) qualityExportStatus(ctx context.Context, p *QualityExperiment) error {
	rows, e := s.DB.Query(ctx, "SELECT payload FROM quality_export WHERE experiment_id=$1 ORDER BY created_at", p.ID)
	if e != nil {
		return e
	}
	defer rows.Close()
	for rows.Next() {
		var raw []byte
		if e = rows.Scan(&raw); e != nil {
			return e
		}
		var receipt QualityExportReceipt
		if e = json.Unmarshal(raw, &receipt); e != nil {
			return e
		}
		index := map[string]experiment.Row{}
		for _, r := range receipt.Rows {
			index[experiment.Key(r)] = r
		}
		for i, r := range p.Rows {
			if prior, ok := index[experiment.Key(r)]; ok && optionalID(prior.Output) == optionalID(r.Output) && prior.Status == r.Status {
				p.Rows[i].Export = "exported"
			}
		}
	}
	return rows.Err()
}
