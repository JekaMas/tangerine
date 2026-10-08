## ADDED Requirements

The current draft and exhaustive reconciliation are specification/v2/README.md and audit/full-release-reconciliation-20261008/gap-reconciliation.json. Source byte preservation, written definition, policy decision, genuine evidence and runtime acceptance are separate. GAP-005/006 remain superseded. The canonical task list stays in this change. All remaining subfindings and source contracts block a gap-free readiness claim.

### Requirement: SPEC-001 Complete product and internal API operation contracts

The application MUST implement the complete operation inventory through its declared closed request and response contracts.

The specification SHALL reconcile GAP-001 through `specification/v2/contracts/openapi.yaml` `specification/v2/domain/operations.yaml` `specification/v2/docs/interface-contract.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-006). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-001 Complete definition and rejection boundary
- **GIVEN** The exact GAP-001 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every in-scope operation has one versioned request/response/security/error contract and links to its flow and owner. An omitted operation, undefined payload/status or unbound route prevents an API-complete claim.

#### Scenario: SPEC-001 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-001`.
- **THEN** The local operator uses a listed preparation or teacher action. The response uses its named schema, status, and atomic effect.

#### Scenario: SPEC-001 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-001`.
- **THEN** An operation has an unknown field, stale revision, or unknown action. The API returns the declared error without a partial successful result.

#### Scenario: SPEC-001 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-002 Public and private transport projections

The API MUST apply the activity and phase allowlists. Before submission, the teacher response contains no key, transcript, count, or target category.

The specification SHALL reconcile GAP-002 through `specification/v2/contracts/library-item.schema.json` `specification/v2/contracts/teacher-start-view.schema.json` `specification/v2/contracts/prepare-view.schema.json` `specification/v2/contracts/key-disclosure.schema.json` `specification/v2/docs/interface-contract.md`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-002 Complete definition and rejection boundary
- **GIVEN** The exact GAP-002 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every activity/state projection emits only its explicitly allowed fields, including errors, caches and metadata. A hidden field in any pre-submit or blind-review projection is rejected.

#### Scenario: SPEC-002 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-002`.
- **THEN** A frozen submitted attempt requests its result. The response can show the exact full key under the selected disclosure policy.

#### Scenario: SPEC-002 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-002`.
- **THEN** An unsubmitted attempt or blind review requests a hidden field. The serializer omits it from payloads, errors, and media metadata.

#### Scenario: SPEC-002 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-003 Complete persistent entity and constraint model

Every persistent field MUST belong to a named closed schema and a typed immutable document. References MUST bind the exact kind, scope, and digest.

The specification SHALL reconcile GAP-003 through `specification/v2/db/schema.sql` `specification/v2/domain/persistence-map.json` `specification/v2/docs/persistence.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-006, FRC-010). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-003 Complete definition and rejection boundary
- **GIVEN** The exact GAP-003 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every field and reference maps to a declared durable entity/constraint and one immutable version identity. Dangling, cross-case/version, duplicate or mutable historical references fail the declared constraints.

#### Scenario: SPEC-003 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-003`.
- **THEN** A new domain document and its reference nodes commit. Its head, references, and audit event share one database transaction.

#### Scenario: SPEC-003 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-003`.
- **THEN** A reference points to another case or missing document. The operation cannot commit a healthy record.

#### Scenario: SPEC-003 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-004 Database and object-store commit protocol

The application MUST reserve an asset, store complete bytes, verify their read-back digest, and commit the owning reference in that order.

The specification SHALL reconcile GAP-004 through `specification/v2/contracts/asset.schema.json` `specification/v2/docs/runtime-and-storage.md`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-004 Complete definition and rejection boundary
- **GIVEN** The exact GAP-004 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Only a durable hash-verified immutable object can become visible through a committed authorized record. A partial upload, DB rollback, competing overwrite or crash cannot publish a missing or changed object.

#### Scenario: SPEC-004 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-004`.
- **THEN** Upload and read-back agree. The final owning transaction links the private immutable asset.

#### Scenario: SPEC-004 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-004`.
- **THEN** The process stops between upload and link. Recovery reports an orphan or pending reservation and never publishes missing bytes.

#### Scenario: SPEC-004 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

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

Case transitions MUST obey the exhaustive guard table. Quarantine MUST prevent new attempts and final score commits until resolved review.

The specification SHALL reconcile GAP-007 through `specification/v2/docs/lifecycle.md` `specification/v2/contracts/case-head.schema.json` `specification/v2/contracts/transition-request.schema.json`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-007 Complete definition and rejection boundary
- **GIVEN** The exact GAP-007 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every allowed transition specifies all guards/effects and all other transitions are denied. Stale revisions, incomplete gates or forbidden transitions cannot alter a case.

#### Scenario: SPEC-007 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-007`.
- **THEN** A verified case has matching final approvals and valid grants. Publication commits the same content and audio digests.

#### Scenario: SPEC-007 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-007`.
- **THEN** A quarantined case is retired. The unresolved quarantine flag remains and final evaluation stays blocked.

#### Scenario: SPEC-007 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-008 Attempt and evaluation recovery transition table

Submission MUST preserve the answer before provider work. Only the current lease epoch can commit a result against frozen inputs.

The specification SHALL reconcile GAP-008 through `specification/v2/contracts/attempt.schema.json` `specification/v2/docs/lifecycle.md` `specification/v2/docs/runtime-and-storage.md`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-008 Complete definition and rejection boundary
- **GIVEN** The exact GAP-008 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A permitted retry preserves the original answer/case/policy and can commit only under its current lease/revision. An active/stale lease, altered answer or forbidden state transition cannot create a final result.

#### Scenario: SPEC-008 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-008`.
- **THEN** An expired evaluation receives explicit recovery. The epoch increases and the exact answer, case, and policy stay fixed.

#### Scenario: SPEC-008 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-008`.
- **THEN** A delayed provider response arrives under a stale epoch or after the deadline. The result is retained as failed evidence and cannot become final.

#### Scenario: SPEC-008 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-009 Dispute and adjudicated result revision records

An adjudication MUST append a traceable result revision. It MUST NOT overwrite the original answer, audio, key, or result.

The specification SHALL reconcile GAP-009 through `specification/v2/contracts/dispute.schema.json` `specification/v2/contracts/adjudication.schema.json` `specification/v2/contracts/unit-correspondence.schema.json` `specification/v2/contracts/result-revision.schema.json` `specification/v2/docs/lifecycle.md`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-009 Complete definition and rejection boundary
- **GIVEN** The exact GAP-009 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** An authorized resolution appends a traceable new result with old answer/result/key references preserved. A reviewer cannot silently overwrite scores, guess unit correspondences or revise unrelated attempts.

