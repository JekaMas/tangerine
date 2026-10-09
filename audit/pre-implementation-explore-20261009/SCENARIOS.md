# Complete user-scenario walkthrough

These38 scenarios cover setup, the primary flow, optional retained features, failures, LLM development and maintenance. Each has a concrete written positive/negative expectation. They are not executed tests. Related property IDs identify existing planning scope; no new behavior is marked implemented.

## SC-001 — ZIP first-use with only an LLM key

**Input:** Source ZIP without .git; DeepSeek key present; speech key absent; local model cache initially empty.

**Positive:** Explicit local speech setup downloads only its selected model assets with actual progress/digests; retry preserves workspace; after setup the one-button generated exercise is usable.

**Negative:** No Azure-key demand on the selected local path, invisible backend fallback, corpus prerequisite, account form or fake ready audio.

**Written owners:** [specification/v2/docs/local-delivery.md](../../specification/v2/docs/local-delivery.md), [specification/v2/docs/ui-flows.md](../../specification/v2/docs/ui-flows.md)

**Open finding:** EXP-009

## SC-002 — Settings and effective profiles

**Input:** Default configured LLM plus an extraction override; credentials are local references.

**Positive:** Freeze actual default/override profile, prompt/schema/budget and speech selection before each operation; show credential presence only.

**Negative:** Changing Settings does not change an in-flight attempt, reveal a key or silently substitute another model.

**Written owners:** [specification/v2/docs/provider-contracts.md](../../specification/v2/docs/provider-contracts.md), [specification/v2/contracts/effective-binding.schema.json](../../specification/v2/contracts/effective-binding.schema.json)


## SC-003 — Unavailable optional source

**Input:** No external corpora acquired; later explicitly select unavailable EFCAMDAT-R2 as context.

**Positive:** Independent generation succeeds without corpus inputs; selected unavailable context offers an explicit source choice or independent generation.

**Negative:** No hidden substitute corpus or false complete-source status; unrelated exercise use remains available.

**Written owners:** [specification/v2/docs/product-data-relevance.md](../../specification/v2/docs/product-data-relevance.md)


## SC-004 — Clean baseline followed by separate mutations

**Input:** Topic travel, two speakers, approximately 180 words, B1 optional.

**Positive:** Persist ordered speaker/utterance canonical text with no units, then a separate mutated candidate whose canonical sequence is identical.

**Negative:** Mutation cannot rewrite the saved baseline, delete a speaker/turn or present a partially generated record as complete.

**Written owners:** [specification/v2/docs/generation-contract-details.md](../../specification/v2/docs/generation-contract-details.md), [specification/v2/contracts/generation-input.schema.json](../../specification/v2/contracts/generation-input.schema.json)


## SC-005 — Exact count and family precedence

**Input:** Explicit count=2 with grammar+lexis; variant count=0 with same family metadata.

**Positive:** Positive count has two independent true-error obligations and at least one from each family; zero creates no true-error units and preserves the chosen family metadata.

**Negative:** Controls/secondary labels do not count as errors; impossible count/family combination is reported without silently erasing a choice.

**Written owners:** [specification/v2/docs/generation-contract-details.md](../../specification/v2/docs/generation-contract-details.md)


## SC-006 — Replay text edits

**Input:** Canonical abcdef; delete [1,3), insert X at3, replace [4,6) with Y; all positions against original text.

**Positive:** Literal replay is aXdY; provenance retains originals/spans/unit associations and final-surface scopes.

**Negative:** Applying later offsets against already edited text, unowned changes or conflicting overlapping edits is not accepted as the saved transformation.

**Written owners:** [specification/v2/docs/generation-contract-details.md](../../specification/v2/docs/generation-contract-details.md), [specification/v2/contracts/mutation-manifest.schema.json](../../specification/v2/contracts/mutation-manifest.schema.json)

**Open finding:** EXP-005

## SC-007 — Acoustic-only mutation

**Input:** Canonical/surface words identical; one requested IPA contrast and one prosody request.

**Positive:** Store intent distinct from observation, exact typed render operation and actual final WAV identity.

**Negative:** IPA/SSML or text-only inference is never copied into observed IPA/confirmed heard-acoustic evidence.

**Written owners:** [specification/v2/docs/audio-methods.md](../../specification/v2/docs/audio-methods.md), [specification/v2/docs/mistake-data-and-mutations.md](../../specification/v2/docs/mistake-data-and-mutations.md)


## SC-008 — Backend capability conflict

**Input:** Local basic Kokoro selected; explicit fine-IPA target.

