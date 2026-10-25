# Local checks

From the repository root:

- Native OpenSpec: `OPENSPEC_TELEMETRY=0 DO_NOT_TRACK=1 OPENSPEC_NO_UPDATE_CHECK=1 node "$TANGERINE_OPENSPEC_CLI" validate implement-teacher-error-trainer --strict`.
- Graph: `python3 -B .agents/workflow/scripts/evidence_graph_check.py --root . --change implement-teacher-error-trainer validate`.
- Affected graph: use the shared requirement_tests.py query/run with exact selectors and a unique output.
- Go behavior: `cd services/api && GOWORK=off go test -json -count=1 ./...`.
- Go static analysis: `cd services/api && GOWORK=off go vet ./...`; check gofmt after the stable batch.
- Python: `python3 -B -m unittest discover -s tests -v`.
- Web: `cd services/web && npm ci && npm run build`.
- Compose: validate with `docker compose --env-file .env --env-file data/config/runtime.env -f deploy/local/compose.yaml config --quiet`, then actual build/readiness only with a running daemon.
- Workflow setup: bootstrap status, skill_packages validate, workflow_publication, check_opsx_routes, then shared make check, exactly as .agents/workflow/docs/project-flow.md states.

Retain exit codes and bounded receipts under the selected change/evidence. Do not use imported-validation-results.json as a receipt for current code. The repository is not release ready until all required tasks and cases pass with real dependencies and observed content.


For iteration1, the native acceptance selection is I1-01.P1 through I1-08.P1.
Run its `python-unittest` graph command alone; concurrent instances compete for
loopback port3000 and are invalid evidence. The suite owns fresh test volumes;
only its cleanup removes those volumes. The application launcher never does.
Legacy account/session suites are historical and are not current no-login
acceptance. Broader original feature plans remain pending their full owners.

The application builds from a ZIP using Docker only. When the host Go differs
from the pinned version, use the Dockerfile's `build` target for `go test -race
-json ./...` and `go vet ./...`, retaining the actual Go image/command receipts.
The production web Docker build already executes locked `npm ci` and
`npm run build`; it is the same language/build check without host Node setup.
No host prerequisite installation follows from this adapter.

Iteration2 completion selects I2-01.P1 through I2-14.P1 and the invalidated I1
foundation closure. Run native commands sequentially: both own loopback3000.
The56 new cases are real storage/browser fixtures; they do not establish later
LLM/generation/scoring/import semantic acceptance. Compile/vet/race use pinned
Go1.26.5 Docker; host Go remains an acceptance-tool mismatch, not a prerequisite.

The iterations1/2 repair closure selects all I1-01.P1 through I1-08.P1 and I2-01.P1 through I2-18.P1:104 exact cases. The native regression adapter owns disposable PostgreSQL/MinIO containers without published ports and observes16 actual Go race cases. The historical88-case receipts do not prove the expanded repair closure. Original taxonomy/recipes/formulas/source scopes remain required.

This host's native acceptance commands explicitly bind Docker Desktop docker.raw.sock after its normal API proxy became unavailable. Both endpoints identify the same actual engine. This is a local evidence-tool transport binding, preserving real containers/browser and the product launcher. Other qualification hosts must select their actually available native Docker endpoint.

Native browser cases use installed Chrome through Playwright. The test transport defaults to the existing Codex bundled Node/Playwright; explicit TANGERINE_TEST_NODE and TANGERINE_TEST_PLAYWRIGHT_MODULE paths may select an existing installation. The tests never download/install dependencies. Node24.19.0, Playwright1.62.1 and Chrome154 were observed during iteration4 verification. These are development test tools; ordinary Tangerine startup does not require them.

## Continuation iterations 17–30

Read `completion-iterations.json` in the canonical change for the selected
iteration’s `verify_property_ids`, dependency edges and source findings. For
example, preparation iteration 18 selects:

```sh
python3 -B .agents/workflow/scripts/requirement_tests.py --root . \
  --change implement-teacher-error-trainer query \
  --properties FIN-UI-01.P1,FIN-UI-06.P1,FIN-UI-07.P1,FIN-VERIFY.I18
```

Use the JSON result to reconcile the complete exact selected case identities;
include dependent cases whose actual inputs changed. The registered
`completion-i<n>` commands target future `tests.test_completion_i<n>` modules.
They are **planned**, not currently executable acceptance evidence. During
apply, materialize those literal tests through the actual application/test
owners, select permitted dependencies, register their real source bindings and
run directly affected cases. Do not create tests that merely assert a report
says “pass”, or run a placeholder command to manufacture a green result.

Every verify loads `UI_UX_TYPOGRAPHY_VERIFICATION.md` via the project review
adapter. Inspect actual interaction, loaded typography and evidence content;
record each dimension, including concrete not-applicable reasons. Structural
graph/discovery validation checks this plan’s wiring only. It cannot execute a
future UI repair, qualify a provider, acquire a restricted source or prove an
audio mutation. Reuse original valid greens and record new observations only
for actual invalidations or newly required cases. No automatic installation,
provider call or paid use is authorized by command registration.

The current budget scope excludes LLM performance/bulk model campaigns from
mandatory apply/verify selection. Use retained evidence and deterministic report
fixtures; do not dispatch calls for latency percentiles, throughput, model sweeps
or judge statistics. Iteration 28 verifies saved-data reports with zero new
inference. Direct functional provider/flow checks still need their actual
permitted resources and must remain within included/free/local limits.

The final continuation trace is `completion-coverage.md` in the canonical
change; concrete API/replay/form/adapter behavior is in
`specification/v2/docs/completion-contract-details.md`. Iteration 19 applies its
additive canonical history schemas to the embedded runtime copies and native UI
projections during implementation. Iteration 26 also selects CV-01–CV-06 from
the existing native/evidence registry; retain valid observations instead of
rerunning model calls or duplicating those owners.

The future `completion-i<n>` modules are planned routing targets. During apply,
reuse an existing FX/CV/native test identity if it already proves the exact
literal case; record the actual command/source and shared-test scope rather
than introducing a duplicate assertion module. A renamed case alone invalidates
no behavioral receipt.

Iteration 17 binds the existing 1.13.1 CLI explicitly as documented in
`OPENSPEC_WORKFLOW.md`; global 1.14.3 is not the selected contract. The six implemented
`completion-i17` tests reconcile maintained status and real retained evidence only;
no product Go/Python speech/web owner changed, so their unaffected language/build/
behavior greens are retained. UI/UX and product typography are not applicable
with the concrete scope reasons in the I17 review. Later FIN case placeholders
remain planned; the existing FX/CV observations are candidate reuse bindings,
not automatic acceptance of those iterations.
