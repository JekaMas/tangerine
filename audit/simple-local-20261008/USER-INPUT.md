# Current remaining input — simple local scope

The historical 55-gap questionnaire is superseded by the dispositions below. GAP-005/006 require no role/account decision. 53 grouped definitions remain open; 33 are engineering definitions and 20 need product, linguistic or source-owner input. Removing login does not resolve linguistic policy or source access. Full details and exact original source locations remain in audit/spec-fullness-20261008/GAPS.md.

## GAP-002: Public and private transport projections

Define teacher, authoring, blind-review and result view projections; no adversarial separation from the local operator.

Define each view field-by-field, its audience/state, and when transcripts/keys/evidence become visible. Decide whether a teacher receives the complete key after submission or only result-linked excerpts.

## GAP-007: Case lifecycle transition and guard table

Lifecycle guards concern case state, source permission and real evidence, not application role assignment.

Complete the case transition table, including edit/re-render/re-review, quarantine/release, retirement, concurrent publication and the policy for already-started/evaluating attempts.

## GAP-009: Dispute and adjudicated result revision records

Local review/dispute records and immutable result revisions; no adjudicator account or role permissions.

Define dispute submit/review/resolve records and who can request a revision; specify mapping/recalculation versus preserved original scores, notifications/readback and which other historical attempts may be revised.

## GAP-011: Reviewer independence and qualification records

Real person/qualification/conflict attestations without authenticated reviewer accounts; genuine independence still requires evidence.

Define who verifies a person and qualification, accepted competence evidence, validity period and conflicts; specify third-adjudicator eligibility and whether two resolved final approvals must still be recorded after adjudication.

## GAP-014: Frozen English/Russian aliases and taxonomy ancestors

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Supply exact English/Russian alias entries with target ID(s), parent-versus-leaf status, ambiguity behavior and normalization/version rules. Retain unresolved unknown wording.

## GAP-015: Severity assignment and fixed weight binding

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Define the severity rubric and exact severity-to-weight mapping, or explicitly authorize independent reviewed weights with required evidence. Do not change inherited composite weights.

## GAP-016: Rated difficulty evidence protocol

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Either freeze v1 difficulty to unrated everywhere until a separately specified study, or define the complete rating method and evidence requirements for every enabled rating.

## GAP-017: Variety, register and judgment consistency table

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Define allowed variety/register/basis values or an explicit reviewed free-text contract, permitted label combinations and required public facts for each context-dependent leaf.

## GAP-027: Feedback-only failure versus evaluation-failure outcome

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Specify the feedback-only failure exception and response/state table, including whether a valid score remains complete, how fallback provenance is represented and which explicit retry repeats only feedback.

## GAP-028: Linguistic audit role prompt, schema and decisions

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Resolve DEC-001 using the exact proposed or replacement input, prompt, closed schema and finding-to-candidate rules; record the scoped decision without treating a model as a human reviewer.

## GAP-032: Typed render operator and hard-capability catalog

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Define the capability catalog and each operator payload/range, legal combinations and conflict results. State exactly which parameters constitute pace, accent, stress and prosody constraints.

## GAP-035: Speech tokenizer, reviewed intervals and disfluency event rules

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Resolve DEC-005 with the full tokenizer and interval/event protocol, including punctuation, partial words, overlaps, zero-duration and intended pause treatment.

## GAP-036: Prosody feature/unit/method and valid missingness table

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Resolve DEC-006 for every enabled feature: method/version, valid units, bounds, interval/voicing policy, evidence type and human-only/unknown outcome.

## GAP-043: EFCAMDAT full release and derivative ingest scope

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Confirm second release only or also separately versioned Shatz2020/Oksuz2025 derivatives. Supply the applicable release schema/documentation and intended research/product/transfer use under an actual agreement. Access evidence remains separate.

## GAP-044: Doubao underlying study-record release contract

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Provide an actual author-authorized release identifier/documentation, all recording/annotation components and allowed uses, or explicitly keep this source research-only with an unresolved all-corpora-acquired obligation. Do not invent545 assets.

## GAP-045: Moodrick and NIR vendor-data scope and contracts

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

For each vendor separately, provide an authorized full-release data contract/rights or explicitly select public comparison-only scope. An all-sources-acquired claim remains blocked where no release exists.

## GAP-046: Leakage grouping, split allocation and duplicate protocol

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Define grouping/normalization/duplicate rules and assignment algorithm. Resolve cases where shared CMU prompts connect many L2 speakers into one component; do not weaken the speaker/script disjointness to manufacture holdout.

## GAP-047: Gold stimulus, asset and negative-control counting

Retain the full source finding and positive/negative closure criteria; local simplicity supplies no missing linguistic, source or scoring definition.

Resolve DEC-002 with separate asset/stimulus/observation/pair/control counts and exact per-leaf/per-split counting, including permitted-variant leaves; do not alter the inherited floor implicitly.

## GAP-051: Retention, deletion and permission revocation lifecycle

Define simple local retention/deletion/revocation actions and operator duties; no tenant/account offboarding.

Specify retention for each data class, who requests/authorizes deletion, tombstone/hash/history policy, revocation effects on existing cases/results and backup expiry. Specify required disclosure/consent text and version.

## GAP-052: Request quotas, concurrency, costs and import resource bounds

Define local operation concurrency, bounded resources and provider usage; no per-user/tenant quotas or billing.

Choose limits/defaults/configuration authority for generation/evaluation/cost/concurrency and archive member/expanded-byte limits. Define failed/cancelled/retried usage accounting and playback exemption.
