# Remaining specification gaps and decisions — 2026-10-08

This report replaces the old missing-file questionnaire for the current v2 draft. It distinguishes missing written rules, proposed choices, external source contracts and unperformed implementation/evidence. The historical 55 IDs stay stable: GAP-005/006 were superseded by the actual simple-local user scope. The other 53 have been reconciled individually. No attachment approval, mock, invented source data or copied reference validator closes a gap.

Current statuses: **30 partially specified entries; 9 policy-only entries; 3 missing external contracts; 11 entries with a supplied written definition and unperformed runtime/data acceptance**. Policy proposals also occur within partial entries: **17 original policy choices** remain unapproved, plus newly identified licensing, gate-applicability and first-run-content decisions. These are overlapping categories, not additive gap totals.

## Recheck findings requiring further definition or decisions

The twelve findings below group the exact remaining defects across the original gap IDs. Engineering owns technical refinements; only actual product/linguistic/rightsholder decisions need user or source-owner input. Each finding specifies its missing rule and both closure boundaries.

### FRC-006 — Request versus server versus source field ownership is incomplete

**Owner:** engineering. **Related IDs:** GAP-001, GAP-003, GAP-010, GAP-029.

**What is missing or contradictory:** Many create/submit endpoints require full-record IDs, server timestamps, digests or revisions while ownership says server assigns them. The referenced prior reservation has no corresponding general operation. An automated scan flags 26 operations; frozen precondition hashes are legitimate, not all flagged fields are errors.

**Required definition or input:** For each flagged operation supply a field-by-field input/server/import/precondition classification and separate creation DTO where necessary. Define actual reservation or direct server assignment without inventing source dates, person identity or approval. See operation-field-ownership.json.

**Affected artifacts:** `specification/v2/domain/operation-ownership.yaml`, `specification/v2/docs/interface-contract.md`, `specification/v2/contracts/person.schema.json`, `specification/v2/contracts/review-context.schema.json`, `specification/v2/contracts/dispute.schema.json`.

**Positive closure:** Valid source metadata and client input create a server-owned envelope with exact recorded identities.

**Negative closure:** Client-chosen local receipt/lease/approval/time cannot pass, and genuine imported evidence is not rejected just for containing source IDs.

### FRC-008 — Synthetic voice grouping and gold split feasibility

**Owner:** product and qualified linguistic reviewer. **Related IDs:** GAP-046, GAP-047.

**What is missing or contradictory:** Grouping uses speaker identity and pair families, but does not define whether shared synthetic voice/profile joins all generated stimuli. Four reused voices and multi-voice dialogues can create one connected group, making one pair/leaf/split impossible.

**Required definition or input:** Choose and document distinct genuine learner/speaker, synthetic character, provider voice, prompt and participant grouping axes; define which are strict held-out axes and how global IDs are assigned. Provide feasible full-scope allocation or report impossibility; do not cut real leakage edges.

**Affected artifacts:** `specification/v2/docs/splits-and-validation.md`, `specification/v2/docs/review-and-gold.md`, `specification/v2/domain/providers.v1.yaml`, `specification/v2/contracts/split-manifest.schema.json`.

**Positive closure:** Chosen grouping has independently allocatable full coverage with every edge preserved.

**Negative closure:** Reused identities or arbitrary per-case renaming cannot make leaked holdout look independent.

### FRC-009 — Required target/profile qualification matrix is not enumerated

**Owner:** engineering with qualified linguistic reviewers. **Related IDs:** GAP-032, GAP-036, GAP-038, GAP-047.

**What is missing or contradictory:** All 122 leaf entries exist, but required_observation repeats a generic two-review rule. No finite list defines required voice/locale/acoustic target combinations, per-combination exact constraints, comparison/control instructions and measurement/human-label requirements. Presence of 122 entries is not a complete capability matrix.

**Required definition or input:** Bind every leaf to required supported profile/voice/locale/operator combinations, target/control plan, public context and hard observation criteria. Identify human judgment cases and exact acoustic methods/units where numeric criteria are required. Unsupported combinations remain blockers. No actual canary audio/approval is fabricated.

**Affected artifacts:** `specification/v2/domain/target-capabilities.yaml`, `specification/v2/docs/audio-methods.md`, `specification/v2/domain/providers.v1.yaml`.

**Positive closure:** Every required combination has one precise positive/control qualification protocol.

**Negative closure:** A different word/voice, generic approval, requested accent or absent observation cannot qualify the combination.

### FRC-010 — DDL immutability, erasure and frozen-version references conflict

**Owner:** engineering. **Related IDs:** GAP-003, GAP-051, GAP-053, GAP-055.

**What is missing or contradictory:** document_immutable blocks UPDATE only, while ordinary DELETE is possible where no FK prevents it. Audit immutability and restrictive references conflict with rights-aware erasure. object_node.case_version_id points to a mutable entity_head, with no database guard that the head continues to identify that exact immutable case version.

**Required definition or input:** Supply the exact write privileges/trigger and maintenance erasure/tombstone procedure, reference closure, permitted audit retention and immutable case-version identity constraints. The SQL is a design reference until these definitions are consistent. Inspect actual SQL in PostgreSQL after implementation authorization.

**Affected artifacts:** `specification/v2/db/schema.sql`, `specification/v2/docs/persistence.md`.

**Positive closure:** Only version-bound documents can support references; a permitted erasure produces honest unavailable/tombstone reads.

**Negative closure:** Normal delete, head retargeting, audit-reference destruction or forbidden personal-data retention cannot evade guards.

### FRC-012 — Non-evaluation operation budgets and cost admission are incomplete

**Owner:** engineering. **Related IDs:** GAP-031, GAP-052.

**What is missing or contradictory:** 270 seconds is exact for teacher evaluation; generation, linguistic audit, render, measurement, full imports and reconsideration batches lack separate exact admission/time/output/recovery budgets. Price-profile fields and reservation calculation/unknown-charge reconciliation are prose, without a complete closed price/cost contract.

**Required definition or input:** Define each foreground operation deadline, cancellation/restart, per-call limits, nested-call concurrency admission, full-import atomic/partial boundary and cost profile/reservation state transition. Bind real pricing units/date/recipient; unknown cost is never zero. These are engineering definitions, not requests to execute paid work.

**Affected artifacts:** `specification/v2/domain/configuration-registry.yaml`, `specification/v2/docs/runtime-and-storage.md`, `specification/v2/docs/maintenance-and-limits.md`, `specification/v2/domain/operations.yaml`.

**Positive closure:** Every listed foreground operation has bounded progress, cancellation and truthful costs.

**Negative closure:** Nested operations, long imports, retries or unknown bills cannot bypass local guards or produce fake full completion.

### FRC-015 — Critical acceptance cases and gold alignment need exact inventory

**Owner:** engineering and qualified gold annotators. **Related IDs:** GAP-048, GAP-050.

**What is missing or contradictory:** Critical classes are named, but no complete case ID/provenance/expected-decision inventory is supplied. When extraction differs between gold/model/repeated runs, exact decision populations still need a frozen correspondence; otherwise unresolved/omitted claims can shift denominators.

**Required definition or input:** Specify immutable gold event/claim alignment IDs, treatment of unmatched/spurious/omitted decisions for every statistic, and each critical case’s exact expected semantic outcome and source. The cases themselves require real or separately authorized evidence. Do not invent teacher answers to fill them.

**Affected artifacts:** `specification/v2/docs/splits-and-validation.md`, `specification/v2/docs/math-and-judgments.md`, `specification/v2/contracts/teacher-gold.schema.json`, `specification/v2/contracts/holdout-report.schema.json`.

**Positive closure:** All numerators/denominators trace to one fixed complete gold population and actual critical-case ledger.

**Negative closure:** Dropped omissions, retractions, changed alignment or generic class labels cannot pass exact acceptance.

### FRC-016 — Audio implementation binding and comparison-token normalization are underspecified

**Owner:** engineering with qualified linguistic reviewer. **Related IDs:** GAP-034, GAP-035, GAP-036, GAP-037.

