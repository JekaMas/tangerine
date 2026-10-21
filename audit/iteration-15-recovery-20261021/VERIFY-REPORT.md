# Iteration 15 verification — passed

All eight iteration15 properties are implemented and verified within their defined boundaries. Full self-review found five defect groups, repaired them through their actual lifecycle/storage owners, and added nine registered regression tests. No I15 finding or product decision remains open. This report supersedes the earlier apply conclusion for the expanded review scope; original reports and receipts remain historical evidence.

## Findings and repairs

| Finding | Trigger and consequence | Repair and observed evidence |
|---|---|---|
| V1 Partial-stop recovery | Docker stop can fail after stopping some services. Backup/switch installed recovery only afterward, leaving the previous app partially stopped. | Install recovery before stop, use a fresh recovery context, restart only previously running services, report recovery failure accurately. Exact backup/switch partial-stop and failed-restart counterexamples plus existing success/rollback cases pass. |
| V2 Selected-workspace Lab | After switch, scripts/lab still loaded original database credentials. Missing restored credentials could also fall back to the original runtime. | scripts/workspace-env is the single selection owner for launcher and Lab, respecting explicit overrides and remembered selection. Both shell entrypoints and missing-runtime negatives pass; actual native Lab readback after real restore/switch passes with distinct restored database credentials. |
| V3 Expired foreground cleanup | Any operation left running by a crash blocked deletion indefinitely. | Use the established270s foreground owner lifetime while preserving actual evaluation/import/experiment leases. Native expired cleanup passes; actual live rendering, stale plans and shared references remain protected. |
| V4 Complete experiment erasure | Selecting an experiment omitted its recorded receipts and comparison bytes from the native plan. | Include recorded receipt roots, linked row operations/context/diagnostics and comparison artifacts through the existing storage closure. Native whole-experiment deletion removes receipts, call indexes and comparison bytes without inference. |
| V5 Retained experiment references | Selecting an individual receipt/comparison artifact could invalidate a retained experiment. | Block separately selected receipts and frozen/comparison/row-output/export assets still used by a retained experiment. The negative receipt/artifact cases reject apply with the expected revision error; whole-experiment erasure still succeeds. |

Decisive red receipts: data/iteration15/verify-partial-stop-red.jsonl; verify-launcher-admitted-red.stderr; verify-deletion-red.jsonl; verify-reference-red.jsonl. The first shell fixture used /var while the real shell returned /private/var; that fixture was corrected before retaining the decisive admission failure. Failed receipts remain failed.

## Complete scope and responsibility review

| Property | Reviewed owners and conclusion |
|---|---|
| I15-01 Preparation entry/resume | generation.go orchestrates existing canonical, mutation and speech owners; generation_http.go owns transport and generation_storage.go owns SQL readback. Frozen configuration and original action replay remain unchanged. |
| I15-02 Interruption | Saved immutable checkpoints, explicit Resume, cancellation propagation, live owner and exact replay/readback behavior inspected. No automatic inference, worker or paid fallback added. |
| I15-03 Backup | localctl owns writer/service lifecycle; app/snapshot.go owns native PostgreSQL/MinIO/model/Lab export; recovery owns archive encoding. Partial publication/collision and failed stop/restart paths covered. |
| I15-04 Restore | Single external archive admission, compatible migration prefix, fresh volumes/configuration, native pg_restore/private bytes and exact stored draft/audio readback covered. No repeated stored payload/schema/hash checks added. |
| I15-05 Workspace selection | Explicit ready-target switch, marker publication/rollback, original custom project, previous volume retention and selected Lab/runtime are covered. Shared shell selection has one responsibility. |
| I15-06 Erasure | Preview/apply confirmation, native transaction/FK ordering, live/expired writers, stale membership, shared assets, source release/file/report/experiment ownership, private diagnostic copies, retryable media and copied-Lab disposition reviewed. Storage remains separate from Docker and HTTP. |
| I15-07 Usability | Library/Prepare/Recovery/Cleanup navigation, private proxy routes, actionable failures, input retention, progress and explicit resume/retry inspected and observed through the actual browser where selected. |
| I15-08 Evidence | Exact graph selection, independent literal expectations, actual per-test results, substituted boundary limits, failed/successful receipts and preserved scope reconciled. The complete current scope has no failed/skipped/missing selected case. |

No new auth, public API surface, queue, workflow gate, consistency audit, provider switch or model/scoring owner was introduced. Native generation and speech stages, prompts, taxonomy, recipes and numeric equations remain unchanged.

## Acceptance and validation

- Current selection:83case edges across74registered physical tests and8properties;42positive and41negative.
- The first stable verification repair observed61/61affected edges on committed-clean63329a116c410b52574dd36d66e14f3f3e97dc7e, preserving21unchanged clean stage/archive/Lab edges.
- The final retained-experiment repair observed14/14native ownership edges on committed-cleandd64bcad207e5c6ec28332f8cf08e52b0670b022. Complete reconciliation retains69still-valid prior clean edges and these14fresh passes.
- VERIFY-ACCEPTANCE.json stores the exact per-case source receipt/revision, original/current fingerprints and retention reason. verify_reconcile.py checks complete membership, exact statuses, commands/assertions and the bounded semantic diff. It does not relabel failed executions or claim one fresh83-case run.
- Actual extracted-source/source-built API/Next/PostgreSQL/MinIO/Chrome run data/iteration15/workspace/run-b4827df41f passed27scenarios. This includes generation, browser failures/recovery/cleanup, restart, private backup, corrupt/existing/fresh restore, exact saved draft/audio, reversible switch, selected native Lab readback and confirmed/unconfirmed Lab purge. Its screenshot was visually inspected.
- Strict OpenSpec1.13.1, current DAG/discovery validation,423static contract checks and5161property/fixture assertions pass. These are structural results, not runtime/model observations.
- Final pinned Go1.26.5 vet/gofmt passes. The final storage repair invalidated the first stable language gate; both original receipts are preserved. No later production Go edit occurred.
- VERIFY-PRESERVATION.json retains the original122taxonomy/recipe identities,42grading formulas,11full-source identities,22Lab diagnostics, shipped prompts and migrations001–008. The unrelated canonical GAPS.md remains protected.

The final documentation/task commit changes no runtime owner, assertion, fixture, command, graph manifest or accepted contract; it does not invalidate the recorded behavior passes.

## Proof limits

This is self-review plus observed native evidence, not an independent external review. Constructed text/speech responses and PCM prove the labelled coordination/storage/maintenance/browser boundaries; they do not establish linguistic/acoustic quality or hosted entitlement. Existing actual stage/model evidence retains its original selected scope. The retained actual MLflow3.17 artifact records deterministic control, two constructed text dispatches/two receipts/two snapshots and one constructed speech dispatch/receipt; actual model inference is zero.

Unchanged cached speech runtime906700d3eda9 remains bound to the existing matched16source files; no fresh cold speech dependency build or architecture matrix is inferred. Earlier unfinished I8/I12 acceptance and whole-product release qualification remain separate. No paid API use, purchase, model download, host install, account action, external publication, merge or archive occurred.

Actual semantic search returned no Context index for this checkout. The prior exact-path JetBrains lookup reported project_not_found; this pass obtains no new IDE-index evidence and uses no unrelated index. Exact source/specification tracing is recorded in discovery.
