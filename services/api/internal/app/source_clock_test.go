package app

import (
	"math/big"
	"testing"
)

func TestSourceSerializedClockPositive(t *testing.T) {
	// Actual official ABA arctic_a0023 endpoint and original WAVE sample clock.
	end, _ := new(big.Rat).SetString("6.835963718820862")
	within, serialized := sourceWaveEnd(end, big.NewRat(301466, 1), big.NewRat(44100, 1))
	l2Assert(t, true, within)
	l2Assert(t, true, serialized)
	l2Assert(t, "6.835963718820862", end.FloatString(15))
	within, serialized = sourceWaveEnd(big.NewRat(1, 2), big.NewRat(22050, 1), big.NewRat(44100, 1))
	l2Assert(t, true, within)
	l2Assert(t, false, serialized)
}
func TestSourceSerializedClockNegative(t *testing.T) {
	for _, literal := range []string{"6.835963718820864", "7"} {
		end, _ := new(big.Rat).SetString(literal)
		within, _ := sourceWaveEnd(end, big.NewRat(301466, 1), big.NewRat(44100, 1))
		l2Assert(t, false, within)
	}
	within, _ := sourceWaveEnd(big.NewRat(5001, 10000), big.NewRat(22050, 1), big.NewRat(44100, 1))
	l2Assert(t, false, within)
	within, _ = sourceWaveEnd(big.NewRat(1, 2), big.NewRat(22050, 1), big.NewRat(0, 1))
	l2Assert(t, false, within)
}