**What is missing or contradictory:** The text asks for a pinned resampler/options and recorded measurement commands without supplying them. WER refers to reviewed comparison-token policy without an exact case/apostrophe/punctuation/numeral normalization for the ASR hypothesis. Semantic human tokens alone do not define deterministic hypothesis tokenization.

**Required definition or input:** Define versioned FFmpeg resample/ebur128 command options, Praat/binding compatibility constraints, clock conversion and deterministic WER tokenization for both reference/hypothesis, including actual spoken numerals, contractions, fillers and missingness. Preserve separate human judgment and advisory roles.

**Affected artifacts:** `specification/v2/docs/audio-methods.md`, `specification/v2/domain/audio-methods.yaml`.

**Positive closure:** Same raw bytes/transcripts and method binding give reproducible measurements/token lists.

**Negative closure:** Different default filters, guessed numeral expansions or ASR inference cannot masquerade as the same method.

### FRC-017 — Full-release archive handling must account for inert ancillary scripts

**Owner:** engineering. **Related IDs:** GAP-039, GAP-040, GAP-041, GAP-042, GAP-052.

**What is missing or contradictory:** The full-source requirement retains all supplied members, but blanket executable-member rejection can reject an official release containing helper scripts. No disposition distinguishes inert ancillary source material from executable processing input.

**Required definition or input:** Define full member accounting, fail/quarantine dispositions, preservation location and no-execution handling for official scripts/executable bits. Path/symlink/device/expansion restrictions must remain. A rejected member cannot disappear from full completeness counts.

**Affected artifacts:** `specification/v2/docs/sources/acquisition-and-rights.md`, `specification/v2/contracts/source-release.schema.json`.

**Positive closure:** All authorized native release members have a retained/quarantined/rejected counted disposition.

**Negative closure:** Executing a helper or dropping it uncounted cannot create a complete safe ingest.

### FRC-018 — Normalized semantic groups lack an exact scorer projection

**Owner:** engineering with qualified linguistic reviewer. **Related IDs:** GAP-018, GAP-019, GAP-020, GAP-023, GAP-022.

**What is missing or contradictory:** The prose permits compatible correction/explanation fragments to combine under an earliest endorsed representative. The scorer accepts only one already-derived decision per unit and rejects duplicate decisions whose credit/fields differ. No total conversion specifies how normalized multi-claim groups become supplied/category/option/proposition/credit fields without discarding source fragments or choosing favorable alternatives. Static formula equality cannot prove this conversion.

**Required definition or input:** Define the exact deterministic normalization-plus-mapping to scoring-input projection: retracted/ignored members, representative identity, merged source spans, category consistency, reviewed equivalent alternatives, satisfied/forbidden proposition aggregation, FP unnecessary-correction counts, unresolved groups and raw duplicate telemetry. Preserve all actual source claims and apply each independent event once. Resolve material interpretation choices with linguistic policy, not arithmetic fixtures.

**Affected artifacts:** `specification/v2/contracts/normalization.schema.json`, `specification/v2/contracts/evaluator-output.schema.json`, `specification/v2/contracts/scoring-input.schema.json`, `specification/v2/docs/math-and-judgments.md`, `specification/v2/reference/scorer.py`.

**Positive closure:** Complete compatible source fragments yield exactly one evidence-backed event/credit projection with no fabricated teacher content.

**Negative closure:** Dropped false clauses, favorable repair selection, conflicting categories or duplicate counts cannot become a complete score.

### FRC-019 — Open-source software and original-bank license is not selected

**Owner:** project owner and actual content rights holders. **Related IDs:** GAP-039, GAP-054.

**What is missing or contradictory:** The product is called open source, but no project LICENSE or chosen software license is supplied. Dependency/source-corpus licenses are not a license for Tangerine, its original illustrations or a distributable reviewed bank.

**Required definition or input:** Select the project software license and attribution/copyright owner; specify separate license/consent/redistribution terms for original reviewed audio, taxonomy content and any shipped bank. MIT or Apache-2.0 can be proposed, but this review does not grant author rights or publish a license. Preserve third-party attribution and exclude unlicensed/NC/private corpus data from public source distribution.

**Affected artifacts:** `README.md`, `specification/v2/docs/local-delivery.md`, `specification/v2/docs/sources/acquisition-and-rights.md`.

**Positive closure:** A source ZIP states exact rights for software and every included data/content class.

**Negative closure:** Calling a repository open source or having provider keys cannot grant redistribution of private/noncommercial data.

### FRC-020 — Correction acceptance gate contradicts control-only domain eligibility

**Owner:** product and qualified linguistic reviewers. **Related IDs:** GAP-017, GAP-047, GAP-048, GAP-050.

**What is missing or contradictory:** VAL-REPAIR states at least 100 actual correction attempts per observable domain. acceptable_variant is an observable reporting domain, but its controls are prohibited from correction eligibility/credit. Counting unnecessary corrections as eligible repairs or relabeling acceptable variants as errors would change the metric populations.

**Required definition or input:** Define the exact gate-by-domain/component applicability matrix. State whether correction precision is required only for genuine correction-opportunity domains and supply a separate zero-credit/overcorrection control gate. Preserve all domains and existing thresholds; any correction to applicability must be an explicit policy decision rather than silently treating no eligible data as passing.

**Affected artifacts:** `specification/v2/domain/validation-policy.yaml`, `specification/v2/docs/splits-and-validation.md`, `specification/v2/docs/math-and-judgments.md`, `specification/v2/contracts/scoring-input.schema.json`.

**Positive closure:** Each gate has a possible legitimate gold population and explicit control-domain checks.

**Negative closure:** No-opportunity domains, spurious corrections or relabeled acceptable variants cannot satisfy the repair sample floor.

### FRC-021 — First-run usable content delivery remains undecided

**Owner:** project owner with real data/consent holders. **Related IDs:** GAP-039, GAP-047, GAP-054.

**What is missing or contradictory:** The setup correctly preserves an empty bank without genuine content. The requested download-run-use-as-is product does not yet specify whether the GitHub source package includes a real reviewed original bank or begins empty and requires authoring plus two qualified human reviews. Provider keys alone cannot create publication approvals or access private corpus releases.

**Required definition or input:** Choose and document the first-run content contract: include a genuinely reviewed redistributable original bank (with exact permitted audio/key/review provenance) or explicitly document an initially empty workspace and preparation/review requirements. Specify how real bundled content is imported and validated without creating fake approvals or automatic network corpus acquisition. Keep project full-source research/qualification gates distinct from each installation’s usable-content checks.

**Affected artifacts:** `specification/v2/docs/local-delivery.md`, `specification/v2/docs/review-and-gold.md`, `specification/v2/domain/corpus-sources.v1.yaml`.

**Positive closure:** A fresh download has the promised usable content or clearly specified actual preparation prerequisites.

**Negative closure:** An empty bank, unreviewed generated case or unavailable private corpus cannot masquerade as an as-is ready exercise bank.

## Decisions still requiring actual approval

These are proposed policy definitions supplied in the ZIP. Its policy-activation.json has no actual scoped approval. An engineering default or the general instruction to research the package does not settle them. A global policy choice and actual per-case human approval are separate records.

### GAP-002 — Post-submit key disclosure

Allow key disclosure only after submission, on the exact case version, through the teacher-safe projection; keep blind reviewer disclosure as a separately recorded phase. Choose whether teachers may request that disclosure at all and its intended timing. Private approvals, evidence and person identities stay private.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-007 — Publication and case transitions

Select the supplied draft/review/approved/published/retracted transition guards, required resolved final-audio reviews, and retraction/republication behavior. Confirm whether two final approvals after adjudication are required; models cannot supply them.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-009 — Dispute resolution

Select the supplied immutable dispute/adjudication/unit-correspondence/result-revision approach and whether results may be reconsidered under a new key. Specify user-visible historical versus revised results and the approved correspondence/recompute trigger.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-011 — Reviewer qualifications and independence

Approve acceptable actual qualification/competence evidence, phonetics competence for acoustic cases, per-review conflict re-attestation, two distinct non-author reviewers, and a third qualified adjudicator for disagreement. Names or accounts alone cannot establish independence.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-014 — Aliases and ancestors

