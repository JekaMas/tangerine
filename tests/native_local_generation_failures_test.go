package app

import (
	"context"
	"io"
	"net/http"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
)

// Deterministic remote-boundary packets exercise the real preparation owner.
// They do not claim a new MLX crash or consume 90/240 seconds deliberately.
func TestNativeLocalGenerationFailureModes(t *testing.T) {
	for _, mode := range []string{"runner", "deadline", "invalid-quote"} {
		t.Run(mode, func(t *testing.T) {
			s, r, good, goodCalls, clean := nativeMutationFixture(t, "")
			defer g23Dump(t, s, "failure-"+mode+"-")
			calls := 0
			ctx := context.Background()
			if mode == "deadline" {
				var cancel context.CancelFunc
				ctx, cancel = context.WithTimeout(ctx, 5*time.Second)
				defer cancel()
			}
			bad := &http.Client{Transport: g23Trip(func(req *http.Request) (*http.Response, error) {
				calls++
				if mode == "deadline" {
					<-req.Context().Done()
					return nil, req.Context().Err()
				}
				if mode == "runner" {
					return &http.Response{StatusCode: 500, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(`{"error":{"message":"mlx runner failed: Maximum threads per threadgroup is 896 but requested 1024"}}`))}, nil
				}
				// This exact absent canonical quote must not be relocated to the
				// changed surface. Both semantic attempts return the same defect.
				_, _, candidate, _ := mutationFixture()
				candidate["blueprint_id"] = r.BlueprintID
				candidate["planned_units"].([]any)[0].(map[string]any)["text_spans"].([]any)[0].(map[string]any)["span"].(map[string]any)["exact_text"] = "opens"
				body := `{"object":"response","status":"completed","model":"constructed-clean-text","output":[{"type":"message","content":[{"type":"output_text","text":` + string(g23JSON(string(g23JSON(candidate)))) + `}]}]}`
				return &http.Response{StatusCode: 200, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(body))}, nil
			})}
			p, e := s.PrepareMutation(ctx, r, uuid.NewString(), bad)
			if e == nil || p == nil || p["phase_states"].(map[string]any)["mutation"] != "failed" || p["canonical_asset_id"] != clean["canonical_asset_id"] || p["candidate_id"] != nil || p["mutation_manifest_asset_id"] != nil || p["key_id"] != nil {
				t.Fatal("failed output escaped containment", p, e)
			}
			want := 2
			if mode == "deadline" {
				want = 1
			}
			if calls != want {
				t.Fatal("unexpected retry", calls, want)
			}
			g23Write(t, "failure-"+mode+"-before.json", p)
			before, _ := s.Store.ReadAsset(context.Background(), clean["canonical_asset_id"].(string))
			r.Attempt = 3
			p, e = s.PrepareMutation(context.Background(), r, uuid.NewString(), good)
			if e != nil || *goodCalls != 1 || p["settings_asset_id"] != clean["settings_asset_id"] || p["last_failure"] != nil || p["phase_states"].(map[string]any)["mutation"] != "complete" {
				t.Fatal("explicit recovery failed", p, e, *goodCalls)
			}
			after, _ := s.Store.ReadAsset(context.Background(), clean["canonical_asset_id"].(string))
			if string(before) != string(after) {
				t.Fatal("recovery changed saved clean text")
			}
			g23Write(t, "failure-"+mode+"-after.json", map[string]any{"preparation": p, "failed_dispatches": calls, "recovery_dispatches": *goodCalls, "origin": "constructed runner/deadline/invalid-output packets; real storage, inference, admission and explicit recovery owners"})
		})
	}
}
