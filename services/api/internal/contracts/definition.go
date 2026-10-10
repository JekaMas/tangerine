package contracts

import (
	"bytes"
	"fmt"
	"github.com/santhosh-tekuri/jsonschema/v6"
)

func ValidateDefinition(kind, name string, raw []byte) error {
	registry, e := Registry()
	if e != nil {
		return e
	}
	c := jsonschema.NewCompiler()
	c.AssertFormat()
	for _, v := range registry {
		x, e := jsonschema.UnmarshalJSON(bytes.NewReader(v.Bytes))
		if e != nil {
			return e
		}
		if e = c.AddResource("https://tangerine.invalid/schemas/"+v.Kind+".schema.json", x); e != nil {
			return e
		}
	}
	schema, e := c.Compile(fmt.Sprintf("https://tangerine.invalid/schemas/%s.schema.json#/$defs/%s", kind, name))
	if e != nil {
		return e
	}
	canonical, e := Canonical(raw)
	if e != nil {
		return e
	}
	value, e := jsonschema.UnmarshalJSON(bytes.NewReader(canonical))
	if e != nil {
		return e
	}
	return schema.Validate(value)
}