Review and approve every English/Russian alias and exact taxonomy ancestor binding in category-aliases.v1.yaml. A generated bilingual label is not linguistic equivalence; unknown/ambiguous aliases remain abstentions. The complete original taxonomy is preserved.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-015 — Severity weights

Approve the proposed severity assignment and fixed 1–4 weight binding with reviewed rationale/evidence. Separate severity from learner proficiency, rated difficulty and detection credit. Do not infer it from a corpus score.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-016 — Rated difficulty

Approve the proposed >=100 independent first-exposure participant floor, Wilson interval bands, unit success versus exercise composite >=80, and unrated boundary. These are candidate thresholds, not established teacher norms.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-017 — Variety and register

Approve contextual error/acceptable-variant/uncertain judgments, allowed corrections and exclusions for all leaves and public variety/register/task context. Resolve FRC-020 control-domain gate applicability without relabeling permitted variants as errors.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-027 — Feedback failure

Confirm that a successful deterministic evaluation with feedback-only failure retains its score and exposes feedback_unavailable with a separate feedback retry. Confirm exact user-facing retry/invalidation behavior; no score recomputation merely to regenerate prose.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-028 — Linguistic audit authority

Approve the supplied advisory audit role, scope and prompt. Decide which disagreements block preparation and require actual human resolution. Audit/model prose is never a human approval or a replacement for blind final-audio review.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-032 — Render operators

Approve the typed operator catalog and hard-failure versus advisory distinction. Complete FRC-009 per-target/profile combinations and exact criteria; asking a voice for an accent or prosody does not establish observed realization.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-035 — Speech tokens and disfluencies

Approve reviewed token/interval/filler/repetition/repair boundaries and multilingual/apostrophe/numeral rules. Complete FRC-016 deterministic comparison-token normalization for both WER inputs; ASR cannot set human event truth.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-036 — Prosody methods and judgments

Approve feature units, raw-ac method choice and missingness/judgment conditions per target. Complete FRC-009 and FRC-016 exact implementation/qualification bindings; automatic measurements remain advisory unless explicitly reviewed.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-046 — Holdout grouping and allocation

Approve strict grouping axes, 60/20/20 allocation and complete pair-family retention. Resolve FRC-008 synthetic voice versus genuine speaker/character grouping and demonstrate feasible complete-leaf allocation without cutting leakage edges.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-047 — Gold counts

Approve six distinct stimuli per leaf, >=732 distinct stimuli overall, matched target/control pairs and one pair per leaf per split. Shared targets cannot multiply assets; acceptable-variant pairs are both permitted. Resolve FRC-008/009/020/021.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-051 — Retention and revocation

Approve actual retention, purpose limits and rights revocation triggers; resolve FRC-010 immutable audit/reference versus erasure/tombstone behavior. Choose what permitted metadata remains and what personal/source content must disappear.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

### GAP-052 — Limits and costs

Approve proposed spend, concurrency, request and import resource defaults. Complete FRC-012 full per-operation budgets/reservations and FRC-017 inert archive member accounting. Unknown provider charges cannot be recorded as zero.

**Needed:** an explicit scoped choice, and qualified linguistic approval where the rule changes language judgments; actual review/consent records remain separate from that choice.

## Every original gap, reconciled

“Supplied” below means a written definition now exists. It does not mean code implements it. Earlier missing-file descriptions remain in gap-reconciliation.json under existing_gap_detail for provenance and must not be read as current absence claims.

### GAP-001 — Complete product and internal API operation contracts

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-001`.

**Now supplied:** `specification/v2/contracts/openapi.yaml`, `specification/v2/domain/operations.yaml`, `specification/v2/docs/interface-contract.md`.

**Remaining definition (FRC-006):** For each flagged operation supply a field-by-field input/server/import/precondition classification and separate creation DTO where necessary. Define actual reservation or direct server assignment without inventing source dates, person identity or approval. See operation-field-ownership.json.

**Positive acceptance:** The local operator uses a listed preparation or teacher action. The response uses its named schema, status, and atomic effect.

**Negative acceptance:** An operation has an unknown field, stale revision, or unknown action. The API returns the declared error without a partial successful result.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-002 — Public and private transport projections

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-002`.

**Now supplied:** `specification/v2/contracts/library-item.schema.json`, `specification/v2/contracts/teacher-start-view.schema.json`, `specification/v2/contracts/prepare-view.schema.json`, `specification/v2/contracts/key-disclosure.schema.json`, `specification/v2/docs/interface-contract.md`.

**Remaining choice:** Allow key disclosure only after submission, on the exact case version, through the teacher-safe projection; keep blind reviewer disclosure as a separately recorded phase. Choose whether teachers may request that disclosure at all and its intended timing. Private approvals, evidence and person identities stay private.

**Positive acceptance:** A frozen submitted attempt requests its result. The response can show the exact full key under the selected disclosure policy.

**Negative acceptance:** An unsubmitted attempt or blind review requests a hidden field. The serializer omits it from payloads, errors, and media metadata.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-003 — Complete persistent entity and constraint model

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-003`.

**Now supplied:** `specification/v2/db/schema.sql`, `specification/v2/domain/persistence-map.json`, `specification/v2/docs/persistence.md`.

**Remaining definition (FRC-006):** For each flagged operation supply a field-by-field input/server/import/precondition classification and separate creation DTO where necessary. Define actual reservation or direct server assignment without inventing source dates, person identity or approval. See operation-field-ownership.json.

**Remaining definition (FRC-010):** Supply the exact write privileges/trigger and maintenance erasure/tombstone procedure, reference closure, permitted audit retention and immutable case-version identity constraints. The SQL is a design reference until these definitions are consistent. Inspect actual SQL in PostgreSQL after implementation authorization.

**Positive acceptance:** A new domain document and its reference nodes commit. Its head, references, and audit event share one database transaction.

**Negative acceptance:** A reference points to another case or missing document. The operation cannot commit a healthy record.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-004 — Database and object-store commit protocol

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-004`.

**Now supplied:** `specification/v2/contracts/asset.schema.json`, `specification/v2/docs/runtime-and-storage.md`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** Upload and read-back agree. The final owning transaction links the private immutable asset.

**Negative acceptance:** The process stops between upload and link. Recovery reports an orphan or pending reservation and never publishes missing bytes.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-007 — Case lifecycle transition and guard table

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-007`.

**Now supplied:** `specification/v2/docs/lifecycle.md`, `specification/v2/contracts/case-head.schema.json`, `specification/v2/contracts/transition-request.schema.json`.

**Remaining choice:** Select the supplied draft/review/approved/published/retracted transition guards, required resolved final-audio reviews, and retraction/republication behavior. Confirm whether two final approvals after adjudication are required; models cannot supply them.

**Positive acceptance:** A verified case has matching final approvals and valid grants. Publication commits the same content and audio digests.

**Negative acceptance:** A quarantined case is retired. The unresolved quarantine flag remains and final evaluation stays blocked.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-008 — Attempt and evaluation recovery transition table

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-008`.

**Now supplied:** `specification/v2/contracts/attempt.schema.json`, `specification/v2/docs/lifecycle.md`, `specification/v2/docs/runtime-and-storage.md`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** An expired evaluation receives explicit recovery. The epoch increases and the exact answer, case, and policy stay fixed.

**Negative acceptance:** A delayed provider response arrives under a stale epoch or after the deadline. The result is retained as failed evidence and cannot become final.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-009 — Dispute and adjudicated result revision records

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-009`.

**Now supplied:** `specification/v2/contracts/dispute.schema.json`, `specification/v2/contracts/adjudication.schema.json`, `specification/v2/contracts/unit-correspondence.schema.json`, `specification/v2/contracts/result-revision.schema.json`, `specification/v2/docs/lifecycle.md`.

**Remaining choice:** Select the supplied immutable dispute/adjudication/unit-correspondence/result-revision approach and whether results may be reconsidered under a new key. Specify user-visible historical versus revised results and the approved correspondence/recompute trigger.

**Positive acceptance:** The operator selects affected historical attempts after a reviewed key correction. New revisions use an explicit old-to-new unit map.

**Negative acceptance:** A replacement recording differs from the heard asset. The application cannot rescore the old listening attempt as though that recording was heard.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-010 — Independent blind-listening annotation contract

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-010`.