**Positive:** Explain the unsupported operation and offer explicit supported service/backend or edited request; retain target and clean baseline.

**Negative:** No deletion of the requested target, invented local capability or silent switch to a paid provider.

**Written owners:** [specification/v2/docs/simple-generation-flow.md](../../specification/v2/docs/simple-generation-flow.md), [specification/v2/domain/providers.v1.yaml](../../specification/v2/domain/providers.v1.yaml)


## SC-009 — Novel mutation instances

**Input:** Article-omission recipe illustration I bought a pen; request new cooking context.

**Positive:** Select a new contextual opportunity preserving inclusion/exclusion and one independent repair obligation; record novelty basis.

**Negative:** Copying the illustration is reported; no assertion of absence from proprietary training data or corpus-wide OOD proof.

**Written owners:** [specification/v2/docs/simple-generation-flow.md](../../specification/v2/docs/simple-generation-flow.md), [specification/v2/domain/mutation-recipes.v1.json](../../specification/v2/domain/mutation-recipes.v1.json)


## SC-010 — Compile and save real audio

**Input:** Two literal surface turns; configured voice/locale; gap_after_ms=100.

**Positive:** Call in order, save actual responses and 24kHz mono PCM16 master, including exactly2400 silence samples after each turn; final hash refers to those bytes.

**Negative:** Corrupt/truncated/all-silent output produces no playable placeholder; no silent trimming/correction of the intended mutations.

**Written owners:** [specification/v2/docs/audio-methods.md](../../specification/v2/docs/audio-methods.md), [specification/v2/contracts/render-plan.schema.json](../../specification/v2/contracts/render-plan.schema.json)


## SC-011 — Repeated playback is a read

**Input:** Published exercise with actual stored master hash.

**Positive:** Reopen/replay the same saved audio without inference and retain its case/audio identity.

**Negative:** Missing stored bytes cannot be hidden by synthesizing new speech under the old identity.

**Written owners:** [specification/v2/docs/simple-generation-flow.md](../../specification/v2/docs/simple-generation-flow.md), [specification/v2/docs/runtime-and-storage.md](../../specification/v2/docs/runtime-and-storage.md)


## SC-012 — Shared voice assignment

**Input:** Five en-US speakers with local voice order af_heart,am_adam.

**Positive:** Assignments are af_heart,am_adam,af_heart,am_adam,af_heart; preparation shows shared voices and stable s1..s5.

**Negative:** No unstated five-distinct-voice requirement, fabricated speaker identity or invisible voice substitution.

**Written owners:** [specification/v2/docs/generation-contract-details.md](../../specification/v2/docs/generation-contract-details.md), [specification/v2/domain/providers.v1.yaml](../../specification/v2/domain/providers.v1.yaml)


## SC-013 — Listener-visible decisive context

**Input:** Dr Lee has requested address Dr Lee in this meeting; surface greeting uses mate.

**Positive:** The address preference is in audible text or neutral public context before answering; key/error labels remain hidden.

**Negative:** A preference present only in a private recipe/key cannot justify scoring the listener against that fact.

**Written owners:** [specification/v2/docs/generation-contract-details.md](../../specification/v2/docs/generation-contract-details.md), [specification/v2/docs/mistake-data-and-mutations.md](../../specification/v2/docs/mistake-data-and-mutations.md)

**Open finding:** EXP-004

## SC-014 — Control-only or empty key

**Input:** Explicit count=0; permissible variant control; error G=0.

**Positive:** Play real audio, report control/overcorrection findings and N/A true-error composite.

**Negative:** Do not manufacture a100-point composite or treat every lawful accent/variant as erroneous.

**Written owners:** [specification/v2/docs/math-and-judgments.md](../../specification/v2/docs/math-and-judgments.md), [specification/v2/docs/review-and-gold.md](../../specification/v2/docs/review-and-gold.md)


## SC-015 — Exact answer/draft bytes

**Input:** Russian free text includes emoji, combining marks and two repeated quotes.

**Positive:** Save exact UTF-8; offsets count original Unicode codepoints; uniquely recoverable quotes are mapped, ambiguous repeats remain explicit.

**Negative:** No NFC rewrite of saved answer, UTF-16/codepoint confusion or arbitrary repeated-quote localization.

**Written owners:** [specification/v2/docs/math-and-judgments.md](../../specification/v2/docs/math-and-judgments.md), [specification/v2/contracts/claim-extraction.schema.json](../../specification/v2/contracts/claim-extraction.schema.json)


## SC-016 — No assertions

**Input:** One true error and one control; empty or nonassertive teacher response.

