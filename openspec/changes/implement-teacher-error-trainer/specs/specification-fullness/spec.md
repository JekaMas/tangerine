## ADDED Requirements

The current user request requires complete definitions, not another implementation increment. These obligations track the historical findings in audit/spec-fullness-20261008/GAPS.md under the current local scope in docs/simple-local-product.md and audit/simple-local-20261008/gap-disposition.json. GAP-005/006 are superseded design choices, not open account/role requirements. They preserve original taxonomy IDs, formulas, source bytes and genuine decision/evidence boundaries. Engineering may draft complete contracts; unprovided product/linguistic/source-owner choices stay explicit. A listed closure obligation is not a completed definition or implemented test.

### Requirement: SPEC-001 Complete product and internal API operation contracts
The specification SHALL close GAP-001 with an exact versioned definition of the following: No complete method/path/operation inventory or transport contract defines request bodies, response bodies, headers, revision preconditions, pagination, idempotency scope, or errors for local preparation/review/publication/disputes/import/settings/speech operations. The definition SHALL preserve these existing rules: Minimal internal UI/service contracts, selected submission statuses and private media are required; no public API, account endpoints or tenant transport is required; domain schemas are supplied. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-001 Complete definition and rejection boundary
- **GIVEN** The exact GAP-001 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every in-scope operation has one versioned request/response/security/error contract and links to its flow and owner. An omitted operation, undefined payload/status or unbound route prevents an API-complete claim.

### Requirement: SPEC-002 Public and private transport projections
The specification SHALL close GAP-002 with an exact versioned definition of the following: No field allowlists define library, exercise-start, media, pre-key review, post-key review, attempt, result, dispute, preparation and local settings views. Post-submit key visibility and historical/quarantined views are not fully defined. The definition SHALL preserve these existing rules: Pre-submit key/transcript/count leakage is forbidden; post-submit results and private review views are required. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-002 Complete definition and rejection boundary
- **GIVEN** The exact GAP-002 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every activity/state projection emits only its explicitly allowed fields, including errors, caches and metadata. A hidden field in any pre-submit or blind-review projection is rejected.

### Requirement: SPEC-003 Complete persistent entity and constraint model
The specification SHALL close GAP-003 with an exact versioned definition of the following: The referenced full table list does not exist. Domain entities, columns/types/nullability, keys, unique constraints, indexes, referential actions, revisions and record ownership are not enumerated. The definition SHALL preserve these existing rules: Single-workspace case/unit/version references, immutable versions and transactional audit are required; existing foundation tables are provisional. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-003 Complete definition and rejection boundary
- **GIVEN** The exact GAP-003 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every field and reference maps to a declared durable entity/constraint and one immutable version identity. Dangling, cross-case/version, duplicate or mutable historical references fail the declared constraints.

### Requirement: SPEC-004 Database and object-store commit protocol
The specification SHALL close GAP-004 with an exact versioned definition of the following: PostgreSQL and MinIO have no joint transaction specification. Pending uploads, hash verification, object promotion, orphan handling, overwrite/race behavior and crash recovery are unspecified. The definition SHALL preserve these existing rules: Domain/audit changes commit together; asset bytes are private and immutable. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-004 Complete definition and rejection boundary
- **GIVEN** The exact GAP-004 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Only a durable hash-verified immutable object can become visible through a committed authorized record. A partial upload, DB rollback, competing overwrite or crash cannot publish a missing or changed object.

### Requirement: SPEC-005 Single workspace activities without access roles
The specification SHALL follow docs/simple-local-product.md: one local workspace with teaching, preparation, review and publication activities and no role/action/resource authorization matrix. Genuine person independence, qualification, lifecycle and source-use guards SHALL remain mandatory. The user request supersedes the former GAP-005 access-role product choice.

#### Scenario: SPEC-005 Complete definition and rejection boundary
- **GIVEN** The user-selected simple local product scope.
- **WHEN** Its supported behavior and violating boundary are checked.
- **THEN** Every activity is available without role assignment while invalid source/state/review evidence is rejected. A model approval or one person represented as two reviewers cannot publish a case.

### Requirement: SPEC-006 Local startup without accounts or sessions
The specification SHALL follow docs/simple-local-product.md: no account bootstrap, passwords, login/logout, session cookies, invitations or account recovery. Loopback-only exposure, same-origin checks and server-only provider/internal-service secrets SHALL remain mandatory. The user request supersedes the former GAP-006 account-lifecycle product choice.

#### Scenario: SPEC-006 Complete definition and rejection boundary
- **GIVEN** The user-selected simple local product scope.
- **WHEN** Its supported behavior and violating boundary are checked.
- **THEN** A fresh workspace opens without login or session state. Unsupported remote exposure, cross-origin mutations and browser-visible secrets are rejected; no password setup is required.