#### Scenario: SPEC-009 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-009`.
- **THEN** The operator selects affected historical attempts after a reviewed key correction. New revisions use an explicit old-to-new unit map.

#### Scenario: SPEC-009 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-009`.
- **THEN** A replacement recording differs from the heard asset. The application cannot rescore the old listening attempt as though that recording was heard.

#### Scenario: SPEC-009 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-010 Independent blind-listening annotation contract

A blind review MUST save independently observed intervals, labels, uncertainty, and notes before the planned-key disclosure event.

The specification SHALL reconcile GAP-010 through `specification/v2/contracts/blind-annotation.schema.json` `specification/v2/contracts/review-context.schema.json` `specification/v2/contracts/disclosure-record.schema.json` `specification/v2/docs/review-and-gold.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-006). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-010 Complete definition and rejection boundary
- **GIVEN** The exact GAP-010 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A reviewer can save discoveries without seeing planned IDs; pre-key annotations remain immutable after disclosure. Key-dependent labels, changed pre-key notes or post-key records cannot masquerade as independent blind evidence.

#### Scenario: SPEC-010 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-010`.
- **THEN** A genuine reviewer submits observations. Their hash and time freeze before key correspondence becomes available.

#### Scenario: SPEC-010 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-010`.
- **THEN** The reviewer already saw the key or changes a submitted observation. The evidence cannot count as an original independent blind annotation.

#### Scenario: SPEC-010 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-011 Reviewer independence and qualification records

Counted reviews MUST reference distinct genuine people, applicable competence, declared conflicts, and the exact final artifact.

The specification SHALL reconcile GAP-011 through `specification/v2/contracts/person.schema.json` `specification/v2/contracts/qualification.schema.json` `specification/v2/contracts/review-decision.schema.json` `specification/v2/docs/review-and-gold.md`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-011 Complete definition and rejection boundary
- **GIVEN** The exact GAP-011 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each counted reviewer has genuine recorded person/qualification/conflict evidence for the exact review. Alias identities, expired qualifications, missing competence or unresolved disagreement cannot approve publication.

#### Scenario: SPEC-011 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-011`.
- **THEN** Two eligible people independently review final audio and resolve findings. Their actual final approvals can satisfy the human gate.

#### Scenario: SPEC-011 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-011`.
- **THEN** Two names describe one person, competence is unsupported, or the author reviews their own case. Publication cannot count those records as independent approvals.

#### Scenario: SPEC-011 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-012 Teacher-answer gold annotation data contract

Teacher gold MUST retain actual original answers, independent pre-model annotations, disagreement, and adjudicated expected mappings.

The specification SHALL reconcile GAP-012 through `specification/v2/contracts/teacher-gold.schema.json` `specification/v2/docs/review-and-gold.md` `specification/v2/docs/splits-and-validation.md`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-012 Complete definition and rejection boundary
- **GIVEN** The exact GAP-012 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Real answer gold preserves raw text and separate pre-adjudication labels with an auditable final mapping. Model-seen labels, fabricated answers or missing substantive clauses cannot qualify as independent gold.

#### Scenario: SPEC-012 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-012`.
- **THEN** Annotators label a real frozen answer before model output. Their original labels and final correspondence remain separate.

#### Scenario: SPEC-012 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-012`.
- **THEN** A generated answer or model-derived label is presented as independent human gold. It cannot satisfy heldout evidence.

#### Scenario: SPEC-012 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-013 Detection-event boundaries and overlapping category resolution

The reviewed unitization MUST count one independent repair obligation as one event and preserve secondary categories without extra denominator credit.

The specification SHALL reconcile GAP-013 through `specification/v2/docs/math-and-judgments.md` `specification/v2/domain/error-taxonomy.v1.yaml`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-013 Complete definition and rejection boundary
- **GIVEN** The exact GAP-013 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The same evidence supports one reproducible primary event count with explicit secondary labels or review. Overlapping labels, ambiguous primary domains or repeated labels cannot inflate opportunities.

#### Scenario: SPEC-013 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-013`.
- **THEN** Two repairs share a span but either repair leaves the other defect. The reviewed key retains two independent units with the rationale.

#### Scenario: SPEC-013 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-013`.
- **THEN** Two labels describe the same repair or equally supported primary domains remain unresolved. The application cannot inflate opportunities or choose a primary domain arbitrarily.

#### Scenario: SPEC-013 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-014 Frozen English/Russian aliases and taxonomy ancestors

Explicit category interpretation MUST use the frozen English/Russian registry. An unknown or ambiguous alias cannot receive a guessed narrow category.

The specification SHALL reconcile GAP-014 through `specification/v2/domain/category-aliases.v1.yaml` `specification/v2/docs/math-and-judgments.md`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-014 Complete definition and rejection boundary
- **GIVEN** The exact GAP-014 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Only an approved unambiguous explicit alias receives the declared category/hierarchy credit. Unknown, ambiguous, invented or other-version aliases cannot earn guessed category credit.

#### Scenario: SPEC-014 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-014`.
- **THEN** The teacher supplies one registered unambiguous term. The mapper uses that exact ancestor or leaf identity.

#### Scenario: SPEC-014 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-014`.
- **THEN** A term maps to multiple entries or a different registry version. The affected category decision remains unresolved.

#### Scenario: SPEC-014 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-015 Severity assignment and fixed weight binding

Severity MUST bind to the fixed 1-to-4 weight rubric before answer entry. False assertions retain weight one.

The specification SHALL reconcile GAP-015 through `specification/v2/domain/judgment-policy.yaml` `specification/v2/docs/review-and-gold.md` `specification/v2/docs/scoring-v1.md`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-015 Complete definition and rejection boundary
- **GIVEN** The exact GAP-015 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each case weight has an approved reproducible severity policy and pre-attempt record. Post-answer weight changes or inconsistent unsupported severity assignments fail.

#### Scenario: SPEC-015 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-015`.
- **THEN** Reviewers justify the context-specific severity under the fixed rubric. The immutable case records the corresponding weight.

#### Scenario: SPEC-015 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-015`.
- **THEN** An evaluator changes weight after it sees an answer. The score input fails the fixed-policy guard.

#### Scenario: SPEC-015 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-016 Rated difficulty evidence protocol

Difficulty labels MUST use the specified target population, actual first-exposure outcomes, sample floor, and Wilson interval bands. Otherwise the label is unrated.

The specification SHALL reconcile GAP-016 through `specification/v2/contracts/difficulty-study.schema.json` `specification/v2/docs/review-and-gold.md`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-016 Complete definition and rejection boundary
- **GIVEN** The exact GAP-016 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A rated value is displayed only under its declared measurement protocol; otherwise it remains unrated. Author intuition or unrelated corpus CEFR cannot become a measured difficulty rating.