**Positive:** No TP/FP; true-error miss remains and requested missing repair gets zero; nonassertive content is retained/ignored.

**Negative:** No perfect score, fabricated teacher repair or false assertion inferred from silence.

**Written owners:** [specification/v2/docs/math-and-judgments.md](../../specification/v2/docs/math-and-judgments.md), [specification/v2/docs/scoring-v1.md](../../specification/v2/docs/scoring-v1.md)


## SC-017 — Paraphrase and alternative correction

**Input:** She work here; answer The verb after she needs s; say works.

**Positive:** LLM localizes one event and checks the existing semantic rubric; native code derives credit.

**Negative:** Literal category keyword or answer-string equality cannot replace semantic matching; invented quote/option IDs fail projection.

**Written owners:** [specification/v2/docs/math-and-judgments.md](../../specification/v2/docs/math-and-judgments.md)


## SC-018 — Wrong category with correct detection

**Input:** Correctly localize agreement defect but call it a preposition error; classify enabled and disabled variants.

**Positive:** Detection remains TP; category credit reflects the supported wrong/unknown mapping; disabled classification does not change composite.

**Negative:** Do not cancel detection or create a new taxonomy ID to improve the grade.

**Written owners:** [specification/v2/docs/scoring-v1.md](../../specification/v2/docs/scoring-v1.md), [specification/v2/docs/math-and-judgments.md](../../specification/v2/docs/math-and-judgments.md)


## SC-019 — Repeated target localization

**Input:** Two identical She work here occurrences in separate turns; answer names only that quote.

**Positive:** Specific turn/context can select one target; unlocalized ambiguous quote remains unresolved.

**Negative:** No one claim fans out into two TPs or selects the most favorable occurrence.

**Written owners:** [specification/v2/docs/math-and-judgments.md](../../specification/v2/docs/math-and-judgments.md)


## SC-020 — Duplicate, retraction and contradiction

**Input:** Two duplicate claims; a later explicit retraction; two incompatible unretracted repairs.

**Positive:** Duplicates count once, backward explicit retraction deactivates its target; unresolved endorsed contradiction goes to LLM reconsideration.

**Negative:** No highest-scoring fragment selection, retraction cycle or forward reference.

**Written owners:** [specification/v2/docs/math-and-judgments.md](../../specification/v2/docs/math-and-judgments.md)


## SC-021 — False additional explanation

**Input:** Correct agreement explanation plus every English verb always ends in s.

**Positive:** Use actual answer spans and fixed forbidden-assertion semantics to give zero for the affected explanation only.

**Negative:** A complete required-proposition set cannot earn full credit while a verified false extra rule is ignored.

**Written owners:** [specification/v2/docs/math-and-judgments.md](../../specification/v2/docs/math-and-judgments.md), [specification/v2/contracts/evaluator-output.schema.json](../../specification/v2/contracts/evaluator-output.schema.json)

**Open finding:** EXP-001

## SC-022 — Required components and exact composite

**Input:** Detection/correction enabled; classification/explanation disabled; one true error with no repair.

**Positive:** Missing requested correction is zero; disabled components do not contribute; no-opportunity components are N/A.

**Negative:** LLM free-text numeric grade, unrequested trait estimate or reweighted composite cannot replace registered arithmetic.

**Written owners:** [specification/v2/docs/scoring-v1.md](../../specification/v2/docs/scoring-v1.md), [specification/v2/domain/metrics.v1.yaml](../../specification/v2/domain/metrics.v1.yaml)


## SC-023 — Feedback and recommendations

**Input:** Frozen exact score with one miss and a control FP; feedback call fails.

**Positive:** Preserve answer/score, report feedback failure, allow feedback-only retry; new advice/examples link to actual findings and are labelled new practice.

**Negative:** No regrading on recommendation retry or fabricated unheard audio/corpus quotation.

**Written owners:** [specification/v2/docs/simple-generation-flow.md](../../specification/v2/docs/simple-generation-flow.md), [specification/v2/contracts/feedback-output.schema.json](../../specification/v2/contracts/feedback-output.schema.json)


## SC-024 — Supported omitted error or defective rubric

**Input:** Plausible extra error not in key, or valid alternative outside its options; same heard audio.

**Positive:** LLM provides a typed supported new-key proposal, server versions it and creates unit correspondence before selected rescoring.

**Negative:** No reason-only key repair, in-place mutation of old denominator or automatic FP solely because the generator omitted it.

