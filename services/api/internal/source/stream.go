package source

import (
	"archive/zip"
	"bufio"
	"context"
	"encoding/csv"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"os"
	"strings"
)

type Emit func(table string, row Row) error

// Walk bounds memory by a native record. Archive/XLSX random access uses a
// private disk spool; source paths are never extracted or executed.
func Walk(ctx context.Context, member string, r io.Reader, o Options, emit Emit) error {
	if o.Format == "xlsx" {
		return walkWorkbook(ctx, member, r, o.Selector, emit)
	}
	reader, e := textReader(r, o.Encoding)
	if e != nil {
		return Failure(member, "encoding", e.Error())
	}
	r = reader
	br := bufio.NewReader(r)
	if b, err := br.Peek(3); err != nil && err != io.EOF {
		return Failure(member, "encoding", err.Error())
	} else if string(b) == "\xef\xbb\xbf" {
		_, _ = br.Discard(3)
	}
	send := func(table string, row Row) error {
		if e := ctx.Err(); e != nil {
			return e
		}
		return emit(table, row)
	}
	switch o.Format {
	case "json", "jsonl":
		d := json.NewDecoder(br)
		d.UseNumber()
		ordinal := 0
		value := func(v, tree any, duplicate bool, key *string) error {
			row := Row{"member": member, "row": ordinal, "value": v, "source_json_tree": tree}
			if duplicate {
				row["ambiguous_keys"] = true
			}
			if key != nil {
				row["key"] = *key
			}
			ordinal++
			return send("records", row)
		}
		if o.Format == "jsonl" {
			for {
				v, tree, duplicate, e := orderedJSON(d)
				if e == io.EOF {
					return nil
				}
				if e != nil {
					return Failure(member, "json_syntax", e.Error())
				}
				if e = value(v, tree, duplicate, nil); e != nil {
					return e
				}
			}
		}
		for {
			b, err := br.ReadByte()
			if err != nil {
				break
			}
			if b != ' ' && b != '\n' && b != '\r' && b != '\t' {
				_ = br.UnreadByte()
				break
			}
		}
		b, _ := br.Peek(1)
		if len(b) == 0 {
			return Failure(member, "json_syntax", "Empty JSON document")
		}
		if b[0] == '[' || o.Selector == "keyed_records" {
			token, e := d.Token()
			if e != nil {
				return e
			}
			object := token == json.Delim('{')
			if o.Selector == "keyed_records" && !object {
				return Failure(member, "json_shape", "Expected a keyed object")
			}
			seen := map[string]bool{}
			for d.More() {
				var key *string
				if object {
					t, e := d.Token()
					if e != nil {
						return e
					}
					s := t.(string)
					if seen[s] {
						return Failure(member, "duplicate_key", "Conflicting native keyed JSON identity; full original retained")
					}
					seen[s] = true
					key = &s
				}
				v, tree, duplicate, e := orderedJSON(d)
				if e != nil {
					return Failure(member, "json_syntax", e.Error())
				}
				if e = value(v, tree, duplicate, key); e != nil {
					return e
				}
			}
			if _, e = d.Token(); e != nil {
				return e
			}
		} else {
			v, tree, duplicate, e := orderedJSON(d)
			if e != nil {
				return e
			}
			if e = value(v, tree, duplicate, nil); e != nil {
				return e
			}
		}
		if !jsonEOF(d) {
			return Failure(member, "json_syntax", "Trailing JSON content")
		}
		return nil

	case "csv", "tsv":
		c := csv.NewReader(br)
		c.FieldsPerRecord = -1
		if o.Format == "tsv" {
			c.Comma = '\t'
		}
		if o.Delimiter != nil {
			a := []rune(*o.Delimiter)
			if len(a) != 1 {
				return Failure(member, "delimiter", "Expected one delimiter")
			}
			c.Comma = a[0]
		}
		header := []string{}
		width := -1
		row := 0
		for {
			cells, e := c.Read()
			if e == io.EOF {
				return nil
			}
			if e != nil {
				return Failure(member, "csv_syntax", e.Error())
			}
			row++
			if width < 0 {
				width = len(cells)
				if o.Header {
					header = append(header, cells...)
					continue
				}
			}
			v := Row{"member": member, "row": row, "header": header, "cells": cells}
			if len(cells) != width {
				v["invalid"] = true
				v["issue"] = "csv_width"
			}
			if e = send("records", v); e != nil {
				return e
			}
		}
	case "m2":
		var block strings.Builder
		index := 0
		lineReader := bufio.NewReader(br)
		flush := func() error {
			if block.Len() == 0 {
				return nil
			}
			n, e := parseM2(member, block.String())
			block.Reset()
			if e != nil {
				return e
			}
			for _, t := range n.Tables {
				for _, row := range t.Rows {
					row["sentence_index"] = index
					if e = send(t.Name, row); e != nil {
						return e
					}
				}
			}
			index++
			return nil
		}
		for {
			line, e := lineReader.ReadString('\n')
			if strings.TrimSpace(line) == "" {
				if e := flush(); e != nil {
					return e
				}
			} else {
				block.WriteString(line)
			}
			if e == io.EOF {
				return flush()
			}
			if e != nil {
				return e
			}
		}
	case "kaldi":
		index := 0
		for {
			line, e := br.ReadString('\n')
			if strings.TrimSpace(line) != "" {
				n, pe := parseKaldi(member, line)
				if pe != nil {
					return pe
				}
				for _, t := range n.Tables {
					for _, row := range t.Rows {
						row["row"] = index
						if e = send(t.Name, row); e != nil {
							return e
						}
						index++
					}
				}
			}
			if e == io.EOF {
				return nil
			}
			if e != nil {
				return e
			}
		}
	case "xml":
		return walkXML(member, br, o.Selector, send)
	case "xlsx":
		return walkWorkbook(ctx, member, br, o.Selector, send)
	case "lines":
		index := 0
		for {
			line, e := br.ReadString('\n')
			if len(line) > 0 {
				v := Row{"member": member, "row": index, "text": strings.TrimSuffix(strings.TrimSuffix(line, "\n"), "\r"), "line_ending": strings.TrimPrefix(line, strings.TrimRight(line, "\r\n"))}
				if e = send("sentences", v); e != nil {
					return e
				}
				index++
			}
			if e == io.EOF {
				return nil
			}
			if e != nil {
				return e
			}
		}
	default:
		b, e := io.ReadAll(br)
		if e != nil {
			return e
		}
		n, e := Parse(member, b, o)
		if e != nil {
			return e
		}
		for _, t := range n.Tables {
			for _, row := range t.Rows {
				if e = send(t.Name, row); e != nil {
					return e
				}
			}
		}
		return nil
	}
}
func walkXML(member string, r io.Reader, selector string, emit Emit) error {
	d := xml.NewDecoder(r)
	stack := []string{}
	index := 0
	for {
		tok, e := d.Token()
		if e == io.EOF {
			return nil
		}
		if e != nil {
			return Failure(member, "xml_syntax", e.Error())
		}
		switch t := tok.(type) {
		case xml.Directive:
			return Failure(member, "xml_directive", "DTD/entity directives disabled")
		case xml.StartElement:
			stack = append(stack, expanded(t.Name))
			p := "/" + strings.Join(stack, "/")
			if selector != "" && selector != "records" && p != selector {
				continue
			}
			// Stream one selected subtree, retaining mixed text/tails and every field.
			row, e := xmlNode(d, t, member, p)
			if e != nil {
				return e
			}
			row["row"] = index
			index++
			if e = emit(selector, row); e != nil {
				return e
			}
			stack = stack[:len(stack)-1]
		case xml.EndElement:
			if len(stack) > 0 {
				stack = stack[:len(stack)-1]
			}
		}
	}
}
func xmlNode(d *xml.Decoder, start xml.StartElement, member, p string) (Row, error) {
	attrs := []any{}
	for _, a := range start.Attr {
		attrs = append(attrs, map[string]any{"name": expanded(a.Name), "value": a.Value})
	}
	row := Row{"member": member, "path": p, "name": expanded(start.Name), "attributes": attrs, "text": "", "tail": "", "children": []any{}}
	for {
		tok, e := d.Token()
		if e != nil {
			return nil, e
		}
		switch t := tok.(type) {
		case xml.Directive:
			return nil, Failure(member, "xml_directive", "DTD disabled")
		case xml.StartElement:
			child, e := xmlNode(d, t, member, p+"/"+expanded(t.Name))
			if e != nil {
				return nil, e
			}
			row["children"] = append(row["children"].([]any), child)
		case xml.CharData:
			c := row["children"].([]any)
			if len(c) == 0 {
				row["text"] = row["text"].(string) + string(t)
			} else {
				last := c[len(c)-1].(Row)
				last["tail"] = last["tail"].(string) + string(t)
			}
		case xml.EndElement:
			return row, nil
		}
	}
}
func walkWorkbook(ctx context.Context, member string, r io.Reader, selector string, emit Emit) error {
	// ZIP needs random access. The spool is bounded by the already admitted file
	// length/operator capacity, then removed; no workbook members reach the OS.
	f, e := os.CreateTemp("", "tangerine-xlsx-")
	if e != nil {
		return e
	}
	defer os.Remove(f.Name())
	defer f.Close()
	if _, e = io.Copy(f, r); e != nil {
		return e
	}
	z, e := zip.OpenReader(f.Name())
	if e != nil {
		return e
	}
	defer z.Close()
	// Native workbook metadata and shared strings are small relative to sheets.
	// Reuse the strict metadata parser on an envelope containing only metadata,
	// while sheet XML itself is consumed a single native row at a time.
	files := map[string]*zip.File{}
	for _, v := range z.File {
		if v.FileInfo().IsDir() {
			continue
		}
		n, e := SafePath(v.Name)
		if e != nil || files[n] != nil || !v.Mode().IsRegular() {
			return Failure(member, "xlsx_member", "Unsafe or duplicate member")
		}
		files[n] = v
	}
	read := func(n string, out any) error {
		f := files[n]
		if f == nil {
			return fmt.Errorf("missing workbook member %s", n)
		}
		r, e := f.Open()
		if e != nil {
			return e
		}
		defer r.Close()
		return xml.NewTokenDecoder(inertXMLTokens{xml.NewDecoder(r), member}).Decode(out)
	}
	var book struct {
		Sheets []struct {
			Name  string `xml:"name,attr"`
			ID    string `xml:"id,attr"`
			State string `xml:"state,attr"`
		} `xml:"sheets>sheet"`
	}
	if e = read("xl/workbook.xml", &book); e != nil {
		return e
	}
	var rel struct {
		Items []struct {
			ID     string `xml:"Id,attr"`
			Target string `xml:"Target,attr"`
			Mode   string `xml:"TargetMode,attr"`
		} `xml:"Relationship"`
	}
	if e = read("xl/_rels/workbook.xml.rels", &rel); e != nil {
		return e
	}
	targets := map[string]string{}
	for _, v := range rel.Items {
		if v.Mode == "External" {
			return Failure(member, "external_relationship", "External workbook relationships disabled")
		}
		t := "xl/" + v.Target
		if strings.HasPrefix(v.Target, "/") {
			t = strings.TrimPrefix(v.Target, "/")
		}
		n, e := SafePath(t)
		if e != nil {
			return e
		}
		targets[v.ID] = n
	}
	shared := []string{}
	if files["xl/sharedStrings.xml"] != nil {
		var s struct {
			Items []richText `xml:"si"`
		}
		if e = read("xl/sharedStrings.xml", &s); e != nil {
			return e
		}
		for _, v := range s.Items {
			shared = append(shared, rich(v))
		}
	}
	for _, s := range book.Sheets {
		if selector != "" && selector != "records" && selector != s.Name {
			continue
		}
		file := files[targets[s.ID]]
		if file == nil {
			return fmt.Errorf("missing worksheet")
		}
		r, e := file.Open()
		if e != nil {
			return e
		}
		e = func() error {
			defer r.Close()
			d := xml.NewDecoder(r)
			for {
				if e := ctx.Err(); e != nil {
					return e
				}
				tok, e := d.Token()
				if e == io.EOF {
					return nil
				}
				if e != nil {
					return e
				}
				if _, ok := tok.(xml.Directive); ok {
					return Failure(member, "xml_directive", "Workbook DTD disabled")
				}
				start, ok := tok.(xml.StartElement)
				if !ok || start.Name.Local != "row" {
					continue
				}
				tree, e := xmlNode(d, start, member, "/worksheet/sheetData/row")
				if e != nil {
					return e
				}
				row, e := workbookRow(member, s.Name, s.State, tree, shared)
				if e != nil {
					return e
				}
				if e = emit(s.Name, row); e != nil {
					return e
				}
			}
		}()
		if e != nil {
			return e
		}
	}
	return nil
}

// Workbook metadata is decoded without resolving or ignoring native DTDs.
type inertXMLTokens struct {
	decoder *xml.Decoder
	member  string
}

func (d inertXMLTokens) Token() (xml.Token, error) {
	t, e := d.decoder.Token()
	if _, ok := t.(xml.Directive); ok {
		return nil, Failure(d.member, "xml_directive", "Workbook directives remain inert raw bytes")
	}
	return t, e
}
