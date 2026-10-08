# Exact specification gaps — 2026-10-08

The full v6 archive is present. Its taxonomy, schemas, five prompts and scoring policy are recovered. The active specification still has **55 grouped definition gaps**. These are missing or conflicting definitions, not a count of unimplemented features. Each finding lists the specific fields/rules needed; grouped findings can contain several atomic omissions.

Current work is specification/research only. No runtime, provider request, acquired corpus, reviewer approval or empirical result is created by this audit. Existing DEC proposals stay unapproved. Exact line indexing supports navigation; it does not prove semantic correctness.

Engineering-definition items can be drafted from this register without requiring you to design API internals. Product/linguistic/source-owner items need your choice or actual source documentation. Nothing below is silently adopted as policy.

| ID | Area | Missing definition | Input owner |
|---|---|---|---|
| GAP-001 | api | [Complete product and internal API operation contracts](#gap-001) | engineering_definition |
| GAP-002 | api | [Public and private transport projections](#gap-002) | product_choice |
| GAP-003 | data | [Complete persistent entity and constraint model](#gap-003) | engineering_definition |
| GAP-004 | data | [Database and object-store commit protocol](#gap-004) | engineering_definition |
| GAP-005 | flows | [Role/action/resource authorization matrix](#gap-005) | product_choice |
| GAP-006 | flows | [Account and session lifecycle contract](#gap-006) | product_choice |
| GAP-007 | flows | [Case lifecycle transition and guard table](#gap-007) | product_choice |
| GAP-008 | flows | [Attempt and evaluation recovery transition table](#gap-008) | engineering_definition |
| GAP-009 | flows | [Dispute and adjudicated result revision records](#gap-009) | product_choice |
| GAP-010 | review | [Independent blind-listening annotation contract](#gap-010) | engineering_definition |
| GAP-011 | review | [Reviewer independence and qualification records](#gap-011) | product_choice |
| GAP-012 | review | [Teacher-answer gold annotation data contract](#gap-012) | engineering_definition |
| GAP-013 | taxonomy | [Detection-event boundaries and overlapping category resolution](#gap-013) | engineering_definition |
| GAP-014 | taxonomy | [Frozen English/Russian aliases and taxonomy ancestors](#gap-014) | linguistic_policy |
| GAP-015 | scoring | [Severity assignment and fixed weight binding](#gap-015) | product_choice |
| GAP-016 | scoring | [Rated difficulty evidence protocol](#gap-016) | product_choice |
| GAP-017 | taxonomy | [Variety, register and judgment consistency table](#gap-017) | linguistic_policy |
| GAP-018 | scoring | [Claim identity, extraction partition and completeness](#gap-018) | engineering_definition |
| GAP-019 | scoring | [Fragment consolidation, duplicate and retraction normalization](#gap-019) | engineering_definition |
| GAP-020 | scoring | [Evaluator and cross-schema conditional truth tables](#gap-020) | engineering_definition |
| GAP-021 | scoring | [Approved rationale registry and explanation-null binding](#gap-021) | engineering_definition |
| GAP-022 | scoring | [Semantic decisions to deterministic rubric and scorer input](#gap-022) | engineering_definition |
| GAP-023 | scoring | [Mapper/auditor comparison equality contract](#gap-023) | engineering_definition |
| GAP-024 | scoring | [Exact score transport, composite rational and numeric bounds](#gap-024) | engineering_definition |
| GAP-025 | scoring | [Auxiliary and provisional result response contracts](#gap-025) | engineering_definition |
| GAP-026 | feedback | [Grounded bilingual feedback and missed-unit references](#gap-026) | engineering_definition |
| GAP-027 | feedback | [Feedback-only failure versus evaluation-failure outcome](#gap-027) | product_choice |
| GAP-028 | providers | [Linguistic audit role prompt, schema and decisions](#gap-028) | linguistic_policy |
| GAP-029 | providers | [Complete role input and configuration binding schemas](#gap-029) | engineering_definition |
| GAP-030 | providers | [Provider-specific strict-schema projection and response parsing](#gap-030) | engineering_definition |
| GAP-031 | providers | [Retry, deadline and input/output capacity protocol](#gap-031) | engineering_definition |
| GAP-032 | audio | [Typed render operator and hard-capability catalog](#gap-032) | product_choice |
| GAP-033 | audio | [SSML compilation and final-audio assembly specification](#gap-033) | engineering_definition |
| GAP-034 | audio | [Audio quality measurement method and boundary rules](#gap-034) | engineering_definition |
| GAP-035 | audio | [Speech tokenizer, reviewed intervals and disfluency event rules](#gap-035) | linguistic_policy |
| GAP-036 | audio | [Prosody feature/unit/method and valid missingness table](#gap-036) | linguistic_policy |
| GAP-037 | audio | [ASR and pronunciation advisory normalization](#gap-037) | engineering_definition |
| GAP-038 | audio | [Full synthetic target capability and canary specification](#gap-038) | engineering_definition |
| GAP-039 | corpora | [Full source manifest, legal scope and transformation contracts](#gap-039) | engineering_definition |
| GAP-040 | corpora | [Complete SpeechOcean762 parser and source scale profile](#gap-040) | engineering_definition |
| GAP-041 | corpora | [Complete L2-ARCTIC v5 read and suitcase parser profile](#gap-041) | engineering_definition |
| GAP-042 | corpora | [Complete W&I+LOCNESS and FCE v2.1 M2 parser profiles](#gap-042) | engineering_definition |
| GAP-043 | corpora | [EFCAMDAT full release and derivative ingest scope](#gap-043) | source_owner_input |
| GAP-044 | corpora | [Doubao underlying study-record release contract](#gap-044) | source_owner_input |
| GAP-045 | corpora | [Moodrick and NIR vendor-data scope and contracts](#gap-045) | source_owner_input |
| GAP-046 | corpora | [Leakage grouping, split allocation and duplicate protocol](#gap-046) | product_choice |
| GAP-047 | corpora | [Gold stimulus, asset and negative-control counting](#gap-047) | linguistic_policy |
| GAP-048 | formulas | [Agreement and semantic evaluation denominator protocols](#gap-048) | engineering_definition |
| GAP-049 | formulas | [Elapsed attempt start and validated playback event contracts](#gap-049) | engineering_definition |
| GAP-050 | validation | [Complete heldout acceptance protocol and critical cases](#gap-050) | engineering_definition |
| GAP-051 | data | [Retention, deletion and permission revocation lifecycle](#gap-051) | product_choice |
| GAP-052 | operations | [Request quotas, concurrency, costs and import resource bounds](#gap-052) | product_choice |
| GAP-053 | operations | [Backup/restore consistency and compatibility protocol](#gap-053) | engineering_definition |
| GAP-054 | operations | [Complete deployment/configuration and release manifest schema](#gap-054) | engineering_definition |
| GAP-055 | governance | [Specification authority, version compatibility and drift closure](#gap-055) | engineering_definition |

## GAP-001

**Complete product and internal API operation contracts**

Source: [docs/runtime-v1.md:53](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:53); [openspec/changes/implement-teacher-error-trainer/specs/v6-platform-foundation/spec.md:5](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/specs/v6-platform-foundation/spec.md:5).

**Already specified:** Role-aware API behavior, selected submission statuses and private media are required; domain schemas are supplied.

**Missing or conflicting:** No complete method/path/operation inventory or transport contract defines request bodies, response bodies, headers, authentication, revision preconditions, pagination, idempotency scope, or errors for author/review/publication/disputes/import/admin/speech operations.

**Fill in:** Specify the operation contracts for every row of api-obligations.md, including required/nullable fields, defaults, ranges, success/error status and atomic effects. Engineering can draft these; identify any required route conventions.

**Positive closure:** Every in-scope operation has one versioned request/response/security/error contract and links to its flow and owner.

**Negative closure:** An omitted operation, undefined payload/status or unbound route prevents an API-complete claim.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-002

**Public and private transport projections**

Source: [docs/runtime-v1.md:53](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:53); [contracts/ground-truth.schema.json:34](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:34).

**Already specified:** Pre-submit key/transcript/count leakage is forbidden; post-submit results and private review views are required.

**Missing or conflicting:** No field allowlists define library, exercise-start, media, pre-key review, post-key review, attempt, result, dispute, author and admin views. Post-submit key visibility and historical/quarantined views are not fully defined.

**Fill in:** Define each view field-by-field, its audience/state, and when transcripts/keys/evidence become visible. Decide whether a teacher receives the complete key after submission or only result-linked excerpts.

**Positive closure:** Every state/role projection emits only its explicitly allowed fields, including errors, caches and metadata.

**Negative closure:** A hidden field in any pre-submit or blind-review projection is rejected.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-003

**Complete persistent entity and constraint model**

Source: [docs/runtime-v1.md:49](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:49); [openspec/changes/implement-teacher-error-trainer/design.md:15](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/design.md:15).

**Already specified:** Tenant-aware references, immutable versions and transactional audit are required; existing foundation tables are provisional.

**Missing or conflicting:** The referenced full table list does not exist. Domain entities, columns/types/nullability, keys, unique constraints, indexes, referential actions, revisions and record ownership are not enumerated.

**Fill in:** Provide a domain entity dictionary covering all schemas plus users/roles, qualifications, reviews, permissions, releases/manifests, transformations, stages, audit, disclosures, disputes and result revisions; define each relation and uniqueness scope.

**Positive closure:** Every field and reference maps to a declared durable entity/constraint and one immutable version identity.

**Negative closure:** Dangling, cross-tenant, duplicate or mutable historical references fail the declared constraints.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-004

**Database and object-store commit protocol**

Source: [docs/runtime-v1.md:50](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:50); [docs/contract-invariants.md:51](/Users/jekamas/projects/0xatelerix/tangerine/docs/contract-invariants.md:51).

**Already specified:** Domain/audit changes commit together; asset bytes are private and immutable.

**Missing or conflicting:** PostgreSQL and MinIO have no joint transaction specification. Pending uploads, hash verification, object promotion, orphan handling, overwrite/race behavior and crash recovery are unspecified.

**Fill in:** Define the durable asset states and ordered upload/hash/DB-link operations, visibility guards, cleanup permission and recovery for every crash boundary without a background queue.

**Positive closure:** Only a durable hash-verified immutable object can become visible through a committed authorized record.

**Negative closure:** A partial upload, DB rollback, competing overwrite or crash cannot publish a missing or changed object.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-005

**Role/action/resource authorization matrix**

Source: [docs/runtime-v1.md:57](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:57); [openspec/changes/implement-teacher-error-trainer/specs/v6-content-lifecycle/spec.md:9](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/specs/v6-content-lifecycle/spec.md:9).

**Already specified:** Teacher, author, reviewer and administrator are named; tenant isolation and authenticated actions are mandatory.

**Missing or conflicting:** Publisher/adjudicator are workflow labels with no mapping to the four roles. Read/write/publish/quarantine/adjudicate/import/configure rights, same-person restrictions and admin scope are not a complete matrix.

**Fill in:** Assign every API operation to roles and resource ownership. State who publishes and adjudicates, whether authors may review their own work, and whether administrators may bypass any review guard (structural/rights guards remain non-overridable).

**Positive closure:** Every operation has a deny-by-default role/resource/state rule and immutable actor evidence.

**Negative closure:** Unauthorized, other-tenant, self-conflicting or model-origin actions are denied.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-006

**Account and session lifecycle contract**

Source: [docs/runtime-v1.md:60](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:60); [openspec/changes/implement-teacher-error-trainer/design.md:17](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/design.md:17).

**Already specified:** Real local accounts, hashed secrets/tokens, CSRF/same-origin and production rejection of development authentication are defined.

**Missing or conflicting:** The full account/role assignment lifecycle, session expiry/renewal/revocation, cookie policy, login throttling and local bootstrap recovery are not frozen product contracts. Existing foundation behavior is not a complete domain spec.

**Fill in:** Specify account creation/disable/role changes and session TTL/renewal/revocation/cookie/CSRF behavior; state whether password recovery is an operator-only local procedure or an in-scope UI.

**Positive closure:** Account/session transitions and revocation effects are defined for each actor and operation.

**Negative closure:** Disabled/expired/revoked sessions and unauthorized role assignment cannot authorize domain actions.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-007

**Case lifecycle transition and guard table**

Source: [openspec/changes/implement-teacher-error-trainer/design.md:46](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/design.md:46); [contracts/ground-truth.schema.json:29](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:29).

**Already specified:** Case states, main progression, quarantine, retirement and new-version immutability are defined.

**Missing or conflicting:** No exhaustive transition table binds each state pair to actor, guard, revision, evidence requirements, audit payload and invalid transition result; treatment of in-progress attempts during quarantine is unspecified.

**Fill in:** Complete the case transition table, including edit/re-render/re-review, quarantine/release, retirement, concurrent publication and the policy for already-started/evaluating attempts.

**Positive closure:** Every allowed transition specifies all guards/effects and all other transitions are denied.

**Negative closure:** Stale revisions, incomplete gates or forbidden transitions cannot alter a case.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-008

**Attempt and evaluation recovery transition table**

Source: [docs/runtime-v1.md:28](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:28); [contracts/attempt.schema.json:92](/Users/jekamas/projects/0xatelerix/tangerine/contracts/attempt.schema.json:92).

**Already specified:** Original save before providers, explicit user retry, 300-second lease and 270-second deadline are defined.

**Missing or conflicting:** State-specific field invariants, retry eligibility/limits, result lookup during a lease, interrupted evaluation, expired-lease takeover and case/policy changes at retry are not a complete transition contract.

**Fill in:** Define every attempt transition and HTTP outcome, exact recovery guards and allowed reuse, who can retry/review, and how an immutable case later quarantined or retired affects recovery.

**Positive closure:** A permitted retry preserves the original answer/case/policy and can commit only under its current lease/revision.

**Negative closure:** An active/stale lease, altered answer or forbidden state transition cannot create a final result.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-009

**Dispute and adjudicated result revision records**

Source: [docs/verification-v1.md:72](/Users/jekamas/projects/0xatelerix/tangerine/docs/verification-v1.md:72); [openspec/changes/implement-teacher-error-trainer/specs/v6-content-lifecycle/spec.md:31](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/specs/v6-content-lifecycle/spec.md:31).

**Already specified:** Plausible off-key claims require review; confirmed defects create a new case version and explicit result revision.

**Missing or conflicting:** There is no closed dispute/adjudication/result-revision schema, complete states, evidence visibility rule, reviewer selection or old-to-new unit mapping. Existing attempts affected by a corrected key have no explicit re-evaluation policy.

**Fill in:** Define dispute submit/review/resolve records and who can request a revision; specify mapping/recalculation versus preserved original scores, notifications/readback and which other historical attempts may be revised.

**Positive closure:** An authorized resolution appends a traceable new result with old answer/result/key references preserved.

**Negative closure:** A reviewer cannot silently overwrite scores, guess unit correspondences or revise unrelated attempts.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-010

**Independent blind-listening annotation contract**

Source: [docs/verification-v1.md:56](/Users/jekamas/projects/0xatelerix/tangerine/docs/verification-v1.md:56); [contracts/ground-truth.schema.json:1129](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:1129).

**Already specified:** Two qualified people listen before the planned key and record observations/intervals; review records contain phase and decision.

**Missing or conflicting:** The supplied record mostly references planned unit IDs plus free text. It lacks a structured independently discovered observation set, interval/category/control/uncertainty fields, frozen pre-key submission and key-disclosure event.

**Fill in:** Define the blind annotation schema and phase transition: independently observed units/controls, exact audio intervals, taxonomy uncertainty, original note, submit hash/time, then permitted correspondence with planned units and corrections.

**Positive closure:** A reviewer can save discoveries without seeing planned IDs; pre-key annotations remain immutable after disclosure.

**Negative closure:** Key-dependent labels, changed pre-key notes or post-key records cannot masquerade as independent blind evidence.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-011

**Reviewer independence and qualification records**

Source: [docs/verification-v1.md:58](/Users/jekamas/projects/0xatelerix/tangerine/docs/verification-v1.md:58); [contracts/ground-truth.schema.json:1110](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:1110).

**Already specified:** Two accounts belonging to one person are insufficient; acoustic review requires phonetics competence and disagreement requires a third adjudicator or blocking.

**Missing or conflicting:** Qualification record schema/authority/expiry, identity linkage, independence beyond duplicate accounts, author conflicts and adjudicator qualification/decision rules are unspecified.

**Fill in:** Define who verifies a person and qualification, accepted competence evidence, validity period and conflicts; specify third-adjudicator eligibility and whether two resolved final approvals must still be recorded after adjudication.

**Positive closure:** Each counted reviewer has valid authenticated person/qualification/conflict evidence for the exact review.

**Negative closure:** Alias identities, expired qualifications, missing competence or unresolved disagreement cannot approve publication.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-012

**Teacher-answer gold annotation data contract**

Source: [docs/corpus-acquisition.md:149](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:149); [contracts/corpus-record.schema.json:186](/Users/jekamas/projects/0xatelerix/tangerine/contracts/corpus-record.schema.json:186).

**Already specified:** Real answers and independent labels before model results are required for correct/partial/vague/repeated/contradictory/false/off-key classes.

**Missing or conflicting:** No closed teacher-answer annotation schema defines source spans, fragmentation, stance/category/repair/rationale judgments, expected mappings, uncertainty, rater identity, adjudication or frozen pre-model label sets.

**Fill in:** Define that gold record and annotation handbook, all required answer classes, how unknown/missing judgments are retained, and how labels bind the exact answer/case/policy/split.

**Positive closure:** Real answer gold preserves raw text and separate pre-adjudication labels with an auditable final mapping.

**Negative closure:** Model-seen labels, fabricated answers or missing substantive clauses cannot qualify as independent gold.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-013

**Detection-event boundaries and overlapping category resolution**

Source: [docs/contract-invariants.md:28](/Users/jekamas/projects/0xatelerix/tangerine/docs/contract-invariants.md:28); [domain/error-taxonomy.v1.yaml:46](/Users/jekamas/projects/0xatelerix/tangerine/domain/error-taxonomy.v1.yaml:46).

**Already specified:** All 122 leaves define inclusion/exclusion; use the narrowest supported category, separate independent repairs and retain secondary labels.

**Missing or conflicting:** No complete event-boundary/overlap handbook resolves equally narrow categories, shared repair spans, repeated occurrences, multi-utterance events or ambiguity across reporting domains.

**Fill in:** Specify the reviewed unitization procedure and ambiguity outcome for overlapping taxonomy cases; define identity of one event, independent repairs and primary versus secondary labels for each relevant contrast.

**Positive closure:** The same evidence supports one reproducible primary event count with explicit secondary labels or review.

**Negative closure:** Overlapping labels, ambiguous primary domains or repeated labels cannot inflate opportunities.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-014

**Frozen English/Russian aliases and taxonomy ancestors**

Source: [docs/scoring-v1.md:68](/Users/jekamas/projects/0xatelerix/tangerine/docs/scoring-v1.md:68); [audit/open-decisions.json:34](/Users/jekamas/projects/0xatelerix/tangerine/audit/open-decisions.json:34).

**Already specified:** Explicit categories earn separate credit; unknown synonyms must not be guessed.

**Missing or conflicting:** The approved bilingual alias map is absent. Accepted parent/family nodes, canonical spellings, ambiguous aliases, normalization and version migration are not enumerated.

**Fill in:** Supply exact English/Russian alias entries with target ID(s), parent-versus-leaf status, ambiguity behavior and normalization/version rules. Retain unresolved unknown wording.

**Positive closure:** Only an approved unambiguous explicit alias receives the declared category/hierarchy credit.

**Negative closure:** Unknown, ambiguous, invented or other-version aliases cannot earn guessed category credit.

**Decision links:** DEC-003.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-015

**Severity assignment and fixed weight binding**

Source: [contracts/ground-truth.schema.json:717](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:717); [contracts/ground-truth.schema.json:727](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:727).

**Already specified:** Four severity labels, weights 1–4 and FP weight one exist; weights are frozen before the answer.

**Missing or conflicting:** No severity rubric binds labels to weight values or explains whether labels and weights may vary independently; communication/context evidence and author/reviewer authority are unspecified.

**Fill in:** Define the severity rubric and exact severity-to-weight mapping, or explicitly authorize independent reviewed weights with required evidence. Do not change inherited composite weights.

**Positive closure:** Each case weight has an approved reproducible severity policy and pre-attempt record.

**Negative closure:** Post-answer weight changes or inconsistent unsupported severity assignments fail.

**Decision links:** DEC-008.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-016

**Rated difficulty evidence protocol**

Source: [contracts/ground-truth.schema.json:744](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:744); [contracts/case-candidate.schema.json:416](/Users/jekamas/projects/0xatelerix/tangerine/contracts/case-candidate.schema.json:416).

**Already specified:** Generated candidates are unrated; reviewed records allow easy/medium/hard/expert with evidence.

**Missing or conflicting:** No rating method, population, sample sufficiency or difficulty-to-evidence rule exists for the non-unrated enum values.

**Fill in:** Either freeze v1 difficulty to unrated everywhere until a separately specified study, or define the complete rating method and evidence requirements for every enabled rating.

**Positive closure:** A rated value is displayed only under its declared measurement protocol; otherwise it remains unrated.

**Negative closure:** Author intuition or unrelated corpus CEFR cannot become a measured difficulty rating.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-017

**Variety, register and judgment consistency table**

Source: [contracts/ground-truth.schema.json:64](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:64); [contracts/ground-truth.schema.json:351](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:351).

**Already specified:** Public variety/context constraints and separation of error, permitted variant and naturalness are mandatory.

**Missing or conflicting:** Accepted-variety/register strings have no registry or full expected_judgment/status_label/basis/eligibility compatibility table. Authoring conflict validation and public-context sufficiency lack a complete review rubric.

**Fill in:** Define allowed variety/register/basis values or an explicit reviewed free-text contract, permitted label combinations and required public facts for each context-dependent leaf.

**Positive closure:** Every scored context-dependent event uses a reviewed public constraint and compatible status/eligibility.

**Negative closure:** A hidden dialect constraint, incompatible status or accent preference cannot count as a true error.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-018

**Claim identity, extraction partition and completeness**

Source: [docs/contract-invariants.md:19](/Users/jekamas/projects/0xatelerix/tangerine/docs/contract-invariants.md:19); [contracts/claim-extraction.schema.json:233](/Users/jekamas/projects/0xatelerix/tangerine/contracts/claim-extraction.schema.json:233).

**Already specified:** Exact codepoint spans, server-assigned claim IDs and preservation of unparsed substantive text are required.

**Missing or conflicting:** Stable-ID construction, clause ordering, allowed span overlaps/nesting, attachment containment and checking that all substantive assertions were extracted or marked unparsed are not fully specified.

**Fill in:** Define the deterministic ID/order algorithm and extraction coverage rules, including repeated/overlapping spans, category-only comments, cross-clause correction attachments and unsupported omissions.

**Positive closure:** The frozen answer deterministically produces stable checked claims and explicit unresolved substantive coverage.

**Negative closure:** Fabricated/overlapping-invalid spans or silently omitted substantive assertions cannot score as complete.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-019

**Fragment consolidation, duplicate and retraction normalization**

Source: [docs/scoring-v1.md:99](/Users/jekamas/projects/0xatelerix/tangerine/docs/scoring-v1.md:99); [spec-inputs/v6-ste/reference/scorer.py:94](/Users/jekamas/projects/0xatelerix/tangerine/spec-inputs/v6-ste/reference/scorer.py:94).

**Already specified:** Exact duplicates count once; compatible fragments may combine; explicit retraction uses the final endorsed statement; contradictions require review.

**Missing or conflicting:** The transformation from several clauses to one unit decision is absent. The reference scorer rejects multiple nonduplicate assignments; exact grouping, attachment, retraction chains and provenance are not defined.

**Fill in:** Specify the normalization record/algorithm for compatible fragments, exact duplicates and scoped retractions, including ordering and transitive references; preserve each original clause and avoid best-of selection.

**Positive closure:** Compatible fragments form one traceable scorer decision and valid duplicates/retractions retain all source evidence.

**Negative closure:** Cycles, conflicting repairs or arbitrary last-write/best-of grouping cannot produce final credit.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-020

**Evaluator and cross-schema conditional truth tables**

Source: [contracts/evaluator-output.schema.json:252](/Users/jekamas/projects/0xatelerix/tangerine/contracts/evaluator-output.schema.json:252); [docs/contract-invariants.md:63](/Users/jekamas/projects/0xatelerix/tangerine/docs/contract-invariants.md:63).

**Already specified:** Closed structural schemas and several membership/stance/evidence invariants are supplied.

**Missing or conflicting:** A full permitted tuple table is absent for decision/unit/stance/reason/duplicate and supplied/option/propositions/status/unresolved_reason, and for candidate failure/realization/verification/review states.

**Fill in:** Specify every conditional required/null/empty/value relation and eligibility rule, with explicit reject versus review outcomes; include all 15 schemas and enum branches.

**Positive closure:** Every accepted cross-field tuple has a declared semantic invariant and derivation.

**Negative closure:** A structurally valid but contradictory tuple is rejected before publication/scoring.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-021

**Approved rationale registry and explanation-null binding**

Source: [spec-inputs/v6-ste/reference/validators.py:39](/Users/jekamas/projects/0xatelerix/tangerine/spec-inputs/v6-ste/reference/validators.py:39); [contracts/feedback.schema.json:29](/Users/jekamas/projects/0xatelerix/tangerine/contracts/feedback.schema.json:29); [contracts/ground-truth.schema.json:907](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:907).

**Already specified:** Key units have rationale propositions/text. The reference validator explicitly requires explanation.option_id=null; no explanation-option registry is needed under that rule.

**Missing or conflicting:** Feedback approved_rationale_ids still lacks an explicit identity/entity contract linking the unit rationale to approved text, language and evidence. The explanation-null requirement needs an active cross-field binding rather than inference from schema shape alone.

**Fill in:** Define the approved-rationale identities (ID, unit/version, language, approved text, evidence) and bind explanation.option_id=null explicitly across active schema invariants/prompts; do not invent explanation options.

**Positive closure:** Each explanation/feedback reference resolves to the exact approved unit/version/language record.

**Negative closure:** A nonexistent, correction-only, wrong-language or other-version rationale ID is rejected.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-022

**Semantic decisions to deterministic rubric and scorer input**

Source: [docs/scoring-v1.md:78](/Users/jekamas/projects/0xatelerix/tangerine/docs/scoring-v1.md:78); [contracts/scoring-input.schema.json:145](/Users/jekamas/projects/0xatelerix/tangerine/contracts/scoring-input.schema.json:145).

**Already specified:** q is satisfied required propositions / required propositions; forbidden assertions force zero, approved alternatives earn one, missing supplied work earns zero and novel alternatives require review.

**Missing or conflicting:** No complete binding algorithm selects a reviewed option, validates normalized alternative matches, maps proposition findings/status to exact fractions and converts excluded units/ignore/retractions into scorer records.

**Fill in:** Define this transformation field-by-field, including multiple alternatives, extra false clauses, ineligible corrections, null options, acceptable controls and exclusions. violated_proposition_ids already means forbidden propositions in data-dictionary.md.

**Positive closure:** Code derives exact fractions and sufficient statistics solely from validated source claims and fixed reviewed options.

**Negative closure:** Model fractions, teacher-unsupplied content or cherry-picked contradictory options cannot enter the scorer.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-023

**Mapper/auditor comparison equality contract**

Source: [docs/providers-v1.md:29](/Users/jekamas/projects/0xatelerix/tangerine/docs/providers-v1.md:29); [prompts/audit-map-v1.txt:4](/Users/jekamas/projects/0xatelerix/tangerine/prompts/audit-map-v1.txt:4).

**Already specified:** Audit is a separate blind-to-first-output consistency request; relevant disagreement requires review, never favorable retries.

**Missing or conflicting:** The canonical compared projection, set/order treatment, handling of duplicates/evidence/option/status/reasons and definition of score-relevant versus harmless differences are unspecified.

**Fill in:** Define comparison fields and normalization, with a difference-to-review table and records for both outputs. State how extraction-level stance differences can be compared when mapper outputs do not carry stance.

**Positive closure:** Two semantically equivalent records compare consistently without hiding any score-relevant difference.

**Negative closure:** Different target, option, stance or proposition credit cannot be ignored as harmless formatting.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-024

**Exact score transport, composite rational and numeric bounds**

Source: [docs/scoring-v1.md:111](/Users/jekamas/projects/0xatelerix/tangerine/docs/scoring-v1.md:111); [contracts/score-result.schema.json:4681](/Users/jekamas/projects/0xatelerix/tangerine/contracts/score-result.schema.json:4681).

**Already specified:** Core ratios retain exact numerator/denominator, sufficient statistics and one-decimal half-up displays; the composite formula is explicit.

**Missing or conflicting:** The composite has only a floating value and no exact fraction. Integer caps, safe cross-language representation, decimal serialization and complete display rounding for composite/auxiliary values are unspecified.

**Fill in:** Define exact composite storage/transport, all numeric ranges and overflow policy, serialization and display rules. Decide bounded JSON integers versus decimal-string arbitrary integers without silently weakening existing schemas.

**Positive closure:** Every score can be reproduced exactly across services from saved statistics and policy.

**Negative closure:** Overflow, binary-float drift or a rounded display reused as an exact value is rejected.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-025

**Auxiliary and provisional result response contracts**

Source: [domain/metrics.v1.yaml:235](/Users/jekamas/projects/0xatelerix/tangerine/domain/metrics.v1.yaml:235); [contracts/score-result.schema.json:103](/Users/jekamas/projects/0xatelerix/tangerine/contracts/score-result.schema.json:103).

**Already specified:** All 27 core and 15 auxiliary formulas are retained; unresolved decisions withhold final aggregates and unobserved teacher traits are null.

**Missing or conflicting:** The score-result schema enumerates core ratios only. No complete output shape binds auxiliary values/methods/units/missing reasons or provisional item evidence and review issue lists.

**Fill in:** Define the separate auxiliary/provisional result schema, each N/A/review/insufficient/not-observable reason, and exactly which evidence can be displayed pending adjudication.

**Positive closure:** All 42 named measurements have an explicit output location/status/method, without final aggregates for unresolved decisions.

**Negative closure:** Missing measurements cannot disappear, become zero/perfect, or be displayed as final confirmed misses.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-026

**Grounded bilingual feedback and missed-unit references**

Source: [contracts/feedback.schema.json:24](/Users/jekamas/projects/0xatelerix/tangerine/contracts/feedback.schema.json:24); [prompts/feedback-v1.txt:9](/Users/jekamas/projects/0xatelerix/tangerine/prompts/feedback-v1.txt:9).

**Already specified:** Feedback may explain validated findings/misses in English or Russian, cite reviewed material and introduce no new errors or grades.

**Missing or conflicting:** Missed units have no extracted teacher decision ID; the supplied feedback shape requires one. Approved bilingual rationale text/IDs and a deterministic check of free-text factual grounding are absent.

**Fill in:** Define feedback item types for detected/missed/false-positive/pending findings, their exact references and approved bilingual fallback text; define unsupported paraphrase handling and requested versus detected language.

**Positive closure:** Every feedback statement traces to a validated result or approved rationale in the selected language.

**Negative closure:** Invented decision IDs, new repairs/grades or untranslated unsupported fallback content fail.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-027

**Feedback-only failure versus evaluation-failure outcome**

Source: [docs/runtime-v1.md:40](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:40); [docs/runtime-v1.md:44](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:44).

**Already specified:** Metric computation and feedback are distinct; approved stored rationale is allowed if feedback fails.

**Missing or conflicting:** The blanket provider-failure status conflicts with an undefined completed-score-plus-fallback response. Persisted attempt/result state and HTTP status for feedback-only refusal/truncation/schema/timeout are not frozen.

**Fill in:** Specify the feedback-only failure exception and response/state table, including whether a valid score remains complete, how fallback provenance is represented and which explicit retry repeats only feedback.

**Positive closure:** Feedback failure preserves valid numeric evidence and shows an explicitly labelled approved fallback under the declared response status.

**Negative closure:** A failed semantic stage cannot use this fallback exception to fabricate a completed score.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-028

**Linguistic audit role prompt, schema and decisions**

Source: [audit/open-decisions.json:5](/Users/jekamas/projects/0xatelerix/tangerine/audit/open-decisions.json:5); [domain/providers.v1.yaml:13](/Users/jekamas/projects/0xatelerix/tangerine/domain/providers.v1.yaml:13).

**Already specified:** The role is advisory and configurable; a separate draft proposal exists, not an approved active contract.

**Missing or conflicting:** The active manifest has no exact linguistic-audit input/output/prompt version with target/span findings, refusal rules, allowed evidence and integration into candidate review.

**Fill in:** Resolve DEC-001 using the exact proposed or replacement input, prompt, closed schema and finding-to-candidate rules; record the scoped decision without treating a model as a human reviewer.

**Positive closure:** The selected active linguistic-audit contract is complete and version-bound before the role is enabled.

**Negative closure:** Reused unrelated schemas or invented human approvals cannot activate the role.

**Decision links:** DEC-001.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-029

**Complete role input and configuration binding schemas**

Source: [docs/llm-configuration.md:7](/Users/jekamas/projects/0xatelerix/tangerine/docs/llm-configuration.md:7); [prompts/manifest.yaml:1](/Users/jekamas/projects/0xatelerix/tangerine/prompts/manifest.yaml:1).

**Already specified:** Roles, profiles, prompt/schema hashes, disclosure boundaries, frozen identities and configurable DeepSeek development selection are described.

**Missing or conflicting:** There is no closed schema for each stage input DTO, effective role binding, configuration registry, provider receipt or stage-cache record. Required input fields and maximum sizes are mostly prose.

**Fill in:** Define all role inputs and operator binding records, their exact disclosure allowlists, version/hash derivation, required settings/defaults and receipt/cache keys, including tenant/authorization scope.

**Positive closure:** Each role receives only its complete permitted input under a frozen validated binding.

**Negative closure:** Extraction keys, raw identities, unknown settings or cross-tenant cached output cannot enter the role.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-030

**Provider-specific strict-schema projection and response parsing**

Source: [docs/contract-invariants.md:82](/Users/jekamas/projects/0xatelerix/tangerine/docs/contract-invariants.md:82); [domain/providers.configurable.v1.yaml:21](/Users/jekamas/projects/0xatelerix/tangerine/domain/providers.configurable.v1.yaml:21).

**Already specified:** The full application schemas cannot be weakened; unsupported wire projections block the profile.

**Missing or conflicting:** The per-provider supported keyword projection, preserved application validation mapping and responses output/refusal/incomplete parser are not specified. DeepSeek trusted-instruction and reasoning/output handling need exact transport rules.

**Fill in:** Define the OpenAI and DeepSeek transport adapters as specifications: instruction/input separation, reasoning effort, format payload, output-text selection, incomplete/refusal handling and every schema keyword disposition. Research notes resolve documented fields, not live support.

**Positive closure:** The adapter preserves every application constraint and accepts only a completed structurally and semantically valid stage payload.

**Negative closure:** Developer-as-user instructions, reasoning text, dropped constraints or JSON repair cannot become accepted stage output.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-031

**Retry, deadline and input/output capacity protocol**

Source: [docs/runtime-v1.md:32](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:32); [domain/providers.configurable.v1.yaml:18](/Users/jekamas/projects/0xatelerix/tangerine/domain/providers.configurable.v1.yaml:18).

**Already specified:** Stage/global deadlines, no semantic retries, explicit recovery and candidate generation/render attempt caps are present.

**Missing or conflicting:** Retry count scope (request versus stage), retryable status/error list, backoff within reserve, generation-attempt versus transport-attempt accounting, disconnect cancellation and prompt/token overflow are not complete contracts.

**Fill in:** Define retryable failures and counter scope, actual deadline propagation, generation budgets, input/output token estimation and deterministic oversize behavior without truncating claims or key content.

**Positive closure:** Every retry is counted and fits the remaining budget; oversized work returns the declared safe outcome with saved source input.

**Negative closure:** 429/5xx loops, reasoning-token exhaustion, silent truncation or late commits cannot bypass limits.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-032

**Typed render operator and hard-capability catalog**

Source: [contracts/render-plan.schema.json:91](/Users/jekamas/projects/0xatelerix/tangerine/contracts/render-plan.schema.json:91); [contracts/blueprint.schema.json:193](/Users/jekamas/projects/0xatelerix/tangerine/contracts/blueprint.schema.json:193).

**Already specified:** Four typed render operations and five capability names exist; arbitrary XML and remote audio are forbidden.

**Missing or conflicting:** Per-operator required/null fields, rate/pitch/pause ranges, locale/voice/capability compatibility and hard-constraint precedence/conflict rules are not closed. DEC-004 still uses unrestricted strings.

**Fill in:** Define the capability catalog and each operator payload/range, legal combinations and conflict results. State exactly which parameters constitute pace, accent, stress and prosody constraints.

**Positive closure:** A complete typed plan is validated against a fixed profile/capability catalog before synthesis.

**Negative closure:** Unknown hard constraints, irrelevant payload fields and incompatible voice/locale/target combinations fail.

**Decision links:** DEC-004.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-033

**SSML compilation and final-audio assembly specification**

Source: [docs/providers-v1.md:42](/Users/jekamas/projects/0xatelerix/tangerine/docs/providers-v1.md:42); [docs/providers-v1.md:48](/Users/jekamas/projects/0xatelerix/tangerine/docs/providers-v1.md:48).

**Already specified:** Azure REST, escaped typed SSML and a 24-kHz mono PCM16 master are prescribed; final bytes require review.

**Missing or conflicting:** The compiler grammar, per-turn call ordering, punctuation/prosody scope, concatenation/gaps, resampling, delivery codec, timestamp frame rounding and transformation manifest are not fully defined.

**Fill in:** Specify the exact SSML lowering and audio pipeline, including ordered turn-to-utterance mapping, sample/clock conversion, trimming/mixing/normalization policy and immutable final hash boundaries.

**Positive closure:** The final delivered asset and every turn/unit interval are reproducibly linked to exact plan and transformations.

**Negative closure:** A reordered turn, changed encoded file, unsupported phoneme or altered intentional target cannot inherit prior review.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-034

**Audio quality measurement method and boundary rules**

Source: [docs/verification-v1.md:26](/Users/jekamas/projects/0xatelerix/tangerine/docs/verification-v1.md:26); [docs/verification-v1.md:31](/Users/jekamas/projects/0xatelerix/tangerine/docs/verification-v1.md:31).

**Already specified:** Peak .9999, -18±2 LUFS, ≤-1 dBTP, silence thresholds and finite/mono/duration checks are specified.

**Missing or conflicting:** Loudness/true-peak algorithm/version, decoding/sample normalization, RMS hop/window-edge treatment, near-silence grouping and planned-pause overlap classification are absent.

**Fill in:** Define method versions and formulas/options for loudness/true peak/RMS, exact inclusive thresholds and interval rounding, all-silent/too-short/NaN treatment and how planned versus unplanned silence is decided.

**Positive closure:** Every QC value has its final-byte subject, method, unit and reproducible boundary classification.

**Negative closure:** A method-less value, padding-dependent silence or upstream-file measurement cannot approve final delivery.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-035

**Speech tokenizer, reviewed intervals and disfluency event rules**

Source: [domain/metrics.v1.yaml:253](/Users/jekamas/projects/0xatelerix/tangerine/domain/metrics.v1.yaml:253); [audit/open-decisions.json:62](/Users/jekamas/projects/0xatelerix/tangerine/audit/open-decisions.json:62).

**Already specified:** Elapsed speech includes internal pauses; articulation uses reviewed speech intervals; disfluency counts only reviewed events.

**Missing or conflicting:** Exact contraction/number/filler/repetition tokenization, interval union rules, active speech/pauses and countable disfluency event identities are absent.

**Fill in:** Resolve DEC-005 with the full tokenizer and interval/event protocol, including punctuation, partial words, overlaps, zero-duration and intended pause treatment.

**Positive closure:** Every rate/density numerator and denominator can be recomputed from a fixed reviewed annotation/method.

**Negative closure:** Different tokenizers, overlapping intervals or ordinary permitted fillers cannot produce comparable error metrics.

**Decision links:** DEC-005.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-036

**Prosody feature/unit/method and valid missingness table**

Source: [contracts/ground-truth.schema.json:563](/Users/jekamas/projects/0xatelerix/tangerine/contracts/ground-truth.schema.json:563); [audit/open-decisions.json:76](/Users/jekamas/projects/0xatelerix/tangerine/audit/open-decisions.json:76).

**Already specified:** Eleven named prosody features distinguish requested bounds, observation and evidence; unsupported numeric methods remain unavailable.

**Missing or conflicting:** There is no complete feature-to-unit/method table, F0 reference/log conversion, slope/range extraction, voiced-frame selection, syllable/phrase boundaries or label vocabularies.

**Fill in:** Resolve DEC-006 for every enabled feature: method/version, valid units, bounds, interval/voicing policy, evidence type and human-only/unknown outcome.

**Positive closure:** Every observed feature has a valid method/unit/subject combination and separates intended from measured values.

**Negative closure:** Invalid feature units, unvoiced F0 or provider naturalness scores cannot masquerade as measured target evidence.

**Decision links:** DEC-006.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-037

**ASR and pronunciation advisory normalization**

Source: [docs/providers-v1.md:65](/Users/jekamas/projects/0xatelerix/tangerine/docs/providers-v1.md:65); [domain/providers.v1.yaml:89](/Users/jekamas/projects/0xatelerix/tangerine/domain/providers.v1.yaml:89).

**Already specified:** Whisper raw hypothesis precedes alignment; Azure advisory chunks use 16-kHz mono PCM, max25s; prosody en-US only.

**Missing or conflicting:** Chunk boundaries/reference slices, overlap/stitching, tick/second-to-ms conversion, missing/NoMatch handling and typed provider-field normalization are incomplete.

**Fill in:** Define each raw response field retained, status/range/unit mapping and chunk-to-final-audio interval conversion; distinguish transport streaming from prohibited live product interaction.

**Positive closure:** Each advisory observation retains its raw response and exact final-audio/chunk/version mapping.

**Negative closure:** Missing fields, reference-conditioned scores or wrong offset units cannot create observed IPA or automatic gold.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-038

**Full synthetic target capability and canary specification**

Source: [domain/error-taxonomy.v1.yaml:35](/Users/jekamas/projects/0xatelerix/tangerine/domain/error-taxonomy.v1.yaml:35); [audit/open-decisions.json:90](/Users/jekamas/projects/0xatelerix/tangerine/audit/open-decisions.json:90).

**Already specified:** Every taxonomy target remains in scope; three render attempts then blocking; no active human-recording/provider fallback.

**Missing or conflicting:** Per-leaf/voice/locale target requests, observable realization criteria and canary change-detection protocol are incomplete. Taxonomy recording-route alternatives are not active profiles.

**Fill in:** Define target capability records for all 122 leaves/controls and acoustic feature combinations, exact observable success/failure and required review. Real DEC-007 calls are evidence work, not missing definitions.

**Positive closure:** Each target has a complete requested-versus-observed qualification contract, even if evidence later fails.

**Negative closure:** An unproven/failed target cannot be dropped, replaced or marked observed from SSML settings.

**Decision links:** DEC-007.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-039

**Full source manifest, legal scope and transformation contracts**

Source: [docs/corpus-acquisition.md:52](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:52); [contracts/corpus-record.schema.json:215](/Users/jekamas/projects/0xatelerix/tangerine/contracts/corpus-record.schema.json:215).

**Already specified:** Eight profiles, immutable raw records, private quarantine, full-release obligations and per-use rights are required.

**Missing or conflicting:** No closed release manifest/permissions/import report/transformation schema defines required components/count units, parser identities, checksums, rejection reconciliation and normalized grouping/label relations.

**Fill in:** Define those records for each profile, including release/source format, all files/partitions, observed counts and rights uses/expiry. Unknown acquisition hashes remain null pending evidence, not invented constants.

**Positive closure:** All acquired components/counts and rejected rows reconcile to an exact manifest with each transformation and allowed use.

**Negative closure:** Samples, omitted components, mixed releases or unapproved transfer cannot satisfy a full-source claim.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-040

**Complete SpeechOcean762 parser and source scale profile**

Source: [domain/corpus-sources.v1.yaml:24](/Users/jekamas/projects/0xatelerix/tangerine/domain/corpus-sources.v1.yaml:24); [docs/corpus-acquisition.md:72](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:72).

**Already specified:** Full train/test, raw scores and five raters are required; no phone substitution may be inferred from low accuracy.

**Missing or conflicting:** Source metadata spk2utt/spk2age/spk2gender is missing from the abbreviated plan. Complete field/scale/marker/raw-to-normalized profiles and approved ARPAbet↔IPA conversion are absent; docs illustrate differing completeness scales.

**Fill in:** Supply the exact selected release format and conversion tables; retain all metadata and scores-detail versus aggregate fields independently, define unknown/inserted phone markers and quarantine mixed scales.

**Positive closure:** All selected-release fields and raters are retained with declared source scales and original marker uncertainty.

**Negative closure:** Dropped child/speaker metadata, inferred phones, mixed scales or guessed IPA mapping fails full faithful import.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-041

**Complete L2-ARCTIC v5 read and suitcase parser profile**

Source: [domain/corpus-sources.v1.yaml:39](/Users/jekamas/projects/0xatelerix/tangerine/domain/corpus-sources.v1.yaml:39); [docs/corpus-acquisition.md:91](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:91).

**Already specified:** Full24-speaker read release and22-speaker suitcase extension remain required in the inventory; automatic/manual tiers stay distinct.

**Missing or conflicting:** No complete v5 directory/tier/marker grammar, CPL/PPL/s/a/d/err/* conversion profile, 44.1-kHz clock mapping or approved phone/taxonomy mapping is supplied.

**Fill in:** Specify the full v5 parser for README/LICENSE/PROMPTS and wav/transcript/textgrid/annotation plus suitcase; preserve all source labels before approved conversion and define unknown-tier quarantine.

**Positive closure:** Every component and manual/automatic label is retained with exact source-clock and annotation provenance.

**Negative closure:** Automatic alignments, err/* uncertainty or unsupported phone conversions cannot become manual narrow-category gold.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-042

**Complete W&I+LOCNESS and FCE v2.1 M2 parser profiles**

Source: [docs/corpus-acquisition.md:110](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:110); [audit/full-source-inventory.json:97](/Users/jekamas/projects/0xatelerix/tangerine/audit/full-source-inventory.json:97).

**Already specified:** Half-open source token spans, one-annotator edits, alternatives/noop and CEFR granularity are required; separate releases/licences retained.

**Missing or conflicting:** Approved ERRANT-to-project leaf mappings are absent; per-release partition metadata/group IDs, detection-only labels, historical fields, edit-order ties and full parser output schema are incomplete.

**Fill in:** Define both exact v2.1 profiles and mappings including noop, UNK/Um, insertions/overlaps/multiple alternatives and source token-to-codepoint correspondence. Specify handling of unavailable test labels; pin evaluation-tool version separately.

**Positive closure:** All supplied components/annotators/edits/native controls and original group metadata are faithfully retained.

**Negative closure:** Combined annotators, invented learner IDs/test labels or guessed narrow leaf mapping fails import.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-043

**EFCAMDAT full release and derivative ingest scope**

Source: [domain/corpus-sources.v1.yaml:81](/Users/jekamas/projects/0xatelerix/tangerine/domain/corpus-sources.v1.yaml:81); [audit/full-source-inventory.json:164](/Users/jekamas/projects/0xatelerix/tangerine/audit/full-source-inventory.json:164).

**Already specified:** Full second-release XML is identified; first release and cleaned/error-coded derivatives are distinct; baseline is discovery-only.

**Missing or conflicting:** The current full-source request and discovery-only baseline are not a completed ingest contract. Full XML schema, labels/offsets, prompt/task/learner grouping, selected derivative scope and permitted intended use are unspecified.

**Fill in:** Confirm second release only or also separately versioned Shatz2020/Oksuz2025 derivatives. Supply the applicable release schema/documentation and intended research/product/transfer use under an actual agreement. Access evidence remains separate.

**Positive closure:** Every selected EFCAMDAT release has its own complete component/parser/use contract.

**Negative closure:** Discovery metadata, cleaned subsets, inaccessible labels or academic access alone cannot satisfy full product ingest.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-044

**Doubao underlying study-record release contract**

Source: [domain/corpus-sources.v1.yaml:93](/Users/jekamas/projects/0xatelerix/tangerine/domain/corpus-sources.v1.yaml:93); [docs/corpus-acquisition.md:162](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:162).

**Already specified:** The study is a research reference; no supplied downloadable participant-record corpus or rights exists.

**Missing or conflicting:** There is no identified full release, schema, annotation inventory, participant grouping or permission contract for the reported study records.

**Fill in:** Provide an actual author-authorized release identifier/documentation, all recording/annotation components and allowed uses, or explicitly keep this source research-only with an unresolved all-corpora-acquired obligation. Do not invent545 assets.

**Positive closure:** A real full release contract or an explicit scoped research-only disposition is recorded without hiding missing data.

**Negative closure:** Paper sample counts or questionnaire percentages cannot stand in for an acquired labelled corpus.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-045

**Moodrick and NIR vendor-data scope and contracts**

Source: [domain/corpus-sources.v1.yaml:99](/Users/jekamas/projects/0xatelerix/tangerine/domain/corpus-sources.v1.yaml:99); [domain/corpus-sources.v1.yaml:105](/Users/jekamas/projects/0xatelerix/tangerine/domain/corpus-sources.v1.yaml:105).

**Already specified:** Both vendors are comparison sources; private answer banks/prompts/rubrics have no supplied data licence.

**Missing or conflicting:** No full annotated release or exact comparison-only versus corpus-ingest definition exists for both vendors under the latest full-source requirement.

**Fill in:** For each vendor separately, provide an authorized full-release data contract/rights or explicitly select public comparison-only scope. An all-sources-acquired claim remains blocked where no release exists.

**Positive closure:** Both vendor sources have exact documented scope and no fictional assets or inferred providers.

**Negative closure:** Product descriptions, demo percentages or another vendor product disclosure cannot qualify as this corpus.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-046

**Leakage grouping, split allocation and duplicate protocol**

Source: [docs/corpus-acquisition.md:38](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:38); [docs/corpus-acquisition.md:37](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:37).

**Already specified:** Development/calibration/holdout preserve related speaker/learner/script/derivative groups; upstream benchmark splits are retained.

**Missing or conflicting:** Canonical group identities, connection/duplicate equivalence, split allocation ratios/seed, upstream-versus-project split distinction and infeasible connected components are not specified.

**Fill in:** Define grouping/normalization/duplicate rules and assignment algorithm. Resolve cases where shared CMU prompts connect many L2 speakers into one component; do not weaken the speaker/script disjointness to manufacture holdout.

**Positive closure:** Frozen group manifests prove every intended independence boundary and report infeasible splits explicitly.

**Negative closure:** Connected derivatives/speakers/scripts cannot cross splits or be accepted through a changed leakage definition.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-047

**Gold stimulus, asset and negative-control counting**

Source: [docs/corpus-acquisition.md:120](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:120); [domain/validation-policy.yaml:7](/Users/jekamas/projects/0xatelerix/tangerine/domain/validation-policy.yaml:7).

**Already specified:** 122 leaves, six candidate stimuli per leaf/732 total and one contrast pair per split are preserved policy candidates.

**Missing or conflicting:** Counting unit for multi-target files, acceptable-variant counterparts, approved observations versus assets and independent pair families remains unresolved.

**Fill in:** Resolve DEC-002 with separate asset/stimulus/observation/pair/control counts and exact per-leaf/per-split counting, including permitted-variant leaves; do not alter the inherited floor implicitly.

**Positive closure:** Each leaf/control satisfies its approved counting rule with exact record IDs and independent final-audio reviews.

**Negative closure:** Multi-label files, duplicated stimuli or treating a permitted variant as an error cannot inflate coverage.

**Decision links:** DEC-002.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-048

**Agreement and semantic evaluation denominator protocols**

Source: [domain/metrics.v1.yaml:238](/Users/jekamas/projects/0xatelerix/tangerine/domain/metrics.v1.yaml:238); [domain/metrics.v1.yaml:275](/Users/jekamas/projects/0xatelerix/tangerine/domain/metrics.v1.yaml:275).

**Already specified:** Raw agreement/kappa and semantic coverage/exact mapping equations exist; pre-adjudication labels and abstentions must be retained.

**Missing or conflicting:** The annotation unit/label inventory, alignment and missing-rater handling, exact resolved/eligible/gold-decision definitions and class/stratum weighting are not specified enough to calculate comparable values.

**Fill in:** Define eligible events and label matching for each auxiliary evaluation metric, including ignored/meta/duplicates/retractions/key defects/abstentions and Cohen-kappa pairs. Preserve kappa undefined at N=0 or Pe=1.

**Positive closure:** Every numerator/denominator is traceable to the same frozen independently labelled population.

**Negative closure:** Adjudicated unanimity, dropped abstentions or changed eligibility cannot improve apparent agreement.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-049

**Elapsed attempt start and validated playback event contracts**

Source: [domain/metrics.v1.yaml:280](/Users/jekamas/projects/0xatelerix/tangerine/domain/metrics.v1.yaml:280); [contracts/attempt.schema.json:102](/Users/jekamas/projects/0xatelerix/tangerine/contracts/attempt.schema.json:102).

**Already specified:** Elapsed wall time and accepted play-event count are descriptive; client events do not prove listening.

**Missing or conflicting:** started_at is absent from attempt.schema; its trigger/clock/restart behavior is undefined. No playback-event schema/validation/deduplication or event transport contract exists.

**Fill in:** Define started_at creation and server-authoritative time semantics, plus event identity/type/audio/attempt/time validation, replay counting rules and duplicate/out-of-order handling.

**Positive closure:** Elapsed time and replay count recompute from declared saved timestamps and accepted event IDs.

**Negative closure:** Client-forged duration, duplicate plays or missing start cannot become an ability score.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-050

**Complete heldout acceptance protocol and critical cases**

Source: [domain/validation-policy.yaml:25](/Users/jekamas/projects/0xatelerix/tangerine/domain/validation-policy.yaml:25); [domain/validation-policy.yaml:29](/Users/jekamas/projects/0xatelerix/tangerine/domain/validation-policy.yaml:29).

**Already specified:** Mapping/coverage/correction/repeat gates have numeric limits and minimum denominators; every domain and fixed configuration requires evidence.

**Missing or conflicting:** Exact gold-mapping precision equality, correction-attempt eligibility, critical-counterexample inventory, domain assignment, three-run agreement estimator and configuration/prompt freeze protocol are incomplete.

**Fill in:** Define all acceptance calculations and critical case classes/approved oracle provenance, including pairwise versus unanimous repeat comparison and every denominator. Separate100 mapping decisions/domain from100 correction attempts/domain.

**Positive closure:** Each gate calculates the frozen defined statistic with adequate actual strata and untouched holdout evidence.

**Negative closure:** Tiny/subset domains, omitted critical failures or threshold tuning on exposed holdout cannot pass.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-051

**Retention, deletion and permission revocation lifecycle**

Source: [docs/corpus-acquisition.md:140](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:140); [contracts/approval-record.schema.json:68](/Users/jekamas/projects/0xatelerix/tangerine/contracts/approval-record.schema.json:68).

**Already specified:** Raw answers/evidence are immutable, private, consent-bound and tied to approved use; owner approvals can expire or be revoked.

**Missing or conflicting:** No exact retention periods or deletion/revocation contract reconciles immutable history, personal/source data, provider responses, backups and affected future use.

**Fill in:** Specify retention for each data class, who requests/authorizes deletion, tombstone/hash/history policy, revocation effects on existing cases/results and backup expiry. Specify required disclosure/consent text and version.

**Positive closure:** Each retained or deleted artifact has a defined permitted lifecycle and future transfer/publication guard.

**Negative closure:** Expired/revoked permission or a delete request cannot silently retain active use or destroy audit references inconsistently.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-052

**Request quotas, concurrency, costs and import resource bounds**

Source: [openspec/changes/implement-teacher-error-trainer/specs/v6-platform-foundation/spec.md:19](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/specs/v6-platform-foundation/spec.md:19); [docs/corpus-acquisition.md:24](/Users/jekamas/projects/0xatelerix/tangerine/docs/corpus-acquisition.md:24).

**Already specified:** Requests/costs are limited; provider usage is recorded; exhausted generation quotas cannot block permitted playback; imports must reject unbounded decompression.

**Missing or conflicting:** Numeric limits/units/reset rules, tenant/user concurrency, reservation/settlement, request/file/archive limits and exhausted-budget failure codes are absent.

**Fill in:** Choose limits/defaults/configuration authority for generation/evaluation/cost/concurrency and archive member/expanded-byte limits. Define failed/cancelled/retried usage accounting and playback exemption.

**Positive closure:** Usage/resource admission and settlement are deterministic under declared limits and concurrent requests.

**Negative closure:** Quota races, retry double charges, archive expansion or evaluation limits cannot bypass admission or block authorized playback.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-053

**Backup/restore consistency and compatibility protocol**

Source: [docs/runtime-v1.md:78](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:78); [openspec/changes/implement-teacher-error-trainer/design.md:35](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/design.md:35).

**Already specified:** Named volumes preserve data, migrations have checksums/locks and destructive reset needs operator confirmation.

**Missing or conflicting:** Full domain DB/media snapshot boundary, manifest schema, restore validation/order/rollback, schema/profile compatibility and historical private evidence coverage are not completely specified.

**Fill in:** Define the complete backup/restore manifest and ordered procedure, consistent snapshot identity, all included data classes, hash checks, compatibility guard, restore conflict behavior and recovery goals.

**Positive closure:** A validated compatible backup restores every declared domain/media reference and historical answer/result.

**Negative closure:** Missing assets, tampered manifests, incompatible migrations or an existing conflicting target cannot produce a healthy partial restore.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-054

**Complete deployment/configuration and release manifest schema**

Source: [docs/runtime-v1.md:82](/Users/jekamas/projects/0xatelerix/tangerine/docs/runtime-v1.md:82); [domain/providers.configurable.v1.yaml:2](/Users/jekamas/projects/0xatelerix/tangerine/domain/providers.configurable.v1.yaml:2).

**Already specified:** Topology, localhost port, server secrets, real services, exact workflow/tool pin and two architectures are required.

**Missing or conflicting:** No complete versioned runtime configuration schema covers domains/roles/provider bindings/limits/locale/timeouts/storage/migrations, all env types/defaults/validation or complete release artifact/provenance compatibility.

**Fill in:** Specify every configuration setting and its owner/container, validation/default/override/version rules; define release manifest linking exact images/dependencies/config schemas/migrations/prompts/policies and both-architecture evidence.

**Positive closure:** An operator supplies only declared local secrets/settings; all nonsecret release identities and compatibility are frozen.

**Negative closure:** Unknown settings, unresolved image references, leaked env or unqualified architecture cannot be accepted as a release.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._

## GAP-055

**Specification authority, version compatibility and drift closure**

Source: [docs/authority.md:3](/Users/jekamas/projects/0xatelerix/tangerine/docs/authority.md:3); [openspec/changes/implement-teacher-error-trainer/design.md:44](/Users/jekamas/projects/0xatelerix/tangerine/openspec/changes/implement-teacher-error-trainer/design.md:44).

**Already specified:** Current user scope outranks imported instructions; archive bytes remain immutable and source recovery is distinct from implementation.

**Missing or conflicting:** Multiple initial/recovered/overlay registries/specs and provisional implementation contain divergent contracts. No full active precedence/compatibility map or closure process binds every overlapping definition/version.

**Fill in:** Define the authoritative artifact for every domain, overlay order, version compatibility/migration/cache invalidation, and disposition of each divergence. Keep old evidence with its original proof boundary; no count-based gap-free declaration.

**Positive closure:** Every active requirement resolves to one consistent definition and every known gap has exact closure evidence.

**Negative closure:** Duplicate contradictory definitions, stale missing-file claims or structural counts cannot establish semantic completeness.

**Decision links:** No existing DEC covers this complete finding.

**Answer / artifact path / decision reference:** _Not supplied._
