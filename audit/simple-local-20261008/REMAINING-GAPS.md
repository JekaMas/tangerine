# Full remaining specification gaps — Tangerine

This is the complete current list of **53 grouped definition gaps** after the simple-local scope change. A grouped gap may contain several missing fields/rules; 53 is not an atomic subfield count or a claim of absolute completeness. The full taxonomy, schemas, five original prompts and formulas have been recovered. The missing definitions below are the rules needed to bind them into one complete product specification.

**33 engineering definitions** can be drafted by engineering. **20 input items** consist of 11 product choices, six linguistic policies and three source-owner items. You do not need to design internal APIs, database tables or serialization yourself. Product/linguistic/source inputs are identified on every entry. Reply by GAP ID; engineering items can be assigned to engineering rather than answered field by field.

The product remains one local workspace with provider keys and no accounts, sessions, access roles, tenants or public API setup. GAP-005 and GAP-006 are superseded and excluded. Internal contracts are implementation details. Reviewer qualifications and actual source-use permissions remain evidence responsibilities.

“Already specified” describes existing definitions, not implementation or observation. “Needed to close” names the artifact or decision required. Positive/negative closure criteria describe the later checks; they are not newly executed tests. Actual recordings, permissions, provider behavior, reviewer observations and runtime acceptance remain separate evidence obligations.

The references preserve historical audit anchors. Line numbers are from the earlier audit snapshot and may differ in revised active files; the current active requirement IDs and source anchors disambiguate them.

## Index

