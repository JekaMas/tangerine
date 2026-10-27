package app

import (
	"context"
	"tangerine.local/api/internal/source"
	"testing"
)

func TestSourceL2ClockQualityPositive(t *testing.T) {
	m := source.BaseProjection("L2-ARCTIC", "r", "HKK/annotation/a.TextGrid", "intervals", 0, source.Row{"kind": "interval", "tier": "phones", "start_seconds": "0", "end_seconds": "1.201375", "label": "S"})
	m.Status = "metadata"
	wav := source.Member{Path: "HKK/wav/a.wav", AssetID: "actual-wave", Media: map[string]any{"sample_rate_hz": 44100, "sample_count": 52980, "channels": 1}}
	s := Storage{}
	run := SourceRun{Report: SourceReport{ParserVersion: source.L2ParserVersion}, Frozen: SourceFrozen{Native: true, Release: SourceRelease{Source: "L2-ARCTIC"}}}
	l2Require(t, s.enrichNative(context.Background(), run, &m, map[string]source.Member{wav.Path: wav}))
	l2Assert(t, "metadata", m.Status)
	raw := m.Value["raw_metadata"].(map[string]any)
	l2Assert(t, "native_extent_exceeds_media", raw["clock_bound_relation"])
	l2Assert(t, "unverified", raw["clock_alignment_status"])
	l2Assert(t, nil, raw["annotation_processing_rate_hz"])
	l2Assert(t, "1.201375", m.Raw["end_seconds"])
}
func TestSourceL2ClockQualityNegative(t *testing.T) {
	m := source.BaseProjection("L2-ARCTIC", "r", "HKK/annotation/a.TextGrid", "intervals", 0, source.Row{"kind": "interval", "tier": "phones", "start_seconds": "0", "end_seconds": "0.5001", "label": "S"})
	m.Status = "metadata"
	wav := source.Member{Path: "HKK/wav/a.wav", AssetID: "actual-wave", Media: map[string]any{"sample_rate_hz": 44100, "sample_count": 22050, "channels": 1}}
	s := Storage{}
	run := SourceRun{Report: SourceReport{ParserVersion: source.L2ParserVersion}, Frozen: SourceFrozen{Native: true, Release: SourceRelease{Source: "L2-ARCTIC"}}}
	l2Require(t, s.enrichNative(context.Background(), run, &m, map[string]source.Member{wav.Path: wav}))
	raw := m.Value["raw_metadata"].(map[string]any)
	l2Assert(t, "metadata", m.Status)
	l2Assert(t, "unverified", raw["clock_alignment_status"])
	l2Assert(t, nil, raw["annotation_processing_rate_hz"])
	// Structurally invalid clocks still fail the v2 import; no fabricated rate.
	wav.Media["sample_rate_hz"] = 0
	l2Require(t, s.enrichNative(context.Background(), run, &m, map[string]source.Member{wav.Path: wav}))
	l2Assert(t, "quarantined", m.Status)
}
