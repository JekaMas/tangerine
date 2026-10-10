# Local checks

From the repository root:

- Native OpenSpec: `OPENSPEC_TELEMETRY=0 DO_NOT_TRACK=1 OPENSPEC_NO_UPDATE_CHECK=1 openspec validate implement-teacher-error-trainer --strict`.
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