- [GAP-001 — Complete product and internal API operation contracts](#gap-001) (engineering definition)
- [GAP-002 — Public and private transport projections](#gap-002) (product choice)
- [GAP-003 — Complete persistent entity and constraint model](#gap-003) (engineering definition)
- [GAP-004 — Database and object-store commit protocol](#gap-004) (engineering definition)
- [GAP-007 — Case lifecycle transition and guard table](#gap-007) (product choice)
- [GAP-008 — Attempt and evaluation recovery transition table](#gap-008) (engineering definition)
- [GAP-009 — Dispute and adjudicated result revision records](#gap-009) (product choice)
- [GAP-010 — Independent blind-listening annotation contract](#gap-010) (engineering definition)
- [GAP-011 — Reviewer independence and qualification records](#gap-011) (product choice)
- [GAP-012 — Teacher-answer gold annotation data contract](#gap-012) (engineering definition)
- [GAP-013 — Detection-event boundaries and overlapping category resolution](#gap-013) (engineering definition)
- [GAP-014 — Frozen English/Russian aliases and taxonomy ancestors](#gap-014) (linguistic policy)
- [GAP-015 — Severity assignment and fixed weight binding](#gap-015) (product choice)
- [GAP-016 — Rated difficulty evidence protocol](#gap-016) (product choice)
- [GAP-017 — Variety, register and judgment consistency table](#gap-017) (linguistic policy)
- [GAP-018 — Claim identity, extraction partition and completeness](#gap-018) (engineering definition)
- [GAP-019 — Fragment consolidation, duplicate and retraction normalization](#gap-019) (engineering definition)
- [GAP-020 — Evaluator and cross-schema conditional truth tables](#gap-020) (engineering definition)
- [GAP-021 — Approved rationale registry and explanation-null binding](#gap-021) (engineering definition)
- [GAP-022 — Semantic decisions to deterministic rubric and scorer input](#gap-022) (engineering definition)
- [GAP-023 — Mapper/auditor comparison equality contract](#gap-023) (engineering definition)
- [GAP-024 — Exact score transport, composite rational and numeric bounds](#gap-024) (engineering definition)
- [GAP-025 — Auxiliary and provisional result response contracts](#gap-025) (engineering definition)
- [GAP-026 — Grounded bilingual feedback and missed-unit references](#gap-026) (engineering definition)
- [GAP-027 — Feedback-only failure versus evaluation-failure outcome](#gap-027) (product choice)
- [GAP-028 — Linguistic audit role prompt, schema and decisions](#gap-028) (linguistic policy)
- [GAP-029 — Complete role input and configuration binding schemas](#gap-029) (engineering definition)
- [GAP-030 — Provider-specific strict-schema projection and response parsing](#gap-030) (engineering definition)
- [GAP-031 — Retry, deadline and input/output capacity protocol](#gap-031) (engineering definition)
- [GAP-032 — Typed render operator and hard-capability catalog](#gap-032) (product choice)
- [GAP-033 — SSML compilation and final-audio assembly specification](#gap-033) (engineering definition)
- [GAP-034 — Audio quality measurement method and boundary rules](#gap-034) (engineering definition)
- [GAP-035 — Speech tokenizer, reviewed intervals and disfluency event rules](#gap-035) (linguistic policy)
- [GAP-036 — Prosody feature/unit/method and valid missingness table](#gap-036) (linguistic policy)
- [GAP-037 — ASR and pronunciation advisory normalization](#gap-037) (engineering definition)
- [GAP-038 — Full synthetic target capability and canary specification](#gap-038) (engineering definition)
- [GAP-039 — Full source manifest, legal scope and transformation contracts](#gap-039) (engineering definition)
- [GAP-040 — Complete SpeechOcean762 parser and source scale profile](#gap-040) (engineering definition)
- [GAP-041 — Complete L2-ARCTIC v5 read and suitcase parser profile](#gap-041) (engineering definition)
- [GAP-042 — Complete W&I+LOCNESS and FCE v2.1 M2 parser profiles](#gap-042) (engineering definition)
- [GAP-043 — EFCAMDAT full release and derivative ingest scope](#gap-043) (source owner input)
- [GAP-044 — Doubao underlying study-record release contract](#gap-044) (source owner input)
- [GAP-045 — Moodrick and NIR vendor-data scope and contracts](#gap-045) (source owner input)
- [GAP-046 — Leakage grouping, split allocation and duplicate protocol](#gap-046) (product choice)
- [GAP-047 — Gold stimulus, asset and negative-control counting](#gap-047) (linguistic policy)
- [GAP-048 — Agreement and semantic evaluation denominator protocols](#gap-048) (engineering definition)
- [GAP-049 — Elapsed attempt start and validated playback event contracts](#gap-049) (engineering definition)
- [GAP-050 — Complete heldout acceptance protocol and critical cases](#gap-050) (engineering definition)
- [GAP-051 — Retention, deletion and permission revocation lifecycle](#gap-051) (product choice)
- [GAP-052 — Request quotas, concurrency, costs and import resource bounds](#gap-052) (product choice)
- [GAP-053 — Backup/restore consistency and compatibility protocol](#gap-053) (engineering definition)
- [GAP-054 — Complete deployment/configuration and release manifest schema](#gap-054) (engineering definition)
- [GAP-055 — Specification authority, version compatibility and drift closure](#gap-055) (engineering definition)

<a id="gap-001"></a>
## GAP-001 — Complete product and internal API operation contracts

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-001`.

**Already specified:** One local workspace; same-origin internal calls; preserved domain schemas, selected submission statuses and private media. No public API/SDK, login/account endpoints or tenant setup is required.

**What remains missing:** The minimal interface/service operation inventory still lacks exact method/path, payloads, required/nullable fields, limits, headers, revision preconditions, pagination where needed, idempotency scope, success/error outcomes and atomic effects for local preparation, review, publication, answers/results, disputes, import, settings, media and speech.

**Why it matters:** The interface needs an unambiguous contract for every action so the browser, backend and speech service agree on what to save and return. This concerns private implementation calls, not a public API product.

**Needed to close:** Engineering should define each remaining internal operation and remove superseded account/tenant/admin API rows. Specify request/response fields, validation, statuses and state/DB/media effects; ordinary users configure no API.

**Positive closure:** Every in-scope operation has one versioned request/response/security/error contract and links to its flow and owner.

**Negative closure:** An omitted operation, undefined payload/status or unbound route prevents an API-complete claim.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 53, anchor: Use explicit public response objects.
- [openspec/changes/implement-teacher-error-trainer/specs/v6-platform-foundation/spec.md](../../openspec/changes/implement-teacher-error-trainer/specs/v6-platform-foundation/spec.md) — historical audit line 5, anchor: Authorization and audit

<a id="gap-002"></a>
## GAP-002 — Public and private transport projections

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-002`.

**Already specified:** Teacher and blind-review views omit keys at their required stages. All activities belong to the same local operator; there is no adversarial separation between access roles.

**What remains missing:** Complete activity/state field allowlists are absent for Library, exercise start/media, pre-key/post-key Review, attempts/results, disputes, Prepare and local settings. Post-submit transcript/key visibility and historical/quarantined projections remain undefined.

**Why it matters:** Hiding a key on screen is insufficient if it still appears in the response, error, cache or media metadata. The missing decision is what each activity reveals at each stage, especially after submission.

**Needed to close:** Choose whether post-submit teaching results expose the whole transcript/key or only result-linked excerpts; define what a user can see for quarantined/historical exercises. Engineering can then define all field allowlists, including errors, caches and metadata.

**Positive closure:** Each activity/state response contains only its declared fields, while ordinary local navigation remains available without accounts.

**Negative closure:** A pre-submit teacher or pre-key review response cannot expose a hidden field; no unsupported promise of secrecy from the installation owner is made.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 53, anchor: Do not serialize an internal case object
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 34, anchor: "public_context"

<a id="gap-003"></a>
## GAP-003 — Complete persistent entity and constraint model

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-003`.

**Already specified:** One workspace local; immutable versions and transactional audit; active attempt schema 1.1.0 removes tenant_id/user_id and requires workspace_id=local. The complete durable model is not defined by the provisional foundation tables.

**What remains missing:** All domain entities still need columns/types/nullability, primary/foreign/unique keys, indexes, referential actions, revision rules, evidence ownership and local migration compatibility.

**Why it matters:** JSON schemas describe individual records, but not how all records relate durably. Missing constraints can attach a result or approval to the wrong version, duplicate a logical attempt or leave broken media references.

**Needed to close:** Engineering should specify the full local entity dictionary for cases/units/assets/attempts/results, genuine people/qualifications/reviews, rights/manifests/transforms, evaluation stages, disclosures, audit, disputes and result revisions. Exclude user accounts/roles/tenants; define compatibility with preserved earlier data.

**Positive closure:** Every field and reference maps to a declared durable entity/constraint and one immutable version identity.

**Negative closure:** Dangling, wrong-case/version, duplicate or mutable historical references fail declared constraints.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 49, anchor: Use the tables listed in the design
- [openspec/changes/implement-teacher-error-trainer/design.md](../../openspec/changes/implement-teacher-error-trainer/design.md) — historical audit line 15, anchor: foundation exercise catalog

<a id="gap-004"></a>
## GAP-004 — Database and object-store commit protocol

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-004`.

**Already specified:** Domain/audit changes commit together; asset bytes are private and immutable.

**What remains missing:** PostgreSQL and MinIO have no joint transaction specification. Pending uploads, hash verification, object promotion, orphan handling, overwrite/race behavior and crash recovery are unspecified.

**Why it matters:** A database commit and audio upload can fail independently. Without a defined protocol, a published exercise can point to missing or partly written audio, or an orphan object can survive unnoticed.

**Needed to close:** Define the durable asset states and ordered upload/hash/DB-link operations, visibility guards, cleanup permission and recovery for every crash boundary without a background queue.

**Positive closure:** Only a durable hash-verified immutable object can become visible through a committed valid local record.

**Negative closure:** A partial upload, DB rollback, competing overwrite or crash cannot publish a missing or changed object.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 50, anchor: Keep provider responses and evidence in private storage
- [docs/contract-invariants.md](../../docs/contract-invariants.md) — historical audit line 51, anchor: Hashes identify stored immutable byte payloads

<a id="gap-007"></a>
## GAP-007 — Case lifecycle transition and guard table

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-007`.

**Already specified:** Case states, main progression, quarantine, retirement and new-version immutability are defined.

**What remains missing:** No exhaustive transition table binds each state pair to actor, guard, revision, evidence requirements, audit payload and invalid transition result; treatment of in-progress attempts during quarantine is unspecified.

**Why it matters:** Naming draft/rendered/needs_review/verified/published/quarantined/retired states does not define every allowed move. The treatment of a currently running attempt when its exercise is quarantined is a product decision.

**Needed to close:** Choose how quarantine/retirement affects already-open or evaluating attempts and whether/how a quarantined version can return to review. Engineering should complete every state transition with local operation, revision precondition, source/evidence guards, atomic effects, audit and error. No role-permission matrix is required.

**Positive closure:** Every allowed transition specifies all guards/effects and all other transitions are denied.

**Negative closure:** Stale revisions, incomplete gates or forbidden transitions cannot alter a case.

**Source context:**
- [openspec/changes/implement-teacher-error-trainer/design.md](../../openspec/changes/implement-teacher-error-trainer/design.md) — historical audit line 46, anchor: Case lifecycle is draft
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 29, anchor: "quarantined"

<a id="gap-008"></a>
## GAP-008 — Attempt and evaluation recovery transition table

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-008`.

**Already specified:** Original save before providers, explicit user retry, 300-second lease and 270-second deadline are defined.

**What remains missing:** State-specific field invariants, retry eligibility/limits, result lookup during a lease, interrupted evaluation, expired-lease takeover and case/policy changes at retry are not a complete transition contract.

**Why it matters:** A saved answer must survive cancellation, disconnection and retry without two evaluations overwriting each other. The broad deadline/lease rules exist; the exact state-by-state recovery behavior does not.

**Needed to close:** Engineering should define every attempt transition, HTTP outcome, valid retry/reuse rule and lease takeover condition while preserving the original answer/case/policy. Specify the behavior of saved attempts after the case is quarantined/retired, consistently with GAP-007; local retries require no account.

**Positive closure:** A permitted retry preserves the original answer/case/policy and can commit only under its current lease/revision.

**Negative closure:** An active/stale lease, altered answer or forbidden state transition cannot create a final result.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 28, anchor: current revision and token must match
- [contracts/attempt.schema.json](../../contracts/attempt.schema.json) — historical audit line 92, anchor: "evaluation_failed"

<a id="gap-009"></a>
## GAP-009 — Dispute and adjudicated result revision records

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-009`.

**Already specified:** Local dispute/review activities; plausible off-key claims require review; a confirmed key defect creates a new version and explicit result revision. No adjudicator account or access role is required.

**What remains missing:** There is no closed dispute/adjudication/result-revision schema, complete states, evidence visibility rule, reviewer selection or old-to-new unit mapping. Existing attempts affected by a corrected key have no explicit re-evaluation policy.

**Why it matters:** Correcting an exercise key may change an earlier result. The application must distinguish the original result from a reviewed revision and specify which historical attempts may be reconsidered.

**Needed to close:** Choose whether corrections revise only a disputed attempt or also other historical attempts, how revised results are displayed and how users request reconsideration. Engineering should define dispute/adjudication/revision schemas and states, exact old/new unit mapping and recalculation/readback without overwriting history.

**Positive closure:** A valid evidence-backed local resolution appends a traceable new result preserving original answer/result/key references.

**Negative closure:** A reviewer cannot silently overwrite scores, guess unit correspondences or revise unrelated attempts.

**Source context:**
- [docs/verification-v1.md](../../docs/verification-v1.md) — historical audit line 72, anchor: explicit result revision
- [openspec/changes/implement-teacher-error-trainer/specs/v6-content-lifecycle/spec.md](../../openspec/changes/implement-teacher-error-trainer/specs/v6-content-lifecycle/spec.md) — historical audit line 31, anchor: Disputed answers

<a id="gap-010"></a>
## GAP-010 — Independent blind-listening annotation contract

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-010`.

**Already specified:** Two qualified people listen before the planned key and record observations/intervals; review records contain phase and decision.

**What remains missing:** The supplied record mostly references planned unit IDs plus free text. It lacks a structured independently discovered observation set, interval/category/control/uncertainty fields, frozen pre-key submission and key-disclosure event.

**Why it matters:** Reviewing planned errors after seeing the key does not establish independent discovery. The data format must preserve what each person actually heard before disclosure, including uncertainty and controls.

**Needed to close:** Define the blind annotation schema and phase transition: independently observed units/controls, exact audio intervals, taxonomy uncertainty, original note, submit hash/time, then permitted correspondence with planned units and corrections.

**Positive closure:** A reviewer can save discoveries without seeing planned IDs; pre-key annotations remain immutable after disclosure.

**Negative closure:** Key-dependent labels, changed pre-key notes or post-key records cannot masquerade as independent blind evidence.

**Source context:**
- [docs/verification-v1.md](../../docs/verification-v1.md) — historical audit line 56, anchor: Each person records observed errors
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 1129, anchor: "approved_unit_ids"

<a id="gap-011"></a>
## GAP-011 — Reviewer independence and qualification records

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-011`.

**Already specified:** Two genuinely different qualified people are required; acoustic review needs phonetics competence; unresolved disagreement needs a third qualified adjudicator or blocks publication. Names/accounts cannot manufacture independence. Local records do not authenticate external identity.

**What remains missing:** The accepted person/qualification/conflict evidence, verifier responsibility, validity/expiry, author conflicts and adjudicator eligibility/outcome rules remain unspecified. Closed evidence records are also needed.

**Why it matters:** Local names and IDs are not proof that two reviewers are different qualified people. The missing policy defines acceptable evidence and conflict rules without introducing reviewer accounts.

**Needed to close:** Specify acceptable competence/identity/independence evidence and who attests it locally; decide conflicts and third-adjudicator eligibility, and whether two resolved final approvals must be recorded after adjudication. No reviewer accounts are required.

**Positive closure:** Every counted review links genuine distinct-person, qualification/conflict and exact final-artifact evidence.

**Negative closure:** Duplicate-person aliases, unsupported/expired competence or unresolved disagreement cannot satisfy publication.

**Source context:**
- [docs/verification-v1.md](../../docs/verification-v1.md) — historical audit line 58, anchor: evidence of phonetics competence
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 1110, anchor: "qualification_evidence_id"

<a id="gap-012"></a>
## GAP-012 — Teacher-answer gold annotation data contract

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-012`.

**Already specified:** Real answers and independent labels before model results are required for correct/partial/vague/repeated/contradictory/false/off-key classes.

**What remains missing:** No closed teacher-answer annotation schema defines source spans, fragmentation, stance/category/repair/rationale judgments, expected mappings, uncertainty, rater identity, adjudication or frozen pre-model label sets.

**Why it matters:** LLM quality cannot be evaluated against its own answers. Real teacher text needs independently recorded expected interpretations, including partial, contradictory, retracted and off-key claims.

**Needed to close:** Define that gold record and annotation handbook, all required answer classes, how unknown/missing judgments are retained, and how labels bind the exact answer/case/policy/split.

**Positive closure:** Real answer gold preserves raw text and separate pre-adjudication labels with an auditable final mapping.

**Negative closure:** Model-seen labels, fabricated answers or missing substantive clauses cannot qualify as independent gold.

**Source context:**
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 149, anchor: Human annotators define expected claims
- [contracts/corpus-record.schema.json](../../contracts/corpus-record.schema.json) — historical audit line 186, anchor: "raw_annotations_asset_id"

<a id="gap-013"></a>
## GAP-013 — Detection-event boundaries and overlapping category resolution

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-013`.

**Already specified:** All 122 leaves define inclusion/exclusion; use the narrowest supported category, separate independent repairs and retain secondary labels.

**What remains missing:** No complete event-boundary/overlap handbook resolves equally narrow categories, shared repair spans, repeated occurrences, multi-utterance events or ambiguity across reporting domains.

**Why it matters:** One observable problem can fit several categories, and several independent errors can share a span. Without unitization rules, the same audio can produce different opportunity counts and different scores.

**Needed to close:** Specify the reviewed unitization procedure and ambiguity outcome for overlapping taxonomy cases; define identity of one event, independent repairs and primary versus secondary labels for each relevant contrast.

**Positive closure:** The same evidence supports one reproducible primary event count with explicit secondary labels or review.

**Negative closure:** Overlapping labels, ambiguous primary domains or repeated labels cannot inflate opportunities.

**Source context:**
- [docs/contract-invariants.md](../../docs/contract-invariants.md) — historical audit line 28, anchor: Secondary labels must not create extra detection units
- [domain/error-taxonomy.v1.yaml](../../domain/error-taxonomy.v1.yaml) — historical audit line 46, anchor: annotation_priority:

<a id="gap-014"></a>
## GAP-014 — Frozen English/Russian aliases and taxonomy ancestors

**Who closes it:** Linguistic policy — reviewed definitions/registry needed. Active requirement: `SPEC-014`.

**Already specified:** Explicit categories earn separate credit; unknown synonyms must not be guessed.

**What remains missing:** The approved bilingual alias map is absent. Accepted parent/family nodes, canonical spellings, ambiguous aliases, normalization and version migration are not enumerated.

**Why it matters:** The 122 category IDs are present, but teacher wording can use English/Russian names, synonyms or broader families. Credit needs a fixed reviewed mapping rather than model guesses.

**Needed to close:** Supply exact English/Russian alias entries with target ID(s), parent-versus-leaf status, ambiguity behavior and normalization/version rules. Retain unresolved unknown wording.

**Positive closure:** Only an approved unambiguous explicit alias receives the declared category/hierarchy credit.

**Negative closure:** Unknown, ambiguous, invented or other-version aliases cannot earn guessed category credit.

**Related decisions:** DEC-003.

**Source context:**
- [docs/scoring-v1.md](../../docs/scoring-v1.md) — historical audit line 68, anchor: alias
- [audit/open-decisions.json](../../audit/open-decisions.json) — historical audit line 34, anchor: Category alias map

<a id="gap-015"></a>
## GAP-015 — Severity assignment and fixed weight binding

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-015`.

**Already specified:** Four severity labels, weights 1–4 and FP weight one exist; weights are frozen before the answer.

**What remains missing:** No severity rubric binds labels to weight values or explains whether labels and weights may vary independently; communication/context evidence and author/reviewer authority are unspecified.

**Why it matters:** Weighted recall/F1 depends on the weight attached to each error. The allowed weights exist, but the policy that assigns them consistently before an answer is missing.

**Needed to close:** Define the severity rubric and exact severity-to-weight mapping, or explicitly authorize independent reviewed weights with required evidence. Do not change inherited composite weights.

**Positive closure:** Each case weight has an approved reproducible severity policy and pre-attempt record.

**Negative closure:** Post-answer weight changes or inconsistent unsupported severity assignments fail.

**Related decisions:** DEC-008.

**Source context:**
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 717, anchor: "severity"
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 727, anchor: "weight"

<a id="gap-016"></a>
## GAP-016 — Rated difficulty evidence protocol

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-016`.

**Already specified:** Generated candidates are unrated; reviewed records allow easy/medium/hard/expert with evidence.

**What remains missing:** No rating method, population, sample sufficiency or difficulty-to-evidence rule exists for the non-unrated enum values.

**Why it matters:** A displayed difficulty label would imply evidence about a defined population. The current enum alone does not justify easy, hard or expert labels; leaving every exercise unrated is an explicit available choice.

**Needed to close:** Either freeze v1 difficulty to unrated everywhere until a separately specified study, or define the complete rating method and evidence requirements for every enabled rating.

**Positive closure:** A rated value is displayed only under its declared measurement protocol; otherwise it remains unrated.

**Negative closure:** Author intuition or unrelated corpus CEFR cannot become a measured difficulty rating.

**Source context:**
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 744, anchor: "difficulty_evidence_ref"
- [contracts/case-candidate.schema.json](../../contracts/case-candidate.schema.json) — historical audit line 416, anchor: "unrated"

<a id="gap-017"></a>
## GAP-017 — Variety, register and judgment consistency table

**Who closes it:** Linguistic policy — reviewed definitions/registry needed. Active requirement: `SPEC-017`.

**Already specified:** Public variety/context constraints and separation of error, permitted variant and naturalness are mandatory.

**What remains missing:** Accepted-variety/register strings have no registry or full expected_judgment/status_label/basis/eligibility compatibility table. Authoring conflict validation and public-context sufficiency lack a complete review rubric.

**Why it matters:** A pronunciation or grammar form may be acceptable in one variety or register and unsuitable in another. Scoring must rely on visible agreed context, not a hidden preference for one accent or style.

**Needed to close:** Define allowed variety/register/basis values or an explicit reviewed free-text contract, permitted label combinations and required public facts for each context-dependent leaf.

**Positive closure:** Every scored context-dependent event uses a reviewed public constraint and compatible status/eligibility.

**Negative closure:** A hidden dialect constraint, incompatible status or accent preference cannot count as a true error.

**Source context:**
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 64, anchor: "assessment_basis"
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 351, anchor: "status_label"

<a id="gap-018"></a>
## GAP-018 — Claim identity, extraction partition and completeness

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-018`.

**Already specified:** Exact codepoint spans, server-assigned claim IDs and preservation of unparsed substantive text are required.

**What remains missing:** Stable-ID construction, clause ordering, allowed span overlaps/nesting, attachment containment and checking that all substantive assertions were extracted or marked unparsed are not fully specified.

**Why it matters:** Claims must quote the exact saved answer and have reproducible identities. Otherwise repeated runs, attached corrections and audit comparison can refer to different assertions or overlook substantive text.

**Needed to close:** Define the deterministic ID/order algorithm and extraction coverage rules, including repeated/overlapping spans, category-only comments, cross-clause correction attachments and unsupported omissions.

**Positive closure:** The frozen answer deterministically produces stable checked claims and explicit unresolved substantive coverage.

**Negative closure:** Fabricated/overlapping-invalid spans or silently omitted substantive assertions cannot score as complete.

**Source context:**
- [docs/contract-invariants.md](../../docs/contract-invariants.md) — historical audit line 19, anchor: unique stable ID after server assignment
- [contracts/claim-extraction.schema.json](../../contracts/claim-extraction.schema.json) — historical audit line 233, anchor: "unparsed_spans"

<a id="gap-019"></a>
## GAP-019 — Fragment consolidation, duplicate and retraction normalization

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-019`.

**Already specified:** Exact duplicates count once; compatible fragments may combine; explicit retraction uses the final endorsed statement; contradictions require review.

**What remains missing:** The transformation from several clauses to one unit decision is absent. The reference scorer rejects multiple nonduplicate assignments; exact grouping, attachment, retraction chains and provenance are not defined.

**Why it matters:** A teacher may split one argument across sentences, repeat it or explicitly withdraw it. A scorer needs a defined normalization step that preserves all clauses and does not select only the favorable fragment.

**Needed to close:** Specify the normalization record/algorithm for compatible fragments, exact duplicates and scoped retractions, including ordering and transitive references; preserve each original clause and avoid best-of selection.

**Positive closure:** Compatible fragments form one traceable scorer decision and valid duplicates/retractions retain all source evidence.

**Negative closure:** Cycles, conflicting repairs or arbitrary last-write/best-of grouping cannot produce final credit.

**Source context:**
- [docs/scoring-v1.md](../../docs/scoring-v1.md) — historical audit line 99, anchor: Compatible fragments can form one response
- [spec-inputs/v6-ste/reference/scorer.py](../../spec-inputs/v6-ste/reference/scorer.py) — historical audit line 94, anchor: unresolved duplicate or contradictory unit decisions

<a id="gap-020"></a>
## GAP-020 — Evaluator and cross-schema conditional truth tables

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-020`.

**Already specified:** Closed structural schemas and several membership/stance/evidence invariants are supplied.

**What remains missing:** A full permitted tuple table is absent for decision/unit/stance/reason/duplicate and supplied/option/propositions/status/unresolved_reason, and for candidate failure/realization/verification/review states.

**Why it matters:** Valid JSON can still contain an impossible combination of fields. The application needs explicit semantic rules for every conditional combination, including nulls, empty lists and review versus rejection.

**Needed to close:** Specify every conditional required/null/empty/value relation and eligibility rule, with explicit reject versus review outcomes; include all 15 schemas and enum branches.

**Positive closure:** Every accepted cross-field tuple has a declared semantic invariant and derivation.

**Negative closure:** A structurally valid but contradictory tuple is rejected before publication/scoring.

**Source context:**
- [contracts/evaluator-output.schema.json](../../contracts/evaluator-output.schema.json) — historical audit line 252, anchor: "reason_code"
- [docs/contract-invariants.md](../../docs/contract-invariants.md) — historical audit line 63, anchor: correction verdict must agree

<a id="gap-021"></a>
## GAP-021 — Approved rationale registry and explanation-null binding

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-021`.

**Already specified:** Key units have rationale propositions/text. The reference validator explicitly requires explanation.option_id=null; no explanation-option registry is needed under that rule.

**What remains missing:** Feedback approved_rationale_ids still lacks an explicit identity/entity contract linking the unit rationale to approved text, language and evidence. The explanation-null requirement needs an active cross-field binding rather than inference from schema shape alone.

**Why it matters:** The explanation option field is already defined as null; an explanation-option catalog is not missing. What remains is a stable record for the approved rationale that feedback cites and consistent enforcement of that null rule.

**Needed to close:** Define the approved-rationale identities (ID, unit/version, language, approved text, evidence) and bind explanation.option_id=null explicitly across active schema invariants/prompts; do not invent explanation options.

**Positive closure:** Each explanation/feedback reference resolves to the exact approved unit/version/language record.

**Negative closure:** A nonexistent, correction-only, wrong-language or other-version rationale ID is rejected.

**Source context:**
- [spec-inputs/v6-ste/reference/validators.py](../../spec-inputs/v6-ste/reference/validators.py) — historical audit line 39, anchor: rationale is not a correction option
- [contracts/feedback.schema.json](../../contracts/feedback.schema.json) — historical audit line 29, anchor: "approved_rationale_ids"
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 907, anchor: "rationale_required_propositions"

<a id="gap-022"></a>
## GAP-022 — Semantic decisions to deterministic rubric and scorer input

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-022`.

**Already specified:** q is satisfied required propositions / required propositions; forbidden assertions force zero, approved alternatives earn one, missing supplied work earns zero and novel alternatives require review.

**What remains missing:** No complete binding algorithm selects a reviewed option, validates normalized alternative matches, maps proposition findings/status to exact fractions and converts excluded units/ignore/retractions into scorer records.

**Why it matters:** The LLM provides bounded semantic findings; code must turn them into the exact rubric and counters. The missing specification is the conversion algorithm, not permission for the model to invent fractions or grades.

**Needed to close:** Define this transformation field-by-field, including multiple alternatives, extra false clauses, ineligible corrections, null options, acceptable controls and exclusions. violated_proposition_ids already means forbidden propositions in data-dictionary.md.

**Positive closure:** Code derives exact fractions and sufficient statistics solely from validated source claims and fixed reviewed options.

**Negative closure:** Model fractions, teacher-unsupplied content or cherry-picked contradictory options cannot enter the scorer.

**Source context:**
- [docs/scoring-v1.md](../../docs/scoring-v1.md) — historical audit line 78, anchor: required propositions
- [contracts/scoring-input.schema.json](../../contracts/scoring-input.schema.json) — historical audit line 145, anchor: "correction_credit"

<a id="gap-023"></a>
## GAP-023 — Mapper/auditor comparison equality contract

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-023`.

**Already specified:** Audit is a separate blind-to-first-output consistency request; relevant disagreement requires review, never favorable retries.

**What remains missing:** The canonical compared projection, set/order treatment, handling of duplicates/evidence/option/status/reasons and definition of score-relevant versus harmless differences are unspecified.

**Why it matters:** A separate audit request can legitimately reorder equivalent records or reveal a substantive disagreement. The application needs an exact comparison rule that distinguishes the two without hiding scoring differences.

**Needed to close:** Define comparison fields and normalization, with a difference-to-review table and records for both outputs. State how extraction-level stance differences can be compared when mapper outputs do not carry stance.

**Positive closure:** Two semantically equivalent records compare consistently without hiding any score-relevant difference.

**Negative closure:** Different target, option, stance or proposition credit cannot be ignored as harmless formatting.

**Source context:**
- [docs/providers-v1.md](../../docs/providers-v1.md) — historical audit line 29, anchor: Compare claim IDs, stance, target, and proposition sets
- [prompts/audit-map-v1.txt](../../prompts/audit-map-v1.txt) — historical audit line 4, anchor: schema

<a id="gap-024"></a>
## GAP-024 — Exact score transport, composite rational and numeric bounds

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-024`.

**Already specified:** Core ratios retain exact numerator/denominator, sufficient statistics and one-decimal half-up displays; the composite formula is explicit.

**What remains missing:** The composite has only a floating value and no exact fraction. Integer caps, safe cross-language representation, decimal serialization and complete display rounding for composite/auxiliary values are unspecified.

**Why it matters:** Exact arithmetic is not preserved automatically when values pass between Python, Go, JSON and the browser. The composite and integer/decimal transport rules must prevent overflow and reuse of rounded values.

**Needed to close:** Define exact composite storage/transport, all numeric ranges and overflow policy, serialization and display rules. Decide bounded JSON integers versus decimal-string arbitrary integers without silently weakening existing schemas.

**Positive closure:** Every score can be reproduced exactly across services from saved statistics and policy.

**Negative closure:** Overflow, binary-float drift or a rounded display reused as an exact value is rejected.

**Source context:**
- [docs/scoring-v1.md](../../docs/scoring-v1.md) — historical audit line 111, anchor: exact reduced rational
- [contracts/score-result.schema.json](../../contracts/score-result.schema.json) — historical audit line 4681, anchor: "value_0_100"

<a id="gap-025"></a>
## GAP-025 — Auxiliary and provisional result response contracts

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-025`.

**Already specified:** All 27 core and 15 auxiliary formulas are retained; unresolved decisions withhold final aggregates and unobserved teacher traits are null.

**What remains missing:** The score-result schema enumerates core ratios only. No complete output shape binds auxiliary values/methods/units/missing reasons or provisional item evidence and review issue lists.

**Why it matters:** Preserving 42 formula names does not give all 42 a defined response representation. The interface needs explicit observed, unavailable, inapplicable and provisional fields rather than silently omitting measurements.

**Needed to close:** Define the separate auxiliary/provisional result schema, each N/A/review/insufficient/not-observable reason, and exactly which evidence can be displayed pending adjudication.

**Positive closure:** All 42 named measurements have an explicit output location/status/method, without final aggregates for unresolved decisions.

**Negative closure:** Missing measurements cannot disappear, become zero/perfect, or be displayed as final confirmed misses.

**Source context:**
- [domain/metrics.v1.yaml](../../domain/metrics.v1.yaml) — historical audit line 235, anchor: auxiliary_metrics:
- [contracts/score-result.schema.json](../../contracts/score-result.schema.json) — historical audit line 103, anchor: "metrics"

<a id="gap-026"></a>
## GAP-026 — Grounded bilingual feedback and missed-unit references

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-026`.

**Already specified:** Feedback may explain validated findings/misses in English or Russian, cite reviewed material and introduce no new errors or grades.

**What remains missing:** Missed units have no extracted teacher decision ID; the supplied feedback shape requires one. Approved bilingual rationale text/IDs and a deterministic check of free-text factual grounding are absent.

**Why it matters:** A missed error has no corresponding extracted teacher claim. Feedback must have a valid way to reference that gold unit and must use supported English/Russian rationale rather than fabricated claim IDs or facts.

**Needed to close:** Define feedback item types for detected/missed/false-positive/pending findings, their exact references and approved bilingual fallback text; define unsupported paraphrase handling and requested versus detected language.

**Positive closure:** Every feedback statement traces to a validated result or approved rationale in the selected language.

**Negative closure:** Invented decision IDs, new repairs/grades or untranslated unsupported fallback content fail.

**Source context:**
- [contracts/feedback.schema.json](../../contracts/feedback.schema.json) — historical audit line 24, anchor: "decision_id"
- [prompts/feedback-v1.txt](../../prompts/feedback-v1.txt) — historical audit line 9, anchor: rationale

<a id="gap-027"></a>
## GAP-027 — Feedback-only failure versus evaluation-failure outcome

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-027`.

**Already specified:** Metric computation and feedback are distinct; approved stored rationale is allowed if feedback fails.

**What remains missing:** The blanket provider-failure status conflicts with an undefined completed-score-plus-fallback response. Persisted attempt/result state and HTTP status for feedback-only refusal/truncation/schema/timeout are not frozen.

**Why it matters:** The semantic score may already be valid when the final feedback request fails. The specification must decide whether that attempt stays complete with approved fallback text or becomes a failure, and what an explicit retry repeats.

**Needed to close:** Specify the feedback-only failure exception and response/state table, including whether a valid score remains complete, how fallback provenance is represented and which explicit retry repeats only feedback.

**Positive closure:** Feedback failure preserves valid numeric evidence and shows an explicitly labelled approved fallback under the declared response status.

**Negative closure:** A failed semantic stage cannot use this fallback exception to fabricate a completed score.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 40, anchor: provider refusal or invalid structure produces HTTP 502
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 44, anchor: If feedback generation fails

<a id="gap-028"></a>
## GAP-028 — Linguistic audit role prompt, schema and decisions

**Who closes it:** Linguistic policy — reviewed definitions/registry needed. Active requirement: `SPEC-028`.

**Already specified:** The role is advisory and configurable; a separate draft proposal exists, not an approved active contract.

**What remains missing:** The active manifest has no exact linguistic-audit input/output/prompt version with target/span findings, refusal rules, allowed evidence and integration into candidate review.

**Why it matters:** This advisory stage must inspect a candidate under its own exact prompt/input/output contract. The existing five prompts do not supply this additional contract, and a draft proposal is not an active approved definition.

**Needed to close:** Resolve DEC-001 using the exact proposed or replacement input, prompt, closed schema and finding-to-candidate rules; record the scoped decision without treating a model as a human reviewer.

**Positive closure:** The selected active linguistic-audit contract is complete and version-bound before the role is enabled.

**Negative closure:** Reused unrelated schemas or invented human approvals cannot activate the role.

**Related decisions:** DEC-001.

**Source context:**
- [audit/open-decisions.json](../../audit/open-decisions.json) — historical audit line 5, anchor: linguistic_audit output contract
- [domain/providers.v1.yaml](../../domain/providers.v1.yaml) — historical audit line 13, anchor: linguistic_audit

<a id="gap-029"></a>
## GAP-029 — Complete role input and configuration binding schemas

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-029`.

**Already specified:** Versioned configurable providers, supplied default DeepSeek development profile and processing-stage bindings; documented disclosure/hash rules. Processing-stage roles do not represent human access roles.

**What remains missing:** There is no closed schema for each stage input DTO, effective role binding, configuration registry, provider receipt or stage-cache record. Required input fields and maximum sizes are mostly prose.

**Why it matters:** The selected provider profile is described, but the program needs closed input/configuration/receipt/cache records. These roles are processing stages, not human permissions, and ordinary setup uses supplied defaults.

**Needed to close:** Engineering should specify closed stage input, effective binding/configuration, receipt and cache records: allowed fields/sizes, settings/defaults, hash/version derivation and exact case/answer/stage/profile scope. Normal startup uses supplied defaults and provider keys. Exclude tenant/account authorization fields.

**Positive closure:** Each role receives only its complete permitted input under a frozen validated binding.

**Negative closure:** Blind extraction cannot receive the key; raw identity/consent records, unknown settings or wrong-case/version cached outputs cannot enter a stage.

**Source context:**
- [docs/llm-configuration.md](../../docs/llm-configuration.md) — historical audit line 7, anchor: versioned role binding
- [prompts/manifest.yaml](../../prompts/manifest.yaml) — historical audit line 1, anchor: version:

<a id="gap-030"></a>
## GAP-030 — Provider-specific strict-schema projection and response parsing

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-030`.

**Already specified:** Trusted prompt/input separation, documented DeepSeek Responses/low-reasoning binding and completed-visible-output rules are described in docs/llm-configuration.md. Every full application constraint must remain enforced; documented fields do not prove live conformance.

**What remains missing:** A complete per-provider/per-schema keyword disposition and wire payload/response/error mapping is absent. Exact output block assembly, refusal/incomplete handling and interaction with local semantic validation need a complete specification.

**Why it matters:** A provider response can be syntactically valid while incomplete, refused or incompatible with the full schema. Adapter definitions must preserve constraints and select visible completed output separately from reasoning.

**Needed to close:** Define the OpenAI and DeepSeek transport adapters as specifications: instruction/input separation, reasoning effort, format payload, output-text selection, incomplete/refusal handling and every schema keyword disposition. Research notes resolve documented fields, not live support.

**Positive closure:** The adapter preserves every application constraint and accepts only a completed structurally and semantically valid stage payload.

**Negative closure:** Developer-as-user instructions, reasoning text, dropped constraints or JSON repair cannot become accepted stage output.

**Source context:**
- [docs/contract-invariants.md](../../docs/contract-invariants.md) — historical audit line 82, anchor: supported strict-schema subset
- [domain/providers.configurable.v1.yaml](../../domain/providers.configurable.v1.yaml) — historical audit line 21, anchor: response_contract:

<a id="gap-031"></a>
## GAP-031 — Retry, deadline and input/output capacity protocol

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-031`.

**Already specified:** Stage/global deadlines, no semantic retries, explicit recovery and candidate generation/render attempt caps are present.

**What remains missing:** Retry count scope (request versus stage), retryable status/error list, backoff within reserve, generation-attempt versus transport-attempt accounting, disconnect cancellation and prompt/token overflow are not complete contracts.

**Why it matters:** One retry rule cannot be interpreted separately by each layer. Deadlines, retry counters and token limits must have a single meaning so provider failures cannot cause loops, truncated evidence or late writes.

**Needed to close:** Define retryable failures and counter scope, actual deadline propagation, generation budgets, input/output token estimation and deterministic oversize behavior without truncating claims or key content.

**Positive closure:** Every retry is counted and fits the remaining budget; oversized work returns the declared safe outcome with saved source input.

**Negative closure:** 429/5xx loops, reasoning-token exhaustion, silent truncation or late commits cannot bypass limits.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 32, anchor: Allow at most one transport retry
- [domain/providers.configurable.v1.yaml](../../domain/providers.configurable.v1.yaml) — historical audit line 18, anchor: max_output_tokens:

<a id="gap-032"></a>
## GAP-032 — Typed render operator and hard-capability catalog

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-032`.

**Already specified:** Four typed render operations and five capability names exist; arbitrary XML and remote audio are forbidden.

**What remains missing:** Per-operator required/null fields, rate/pitch/pause ranges, locale/voice/capability compatibility and hard-constraint precedence/conflict rules are not closed. DEC-004 still uses unrestricted strings.

**Why it matters:** Typed operations text/phoneme/pause/prosody are present, but types alone do not define valid parameter combinations or guaranteed capabilities. Unsupported accent/stress/pace constraints must fail explicitly.

**Needed to close:** Define the capability catalog and each operator payload/range, legal combinations and conflict results. State exactly which parameters constitute pace, accent, stress and prosody constraints.

**Positive closure:** A complete typed plan is validated against a fixed profile/capability catalog before synthesis.

**Negative closure:** Unknown hard constraints, irrelevant payload fields and incompatible voice/locale/target combinations fail.

**Related decisions:** DEC-004.

**Source context:**
- [contracts/render-plan.schema.json](../../contracts/render-plan.schema.json) — historical audit line 91, anchor: "rate_percent"
- [contracts/blueprint.schema.json](../../contracts/blueprint.schema.json) — historical audit line 193, anchor: "hard_render_constraints"

<a id="gap-033"></a>
## GAP-033 — SSML compilation and final-audio assembly specification

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-033`.

**Already specified:** Azure REST, escaped typed SSML and a 24-kHz mono PCM16 master are prescribed; final bytes require review.

**What remains missing:** The compiler grammar, per-turn call ordering, punctuation/prosody scope, concatenation/gaps, resampling, delivery codec, timestamp frame rounding and transformation manifest are not fully defined.

**Why it matters:** Review applies to the actual delivered audio bytes. The compilation and conversion steps must preserve turn order, intentional errors and exact time intervals so a different encoded asset cannot inherit approval.

**Needed to close:** Specify the exact SSML lowering and audio pipeline, including ordered turn-to-utterance mapping, sample/clock conversion, trimming/mixing/normalization policy and immutable final hash boundaries.

**Positive closure:** The final delivered asset and every turn/unit interval are reproducibly linked to exact plan and transformations.

**Negative closure:** A reordered turn, changed encoded file, unsupported phoneme or altered intentional target cannot inherit prior review.

**Source context:**
- [docs/providers-v1.md](../../docs/providers-v1.md) — historical audit line 42, anchor: Compile SSML from the typed render operations
- [docs/providers-v1.md](../../docs/providers-v1.md) — historical audit line 48, anchor: Keep the turn offsets

<a id="gap-034"></a>
## GAP-034 — Audio quality measurement method and boundary rules

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-034`.

**Already specified:** Peak .9999, -18±2 LUFS, ≤-1 dBTP, silence thresholds and finite/mono/duration checks are specified.

**What remains missing:** Loudness/true-peak algorithm/version, decoding/sample normalization, RMS hop/window-edge treatment, near-silence grouping and planned-pause overlap classification are absent.

**Why it matters:** A threshold without a measurement method is ambiguous. Different loudness, true-peak or silence algorithms can disagree on the same waveform, particularly at window boundaries and planned pauses.

**Needed to close:** Define method versions and formulas/options for loudness/true peak/RMS, exact inclusive thresholds and interval rounding, all-silent/too-short/NaN treatment and how planned versus unplanned silence is decided.

**Positive closure:** Every QC value has its final-byte subject, method, unit and reproducible boundary classification.

**Negative closure:** A method-less value, padding-dependent silence or upstream-file measurement cannot approve final delivery.

**Source context:**
- [docs/verification-v1.md](../../docs/verification-v1.md) — historical audit line 26, anchor: Integrated loudness
- [docs/verification-v1.md](../../docs/verification-v1.md) — historical audit line 31, anchor: 20-millisecond RMS windows

<a id="gap-035"></a>
## GAP-035 — Speech tokenizer, reviewed intervals and disfluency event rules

**Who closes it:** Linguistic policy — reviewed definitions/registry needed. Active requirement: `SPEC-035`.

**Already specified:** Elapsed speech includes internal pauses; articulation uses reviewed speech intervals; disfluency counts only reviewed events.

**What remains missing:** Exact contraction/number/filler/repetition tokenization, interval union rules, active speech/pauses and countable disfluency event identities are absent.

**Why it matters:** Speech rate, articulation rate and disfluency density depend on exactly what counts as a token, speech interval and event. Different treatment of contractions, fillers or repetitions would change the metrics.

**Needed to close:** Resolve DEC-005 with the full tokenizer and interval/event protocol, including punctuation, partial words, overlaps, zero-duration and intended pause treatment.

**Positive closure:** Every rate/density numerator and denominator can be recomputed from a fixed reviewed annotation/method.

**Negative closure:** Different tokenizers, overlapping intervals or ordinary permitted fillers cannot produce comparable error metrics.

**Related decisions:** DEC-005.

**Source context:**
- [domain/metrics.v1.yaml](../../domain/metrics.v1.yaml) — historical audit line 253, anchor: spoken_token_count
- [audit/open-decisions.json](../../audit/open-decisions.json) — historical audit line 62, anchor: Speech tokenization and pause measurement

<a id="gap-036"></a>
## GAP-036 — Prosody feature/unit/method and valid missingness table

**Who closes it:** Linguistic policy — reviewed definitions/registry needed. Active requirement: `SPEC-036`.

**Already specified:** Eleven named prosody features distinguish requested bounds, observation and evidence; unsupported numeric methods remain unavailable.

**What remains missing:** There is no complete feature-to-unit/method table, F0 reference/log conversion, slope/range extraction, voiced-frame selection, syllable/phrase boundaries or label vocabularies.

**Why it matters:** Requested prosody is not observed prosody. Each enabled feature needs a valid unit, extraction/annotation method and missingness rule before its numeric value can support a judgment.

**Needed to close:** Resolve DEC-006 for every enabled feature: method/version, valid units, bounds, interval/voicing policy, evidence type and human-only/unknown outcome.

**Positive closure:** Every observed feature has a valid method/unit/subject combination and separates intended from measured values.

**Negative closure:** Invalid feature units, unvoiced F0 or provider naturalness scores cannot masquerade as measured target evidence.

**Related decisions:** DEC-006.

**Source context:**
- [contracts/ground-truth.schema.json](../../contracts/ground-truth.schema.json) — historical audit line 563, anchor: "f0_range_semitones"
- [audit/open-decisions.json](../../audit/open-decisions.json) — historical audit line 76, anchor: Prosody feature methods and units

<a id="gap-037"></a>
## GAP-037 — ASR and pronunciation advisory normalization

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-037`.

**Already specified:** Whisper raw hypothesis precedes alignment; Azure advisory chunks use 16-kHz mono PCM, max25s; prosody en-US only.

**What remains missing:** Chunk boundaries/reference slices, overlap/stitching, tick/second-to-ms conversion, missing/NoMatch handling and typed provider-field normalization are incomplete.

**Why it matters:** ASR and pronunciation-assessment outputs are advisory. Their timestamps, chunks and scale/status conversions must map to the final audio and must not be interpreted as observed phonemes or automatic gold.

**Needed to close:** Define each raw response field retained, status/range/unit mapping and chunk-to-final-audio interval conversion; distinguish transport streaming from prohibited live product interaction.

**Positive closure:** Each advisory observation retains its raw response and exact final-audio/chunk/version mapping.

**Negative closure:** Missing fields, reference-conditioned scores or wrong offset units cannot create observed IPA or automatic gold.

**Source context:**
- [docs/providers-v1.md](../../docs/providers-v1.md) — historical audit line 65, anchor: chunks of no more than 25 seconds
- [domain/providers.v1.yaml](../../domain/providers.v1.yaml) — historical audit line 89, anchor: pronunciation_assessment_header:

<a id="gap-038"></a>
## GAP-038 — Full synthetic target capability and canary specification

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-038`.

**Already specified:** Every taxonomy target remains in scope; three render attempts then blocking; no active human-recording/provider fallback.

**What remains missing:** Per-leaf/voice/locale target requests, observable realization criteria and canary change-detection protocol are incomplete. Taxonomy recording-route alternatives are not active profiles.

**Why it matters:** Synthesis controls do not prove the intended error was realized. Every target needs a defined observable qualification criterion and drift check, even when real synthesis later fails that criterion.

**Needed to close:** Define target capability records for all 122 leaves/controls and acoustic feature combinations, exact observable success/failure and required review. Real DEC-007 calls are evidence work, not missing definitions.

**Positive closure:** Each target has a complete requested-versus-observed qualification contract, even if evidence later fails.

**Negative closure:** An unproven/failed target cannot be dropped, replaced or marked observed from SSML settings.

**Related decisions:** DEC-007.

**Source context:**
- [domain/error-taxonomy.v1.yaml](../../domain/error-taxonomy.v1.yaml) — historical audit line 35, anchor: render_route:
- [audit/open-decisions.json](../../audit/open-decisions.json) — historical audit line 90, anchor: Requested accent and full acoustic generation

<a id="gap-039"></a>
## GAP-039 — Full source manifest, legal scope and transformation contracts

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-039`.

**Already specified:** Eight profiles, immutable raw records, private quarantine, full-release obligations and per-use rights are required.

**What remains missing:** No closed release manifest/permissions/import report/transformation schema defines required components/count units, parser identities, checksums, rejection reconciliation and normalized grouping/label relations.

**Why it matters:** A source name or expected webpage count cannot establish full ingestion. Complete manifests must reconcile each supplied file, partition, label, accepted/rejected record and transformation with permitted uses.

**Needed to close:** Define those records for each profile, including release/source format, all files/partitions, observed counts and rights uses/expiry. Unknown acquisition hashes remain null pending evidence, not invented constants.

**Positive closure:** All acquired components/counts and rejected rows reconcile to an exact manifest with each transformation and allowed use.

**Negative closure:** Samples, omitted components, mixed releases or unapproved transfer cannot satisfy a full-source claim.

**Source context:**
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 52, anchor: manifest.json
- [contracts/corpus-record.schema.json](../../contracts/corpus-record.schema.json) — historical audit line 215, anchor: "transform_ids"

<a id="gap-040"></a>
## GAP-040 — Complete SpeechOcean762 parser and source scale profile

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-040`.

**Already specified:** Full selected train/test components, speaker grouping/age/gender metadata, aggregate/detail scores and all five raters are already required in the current full-source inventory. Low scores do not identify substituted phones.

**What remains missing:** The exact selected-release parser/output schemas, field/scale/marker semantics, aggregate-versus-rater reconciliation, uncertainty handling and approved ARPAbet/IPA conversion rules remain incomplete. Metadata presence is no longer an omitted planning requirement.

**Why it matters:** The inventory already includes speaker/age/gender metadata. What remains is a faithful parser/scale/conversion contract for every component and all raters, rather than a reduced subset or inferred phone labels.

**Needed to close:** Supply the exact selected release format and conversion tables; retain all metadata and scores-detail versus aggregate fields independently, define unknown/inserted phone markers and quarantine mixed scales.

**Positive closure:** All selected-release fields and raters are retained with declared source scales and original marker uncertainty.

**Negative closure:** Dropped child/speaker metadata, inferred phones, mixed scales or guessed IPA mapping fails full faithful import.

**Source context:**
- [domain/corpus-sources.v1.yaml](../../domain/corpus-sources.v1.yaml) — historical audit line 24, anchor: train/test/{text,utt2spk,wav.scp}
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 72, anchor: mixed or unknown completeness scale

<a id="gap-041"></a>
## GAP-041 — Complete L2-ARCTIC v5 read and suitcase parser profile

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-041`.

**Already specified:** Full24-speaker read release and22-speaker suitcase extension remain required in the inventory; automatic/manual tiers stay distinct.

**What remains missing:** No complete v5 directory/tier/marker grammar, CPL/PPL/s/a/d/err/* conversion profile, 44.1-kHz clock mapping or approved phone/taxonomy mapping is supplied.

**Why it matters:** The full v5 scope includes read speech and the suitcase extension. Automatic alignments, manual labels and uncertain markers must remain distinguishable when mapped into the project.

**Needed to close:** Specify the full v5 parser for README/LICENSE/PROMPTS and wav/transcript/textgrid/annotation plus suitcase; preserve all source labels before approved conversion and define unknown-tier quarantine.

**Positive closure:** Every component and manual/automatic label is retained with exact source-clock and annotation provenance.

**Negative closure:** Automatic alignments, err/* uncertainty or unsupported phone conversions cannot become manual narrow-category gold.

**Source context:**
- [domain/corpus-sources.v1.yaml](../../domain/corpus-sources.v1.yaml) — historical audit line 39, anchor: original TextGrid tiers
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 91, anchor: Unknown tiers or phone markers

<a id="gap-042"></a>
## GAP-042 — Complete W&I+LOCNESS and FCE v2.1 M2 parser profiles

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-042`.

**Already specified:** Half-open source token spans, one-annotator edits, alternatives/noop and CEFR granularity are required; separate releases/licences retained.

**What remains missing:** Approved ERRANT-to-project leaf mappings are absent; per-release partition metadata/group IDs, detection-only labels, historical fields, edit-order ties and full parser output schema are incomplete.

**Why it matters:** Written edit corpora have annotator-specific alternatives, insertions and token offsets. Mapping them into the listening taxonomy requires declared conversion rules and preservation of all original annotation identities.

**Needed to close:** Define both exact v2.1 profiles and mappings including noop, UNK/Um, insertions/overlaps/multiple alternatives and source token-to-codepoint correspondence. Specify handling of unavailable test labels; pin evaluation-tool version separately.

**Positive closure:** All supplied components/annotators/edits/native controls and original group metadata are faithfully retained.

**Negative closure:** Combined annotators, invented learner IDs/test labels or guessed narrow leaf mapping fails import.

**Source context:**
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 110, anchor: source-category mapping file
- [audit/full-source-inventory.json](../../audit/full-source-inventory.json) — historical audit line 97, anchor: WILOCNESS-2.1

<a id="gap-043"></a>
## GAP-043 — EFCAMDAT full release and derivative ingest scope

**Who closes it:** Source information — release/use contract or explicit scope decision needed. Active requirement: `SPEC-043`.

**Already specified:** Full second-release XML is identified; first release and cleaned/error-coded derivatives are distinct; baseline is discovery-only.

**What remains missing:** The current full-source request and discovery-only baseline are not a completed ingest contract. Full XML schema, labels/offsets, prompt/task/learner grouping, selected derivative scope and permitted intended use are unspecified.

**Why it matters:** The full second release and cleaned derivatives are different source artifacts. A complete contract must identify which are included, their formats/grouping/annotations and the actual permitted intended uses.

**Needed to close:** Confirm second release only or also separately versioned Shatz2020/Oksuz2025 derivatives. Supply the applicable release schema/documentation and intended research/product/transfer use under an actual agreement. Access evidence remains separate.

**Positive closure:** Every selected EFCAMDAT release has its own complete component/parser/use contract.

**Negative closure:** Discovery metadata, cleaned subsets, inaccessible labels or academic access alone cannot satisfy full product ingest.

**Source context:**
- [domain/corpus-sources.v1.yaml](../../domain/corpus-sources.v1.yaml) — historical audit line 81, anchor: No accepted ingest format
- [audit/full-source-inventory.json](../../audit/full-source-inventory.json) — historical audit line 164, anchor: full second release (XML)

<a id="gap-044"></a>
## GAP-044 — Doubao underlying study-record release contract

**Who closes it:** Source information — release/use contract or explicit scope decision needed. Active requirement: `SPEC-044`.

**Already specified:** The study is a research reference; no supplied downloadable participant-record corpus or rights exists.

**What remains missing:** There is no identified full release, schema, annotation inventory, participant grouping or permission contract for the reported study records.

**Why it matters:** The attachments cite a study without supplying a full participant-data release contract. A paper count cannot be turned into downloadable recordings or a right to use those recordings.

**Needed to close:** Provide an actual author-authorized release identifier/documentation, all recording/annotation components and allowed uses, or explicitly keep this source research-only with an unresolved all-corpora-acquired obligation. Do not invent545 assets.

**Positive closure:** A real full release contract or an explicit scoped research-only disposition is recorded without hiding missing data.

**Negative closure:** Paper sample counts or questionnaire percentages cannot stand in for an acquired labelled corpus.

**Source context:**
- [domain/corpus-sources.v1.yaml](../../domain/corpus-sources.v1.yaml) — historical audit line 93, anchor: Not supplied
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 162, anchor: Doubao study records

<a id="gap-045"></a>
## GAP-045 — Moodrick and NIR vendor-data scope and contracts

**Who closes it:** Source information — release/use contract or explicit scope decision needed. Active requirement: `SPEC-045`.

**Already specified:** Both vendors are comparison sources; private answer banks/prompts/rubrics have no supplied data licence.

**What remains missing:** No full annotated release or exact comparison-only versus corpus-ingest definition exists for both vendors under the latest full-source requirement.

**Why it matters:** Moodrick and NIR are two separate vendor sources in one profile. Each needs its own data-release/use contract or explicit comparison-only disposition; public product descriptions cannot provide private answer banks.

**Needed to close:** For each vendor separately, provide an authorized full-release data contract/rights or explicitly select public comparison-only scope. An all-sources-acquired claim remains blocked where no release exists.

**Positive closure:** Both vendor sources have exact documented scope and no fictional assets or inferred providers.

**Negative closure:** Product descriptions, demo percentages or another vendor product disclosure cannot qualify as this corpus.

**Source context:**
- [domain/corpus-sources.v1.yaml](../../domain/corpus-sources.v1.yaml) — historical audit line 99, anchor: MOODRICK-NIR-DATA
- [domain/corpus-sources.v1.yaml](../../domain/corpus-sources.v1.yaml) — historical audit line 105, anchor: No public annotated corpus

<a id="gap-046"></a>
## GAP-046 — Leakage grouping, split allocation and duplicate protocol

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-046`.

**Already specified:** Development/calibration/holdout preserve related speaker/learner/script/derivative groups; upstream benchmark splits are retained.

**What remains missing:** Canonical group identities, connection/duplicate equivalence, split allocation ratios/seed, upstream-versus-project split distinction and infeasible connected components are not specified.

**Why it matters:** Related speakers, scripts and derivative records can leak answers from development into evaluation. Split rules must specify connected groups and honestly handle a group too large to divide independently.

**Needed to close:** Define grouping/normalization/duplicate rules and assignment algorithm. Resolve cases where shared CMU prompts connect many L2 speakers into one component; do not weaken the speaker/script disjointness to manufacture holdout.

**Positive closure:** Frozen group manifests prove every intended independence boundary and report infeasible splits explicitly.

**Negative closure:** Connected derivatives/speakers/scripts cannot cross splits or be accepted through a changed leakage definition.

**Source context:**
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 38, anchor: Keep connected groups in one split
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 37, anchor: script family

<a id="gap-047"></a>
## GAP-047 — Gold stimulus, asset and negative-control counting

**Who closes it:** Linguistic policy — reviewed definitions/registry needed. Active requirement: `SPEC-047`.

**Already specified:** 122 leaves, six candidate stimuli per leaf/732 total and one contrast pair per split are preserved policy candidates.

**What remains missing:** Counting unit for multi-target files, acceptable-variant counterparts, approved observations versus assets and independent pair families remains unresolved.

**Why it matters:** One multi-target recording can support several observations but is not several independent recordings. The counting policy must distinguish assets, stimuli, target observations, contrast pairs and acceptable controls.

**Needed to close:** Resolve DEC-002 with separate asset/stimulus/observation/pair/control counts and exact per-leaf/per-split counting, including permitted-variant leaves; do not alter the inherited floor implicitly.

**Positive closure:** Each leaf/control satisfies its approved counting rule with exact record IDs and independent final-audio reviews.

**Negative closure:** Multi-label files, duplicated stimuli or treating a permitted variant as an error cannot inflate coverage.

**Related decisions:** DEC-002.

**Source context:**
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 120, anchor: three independent contrast pairs per leaf
- [domain/validation-policy.yaml](../../domain/validation-policy.yaml) — historical audit line 7, anchor: minimum_total_stimuli:

<a id="gap-048"></a>
## GAP-048 — Agreement and semantic evaluation denominator protocols

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-048`.

**Already specified:** Raw agreement/kappa and semantic coverage/exact mapping equations exist; pre-adjudication labels and abstentions must be retained.

**What remains missing:** The annotation unit/label inventory, alignment and missing-rater handling, exact resolved/eligible/gold-decision definitions and class/stratum weighting are not specified enough to calculate comparable values.

**Why it matters:** Agreement, coverage and precision depend on who and what is counted. Removing abstentions or using post-adjudication unanimity would falsely improve the reported performance.

**Needed to close:** Define eligible events and label matching for each auxiliary evaluation metric, including ignored/meta/duplicates/retractions/key defects/abstentions and Cohen-kappa pairs. Preserve kappa undefined at N=0 or Pe=1.

**Positive closure:** Every numerator/denominator is traceable to the same frozen independently labelled population.

**Negative closure:** Adjudicated unanimity, dropped abstentions or changed eligibility cannot improve apparent agreement.

**Source context:**
- [domain/metrics.v1.yaml](../../domain/metrics.v1.yaml) — historical audit line 238, anchor: agreements/N
- [domain/metrics.v1.yaml](../../domain/metrics.v1.yaml) — historical audit line 275, anchor: eligible_gold_decisions

<a id="gap-049"></a>
## GAP-049 — Elapsed attempt start and validated playback event contracts

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-049`.

**Already specified:** Elapsed time and accepted playback-event count are descriptive metrics. Original answer submission time is present; neither the baseline nor active local attempt schema contains started_at. Client events do not prove listening.

**What remains missing:** started_at is absent from attempt.schema; its trigger/clock/restart behavior is undefined. No playback-event schema/validation/deduplication or event transport contract exists.

**Why it matters:** The elapsed-time formula refers to a start timestamp not present in the active attempt schema. Playback also needs a saved deduplicated event definition; neither metric proves listening or teaching ability.

**Needed to close:** Define started_at creation and server-authoritative time semantics, plus event identity/type/audio/attempt/time validation, replay counting rules and duplicate/out-of-order handling.

**Positive closure:** Elapsed time and replay count recompute from declared saved timestamps and accepted event IDs.

**Negative closure:** Client-forged duration, duplicate plays or missing start cannot become an ability score.

**Source context:**
- [domain/metrics.v1.yaml](../../domain/metrics.v1.yaml) — historical audit line 280, anchor: submitted_at-started_at
- [contracts/attempt.schema.json](../../contracts/attempt.schema.json) — historical audit line 102, anchor: "submitted_at"

<a id="gap-050"></a>
## GAP-050 — Complete heldout acceptance protocol and critical cases

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-050`.

**Already specified:** Mapping/coverage/correction/repeat gates have numeric limits and minimum denominators; every domain and fixed configuration requires evidence.

**What remains missing:** Exact gold-mapping precision equality, correction-attempt eligibility, critical-counterexample inventory, domain assignment, three-run agreement estimator and configuration/prompt freeze protocol are incomplete.

**Why it matters:** The numeric acceptance thresholds already exist as policy candidates. The missing definitions specify their exact event populations, correctness comparisons, critical cases and repeatability estimator before measurement.

**Needed to close:** Engineering should define every acceptance population, correctness relation, domain/abstention handling and critical case inventory, then specify pairwise versus unanimous comparison for three repeated runs and exact configuration freeze. Preserve separate mapping-decision and correction-attempt sample floors. Reconcile the inherited VAL-ISOLATION cross-role wording with local teacher/blind-review projection checks; user accounts/access-role attack tests are outside the chosen scope.

**Positive closure:** Each gate calculates the frozen defined statistic with adequate actual strata and untouched holdout evidence.

**Negative closure:** Tiny/subset domains, omitted critical failures or threshold tuning on exposed holdout cannot pass.

**Source context:**
- [domain/validation-policy.yaml](../../domain/validation-policy.yaml) — historical audit line 25, anchor: all critical counterexamples correct
- [domain/validation-policy.yaml](../../domain/validation-policy.yaml) — historical audit line 29, anchor: 3 runs of identical

<a id="gap-051"></a>
## GAP-051 — Retention, deletion and permission revocation lifecycle

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-051`.

**Already specified:** Raw answers/evidence are immutable, private, consent-bound and tied to approved use; owner approvals can expire or be revoked.

**What remains missing:** No exact retention periods or deletion/revocation contract reconciles immutable history, personal/source data, provider responses, backups and affected future use.

**Why it matters:** Immutable audit history must be reconciled with personal/source-data deletion and permission withdrawal. Local storage does not remove the need to define future-use restrictions and what happens to backups.

**Needed to close:** Choose retention periods and deletion/revocation behavior for local source/personal data, answers, provider records, historical results and backups. Define what can remain as a tombstone/hash/audit reference, future-use restrictions and disclosure/consent text/version. Engineering should specify local actions and storage effects; no tenant/account offboarding is required.

**Positive closure:** Each retained or deleted artifact has a defined permitted lifecycle and future transfer/publication guard.

**Negative closure:** Expired/revoked permission or a delete request cannot silently retain active use or destroy audit references inconsistently.

**Source context:**
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 140, anchor: Collect real teacher answers
- [contracts/approval-record.schema.json](../../contracts/approval-record.schema.json) — historical audit line 68, anchor: "expires_at"

<a id="gap-052"></a>
## GAP-052 — Request quotas, concurrency, costs and import resource bounds

**Who closes it:** Product policy — user choice, then engineering contract. Active requirement: `SPEC-052`.

**Already specified:** Bounded local work/imports and recorded provider usage; stored approved audio remains playable when cloud generation is disabled or its budget is exhausted. No per-user/tenant quota, billing or reservation service is required.

**What remains missing:** Local defaults/units for spend, concurrency and request/file/archive/member/expanded-byte limits, provider-failure/retry usage accounting, admission errors and limit configuration remain unspecified.

**Why it matters:** A simple local app still needs bounded provider spend, concurrent work and archive expansion. This is local resource policy, not tenant billing, per-user quotas or a reservation platform.

**Needed to close:** Choose local cost/concurrency/import safety defaults or authorize engineering defaults with explicit configuration bounds. Define treatment of failed/cancelled/retried calls and playback exemption; do not introduce per-user/tenant quotas or billing.

**Positive closure:** Declared local limits deterministically bound concurrent operations/imports and usage accounting.

**Negative closure:** Concurrent calls, retry double-counting or archive expansion cannot bypass limits or prevent unrelated stored playback.

**Source context:**
- [openspec/changes/implement-teacher-error-trainer/specs/v6-platform-foundation/spec.md](../../openspec/changes/implement-teacher-error-trainer/specs/v6-platform-foundation/spec.md) — historical audit line 19, anchor: platform MUST limit requests
- [docs/corpus-acquisition.md](../../docs/corpus-acquisition.md) — historical audit line 24, anchor: unbounded decompression

<a id="gap-053"></a>
## GAP-053 — Backup/restore consistency and compatibility protocol

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-053`.

**Already specified:** Named volumes, checksummed migrations and non-destructive local recovery; the launcher supplies backup/restore as a local tool, not a management service.

**What remains missing:** Full domain DB/media snapshot boundary, manifest schema, restore validation/order/rollback, schema/profile compatibility and historical private evidence coverage are not completely specified.

**Why it matters:** A backup is useful only if database rows, audio and immutable historical evidence form one consistent restorable snapshot. The full manifest, compatibility and partial-failure procedure must be defined.

**Needed to close:** Engineering should define the complete DB/media/evidence backup manifest and consistent snapshot boundary, ordered backup/restore/hash validation, schema/profile compatibility, conflict/rollback procedure and included/excluded data. Preserve server secrets separately and describe recovery without manual infrastructure administration.

**Positive closure:** A validated compatible backup restores every declared domain/media reference and historical answer/result.

**Negative closure:** Missing assets, tampered manifests, incompatible migrations or an existing conflicting target cannot produce a healthy partial restore.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 78, anchor: backup procedure must include frozen answers
- [openspec/changes/implement-teacher-error-trainer/design.md](../../openspec/changes/implement-teacher-error-trainer/design.md) — historical audit line 35, anchor: stored checksums

<a id="gap-054"></a>
## GAP-054 — Complete deployment/configuration and release manifest schema

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-054`.

**Already specified:** Docker prerequisite; supplied launcher and key-only setup; automatic persistent internal secrets and migrations; bundled prescribed services, loopback web port, server-only keys and amd64/arm64 support. These are chosen product requirements, not already implemented startup.

**What remains missing:** The exact launcher/bootstrap and recovery procedure, internal secret generation/storage/reuse/rotation, all setting types/defaults/validation/ownership/overrides and release compatibility/provenance manifest still need engineering definitions. No user account/role or manual DB/storage setup is required.

**Why it matters:** The one-command/key-only user experience is already chosen. The missing engineering detail is how the supplied bundle, automatic internal secrets, configuration validation and versioned release artifacts deliver it.

**Needed to close:** Engineering should specify the launcher/first-run/restart/failure path; every provider and internal setting with defaults, destination and validation; generated secret persistence and safe rotation; complete image/dependency/config/migration/prompt/policy manifest and architecture qualification. Users supply only operation-specific provider keys.

**Positive closure:** An operator supplies only declared local secrets/settings; all nonsecret release identities and compatibility are frozen.

**Negative closure:** Unknown settings, unresolved image references, leaked env or unqualified architecture cannot be accepted as a release.

**Source context:**
- [docs/runtime-v1.md](../../docs/runtime-v1.md) — historical audit line 82, anchor: publisher must supply built images
- [domain/providers.configurable.v1.yaml](../../domain/providers.configurable.v1.yaml) — historical audit line 2, anchor: specification_only_not_live_qualified

<a id="gap-055"></a>
## GAP-055 — Specification authority, version compatibility and drift closure

**Who closes it:** Engineering — can be drafted without a new product decision. Active requirement: `SPEC-055`.

**Already specified:** Actual user requests outrank imported instructions; original bytes remain preserved; docs/simple-local-product.md and active deltas explicitly supersede account/tenant/access-role requirements, and attempt 1.1.0 is the active local overlay.

**What remains missing:** A complete domain-by-domain authority/overlay/version map and compatibility/migration/cache invalidation table is missing. Each remaining source/overlay/implementation divergence needs explicit disposition, including legacy isolation/authorization language.

**Why it matters:** The current user authority and local overlay are explicit. The remaining work is a complete artifact-by-artifact compatibility map and drift disposition, so preserved historical sources do not reintroduce obsolete behavior.

**Needed to close:** Engineering should identify the authoritative artifact and exact overlay order for every domain, accepted version combinations and migration/cache rules; resolve each tracked divergence while retaining historical source/test proof. No account/role requirement should be revived by an imported artifact.

**Positive closure:** Every active requirement resolves to one consistent definition and every known gap has exact closure evidence.

**Negative closure:** Duplicate contradictory definitions, stale missing-file claims or structural counts cannot establish semantic completeness.

**Source context:**
- [docs/authority.md](../../docs/authority.md) — historical audit line 3, anchor: user
- [openspec/changes/implement-teacher-error-trainer/design.md](../../openspec/changes/implement-teacher-error-trainer/design.md) — historical audit line 44, anchor: only active original-text adjustment

## Separate outstanding evidence and implementation

These are not additional missing-definition IDs and cannot be closed by writing a policy: full source bytes and actual hashes/counts; genuine use/transfer agreements and consents; actual qualified independent reviewers and final-audio observations; observed synthetic capabilities; real teacher answers and independent gold labels; actual LLM/speech conformance/latency/heldout results; full local browser/start/restart/restore and both-architecture results; genuine scoped decision records; full schema dialect/provider-subset validation. See [the earlier evidence register](../spec-fullness-20261008/EVIDENCE.md). The report creates none of that evidence.

The metric equations are not all missing: all 27 core and 15 auxiliary formulas are present. Gaps concern semantic event/counter definitions, auxiliary method/denominator contracts, exact transport and measurement/validation protocols. Existing threshold values remain documented policy candidates rather than measured results.

The full-source list remains TET-GOLD-1, SPEECHOCEAN762, L2-ARCTIC, WILOCNESS-2.1, FCE-2.1, EFCAMDAT, DOUBAO-STUDY-RECORDS and MOODRICK-NIR-DATA. Where an actual study/vendor release is unspecified or unavailable, scope must be resolved explicitly; research metadata cannot satisfy all-corpora-acquired acceptance.

No product behavior, formula, source permission or decision was invented or changed by this clarification report. No application code, test, provider call, corpus acquisition or deployment was performed.
