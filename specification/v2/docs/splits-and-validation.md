# Splits and actual acceptance

## Leakage groups

Construct an undirected graph of acquired records and their known source relationships.
Add edges for the same genuine learner, speaker, prompt/script family, exact recording, text derivative, or documented source derivation.
Normalize duplicate text for grouping with NFC, casefold, and whitespace collapse only. Retain original bytes separately.
Exact hashes can identify identical content. They do not prove two people are the same individual.
Do not use approximate similarity as a proved identity edge without reviewed evidence.
Compute connected components. Assign each complete component to one project split.
Preserve upstream benchmark partitions as independent metadata. They do not override project leakage constraints.

Use seed `tangerine-split-v1` and SHA-256 of seed plus component's sorted member IDs.
Sort components by this digest. Assign each to the split with the largest remaining target deficit, with development/calibration/holdout as tie order.
The proposed external-data ratio is 60/20/20 by record count, subject to indivisible components.
A large component can make that ratio infeasible. Record the actual proportions and insufficient coverage.
Do not cut a shared-speaker or shared-script component to produce a convenient holdout.
Original gold uses the separate one-pair-family per leaf per split requirement.
Freeze the manifest and all group edges before model/prompt calibration.
A newly discovered cross-split edge invalidates the affected holdout use. It does not disappear from the graph.

## Frozen evaluation

Freeze model identifier, actual returned identity, prompt hashes, schemas, adapters, taxonomy, aliases, scorer, source grants, and audio methods.
Record genuine gold labels before model results.
Use the same fixed holdout for the paired three-run repeatability measurement.
Do not tune a threshold, prompt, or alias map on exposed holdout and then report untouched-holdout performance.
A changed configuration requires a new qualification or an explicit disclosure of reused evidence.

VAL-MAP requires exact mapping precision>=0.98 overall and>=0.95 in each observable domain.
It requires at least 100 eligible independently labeled mapping decisions per domain.
VAL-COVER requires non-abstained/eligible>=0.90 overall and in every domain.
VAL-REPAIR requires strict correction agreement>=0.95 on at least 100 actual correction attempts per domain.
The correction sample floor is separate from the mapping sample floor.
VAL-REPEAT requires pairwise three-run exact agreement>=0.99 under the math contract.
VAL-AUDIO requires two resolved approvals for every target and control on final audio bytes.
VAL-SCORE requires exact arithmetic agreement for every approved real or separately authorized oracle case.
VAL-ISOLATION checks teacher and blind-review field projections. It does not invent removed account/role attack boundaries.

Critical cases include genuine novel valid corrections, disputed off-key defects, contradictory repairs, explicit retractions, missing extraction content,
wrong-version evidence, repeated ambiguous phrases, false correction of acceptable varieties, and wrong phonetic inference from ASR scores.
Each critical case must have actual source evidence or a separate explicit authorization for that exact constructed test.
No constructed test has such approval in this package.
Insufficient cases remain a failed or not-run gate. They are not zero observed failures.

## Threshold status

The retained thresholds are engineering acceptance policies, not measured outcomes or universal teacher standards.
Store every numerator, denominator, excluded class, abstention, and domain assignment.
A domain with no cases cannot disappear from the report or inherit the overall score.
A structurally valid acceptance report is not proof that its provider calls occurred.
The report must resolve every run to actual immutable receipts and independent gold records.

## Digest encoding clarification

Hash UTF-8 JCS of [seed, sorted_component_member_ids] for allocation order. Each ID is unique and sorted by Unicode codepoint order; collisions require an explicit component-ID tie break. Target counts are exact rational 3N/5, N/5, N/5 for the proposed external-data ratio. At each step choose the greatest target-minus-assigned record deficit; tie order is development, calibration, holdout. Add the whole component count. No greedy allocation claims an exact feasible ratio. The distinction between genuine source speaker identity and reused synthetic voice remains GAP-046/FRC-008; no hidden weakening is allowed.
