# Pre-implementation specification findings

Baseline `9d581e220d375fbc28016af48f41e691737094ad`. Ten repair groups are proposed; none is applied to the active behavior contracts in this exploration. All are engineering specification work within the agreed product scope. No additional product approval is needed.

## EXP-001 — False additional correction or explanation assertion has no total scorer projection (high)

The prose gives zero credit when an additional assertion is verified false. The mapper can return only existing forbidden proposition IDs, and native credit is otherwise satisfied-required/all-required; rejected status itself is not a zero-credit rule. A finite rubric need not include the extra assertion. There is no total mapping from that false assertion into the declared arithmetic.

**Concrete failure:** Key: present-tense She work here -> She works here. The answer supplies works and correctly explains agreement, but also asserts that every English verb always ends in s. All listed required propositions may be satisfied while no enumerated forbidden proposition names this new false rule.

**Proposed repair:** Specify one fixed semantic contradiction/false-addition proposition per eligible correction option and unit rationale, with actual supporting answer spans and case/rule evidence. Alternatively define an equally explicit typed verdict that maps into that fixed forbidden condition. Do not let the model supply a numeric credit or fabricate a new proposition ID at grading time. Preserve the existing zero-if-forbidden and 42 formulas.

**Positive:** A supported equivalent correction with harmless extra true detail satisfies the existing rubric and earns its exact fraction.

**Negative:** A correct repair plus a supported false added assertion earns zero for the affected correction/explanation component, without cancelling a correctly localized detection.