**Now supplied:** `specification/v2/contracts/blind-annotation.schema.json`, `specification/v2/contracts/review-context.schema.json`, `specification/v2/contracts/disclosure-record.schema.json`, `specification/v2/docs/review-and-gold.md`.

**Remaining definition (FRC-006):** For each flagged operation supply a field-by-field input/server/import/precondition classification and separate creation DTO where necessary. Define actual reservation or direct server assignment without inventing source dates, person identity or approval. See operation-field-ownership.json.

**Positive acceptance:** A genuine reviewer submits observations. Their hash and time freeze before key correspondence becomes available.

**Negative acceptance:** The reviewer already saw the key or changes a submitted observation. The evidence cannot count as an original independent blind annotation.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-011 — Reviewer independence and qualification records

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-011`.

**Now supplied:** `specification/v2/contracts/person.schema.json`, `specification/v2/contracts/qualification.schema.json`, `specification/v2/contracts/review-decision.schema.json`, `specification/v2/docs/review-and-gold.md`.

**Remaining choice:** Approve acceptable actual qualification/competence evidence, phonetics competence for acoustic cases, per-review conflict re-attestation, two distinct non-author reviewers, and a third qualified adjudicator for disagreement. Names or accounts alone cannot establish independence.

**Positive acceptance:** Two eligible people independently review final audio and resolve findings. Their actual final approvals can satisfy the human gate.

**Negative acceptance:** Two names describe one person, competence is unsupported, or the author reviews their own case. Publication cannot count those records as independent approvals.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-012 — Teacher-answer gold annotation data contract

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-012`.

**Now supplied:** `specification/v2/contracts/teacher-gold.schema.json`, `specification/v2/docs/review-and-gold.md`, `specification/v2/docs/splits-and-validation.md`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** Annotators label a real frozen answer before model output. Their original labels and final correspondence remain separate.

**Negative acceptance:** A generated answer or model-derived label is presented as independent human gold. It cannot satisfy heldout evidence.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-013 — Detection-event boundaries and overlapping category resolution

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-013`.

**Now supplied:** `specification/v2/docs/math-and-judgments.md`, `specification/v2/domain/error-taxonomy.v1.yaml`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** Two repairs share a span but either repair leaves the other defect. The reviewed key retains two independent units with the rationale.

**Negative acceptance:** Two labels describe the same repair or equally supported primary domains remain unresolved. The application cannot inflate opportunities or choose a primary domain arbitrarily.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-014 — Frozen English/Russian aliases and taxonomy ancestors

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-014`.

**Now supplied:** `specification/v2/domain/category-aliases.v1.yaml`, `specification/v2/docs/math-and-judgments.md`.

**Remaining choice:** Review and approve every English/Russian alias and exact taxonomy ancestor binding in category-aliases.v1.yaml. A generated bilingual label is not linguistic equivalence; unknown/ambiguous aliases remain abstentions. The complete original taxonomy is preserved.

**Positive acceptance:** The teacher supplies one registered unambiguous term. The mapper uses that exact ancestor or leaf identity.

**Negative acceptance:** A term maps to multiple entries or a different registry version. The affected category decision remains unresolved.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-015 — Severity assignment and fixed weight binding

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-015`.

**Now supplied:** `specification/v2/domain/judgment-policy.yaml`, `specification/v2/docs/review-and-gold.md`, `specification/v2/docs/scoring-v1.md`.

**Remaining choice:** Approve the proposed severity assignment and fixed 1–4 weight binding with reviewed rationale/evidence. Separate severity from learner proficiency, rated difficulty and detection credit. Do not infer it from a corpus score.

**Positive acceptance:** Reviewers justify the context-specific severity under the fixed rubric. The immutable case records the corresponding weight.

**Negative acceptance:** An evaluator changes weight after it sees an answer. The score input fails the fixed-policy guard.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-016 — Rated difficulty evidence protocol

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-016`.

**Now supplied:** `specification/v2/contracts/difficulty-study.schema.json`, `specification/v2/docs/review-and-gold.md`.

**Remaining choice:** Approve the proposed >=100 independent first-exposure participant floor, Wilson interval bands, unit success versus exercise composite >=80, and unrated boundary. These are candidate thresholds, not established teacher norms.

**Positive acceptance:** The complete study evidence meets the frozen band rule. The display cites that study and its population.

**Negative acceptance:** The interval crosses bands or the sample is insufficient. The application keeps unrated and does not substitute author intuition or learner CEFR.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-017 — Variety, register and judgment consistency table

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-017`.

**Now supplied:** `specification/v2/domain/judgment-policy.yaml`, `specification/v2/docs/review-and-gold.md`.

**Remaining definition (FRC-020):** Define the exact gate-by-domain/component applicability matrix. State whether correction precision is required only for genuine correction-opportunity domains and supply a separate zero-credit/overcorrection control gate. Preserve all domains and existing thresholds; any correction to applicability must be an explicit policy decision rather than silently treating no eligible data as passing.

**Remaining choice:** Approve contextual error/acceptable-variant/uncertain judgments, allowed corrections and exclusions for all leaves and public variety/register/task context. Resolve FRC-020 control-domain gate applicability without relabeling permitted variants as errors.

**Positive acceptance:** The public task establishes the relevant constraint and reviewers support the target judgment. The unit can enter the declared error population.

**Negative acceptance:** The only basis is a hidden accent preference or an incompatible context label. The case cannot publish that unit as a true error.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-018 — Claim identity, extraction partition and completeness

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-018`.

**Now supplied:** `specification/v2/contracts/claim-extraction.schema.json`, `specification/v2/docs/math-and-judgments.md`, `specification/v2/reference/validators_v2.py`.

**Remaining definition (FRC-018):** Define the exact deterministic normalization-plus-mapping to scoring-input projection: retracted/ignored members, representative identity, merged source spans, category consistency, reviewed equivalent alternatives, satisfied/forbidden proposition aggregation, FP unnecessary-correction counts, unresolved groups and raw duplicate telemetry. Preserve all actual source claims and apply each independent event once. Resolve material interpretation choices with linguistic policy, not arithmetic fixtures.

**Positive acceptance:** All exact spans and coverage cells agree with the frozen answer. The server assigns reproducible persistent identities.

**Negative acceptance:** A source quote is fabricated, an assertion is omitted, or identical spans carry conflicting interpretations. The extraction cannot enter completed scoring.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-019 — Fragment consolidation, duplicate and retraction normalization

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-019`.

**Now supplied:** `specification/v2/contracts/normalization.schema.json`, `specification/v2/docs/math-and-judgments.md`.

**Remaining definition (FRC-018):** Define the exact deterministic normalization-plus-mapping to scoring-input projection: retracted/ignored members, representative identity, merged source spans, category consistency, reviewed equivalent alternatives, satisfied/forbidden proposition aggregation, FP unnecessary-correction counts, unresolved groups and raw duplicate telemetry. Preserve all actual source claims and apply each independent event once. Resolve material interpretation choices with linguistic policy, not arithmetic fixtures.

**Positive acceptance:** A later explicit retraction withdraws an earlier assertion. The final endorsed group retains both clauses and the retraction evidence.

**Negative acceptance:** Two unretracted repairs conflict or a relation forms a cycle. The group requires review rather than best-of or last-write credit.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-020 — Evaluator and cross-schema conditional truth tables

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-020`.

**Now supplied:** `specification/v2/docs/cross-field-invariants.md`, `specification/v2/domain/semantic-invariants.yaml`, `specification/v2/reference/validators_v2.py`.

**Remaining definition (FRC-018):** Define the exact deterministic normalization-plus-mapping to scoring-input projection: retracted/ignored members, representative identity, merged source spans, category consistency, reviewed equivalent alternatives, satisfied/forbidden proposition aggregation, FP unnecessary-correction counts, unresolved groups and raw duplicate telemetry. Preserve all actual source claims and apply each independent event once. Resolve material interpretation choices with linguistic policy, not arithmetic fixtures.

**Positive acceptance:** A supplied correction, selected option, proposition sets, and verdict agree with the same source and unit. The tuple enters normalization.

