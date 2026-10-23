package app

// Explicit development observations only. The ordinary test command has no
// inference authority; these run only in the admitted preview with a named root.
import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/google/uuid"
	"tangerine.local/api/internal/lab"
)

func observeUXExercise(t *testing.T, count int, label string) {
	root := os.Getenv("TANGERINE_UX_OBSERVATION")
	if root == "" {
		t.Skip("explicit included/local development observation only")
	}
	dir := filepath.Join(root, label)
	if e := os.MkdirAll(dir, 0700); e != nil {
		t.Fatal(e)
	}
	save := func(name string, v any) {
		raw, _ := json.MarshalIndent(v, "", "  ")
		if e := os.WriteFile(filepath.Join(dir, name), append(raw, '\n'), 0600); e != nil {
			t.Fatal(e)
		}
	}
	read := func(name string) map[string]any {
		raw, e := os.ReadFile(filepath.Join(dir, name))
		if os.IsNotExist(e) {
			return nil
		}
		if e != nil {
			t.Fatal(e)
		}
		var v map[string]any
		if e = json.Unmarshal(raw, &v); e != nil {
			t.Fatal(e)
		}
		return v
	}
	ctx := context.Background()
	store, e := OpenStorage(ctx, os.Getenv("DATABASE_URL"), os.Getenv("MINIO_ENDPOINT"), os.Getenv("MINIO_ACCESS_KEY"), os.Getenv("MINIO_SECRET_KEY"), os.Getenv("MINIO_BUCKET"))
	if e != nil {
		t.Fatal(e)
	}
	defer store.DB.Close()
	config, _, e := store.Configuration(ctx)
	if e != nil {
		t.Fatal(e)
	}
	profile, e := FreezeProfile(config, "case_generation")
	if e != nil || profile.Provider != "openai_chatgpt" || profile.Billing != "included_subscription" {
		t.Fatal("existing included profile required; no fallback", e)
	}
	config["llm_lab_capture_content"], config["llm_lab_trace_enabled"] = true, true
	delete(config, "configuration_sha256")
	config["configuration_sha256"] = lab.Hash(config)
	ctx = qualityContext(ctx, qualityBinding{Configuration: config, Bundle: lab.Shipped()})
	server := NewServer(store, os.Getenv("APP_ORIGIN"), os.Getenv("SPEECH_URL"))
	b := read("blueprint.json")
	if b == nil {
		raw, _ := json.Marshal(map[string]any{"exercise_request": map[string]any{"topic": "Tangerine practice: two friends planning a short train journey and discussing a small booking mistake. Include the correct phrase I made a mistake naturally in the clean dialogue.", "speaker_count": 2, "text_length_words": 45, "english_level": "B1", "category_families": []any{}, "category_ids": []any{"lexis.collocation"}, "severity_levels": []any{"minor"}, "mutation_count": count}})
		b, e = store.WriteBlueprint(ctx, raw, uuid.NewString())
		if e != nil {
			t.Fatal(e)
		}
		save("blueprint.json", b)
	}
	r := CanonicalPreparationRequest{BlueprintID: b["id"].(string), ConfigurationSHA: config["configuration_sha256"].(string), Sources: []string{}, Attempt: 1}
	prep := read("canonical.json")
	if prep == nil {
		prep, e = server.PrepareCanonical(ctx, r, uuid.NewString(), nil)
		save("canonical-observation.json", map[string]any{"preparation": prep, "error": fmt.Sprint(e)})
		if e != nil {
			t.Fatal("actual clean-text stage", e)
		}
		save("canonical.json", prep)
	}
	id := prep["id"].(string)
	r.PreparationID = &id
	r.Attempt = 2
	mut := read("mutation.json")
	if mut == nil {
		mut, e = server.PrepareMutation(ctx, r, uuid.NewString(), nil)
		save("mutation-observation.json", map[string]any{"preparation": mut, "error": fmt.Sprint(e)})
		if e != nil {
			t.Fatal("actual mutation stage", e)
		}
		save("mutation.json", mut)
	}
	rendered := read("render.json")
	if rendered == nil {
		rendered, e = server.RenderPreparation(ctx, id, uuid.NewString(), 1, nil)
		save("render-observation.json", map[string]any{"preparation": rendered, "error": fmt.Sprint(e)})
		if e != nil {
			t.Fatal("actual local audio", e)
		}
		save("render.json", rendered)
	}
	for _, field := range []string{"canonical_asset_id", "mutated_asset_id", "mutation_manifest_asset_id", "audio_asset_id"} {
		asset, e := store.ReadAsset(ctx, rendered[field].(string))
		if e != nil {
			t.Fatal(e)
		}
		name := field + ".json"
		if field == "audio_asset_id" {
			name = "actual.wav"
		}
		if e = os.WriteFile(filepath.Join(dir, name), asset, 0600); e != nil {
			t.Fatal(e)
		}
	}
	doc, e := store.ReadDocument(ctx, rendered["key_id"].(string))
	if e != nil {
		t.Fatal(e)
	}
	var key map[string]any
	if e = json.Unmarshal(doc.Payload, &key); e != nil {
		t.Fatal(e)
	}
	save("ground-truth.json", key)
	units := key["units"].([]any)
	if len(units) != count {
		t.Fatal("wrong independently requested count", len(units), count)
	}
	if count > 0 {
		u := units[0].(map[string]any)
		if u["primary_taxonomy_id"] != "lexis.collocation" || u["severity"] != "minor" || u["weight"] != float64(1) {
			t.Fatal("selected category/severity lost", u)
		}
	}
	var published string
	if e = store.DB.QueryRow(ctx, "SELECT case_version_id FROM listening_case WHERE source_key_id=$1", rendered["key_id"]).Scan(&published); e != nil {
		t.Fatal(e)
	}
	save("binding.json", map[string]any{"blueprint_id": b["id"], "preparation_id": id, "case_id": published, "expected_count": count, "severity": "minor", "category": "lexis.collocation", "configuration": config, "bundle": lab.Shipped()})
}

func TestUXObserveMinorPositive(t *testing.T) { observeUXExercise(t, 1, "minor") }
func TestUXObserveZeroNegative(t *testing.T)  { observeUXExercise(t, 0, "zero") }