**Owners:** [specification/v2/docs/math-and-judgments.md:75](../../specification/v2/docs/math-and-judgments.md#L75), [specification/v2/docs/math-and-judgments.md:67](../../specification/v2/docs/math-and-judgments.md#L67), [specification/v2/contracts/evaluator-output.schema.json:104](../../specification/v2/contracts/evaluator-output.schema.json#L104)

## EXP-002 — Key-defect adjudication cannot return the proposed repaired key (high)

LLM review output can carry judgments of existing units, mapping decisions, issue strings and a reason. It cannot carry a new unit, repaired correction option/rationale, or typed key proposal. The prose promises automatic new key versions and correspondence; key-write requires a complete ground truth. That producer-to-writer conversion is missing.

**Concrete failure:** An answer correctly identifies an omitted second error, or gives a valid repair that no existing rubric option permits. resolution=key_defect plus a reason does not specify the new unit/options and correspondence needed for rescoring.

**Proposed repair:** Define a typed semantic key-repair proposal or one explicit existing-role repair call with a complete input/output contract. Server derives IDs/envelopes, preserves the heard audio, validates the proposed units/rubric, and appends the new key plus total added/removed/retained unit correspondence. If unsupported, retain the old provisional result. No human review or new service.

**Positive:** A supported omitted error yields an explicit new key unit and same-audio correspondence before selected rescoring.

**Negative:** A key_defect reason without a complete supported proposal cannot be treated as a repaired key or revised score.

**Owners:** [specification/v2/docs/review-and-gold.md:9](../../specification/v2/docs/review-and-gold.md#L9), [specification/v2/contracts/llm-review-output.schema.json:16](../../specification/v2/contracts/llm-review-output.schema.json#L16), [specification/v2/contracts/key-write.schema.json:8](../../specification/v2/contracts/key-write.schema.json#L8), [specification/v2/docs/math-and-judgments.md:69](../../specification/v2/docs/math-and-judgments.md#L69)

## EXP-003 — Generation checkpoint and resume identity are underdefined (high)

The contracts promise saving/reusing the canonical checkpoint and frozen generation/render settings after browser/process loss. generate input contains blueprint/configuration/source IDs and an integer generation_attempt; output is only candidate envelope. The described reusable stage-cache is linked to an answer attempt, not a preparation operation. No written deterministic association/readback selects the canonical checkpoint and frozen speech binding for the next generate/render continuation.

**Concrete failure:** Canonical generation completes, mutation times out, browser closes, settings are changed, and the operator presses Resume. Which original operation/checkpoint is selected, and where is its render configuration recovered?

**Proposed repair:** Define a durable preparation-operation checkpoint association using existing documents/assets/operation status: original operation ID, phase state, canonical asset/hash, frozen complete settings/bundle/speech binding, candidate/manifest references and failure. State how Resume reads it and starts a new idempotent continuation. No new background queue; changed inputs create a new preparation explicitly.

**Positive:** Resume after completed canonical phase reuses its bytes and original bindings and invokes only the unfinished mutation/render phase.

**Negative:** Resume cannot choose a different baseline by blueprint ID alone or adopt newly active speech/model settings silently.

**Owners:** [specification/v2/docs/generation-contract-details.md:39](../../specification/v2/docs/generation-contract-details.md#L39), [specification/v2/contracts/generation-request.schema.json:36](../../specification/v2/contracts/generation-request.schema.json#L36), [specification/v2/contracts/candidate-envelope.schema.json:28](../../specification/v2/contracts/candidate-envelope.schema.json#L28), [specification/v2/contracts/stage-cache.schema.json:19](../../specification/v2/contracts/stage-cache.schema.json#L19)

## EXP-004 — Decisive generated context has no explicit disclosure projection (high)

Recipes require decisive roles/facts/intent to diagnose pragmatic/discourse events. Simple preparation supplies topic plus generic public policy; candidate output has only utterances and planned units. The contracts do not explicitly require each decisive generated fact to be either audible or in a neutral pre-answer public context, nor specify how a generated external fact reaches that view.

**Concrete failure:** The sociolinguistic recipe treats mate as inappropriate because Dr Lee explicitly requested Dr Lee in this meeting. If the only heard line is Good morning, mate and the public topic is a meeting, the private recipe context cannot justify penalizing the listener.

**Proposed repair:** Require the generator to locate each decisive fact in audible surface text or an explicit neutral public-context addition. Specify its projection into stored case and listening view, excluding mutation labels/locations/key. Contextual judgments with missing decisive facts remain unsupported or are regenerated; this is not a separate review gate.

**Positive:** A listener is given the relevant address preference/role context and can judge the contextual event without seeing its answer label.

**Negative:** An intent/relationship known only to the generator or private mutation key cannot determine a scored contextual error.

**Owners:** [specification/v2/docs/generation-contract-details.md:11](../../specification/v2/docs/generation-contract-details.md#L11), [specification/v2/docs/mistake-data-and-mutations.md:58](../../specification/v2/docs/mistake-data-and-mutations.md#L58), [specification/v2/domain/mutation-recipes.v1.json:5103](../../specification/v2/domain/mutation-recipes.v1.json#L5103), [specification/v2/contracts/case-candidate.schema.json:35](../../specification/v2/contracts/case-candidate.schema.json#L35)

## EXP-005 — Two active mutation provenance contracts disagree (medium)

The older active mistake-data contract prohibits adding recipe fields to generation-input and defines a different provenance payload/digest interpretation. The newer generation contract explicitly requires mutation_recipes/recipe_registry_sha256 in that DTO and owns mutation-manifest. Both remain normative active files; general overlay precedence is not a single field contract.

**Concrete failure:** An implementer following the older paragraph omits the recipe array or writes the older custom edit payload, while another consumer expects the typed manifest and JCS candidate hashes.

**Proposed repair:** Replace the obsolete DTO/provenance paragraphs with explicit references to generation-input and mutation-manifest and its exact hash/replay projection. Preserve native examples, all recipes, lossless edits and source provenance.

**Positive:** Both generation and mutation evidence resolve the same typed manifest/hash projection.

**Negative:** The old incompatible payload or absent recipe-array instruction cannot be selected as an alternative current contract.

**Owners:** [specification/v2/docs/mistake-data-and-mutations.md:48](../../specification/v2/docs/mistake-data-and-mutations.md#L48), [specification/v2/docs/generation-contract-details.md:19](../../specification/v2/docs/generation-contract-details.md#L19), [specification/v2/docs/generation-contract-details.md:23](../../specification/v2/docs/generation-contract-details.md#L23)

## EXP-006 — Revocation still requires the removed permission-epoch service (medium)

Both operation registries require incrementing permission epoch and atomically blocking derived use. Current maintenance/source/runtime policy explicitly removes mandatory permission epochs and dependency-closure permissions. The nullable legacy stage-cache field is already correctly archival; the operation effects are the stale part.

**Concrete failure:** A local source notice changes and revoke is invoked. The operation table demands a runtime grant/epoch closure that the current product explicitly excludes.

**Proposed repair:** Change revoke effects consistently to save the actual notice/status, expose affected selected-source actions and operator choices, and retain provenance. Do not resurrect grant graphs or invalidate unrelated authored exercises. Keep the operation and native legacy metadata.

**Positive:** A source revocation notice is stored/shown with actual source provenance.

**Negative:** The action neither demands a grant/epoch service nor silently treats revoked source content as unrestricted or blocks independent generated content.

**Owners:** [specification/v2/domain/operations.yaml:381](../../specification/v2/domain/operations.yaml#L381), [specification/v2/domain/operation-ownership.yaml:802](../../specification/v2/domain/operation-ownership.yaml#L802), [specification/v2/docs/maintenance-and-limits.md:7](../../specification/v2/docs/maintenance-and-limits.md#L7)

## EXP-007 — Lifetime three-attempt caps conflict with explicit recovery (medium)

Generation request has maximum=3 and audio methods/registry/122 target records cap render attempts at three per candidate. The ordinary flow offers explicit retry/resume, but no lifetime counter ownership or fourth-attempt behavior is defined. This arbitrary content-lifetime boundary is unnecessary; per-operation deadlines and bounded automatic retries already exist.

**Concrete failure:** Three manually requested synthesis calls fail during a service outage. After service recovery the unchanged valid candidate cannot be rendered under the literal cap.

**Proposed repair:** Remove candidate-lifetime manual attempt ceilings, preserving monotonic attempt provenance, idempotency, one foreground action and per-operation transport/repair/deadline bounds. Optional diagnostics may select a finite repetition count without capping ordinary recovery.

**Positive:** A fourth explicit user retry after an outage can reuse the saved candidate and perform a real render call.

**Negative:** No retry loops automatically, hides earlier failures or bypasses the existing per-operation budget.

**Owners:** [specification/v2/contracts/generation-request.schema.json:40](../../specification/v2/contracts/generation-request.schema.json#L40), [specification/v2/docs/audio-methods.md:121](../../specification/v2/docs/audio-methods.md#L121), [specification/v2/domain/configuration-registry.yaml:51](../../specification/v2/domain/configuration-registry.yaml#L51), [specification/v2/domain/target-capabilities.yaml:32](../../specification/v2/domain/target-capabilities.yaml#L32)

## EXP-008 — Linguistic-audit prompt contradicts the shared repair policy (medium)

The trusted prompt forbids repairing JSON with a second response. The shared provider contract permits one same-profile repair for every malformed/truncated/ambiguous stage output. The special stage exception is not specified.

**Concrete failure:** A linguistic audit returns truncated JSON. The adapter sends the permitted repair request while the retained stage instruction says not to repair it.

**Proposed repair:** Align the prompt with exactly one adapter-owned repair request and one object per individual response. Retain the original failure/raw output and cap the whole logical stage; remove the conflicting blanket prohibition.

**Positive:** One malformed audit output may be repaired by the same profile within the original cap.

**Negative:** No unlimited conversational correction loop or missing-content fabrication is permitted.

**Owners:** [specification/v2/prompts/linguistic-audit-v1.txt:29](../../specification/v2/prompts/linguistic-audit-v1.txt#L29), [specification/v2/docs/provider-contracts.md:15](../../specification/v2/docs/provider-contracts.md#L15)

## EXP-009 — LLM-key-only first-use journey is incomplete (medium)

The default speech profile is Azure; it needs a separate speech key. Local Kokoro is supported through a separate model-setup action, but the start/first-use scenario does not define an explicit local choice and missing-model continuation before Generate for someone who supplied only an LLM key. Thus the stated simple LLM-key local-use goal still has an underspecified setup branch.

**Concrete failure:** A user extracts the ZIP, supplies a DeepSeek key and starts the app. The default speech setting requires an absent Azure key even though the intended local speech route needs no speech key.

**Proposed repair:** Specify first-use local/service speech choice with local as the LLM-only path and one explicit model-setup action/progress/retry when assets are absent. Service choice uses its supplied key. Freeze the choice before generation; do not silently fall back between paid service and local rendering or download models on an unrelated startup.

**Positive:** A user with only an LLM key completes the documented local speech setup and generates an exercise.

**Negative:** Missing Azure credentials cannot unexpectedly stop the local choice, and missing local weights cannot produce fake successful audio.

**Owners:** [specification/v2/domain/configuration-registry.yaml:53](../../specification/v2/domain/configuration-registry.yaml#L53), [specification/v2/docs/local-delivery.md:9](../../specification/v2/docs/local-delivery.md#L9), [specification/v2/docs/ui-flows.md:3](../../specification/v2/docs/ui-flows.md#L3)

## EXP-010 — Property-plan counts overstate concrete scenario design (medium)

The graph contains positive/negative entries, but many are generic translations of a SHALL/THEN with unspecified accepted/rejected input and expected result. In particular new completeness cases say exercise the positive condition rather than supplying a concrete packet and oracle. Distinct IDs/fingerprints do not by themselves establish independently specified counterexamples for every step/property.

**Concrete failure:** CMP-01.P1.S1.POSITIVE says to freeze the stated case/configuration/reference and exercise the positive condition; its observable is only Defaults and shared voices are visible. It does not name speaker/voice inputs and the exact projected assignments.

**Proposed repair:** Before implementation, bind each affected plan to a concrete fixture, exact expected state/artifacts/counts/fraction or failure, and its independent oracle. Parameterize 122-leaf recipe cases from the authored catalogue with declared limitations. The scenario and scoring packets in this audit are specification examples only, not executed tests or empirical gold.

**Positive:** For five en-US speakers and local voice order af_heart,am_adam, expected assignments cycle af_heart,am_adam,af_heart,am_adam,af_heart with shared voice disclosure.

**Negative:** A generic positive/negative label or empty assertion cannot count as a concrete tested or fully designed semantic property.

**Owners:** [openspec/changes/implement-teacher-error-trainer/verification.json:48414](../../openspec/changes/implement-teacher-error-trainer/verification.json#L48414), [specification/v2/docs/splits-and-validation.md:13](../../specification/v2/docs/splits-and-validation.md#L13)
