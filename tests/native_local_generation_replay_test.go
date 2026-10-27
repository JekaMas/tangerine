package app

// Current mechanical projection/finalization, using retained actual replies.
// Identity is rebound for new test-owned preparations. No network model call;
// this is not represented as a fresh inference or new generation latency.
import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
)

func TestNativeLocalGenerationProjectionReplay(t *testing.T) {
	var plan map[string]any
	raw, e := os.ReadFile("/plan/PLAN.json")
	g23Require(t, e)
	g23Require(t, json.Unmarshal(raw, &plan))
	s, _ := g23Setup(t)
	defer g23Dump(t, s, "")
	observations, dispatches := []any{}, []any{}
	for _, value := range plan["cases"].([]any) {
		c := value.(map[string]any)
		caseID := c["id"].(string)
		id := "projection-replay-" + caseID
		sha := i34Profile(t, s, plan, false, "projection-replay")
		request := map[string]any{}
		for k, v := range plan["case_settings"].(map[string]any) {
			request[k] = v
		}
		request["topic"], request["mutation_count"] = c["topic"], c["mutation_count"]
		b, e := s.Store.WriteBlueprint(context.Background(), g23JSON(map[string]any{"exercise_request": request}), uuid.NewString())
		g23Require(t, e)
		g23Write(t, id+"-blueprint.json", b)
		raw, e = os.ReadFile("/recorded/qwen-repaired/qwen-repaired-plain-" + caseID + "-blueprint.json")
		g23Require(t, e)
		var old map[string]any
		g23Require(t, json.Unmarshal(raw, &old))
		oldID := old["id"].(string)
		raw, e = os.ReadFile("/recorded/qwen-repaired/dispatches.json")
		g23Require(t, e)
		var recorded []map[string]any
		g23Require(t, json.Unmarshal(raw, &recorded))
		bodies := map[string]string{}
		for _, d := range recorded {
			if d["http_status"] != float64(200) {
				continue
			}
			wire := d["request"].(map[string]any)
			for _, v := range wire["input"].([]any) {
				item := v.(map[string]any)
				text, _ := item["content"].(string)
				if !strings.HasPrefix(text, "Complete stage input: ") {
					continue
				}
				var input map[string]any
				g23Require(t, json.Unmarshal([]byte(strings.TrimPrefix(text, "Complete stage input: ")), &input))
				if input["blueprint"].(map[string]any)["id"] == oldID {
					bodies[input["phase"].(string)] = strings.ReplaceAll(string(g23JSON(d["response"])), oldID, b["id"].(string))
				}
			}
		}
		client := &http.Client{Transport: g23Trip(func(req *http.Request) (*http.Response, error) {
			raw, e := io.ReadAll(req.Body)
			if e != nil {
				return nil, e
			}
			var wire map[string]any
			g23Require(t, json.Unmarshal(raw, &wire))
			phase := ""
			for _, v := range wire["input"].([]any) {
				item := v.(map[string]any)
				text, _ := item["content"].(string)
				if strings.HasPrefix(text, "Complete stage input: ") {
					var input map[string]any
					g23Require(t, json.Unmarshal([]byte(strings.TrimPrefix(text, "Complete stage input: ")), &input))
					phase = input["phase"].(string)
				}
			}
			body := bodies[phase]
			if body == "" {
				t.Fatal("missing retained body", phase)
			}
			var response any
			g23Require(t, json.Unmarshal([]byte(body), &response))
			dispatches = append(dispatches, map[string]any{"url": req.URL.String(), "request": wire, "response": response, "http_status": 200, "authorization_present": false, "origin": "retained actual response replay; blueprint identity only rebound; no new inference"})
			g23Write(t, "dispatches.json", dispatches)
			return &http.Response{StatusCode: 200, Header: http.Header{}, Body: io.NopCloser(strings.NewReader(body))}, nil
		})}
		r := CanonicalPreparationRequest{BlueprintID: b["id"].(string), ConfigurationSHA: sha, Sources: []string{}, Attempt: 1}
		start := time.Now()
		p, e := s.PrepareCanonical(context.Background(), r, uuid.NewString(), client)
		g23Require(t, e)
		pid := p["id"].(string)
		r.PreparationID = &pid
		r.Attempt = 2
		p, e = s.PrepareMutation(context.Background(), r, uuid.NewString(), client)
		g23Require(t, e)
		i34Snapshot(t, s, id+"-", p)
		observations = append(observations, map[string]any{"id": id, "case": caseID, "alternative": "projection-replay", "admitted": true, "preparation_id": p["id"], "configuration_sha256": sha, "total_seconds": time.Since(start).Seconds(), "actual_inference": false, "origin": "current production projection and persistence; retained actual Qwen replies with identity rebound only"})
		g23Write(t, "observations.json", observations)
	}
	if len(dispatches) != 4 {
		t.Fatal("unexpected model-boundary replay/repair", len(dispatches))
	}
}
