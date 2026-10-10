# Iteration 3 verification and repair

Iteration 3 verification passes on committed-clean candidate **944e0a39a39eb4ae37d19c875a4314bb4ecd5b98**. All seven findings are repaired and verified closed. Exact reconciliation covers **88/88 iteration 3 cases**:44 positive and44 negative cases across22 properties, each with two distinct literal fixtures per polarity. The affected foundation closure also passes **32/32 cases**:16 positive and16 negative. There are no remaining in-scope findings or product decisions.

This report supersedes the earlier implementation acceptance on a523a13. The review and repairs were performed by the implementing agent; this is self-review, not a claim of independent reviewer approval.

## Findings and verified repairs

| Finding | Original problem | Repair and observed result |
| --- | --- | --- |
| F1: export ownership | An explicit MLflow run ID could select another diagnostic operation; UUID representations differed. | Sync verifies the development experiment and canonical operation linkage. The native foreign-run case rejects the mismatch without damaging the original export; repeated and uppercase-UUID synchronization preserve the same run. |
| F2: actual case results | A selected case/property could be reported without a retained execution result. | The native result artifact supplies exact unique case/property IDs and executed status. Missing, duplicate, skipped, unperformed or wrong-property results fail reconciliation. Executed failures remain failures; instrumentation does not turn them into passing behavior or impose a new quality threshold. |
| F3: source identity | A run could declare different dependencies, and inventory declarations were not checked against actual source bytes or every original surface. | Revision and dependency maps must agree. Native verification reads mounted source bytes, checks their hashes and preserves the finite declared surface set. Changed declarations, actual source drift and a removed/resealed surface produce incomplete verification. |
| F4: sanitized credentials | A known credential embedded in a field name could leak through redaction reasons. | Sanitized copies omit those keys; reasons are categorical and do not echo raw field names. Canary checks cover the serialized payload and complete redaction metadata; private native originals remain intact. |
| F5: context and bindings | Inspection found missing required LLM context, unchecked effective-binding digests and unchecked generation phase. | The caller requires LLM/judge context, validates the existing typed binding and its self-digest, and matches exact stage/phase. Positive and negative kernel cases cover correct context, missing context, changed binding and wrong phase. Non-LLM execution context remains distinct. These are deterministic verifier/caller observations, not a real provider dispatch. |
| F6: coverage arithmetic | Two native records for one dispatch yielded an incomplete result with matched coverage2/1. | Only a unique one-to-one native match contributes. The independently expected duplicate case is incomplete with observed1, matched0 and ratio0/1. Valid unique joins still pass. |
| F7: command ambiguity | Duplicate action/flag fields silently dispatched the final value. | Both command entrypoints use the shared canonical decoder before typed dispatch. Duplicate action/capture fields fail; the native activation rejection case independently confirms unchanged active configuration and subsequent usable readback. |

FINDINGS.json maps each repair to its properties and acceptance evidence. Direct regressions and the frozen fixture/DAG rows expand the existing literal cases; no original categories, scoring formulas, corpus scopes or future feature obligations were removed.

## Acceptance evidence and reuse

The complete iteration selection ran with `--require-clean` on candidate944e0a3. All53 named Go race tests passed. Native setup could not bind5001 because an earlier disposable test-owned Lab container remained listening with no test process. That original receipt remains **failed and byte-preserved**. After stopping only that identified container, the unobserved native command was retried with `--require-clean` on the identical candidate and all36 native PostgreSQL/MinIO/MLflow tests passed. The separate affected foundation selection passed all32 native tests on the same candidate.

The reconciler reparses the exact raw logs, retains both original statuses, verifies disjoint successful case observations, requires all88 cases, checks current source/fixture/scenario/oracle/command/dependency fingerprints and committed-clean provenance, and records52 retained Go case observations plus36 new native case observations. No unavailable, failed, skipped or missing case is counted as a pass. Passing unaffected cases were not rerun merely to refresh a receipt.

Primary evidence is `openspec/changes/implement-teacher-error-trainer/evidence/iteration3/ACCEPTANCE.json`, the unchanged failed `clean.json`, passed `clean-native-retry.json`, passed `clean-foundation.json`, their raw logs and `NATIVE-ARTIFACTS.json`. Retained actual artifacts include native MLflow SQLite state, registry versions, downloaded export bytes, browser observations and an ingested OTLP span. Earlier implementation receipts remain under `historical-a523a13-verification` and earlier historical directories.

Readback command: `python3 -B audit/iteration-3-llm-lab-20261010/reconcile.py --check`. Evidence-only acceptance/report/task edits introduce no behavior changes; valid green behavior is reused after the record commit.

## Structural checks and preservation

Strict OpenSpec, DAG/discovery, **3050 structural/preservation assertions** and pinned Go1.26.5 vet/gofmt passed on the final semantic batch. CHECKS.json records exact retained log hashes. The graph preserves455 requirements,470 properties and2324 case edges, including2056 blocked and16 planned future cases; structural success does not implement those cases.

The original122 taxonomy leaves/recipes,42 scoring formulas,11 full-source scopes, source/provider registries and migrations001/002/003 remain unchanged. Earlier fixture/property preservation remains covered by the structural check. PREVIEW-PRESERVATION.json records current saved configuration, Library and protected canonical GAPS.md byte readbacks. Startup logs are retained in this audit's evidence directory.

## Scope and remaining development

This acceptance closes the full agreed iteration3 tooling scope. All21 model/speech execution surfaces remain planned. Constructed command/result/context/span fixtures make zero provider calls, retain their origin and use explicit N/A inference coverage. They establish tooling behavior, not semantic model quality, actual provider dispatch or whole-product operation.

Provider adapters remain iteration4. Full pipeline experiments and the22 diagnostic arithmetic contracts remain iteration14. No inference, speech synthesis, paid usage, account registration or corpus import occurred. These preserved later-iteration tasks are not unresolved iteration3 findings.
