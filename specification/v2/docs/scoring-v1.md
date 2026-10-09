# Scoring policy 1.0.0

This file retains the inherited domain explanation. The active schemas and `docs/cross-field-invariants.md` define version 2 transport.
The arithmetic in `domain/metrics.v1.yaml` is unchanged. Earlier transport, authentication, and reference-code completion claims do not apply.


A detection unit is one distinct observation that the teacher can identify.
Each scored unit is a true error or a designated permitted control. Public context determines that judgment.
One unit has one primary taxonomy leaf and reporting domain. Secondary labels and alternative repairs do not increase its count.

## Unit matching

The teacher does not need timestamps. A quotation, word, or sufficient context can identify the target.
A wrong category does not cancel a correctly identified error.
If a repeated expression has ambiguous locations, the mapper must return an unresolved decision.
The mapper must not give credit for every possible occurrence.

A quoted expression is not necessarily an error assertion.
Preserve the difference between a question, an example, an error assertion, and an explicit permitted-form assertion.
The LLM proposes these semantic decisions. The backend accepts only decisions that pass the required boundary checks.
Arithmetic does not prove that an upstream semantic decision is true.

## Counts and sums

The metric registry uses these symbols:

| Symbol | Meaning |
|---|---|
| `G` | Number of all confirmed true-error units. |
| `D` | Number of designated permitted controls. |
| `TP` | Number of distinct true units with a supported error assertion. |
| `FN` | `G-TP`. |
| `FP` | Number of resolved false error assertions after duplicate removal. |
| `LC` | Number of TP units with an explicit valid category. |
| `LF` | Number of those categories in the correct reporting domain. |
| `LE` | Number of those categories in the permitted exact-leaf set. |
| `H` | Sum of hierarchical credit for the TP units. |
| `GC` | Number of all correction-eligible true units. |
| `GE` | Number of all explanation-eligible true units. |
| `TC` | Number of correction-eligible TP units. |
| `TE` | Number of explanation-eligible TP units. |
| `CA` | Number of those TP units with a supplied correction. |
| `EA` | Number of those TP units with a supplied explanation. |
| `CK` | Number of supplied eligible corrections with credit exactly one. |
| `EK` | Number of supplied eligible explanations with credit exactly one. |
| `CQ` | Sum of correction credit for eligible TP units. |
| `EQ` | Sum of explanation credit for eligible TP units. |
| `FC` | Number of FP assertions with an unnecessary correction. |
| `DF` | Number of distinct designated controls wrongly flagged. |
| `DA` | Number of designated controls explicitly identified as permitted. |
| `SN` | Number of explicit judgments mapped to true units or controls. |
| `SA` | Number of those judgments that agree with the key. |
| `WTP` | Sum of weights for detected true units. |
| `WFN` | Sum of weights for missed true units. |
| `WFP` | `FP`, with the existing fixed false-assertion weight of one. |

A plausible off-key error must not immediately count as FP.
It requires evidence review or a `potential_key_defect` decision. A disputed decision blocks final aggregate metrics.
Calling a true error permitted creates a miss and a wrong acceptability judgment. It does not create an extra FP.

## Hierarchical category credit

For each explicitly categorized TP unit, calculate the maximum credit over the permitted gold taxonomy IDs:

```text
H_i = max_gold(2*depth(LCA(pred,gold))/(depth(pred)+depth(gold)))
H = sum(H_i)
```

The implicit root has depth zero. Each dot-separated ID component increases depth by one.
`LCA` means the longest common ancestor path. A missing category gives zero credit.
A configured alias map is retained as lookup data. The LLM may map a contextual synonym to an existing taxonomy category with saved rationale; a missing alias-table entry does not by itself block that credit. Do not create a new taxonomy ID to improve a match. Classification uncertainty remains distinct from correctly localized detection credit.

## Correction and explanation credit

Preserve the original teacher answer before normalization. The following rules normalize exact text comparisons; semantic correction credit follows the proposition contract and LLM judgment in math-and-judgments.md.
Use Unicode NFC. Trim outer whitespace and collapse internal whitespace.
Treat straight and curly apostrophes as equivalent. Do not repair grammar, simplify IPA, or erase arbitrary punctuation.
The LLM may accept case or terminal-period differences when they do not change the required meaning in context. No case-specific human approval is required; capitalization or punctuation that changes a scored obligation remains part of the judgment.

