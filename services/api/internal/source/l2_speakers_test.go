package source

import "testing"

func TestL2SpeakerTablePositive(t *testing.T) {
	text := "### Other table\n|Index|ARPAbet|Example|\n|1|AA|odd|\n\n### File summary and speaker information\n|Speaker|Gender|Native Language|# Wav Files|# Annotations|\n|---|---|---|---|---|\n|ABA|M|Arabic|1129|150|\n|SKA|F|Arabic|974|150|\n|**Total**|||**2103**|**300**|\n\n### Phoneme set\n|1|AA|odd|\n"
	n, e := Parse("README.md", []byte(text), Options{Format: "l2-speakers", Encoding: "utf-8"})
	if e != nil {
		t.Fatal(e)
	}
	equal(t, 1, len(n.Tables))
	equal(t, "speakers", n.Tables[0].Name)
	equal(t, 2, len(n.Tables[0].Rows))
	equal(t, "ABA", n.Tables[0].Rows[0]["key"])
	equal(t, "Arabic", n.Tables[0].Rows[0]["native_language"])
	equal(t, "M", n.Tables[0].Rows[0]["gender"])
	equal(t, "1129", n.Tables[0].Rows[0]["read_wav_files"])
	equal(t, "|SKA|F|Arabic|974|150|", n.Tables[0].Rows[1]["source_line"])
	o, name, ok := NativePlan("L2-ARCTIC", NewMember("README.md"))
	equal(t, true, ok)
	equal(t, "speakers", name)
	equal(t, "l2-speakers", o.Format)
}
func TestL2SpeakerTableNegative(t *testing.T) {
	if _, e := Parse("README.md", []byte("|1|AA|odd|"), Options{Format: "l2-speakers"}); e == nil {
		t.Fatal("unrelated table invented speakers")
	}
	if _, e := Parse("README.md", []byte("|Speaker|Gender|Native Language|# Wav Files|# Annotations|\n|ABA|M|Arabic|unknown|150|"), Options{Format: "l2-speakers"}); e == nil {
		t.Fatal("unknown source count invented")
	}
	if _, _, ok := NativePlan("FCE-2.1", NewMember("README.md")); ok {
		t.Fatal("source-specific parser applied to other README")
	}
}
