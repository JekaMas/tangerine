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
Two reviewers must resolve unit boundaries before the item enters gold.

## Claim identity and coverage

Preserve UTF-8 bytes and count offsets in decoded Unicode codepoints. Reject invalid UTF-8 and unpaired surrogates.
No NFC transformation changes the saved answer or its source offsets.
Sort extracted clauses by start offset, end offset, and their original output position.
Assign `clm_` plus the first 32 hexadecimal SHA-256 digits of UTF-8 JCS encoding of the ordered array [answer_sha256, start_cp, end_cp, exact_text]. Offset values are safe integers. Do not concatenate undelimited strings. Hash collisions or competing interpretations of an identical span require review and cannot overwrite the original clause.
If identical spans contain different interpretations, retain them as an unresolved extraction conflict.
Check the complete span partition. Each codepoint belongs to a claim, attachment, unparsed span, non-assertive span, or whitespace.
Coverage cells form an ordered disjoint partition. Original source spans can overlap only for a declared contained attachment.
A substantive assertion cannot disappear because it is difficult to classify.
Models can mislabel non-assertive text. A separate coverage review must expose that uncertainty.
Schema or arithmetic checks alone cannot prove extraction completeness.

## Consolidation

A group contains only claims about the same identified event and compatible stance.
All members remain stored. The representative is the earliest endorsed claim, not the highest-scoring claim.
Normalize exact duplicate content only with NFC, apostrophe equivalence, and whitespace rules.
Do not erase arbitrary punctuation or change case without an approved comparison rule for that correction.
A retraction must explicitly refer to an earlier assertion. Its evidence span must occur later in the original answer.
Reject cycles and forward references. A later contradiction without an explicit retraction remains unresolved.
Compatible correction and explanation fragments can combine. An additional false clause remains part of the group's meaning.
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
An unknown explicit alias preserves detection evidence but blocks any final score that its category interpretation can change.
Missing category text gives zero classification coverage. It is not an unknown-alias dispute.

## Correction and explanation tuple rules

For an eligible detected unit, an absent correction has supplied=false, option_id=null, empty proposition sets, and zero credit.
A supplied correction refers to exactly one reviewed option or a reviewed equivalent option set.
The required proposition set must be nonempty. Every satisfied or violated ID must belong to that exact unit and option.
`violated_proposition_ids` identifies forbidden assertions, not required propositions that were merely omitted.
If a forbidden assertion exists, code sets credit to zero.
Otherwise code sets credit to the count of satisfied required propositions divided by the count of all required propositions.
A complete normalized approved alternative sets all required propositions satisfied only if no additional contradictory clause remains.
A novel plausible alternative produces review. It cannot silently add a new key option.
A correction for an ineligible control cannot earn correction credit. An unnecessary correction attached to FP increments FC once.

An explanation always has option_id=null.
Its propositions belong to the unit rationale, not a correction option.
A category label alone is not an explanation. Unsupplied explanations contribute zero when the task requires them.
An unknown additional claim in an explanation produces review. A verified false assertion triggers the fixed forbidden-proposition rule.
An unsupported evaluator tuple is rejected, not repaired.

## Mapper and auditor comparison

Use the same frozen extraction for both requests. The audit request does not see the first mapping output.
Canonicalize record order by server claim ID. Sort fields declared as sets and reject duplicate members.
Compare target IDs, stance source references, group membership, retractions, decision kind, option identity, proposition sets, unresolved reasons, and exclusions.
Compare evidence scope and approved rationale identities. A different free-text explanation alone does not change arithmetic.
An alternative evidence reference is harmless only when both resolve to the same exact subject, observation, version, and digest.
Every score-relevant difference produces review. Persist both outputs and the exact difference.
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

The fixed weights remain 45, 15, 30, and 10 for detection, classification, correction, and explanation.
The classification component uses `classification.hierarchical_recall`, not conditional accuracy.
An omitted requested component remains zero. Only a lack of structural opportunities removes its weight.
A score-relevant unresolved issue makes the entire final composite unavailable.

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

Detection and classification have composite opportunities only when G is positive. Correction requires GC positive. Explanation requires GE positive.
On a control-only exercise, keep control and false-assertion metrics. Do not manufacture a composite score from absent true-error opportunities.