#### Scenario: SPEC-016 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-016`.
- **THEN** The complete study evidence meets the frozen band rule. The display cites that study and its population.

#### Scenario: SPEC-016 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-016`.
- **THEN** The interval crosses bands or the sample is insufficient. The application keeps unrated and does not substitute author intuition or learner CEFR.

#### Scenario: SPEC-016 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-017 Variety, register and judgment consistency table

Context-dependent judgments MUST use a visible variety, register, and assessment basis compatible with the judgment table.

The specification SHALL reconcile GAP-017 through `specification/v2/domain/judgment-policy.yaml` `specification/v2/docs/review-and-gold.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-020). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-017 Complete definition and rejection boundary
- **GIVEN** The exact GAP-017 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every scored context-dependent event uses a reviewed public constraint and compatible status/eligibility. A hidden dialect constraint, incompatible status or accent preference cannot count as a true error.

#### Scenario: SPEC-017 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-017`.
- **THEN** The public task establishes the relevant constraint and reviewers support the target judgment. The unit can enter the declared error population.

#### Scenario: SPEC-017 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-017`.
- **THEN** The only basis is a hidden accent preference or an incompatible context label. The case cannot publish that unit as a true error.

#### Scenario: SPEC-017 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-018 Claim identity, extraction partition and completeness

Claim IDs MUST derive from the exact saved answer and Unicode spans. A disjoint coverage partition MUST preserve every substantive segment or mark it unresolved.

The specification SHALL reconcile GAP-018 through `specification/v2/contracts/claim-extraction.schema.json` `specification/v2/docs/math-and-judgments.md` `specification/v2/reference/validators_v2.py`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-018). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-018 Complete definition and rejection boundary
- **GIVEN** The exact GAP-018 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The frozen answer deterministically produces stable checked claims and explicit unresolved substantive coverage. Fabricated/overlapping-invalid spans or silently omitted substantive assertions cannot score as complete.

#### Scenario: SPEC-018 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-018`.
- **THEN** All exact spans and coverage cells agree with the frozen answer. The server assigns reproducible persistent identities.

#### Scenario: SPEC-018 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-018`.
- **THEN** A source quote is fabricated, an assertion is omitted, or identical spans carry conflicting interpretations. The extraction cannot enter completed scoring.

#### Scenario: SPEC-018 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-019 Fragment consolidation, duplicate and retraction normalization

Normalization MUST preserve all source clauses, combine only compatible fragments, and apply only explicit backward retractions.

The specification SHALL reconcile GAP-019 through `specification/v2/contracts/normalization.schema.json` `specification/v2/docs/math-and-judgments.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-018). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-019 Complete definition and rejection boundary
- **GIVEN** The exact GAP-019 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Compatible fragments form one traceable scorer decision and valid duplicates/retractions retain all source evidence. Cycles, conflicting repairs or arbitrary last-write/best-of grouping cannot produce final credit.

#### Scenario: SPEC-019 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-019`.
- **THEN** A later explicit retraction withdraws an earlier assertion. The final endorsed group retains both clauses and the retraction evidence.

#### Scenario: SPEC-019 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-019`.
- **THEN** Two unretracted repairs conflict or a relation forms a cycle. The group requires review rather than best-of or last-write credit.

#### Scenario: SPEC-019 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-020 Evaluator and cross-schema conditional truth tables

Structural validity MUST be followed by the declared cross-field, scope, null, and eligibility rules. An impossible tuple is rejected.

The specification SHALL reconcile GAP-020 through `specification/v2/docs/cross-field-invariants.md` `specification/v2/domain/semantic-invariants.yaml` `specification/v2/reference/validators_v2.py`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-018). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-020 Complete definition and rejection boundary
- **GIVEN** The exact GAP-020 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every accepted cross-field tuple has a declared semantic invariant and derivation. A structurally valid but contradictory tuple is rejected before publication/scoring.

#### Scenario: SPEC-020 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-020`.
- **THEN** A supplied correction, selected option, proposition sets, and verdict agree with the same source and unit. The tuple enters normalization.

#### Scenario: SPEC-020 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-020`.
- **THEN** A model reports accepted credit without supplied text, a foreign proposition, or an unresolved component in a resolved decision. The application rejects the tuple.

#### Scenario: SPEC-020 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-021 Approved rationale registry and explanation-null binding

Explanation option_id MUST remain null. Feedback rationale identities MUST resolve to the same case, unit, language, approved text, and evidence.

The specification SHALL reconcile GAP-021 through `specification/v2/contracts/rationale.schema.json` `specification/v2/contracts/evaluator-output.schema.json` `specification/v2/docs/math-and-judgments.md`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-021 Complete definition and rejection boundary
- **GIVEN** The exact GAP-021 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each explanation/feedback reference resolves to the exact approved unit/version/language record. A nonexistent, correction-only, wrong-language or other-version rationale ID is rejected.

#### Scenario: SPEC-021 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-021`.
- **THEN** A rationale ID resolves to the reviewed language-specific unit record. Feedback can cite its exact text.

#### Scenario: SPEC-021 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-021`.
- **THEN** A correction option is used as an explanation option or the rationale belongs to another language/version. The reference is rejected.

#### Scenario: SPEC-021 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-022 Semantic decisions to deterministic rubric and scorer input

Code MUST derive rubric fractions from fixed required and forbidden propositions. Models MUST NOT provide authoritative grades.

The specification SHALL reconcile GAP-022 through `specification/v2/docs/math-and-judgments.md` `specification/v2/contracts/scoring-input.schema.json` `specification/v2/reference/validators_v2.py` `specification/v2/reference/scorer.py`. Current definition status: `definition_incomplete_after_recheck`. FRC-018 requires the exact normalized multi-claim/retraction to scoring-input projection. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-022 Complete definition and rejection boundary
- **GIVEN** The exact GAP-022 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Code derives exact fractions and sufficient statistics solely from validated source claims and fixed reviewed options. Model fractions, teacher-unsupplied content or cherry-picked contradictory options cannot enter the scorer.

#### Scenario: SPEC-022 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-022`.
- **THEN** Required proposition findings resolve without forbidden assertions. Code calculates the exact satisfied-count fraction.

#### Scenario: SPEC-022 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-022`.
- **THEN** A supplied response includes a forbidden assertion or a plausible novel alternative. The first receives zero under the fixed rubric; the second requires review.

#### Scenario: SPEC-022 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-023 Mapper/auditor comparison equality contract

Mapper and auditor comparison MUST use the same frozen extraction and key, an exact compared projection, and explicit set normalization.

The specification SHALL reconcile GAP-023 through `specification/v2/docs/math-and-judgments.md` `specification/v2/contracts/mapping-input.schema.json` `specification/v2/prompts/audit-map-v1.txt`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-018). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-023 Complete definition and rejection boundary
- **GIVEN** The exact GAP-023 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Two semantically equivalent records compare consistently without hiding any score-relevant difference. Different target, option, stance or proposition credit cannot be ignored as harmless formatting.