**Negative acceptance:** A model reports accepted credit without supplied text, a foreign proposition, or an unresolved component in a resolved decision. The application rejects the tuple.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-021 — Approved rationale registry and explanation-null binding

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-021`.

**Now supplied:** `specification/v2/contracts/rationale.schema.json`, `specification/v2/contracts/evaluator-output.schema.json`, `specification/v2/docs/math-and-judgments.md`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** A rationale ID resolves to the reviewed language-specific unit record. Feedback can cite its exact text.

**Negative acceptance:** A correction option is used as an explanation option or the rationale belongs to another language/version. The reference is rejected.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-022 — Semantic decisions to deterministic rubric and scorer input

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-022`.

**Now supplied:** `specification/v2/docs/math-and-judgments.md`, `specification/v2/contracts/scoring-input.schema.json`, `specification/v2/reference/validators_v2.py`, `specification/v2/reference/scorer.py`.

**Remaining definition (FRC-018):** Define the exact deterministic normalization-plus-mapping to scoring-input projection: retracted/ignored members, representative identity, merged source spans, category consistency, reviewed equivalent alternatives, satisfied/forbidden proposition aggregation, FP unnecessary-correction counts, unresolved groups and raw duplicate telemetry. Preserve all actual source claims and apply each independent event once. Resolve material interpretation choices with linguistic policy, not arithmetic fixtures.

**Positive acceptance:** Required proposition findings resolve without forbidden assertions. Code calculates the exact satisfied-count fraction.

**Negative acceptance:** A supplied response includes a forbidden assertion or a plausible novel alternative. The first receives zero under the fixed rubric; the second requires review.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-023 — Mapper/auditor comparison equality contract

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-023`.

**Now supplied:** `specification/v2/docs/math-and-judgments.md`, `specification/v2/contracts/mapping-input.schema.json`, `specification/v2/prompts/audit-map-v1.txt`.

**Remaining definition (FRC-018):** Define the exact deterministic normalization-plus-mapping to scoring-input projection: retracted/ignored members, representative identity, merged source spans, category consistency, reviewed equivalent alternatives, satisfied/forbidden proposition aggregation, FP unnecessary-correction counts, unresolved groups and raw duplicate telemetry. Preserve all actual source claims and apply each independent event once. Resolve material interpretation choices with linguistic policy, not arithmetic fixtures.

**Positive acceptance:** Record order differs but all score-relevant fields and evidence meanings agree. The difference does not change the score.

**Negative acceptance:** The target, option, proposition credit, stance source, or exclusion differs. The result requires review and both outputs remain stored.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-024 — Exact score transport, composite rational and numeric bounds

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-024`.

**Now supplied:** `specification/v2/contracts/exact-rational.schema.json`, `specification/v2/contracts/score-result.schema.json`, `specification/v2/docs/math-and-judgments.md`, `specification/v2/reference/scorer.py`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** A result crosses Python, JSON, Go, and browser boundaries. Its reduced rational stays identical.

**Negative acceptance:** A number overflows, a denominator is zero, or a rounded display is submitted as the exact value. The numeric contract rejects it or uses the declared unavailable state.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-025 — Auxiliary and provisional result response contracts

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-025`.

**Now supplied:** `specification/v2/contracts/auxiliary-results.schema.json`, `specification/v2/contracts/result-envelope.schema.json`, `specification/v2/domain/metrics.v1.yaml`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** An observable auxiliary measure has a genuine method and source intervals. The response includes the measure with its actual evidence.

**Negative acceptance:** Teacher speech is unobserved or a semantic decision is pending. The corresponding field stays unavailable and no final aggregate or invented zero appears.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-026 — Grounded bilingual feedback and missed-unit references

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-026`.

**Now supplied:** `specification/v2/contracts/feedback.schema.json`, `specification/v2/contracts/feedback-output.schema.json`, `specification/v2/prompts/feedback-v1.txt`, `specification/v2/docs/interface-contract.md`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** A missed unit has no teacher claim. Its feedback references the real key unit and approved rationale without inventing a claim ID.

**Negative acceptance:** A generated explanation introduces a new correction, score, or unsupported observation. It cannot appear as confirmed feedback.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-027 — Feedback-only failure versus evaluation-failure outcome

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-027`.

**Now supplied:** `specification/v2/docs/lifecycle.md`, `specification/v2/contracts/result-envelope.schema.json`, `specification/v2/contracts/retry-request.schema.json`.

**Remaining choice:** Confirm that a successful deterministic evaluation with feedback-only failure retains its score and exposes feedback_unavailable with a separate feedback retry. Confirm exact user-facing retry/invalidation behavior; no score recomputation merely to regenerate prose.

**Positive acceptance:** The final feedback call times out after a valid score commit. An explicit feedback retry uses the same score and cannot re-map claims.

**Negative acceptance:** The mapper fails. The feedback exception cannot promote that attempt to a completed score.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-028 — Linguistic audit role prompt, schema and decisions

**Current status:** `policy_proposal_requires_explicit_decision_before_activation`. **OpenSpec:** `SPEC-028`.

**Now supplied:** `specification/v2/contracts/linguistic-audit-input.schema.json`, `specification/v2/contracts/linguistic-audit.schema.json`, `specification/v2/prompts/linguistic-audit-v1.txt`.

**Remaining choice:** Approve the supplied advisory audit role, scope and prompt. Decide which disagreements block preparation and require actual human resolution. Audit/model prose is never a human approval or a replacement for blind final-audio review.

**Positive acceptance:** The candidate contains an apparent untracked textual issue. The audit references its exact subject and span for human review.

**Negative acceptance:** The audit claims a heard phone from planned SSML or reports missing input as no_findings. The output fails its authority and status rules.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-029 — Complete role input and configuration binding schemas

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-029`.

**Now supplied:** `specification/v2/contracts/effective-binding.schema.json`, `specification/v2/contracts/provider-receipt.schema.json`, `specification/v2/contracts/stage-cache.schema.json`, `specification/v2/contracts/taxonomy-context.schema.json`, `specification/v2/prompts/manifest.yaml`.

**Remaining definition (FRC-006):** For each flagged operation supply a field-by-field input/server/import/precondition classification and separate creation DTO where necessary. Define actual reservation or direct server assignment without inventing source dates, person identity or approval. See operation-field-ownership.json.

**Positive acceptance:** The server supplies actual taxonomy definitions and authorized excerpts rather than inaccessible version IDs alone. The stage receipt records that exact payload.

**Negative acceptance:** Blind extraction receives the key, an unknown configuration field enters a stage, or a cache entry belongs to other inputs. The operation is rejected.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-030 — Provider-specific strict-schema projection and response parsing

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-030`.

**Now supplied:** `specification/v2/domain/schema-projection.yaml`, `specification/v2/docs/provider-contracts.md`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** The documented wire projection returns a completed object. Full local schema and semantic checks still run.

**Negative acceptance:** Reasoning text, a refusal, incomplete output, ignored instruction placement, or JSON repair produces plausible text. The adapter cannot treat it as a successful stage.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-031 — Retry, deadline and input/output capacity protocol

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-031`.

**Now supplied:** `specification/v2/docs/runtime-and-storage.md`, `specification/v2/domain/configuration-registry.yaml`.

**Remaining definition (FRC-012):** Define each foreground operation deadline, cancellation/restart, per-call limits, nested-call concurrency admission, full-import atomic/partial boundary and cost profile/reservation state transition. Bind real pricing units/date/recipient; unknown cost is never zero. These are engineering definitions, not requests to execute paid work.

**Positive acceptance:** A retryable transport failure occurs with sufficient reserve and retry budget. One accounted retry can proceed.

