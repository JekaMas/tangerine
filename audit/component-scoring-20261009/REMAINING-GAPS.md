# Remaining specification gaps after independent component scoring

This supersedes the open/closed status in the historical pre-implementation exploration without rewriting its evidence. Six of its ten groups are resolved in the written specification: EXP-001 and EXP-005 through EXP-009. The four groups below remain engineering specification work; none needs another product-owner decision. The implemented application and actual model/audio observations are outside this specification-only increment and are not counted as specification gaps.

## EXP-002 — Typed automatic key and rubric repair

The existing adjudication response can identify a key defect and explain it, but cannot supply the complete new or repaired unit, correction options, explanation propositions and old-to-new correspondence required by key-write. A reason string is insufficient to construct a new version deterministically. Independent optional-explanation scope is now defined; this does not supply the missing repair payload.

**Where it matters:** a listener finds a real omitted error; gives a valid repair that fits no available option; or challenges an incorrect explanation rubric. The last case must preserve supported primary scores while its optional component is reconsidered.

**Repair:** define a typed repair payload on the existing LLM adjudication operation (or one explicit existing-role repair call), with complete proposed units/options/rationales, evidence, added/removed/retained correspondence and validation outcome. The server supplies immutable IDs/envelopes and appends the supported key version while keeping the heard audio and original result. Incomplete or unsupported proposals remain provisional only for affected components. No human review, new service or mandatory extra ordinary call.

**Why needed:** it is necessary for the already promised automatic key-repair feature. Ordinary correctly generated exercises can be scored without taking this branch. Without this contract an implementer would have to invent missing key content from prose.

**Owners:** specification/v2/contracts/llm-review-output.schema.json; key-write.schema.json; docs/review-and-gold.md; docs/answer-component-scoring.md.

## EXP-003 — Durable preparation checkpoint and exact resume selection

The spec promises reuse of clean text and frozen generation/speech bindings after an interrupted preparation, but does not yet define the persisted association selecting that exact checkpoint and its bindings. The existing answer-attempt stage cache does not establish preparation identity; a blueprint ID alone can refer to several preparations.

**Where it matters:** clean text is saved, mutation fails, the browser closes, settings change, and the user selects Resume. Retry limits are now removed, but that does not identify which old preparation to continue.

**Repair:** define one durable preparation-operation record/association using existing operation/document/asset storage: preparation ID, phase status, canonical asset/hash, frozen complete settings and model/prompt/speech bindings, candidate/manifest references and failure. Define the library/UI readback and continuation input. Resume selects the original ID and unfinished phase; changed inputs start a new preparation. Reuse existing foreground operations and idempotency; no background queue or scheduler.

**Why needed:** it is necessary to make the promised restart/resume behavior reproducible and prevent saved text from silently being paired with newly selected settings or voices. A successful uninterrupted run does not need this recovery branch.

**Owners:** specification/v2/contracts/generation-request.schema.json; candidate-envelope.schema.json; stage-cache.schema.json; docs/generation-contract-details.md; docs/runtime-and-storage.md.

## EXP-004 — Decisive contextual facts must reach the listener

Some pragmatic/discourse recipes depend on roles, intent or external facts. The generator may know those facts privately, while the candidate contains only utterances/planned units and the listening view shows generic public context. There is still no explicit typed projection ensuring that each decisive generated fact is audible or neutrally disclosed before answering.

**Where it matters:** mate is treated as inappropriate because Dr Lee requested Dr Lee in this meeting, but the listener only hears Good morning, mate. Hidden context cannot justify detection/correction penalties or a judgment that the learner's explanation is false.

**Repair:** require each decisive fact to be realized in audible text or a neutral public-context addition, with a typed generated-context field/projection into the saved case and pre-answer listening view. Keep error labels, positions and answer key private. An unsupported contextual judgment must be regenerated or treated as unsupported in its affected component; no human approval or separate review gate.

**Why needed:** it is necessary for fair scoring of the retained contextual categories. Basic errors evident from the audio do not require extra context. The same observable-context rule must govern correction and optional explanation assessment.

**Owners:** specification/v2/contracts/case-candidate.schema.json; case.schema.json; docs/generation-contract-details.md; docs/mistake-data-and-mutations.md; domain/mutation-recipes.v1.json.

## EXP-010 — Concrete fixtures and independent oracles for older property plans

Many earlier positive/negative graph entries still restate a requirement without naming exact accepted/rejected inputs, expected artifacts/counts/fractions or an independent oracle. This increment adds 18 concrete scenario fixtures with 36 unexecuted positive/negative edges for the changed contracts. It does not turn the older generic entries into concrete designs or passing tests.

**Where it matters:** before implementation, each affected user step, category/property and failure path must say what an implementation test will observe. For example, five en-US roles with Kokoro order af_heart/am_adam should project af_heart,am_adam,af_heart,am_adam,af_heart and disclose shared voices; a generic defaults are visible assertion is insufficient.

**Repair:** bind each still-generic affected case to literal or parameterized fixtures, exact expected state/artifacts/counts/fraction/failure and an independent oracle. Use all 122 recipe definitions for category fixtures while retaining authored versus empirical labels. Reconcile case identities without changing existing observed evidence or claiming model quality from constructed packets.

**Why needed:** it is necessary for the user's requested positive/negative coverage of every step/property and for useful implementation acceptance. It is an unfinished test-design obligation, not a new product feature, benchmark gate or demand for human gold labels.

**Owners:** openspec/changes/implement-teacher-error-trainer/verification.json; property-inventory.json; audit/pre-implementation-explore-20261009/SCENARIOS.json; specification/v2/docs/splits-and-validation.md.

## External optional data and future evidence

Restricted Cambridge releases, Doubao participant/instrument data, separate Moodrick/NIR exports, official L2 equivalence and supplementary media retain their existing source-specific status and full scope. They are needed only for their selected imports or exact empirical claims, not generated exercises or ordinary explanation assessment. Existing product-data-relevance mappings still govern them. Native application/provider/audio/Lab observations remain future work under later implementation/execution authority; no static result here is their substitute.

**Product decisions required now: none.** The correction/explanation rule is recorded from the user's request. The remaining repairs above need written engineering contracts and concrete fixtures.
