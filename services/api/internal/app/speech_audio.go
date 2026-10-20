package app

import (
	"encoding/binary"
)

func speechWAV(pcm []byte) []byte {
	out := make([]byte, 44, len(pcm)+44)
	copy(out, "RIFF")
	binary.LittleEndian.PutUint32(out[4:], uint32(len(pcm)+36))
	copy(out[8:], "WAVEfmt ")
	binary.LittleEndian.PutUint32(out[16:], 16)
	binary.LittleEndian.PutUint16(out[20:], 1)
	binary.LittleEndian.PutUint16(out[22:], 1)
	binary.LittleEndian.PutUint32(out[24:], 24000)
	binary.LittleEndian.PutUint32(out[28:], 48000)
	binary.LittleEndian.PutUint16(out[32:], 2)
	binary.LittleEndian.PutUint16(out[34:], 16)
	copy(out[36:], "data")
	binary.LittleEndian.PutUint32(out[40:], uint32(len(pcm)))
	return append(out, pcm...)
}

// speechPaceObservations keeps requested pace separate from acoustic measurements.
// Written words and full-clip duration do not establish spoken lexical tokens/onsets.
func speechPaceObservations(settings map[string]any) []any {
	rows := []any{}
	for _, value := range settings["blueprint"].(map[string]any)["speakers"].([]any) {
		speaker := value.(map[string]any)
		rows = append(rows, map[string]any{"speaker_id": speaker["id"], "target_wpm": speaker["pace_wpm"], "tolerance_fraction": speaker["pace_tolerance_fraction"], "observed_wpm": nil, "deviation_fraction": nil, "state": "not_measurable", "reason": "timed_lexical_tokens_unavailable"})
	}
	return rows
}