#### Scenario: SPEC-023 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-023`.
- **THEN** Record order differs but all score-relevant fields and evidence meanings agree. The difference does not change the score.

#### Scenario: SPEC-023 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-023`.
- **THEN** The target, option, proposition credit, stance source, or exclusion differs. The result requires review and both outputs remain stored.

#### Scenario: SPEC-023 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-024 Exact score transport, composite rational and numeric bounds

Exact metric and composite fractions MUST use bounded decimal-string numerators and positive denominators. Display rounding MUST NOT feed another calculation.

The specification SHALL reconcile GAP-024 through `specification/v2/contracts/exact-rational.schema.json` `specification/v2/contracts/score-result.schema.json` `specification/v2/docs/math-and-judgments.md` `specification/v2/reference/scorer.py`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-024 Complete definition and rejection boundary
- **GIVEN** The exact GAP-024 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every score can be reproduced exactly across services from saved statistics and policy. Overflow, binary-float drift or a rounded display reused as an exact value is rejected.

#### Scenario: SPEC-024 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-024`.
- **THEN** A result crosses Python, JSON, Go, and browser boundaries. Its reduced rational stays identical.

#### Scenario: SPEC-024 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-024`.
- **THEN** A number overflows, a denominator is zero, or a rounded display is submitted as the exact value. The numeric contract rejects it or uses the declared unavailable state.

#### Scenario: SPEC-024 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-025 Auxiliary and provisional result response contracts

All 42 named measurements MUST have an output location and explicit availability, unit, method, and reason. Unresolved scores MUST remain provisional.

The specification SHALL reconcile GAP-025 through `specification/v2/contracts/auxiliary-results.schema.json` `specification/v2/contracts/result-envelope.schema.json` `specification/v2/domain/metrics.v1.yaml`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-025 Complete definition and rejection boundary
- **GIVEN** The exact GAP-025 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** All 42 named measurements have an explicit output location/status/method, without final aggregates for unresolved decisions. Missing measurements cannot disappear, become zero/perfect, or be displayed as final confirmed misses.

#### Scenario: SPEC-025 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-025`.
- **THEN** An observable auxiliary measure has a genuine method and source intervals. The response includes the measure with its actual evidence.

#### Scenario: SPEC-025 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-025`.
- **THEN** Teacher speech is unobserved or a semantic decision is pending. The corresponding field stays unavailable and no final aggregate or invented zero appears.

#### Scenario: SPEC-025 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-026 Grounded bilingual feedback and missed-unit references

Feedback MUST distinguish detected, missed, false-positive, acceptable, and pending items and use their valid reference types in the requested language.

The specification SHALL reconcile GAP-026 through `specification/v2/contracts/feedback.schema.json` `specification/v2/contracts/feedback-output.schema.json` `specification/v2/prompts/feedback-v1.txt` `specification/v2/docs/interface-contract.md`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-026 Complete definition and rejection boundary
- **GIVEN** The exact GAP-026 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every feedback statement traces to a validated result or approved rationale in the selected language. Invented decision IDs, new repairs/grades or untranslated unsupported fallback content fail.

#### Scenario: SPEC-026 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-026`.
- **THEN** A missed unit has no teacher claim. Its feedback references the real key unit and approved rationale without inventing a claim ID.

#### Scenario: SPEC-026 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-026`.
- **THEN** A generated explanation introduces a new correction, score, or unsupported observation. It cannot appear as confirmed feedback.

#### Scenario: SPEC-026 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-027 Feedback-only failure versus evaluation-failure outcome

A feedback-only failure MUST preserve a valid semantic score and show approved stored rationale or an explicit unavailable commentary state.

The specification SHALL reconcile GAP-027 through `specification/v2/docs/lifecycle.md` `specification/v2/contracts/result-envelope.schema.json` `specification/v2/contracts/retry-request.schema.json`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-027 Complete definition and rejection boundary
- **GIVEN** The exact GAP-027 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Feedback failure preserves valid numeric evidence and shows an explicitly labelled approved fallback under the declared response status. A failed semantic stage cannot use this fallback exception to fabricate a completed score.

#### Scenario: SPEC-027 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-027`.
- **THEN** The final feedback call times out after a valid score commit. An explicit feedback retry uses the same score and cannot re-map claims.

#### Scenario: SPEC-027 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-027`.
- **THEN** The mapper fails. The feedback exception cannot promote that attempt to a completed score.

#### Scenario: SPEC-027 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-028 Linguistic audit role prompt, schema and decisions

The advisory linguistic audit MUST use its exact prompt and closed input/output contract with source-bound findings. It cannot issue human or publication approval.

The specification SHALL reconcile GAP-028 through `specification/v2/contracts/linguistic-audit-input.schema.json` `specification/v2/contracts/linguistic-audit.schema.json` `specification/v2/prompts/linguistic-audit-v1.txt`. Current definition status: `policy_proposal_requires_explicit_decision_before_activation`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-028 Complete definition and rejection boundary
- **GIVEN** The exact GAP-028 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The selected active linguistic-audit contract is complete and version-bound before the role is enabled. Reused unrelated schemas or invented human approvals cannot activate the role.

#### Scenario: SPEC-028 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-028`.
- **THEN** The candidate contains an apparent untracked textual issue. The audit references its exact subject and span for human review.

#### Scenario: SPEC-028 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-028`.
- **THEN** The audit claims a heard phone from planned SSML or reports missing input as no_findings. The output fails its authority and status rules.

#### Scenario: SPEC-028 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-029 Complete role input and configuration binding schemas

Every model stage MUST receive its complete allowed input under a hashed provider, prompt, schema, policy, and permission binding.

The specification SHALL reconcile GAP-029 through `specification/v2/contracts/effective-binding.schema.json` `specification/v2/contracts/provider-receipt.schema.json` `specification/v2/contracts/stage-cache.schema.json` `specification/v2/contracts/taxonomy-context.schema.json` `specification/v2/prompts/manifest.yaml`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-006). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-029 Complete definition and rejection boundary
- **GIVEN** The exact GAP-029 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each role receives only its complete permitted input under a frozen validated binding. Extraction keys, raw identities, unknown settings or wrong-case/version cached output cannot enter the role.

#### Scenario: SPEC-029 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-029`.
- **THEN** The server supplies actual taxonomy definitions and authorized excerpts rather than inaccessible version IDs alone. The stage receipt records that exact payload.

#### Scenario: SPEC-029 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-029`.
- **THEN** Blind extraction receives the key, an unknown configuration field enters a stage, or a cache entry belongs to other inputs. The operation is rejected.

