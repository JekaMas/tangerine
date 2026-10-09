# Tangerine pre-implementation OpenSpec exploration

Baseline: `9d581e220d375fbc28016af48f41e691737094ad` on local main, 2026-10-09.

The primary product flow is defined, but the specification is not yet fully consistent or ready to apply without the repairs below. This exploration found **ten repair groups**, including four significant producer/consumer gaps. The other groups concern stale competing instructions, unnecessary limits, first-use clarity and concrete verification design. No additional product approval is needed to specify their resolutions within the agreed scope.

The user's clarification governs this audit: **check the specification before implementation**. Missing application implementation is not a finding or acceptance criterion here. No active behavior contract or application code was changed. Proposed repairs and their positive/negative expectations are recorded, rather than described as closed.

## Findings and disposition

| ID | Finding | Disposition before implementation |
|---|---|---|
| EXP-001 | False additional correction/explanation claims lack a total native credit projection | Define the semantic forbidden-condition bridge with actual source evidence; preserve the42 formulas. |
| EXP-002 | Adjudication can identify a key defect but cannot return the new units/rubric required to write the repaired key | Add an explicit typed repair proposal/call and same-audio correspondence; preserve old results. |
| EXP-003 | Canonical checkpoint/frozen render bindings lack a fully specified durable resume association/readback | Specify the existing-operation checkpoint and continuation identity; no queue or new service. |
| EXP-004 | Decisive generated pragmatic/discourse facts lack an explicit listener-visible projection | Require audible or neutral public context; private recipe facts cannot determine the grade. |
| EXP-005 | Older active mutation DTO/provenance text conflicts with the newer typed manifest | Use one current payload/hash/replay contract, preserving all original data. |
| EXP-006 | Operation effects still require the removed permission-epoch service | Retain revocation/source notice operations and provenance; remove epoch/grant-closure behavior. |
| EXP-007 | Lifetime three-attempt caps obstruct ordinary explicit recovery | Remove manual lifetime ceilings; keep per-operation deadlines/idempotency/bounded automatic attempts. |
| EXP-008 | Linguistic-audit trusted prompt conflicts with the shared one-repair rule | State one object per reply and one adapter-owned repair request within the original cap. |
| EXP-009 | LLM-key-only local first-use path needs explicit speech choice/model-setup continuation | Tighten the setup journey; local/service remain selectable and no hidden fallback/download occurs. |
| EXP-010 | Positive/negative graph entries do not always specify concrete fixture/oracle behavior | Bind affected plans to actual packets/state/artifacts/exact fractions before implementing them. |

[FINDINGS.md](FINDINGS.md) provides the precise contradiction or missing bridge, concrete counterexample, proposed fix, paired expectation and owning file/line for each. EXP-009 is a usability/specification recommendation about the documented default journey, not a claim that a local backend is absent. EXP-010 concerns the quality of the written plans, not whether application tests have already run.

## Full user and data walkthrough

[SCENARIOS.md](SCENARIOS.md) traces38scenario groups with76 positive/negative expectations: ZIP setup and keys, configuration, canonical generation, mutation/count/control rules, edit replay, acoustics/capability selection, stored playback, context disclosure, Unicode answers, paraphrases, repeated targets, duplicates/retractions/contradiction, omitted components, exact grading, recommendations, key reconsideration, refusal/repair/retry, interruption/lease/idempotency, history, optional review, every original source scope, native conversion, frequency/relations, benchmarks/splits, prompt activation, context/debug, Lab comparisons/outage and backup/restore/deletion. Related existing property identities are explicit in SCENARIOS.json.

[DATA-WIRING.md](DATA-WIRING.md) maps each input/output to its purpose, activation, written producer/storage/consumer and completeness limit. It maps all eleven original scopes individually and preserves supplemental full-release scopes. Independently generated exercises need taxonomy/recipes, generated text/key, actual audio, answer and actual semantic decisions. They need no complete empirical mistake corpus, native reference audio, global frequencies, study questionnaire or participant collection. Missing source bytes/dictionaries still affect the specifically selected source or completeness claim; they are not silently declared acquired.

