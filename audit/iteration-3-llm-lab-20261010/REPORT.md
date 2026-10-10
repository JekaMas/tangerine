# Iteration 3: LLM development tooling acceptance

Iteration 3 is implemented and accepted on committed-clean candidate **a523a13daefe1d5658140ef116dfde043bd3aefd**. Its complete selection passed **88/88 registered cases**: 44 positive and 44 negative cases across 22 properties, with two distinct literal fixtures per polarity. The same candidate also passed **32/32 affected foundation cases** for packaged startup, storage, Library and launcher compatibility. No skipped, failed, unavailable or substituted case counts as acceptance.

The implementation provides optional pinned MLflow 3.17.0 startup, all nine immutable prompt/context bindings, exact registry-version export, native configuration activation and reversion, frozen context construction, typed datasets and finite planned experiment populations, an inference inventory, sanitized OTLP traces, private native diagnostic retention, explicit export-only recovery and published development-run verification. Existing PostgreSQL/MinIO storage remains authoritative. Registry edits do not silently activate themselves. Ordinary application startup works without Lab.

## Actual observations and repairs

The committed clean run observed 53 named Go race tests and 36 native integration tests through real disposable PostgreSQL, MinIO and MLflow services, plus the 32 native foundation tests. Retained artifacts include actual MLflow SQLite state, prompt/context versions, browser observations, native diagnostic records, downloaded artifacts and an ingested OTLP span. Reconciliation checks exact command/native results, current registered case fingerprints, source bytes, exported hashes and committed ancestry. It does not refresh old hashes or turn partial receipts into full acceptance.

Native counterexamples discovered during completion are repaired:

- Lab builds its host probe through the pinned Docker target for the actual client; it no longer extracts a Linux probe after normal Compose startup rebuilt the API image.
- A successful diagnostic save returns the linked asset rather than its earlier reserved state.
- Content capture requires a JSON boolean; the invalid string `"false"` cannot enable capture.
- Lab startup recreates a stopped container whose networks were removed by ordinary shutdown, preserving the Lab volume. The native restart test removes only its own stopped Lab network and independently observes all 18 registry versions after recovery.

Both the complete stable dirty run and complete committed-clean run passed after the final repair. Earlier failed or unavailable runs and superseded passed receipts remain historical, including the 8cac728 and 4cb3d71 candidates. The final acceptance-record commit changes only tasks, reports and retained evidence; it introduces no behavior changes.

## Other required checks and preservation

Strict OpenSpec, DAG/discovery, **3,050 structural/preservation assertions** and pinned Go 1.26.5 vet/gofmt passed. CHECKS.json binds retained logs to their hashes and records why unchanged checks remain valid. INVALIDATION.md identifies actual changed semantic inputs. The original 122 taxonomy leaves and recipes, all 42 scoring formulas, 11 source scopes, provider/source registries, migrations 001/002/003 and prior fixture/property rows remain unchanged; PRESERVATION.json records byte readback.

Qualification uses the existing Docker engine on macOS arm64. The registry proxy failed to download the image, so the same official content-verified MLflow image was loaded through host retrieval. Native fixtures assert its exact arm64 image configuration; the published default remains the immutable upstream multiarchitecture digest. The selected preview port is explicitly 5001 because macOS AirPlay owns 5000; no host networking or system service was changed. The existing preview is restored at http://localhost:3000 and Lab is running at http://localhost:5001. PREVIEW-PRESERVATION.json confirms identical saved configuration and Library response hashes and the unchanged protected GAPS.md edit. Actual startup logs are retained in evidence/preview-restore-network.log and evidence/preview-lab-network-final.log.

## Proof limits and next iteration

All 21 model/speech execution surfaces remain **planned**. Deterministic tooling diagnostics make **zero provider calls**; their inference coverage is **N/A with an explicit reason and actual Lab artifacts**. Constructed span timing and response fixtures test tooling, not provider behavior or semantic quality. No inference, synthesis, paid use or corpus import occurred.

Real provider adapters remain iteration 4. Full pipeline experiments and the 22 diagnostic arithmetic contracts remain iteration 14. The original evaluation and full-product obligations are preserved in the canonical task list. This acceptance closes the defined iteration 3 tooling scope; it does not claim that the whole trainer is implemented.

Primary receipts: openspec/changes/implement-teacher-error-trainer/evidence/iteration3/ACCEPTANCE.json, clean.json, clean-foundation.json and NATIVE-ARTIFACTS.json. Independent readback: `python3 -B audit/iteration-3-llm-lab-20261010/reconcile.py --check`.
