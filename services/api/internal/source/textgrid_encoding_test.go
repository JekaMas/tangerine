package source

import (
	"bytes"
	"context"
	"testing"
	"unicode/utf16"
)

func sourceUTF16Grid(text string, encoding string) []byte {
	var b bytes.Buffer
	for _, v := range utf16.Encode([]rune("\ufeff" + text)) {
		if encoding == "utf-16le" {
			b.WriteByte(byte(v))
			b.WriteByte(byte(v >> 8))
		} else {
			b.WriteByte(byte(v >> 8))
			b.WriteByte(byte(v))
		}
	}
	return b.Bytes()
}
func TestSourceTextGridEncodingPositive(t *testing.T) {
	for _, encoding := range []string{"utf-16le", "utf-16be"} {
		rows := []Row{}
		e := Walk(context.Background(), "annotation/a.TextGrid", bytes.NewReader(sourceUTF16Grid(gridLong, encoding)), Options{Format: "textgrid", Encoding: encoding}, func(_ string, row Row) error { rows = append(rows, row); return nil })
		if e != nil {
			t.Fatal(e)
		}
		equal(t, 1, len(rows))
		equal(t, "T,D,s", rows[0]["label"])
		equal(t, "0.1250", rows[0]["start_seconds"])
	}
}
func TestSourceTextGridEncodingNegative(t *testing.T) {
	e := Walk(context.Background(), "bad.TextGrid", bytes.NewReader([]byte{0xff, 0xfe, 1}), Options{Format: "textgrid", Encoding: "utf-16le"}, func(_ string, _ Row) error { return nil })
	if e == nil {
		t.Fatal("truncated encoded TextGrid silently accepted")
	}
}