### Requirement: SPEC-007 Case lifecycle transition and guard table
The specification SHALL close GAP-007 with an exact versioned definition of the following: No exhaustive transition table binds each state pair to actor, guard, revision, evidence requirements, audit payload and invalid transition result; treatment of in-progress attempts during quarantine is unspecified. The definition SHALL preserve these existing rules: Case states, main progression, quarantine, retirement and new-version immutability are defined. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-007 Complete definition and rejection boundary
- **GIVEN** The exact GAP-007 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every allowed transition specifies all guards/effects and all other transitions are denied. Stale revisions, incomplete gates or forbidden transitions cannot alter a case.

### Requirement: SPEC-008 Attempt and evaluation recovery transition table
The specification SHALL close GAP-008 with an exact versioned definition of the following: State-specific field invariants, retry eligibility/limits, result lookup during a lease, interrupted evaluation, expired-lease takeover and case/policy changes at retry are not a complete transition contract. The definition SHALL preserve these existing rules: Original save before providers, explicit user retry, 300-second lease and 270-second deadline are defined. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-008 Complete definition and rejection boundary
- **GIVEN** The exact GAP-008 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A permitted retry preserves the original answer/case/policy and can commit only under its current lease/revision. An active/stale lease, altered answer or forbidden state transition cannot create a final result.

### Requirement: SPEC-009 Dispute and adjudicated result revision records
The specification SHALL close GAP-009 with an exact versioned definition of the following: There is no closed dispute/adjudication/result-revision schema, complete states, evidence visibility rule, reviewer selection or old-to-new unit mapping. Existing attempts affected by a corrected key have no explicit re-evaluation policy. The definition SHALL preserve these existing rules: Plausible off-key claims require review; confirmed defects create a new case version and explicit result revision. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-009 Complete definition and rejection boundary
- **GIVEN** The exact GAP-009 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** An authorized resolution appends a traceable new result with old answer/result/key references preserved. A reviewer cannot silently overwrite scores, guess unit correspondences or revise unrelated attempts.

### Requirement: SPEC-010 Independent blind-listening annotation contract
The specification SHALL close GAP-010 with an exact versioned definition of the following: The supplied record mostly references planned unit IDs plus free text. It lacks a structured independently discovered observation set, interval/category/control/uncertainty fields, frozen pre-key submission and key-disclosure event. The definition SHALL preserve these existing rules: Two qualified people listen before the planned key and record observations/intervals; review records contain phase and decision. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-010 Complete definition and rejection boundary
- **GIVEN** The exact GAP-010 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A reviewer can save discoveries without seeing planned IDs; pre-key annotations remain immutable after disclosure. Key-dependent labels, changed pre-key notes or post-key records cannot masquerade as independent blind evidence.

### Requirement: SPEC-011 Reviewer independence and qualification records
The specification SHALL close GAP-011 with an exact versioned definition of the following: Qualification record schema/authority/expiry, identity linkage, independence beyond duplicate local person entries, author conflicts and adjudicator qualification/decision rules are unspecified. The definition SHALL preserve these existing rules: Two reviewer records belonging to one person are insufficient; acoustic review requires phonetics competence and disagreement requires a third adjudicator or blocking. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-011 Complete definition and rejection boundary
- **GIVEN** The exact GAP-011 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each counted reviewer has genuine recorded person/qualification/conflict evidence for the exact review. Alias identities, expired qualifications, missing competence or unresolved disagreement cannot approve publication.

### Requirement: SPEC-012 Teacher-answer gold annotation data contract
The specification SHALL close GAP-012 with an exact versioned definition of the following: No closed teacher-answer annotation schema defines source spans, fragmentation, stance/category/repair/rationale judgments, expected mappings, uncertainty, rater identity, adjudication or frozen pre-model label sets. The definition SHALL preserve these existing rules: Real answers and independent labels before model results are required for correct/partial/vague/repeated/contradictory/false/off-key classes. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-012 Complete definition and rejection boundary
- **GIVEN** The exact GAP-012 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Real answer gold preserves raw text and separate pre-adjudication labels with an auditable final mapping. Model-seen labels, fabricated answers or missing substantive clauses cannot qualify as independent gold.

### Requirement: SPEC-013 Detection-event boundaries and overlapping category resolution
The specification SHALL close GAP-013 with an exact versioned definition of the following: No complete event-boundary/overlap handbook resolves equally narrow categories, shared repair spans, repeated occurrences, multi-utterance events or ambiguity across reporting domains. The definition SHALL preserve these existing rules: All 122 leaves define inclusion/exclusion; use the narrowest supported category, separate independent repairs and retain secondary labels. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-013 Complete definition and rejection boundary
- **GIVEN** The exact GAP-013 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The same evidence supports one reproducible primary event count with explicit secondary labels or review. Overlapping labels, ambiguous primary domains or repeated labels cannot inflate opportunities.

