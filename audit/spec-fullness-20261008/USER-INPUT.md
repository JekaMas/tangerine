# Information needed from the owner or source maintainer

The55-gap register contains33 engineering definitions and22 product/linguistic/source inputs. You do not need to design SQL tables or API internals to answer the22 items below. Each answer can name an existing artifact/path or state the exact rule. Unanswered choices remain open; no default is silently adopted. All33 engineering contract obligations remain explicit in GAPS.md and OpenSpec.

Reply using the GAP IDs. Existing DEC decisions remain separate even if several answers arrive in one message. Real source permissions, human observations and provider results cannot be created by an answer declaring them complete.

## GAP-002 — Public and private transport projections

Define each view field-by-field, its audience/state, and when transcripts/keys/evidence become visible. Decide whether a teacher receives the complete key after submission or only result-linked excerpts.

**Answer / existing artifact path:** _Not supplied._

## GAP-005 — Role/action/resource authorization matrix

Assign every API operation to roles and resource ownership. State who publishes and adjudicates, whether authors may review their own work, and whether administrators may bypass any review guard (structural/rights guards remain non-overridable).

**Answer / existing artifact path:** _Not supplied._

## GAP-006 — Account and session lifecycle contract

Specify account creation/disable/role changes and session TTL/renewal/revocation/cookie/CSRF behavior; state whether password recovery is an operator-only local procedure or an in-scope UI.

**Answer / existing artifact path:** _Not supplied._

## GAP-007 — Case lifecycle transition and guard table

Complete the case transition table, including edit/re-render/re-review, quarantine/release, retirement, concurrent publication and the policy for already-started/evaluating attempts.

**Answer / existing artifact path:** _Not supplied._

## GAP-009 — Dispute and adjudicated result revision records

Define dispute submit/review/resolve records and who can request a revision; specify mapping/recalculation versus preserved original scores, notifications/readback and which other historical attempts may be revised.

**Answer / existing artifact path:** _Not supplied._

## GAP-011 — Reviewer independence and qualification records

Define who verifies a person and qualification, accepted competence evidence, validity period and conflicts; specify third-adjudicator eligibility and whether two resolved final approvals must still be recorded after adjudication.

**Answer / existing artifact path:** _Not supplied._

## GAP-014 — Frozen English/Russian aliases and taxonomy ancestors

Supply exact English/Russian alias entries with target ID(s), parent-versus-leaf status, ambiguity behavior and normalization/version rules. Retain unresolved unknown wording.

**Answer / existing artifact path:** _Not supplied._

## GAP-015 — Severity assignment and fixed weight binding

Define the severity rubric and exact severity-to-weight mapping, or explicitly authorize independent reviewed weights with required evidence. Do not change inherited composite weights.

**Answer / existing artifact path:** _Not supplied._

## GAP-016 — Rated difficulty evidence protocol

Either freeze v1 difficulty to unrated everywhere until a separately specified study, or define the complete rating method and evidence requirements for every enabled rating.

**Answer / existing artifact path:** _Not supplied._

## GAP-017 — Variety, register and judgment consistency table

Define allowed variety/register/basis values or an explicit reviewed free-text contract, permitted label combinations and required public facts for each context-dependent leaf.

**Answer / existing artifact path:** _Not supplied._

## GAP-027 — Feedback-only failure versus evaluation-failure outcome

Specify the feedback-only failure exception and response/state table, including whether a valid score remains complete, how fallback provenance is represented and which explicit retry repeats only feedback.

**Answer / existing artifact path:** _Not supplied._

## GAP-028 — Linguistic audit role prompt, schema and decisions

Resolve DEC-001 using the exact proposed or replacement input, prompt, closed schema and finding-to-candidate rules; record the scoped decision without treating a model as a human reviewer.

**Answer / existing artifact path:** _Not supplied._

## GAP-032 — Typed render operator and hard-capability catalog

Define the capability catalog and each operator payload/range, legal combinations and conflict results. State exactly which parameters constitute pace, accent, stress and prosody constraints.

**Answer / existing artifact path:** _Not supplied._

## GAP-035 — Speech tokenizer, reviewed intervals and disfluency event rules

Resolve DEC-005 with the full tokenizer and interval/event protocol, including punctuation, partial words, overlaps, zero-duration and intended pause treatment.

**Answer / existing artifact path:** _Not supplied._

## GAP-036 — Prosody feature/unit/method and valid missingness table

Resolve DEC-006 for every enabled feature: method/version, valid units, bounds, interval/voicing policy, evidence type and human-only/unknown outcome.

**Answer / existing artifact path:** _Not supplied._

## GAP-043 — EFCAMDAT full release and derivative ingest scope

Confirm second release only or also separately versioned Shatz2020/Oksuz2025 derivatives. Supply the applicable release schema/documentation and intended research/product/transfer use under an actual agreement. Access evidence remains separate.

**Answer / existing artifact path:** _Not supplied._

## GAP-044 — Doubao underlying study-record release contract

Provide an actual author-authorized release identifier/documentation, all recording/annotation components and allowed uses, or explicitly keep this source research-only with an unresolved all-corpora-acquired obligation. Do not invent545 assets.

**Answer / existing artifact path:** _Not supplied._

## GAP-045 — Moodrick and NIR vendor-data scope and contracts

For each vendor separately, provide an authorized full-release data contract/rights or explicitly select public comparison-only scope. An all-sources-acquired claim remains blocked where no release exists.

**Answer / existing artifact path:** _Not supplied._

## GAP-046 — Leakage grouping, split allocation and duplicate protocol

Define grouping/normalization/duplicate rules and assignment algorithm. Resolve cases where shared CMU prompts connect many L2 speakers into one component; do not weaken the speaker/script disjointness to manufacture holdout.

**Answer / existing artifact path:** _Not supplied._

## GAP-047 — Gold stimulus, asset and negative-control counting

Resolve DEC-002 with separate asset/stimulus/observation/pair/control counts and exact per-leaf/per-split counting, including permitted-variant leaves; do not alter the inherited floor implicitly.

**Answer / existing artifact path:** _Not supplied._

## GAP-051 — Retention, deletion and permission revocation lifecycle

Specify retention for each data class, who requests/authorizes deletion, tombstone/hash/history policy, revocation effects on existing cases/results and backup expiry. Specify required disclosure/consent text and version.

**Answer / existing artifact path:** _Not supplied._

## GAP-052 — Request quotas, concurrency, costs and import resource bounds

Choose limits/defaults/configuration authority for generation/evaluation/cost/concurrency and archive member/expanded-byte limits. Define failed/cancelled/retried usage accounting and playback exemption.

**Answer / existing artifact path:** _Not supplied._