#### Scenario: SPEC-029 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-030 Provider-specific strict-schema projection and response parsing

Provider adapters MUST preserve full local constraints and accept only one completed visible output object under their documented transport.

The specification SHALL reconcile GAP-030 through `specification/v2/domain/schema-projection.yaml` `specification/v2/docs/provider-contracts.md`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-030 Complete definition and rejection boundary
- **GIVEN** The exact GAP-030 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The adapter preserves every application constraint and accepts only a completed structurally and semantically valid stage payload. Developer-as-user instructions, reasoning text, dropped constraints or JSON repair cannot become accepted stage output.

#### Scenario: SPEC-030 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-030`.
- **THEN** The documented wire projection returns a completed object. Full local schema and semantic checks still run.

#### Scenario: SPEC-030 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-030`.
- **THEN** Reasoning text, a refusal, incomplete output, ignored instruction placement, or JSON repair produces plausible text. The adapter cannot treat it as a successful stage.

#### Scenario: SPEC-030 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-031 Retry, deadline and input/output capacity protocol

One request-wide retry and deadline protocol MUST govern provider calls, cancellation, token capacity, and late writes.

The specification SHALL reconcile GAP-031 through `specification/v2/docs/runtime-and-storage.md` `specification/v2/domain/configuration-registry.yaml`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-012). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-031 Complete definition and rejection boundary
- **GIVEN** The exact GAP-031 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every retry is counted and fits the remaining budget; oversized work returns the declared safe outcome with saved source input. 429/5xx loops, reasoning-token exhaustion, silent truncation or late commits cannot bypass limits.

#### Scenario: SPEC-031 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-031`.
- **THEN** A retryable transport failure occurs with sufficient reserve and retry budget. One accounted retry can proceed.

#### Scenario: SPEC-031 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-031`.
- **THEN** The output is incomplete or the prompt exceeds capacity. The application preserves source input and fails without truncation or semantic retries.

#### Scenario: SPEC-031 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-032 Typed render operator and hard-capability catalog

The renderer MUST use only closed text, phoneme, pause, and prosody operations compatible with the selected voice and every hard constraint.

The specification SHALL reconcile GAP-032 through `specification/v2/contracts/render-constraint.schema.json` `specification/v2/contracts/render-plan.schema.json` `specification/v2/domain/audio-methods.yaml`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-009). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-032 Complete definition and rejection boundary
- **GIVEN** The exact GAP-032 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A complete typed plan is validated against a fixed profile/capability catalog before synthesis. Unknown hard constraints, irrelevant payload fields and incompatible voice/locale/target combinations fail.

#### Scenario: SPEC-032 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-032`.
- **THEN** The typed plan satisfies parameter ranges, scope, and known capability requirements. The compiler can issue the real synthesis call.

#### Scenario: SPEC-032 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-032`.
- **THEN** A voice/locale conflicts with a target or a constraint is unknown. The application fails before synthesis instead of dropping the requirement.

#### Scenario: SPEC-032 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-033 SSML compilation and final-audio assembly specification

SSML compilation and final assembly MUST preserve turn order and target scope and bind reviews to the actual delivered mono PCM16 24-kHz WAV.

The specification SHALL reconcile GAP-033 through `specification/v2/docs/audio-methods.md` `specification/v2/contracts/render-plan.schema.json` `specification/v2/contracts/transformation.schema.json`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-033 Complete definition and rejection boundary
- **GIVEN** The exact GAP-033 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The final delivered asset and every turn/unit interval are reproducibly linked to exact plan and transformations. A reordered turn, changed encoded file, unsupported phoneme or altered intentional target cannot inherit prior review.

#### Scenario: SPEC-033 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-033`.
- **THEN** The compiler escapes literal text and assembles turns with recorded offsets. The delivery hash identifies the reviewed bytes.

#### Scenario: SPEC-033 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-033`.
- **THEN** Encoding, normalization, trimming, or a turn order changes after review. Existing approval cannot transfer to that file.

#### Scenario: SPEC-033 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-034 Audio quality measurement method and boundary rules

Every quality threshold MUST use the declared decoding, loudness, peak, RMS, window, and interval method on final delivery bytes.

The specification SHALL reconcile GAP-034 through `specification/v2/docs/audio-methods.md` `specification/v2/domain/audio-methods.yaml` `specification/v2/contracts/audio-measurement.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-016). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-034 Complete definition and rejection boundary
- **GIVEN** The exact GAP-034 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every QC value has its final-byte subject, method, unit and reproducible boundary classification. A method-less value, padding-dependent silence or upstream-file measurement cannot approve final delivery.

#### Scenario: SPEC-034 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-034`.
- **THEN** The report includes actual finite measurements with their method version and boundary classification.

#### Scenario: SPEC-034 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-034`.
- **THEN** The recording is silent, too short, non-finite, or measured on an upstream file. The report cannot approve final audio.

#### Scenario: SPEC-034 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-035 Speech tokenizer, reviewed intervals and disfluency event rules

Speech rates and disfluency density MUST use the fixed tokenizer and reviewed interval/event rules, not estimated text length or an unversioned VAD.

The specification SHALL reconcile GAP-035 through `specification/v2/docs/audio-methods.md` `specification/v2/domain/audio-methods.yaml`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-016). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-035 Complete definition and rejection boundary
- **GIVEN** The exact GAP-035 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every rate/density numerator and denominator can be recomputed from a fixed reviewed annotation/method. Different tokenizers, overlapping intervals or ordinary permitted fillers cannot produce comparable error metrics.

#### Scenario: SPEC-035 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-035`.
- **THEN** Reviewed token events and interval unions are available. Each numerator and denominator can be recomputed.

#### Scenario: SPEC-035 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-035`.
- **THEN** A filler is automatically called an error or overlapping intervals count twice. The measurement is invalid.

#### Scenario: SPEC-035 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-036 Prosody feature/unit/method and valid missingness table

Each of the eleven prosody features MUST use its permitted unit, measurement or human annotation method, and explicit missingness rule.

The specification SHALL reconcile GAP-036 through `specification/v2/domain/audio-methods.yaml` `specification/v2/docs/audio-methods.md` `specification/v2/contracts/audio-measurement.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-009, FRC-016). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-036 Complete definition and rejection boundary
- **GIVEN** The exact GAP-036 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every observed feature has a valid method/unit/subject combination and separates intended from measured values. Invalid feature units, unvoiced F0 or provider naturalness scores cannot masquerade as measured target evidence.

#### Scenario: SPEC-036 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-036`.
- **THEN** A voiced F0 measurement has sufficient valid frames and the specified reference. The report stores the actual semitone result.

#### Scenario: SPEC-036 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-036`.
- **THEN** Unvoiced frames, provider naturalness, or requested settings are used as measured prosody. The observation is rejected or unavailable.

