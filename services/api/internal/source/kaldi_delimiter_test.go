package source

import "testing"

func TestSourceKaldiDelimiterPositive(t *testing.T) {
	for _, input := range []string{"000010011\tWE CALL IT BEAR\n", "000010011 WE CALL IT BEAR\n", "000010011\t  WE CALL IT BEAR\r\n"} {
		native, err := parseKaldi("train/text", input)
		if err != nil {
			t.Fatal(err)
		}
		equal(t, 0, len(native.Issues))
		row := native.Tables[0].Rows[0]
		equal(t, "000010011", row["key"])
		equal(t, "WE CALL IT BEAR", row["value"])
		equal(t, []string{"WE", "CALL", "IT", "BEAR"}, row["fields"])
	}
}

func TestSourceKaldiDelimiterNegative(t *testing.T) {
	native, err := parseKaldi("train/text", "000010011\tWE CALL IT BEAR\n000010011 WE CALL IT DIFFERENTLY\n")
	if err != nil {
		t.Fatal(err)
	}
	if native.Tables[0].Rows[1]["invalid"] != true || len(native.Issues) != 1 || native.Issues[0].Code != "duplicate_key" {
		t.Fatal("mixed separators hid a conflicting native identity", native)
	}
	equal(t, "000010011\tWE CALL IT BEAR", native.Tables[0].Rows[0]["raw"])
	equal(t, "000010011 WE CALL IT DIFFERENTLY", native.Tables[0].Rows[1]["raw"])
}