**Negative acceptance:** The output is incomplete or the prompt exceeds capacity. The application preserves source input and fails without truncation or semantic retries.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-032 — Typed render operator and hard-capability catalog

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-032`.

**Now supplied:** `specification/v2/contracts/render-constraint.schema.json`, `specification/v2/contracts/render-plan.schema.json`, `specification/v2/domain/audio-methods.yaml`.

**Remaining definition (FRC-009):** Bind every leaf to required supported profile/voice/locale/operator combinations, target/control plan, public context and hard observation criteria. Identify human judgment cases and exact acoustic methods/units where numeric criteria are required. Unsupported combinations remain blockers. No actual canary audio/approval is fabricated.

**Remaining choice:** Approve the typed operator catalog and hard-failure versus advisory distinction. Complete FRC-009 per-target/profile combinations and exact criteria; asking a voice for an accent or prosody does not establish observed realization.

**Positive acceptance:** The typed plan satisfies parameter ranges, scope, and known capability requirements. The compiler can issue the real synthesis call.

**Negative acceptance:** A voice/locale conflicts with a target or a constraint is unknown. The application fails before synthesis instead of dropping the requirement.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-033 — SSML compilation and final-audio assembly specification

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-033`.

**Now supplied:** `specification/v2/docs/audio-methods.md`, `specification/v2/contracts/render-plan.schema.json`, `specification/v2/contracts/transformation.schema.json`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** The compiler escapes literal text and assembles turns with recorded offsets. The delivery hash identifies the reviewed bytes.

**Negative acceptance:** Encoding, normalization, trimming, or a turn order changes after review. Existing approval cannot transfer to that file.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-034 — Audio quality measurement method and boundary rules

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-034`.

**Now supplied:** `specification/v2/docs/audio-methods.md`, `specification/v2/domain/audio-methods.yaml`, `specification/v2/contracts/audio-measurement.schema.json`.

**Remaining definition (FRC-016):** Define versioned FFmpeg resample/ebur128 command options, Praat/binding compatibility constraints, clock conversion and deterministic WER tokenization for both reference/hypothesis, including actual spoken numerals, contractions, fillers and missingness. Preserve separate human judgment and advisory roles.

**Positive acceptance:** The report includes actual finite measurements with their method version and boundary classification.

**Negative acceptance:** The recording is silent, too short, non-finite, or measured on an upstream file. The report cannot approve final audio.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-035 — Speech tokenizer, reviewed intervals and disfluency event rules

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-035`.

**Now supplied:** `specification/v2/docs/audio-methods.md`, `specification/v2/domain/audio-methods.yaml`.

**Remaining definition (FRC-016):** Define versioned FFmpeg resample/ebur128 command options, Praat/binding compatibility constraints, clock conversion and deterministic WER tokenization for both reference/hypothesis, including actual spoken numerals, contractions, fillers and missingness. Preserve separate human judgment and advisory roles.

**Remaining choice:** Approve reviewed token/interval/filler/repetition/repair boundaries and multilingual/apostrophe/numeral rules. Complete FRC-016 deterministic comparison-token normalization for both WER inputs; ASR cannot set human event truth.

**Positive acceptance:** Reviewed token events and interval unions are available. Each numerator and denominator can be recomputed.

**Negative acceptance:** A filler is automatically called an error or overlapping intervals count twice. The measurement is invalid.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-036 — Prosody feature/unit/method and valid missingness table

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-036`.

**Now supplied:** `specification/v2/domain/audio-methods.yaml`, `specification/v2/docs/audio-methods.md`, `specification/v2/contracts/audio-measurement.schema.json`.

**Remaining definition (FRC-009):** Bind every leaf to required supported profile/voice/locale/operator combinations, target/control plan, public context and hard observation criteria. Identify human judgment cases and exact acoustic methods/units where numeric criteria are required. Unsupported combinations remain blockers. No actual canary audio/approval is fabricated.

**Remaining definition (FRC-016):** Define versioned FFmpeg resample/ebur128 command options, Praat/binding compatibility constraints, clock conversion and deterministic WER tokenization for both reference/hypothesis, including actual spoken numerals, contractions, fillers and missingness. Preserve separate human judgment and advisory roles.

**Remaining choice:** Approve feature units, raw-ac method choice and missingness/judgment conditions per target. Complete FRC-009 and FRC-016 exact implementation/qualification bindings; automatic measurements remain advisory unless explicitly reviewed.

**Positive acceptance:** A voiced F0 measurement has sufficient valid frames and the specified reference. The report stores the actual semitone result.

**Negative acceptance:** Unvoiced frames, provider naturalness, or requested settings are used as measured prosody. The observation is rejected or unavailable.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-037 — ASR and pronunciation advisory normalization

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-037`.

**Now supplied:** `specification/v2/docs/audio-methods.md`, `specification/v2/docs/provider-contracts.md`, `specification/v2/contracts/evidence.schema.json`.

**Remaining definition (FRC-016):** Define versioned FFmpeg resample/ebur128 command options, Praat/binding compatibility constraints, clock conversion and deterministic WER tokenization for both reference/hypothesis, including actual spoken numerals, contractions, fillers and missingness. Preserve separate human judgment and advisory roles.

**Positive acceptance:** A pronunciation chunk has its actual source interval, reference slice, offsets, and provider scales. Its evidence stays linked to final bytes.

**Negative acceptance:** A missing or NoMatch field is converted to a perfect score, or a low score becomes a phone substitution. The conversion fails.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-038 — Full synthetic target capability and canary specification

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-038`.

**Now supplied:** `specification/v2/domain/target-capabilities.yaml`, `specification/v2/contracts/capability-record.schema.json`, `specification/v2/docs/audio-methods.md`.

**Remaining definition (FRC-009):** Bind every leaf to required supported profile/voice/locale/operator combinations, target/control plan, public context and hard observation criteria. Identify human judgment cases and exact acoustic methods/units where numeric criteria are required. Unsupported combinations remain blockers. No actual canary audio/approval is fabricated.

**Positive acceptance:** An actual synthesis and two human observations satisfy the target-specific criteria for a fixed profile. That profile can use the qualification.

**Negative acceptance:** A target fails after the bounded render attempts. It remains a full-release blocker and cannot be omitted or replaced silently.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-039 — Full source manifest, legal scope and transformation contracts

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-039`.

**Now supplied:** `specification/v2/contracts/source-release.schema.json`, `specification/v2/contracts/permission-grant.schema.json`, `specification/v2/contracts/import-report.schema.json`, `specification/v2/contracts/transformation.schema.json`, `specification/v2/docs/sources/acquisition-and-rights.md`.

**Remaining definition (FRC-017):** Define full member accounting, fail/quarantine dispositions, preservation location and no-execution handling for official scripts/executable bits. Path/symlink/device/expansion restrictions must remain. A rejected member cannot disappear from full completeness counts.

**Remaining definition (FRC-019):** Select the project software license and attribution/copyright owner; specify separate license/consent/redistribution terms for original reviewed audio, taxonomy content and any shipped bank. MIT or Apache-2.0 can be proposed, but this review does not grant author rights or publish a license. Preserve third-party attribution and exclude unlicensed/NC/private corpus data from public source distribution.

**Remaining definition (FRC-021):** Choose and document the first-run content contract: include a genuinely reviewed redistributable original bank (with exact permitted audio/key/review provenance) or explicitly document an initially empty workspace and preparation/review requirements. Specify how real bundled content is imported and validated without creating fake approvals or automatic network corpus acquisition. Keep project full-source research/qualification gates distinct from each installation’s usable-content checks.

**Positive acceptance:** The imported release matches every required component and permitted use. Its raw and normalized identities remain traceable.

**Negative acceptance:** Only a sample is acquired or an external transfer lacks permission. The source cannot satisfy full acquisition or the proposed transfer.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-040 — Complete SpeechOcean762 parser and source scale profile

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-040`.

**Now supplied:** `specification/v2/docs/sources/speechocean762.md`, `specification/v2/contracts/raw-record.schema.json`, `specification/v2/domain/phone-symbols.yaml`.

**Remaining definition (FRC-017):** Define full member accounting, fail/quarantine dispositions, preservation location and no-execution handling for official scripts/executable bits. Path/symlink/device/expansion restrictions must remain. A rejected member cannot disappear from full completeness counts.

**Positive acceptance:** All supplied components reconcile and original score layers remain independent.

**Negative acceptance:** An importer drops child metadata, mixes scales, or guesses a phone from low accuracy. It cannot pass faithful full import.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-041 — Complete L2-ARCTIC v5 read and suitcase parser profile

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-041`.

