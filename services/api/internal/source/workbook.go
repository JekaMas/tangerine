package source

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"strconv"
	"strings"
)

type richText struct {
	Text string `xml:"t"`
	Runs []struct {
		Text string `xml:"t"`
	} `xml:"r"`
}

func rich(r richText) string {
	s := r.Text
	for _, v := range r.Runs {
		s += v.Text
	}
	return s
}
func workbook(member string, data []byte, selector string) (Native, error) {
	n := Native{Tables: []Table{}}
	indices := map[string]int{}
	e := walkWorkbook(context.Background(), member, bytes.NewReader(data), selector, func(table string, row Row) error {
		i, ok := indices[table]
		if !ok {
			i = len(n.Tables)
			indices[table] = i
			n.Tables = append(n.Tables, Table{table, member, []Row{}})
		}
		n.Tables[i].Rows = append(n.Tables[i].Rows, row)
		return nil
	})
	return n, e
}
func xmlLocal(v string) string {
	if i := strings.LastIndex(v, "}"); i >= 0 {
		return v[i+1:]
	}
	return v
}
func xmlAttribute(n Row, key string) string {
	for _, v := range n["attributes"].([]any) {
		a := v.(map[string]any)
		if xmlLocal(a["name"].(string)) == key {
			return a["value"].(string)
		}
	}
	return ""
}
func xmlChild(n Row, key string) Row {
	for _, v := range n["children"].([]any) {
		c := v.(Row)
		if xmlLocal(c["name"].(string)) == key {
			return c
		}
	}
	return nil
}
func xmlText(n Row) string {
	if n == nil {
		return ""
	}
	s := n["text"].(string)
	for _, v := range n["children"].([]any) {
		c := v.(Row)
		s += xmlText(c) + c["tail"].(string)
	}
	return s
}
func workbookRow(member, sheet, state string, tree Row, shared []string) (Row, error) {
	cells := []any{}
	for _, v := range tree["children"].([]any) {
		c := v.(Row)
		if xmlLocal(c["name"].(string)) != "c" {
			continue
		}
		kind := xmlAttribute(c, "t")
		cached := xmlText(xmlChild(c, "v"))
		var value any = cached
		var formula *string
		if f := xmlChild(c, "f"); f != nil {
			t := xmlText(f)
			formula = &t
		}
		switch kind {
		case "s":
			i, e := strconv.Atoi(cached)
			if e != nil || i < 0 || i >= len(shared) {
				return nil, Failure(member, "xlsx_shared_string", "Invalid index")
			}
			value = shared[i]
		case "inlineStr":
			value = xmlText(xmlChild(c, "is"))
		case "b":
			if cached != "0" && cached != "1" {
				return nil, Failure(member, "xlsx_boolean", "Invalid boolean")
			}
			value = cached == "1"
		case "", "n":
			if cached == "" {
				value = nil
			} else {
				if !json.Valid([]byte(cached)) {
					return nil, Failure(member, "xlsx_number", "Invalid native number")
				}
				value = jsonNumber(cached)
			}
		}
		cells = append(cells, map[string]any{"column": xmlAttribute(c, "r"), "type": kind, "style": xmlAttribute(c, "s"), "value": value, "formula": formula, "cached_value": cached})
	}
	if tree == nil {
		return nil, fmt.Errorf("missing native workbook row")
	}
	return Row{"member": member, "sheet": sheet, "sheet_state": state, "row": xmlAttribute(tree, "r"), "cells": cells, "native_xml_row": tree}, nil
}
