package source

import (
	"bytes"
	"context"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"strings"
	"unicode/utf16"
	"unicode/utf8"
)

func Parse(member string, data []byte, o Options) (Native, error) {
	if o.Format == "xlsx" {
		return workbook(member, data, o.Selector)
	}
	text, e := decodeText(data, o.Encoding)
	if e != nil {
		return Native{}, Failure(member, "encoding", e.Error())
	}
	var n Native
	switch o.Format {
	case "json", "jsonl":
		n, e = parseJSON(member, text, o.Format)
	case "csv", "tsv":
		n, e = parseCSV(member, text, o)
	case "xml":
		n, e = parseXML(member, text, o.Selector)
	case "m2":
		n, e = parseM2(member, text)
	case "textgrid":
		n, e = parseTextGrid(member, text)
	case "l2-speakers":
		n, e = parseL2Speakers(member, text)
	case "kaldi":
		n, e = parseKaldi(member, text)
	default:
		e = Failure(member, "format_unbound", "No documented native format selected")
	}
	return n, e
}
func decodeText(data []byte, encoding string) (string, error) {
	switch encoding {
	case "", "utf-8", "utf-8-sig":
		if encoding == "utf-8-sig" {
			data = bytes.TrimPrefix(data, []byte{239, 187, 191})
		}
		if !utf8.Valid(data) {
			return "", fmt.Errorf("invalid UTF-8")
		}
		return string(data), nil
	case "utf-16le", "utf-16be":
		if len(data)%2 != 0 {
			return "", fmt.Errorf("odd UTF-16 byte count")
		}
		s := make([]uint16, 0, len(data)/2)
		for i := 0; i < len(data); i += 2 {
			var v uint16
			if encoding == "utf-16le" {
				v = uint16(data[i]) | uint16(data[i+1])<<8
			} else {
				v = uint16(data[i])<<8 | uint16(data[i+1])
			}
			s = append(s, v)
		}
		if len(s) > 0 && s[0] == 0xfeff {
			s = s[1:]
		}
		for i, v := range s {
			if 0xd800 <= v && v <= 0xdbff {
				if i+1 == len(s) || s[i+1] < 0xdc00 || s[i+1] > 0xdfff {
					return "", fmt.Errorf("unpaired UTF-16 surrogate")
				}
			} else if 0xdc00 <= v && v <= 0xdfff && (i == 0 || s[i-1] < 0xd800 || s[i-1] > 0xdbff) {
				return "", fmt.Errorf("unpaired UTF-16 surrogate")
			}
		}
		return string(utf16.Decode(s)), nil
	}
	return "", fmt.Errorf("unsupported documented encoding")
}
func parseJSON(member, text, format string) (Native, error) {
	rows := []Row{}
	e := Walk(context.Background(), member, strings.NewReader(text), Options{Format: format}, func(_ string, row Row) error { rows = append(rows, row); return nil })
	return Native{Tables: []Table{{"records", member, rows}}}, e
}

func parseCSV(member, text string, o Options) (Native, error) {
	c := csv.NewReader(strings.NewReader(text))
	c.FieldsPerRecord = -1
	c.ReuseRecord = false
	if o.Format == "tsv" {
		c.Comma = '\t'
	}
	if o.Delimiter != nil {
		rr := []rune(*o.Delimiter)
		if len(rr) != 1 {
			return Native{}, Failure(member, "delimiter", "Expected one delimiter")
		}
		c.Comma = rr[0]
	}
	rows := []Row{}
	header := []string{}
	width := -1
	row := 0
	for {
		cells, e := c.Read()
		if e == io.EOF {
			break
		}
		if e != nil {
			return Native{}, Failure(fmt.Sprintf("%s:%d", member, row+1), "csv_syntax", e.Error())
		}
		row++
		if width < 0 {
			width = len(cells)
			if o.Header {
				header = append(header, cells...)
				continue
			}
		}
		if len(cells) != width {
			return Native{}, Failure(fmt.Sprintf("%s:%d", member, row), "csv_width", "Native row width differs from the declared header/first row")
		}
		rows = append(rows, Row{"member": member, "row": row, "header": header, "cells": cells})
	}
	return Native{Tables: []Table{{"records", member, rows}}}, nil
}

// Native numbers retain their original lexeme; this is also used by lossless raw-record.
func RawValue(v any) any {
	switch x := v.(type) {
	case json.Number:
		return map[string]any{"number_lexeme": string(x)}
	case map[string]any:
		a := []any{}
		for _, k := range sortedKeys(x) {
			a = append(a, map[string]any{"key": k, "value": RawValue(x[k])})
		}
		return map[string]any{"entries": a}
	case Row:
		return RawValue(map[string]any(x))
	case []any:
		a := make([]any, len(x))
		for i, y := range x {
			a[i] = RawValue(y)
		}
		return a
	case []string:
		a := make([]any, len(x))
		for i, y := range x {
			a[i] = y
		}
		return a
	default:
		return x
	}
}