#### Scenario: SPEC-036 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-037 ASR and pronunciation advisory normalization

ASR and pronunciation scores MUST retain raw responses and exact chunk-to-final-audio clocks. They remain advisory, not inferred observed IPA.

The specification SHALL reconcile GAP-037 through `specification/v2/docs/audio-methods.md` `specification/v2/docs/provider-contracts.md` `specification/v2/contracts/evidence.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-016). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-037 Complete definition and rejection boundary
- **GIVEN** The exact GAP-037 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each advisory observation retains its raw response and exact final-audio/chunk/version mapping. Missing fields, reference-conditioned scores or wrong offset units cannot create observed IPA or automatic gold.

#### Scenario: SPEC-037 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-037`.
- **THEN** A pronunciation chunk has its actual source interval, reference slice, offsets, and provider scales. Its evidence stays linked to final bytes.

#### Scenario: SPEC-037 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-037`.
- **THEN** A missing or NoMatch field is converted to a perfect score, or a low score becomes a phone substitution. The conversion fails.

#### Scenario: SPEC-037 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-038 Full synthetic target capability and canary specification

Every taxonomy target and requested acoustic combination MUST have requested-versus-observed qualification evidence and a version-bound drift check.

The specification SHALL reconcile GAP-038 through `specification/v2/domain/target-capabilities.yaml` `specification/v2/contracts/capability-record.schema.json` `specification/v2/docs/audio-methods.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-009). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-038 Complete definition and rejection boundary
- **GIVEN** The exact GAP-038 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each target has a complete requested-versus-observed qualification contract, even if evidence later fails. An unproven/failed target cannot be dropped, replaced or marked observed from SSML settings.

#### Scenario: SPEC-038 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-038`.
- **THEN** An actual synthesis and two human observations satisfy the target-specific criteria for a fixed profile. That profile can use the qualification.

#### Scenario: SPEC-038 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-038`.
- **THEN** A target fails after the bounded render attempts. It remains a full-release blocker and cannot be omitted or replaced silently.

#### Scenario: SPEC-038 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-039 Full source manifest, legal scope and transformation contracts

Full-source ingestion MUST reconcile actual components, accepted and rejected records, transformations, permissions, and counts with one exact release manifest.

The specification SHALL reconcile GAP-039 through `specification/v2/contracts/source-release.schema.json` `specification/v2/contracts/permission-grant.schema.json` `specification/v2/contracts/import-report.schema.json` `specification/v2/contracts/transformation.schema.json` `specification/v2/docs/sources/acquisition-and-rights.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-017, FRC-019, FRC-021). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-039 Complete definition and rejection boundary
- **GIVEN** The exact GAP-039 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** All acquired components/counts and rejected rows reconcile to an exact manifest with each transformation and allowed use. Samples, omitted components, mixed releases or unapproved transfer cannot satisfy a full-source claim.

#### Scenario: SPEC-039 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-039`.
- **THEN** The imported release matches every required component and permitted use. Its raw and normalized identities remain traceable.

#### Scenario: SPEC-039 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-039`.
- **THEN** Only a sample is acquired or an external transfer lacks permission. The source cannot satisfy full acquisition or the proposed transfer.

#### Scenario: SPEC-039 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-040 Complete SpeechOcean762 parser and source scale profile

SpeechOcean762 ingestion MUST retain all selected partitions, metadata, aggregate/detail scores, five raters, source scales, and uncertain phone markers.

The specification SHALL reconcile GAP-040 through `specification/v2/docs/sources/speechocean762.md` `specification/v2/contracts/raw-record.schema.json` `specification/v2/domain/phone-symbols.yaml`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-017). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-040 Complete definition and rejection boundary
- **GIVEN** The exact GAP-040 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** All selected-release fields and raters are retained with declared source scales and original marker uncertainty. Dropped child/speaker metadata, inferred phones, mixed scales or guessed IPA mapping fails full faithful import.

#### Scenario: SPEC-040 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-040`.
- **THEN** All supplied components reconcile and original score layers remain independent.

#### Scenario: SPEC-040 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-040`.
- **THEN** An importer drops child metadata, mixes scales, or guesses a phone from low accuracy. It cannot pass faithful full import.

#### Scenario: SPEC-040 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-041 Complete L2-ARCTIC v5 read and suitcase parser profile

L2-ARCTIC v5 ingestion MUST preserve all read and suitcase components, clocks, original tiers, and manual-versus-automatic provenance.

