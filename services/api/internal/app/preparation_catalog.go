package app

import (
	"net/http"
	"sync"

	"go.yaml.in/yaml/v3"
)

// Category metadata is projected once from the same shipped registry generation
// uses. It contains no case keys, source records, credentials or inference.
type preparationCategory struct {
	ID          string `json:"id" yaml:"id"`
	Label       string `json:"label" yaml:"label"`
	Description string `json:"description" yaml:"definition"`
	Family      string `json:"family" yaml:"reporting_domain"`
	Control     bool   `json:"control"`
}

var categoryCatalogue struct {
	sync.Once
	Version string
	Items   []preparationCategory
	Err     error
}

func preparationCategories() ([]preparationCategory, string, error) {
	categoryCatalogue.Do(func() {
		raw, err := generationRegistry("error-taxonomy.v1.yaml")
		if err != nil {
			categoryCatalogue.Err = err
			return
		}
		var registry struct {
			Version string                `yaml:"version"`
			Items   []preparationCategory `yaml:"items"`
		}
		if err = yaml.Unmarshal(raw, &registry); err != nil {
			categoryCatalogue.Err = err
			return
		}
		for i := range registry.Items {
			registry.Items[i].Control = registry.Items[i].Family == "acceptable_variant"
		}
		categoryCatalogue.Items, categoryCatalogue.Version = registry.Items, registry.Version
	})
	return categoryCatalogue.Items, categoryCatalogue.Version, categoryCatalogue.Err
}

func (s *Server) preparationOptions(w http.ResponseWriter, r *http.Request) {
	categories, version, err := preparationCategories()
	if err != nil {
		preparationHTTPError(w, 503, "CATALOGUE_UNAVAILABLE")
		return
	}
	writeJSON(w, 200, map[string]any{"taxonomy_version": version, "categories": categories})
}
