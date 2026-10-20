// Package scoring owns exact arithmetic and counting over admitted decisions.
// It has no provider, persistence, HTTP or UI dependencies.
package scoring

import (
	"errors"
	"math/big"
)

var ErrMagnitude = errors.New("exact rational exceeds 4096 decimal digits")

type Exact struct {
	Numerator   string `json:"numerator"`
	Denominator string `json:"denominator"`
}

func fraction(n, d int64) *big.Rat { return new(big.Rat).SetFrac64(n, d) }
func exact(r *big.Rat) (*Exact, error) {
	if r == nil {
		return nil, nil
	}
	n, d := r.Num().String(), r.Denom().String()
	if len(new(big.Int).Abs(r.Num()).String()) > 4096 || len(d) > 4096 {
		return nil, ErrMagnitude
	}
	return &Exact{n, d}, nil
}

// Display rounds a ratio to one decimal, half up, optionally as percent.
// It never passes through floating point or becomes an arithmetic input.
func Display(r *big.Rat, percent bool) string {
	if r.Sign() < 0 {
		value := Display(new(big.Rat).Neg(r), percent)
		if value == "0.0" {
			return value
		}
		return "-" + value
	}
	scale := int64(10)
	if percent {
		scale = 1000
	}
	n := new(big.Int).Mul(r.Num(), big.NewInt(scale))
	q, rem := new(big.Int), new(big.Int)
	q.QuoRem(n, r.Denom(), rem)
	if new(big.Int).Mul(rem, big.NewInt(2)).Cmp(r.Denom()) >= 0 {
		q.Add(q, big.NewInt(1))
	}
	whole, decimal := new(big.Int), new(big.Int)
	whole.QuoRem(q, big.NewInt(10), decimal)
	return whole.String() + "." + decimal.String()
}

type Metric struct {
	Value       *float64 `json:"value"`
	Numerator   *string  `json:"numerator"`
	Denominator *string  `json:"denominator"`
	Status      string   `json:"status"`
	Reason      *string  `json:"reason"`
	Display     *string  `json:"display,omitempty"`
}

func absent(status, reason string) Metric { return Metric{Status: status, Reason: &reason} }
func ratio(n, d *big.Rat, no string, unknown bool) (Metric, error) {
	if d.Sign() == 0 {
		return absent("not_applicable", no), nil
	}
	if unknown {
		return absent("review_required", "unresolved"), nil
	}
	r := new(big.Rat).Quo(n, d)
	e, err := exact(r)
	if err != nil {
		return Metric{}, err
	}
	v, _ := r.Float64()
	display := Display(r, true)
	return Metric{Value: &v, Numerator: &e.Numerator, Denominator: &e.Denominator, Status: "available", Display: &display}, nil
}