**Now supplied:** `specification/v2/docs/sources/l2-arctic-v5.md`, `specification/v2/contracts/raw-record.schema.json`, `specification/v2/domain/phone-symbols.yaml`.

**Remaining definition (FRC-017):** Define full member accounting, fail/quarantine dispositions, preservation location and no-execution handling for official scripts/executable bits. Path/symlink/device/expansion restrictions must remain. A rejected member cannot disappear from full completeness counts.

**Positive acceptance:** The read and suitcase inventories match the actual source release and retain CPL/PPL/edit labels.

**Negative acceptance:** Automatic alignments or uncertain err markers are converted into manual narrow-label gold. The conversion cannot be accepted.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-042 — Complete W&I+LOCNESS and FCE v2.1 M2 parser profiles

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-042`.

**Now supplied:** `specification/v2/docs/sources/bea-v21.md`, `specification/v2/domain/source-label-map.yaml`, `specification/v2/contracts/raw-record.schema.json`.

**Remaining definition (FRC-017):** Define full member accounting, fail/quarantine dispositions, preservation location and no-execution handling for official scripts/executable bits. Path/symlink/device/expansion restrictions must remain. A rejected member cannot disappear from full completeness counts.

**Positive acceptance:** One original annotator layer is normalized without merging alternative edits. Raw tokens and labels remain recoverable.

**Negative acceptance:** The importer invents learner IDs, missing test labels, or an unsupported exact leaf mapping. The record remains unbound rather than invented gold.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-043 — EFCAMDAT full release and derivative ingest scope

**Current status:** `external_contract_missing`. **OpenSpec:** `SPEC-043`.

**Now supplied:** `specification/v2/docs/sources/efcamdat.md`, `specification/v2/domain/corpus-sources.v1.yaml`, `specification/v2/contracts/source-format-binding.schema.json`.

**Missing external contract:** Required input: separately authorized complete EFCAMDAT R2 XML, Shatz2020 and Öksüz2025 release identifiers and documentation; actual accepted agreements for the intended use/recipient/redistribution; complete XML element/attribute/mixed-content semantics and source byte-to-text offset projection; every derivative workbook/sheet/header/raw type/null marker/label/offset and task/learner/writing relationship; partition/member/count expectations and derivative links. The supplied guide/schema scaffold does not supply private workbook headers. All three are in the draft inventory; a derivative is not a substitute. Access permission is separate from schema definition.

**Positive acceptance:** The operator supplies authorized source files, real documentation, and matching mappings for each release. Full ingestion reconciles them separately.

**Negative acceptance:** Workbook headers, labels, or rights remain unavailable. A generic schema or a cleaned subset cannot falsely satisfy the missing native release contract.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-044 — Doubao underlying study-record release contract

**Current status:** `external_contract_missing`. **OpenSpec:** `SPEC-044`.

**Now supplied:** `specification/v2/docs/sources/private-vendors-and-study.md`, `specification/v2/contracts/source-release.schema.json`, `specification/v2/domain/corpus-sources.v1.yaml`.

**Missing external contract:** Required input: the actual author-authorized Doubao study-record release or a direct decision to keep it unavailable/research-only; all participant recording/video/audio/transcript/annotation components, exact release/member/participant/session IDs and counts, dictionary and instruments/scales, recording/annotation clocks, sampling/exclusion protocol, grouping and consent/use/provider-transfer/redistribution grants. Establish what the reported 545 describes. The publication is not 545 acquired or annotated corpus items.

**Positive acceptance:** An authorized complete release identifies its files, participant groups, annotation format, and permitted uses. It can enter the normal import protocol.

**Negative acceptance:** Only the paper and sample counts exist. Record access remains unavailable and the full-source obligation is not reported complete.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-045 — Moodrick and NIR vendor-data scope and contracts

**Current status:** `external_contract_missing`. **OpenSpec:** `SPEC-045`.

**Now supplied:** `specification/v2/docs/sources/private-vendors-and-study.md`, `specification/v2/contracts/connector-configuration.schema.json`, `specification/v2/contracts/source-format-binding.schema.json`.

**Missing external contract:** Required input separately for Moodrick and NIR: actual authorized complete release/export or native API contract, version, all bank/prompt/rubric/transcript/answer/session/review/score components, exact schemas/field units/nullable meanings, pagination/rate limits/export completeness, revision/record/participant/group IDs, documented auth only for optional acquisition, and actual grants for use/derivatives/provider transfer/redistribution. Public simulator pages do not supply these. If comparison-only is chosen, keep full-acquisition acceptance unresolved or explicitly revise scope; never claim equivalent corpus coverage.

**Positive acceptance:** A real authorized export or documented API contract is supplied with the appropriate credential reference. The source uses only its permitted operations.

**Negative acceptance:** Only public descriptions or a key exist without an authorized interface and release. No private answer bank, endpoint, or source asset is invented.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-046 — Leakage grouping, split allocation and duplicate protocol

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-046`.

**Now supplied:** `specification/v2/docs/splits-and-validation.md`, `specification/v2/contracts/split-manifest.schema.json`.

**Remaining definition (FRC-008):** Choose and document distinct genuine learner/speaker, synthetic character, provider voice, prompt and participant grouping axes; define which are strict held-out axes and how global IDs are assigned. Provide feasible full-scope allocation or report impossibility; do not cut real leakage edges.

**Remaining choice:** Approve strict grouping axes, 60/20/20 allocation and complete pair-family retention. Resolve FRC-008 synthetic voice versus genuine speaker/character grouping and demonstrate feasible complete-leaf allocation without cutting leakage edges.

**Positive acceptance:** Independent connected components admit the chosen allocation. The frozen manifest records every member and seed.

**Negative acceptance:** Shared prompts create one giant connected component. The procedure reports insufficient independent groups rather than weakening leakage boundaries.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-047 — Gold stimulus, asset and negative-control counting

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-047`.

**Now supplied:** `specification/v2/docs/review-and-gold.md`, `specification/v2/domain/validation-policy.yaml`.

**Remaining definition (FRC-008):** Choose and document distinct genuine learner/speaker, synthetic character, provider voice, prompt and participant grouping axes; define which are strict held-out axes and how global IDs are assigned. Provide feasible full-scope allocation or report impossibility; do not cut real leakage edges.

**Remaining definition (FRC-009):** Bind every leaf to required supported profile/voice/locale/operator combinations, target/control plan, public context and hard observation criteria. Identify human judgment cases and exact acoustic methods/units where numeric criteria are required. Unsupported combinations remain blockers. No actual canary audio/approval is fabricated.

**Remaining definition (FRC-020):** Define the exact gate-by-domain/component applicability matrix. State whether correction precision is required only for genuine correction-opportunity domains and supply a separate zero-credit/overcorrection control gate. Preserve all domains and existing thresholds; any correction to applicability must be an explicit policy decision rather than silently treating no eligible data as passing.

**Remaining definition (FRC-021):** Choose and document the first-run content contract: include a genuinely reviewed redistributable original bank (with exact permitted audio/key/review provenance) or explicitly document an initially empty workspace and preparation/review requirements. Specify how real bundled content is imported and validated without creating fake approvals or automatic network corpus acquisition. Keep project full-source research/qualification gates distinct from each installation’s usable-content checks.

**Remaining choice:** Approve six distinct stimuli per leaf, >=732 distinct stimuli overall, matched target/control pairs and one pair per leaf per split. Shared targets cannot multiply assets; acceptable-variant pairs are both permitted. Resolve FRC-008/009/020/021.

**Positive acceptance:** Each leaf has three independent contrast-pair families, one per split, with actual final-audio review.

**Negative acceptance:** One multi-target file is counted as many independent stimuli or an acceptable variant is labeled erroneous to meet the count. Coverage fails.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-048 — Agreement and semantic evaluation denominator protocols

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-048`.

**Now supplied:** `specification/v2/docs/math-and-judgments.md`, `specification/v2/docs/splits-and-validation.md`, `specification/v2/contracts/holdout-report.schema.json`.

**Remaining definition (FRC-015):** Specify immutable gold event/claim alignment IDs, treatment of unmatched/spurious/omitted decisions for every statistic, and each critical case’s exact expected semantic outcome and source. The cases themselves require real or separately authorized evidence. Do not invent teacher answers to fill them.

