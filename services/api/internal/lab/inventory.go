package lab

import (
	"encoding/json"
	"errors"
	"tangerine.local/api/internal/contracts"
)

// ValidateInventory challenges declarations against independently supplied source
// bytes. Planned surfaces remain unexercised; they cannot satisfy required calls.
func ValidateInventory(raw []byte, actual map[string]string) error {
	if _, _, e := contracts.Validate("ai-surface-inventory", "2.0.0", raw); e != nil {
		return e
	}
	var x struct {
		Dependencies []struct {
			Path string `json:"path"`
			SHA  string `json:"sha256"`
		} `json:"dependencies"`
		Unresolved []string `json:"unresolved_paths"`
		Entries    []struct {
			ID        string   `json:"id"`
			State     string   `json:"implementation_state"`
			Owners    []string `json:"owner_paths"`
			Symbols   []string `json:"owner_symbols"`
			Fragments []struct {
				Path  string  `json:"path_or_asset"`
				SHA   *string `json:"sha256"`
				State string  `json:"state"`
			} `json:"trusted_fragments"`
		} `json:"entries"`
	}
	if e := json.Unmarshal(raw, &x); e != nil {
		return e
	}
	if len(x.Unresolved) > 0 {
		return errors.New("unresolved inference inventory")
	}
	seen := map[string]bool{}
	for _, d := range x.Dependencies {
		if actual[d.Path] != d.SHA {
			return errors.New("inventory dependency mismatch")
		}
	}
	for _, v := range x.Entries {
		if seen[v.ID] || v.ID == "" {
			return errors.New("duplicate surface")
		}
		seen[v.ID] = true
		if v.State == "implemented" && (len(v.Owners) == 0 || len(v.Symbols) == 0) {
			return errors.New("implemented owner unresolved")
		}
		for _, f := range v.Fragments {
			if f.State == "observed" && (f.SHA == nil || actual[f.Path] != *f.SHA) {
				return errors.New("unresolved trusted fragment")
			}
		}
	}
	return nil
}
func ValidateDataset(raw []byte) error {
	if _, _, e := contracts.Validate("llm-quality-dataset", "2.0.0", raw); e != nil {
		return e
	}
	var d struct {
		Scope string  `json:"scope"`
		Stage *string `json:"stage"`
		Phase *string `json:"phase"`
		Cases []struct {
			ID    string  `json:"id"`
			Stage string  `json:"stage"`
			Phase *string `json:"phase"`
		} `json:"cases"`
	}
	if e := json.Unmarshal(raw, &d); e != nil {
		return e
	}
	seen := map[string]bool{}
	if len(d.Cases) == 0 {
		return errors.New("empty frozen dataset")
	}
	for _, c := range d.Cases {
		if c.ID == "" || seen[c.ID] {
			return errors.New("duplicate quality case")
		}
		seen[c.ID] = true
		if d.Scope == "stage" && (d.Stage == nil || Pair(c.Stage, c.Phase) != Pair(*d.Stage, d.Phase)) {
			return errors.New("quality dataset stage mismatch")
		}
	}
	return nil
}