### Requirement: SPEC-014 Frozen English/Russian aliases and taxonomy ancestors
The specification SHALL close GAP-014 with an exact versioned definition of the following: The approved bilingual alias map is absent. Accepted parent/family nodes, canonical spellings, ambiguous aliases, normalization and version migration are not enumerated. The definition SHALL preserve these existing rules: Explicit categories earn separate credit; unknown synonyms must not be guessed. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-014 Complete definition and rejection boundary
- **GIVEN** The exact GAP-014 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Only an approved unambiguous explicit alias receives the declared category/hierarchy credit. Unknown, ambiguous, invented or other-version aliases cannot earn guessed category credit.

### Requirement: SPEC-015 Severity assignment and fixed weight binding
The specification SHALL close GAP-015 with an exact versioned definition of the following: No severity rubric binds labels to weight values or explains whether labels and weights may vary independently; communication/context evidence and author/reviewer authority are unspecified. The definition SHALL preserve these existing rules: Four severity labels, weights 1–4 and FP weight one exist; weights are frozen before the answer. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-015 Complete definition and rejection boundary
- **GIVEN** The exact GAP-015 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each case weight has an approved reproducible severity policy and pre-attempt record. Post-answer weight changes or inconsistent unsupported severity assignments fail.

### Requirement: SPEC-016 Rated difficulty evidence protocol
The specification SHALL close GAP-016 with an exact versioned definition of the following: No rating method, population, sample sufficiency or difficulty-to-evidence rule exists for the non-unrated enum values. The definition SHALL preserve these existing rules: Generated candidates are unrated; reviewed records allow easy/medium/hard/expert with evidence. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-016 Complete definition and rejection boundary
- **GIVEN** The exact GAP-016 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A rated value is displayed only under its declared measurement protocol; otherwise it remains unrated. Author intuition or unrelated corpus CEFR cannot become a measured difficulty rating.

### Requirement: SPEC-017 Variety, register and judgment consistency table
The specification SHALL close GAP-017 with an exact versioned definition of the following: Accepted-variety/register strings have no registry or full expected_judgment/status_label/basis/eligibility compatibility table. Authoring conflict validation and public-context sufficiency lack a complete review rubric. The definition SHALL preserve these existing rules: Public variety/context constraints and separation of error, permitted variant and naturalness are mandatory. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-017 Complete definition and rejection boundary
- **GIVEN** The exact GAP-017 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every scored context-dependent event uses a reviewed public constraint and compatible status/eligibility. A hidden dialect constraint, incompatible status or accent preference cannot count as a true error.

### Requirement: SPEC-018 Claim identity, extraction partition and completeness
The specification SHALL close GAP-018 with an exact versioned definition of the following: Stable-ID construction, clause ordering, allowed span overlaps/nesting, attachment containment and checking that all substantive assertions were extracted or marked unparsed are not fully specified. The definition SHALL preserve these existing rules: Exact codepoint spans, server-assigned claim IDs and preservation of unparsed substantive text are required. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-018 Complete definition and rejection boundary
- **GIVEN** The exact GAP-018 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The frozen answer deterministically produces stable checked claims and explicit unresolved substantive coverage. Fabricated/overlapping-invalid spans or silently omitted substantive assertions cannot score as complete.

### Requirement: SPEC-019 Fragment consolidation, duplicate and retraction normalization
The specification SHALL close GAP-019 with an exact versioned definition of the following: The transformation from several clauses to one unit decision is absent. The reference scorer rejects multiple nonduplicate assignments; exact grouping, attachment, retraction chains and provenance are not defined. The definition SHALL preserve these existing rules: Exact duplicates count once; compatible fragments may combine; explicit retraction uses the final endorsed statement; contradictions require review. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-019 Complete definition and rejection boundary
- **GIVEN** The exact GAP-019 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Compatible fragments form one traceable scorer decision and valid duplicates/retractions retain all source evidence. Cycles, conflicting repairs or arbitrary last-write/best-of grouping cannot produce final credit.

### Requirement: SPEC-020 Evaluator and cross-schema conditional truth tables
The specification SHALL close GAP-020 with an exact versioned definition of the following: A full permitted tuple table is absent for decision/unit/stance/reason/duplicate and supplied/option/propositions/status/unresolved_reason, and for candidate failure/realization/verification/review states. The definition SHALL preserve these existing rules: Closed structural schemas and several membership/stance/evidence invariants are supplied. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-020 Complete definition and rejection boundary
- **GIVEN** The exact GAP-020 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every accepted cross-field tuple has a declared semantic invariant and derivation. A structurally valid but contradictory tuple is rejected before publication/scoring.

### Requirement: SPEC-021 Approved rationale registry and explanation-null binding
The specification SHALL close GAP-021 with an exact versioned definition of the following: Feedback approved_rationale_ids still lacks an explicit identity/entity contract linking the unit rationale to approved text, language and evidence. The explanation-null requirement needs an active cross-field binding rather than inference from schema shape alone. The definition SHALL preserve these existing rules: Key units have rationale propositions/text. The reference validator explicitly requires explanation.option_id=null; no explanation-option registry is needed under that rule. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-021 Complete definition and rejection boundary
- **GIVEN** The exact GAP-021 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each explanation/feedback reference resolves to the exact approved unit/version/language record. A nonexistent, correction-only, wrong-language or other-version rationale ID is rejected.

