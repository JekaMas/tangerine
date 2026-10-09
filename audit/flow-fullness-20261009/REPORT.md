# Current specification completeness and contradiction audit

Date: 2026-10-09. Baseline: main at03abd3d. Authority: inspect and update the existing specification, without implementation. The unrelated user change in audit/spec-fullness-20261008/GAPS.md is preserved and excluded.

The preceding claim that the flow was fully backed by contracts was too broad. Its product sequence was coherent, but several execution details remained informal and two diagnostics contradicted their owning rules. This audit closes13groups below. It preserves the ordinary topic → clean text → novel mutations/list → stored synthesized audio → free-text answer → LLM semantic mapping → native score/recommendations flow. Corpora, reference audio, separate case review, empirical benchmark and LLM Lab stay optional for ordinary use. No human peer review is introduced.

## Findings and exact resolutions

| ID | Missing or contradictory contract | Resolution and owning source |
|---|---|---|
| FULL-01 | Minimal requests depended on unspecified workspace locale/register/task/pace/gap defaults; voice assignment beyond two voices was undefined. | Explicit configurable preparation_defaults, fallback values and ordered voice cycling; actual shared voices remain visible. generation-contract-details.md and configuration-registry.yaml. |
| FULL-02 | Blueprint provider_profile_id could be read as either LLM or speech; explicit broad families/counts/advanced targets had no conflict precedence. | Speech binding is distinct from the generation LLM; explicit choices are retained, zero mutation semantics and family coverage are defined, conflicting choices report an actionable conflict without substitution. |
| FULL-03 | Canonical hash and actual recipe delivery were informal; a mutation could change/reorder the canonical script while claiming preservation. | Exact JCS baseline projection and ordered identity preservation; generation-input includes actual selected registry records/hash and cache/context identity. |
| FULL-04 | Mutation provenance lacked a typed asset and an exact offset/edit composition rule. Canonical and surface scopes could drift after insertion/deletion. | mutation-manifest schema, canonical-coordinate replay, surface-coordinate key scopes, ordered insertions, combined overlapping obligations, acoustic intents and exact reconstruction. |
| FULL-05 | Planned-unit projection omitted exact defaults for added key fields and generated provenance. Native recordings were contradicted by ground-truth.audio.origin permitting only synthetic; internal_training could not survive the source-use projection. | Complete projection of units/speakers/turns/evidence/source; ordinary unknown fields stay null/not_verified/unrated; native/local audio origins and the existing eighth source use are representable. Eleven original source identities are unchanged. |
| FULL-06 | Preparation/settings could change between clean generation, mutation and render; resume could use a different binding without a declared new preparation. | Freeze the preparation blueprint/bundle/profile across those phases, preserve checkpoint bindings, and distinguish a changed preparation from retry. Attempts freeze their own evaluator/task/version separately. |
| FULL-07 | Lab dataset and pipeline inputs had no complete typed manifest; a configuration hash alone did not identify the frozen configuration payload. | llm-quality-dataset, answer-pipeline input, per-variant configuration_asset_id and scope-specific input/reference rules. Allocate every case×variant×repetition tuple and retain all failed/cancelled/not-run rows. |
| FULL-08 | Semantic Lab judging named a profile but had no executable input/output/rubric/prompt contract; the ordinary linguistic-audit output did not fit diagnostic propositions. | Dedicated lab-judge prompt/input/output plus frozen judge-policy definition, actual profile/schema/prompt/reference/receipt identities and supported/unsupported/unknown verdicts; arithmetic stays native. |
| FULL-09 | Lab context kinds omitted extraction/candidate/native scores/rubric. mapping_audit policy included prior decisions despite the independent-audit rule. | Complete explicit context kinds; mapping receives saved extraction, feedback receives native scores; independent mapping audit omits first-map decisions. Numeric bundle/phase/version and literal template-substitution rules are explicit. |
| FULL-10 | Lab aggregation could average reduced ratios; unknown totals promised a subtotal that the schema could not store; comparison output shape was informal. | Typed raw sufficient statistics/known subtotal and exact comparison artifact; all22diagnostic metrics have explicit pooling/mean/quantile/sum/pair/macro rules. Original42equations are byte unchanged. |
| FULL-11 | Stage caps could reset per fallback/repair, and1000ms Lab export could consume the persistence reserve. | Logical-stage cumulative caps and export bounded by remaining time after the existing five-second reserve; no queue/retry loop or extended deadline. |
| FULL-12 | Audio prose called thresholds warnings while YAML named them reject/fail; equality and codec-conversion text could add a publication/review gate. | Rename threshold policy to warning without changing values; malformed/empty/all-silent bytes remain failures. Codec byte/version changes do not require separate review. |
| FULL-13 | Wilson difficulty prose emitted moderate/very_hard, while persisted labels were medium/expert. | Preserve numerical thresholds and emit the existing medium/expert enum labels; ordinary generated units remain unrated without the real teacher population. |

The details are in specification/v2/docs/generation-contract-details.md and llm-lab-contract-details.md, with four new schemas and additive changes to existing contracts. These are content/persistence definitions. No public API, required service, human ceremony or startup benchmark has been added.

## Completeness coverage and limits

The audit reconciles the entire active file inventory, every JSON/YAML parse, all local schema references and every indexed field/hash. file-inventory.json lists all209files with byte hash and line count. This is mechanical line/field coverage, not a claim of independent linguistic validation for every sentence or proof that all imaginable English mistakes exist in the finite taxonomy.