The specification SHALL reconcile GAP-041 through `specification/v2/docs/sources/l2-arctic-v5.md` `specification/v2/contracts/raw-record.schema.json` `specification/v2/domain/phone-symbols.yaml`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-017). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-041 Complete definition and rejection boundary
- **GIVEN** The exact GAP-041 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every component and manual/automatic label is retained with exact source-clock and annotation provenance. Automatic alignments, err/* uncertainty or unsupported phone conversions cannot become manual narrow-category gold.

#### Scenario: SPEC-041 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-041`.
- **THEN** The read and suitcase inventories match the actual source release and retain CPL/PPL/edit labels.

#### Scenario: SPEC-041 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-041`.
- **THEN** Automatic alignments or uncertain err markers are converted into manual narrow-label gold. The conversion cannot be accepted.

#### Scenario: SPEC-041 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-042 Complete W&I+LOCNESS and FCE v2.1 M2 parser profiles

Each BEA v2.1 source MUST preserve token-to-codepoint positions, annotator alternatives, insertions, noop and detection-only labels, and unavailable test annotations.

The specification SHALL reconcile GAP-042 through `specification/v2/docs/sources/bea-v21.md` `specification/v2/domain/source-label-map.yaml` `specification/v2/contracts/raw-record.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-017). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-042 Complete definition and rejection boundary
- **GIVEN** The exact GAP-042 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** All supplied components/annotators/edits/native controls and original group metadata are faithfully retained. Combined annotators, invented learner IDs/test labels or guessed narrow leaf mapping fails import.

#### Scenario: SPEC-042 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-042`.
- **THEN** One original annotator layer is normalized without merging alternative edits. Raw tokens and labels remain recoverable.

#### Scenario: SPEC-042 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-042`.
- **THEN** The importer invents learner IDs, missing test labels, or an unsupported exact leaf mapping. The record remains unbound rather than invented gold.

#### Scenario: SPEC-042 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-043 EFCAMDAT full release and derivative ingest scope

The required EFCAMDAT scope MUST include R2, Shatz2020, and Oksuz2025 as separate releases. Each needs actual source-format and permitted-use bindings.

The specification SHALL reconcile GAP-043 through `specification/v2/docs/sources/efcamdat.md` `specification/v2/domain/corpus-sources.v1.yaml` `specification/v2/contracts/source-format-binding.schema.json`. Current definition status: `external_contract_missing`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-043 Complete definition and rejection boundary
- **GIVEN** The exact GAP-043 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every selected EFCAMDAT release has its own complete component/parser/use contract. Discovery metadata, cleaned subsets, inaccessible labels or academic access alone cannot satisfy full product ingest.

#### Scenario: SPEC-043 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-043`.
- **THEN** The operator supplies authorized source files, real documentation, and matching mappings for each release. Full ingestion reconciles them separately.

#### Scenario: SPEC-043 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-043`.
- **THEN** Workbook headers, labels, or rights remain unavailable. A generic schema or a cleaned subset cannot falsely satisfy the missing native release contract.

#### Scenario: SPEC-043 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-044 Doubao underlying study-record release contract

Study-record ingestion MUST require an actual author-authorized Doubao release and participant-use scope. Paper metadata cannot create recordings.

The specification SHALL reconcile GAP-044 through `specification/v2/docs/sources/private-vendors-and-study.md` `specification/v2/contracts/source-release.schema.json` `specification/v2/domain/corpus-sources.v1.yaml`. Current definition status: `external_contract_missing`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-044 Complete definition and rejection boundary
- **GIVEN** The exact GAP-044 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A real full release contract or an explicit scoped research-only disposition is recorded without hiding missing data. Paper sample counts or questionnaire percentages cannot stand in for an acquired labelled corpus.

#### Scenario: SPEC-044 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-044`.
- **THEN** An authorized complete release identifies its files, participant groups, annotation format, and permitted uses. It can enter the normal import protocol.

#### Scenario: SPEC-044 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-044`.
- **THEN** Only the paper and sample counts exist. Record access remains unavailable and the full-source obligation is not reported complete.

#### Scenario: SPEC-044 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-045 Moodrick and NIR vendor-data scope and contracts

Moodrick and NIR MUST have separate licensed or authorized private-source bindings. Account references cannot substitute for data rights or a documented interface.

The specification SHALL reconcile GAP-045 through `specification/v2/docs/sources/private-vendors-and-study.md` `specification/v2/contracts/connector-configuration.schema.json` `specification/v2/contracts/source-format-binding.schema.json`. Current definition status: `external_contract_missing`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-045 Complete definition and rejection boundary
- **GIVEN** The exact GAP-045 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Both vendor sources have exact documented scope and no fictional assets or inferred providers. Product descriptions, demo percentages or another vendor product disclosure cannot qualify as this corpus.

#### Scenario: SPEC-045 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-045`.
- **THEN** A real authorized export or documented API contract is supplied with the appropriate credential reference. The source uses only its permitted operations.

#### Scenario: SPEC-045 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-045`.
- **THEN** Only public descriptions or a key exist without an authorized interface and release. No private answer bank, endpoint, or source asset is invented.

#### Scenario: SPEC-045 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-046 Leakage grouping, split allocation and duplicate protocol

Split allocation MUST preserve connected speaker, learner, script, task, and derivative groups under the fixed policy and retain upstream splits separately.

The specification SHALL reconcile GAP-046 through `specification/v2/docs/splits-and-validation.md` `specification/v2/contracts/split-manifest.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-008). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-046 Complete definition and rejection boundary
- **GIVEN** The exact GAP-046 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Frozen group manifests prove every intended independence boundary and report infeasible splits explicitly. Connected derivatives/speakers/scripts cannot cross splits or be accepted through a changed leakage definition.

#### Scenario: SPEC-046 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-046`.
- **THEN** Independent connected components admit the chosen allocation. The frozen manifest records every member and seed.

#### Scenario: SPEC-046 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-046`.
- **THEN** Shared prompts create one giant connected component. The procedure reports insufficient independent groups rather than weakening leakage boundaries.

#### Scenario: SPEC-046 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-047 Gold stimulus, asset and negative-control counting

Gold coverage MUST count assets, stimuli, target observations, pair families, and controls separately and retain the 732 distinct-stimulus floor.

The specification SHALL reconcile GAP-047 through `specification/v2/docs/review-and-gold.md` `specification/v2/domain/validation-policy.yaml`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-008, FRC-009, FRC-020, FRC-021). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-047 Complete definition and rejection boundary
- **GIVEN** The exact GAP-047 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each leaf/control satisfies its approved counting rule with exact record IDs and independent final-audio reviews. Multi-label files, duplicated stimuli or treating a permitted variant as an error cannot inflate coverage.

#### Scenario: SPEC-047 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-047`.
- **THEN** Each leaf has three independent contrast-pair families, one per split, with actual final-audio review.

#### Scenario: SPEC-047 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-047`.
- **THEN** One multi-target file is counted as many independent stimuli or an acceptable variant is labeled erroneous to meet the count. Coverage fails.

#### Scenario: SPEC-047 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-048 Agreement and semantic evaluation denominator protocols

Agreement and semantic metrics MUST use the declared fixed event populations and retain missing labels, abstentions, and pre-adjudication disagreement.

The specification SHALL reconcile GAP-048 through `specification/v2/docs/math-and-judgments.md` `specification/v2/docs/splits-and-validation.md` `specification/v2/contracts/holdout-report.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-015, FRC-020). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-048 Complete definition and rejection boundary
- **GIVEN** The exact GAP-048 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every numerator/denominator is traceable to the same frozen independently labelled population. Adjudicated unanimity, dropped abstentions or changed eligibility cannot improve apparent agreement.

#### Scenario: SPEC-048 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-048`.
- **THEN** The same independent rater pair labels aligned events. Raw marginals define agreement and kappa.

#### Scenario: SPEC-048 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-048`.
- **THEN** Adjudicated unanimity replaces the original labels or abstentions disappear from coverage. The reported statistic cannot pass.

#### Scenario: SPEC-048 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-049 Elapsed attempt start and validated playback event contracts

Attempt elapsed time MUST use the database start and submission clocks. Play counts MUST use deduplicated validated events bound to the heard asset.

The specification SHALL reconcile GAP-049 through `specification/v2/contracts/attempt.schema.json` `specification/v2/contracts/playback-event.schema.json` `specification/v2/docs/interface-contract.md`. Current definition status: `written_definition_supplied_not_runtime_accepted`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json. An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-049 Complete definition and rejection boundary
- **GIVEN** The exact GAP-049 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Elapsed time and replay count recompute from declared saved timestamps and accepted event IDs. Client-forged duration, duplicate plays or missing start cannot become an ability score.

#### Scenario: SPEC-049 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-049`.
- **THEN** A repeated event ID arrives with the same payload. It is accepted idempotently and does not add another play.

#### Scenario: SPEC-049 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-049`.
- **THEN** A client supplies another asset, an impossible time, or a changed payload under the same event ID. It cannot affect telemetry or ability scores.

#### Scenario: SPEC-049 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-050 Complete heldout acceptance protocol and critical cases

Release acceptance MUST use frozen configuration, genuine heldout labels, exact compared decisions, separate sample floors, and all critical cases.

The specification SHALL reconcile GAP-050 through `specification/v2/docs/splits-and-validation.md` `specification/v2/domain/validation-policy.yaml` `specification/v2/contracts/holdout-report.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-015, FRC-020). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-050 Complete definition and rejection boundary
- **GIVEN** The exact GAP-050 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each gate calculates the frozen defined statistic with adequate actual strata and untouched holdout evidence. Tiny/subset domains, omitted critical failures or threshold tuning on exposed holdout cannot pass.

#### Scenario: SPEC-050 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-050`.
- **THEN** Every domain satisfies the fixed sample and metric gates using untouched holdout evidence. The report cites actual manifests and receipts.

#### Scenario: SPEC-050 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-050`.
- **THEN** The holdout is exposed, a domain is too small, or a critical case fails. Overall averages cannot hide the failed gate.

#### Scenario: SPEC-050 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-051 Retention, deletion and permission revocation lifecycle

Retention and erasure MUST respect actual source and person restrictions and apply revocation before future display, transfer, restoration, or reuse.

The specification SHALL reconcile GAP-051 through `specification/v2/docs/maintenance-and-limits.md` `specification/v2/contracts/deletion-request.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-010). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-051 Complete definition and rejection boundary
- **GIVEN** The exact GAP-051 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Each retained or deleted artifact has a defined permitted lifecycle and future transfer/publication guard. Expired/revoked permission or a delete request cannot silently retain active use or destroy audit references inconsistently.

#### Scenario: SPEC-051 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-051`.
- **THEN** A confirmed erasure plan removes restricted bytes and preserves only expressly permitted tombstones.

#### Scenario: SPEC-051 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-051`.
- **THEN** A backup would restore revoked active content. Restore must reapply the revocation/deletion ledger before serving it.

#### Scenario: SPEC-051 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-052 Request quotas, concurrency, costs and import resource bounds

One local resource policy MUST bound expensive concurrency, request capacity, cost reservations, and safe archive expansion without disabling stored playback.

The specification SHALL reconcile GAP-052 through `specification/v2/domain/configuration-registry.yaml` `specification/v2/contracts/configuration.schema.json` `specification/v2/docs/maintenance-and-limits.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-012, FRC-017). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-052 Complete definition and rejection boundary
- **GIVEN** The exact GAP-052 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Usage/resource admission and settlement are deterministic under declared limits and concurrent requests. Quota races, retry double charges, archive expansion or evaluation limits cannot bypass admission or block authorized playback.

#### Scenario: SPEC-052 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-052`.
- **THEN** A request fits the exact limits and has a known accounted price bound. One expensive foreground operation is admitted.

#### Scenario: SPEC-052 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-052`.
- **THEN** Unknown charge exposure, excessive decompression, or an exhausted budget violates admission. The operation fails rather than truncating required content.

#### Scenario: SPEC-052 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-053 Backup/restore consistency and compatibility protocol

Backup and restore MUST use a consistent database/media/evidence boundary, exact hashes, compatibility checks, and non-destructive target activation.

The specification SHALL reconcile GAP-053 through `specification/v2/contracts/backup-manifest.schema.json` `specification/v2/docs/maintenance-and-limits.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-010). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-053 Complete definition and rejection boundary
- **GIVEN** The exact GAP-053 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** A validated compatible backup restores every declared domain/media reference and historical answer/result. Missing assets, tampered manifests, incompatible migrations or an existing conflicting target cannot produce a healthy partial restore.

#### Scenario: SPEC-053 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-053`.
- **THEN** A complete verified backup restores into an inactive target and passes reference checks before activation.

#### Scenario: SPEC-053 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-053`.
- **THEN** A component is missing, a digest fails, or a schema is incompatible. The original workspace remains active and no partial restore reports success.

#### Scenario: SPEC-053 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-054 Basic GitHub download-and-run setup

The project MUST implement the exact simple GitHub source-download setup defined in specification/v2/docs/local-delivery.md. No prebuilt application images or formal software release manifest is required.

The specification SHALL reconcile GAP-054 through `specification/v2/docs/local-delivery.md` `specification/v2/domain/configuration-registry.yaml` `specification/v2/contracts/configuration.schema.json`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-019, FRC-021). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-054 Complete definition and rejection boundary
- **GIVEN** The exact GAP-054 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** The extracted source contains a complete documented local setup using provider keys and supplied defaults; required internal infrastructure is automatic. Missing prerequisites/build inputs, invalid settings or a failed build yield clear errors without success, manual account/database setup or browser-visible secrets.

#### Scenario: SPEC-054 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-054`.
- **THEN** A qualified release starts the real stack on loopback with persistent data and no account setup.

#### Scenario: SPEC-054 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-054`.
- **THEN** Images are missing, a secret is exposed, or an architecture lacks qualification. The launcher cannot claim a completed first release.

#### Scenario: SPEC-054 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.

### Requirement: SPEC-055 Specification authority, version compatibility and drift closure

Each domain MUST resolve to one active artifact and exact compatible versions. Unavailable repository bytes MUST NOT be claimed integrated.

The specification SHALL reconcile GAP-055 through `specification/v2/docs/authority.md` `audit/full-release-reconciliation-20261008/import-manifest.json` `specification/v2/domain/version-compatibility.yaml` `specification/v2/README.md` `specification/v2/docs/migration-compatibility.md` `audit/full-release-reconciliation-20261008/repository-drift.md`. Current definition status: `definition_incomplete_after_recheck`. The exact remaining input and contradictions are in audit/full-release-reconciliation-20261008/REMAINING-GAPS.md and findings.json (FRC-010). An authored policy, generic schema or imported approval cannot substitute for the exact actual decision, source contract or evidence. This specification-only update does not claim implementation or empirical closure.

#### Scenario: SPEC-055 Complete definition and rejection boundary
- **GIVEN** The exact GAP-055 contract and its source references are under review.
- **WHEN** Its supported behavior and omitted or contradictory boundary are checked.
- **THEN** Every active requirement resolves to one consistent definition and every known gap has exact closure evidence. Duplicate contradictory definitions, stale missing-file claims or structural counts cannot establish semantic completeness.

#### Scenario: SPEC-055 The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-055`.
- **THEN** An implementer compares the supplied package against the real current checkout and records every accepted migration or conflict.

#### Scenario: SPEC-055 An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-055`.
- **THEN** Historical account requirements reappear or a structural count substitutes for semantic integration evidence. The integration gate remains blocked.

#### Scenario: SPEC-055 No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