### Requirement: SPEC-022 Semantic decisions to deterministic rubric and scorer input
The specification SHALL close GAP-022 with an exact versioned definition of the following: No complete binding algorithm selects a reviewed option, validates normalized alternative matches, maps proposition findings/status to exact fractions and converts excluded units/ignore/retractions into scorer records. The definition SHALL preserve these existing rules: q is satisfied required propositions / required propositions; forbidden assertions force zero, approved alternatives earn one, missing supplied work earns zero and novel alternatives require review. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-022 Complete definition and rejection boundary
- **GIVEN** The exact GAP-022 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Code derives exact fractions and sufficient statistics solely from validated source claims and fixed reviewed options. Model fractions, teacher-unsupplied content or cherry-picked contradictory options cannot enter the scorer.

### Requirement: SPEC-023 Mapper/auditor comparison equality contract
The specification SHALL close GAP-023 with an exact versioned definition of the following: The canonical compared projection, set/order treatment, handling of duplicates/evidence/option/status/reasons and definition of score-relevant versus harmless differences are unspecified. The definition SHALL preserve these existing rules: Audit is a separate blind-to-first-output consistency request; relevant disagreement requires review, never favorable retries. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-023 Complete definition and rejection boundary
- **GIVEN** The exact GAP-023 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Two semantically equivalent records compare consistently without hiding any score-relevant difference. Different target, option, stance or proposition credit cannot be ignored as harmless formatting.

### Requirement: SPEC-024 Exact score transport, composite rational and numeric bounds
The specification SHALL close GAP-024 with an exact versioned definition of the following: The composite has only a floating value and no exact fraction. Integer caps, safe cross-language representation, decimal serialization and complete display rounding for composite/auxiliary values are unspecified. The definition SHALL preserve these existing rules: Core ratios retain exact numerator/denominator, sufficient statistics and one-decimal half-up displays; the composite formula is explicit. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-024 Complete definition and rejection boundary
- **GIVEN** The exact GAP-024 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every score can be reproduced exactly across services from saved statistics and policy. Overflow, binary-float drift or a rounded display reused as an exact value is rejected.

### Requirement: SPEC-025 Auxiliary and provisional result response contracts
The specification SHALL close GAP-025 with an exact versioned definition of the following: The score-result schema enumerates core ratios only. No complete output shape binds auxiliary values/methods/units/missing reasons or provisional item evidence and review issue lists. The definition SHALL preserve these existing rules: All 27 core and 15 auxiliary formulas are retained; unresolved decisions withhold final aggregates and unobserved teacher traits are null. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-025 Complete definition and rejection boundary
- **GIVEN** The exact GAP-025 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** All 42 named measurements have an explicit output location/status/method, without final aggregates for unresolved decisions. Missing measurements cannot disappear, become zero/perfect, or be displayed as final confirmed misses.

### Requirement: SPEC-026 Grounded bilingual feedback and missed-unit references
The specification SHALL close GAP-026 with an exact versioned definition of the following: Missed units have no extracted teacher decision ID; the supplied feedback shape requires one. Approved bilingual rationale text/IDs and a deterministic check of free-text factual grounding are absent. The definition SHALL preserve these existing rules: Feedback may explain validated findings/misses in English or Russian, cite reviewed material and introduce no new errors or grades. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-026 Complete definition and rejection boundary
- **GIVEN** The exact GAP-026 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every feedback statement traces to a validated result or approved rationale in the selected language. Invented decision IDs, new repairs/grades or untranslated unsupported fallback content fail.

### Requirement: SPEC-027 Feedback-only failure versus evaluation-failure outcome
The specification SHALL close GAP-027 with an exact versioned definition of the following: The blanket provider-failure status conflicts with an undefined completed-score-plus-fallback response. Persisted attempt/result state and HTTP status for feedback-only refusal/truncation/schema/timeout are not frozen. The definition SHALL preserve these existing rules: Metric computation and feedback are distinct; approved stored rationale is allowed if feedback fails. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-027 Complete definition and rejection boundary
- **GIVEN** The exact GAP-027 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Feedback failure preserves valid numeric evidence and shows an explicitly labelled approved fallback under the declared response status. A failed semantic stage cannot use this fallback exception to fabricate a completed score.

### Requirement: SPEC-028 Linguistic audit role prompt, schema and decisions
The specification SHALL close GAP-028 with an exact versioned definition of the following: The active manifest has no exact linguistic-audit input/output/prompt version with target/span findings, refusal rules, allowed evidence and integration into candidate review. The definition SHALL preserve these existing rules: The role is advisory and configurable; a separate draft proposal exists, not an approved active contract. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-028 Complete definition and rejection boundary
- **GIVEN** The exact GAP-028 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The selected active linguistic-audit contract is complete and version-bound before the role is enabled. Reused unrelated schemas or invented human approvals cannot activate the role.

