package source

import (
	"encoding/xml"
	"fmt"
	"io"
	"strings"
)

func expanded(n xml.Name) string {
	if n.Space != "" {
		return "{" + n.Space + "}" + n.Local
	}
	return n.Local
}
func parseXML(member, text, selector string) (Native, error) {
	d := xml.NewDecoder(strings.NewReader(text))
	stack := []Row{}
	all := []Row{}
	paths := []string{}
	for {
		tok, e := d.Token()
		if e == io.EOF {
			break
		}
		if e != nil {
			return Native{}, Failure(member, "xml_syntax", e.Error())
		}
		switch t := tok.(type) {
		case xml.Directive:
			return Native{}, Failure(member, "xml_directive", "DTD/entity directives are disabled; retained original is inert")
		case xml.StartElement:
			name := expanded(t.Name)
			p := "/" + name
			if len(paths) > 0 {
				p = paths[len(paths)-1] + p
			}
			attrs := []any{}
			for _, a := range t.Attr {
				attrs = append(attrs, map[string]any{"name": expanded(a.Name), "value": a.Value})
			}
			n := Row{"member": member, "path": p, "name": name, "attributes": attrs, "text": "", "tail": "", "children": []any{}}
			if len(stack) > 0 {
				parent := stack[len(stack)-1]
				parent["children"] = append(parent["children"].([]any), n)
			}
			stack = append(stack, n)
			paths = append(paths, p)
			all = append(all, n)
		case xml.CharData:
			if len(stack) > 0 {
				n := stack[len(stack)-1]
				ch := n["children"].([]any)
				if len(ch) == 0 {
					n["text"] = n["text"].(string) + string(t)
				} else {
					last := ch[len(ch)-1].(Row)
					last["tail"] = last["tail"].(string) + string(t)
				}
			}
		case xml.EndElement:
			if len(stack) == 0 {
				return Native{}, fmt.Errorf("unbalanced XML")
			}
			stack = stack[:len(stack)-1]
			paths = paths[:len(paths)-1]
		}
	}
	selected := []Row{}
	for _, n := range all {
		if selector == "" || selector == "records" || selector == n["path"] {
			selected = append(selected, n)
		}
	}
	return Native{Tables: []Table{{selector, member, selected}}}, nil
}