[LLM-AND-SCORING.md](LLM-AND-SCORING.md) traces all nine application bindings, the separate diagnostic judge policy, speech/ASR/assessment surfaces, context disclosure, retries, prompt activation, quality populations and native arithmetic. Eight exact written oracle packets are in SCORING-PACKETS.json. The published [MLflow OTLP/HTTP interface](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/ingest) supports the chosen direct native-client/SQLite design; no additional collector or hosted account is needed. This is interface research, not installed integration evidence.

## Overengineering assessment

Remove the stale permission service and arbitrary lifetime retry ceiling identified above. Keep human qualifications/consent/ratings only as genuine imported source metadata; do not expose them as new review forms or runtime eligibility. Keep benchmark/full-source/population thresholds confined to their selected reports. A single Generate exercise action can orchestrate existing internal operations without exposing67 routes or numerous DTOs to the operator. Lab stays optional during ordinary use; AI development uses its already agreed finite selected evidence route.

The existing local services and immutable key/audio/answer linkage serve preserved features. Do not add another queue, vector database, hosted prompt gateway, account/auth system, approval workflow, universal accent qualification or automatic promotion. Consolidating duplicated schema/prose generation would reduce maintenance drift; it is not a new product feature or prerequisite for this exploration.

Retain the checks with concrete purpose: literal mutation replay, actual playable bytes, reference scope, exact scoring fractions, original answer spans, saved-before-call behavior, idempotency and late-write fencing, source archive path/inert-file handling, secret-safe snapshots and consistent backups. Removing them would weaken correctness or lose user data. Harmless response wrappers/additive model fields already have tolerant normalization; they should not become stricter gates.

## Decisions and external inputs

**No new user decision is required for EXP-001 through EXP-010.** Their proposed resolutions follow the agreed simple local product and LLM-only checking policy. Apache-2.0, configurable models, all 122 categories/recipes, all42 formulas, all 11original full-source scopes and every optional feature/data scope are preserved.

Existing unknown private releases, exact native dictionaries/use terms, supplementary linked media, actual empirical populations and later selected provider/audio observations remain factual inputs for their own optional actions/claims. They cannot be replaced with an approval, generated data or this report. No renewed request for universal source access, participants, human reviewers or official certification is introduced. Current synthesis baselines explicitly specify en-US/en-GB voices; further accent choices would be a future explicit binding/scope addition, not an unresolved decision required by this audit.

## Validation and proof limits

The inventory covers215 active files,134 JSON schemas and34 documents. The existing planning scope has35 capabilities,392 properties and1,568 case edges corresponding to1,566 distinct test identities. This audit mechanically inventories every active file and reconciles the full declared scope; its semantic evidence is the written cross-domain traces and concrete findings. These counts do not establish that every linguistic instance, future provider behavior or declaration is correct.

New audit validation passed: exact finding anchors/owner paths, scenario links/property membership, complete property/test scope reconciliation, unchanged active-file hashes, eight independently derived arithmetic packet results and the required discovery-ledger validator. See [VALIDATION.json](VALIDATION.json). Existing green OpenSpec/declared-graph receipts retain their original proof boundary; unchanged active contracts/graph/commands did not justify rerunning them. No behavior test, model call, audio generation, service launch, dependency installation, corpus acquisition, source email or publication occurred.

An initial auxiliary runtime-owner lookup found no exact Tangerine semantic index and no open exact JetBrains project (`project_not_found`). Those limits are recorded in SEARCH-LIMITS.json and discovery, but do not make a specification gap or change this audit's acceptance criteria. No substitute index or runtime proof is claimed.

The canonical task list and discovery ledger record this exploration and its proposed repairs. Active contracts remain unchanged pending their specification refinement before implementation. The unrelated `audit/spec-fullness-20261008/GAPS.md` edit is preserved.
