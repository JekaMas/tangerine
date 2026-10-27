package app

import "math/big"

// Native Praat times are serialized binary64 values. Preserve their decimal
// lexemes, but do not reject the correctly rounded WAVE endpoint for being a
// fraction above its exact sample/rate rational. There is no arbitrary epsilon:
// an endpoint above the recording is the same exact endpoint only in that binary64 cell.
func sourceWaveEnd(end, frames, rate *big.Rat) (within, serializedEndpoint bool) {
	if end == nil || frames == nil || rate == nil || rate.Sign() <= 0 {
		return false, false
	}
	duration := new(big.Rat).Quo(frames, rate)
	if end.Cmp(duration) <= 0 {
		return true, false
	}
	native, _ := end.Float64()
	actual, _ := duration.Float64()
	return native == actual, native == actual
}