### Requirement: SPEC-029 Complete role input and configuration binding schemas
The specification SHALL close GAP-029 with an exact versioned definition of the following: There is no closed schema for each stage input DTO, effective role binding, configuration registry, provider receipt or stage-cache record. Required input fields and maximum sizes are mostly prose. The definition SHALL preserve these existing rules: Roles, profiles, prompt/schema hashes, disclosure boundaries, frozen identities and configurable DeepSeek development selection are described. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-029 Complete definition and rejection boundary
- **GIVEN** The exact GAP-029 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each role receives only its complete permitted input under a frozen validated binding. Extraction keys, raw identities, unknown settings or wrong-case/version cached output cannot enter the role.

### Requirement: SPEC-030 Provider-specific strict-schema projection and response parsing
The specification SHALL close GAP-030 with an exact versioned definition of the following: The per-provider supported keyword projection, preserved application validation mapping and responses output/refusal/incomplete parser are not specified. DeepSeek trusted-instruction and reasoning/output handling need exact transport rules. The definition SHALL preserve these existing rules: The full application schemas cannot be weakened; unsupported wire projections block the profile. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-030 Complete definition and rejection boundary
- **GIVEN** The exact GAP-030 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The adapter preserves every application constraint and accepts only a completed structurally and semantically valid stage payload. Developer-as-user instructions, reasoning text, dropped constraints or JSON repair cannot become accepted stage output.

### Requirement: SPEC-031 Retry, deadline and input/output capacity protocol
The specification SHALL close GAP-031 with an exact versioned definition of the following: Retry count scope (request versus stage), retryable status/error list, backoff within reserve, generation-attempt versus transport-attempt accounting, disconnect cancellation and prompt/token overflow are not complete contracts. The definition SHALL preserve these existing rules: Stage/global deadlines, no semantic retries, explicit recovery and candidate generation/render attempt caps are present. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-031 Complete definition and rejection boundary
- **GIVEN** The exact GAP-031 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every retry is counted and fits the remaining budget; oversized work returns the declared safe outcome with saved source input. 429/5xx loops, reasoning-token exhaustion, silent truncation or late commits cannot bypass limits.

### Requirement: SPEC-032 Typed render operator and hard-capability catalog
The specification SHALL close GAP-032 with an exact versioned definition of the following: Per-operator required/null fields, rate/pitch/pause ranges, locale/voice/capability compatibility and hard-constraint precedence/conflict rules are not closed. DEC-004 still uses unrestricted strings. The definition SHALL preserve these existing rules: Four typed render operations and five capability names exist; arbitrary XML and remote audio are forbidden. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-032 Complete definition and rejection boundary
- **GIVEN** The exact GAP-032 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A complete typed plan is validated against a fixed profile/capability catalog before synthesis. Unknown hard constraints, irrelevant payload fields and incompatible voice/locale/target combinations fail.

### Requirement: SPEC-033 SSML compilation and final-audio assembly specification
The specification SHALL close GAP-033 with an exact versioned definition of the following: The compiler grammar, per-turn call ordering, punctuation/prosody scope, concatenation/gaps, resampling, delivery codec, timestamp frame rounding and transformation manifest are not fully defined. The definition SHALL preserve these existing rules: Azure REST, escaped typed SSML and a 24-kHz mono PCM16 master are prescribed; final bytes require review. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-033 Complete definition and rejection boundary
- **GIVEN** The exact GAP-033 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The final delivered asset and every turn/unit interval are reproducibly linked to exact plan and transformations. A reordered turn, changed encoded file, unsupported phoneme or altered intentional target cannot inherit prior review.

### Requirement: SPEC-034 Audio quality measurement method and boundary rules
The specification SHALL close GAP-034 with an exact versioned definition of the following: Loudness/true-peak algorithm/version, decoding/sample normalization, RMS hop/window-edge treatment, near-silence grouping and planned-pause overlap classification are absent. The definition SHALL preserve these existing rules: Peak .9999, -18±2 LUFS, ≤-1 dBTP, silence thresholds and finite/mono/duration checks are specified. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-034 Complete definition and rejection boundary
- **GIVEN** The exact GAP-034 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every QC value has its final-byte subject, method, unit and reproducible boundary classification. A method-less value, padding-dependent silence or upstream-file measurement cannot approve final delivery.

### Requirement: SPEC-035 Speech tokenizer, reviewed intervals and disfluency event rules
The specification SHALL close GAP-035 with an exact versioned definition of the following: Exact contraction/number/filler/repetition tokenization, interval union rules, active speech/pauses and countable disfluency event identities are absent. The definition SHALL preserve these existing rules: Elapsed speech includes internal pauses; articulation uses reviewed speech intervals; disfluency counts only reviewed events. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-035 Complete definition and rejection boundary
- **GIVEN** The exact GAP-035 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every rate/density numerator and denominator can be recomputed from a fixed reviewed annotation/method. Different tokenizers, overlapping intervals or ordinary permitted fillers cannot produce comparable error metrics.

