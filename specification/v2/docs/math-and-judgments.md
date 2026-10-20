# Mathematical and semantic contract

The equation registry is `domain/metrics.v1.yaml`.
The symbol table is in `docs/scoring-v1.md`. This document defines the conversion and transport.
A model chooses bounded semantic findings. It cannot supply the authoritative counts, fractions, or composite.

## Detection-event identity

Count one event when one communicative defect has one independent repair obligation in its context.
Two independent repair obligations can share a text span. Keep two units only when fixing either leaves the other defect.
Alternative repairs for the same defect do not create extra units.
Repeated occurrences have distinct event IDs when each occurrence independently satisfies the defect definition.
A discourse event can span several utterances. It still has one reviewed primary unit.
Use the most specific supported leaf. Equal competing primary leaves require review, not arbitrary alphabetical priority.
Secondary labels preserve other valid analyses but do not change denominators.
The LLM assigns unit boundaries with evidence/provenance before a machine-labelled item enters the benchmark.

## Claim identity and coverage

Preserve UTF-8 bytes and count offsets in decoded Unicode codepoints. Reject invalid UTF-8 and unpaired surrogates.
No NFC transformation changes the saved answer or its source offsets.
Sort extracted clauses by start offset, end offset, and their original output position.
Assign `clm_` plus the first 32 hexadecimal SHA-256 digits of UTF-8 JCS encoding of the ordered array [answer_sha256, start_cp, end_cp, exact_text]. Offset values are safe integers. Do not concatenate undelimited strings. Hash collisions or competing interpretations of an identical span use LLM reconsideration and cannot overwrite the original clause.
If identical spans contain different interpretations, retain them as an unresolved extraction conflict.
Check the complete span partition. Each codepoint belongs to a claim, attachment, unparsed span, non-assertive span, or whitespace.
Coverage cells form an ordered disjoint partition. Original source spans can overlap only for a declared contained attachment.
A substantive assertion cannot disappear because it is difficult to classify.
The server derives coverage; substantive missing interpretation invokes LLM repair, without a separate required audit.
Schema or arithmetic checks alone cannot prove extraction completeness.

## Consolidation

A group contains only claims about the same identified event and compatible stance.
All members remain stored. The representative is the earliest endorsed claim, not the highest-scoring claim.
Normalize exact duplicate content only with NFC, apostrophe equivalence, and whitespace rules.
Exact duplicate consolidation does not erase arbitrary punctuation or change case. Semantic correction credit may accept harmless case/terminal-period variation under the contextual proposition rubric; it needs no per-case human approval.
A retraction must explicitly refer to an earlier assertion. Its evidence span must occur later in the original answer.
Reject cycles and forward references. A later contradiction without an explicit retraction remains unresolved only for its affected component; contradictory rationale does not unsettle an independently clear correction.
Compatible fragments combine within their correction or explanation component. Keep each additional false clause in its actual component; do not mix rationale into correction credit.
Do not choose only the most favorable alternative from contradictory endorsed repairs.

## Total stance table

| Reviewed target | Teacher stance | Result | Count effect |
|---|---|---|---|
| True error | Error | Supported detection | One TP and a correct explicit acceptability judgment. |
| True error | Acceptable | Wrong acceptance | One FN and a wrong explicit judgment. No FP. |
| Designated control | Error | False assertion | One FP, one DF, and a wrong explicit judgment. |
| Designated control | Acceptable | Correct acceptance | One DA and a correct explicit judgment. |
| Off-key location, clearly permitted | Error | Resolved false assertion | One unattributed or explicitly categorized FP. |
| Off-key location, plausible defect | Error | Potential key defect | Review. No final counts. |
| Ambiguous location | Either assertion | Unresolved | Review. No final counts. |
| No assertion, example, or question | None | Ignore | No TP, FP, or explicit judgment. |
| Unparsed substantive content | Unknown | Unresolved | Review. No final counts. |

A wrong explicit category does not cancel a correctly identified detection.
An unknown explicit category preserves detection and has zero classification credit unless the LLM supports an existing taxonomy mapping.
Missing category text gives zero classification coverage. It is not an unknown-alias dispute.

## Correction and explanation tuple rules

