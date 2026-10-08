# Local checks

From the repository root:

- Native OpenSpec: `OPENSPEC_TELEMETRY=0 DO_NOT_TRACK=1 OPENSPEC_NO_UPDATE_CHECK=1 openspec validate implement-teacher-error-trainer --strict`.
- Graph: `python3 -B .agents/workflow/scripts/evidence_graph_check.py --root . --change implement-teacher-error-trainer validate`.
- Affected graph: use the shared requirement_tests.py query/run with exact selectors and a unique output.
- Go behavior: `cd services/api && GOWORK=off go test -json -count=1 ./...`.
- Go static analysis: `cd services/api && GOWORK=off go vet ./...`; check gofmt after the stable batch.
- Python: `python3 -B -m unittest discover -s tests -v`.
- Web: `cd services/web && npm ci && npm run build`.
- Compose: validate with `docker compose --env-file deploy/local/.env -f deploy/local/compose.yaml config --quiet`, then actual build/readiness only with a running daemon.
- Workflow setup: bootstrap status, skill_packages validate, workflow_publication, check_opsx_routes, then shared make check, exactly as .agents/workflow/docs/project-flow.md states.

Retain exit codes and bounded receipts under the selected change/evidence. Do not use imported-validation-results.json as a receipt for current code. The repository is not release ready until all required tasks and cases pass with real dependencies and observed content.