### Requirement: SPEC-036 Prosody feature/unit/method and valid missingness table
The specification SHALL close GAP-036 with an exact versioned definition of the following: There is no complete feature-to-unit/method table, F0 reference/log conversion, slope/range extraction, voiced-frame selection, syllable/phrase boundaries or label vocabularies. The definition SHALL preserve these existing rules: Eleven named prosody features distinguish requested bounds, observation and evidence; unsupported numeric methods remain unavailable. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-036 Complete definition and rejection boundary
- **GIVEN** The exact GAP-036 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every observed feature has a valid method/unit/subject combination and separates intended from measured values. Invalid feature units, unvoiced F0 or provider naturalness scores cannot masquerade as measured target evidence.

### Requirement: SPEC-037 ASR and pronunciation advisory normalization
The specification SHALL close GAP-037 with an exact versioned definition of the following: Chunk boundaries/reference slices, overlap/stitching, tick/second-to-ms conversion, missing/NoMatch handling and typed provider-field normalization are incomplete. The definition SHALL preserve these existing rules: Whisper raw hypothesis precedes alignment; Azure advisory chunks use 16-kHz mono PCM, max25s; prosody en-US only. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-037 Complete definition and rejection boundary
- **GIVEN** The exact GAP-037 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each advisory observation retains its raw response and exact final-audio/chunk/version mapping. Missing fields, reference-conditioned scores or wrong offset units cannot create observed IPA or automatic gold.

### Requirement: SPEC-038 Full synthetic target capability and canary specification
The specification SHALL close GAP-038 with an exact versioned definition of the following: Per-leaf/voice/locale target requests, observable realization criteria and canary change-detection protocol are incomplete. Taxonomy recording-route alternatives are not active profiles. The definition SHALL preserve these existing rules: Every taxonomy target remains in scope; three render attempts then blocking; no active human-recording/provider fallback. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-038 Complete definition and rejection boundary
- **GIVEN** The exact GAP-038 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each target has a complete requested-versus-observed qualification contract, even if evidence later fails. An unproven/failed target cannot be dropped, replaced or marked observed from SSML settings.

### Requirement: SPEC-039 Full source manifest, legal scope and transformation contracts
The specification SHALL close GAP-039 with an exact versioned definition of the following: No closed release manifest/permissions/import report/transformation schema defines required components/count units, parser identities, checksums, rejection reconciliation and normalized grouping/label relations. The definition SHALL preserve these existing rules: Eight profiles, immutable raw records, private quarantine, full-release obligations and per-use rights are required. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-039 Complete definition and rejection boundary
- **GIVEN** The exact GAP-039 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** All acquired components/counts and rejected rows reconcile to an exact manifest with each transformation and allowed use. Samples, omitted components, mixed releases or unapproved transfer cannot satisfy a full-source claim.

### Requirement: SPEC-040 Complete SpeechOcean762 parser and source scale profile
The specification SHALL close GAP-040 with an exact versioned definition of the following: Source metadata spk2utt/spk2age/spk2gender is missing from the abbreviated plan. Complete field/scale/marker/raw-to-normalized profiles and approved ARPAbet↔IPA conversion are absent; docs illustrate differing completeness scales. The definition SHALL preserve these existing rules: Full train/test, raw scores and five raters are required; no phone substitution may be inferred from low accuracy. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-040 Complete definition and rejection boundary
- **GIVEN** The exact GAP-040 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** All selected-release fields and raters are retained with declared source scales and original marker uncertainty. Dropped child/speaker metadata, inferred phones, mixed scales or guessed IPA mapping fails full faithful import.

