package source

import "testing"

func TestSupplementNativePlanPositive(t *testing.T) {
	for _, c := range []struct{ id, member, format, table string }{
		{"EDACC", "edacc_v1.0/dev/segments", "lines", "sp_edacc_segments"},
		{"ELRD", "owner/diarized_transcripts/meeting-a-dm01-dm02.jsonl", "jsonl", "sp_elrd_turns"},
		{"DIPLOMAT", "NLI_task_dataset/dataset.json", "jsonl", "sp_diplomat"},
		{"DRAL", "DRAL-8.0/fragments-short.csv", "csv", "sp_dral_fragments_short"},
	} {
		if !Known(c.id) {
			t.Fatalf("Supplemental source %s is unavailable", c.id)
		}
		o, table, ok := NativePlan(c.id, NewMember(c.member))
		if !ok || o.Format != c.format || table != c.table {
			t.Fatalf("%s: got %v %s %s", c.id, ok, o.Format, table)
		}
	}
	if len(IDs) != 11 {
		t.Fatal("Original source scope changed")
	}
}
func TestSupplementNativePlanNegative(t *testing.T) {
	if Known("UNACQUIRED-SUPPLEMENT") {
		t.Fatal("Unknown source invented")
	}
	for _, id := range []string{"EDACC", "ELRD", "DIPLOMAT", "DRAL"} {
		_, table, ok := NativePlan(id, NewMember("owner/evaluate.sh"))
		if ok || table != "ancillary" {
			t.Fatal("Source code became data/execution", id, table)
		}
	}
}
func TestSupplementHistoricalNegative(t *testing.T) {
	for _, name := range []string{"DRAL16kHz/dral-16kHz.tgz/metadata/participant.csv", "DRAL16kHz/history.tar.gz/fragments-short/ES_001.wav"} {
		_, table, parsed := NativePlan("DRAL", NewMember(name))
		if parsed || table != "ancillary" {
			t.Fatal("Overlapping historical view became another primary population", name)
		}
	}
}
func TestSupplementClockPositive(t *testing.T) {
	for native, want := range map[string]string{"0 days 00:00:06.310000": "631/100", "0:01:00.430000": "6043/100", "5.22": "261/50", "71/100": "71/100"} {
		got := SourceSeconds(native)
		if got == nil || got.RatString() != want {
			t.Fatal("Native exact clock lost", native, got)
		}
	}
}
func TestSupplementClockNegative(t *testing.T) {
	for _, native := range []string{"unknown", "-1", "0:00:-1", "1 days 00:00:00"} {
		if SourceSeconds(native) != nil {
			t.Fatal("Unknown clock guessed", native)
		}
	}
	if SourceClock("2", "1")["start"] != nil {
		t.Fatal("Reversed interval guessed")
	}
}