Semantic inspection follows the seven ordinary steps plus optional advanced rendering/import/review/dispute/benchmark/Lab and local-delivery/storage/recovery paths. The following contract families are represented:

| Flow/data family | Definition and cross-contract coverage |
|---|---|
| Input/preparation | Required three inputs, optional level/families/count/seed/backend, full advanced blueprint, defaults/voices/public context, incompatibility handling and frozen settings. |
| Clean generation/mutations | Separate stage identities/prompts; actual recipe selection; immutable canonical checkpoint, exact text edits/novelty origin, contextual/acoustic intent and all122leaf recipes. |
| Audio/playback | Local Kokoro and original Azure profiles, typed render operations, actual WAV assembly/sample clock/hashes, stored replay, failure retention, optional acoustic evidence, independent actual recording imports. |
| Key and answer | Complete shared/additional field projection, source provenance, hidden pre-submit key/transcript/count, exact submitted bytes, Unicode spans, duplicate/retraction/ambiguity/alternative-repair rules. |
| Semantic checking/scoring/advice | Blind extraction, configurable mapper, optional independent audit, LLM reconsideration/dispute/versioning, all27core+15auxiliary equations, structural opportunity/N/A/composite rules, feedback retry without regrading. |
| Local runtime/internal interfaces | All original operations/request-field ownership, local source download/run, generated internal secrets/no accounts, synchronous limits, leases/idempotency, atomic assets/references, explicit backup/restore/deletion/migration. |
| Sources/benchmarks | Eleven original full-release identities/components/native contracts, all supplementary identities and actual acquisition statuses; raw/normalized/missing distinctions, contextual mappings, frequencies/co-occurrence/splits, full732stimulus target and real empirical populations. |
| Optional LLM Lab | Complete nine application prompt/context bindings, saved activation/revert, actual input/output/receipt traces, dataset/configuration/judge identities,22diagnostic formulas/aggregation, failed populations, privacy/export/backup/deletion. |

No further product-owner decision is identified for this defined ordinary flow. This is not a claim that provider quality, full empirical122-leaf coverage, all accents or the future application have been observed. Optional native contracts with unavailable source data retain an exact lossless intake/binding protocol; their actual unknown columns/instruments cannot be fabricated.

## Remaining external inputs and observations

These remain unavailable or unperformed; they are preserved scope and evidence needs, not new prerequisites for independently generated exercises:

1. Complete restricted Cambridge EFCAMDAT R2/Shatz/Öksüz originals/derivatives, native dictionaries/workbooks and applicable access/use terms. The acquired public Öksüz companion cannot replace these. Cambridge's existing response requests an academic email; no eligible institutional identity has been invented.
2. Actual anonymized Doubao participant records/media, exact instrument/prompt wording/scales and reuse terms. Public study text cannot reconstruct withheld rows or consent.
3. Separate complete Moodrick and NIR exports, field dictionaries and actual source-use agreements/private adapter documents. Each remains its own source; the lossless local export path is specified without guessed endpoints.
4. Official L2-ARCTIC byte/version equivalence and explanation of the native annotation-count differences. The complete pinned mirror remains available as raw data with honest third-party provenance; supplied official links do not prove a successful official transfer.
5. ICNALE separately linked speech media and reuse clarification, Speak & Improve eligibility/access, and the unavailable DRAL third-party/optional higher-resolution representations. Existing acquired package scopes remain separately recorded.
6. Future actual localized source→leaf mappings, final full benchmark stimuli/acoustic contrasts and genuine teacher-answer populations for empirical category frequency, difficulty and validity. These are produced/observed during subsequent authorized work, not filled with synthetic evidence by this audit.
7. Actual provider/model/voice/build/dependency observations and application positive/negative acceptance evidence. Basic local/service routes are specified; precise acoustic targets/additional accent bindings retain their actual capability/evidence limits.

The existing acquisition ledger remains the authority for downloaded bytes:75verified files /38,299,550,055bytes at its recorded observation. No fresh download/access retry, email, provider call, model install or native parsing was performed here.

## Validation and handoff

Final366static checks passed: whole current JSON/YAML/reference/field/hash/ownership reconciliation, positive/negative artifact contracts, independent Unicode-edit replay, pooled-F1 arithmetic counterexample, cancellation-denominator accounting and immutable original graph preservation.132schemas contain2,877indexed field occurrences;88local schema references resolve. These checks are not a full JSON Schema engine conformance suite or application tests.

Strict OpenSpec validation passed. The property graph validates362requirements/377properties/1,508case edges. Discovery validates after correcting the authoring helper's affected scope; the already-green graph was retained, not rerun for a discovery-only repair. Six new requirements include24positive/negative behavior plans, all blocked/unexecuted. Existing graph requirement/property/case records remain unchanged. Changes to the current spec hash vector do not update old runtime bindings or refresh old test receipts.

Initial artifact-helper failures and their corrections are retained in initial-check-failure.txt and graph.log. Existing native-data/provider/application observations stay within their earlier proof boundaries. No implementation, inference, audio generation, Docker/MLflow runtime, migration, install, configuration-key change or publication occurred. Keep the product change open for future authorized implementation. Resume from tasks.md; preserve the unrelated GAPS.md edit.