### Requirement: SPEC-041 Complete L2-ARCTIC v5 read and suitcase parser profile
The specification SHALL close GAP-041 with an exact versioned definition of the following: No complete v5 directory/tier/marker grammar, CPL/PPL/s/a/d/err/* conversion profile, 44.1-kHz clock mapping or approved phone/taxonomy mapping is supplied. The definition SHALL preserve these existing rules: Full24-speaker read release and22-speaker suitcase extension remain required in the inventory; automatic/manual tiers stay distinct. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-041 Complete definition and rejection boundary
- **GIVEN** The exact GAP-041 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every component and manual/automatic label is retained with exact source-clock and annotation provenance. Automatic alignments, err/* uncertainty or unsupported phone conversions cannot become manual narrow-category gold.

### Requirement: SPEC-042 Complete W&I+LOCNESS and FCE v2.1 M2 parser profiles
The specification SHALL close GAP-042 with an exact versioned definition of the following: Approved ERRANT-to-project leaf mappings are absent; per-release partition metadata/group IDs, detection-only labels, historical fields, edit-order ties and full parser output schema are incomplete. The definition SHALL preserve these existing rules: Half-open source token spans, one-annotator edits, alternatives/noop and CEFR granularity are required; separate releases/licences retained. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-042 Complete definition and rejection boundary
- **GIVEN** The exact GAP-042 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** All supplied components/annotators/edits/native controls and original group metadata are faithfully retained. Combined annotators, invented learner IDs/test labels or guessed narrow leaf mapping fails import.

### Requirement: SPEC-043 EFCAMDAT full release and derivative ingest scope
The specification SHALL close GAP-043 with an exact versioned definition of the following: The current full-source request and discovery-only baseline are not a completed ingest contract. Full XML schema, labels/offsets, prompt/task/learner grouping, selected derivative scope and permitted intended use are unspecified. The definition SHALL preserve these existing rules: Full second-release XML is identified; first release and cleaned/error-coded derivatives are distinct; baseline is discovery-only. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-043 Complete definition and rejection boundary
- **GIVEN** The exact GAP-043 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every selected EFCAMDAT release has its own complete component/parser/use contract. Discovery metadata, cleaned subsets, inaccessible labels or academic access alone cannot satisfy full product ingest.

### Requirement: SPEC-044 Doubao underlying study-record release contract
The specification SHALL close GAP-044 with an exact versioned definition of the following: There is no identified full release, schema, annotation inventory, participant grouping or permission contract for the reported study records. The definition SHALL preserve these existing rules: The study is a research reference; no supplied downloadable participant-record corpus or rights exists. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-044 Complete definition and rejection boundary
- **GIVEN** The exact GAP-044 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A real full release contract or an explicit scoped research-only disposition is recorded without hiding missing data. Paper sample counts or questionnaire percentages cannot stand in for an acquired labelled corpus.

### Requirement: SPEC-045 Moodrick and NIR vendor-data scope and contracts
The specification SHALL close GAP-045 with an exact versioned definition of the following: No full annotated release or exact comparison-only versus corpus-ingest definition exists for both vendors under the latest full-source requirement. The definition SHALL preserve these existing rules: Both vendors are comparison sources; private answer banks/prompts/rubrics have no supplied data licence. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-045 Complete definition and rejection boundary
- **GIVEN** The exact GAP-045 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Both vendor sources have exact documented scope and no fictional assets or inferred providers. Product descriptions, demo percentages or another vendor product disclosure cannot qualify as this corpus.

### Requirement: SPEC-046 Leakage grouping, split allocation and duplicate protocol
The specification SHALL close GAP-046 with an exact versioned definition of the following: Canonical group identities, connection/duplicate equivalence, split allocation ratios/seed, upstream-versus-project split distinction and infeasible connected components are not specified. The definition SHALL preserve these existing rules: Development/calibration/holdout preserve related speaker/learner/script/derivative groups; upstream benchmark splits are retained. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-046 Complete definition and rejection boundary
- **GIVEN** The exact GAP-046 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Frozen group manifests prove every intended independence boundary and report infeasible splits explicitly. Connected derivatives/speakers/scripts cannot cross splits or be accepted through a changed leakage definition.

### Requirement: SPEC-047 Gold stimulus, asset and negative-control counting
The specification SHALL close GAP-047 with an exact versioned definition of the following: Counting unit for multi-target files, acceptable-variant counterparts, approved observations versus assets and independent pair families remains unresolved. The definition SHALL preserve these existing rules: 122 leaves, six candidate stimuli per leaf/732 total and one contrast pair per split are preserved policy candidates. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-047 Complete definition and rejection boundary
- **GIVEN** The exact GAP-047 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each leaf/control satisfies its approved counting rule with exact record IDs and independent final-audio reviews. Multi-label files, duplicated stimuli or treating a permitted variant as an error cannot inflate coverage.

### Requirement: SPEC-048 Agreement and semantic evaluation denominator protocols
The specification SHALL close GAP-048 with an exact versioned definition of the following: The annotation unit/label inventory, alignment and missing-rater handling, exact resolved/eligible/gold-decision definitions and class/stratum weighting are not specified enough to calculate comparable values. The definition SHALL preserve these existing rules: Raw agreement/kappa and semantic coverage/exact mapping equations exist; pre-adjudication labels and abstentions must be retained. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-048 Complete definition and rejection boundary
- **GIVEN** The exact GAP-048 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every numerator/denominator is traceable to the same frozen independently labelled population. Adjudicated unanimity, dropped abstentions or changed eligibility cannot improve apparent agreement.

### Requirement: SPEC-049 Elapsed attempt start and validated playback event contracts
The specification SHALL close GAP-049 with an exact versioned definition of the following: started_at is absent from attempt.schema; its trigger/clock/restart behavior is undefined. No playback-event schema/validation/deduplication or event transport contract exists. The definition SHALL preserve these existing rules: Elapsed wall time and accepted play-event count are descriptive; client events do not prove listening. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-049 Complete definition and rejection boundary
- **GIVEN** The exact GAP-049 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Elapsed time and replay count recompute from declared saved timestamps and accepted event IDs. Client-forged duration, duplicate plays or missing start cannot become an ability score.

### Requirement: SPEC-050 Complete heldout acceptance protocol and critical cases
The specification SHALL close GAP-050 with an exact versioned definition of the following: Exact gold-mapping precision equality, correction-attempt eligibility, critical-counterexample inventory, domain assignment, three-run agreement estimator and configuration/prompt freeze protocol are incomplete. The definition SHALL preserve these existing rules: Mapping/coverage/correction/repeat gates have numeric limits and minimum denominators; every domain and fixed configuration requires evidence. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-050 Complete definition and rejection boundary
- **GIVEN** The exact GAP-050 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each gate calculates the frozen defined statistic with adequate actual strata and untouched holdout evidence. Tiny/subset domains, omitted critical failures or threshold tuning on exposed holdout cannot pass.

### Requirement: SPEC-051 Retention, deletion and permission revocation lifecycle
The specification SHALL close GAP-051 with an exact versioned definition of the following: No exact retention periods or deletion/revocation contract reconciles immutable history, personal/source data, provider responses, backups and affected future use. The definition SHALL preserve these existing rules: Raw answers/evidence are immutable, private, consent-bound and tied to approved use; owner approvals can expire or be revoked. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-051 Complete definition and rejection boundary
- **GIVEN** The exact GAP-051 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each retained or deleted artifact has a defined permitted lifecycle and future transfer/publication guard. Expired/revoked permission or a delete request cannot silently retain active use or destroy audit references inconsistently.

### Requirement: SPEC-052 Request quotas, concurrency, costs and import resource bounds
The specification SHALL close GAP-052 with an exact versioned definition of the following: Local numeric limits/units, operation concurrency, provider usage accounting, request/file/archive limits and exhausted-budget failure codes need exact engineering definitions; per-user/tenant quotas and billing services are excluded. The definition SHALL preserve these existing rules: Requests/costs are limited; provider usage is recorded; exhausted generation quotas cannot block permitted playback; imports must reject unbounded decompression. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-052 Complete definition and rejection boundary
- **GIVEN** The exact GAP-052 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Usage/resource admission and settlement are deterministic under declared limits and concurrent requests. Quota races, retry double charges, archive expansion or evaluation limits cannot bypass admission or block authorized playback.

### Requirement: SPEC-053 Backup/restore consistency and compatibility protocol
The specification SHALL close GAP-053 with an exact versioned definition of the following: Full domain DB/media snapshot boundary, manifest schema, restore validation/order/rollback, schema/profile compatibility and historical private evidence coverage are not completely specified. The definition SHALL preserve these existing rules: Named volumes preserve data, migrations have checksums/locks and destructive reset needs operator confirmation. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-053 Complete definition and rejection boundary
- **GIVEN** The exact GAP-053 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A validated compatible backup restores every declared domain/media reference and historical answer/result. Missing assets, tampered manifests, incompatible migrations or an existing conflicting target cannot produce a healthy partial restore.

### Requirement: SPEC-054 Basic GitHub download-and-run setup
The specification SHALL close GAP-054 by defining only the basic startup and configuration needed to download the open-source GitHub source ZIP or clone, provide provider keys, run the supplied helper and use the application locally. It SHALL specify prerequisites, included application build inputs, exact start/stop/restart commands, first-run initialization, automatic persistent internal secrets, provider-key settings/defaults/validation and clear build/key/port errors. Application images SHALL build locally; source-ZIP startup SHALL require no Git metadata, workflow submodules or developer planning tools. A formal deployment/release manifest, signed release bundle, prebuilt application image publication and production deployment system are excluded. This user clarification resolves the distribution choice; remaining setup details are ordinary engineering definitions.

#### Scenario: SPEC-054 Complete definition and rejection boundary
- **GIVEN** The exact GAP-054 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The extracted source contains a complete documented local setup using provider keys and supplied defaults; required internal infrastructure is automatic. Missing prerequisites/build inputs, invalid settings or a failed build yield clear errors without success, manual account/database setup or browser-visible secrets.

### Requirement: SPEC-055 Specification authority, version compatibility and drift closure
The specification SHALL close GAP-055 with an exact versioned definition of the following: Multiple initial/recovered/overlay registries/specs and provisional implementation contain divergent contracts. No full active precedence/compatibility map or closure process binds every overlapping definition/version. The definition SHALL preserve these existing rules: Current user scope outranks imported instructions; archive bytes remain immutable and source recovery is distinct from implementation. It SHALL identify every remaining owner/source dependency and SHALL NOT replace unknown definitions or genuine evidence with an invented default.

#### Scenario: SPEC-055 Complete definition and rejection boundary
- **GIVEN** The exact GAP-055 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every active requirement resolves to one consistent definition and every known gap has exact closure evidence. Duplicate contradictory definitions, stale missing-file claims or structural counts cannot establish semantic completeness.
