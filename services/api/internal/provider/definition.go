package provider

import "embed"

// Adapter definitions are private immutable preparation evidence, never model
// instructions. A saved definition is not permission to execute an old adapter.
//
//go:embed transport.go execute.go projection.go
var adapterSources embed.FS

func AdapterDefinitions() map[string]string {
	result := map[string]string{}
	for _, name := range []string{"transport.go", "execute.go", "projection.go"} {
		b, _ := adapterSources.ReadFile(name)
		result[name] = string(b)
	}
	return result
}
