package app

import (
	"context"
	"tangerine.local/api/internal/source"
	"testing"
)

func TestSourceL2AncillaryTierPositive(t *testing.T) {
	for _, name := range []string{"", "IPA", "ISU", "Comments", "Errors"} {
		m := source.BaseProjection("L2-ARCTIC", "r", "ABA/annotation/a.TextGrid", "intervals", 0, source.Row{"kind": "interval", "tier": name, "tier_index": 3, "start_seconds": "0.0", "end_seconds": "0.50", "label": "unclear, native, comment"})
		m.Status = "metadata"
		wav := source.Member{Path: "ABA/wav/a.wav", AssetID: "actual-wave", Media: map[string]any{"sample_rate_hz": 44100, "sample_count": 22050, "channels": 1}}
		s := Storage{}
		run := SourceRun{Frozen: SourceFrozen{Release: SourceRelease{Source: "L2-ARCTIC"}}}
		l2Require(t, s.enrichNative(context.Background(), run, &m, map[string]source.Member{wav.Path: wav}))
		l2Assert(t, "metadata", m.Status)
		raw := m.Value["raw_metadata"].(map[string]any)
		l2Assert(t, "ancillary_comment", raw["tier_role"])
		l2Assert(t, nil, raw["linguistic_interpretation"])
		l2Assert(t, nil, raw["phone_annotation"])
		l2Assert(t, name, m.Raw["tier"])
		l2Assert(t, "unclear, native, comment", m.Raw["label"])
	}
}
func TestSourceL2AncillaryTierNegative(t *testing.T) {
	m := source.BaseProjection("L2-ARCTIC", "r", "ABA/annotation/a.TextGrid", "intervals", 0, source.Row{"kind": "undocumented", "tier": "", "start_seconds": "0", "end_seconds": "0.5", "label": "native"})
	m.Status = "metadata"
	wav := source.Member{Path: "ABA/wav/a.wav", AssetID: "actual-wave", Media: map[string]any{"sample_rate_hz": 44100, "sample_count": 22050, "channels": 1}}
	s := Storage{}
	run := SourceRun{Frozen: SourceFrozen{Release: SourceRelease{Source: "L2-ARCTIC"}}}
	l2Require(t, s.enrichNative(context.Background(), run, &m, map[string]source.Member{wav.Path: wav}))
	l2Assert(t, "unmapped", m.Status)
	// A genuinely uninterpretable media clock must remain quarantined.
	m.Raw["end_seconds"] = "1"
	wav.Media["sample_rate_hz"] = 0
	m.Status = "metadata"
	l2Require(t, s.enrichNative(context.Background(), run, &m, map[string]source.Member{wav.Path: wav}))
	l2Assert(t, "quarantined", m.Status)
}