**Written owners:** [specification/v2/docs/review-and-gold.md](../../specification/v2/docs/review-and-gold.md), [specification/v2/contracts/llm-review-output.schema.json](../../specification/v2/contracts/llm-review-output.schema.json)

**Open finding:** EXP-002

## SC-025 — Generation resume after process/browser loss

**Input:** Canonical phase complete; mutation times out; settings then change.

**Positive:** Explicit Resume selects original durable checkpoint and frozen settings; new request starts new preparation instead.

**Negative:** No regenerated baseline, adopted changed backend or paid background retry under the old operation.

**Written owners:** [specification/v2/docs/generation-contract-details.md](../../specification/v2/docs/generation-contract-details.md), [specification/v2/contracts/generation-request.schema.json](../../specification/v2/contracts/generation-request.schema.json)

**Open finding:** EXP-003

## SC-026 — Provider output normalization and repair

**Input:** Harmless fenced/additive JSON; distinct conflicting valid objects; malformed audit output.

**Positive:** Unique semantic projection is accepted; one same-profile repair handles genuine ambiguity/malformed output within the cumulative cap; all receipts retained.

**Negative:** No rejection solely for harmless wrappers, extra numeric authority, unlimited repairs or conflicting prompt prohibition.

**Written owners:** [specification/v2/docs/provider-contracts.md](../../specification/v2/docs/provider-contracts.md), [specification/v2/prompts/linguistic-audit-v1.txt](../../specification/v2/prompts/linguistic-audit-v1.txt)

**Open finding:** EXP-008

## SC-027 — Refusal, rate limiting and manual retries

**Input:** Provider refuses; alternatively429 with Retry-After; three earlier explicit render outages.

**Positive:** Retain refusal; eligible transport retry stays inside the270s deadline; later explicit render retry may recover the unchanged candidate.

**Negative:** No refusal-challenging loop, SDK nested retries, automatic favorable-grade reruns or lifetime fourth-retry lockout.

**Written owners:** [specification/v2/docs/runtime-and-storage.md](../../specification/v2/docs/runtime-and-storage.md), [specification/v2/docs/audio-methods.md](../../specification/v2/docs/audio-methods.md)

**Open finding:** EXP-007

## SC-028 — Double submit, lease and late reply

**Input:** Double submit same idempotency key; changed body under that key; late old evaluation completion after lease recovery.

**Positive:** One operation for matching bytes, conflict for changed bytes; token/epoch/revision fence rejects late write; answer stays saved.

**Negative:** No duplicated paid action, stale grade publication or database transaction held during provider latency.

**Written owners:** [specification/v2/docs/runtime-and-storage.md](../../specification/v2/docs/runtime-and-storage.md)


## SC-029 — Immutable case/result history

**Input:** Publish revised key/audio after an attempt started; select old result revision.

**Positive:** Old attempt retains heard bytes/key/binding; new version is separate; explicit selection can display either supported revision.

**Negative:** No reinterpretation under latest mutable key or automatic hidden regrading.

**Written owners:** [specification/v2/docs/lifecycle.md](../../specification/v2/docs/lifecycle.md), [specification/v2/docs/persistence.md](../../specification/v2/docs/persistence.md)


## SC-030 — Optional LLM review and modality

**Input:** Text-only DeepSeek with no phone measurements; optional case review selected.

**Positive:** One key-aware machine review records actual exposure/modality and unknown acoustic confirmation; ordinary use does not require it.

**Negative:** No label of independent blind listening or heard phoneme solely from transcript/intent; no human reviewer prerequisites.

**Written owners:** [specification/v2/docs/review-and-gold.md](../../specification/v2/docs/review-and-gold.md)


## SC-031 — Full source intake for every original scope

**Input:** Each of the11 complete scopes, including ancillary files/alternative representations; XML/XLSX/M2/TextGrid or authorized export.

**Positive:** Preserve every supplied member/native field/partition/annotator and exact release; raw completion and normalized completion counted separately.

**Negative:** No sample-as-full, one derivative replacing another, discarded unknown field, executing embedded code or invented missing participant data.

**Written owners:** [specification/v2/docs/sources/acquisition-and-rights.md](../../specification/v2/docs/sources/acquisition-and-rights.md), [specification/v2/domain/corpus-sources.v1.yaml](../../specification/v2/domain/corpus-sources.v1.yaml)


## SC-032 — Native correction and leaf mapping

**Input:** BEA two annotators, noop and overlapping alternative edits; SpeechOcean scores; L2 manual/automatic tiers.

**Positive:** Preserve native labels/clocks/scale/origin; one compatible correction reconstruction; contextual inferred leaf mapping separately identified.

