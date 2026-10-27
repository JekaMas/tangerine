package source

import "testing"

func TestSourceTextGridTierOrderPositive(t *testing.T) {
	text := "\"ooTextFile\"\n\"TextGrid\"\n0\n1\n<exists>\n3\n\"IntervalTier\"\n\"phones\"\n0\n1\n1\n0\n1\n\"S\"\n\"TextTier\"\n\"Comments\"\n0\n1\n1\n0.5\n\"unclear\"\n\"IntervalTier\"\n\"\"\n0\n1\n1\n0\n1\n\"\"\n"
	n, e := Parse("annotation/native.TextGrid", []byte(text), Options{Format: "textgrid"})
	if e != nil {
		t.Fatal(e)
	}
	equal(t, 1, n.Tables[0].Rows[0]["tier_index"])
	equal(t, 3, n.Tables[0].Rows[1]["tier_index"])
	equal(t, 2, n.Tables[1].Rows[0]["tier_index"])
	equal(t, "", n.Tables[0].Rows[1]["tier"])
	equal(t, "unclear", n.Tables[1].Rows[0]["label"])
}
func TestSourceTextGridTierOrderNegative(t *testing.T) {
	// A tier-local interval index alone must never alias different native tiers.
	text := "\"ooTextFile\"\n\"TextGrid\"\n0\n1\n<exists>\n2\n\"IntervalTier\"\n\"phones\"\n0\n1\n1\n0\n1\n\"D\"\n\"IntervalTier\"\n\"phones\"\n0\n1\n1\n0\n1\n\"S\"\n"
	n, e := Parse("annotation/native.TextGrid", []byte(text), Options{Format: "textgrid"})
	if e != nil {
		t.Fatal(e)
	}
	equal(t, 2, len(n.Tables[0].Rows))
	equal(t, n.Tables[0].Rows[0]["index"], n.Tables[0].Rows[1]["index"])
	if n.Tables[0].Rows[0]["tier_index"] == n.Tables[0].Rows[1]["tier_index"] {
		t.Fatal("different native tiers aliased")
	}
}