For an eligible detected unit, an absent correction has supplied=false, option_id=null, empty proposition sets, and zero credit.
For positive or partial repair credit, a supplied correction refers to exactly one authored option or an equivalent option set. A definite LLM rejection of the actual supplied correction can have option_id=null and empty proposition sets: no valid option matched, and the bounded rejected finding yields native zero credit. Do not convert that resolved rejection into novel-alternative uncertainty merely because no valid option matched. An explicit unresolved reason remains unresolved; no accepted/partial credit is created without a valid nonempty rubric.
The required proposition set must be nonempty. Every satisfied or violated ID must belong to that exact unit and option.
`violated_proposition_ids` identifies forbidden assertions, not required propositions that were merely omitted.
If that component has a forbidden assertion or a verified unsupported additional_assertion, code sets that component credit to zero. Unknown additional assertions make only that component unavailable when no verified forbidden condition already determines zero.
Otherwise code sets credit to the count of satisfied required propositions divided by the count of all required propositions.
A complete supported correction satisfies its required propositions independently of explanation; an additional contradictory correction clause remains part of that correction.
The LLM accepts a valid novel alternative that satisfies existing semantic propositions; a genuine rubric defect invokes LLM adjudication and creates a new key version.
A correction for an ineligible control cannot earn correction credit. An unnecessary correction attached to FP increments FC once.

An explanation always has option_id=null.
Its propositions belong to the unit rationale, not a correction option.
A category label alone is not an explanation. Explanation is optional; omission has internal supplied=false/credit0 but displays N/A and never penalizes the primary grade. Supplied explanations are assessed regardless of the legacy task flag.
An additional explanation claim is judged by the LLM under the same proposition rubric. A verified false assertion triggers the fixed forbidden-condition rule only in its component; its exact span/judgment/reason is recorded without inventing a proposition ID.
An unsupported evaluator tuple invokes the one permitted output repair, then explicit failure if still invalid.

## Mapper and auditor comparison

Use the same frozen extraction for both requests. The audit request does not see the first mapping output.
Canonicalize record order by server claim ID. Sort fields declared as sets and reject duplicate members.
Compare target IDs, stance source references, group membership, retractions, decision kind, option identity, proposition sets, unresolved reasons, and exclusions.
Compare evidence scope and approved rationale identities. A different free-text explanation alone does not change arithmetic.
An alternative evidence reference is harmless only when both resolve to the same exact subject, observation, version, and digest.
Optional audit differences are retained diagnostics. Only genuine unresolved scorable meaning invokes LLM adjudication/provisional status.
Do not rerun a semantic stage to search for agreement.

## Exact numbers

A rational is a signed decimal-string numerator and a positive decimal-string denominator.
Store the fraction in lowest terms. Zero is `0/1`. Unavailable is null with an explicit reason.
Limit each magnitude to 4096 decimal digits. Reject overflow before a write or response.
Never encode large exact integers as JavaScript numbers.
Store raw counts separately from reduced ratios. A reduced denominator is not the empirical sample size.

For a ratio n/d, the one-decimal percentage uses half-up rounding of `1000*n/d`, then division by 10.
Calculate the rounding with integer quotient and remainder, not binary floating point.
For the 0-to-100 composite, round `10*n/d` and divide by 10 for display.
The legacy float display field is non-authoritative. Never feed it into another calculation.

```text
C = 100 * sum(w_i * n_i/d_i for i in E) / sum(w_i for i in E)
E = enabled components with structural opportunities
```

New answer-components-v2 primary weights remain45/15/30 for detection/classification/correction. Optional explanation is separately scored by EQ/EA; inherited weight10 applies only to frozen historical/explicit legacy benchmark policy.
The classification component uses `classification.hierarchical_recall`, not conditional accuracy.
An omitted selected detection/classification/correction component remains zero. Explanation omission never changes the primary grade. Only a lack of structural primary opportunities removes its weight.
An unresolved issue affecting the selected primary grade makes its composite unavailable. An optional explanation-only issue leaves primary scores available and is reported separately.

## Auxiliary populations

Agreement uses the same pre-adjudication aligned events from the same pair of genuine raters.
Match intervals only through a reviewed event correspondence, not a guessed overlap threshold.
Keep true_error, acceptable, uncertain, and absent as distinct labels. Missing-rater events are excluded and counted separately.
Raw agreement is agreements/N. Cohen kappa is `(Po-Pe)/(1-Pe)`, with Pe from the two empirical label marginals.
Kappa is unavailable for N=0 or Pe=1. Adjudicated agreement cannot replace the independent labels.