A correction option defines required propositions and forbidden propositions. A proposition is one stated condition for the repair.
Calculate correction credit from those existing propositions:

```text
q = satisfied_required_propositions / all_required_propositions
q = 0 if at least one forbidden proposition is present
```

A fully matched approved alternative gives credit one. A missing correction gives zero credit.
A correction-eligible unit requires at least one required proposition in each scored option.
The LLM accepts a valid novel alternative that satisfies the existing required propositions and violates none of the forbidden propositions. A genuine rubric defect invokes LLM adjudication and a new key version, without human peer review.
A worded pronunciation repair can satisfy the propositions. The teacher does not need to type IPA.

Use the same rule for explanation credit. A category name alone is not an explanation.
Every substantive explanation assertion requires a decision. A true clause does not cancel an additional false explanation.
The scorer must not count model-written corrections as teacher-written corrections.

## Duplicates and contradiction

Group exact duplicate stance, target, repair, and rationale before scoring.
A duplicate earns no extra TP and receives no extra FP. Keep its source span for inspection.
Compatible fragments can form one response to a unit. Do not select the best of contradictory repairs.
An explicit retraction permits the final endorsed statement to determine the result.
Without a retraction, conflicting statements require review.

An unlocated general assertion receives `insufficient_localization`.
Do not map it to all errors. If unresolved interpretation can change a score, withhold the final aggregate score.
The result can show confirmed item evidence and the pending issue. Do not label pending items as confirmed misses or false assertions.

## Ratios and unavailable values

`domain/metrics.v1.yaml` names all 27 core formulas. Preserve its numerator and denominator definitions.
For a zero denominator, return null and the specified reason. Do not replace null with zero or perfection.
For a nonzero denominator, retain the exact reduced rational result and its display value.
Retain raw sufficient statistics separately. The reduced fraction is not the raw observation count.

Detection F1 uses `2*TP/(2*TP+FP+FN)`.
An empty answer with real errors has F1 zero. Its precision is unavailable because no error assertion exists.
A clean exercise with no false assertions has unavailable detection F1. Describe its control judgments separately.

## Composite score

The existing component weights are:

| Component | Input | Weight |
|---|---|---|
| Detection | `detection.f1` | 45 |
| Classification | `classification.hierarchical_recall` | 15 |
| Correction | `correction.graded_recall` | 30 |
| Explanation | `explanation.graded_recall` | 10 |

```text
score = 100*sum(weight_i*metric_i)/sum(weight_i)
```

Use enabled components with structurally available opportunities. Freeze enabled components before answer entry.
Omitted requested work gives zero. It must not become N/A and remove its weight.
If no enabled component has an opportunity, the composite is null.
If a score-relevant decision remains unresolved, the composite is null.

The existing default requests detection and correction. A task can request all four components before it starts.
Unrequested classification and explanation remain descriptive observations. They do not change that task's composite.
These weights are product policy. They are not validated teacher norms or certification boundaries.
Retain these approved weights in policy version 1. A deliberate weight change defines a new saved policy version and cannot alter an already frozen attempt.

## Domains and pooled results

Show all eight reporting domains. Show absent opportunities as N/A, not poor performance.
Assign TP and FN to the primary domain of the actual unit.
For an unmapped FP, use its valid explicit category domain. Otherwise use `unattributed_fp`.
Do not copy that FP into every domain. Global counts must equal the corresponding domain totals.

Pool raw counts to calculate micro metrics. Do not average percentages with different denominators.
A macro mean must state its included domains and exclude N/A. It is not the default composite.
Do not infer unobserved traits from these local attempt measurements. Longitudinal trait claims are not enabled by this contract.

## Excluded measurements

This mode does not measure teacher talk time or the spoken pronunciation of the teacher.
It does not measure classroom management, live intervention timing, or real learner engagement.
Those fields remain null with `not_observable_in_this_mode`.
Playback count and elapsed time are descriptive telemetry. They do not prove listening or teaching ability.