**Negative:** No union of annotator alternatives, score-to-IPA invention or automatic alignment promoted to manual gold.

**Written owners:** [specification/v2/docs/sources/bea-v21.md](../../specification/v2/docs/sources/bea-v21.md), [specification/v2/docs/sources/speechocean762.md](../../specification/v2/docs/sources/speechocean762.md), [specification/v2/docs/sources/l2-arctic-v5.md](../../specification/v2/docs/sources/l2-arctic-v5.md)


## SC-033 — Frequency, relationships and unknown populations

**Input:** One named inspected native-label view with raw counts; no122-leaf crosswalk/learner opportunity population.

**Positive:** Report native frequencies with actual denominator and origin; keep taxonomy hierarchy separate from measured co-occurrence/confusion.

**Negative:** No global English error probabilities, synthetic frequencies as learner prevalence or zero for an uninspected population.

**Written owners:** [specification/v2/docs/mistake-data-and-mutations.md](../../specification/v2/docs/mistake-data-and-mutations.md)


## SC-034 — Full benchmark versus selected development

**Input:** Selected three leaves plus explicit request for full122-leaf732-distinct-stimulus report; source identities connect split groups.

**Positive:** Selected experiments are usable with unselected coverage named; full claim needs exact population; connected provenance groups stay unsplit under60/20/20 targets.

**Negative:** No732unit aliases as732distinct stimuli, split leakage manufacture or participant-derived difficulty from synthetic answers.

**Written owners:** [specification/v2/docs/review-and-gold.md](../../specification/v2/docs/review-and-gold.md), [specification/v2/docs/splits-and-validation.md](../../specification/v2/docs/splits-and-validation.md)


## SC-035 — Prompt/context editing and activation

**Input:** Edit one numeric registry version, export complete nine-binding bundle, activate it, then revert.

**Positive:** Editing makes no inference and does not alter active app; atomic activation affects new operations only; custom absent bundle is unavailable.

**Negative:** No mutable latest alias in a frozen run, hidden fallback, secret template expansion, benchmark gate or automatic promotion.

**Written owners:** [specification/v2/docs/llm-lab.md](../../specification/v2/docs/llm-lab.md), [specification/v2/contracts/prompt-bundle.schema.json](../../specification/v2/contracts/prompt-bundle.schema.json)


## SC-036 — Actual context and input budgets

**Input:** Blind extraction answer; mapper key/extraction; independent audit; speech requests; over-capacity required context.

**Positive:** Keep exact role/order/data assets and trust provenance; blind/audit disclosure respected; local preprocessing/unknown hidden inputs explicitly bounded; size conflict preserves input.

**Negative:** No hidden truncation, key leak to extraction, prior mapping sent to independent audit, fake full capture or credential body export.

**Written owners:** [specification/v2/docs/llm-lab-contract-details.md](../../specification/v2/docs/llm-lab-contract-details.md), [specification/v2/docs/ai-development.md](../../specification/v2/docs/ai-development.md)


## SC-037 — Lab comparisons, judges and denominators

**Input:** Same frozen answer cases, two variants, repeated runs, one failure and one unknown acoustic observation.

**Positive:** Use native pipeline/42 arithmetic plus22 diagnostics; pool raw counts, show paired exclusions and full failure population; judge independent/self-consistency origin explicit.

**Negative:** No average per-case F1 as pooled F1, failed-row deletion, candidate labels leaked to candidate or text-only acoustic proof.

**Written owners:** [specification/v2/docs/llm-lab-contract-details.md](../../specification/v2/docs/llm-lab-contract-details.md), [specification/v2/domain/llm-quality-metrics.v1.json](../../specification/v2/domain/llm-quality-metrics.v1.json)


## SC-038 — Lab outage, source notice and maintenance

**Input:** MLflow unavailable; source revoked; backup/restore/deletion includes native assets and optional Lab copies.

**Positive:** Ordinary score survives Lab outage; explicit sync does no inference; source notice is stored; restore uses consistent assets/schema with previous workspace retained; pending cleanup visible.

**Negative:** No epoch/grant service, regenerated missing media, secret backup, deletion-complete claim while copies remain or corruption hidden behind successful startup.

**Written owners:** [specification/v2/docs/maintenance-and-limits.md](../../specification/v2/docs/maintenance-and-limits.md), [specification/v2/docs/llm-lab.md](../../specification/v2/docs/llm-lab.md), [specification/v2/docs/migration-compatibility.md](../../specification/v2/docs/migration-compatibility.md)

**Open finding:** EXP-006