**Remaining definition (FRC-020):** Define the exact gate-by-domain/component applicability matrix. State whether correction precision is required only for genuine correction-opportunity domains and supply a separate zero-credit/overcorrection control gate. Preserve all domains and existing thresholds; any correction to applicability must be an explicit policy decision rather than silently treating no eligible data as passing.

**Positive acceptance:** The same independent rater pair labels aligned events. Raw marginals define agreement and kappa.

**Negative acceptance:** Adjudicated unanimity replaces the original labels or abstentions disappear from coverage. The reported statistic cannot pass.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-049 — Elapsed attempt start and validated playback event contracts

**Current status:** `written_definition_supplied_not_runtime_accepted`. **OpenSpec:** `SPEC-049`.

**Now supplied:** `specification/v2/contracts/attempt.schema.json`, `specification/v2/contracts/playback-event.schema.json`, `specification/v2/docs/interface-contract.md`.

No additional missing written definition identified in this pass. Implementation, actual permitted data/reviews and empirical qualification are still unobserved; this is not an acceptance pass.

**Positive acceptance:** A repeated event ID arrives with the same payload. It is accepted idempotently and does not add another play.

**Negative acceptance:** A client supplies another asset, an impossible time, or a changed payload under the same event ID. It cannot affect telemetry or ability scores.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-050 — Complete heldout acceptance protocol and critical cases

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-050`.

**Now supplied:** `specification/v2/docs/splits-and-validation.md`, `specification/v2/domain/validation-policy.yaml`, `specification/v2/contracts/holdout-report.schema.json`.

**Remaining definition (FRC-015):** Specify immutable gold event/claim alignment IDs, treatment of unmatched/spurious/omitted decisions for every statistic, and each critical case’s exact expected semantic outcome and source. The cases themselves require real or separately authorized evidence. Do not invent teacher answers to fill them.

**Remaining definition (FRC-020):** Define the exact gate-by-domain/component applicability matrix. State whether correction precision is required only for genuine correction-opportunity domains and supply a separate zero-credit/overcorrection control gate. Preserve all domains and existing thresholds; any correction to applicability must be an explicit policy decision rather than silently treating no eligible data as passing.

**Positive acceptance:** Every domain satisfies the fixed sample and metric gates using untouched holdout evidence. The report cites actual manifests and receipts.

**Negative acceptance:** The holdout is exposed, a domain is too small, or a critical case fails. Overall averages cannot hide the failed gate.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-051 — Retention, deletion and permission revocation lifecycle

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-051`.

**Now supplied:** `specification/v2/docs/maintenance-and-limits.md`, `specification/v2/contracts/deletion-request.schema.json`.

**Remaining definition (FRC-010):** Supply the exact write privileges/trigger and maintenance erasure/tombstone procedure, reference closure, permitted audit retention and immutable case-version identity constraints. The SQL is a design reference until these definitions are consistent. Inspect actual SQL in PostgreSQL after implementation authorization.

**Remaining choice:** Approve actual retention, purpose limits and rights revocation triggers; resolve FRC-010 immutable audit/reference versus erasure/tombstone behavior. Choose what permitted metadata remains and what personal/source content must disappear.

**Positive acceptance:** A confirmed erasure plan removes restricted bytes and preserves only expressly permitted tombstones.

**Negative acceptance:** A backup would restore revoked active content. Restore must reapply the revocation/deletion ledger before serving it.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-052 — Request quotas, concurrency, costs and import resource bounds

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-052`.

**Now supplied:** `specification/v2/domain/configuration-registry.yaml`, `specification/v2/contracts/configuration.schema.json`, `specification/v2/docs/maintenance-and-limits.md`.

**Remaining definition (FRC-012):** Define each foreground operation deadline, cancellation/restart, per-call limits, nested-call concurrency admission, full-import atomic/partial boundary and cost profile/reservation state transition. Bind real pricing units/date/recipient; unknown cost is never zero. These are engineering definitions, not requests to execute paid work.

**Remaining definition (FRC-017):** Define full member accounting, fail/quarantine dispositions, preservation location and no-execution handling for official scripts/executable bits. Path/symlink/device/expansion restrictions must remain. A rejected member cannot disappear from full completeness counts.

**Remaining choice:** Approve proposed spend, concurrency, request and import resource defaults. Complete FRC-012 full per-operation budgets/reservations and FRC-017 inert archive member accounting. Unknown provider charges cannot be recorded as zero.

**Positive acceptance:** A request fits the exact limits and has a known accounted price bound. One expensive foreground operation is admitted.

**Negative acceptance:** Unknown charge exposure, excessive decompression, or an exhausted budget violates admission. The operation fails rather than truncating required content.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-053 — Backup/restore consistency and compatibility protocol

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-053`.

**Now supplied:** `specification/v2/contracts/backup-manifest.schema.json`, `specification/v2/docs/maintenance-and-limits.md`.

**Remaining definition (FRC-010):** Supply the exact write privileges/trigger and maintenance erasure/tombstone procedure, reference closure, permitted audit retention and immutable case-version identity constraints. The SQL is a design reference until these definitions are consistent. Inspect actual SQL in PostgreSQL after implementation authorization.

**Positive acceptance:** A complete verified backup restores into an inactive target and passes reference checks before activation.

**Negative acceptance:** A component is missing, a digest fails, or a schema is incompatible. The original workspace remains active and no partial restore reports success.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-054 — Basic GitHub download-and-run setup

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-054`.

**Now supplied:** `specification/v2/docs/local-delivery.md`, `specification/v2/domain/configuration-registry.yaml`, `specification/v2/contracts/configuration.schema.json`.

**Remaining definition (FRC-019):** Select the project software license and attribution/copyright owner; specify separate license/consent/redistribution terms for original reviewed audio, taxonomy content and any shipped bank. MIT or Apache-2.0 can be proposed, but this review does not grant author rights or publish a license. Preserve third-party attribution and exclude unlicensed/NC/private corpus data from public source distribution.

**Remaining definition (FRC-021):** Choose and document the first-run content contract: include a genuinely reviewed redistributable original bank (with exact permitted audio/key/review provenance) or explicitly document an initially empty workspace and preparation/review requirements. Specify how real bundled content is imported and validated without creating fake approvals or automatic network corpus acquisition. Keep project full-source research/qualification gates distinct from each installation’s usable-content checks.

**Positive acceptance:** A qualified release starts the real stack on loopback with persistent data and no account setup.

**Negative acceptance:** Images are missing, a secret is exposed, or an architecture lacks qualification. The launcher cannot claim a completed first release.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

### GAP-055 — Specification authority, version compatibility and drift closure

**Current status:** `definition_incomplete_after_recheck`. **OpenSpec:** `SPEC-055`.

**Now supplied:** `specification/v2/docs/authority.md`, `audit/full-release-reconciliation-20261008/import-manifest.json`, `specification/v2/domain/version-compatibility.yaml`, `specification/v2/README.md`, `specification/v2/docs/migration-compatibility.md`, `audit/full-release-reconciliation-20261008/repository-drift.md`.

**Remaining definition (FRC-010):** Supply the exact write privileges/trigger and maintenance erasure/tombstone procedure, reference closure, permitted audit retention and immutable case-version identity constraints. The SQL is a design reference until these definitions are consistent. Inspect actual SQL in PostgreSQL after implementation authorization.

**Positive acceptance:** An implementer compares the supplied package against the real current checkout and records every accepted migration or conflict.

**Negative acceptance:** Historical account requirements reappear or a structural count substitutes for semantic integration evidence. The integration gate remains blocked.

**Implementation/evidence:** not performed by this increment; unresolved definitions or decisions block the dependent acceptance.

## What can and cannot close these entries

Engineering can complete DTO ownership, deterministic projection, migration/erasure, budgets, exact audio bindings and inert member accounting without asking for permission to implement. This task authorizes only their specification. Product choices and actual linguistic/rights grants must come from the appropriate owner. External private formats require actual documentation; public metadata is insufficient. Written completeness is separate from live provider, real gold, source acquisition and runtime acceptance. Those later activities were not performed or authorized by this spec-only increment.