Semantic coverage includes every independently gold-labeled eligible substantive decision, including abstentions.
Mapping precision uses resolved predicted decisions. A correct decision matches target, stance, grouping, and resolution class exactly.
Correction agreement uses actual correction attempts as its denominator, not all mapping decisions.
Duplicate and retraction semantics must agree with the gold normalization. Do not create extra sample units from fragments.
Report excluded/meta/no-op records, key defects, absent labels, and abstentions separately.
Pool raw counts for overall estimates. Report each domain with its own denominator.

For three repeated runs, compare the three unordered run pairs on the same N eligible gold decisions.
Repeatability is the number of exact matching decisions across those pairs divided by `3*N`.
Repeated abstention can be repeatable. It cannot pass the separate semantic coverage gate.
Four teacher traits are not observable in this mode and remain null.
Elapsed time and playback counts are descriptive, not ability scores.

Detection and classification have primary composite opportunities only when G is positive. Correction requires GC positive. Explanation is separate under answer-components-v2; its accuracy uses EA and its descriptive opportunity metrics use GE/TE.
On a control-only exercise, keep control and false-assertion metrics. Do not manufacture a composite score from absent true-error opportunities.

## Current LLM-only normalization and scorer projection

These preprocessing rules preserve all numerical equations and define the default single-mapper workflow.

The server derives the coverage partition from validated clause/attachment spans and original answer. It fills whitespace/non-assertive intervals itself; uncovered substantive text is passed to the LLM repair/reconsideration step. Recover a span only from a unique exact quoted substring; convert documented UTF-16 offsets to original Unicode codepoint offsets when the quoted bytes match. An ambiguous repeated quote stays unresolved. No rewritten answer is substituted.

Claims are source-order sorted by start_cp,end_cp,local_ref. Explicit backwards retraction deactivates its target for arithmetic while preserving it. Exact duplicates attach to the earliest active representative. Compatible noncontradictory fragments for the same localized assertion combine their actual correction/reason spans; the union is source ordered and retains member claim IDs. Contradiction is assigned to the affected component for LLM reconsideration; only unresolved primary meaning blocks the primary grade. It cannot select a favorable correction fragment merely for a higher grade.

A resolved group maps to one decision. true_error+assert_error -> matched_error; true_error+assert_acceptable -> wrong_acceptance; acceptable+assert_error -> false_positive with its control unit; acceptable+assert_acceptable -> confirmed_acceptable. An unsupported off-key assertion -> false_positive with unit_id=null. A supported off-key defect -> provisional key-defect adjudication. Meta/question/retracted -> ignore. Unresolved primary assertion -> unresolved; an unknown rationale assertion stays in explanation status/additional_assertions and does not convert a matched_error into an unresolved detection. Duplicates point to the representative's decision and are excluded once. No decision is replicated across all matching units.

Category recognition accepts semantic synonyms justified by context and maps them to an existing122-leaf ID, preferring the most specific supported leaf. Unknown category -> null classification credit; supported detection remains. Existing ancestor compatibility remains as defined by the original classification metric. Correct alternatives and paraphrases are judged by the LLM against existing required/forbidden propositions, not rejected because their wording was absent. A new correction may select the existing option whose semantic constraints it satisfies; if none fits despite correctness, adjudicate a rubric defect and append a version.

For the scorer, supplied flags come only from real spans. A selected option with any violated forbidden proposition or verified unsupported additional_assertion has numerator0 for that component alone. If no verified forbidden condition already determines zero, unknown propositions/assertions have null credit only for their dependent component. Otherwise numerator is the number of its satisfied required propositions, denominator is the number of required propositions. No supplied content -> supplied=false, credit0/1. A zero-required rubric is defective rather than automatically perfect. Explanation follows its unit rationale and option_id=null. IDs outside the unit are invalid and repaired.

Default checking uses one mapper. Optional audit compares and reports differences; it does not null a supported grade. LLM adjudication settles genuine score-relevant ambiguity; unresolved after that remains provisional. Historical reference scorer/validators encode stricter old preprocessing: their arithmetic remains an inert oracle, and their former human/alias/repeat-audit restrictions are not runtime contracts.

Current complete component projection and optional explanation policy are in answer-component-scoring.md; it supersedes inherited whole-answer contradiction/required-explanation instructions. No numeric LLM grade replaces the42formulas.
