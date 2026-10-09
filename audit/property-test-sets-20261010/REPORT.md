# Complete property test sets — 2026-10-10

This increment updates specification/test design and its evidence graph. It implements no application feature and performs no model/provider/speech inference.

## Findings and repairs

1. Several scenario names shared exactly one positive or negative packet. Counts alone overstated distinct test design. The complete set index now requires at least two distinct input/expected packets for each polarity of every property; scenario renaming does not qualify.
2. All eight acceptable-variant leaf packets incorrectly awarded true-error detection/correction credit. They now have zero true-error events and explicit control/acceptability scoring. Overcorrection cases retain false-positive and inappropriate-repair outcomes.
3. Category clean-control false-positive packets also included private decisive context, confounding two behaviors. Those packets now contain no hidden prerequisite; hidden-context generation failure remains tested separately.
4. A secondary unit label used the unregistered grammar.verbs.verb_form identifier. It now references the preserved grammar.verbs.finite_nonfinite_form leaf without creating another detection event.
5. The named V6-SES-01 empty-answer scenario had a nonempty acceptability assertion. It now submits an actual empty answer and independently expects zero detection/correction credit, with optional explanation N/A.
6. New arithmetic/time variants must carry their own oracles. Added foreground-budget cases use min(70,165)=70 or min(70,15)=15; new pooled counts use (1+2)/(2+3)=3/5 rather than inherited baseline literals.
7. The active fixture guide had obsolete requirements/property/case counts. It now describes exact case-binding authority, current counts, distinct sets and future implementation/observation boundaries.

## Complete written coverage

- 407 requirements and 422 properties.
- 2,132 DAG case edges, including 444 additional distinct constructed plans.
- 819 baseline/variant packets; every property has at least two distinct positive and two distinct negative packets.
- All original scenarios retain both polarities. Each new case names its property/scenario, actual future owner, exact packet, independent expected values, pending runner marker and invalidation dependencies. Discovery names every additional test ID.
- The complete per-property index is specification/v2/domain/property-test-sets.v1.json; literal inputs/expected outputs and oracle instructions are in verification-fixtures.v1.json.

Category sets include contextual valid repair, omission of optional explanation, missed true mistakes, correct acceptability and overcorrection. Acoustic cases retain constructed target intent separately from actual unknown realization. Formula sets add changed sufficient statistics/exposure, elapsed time and deduplicated play counts. Source and infrastructure failures isolate missing components/dictionaries/dependencies; persistence cases preserve frozen audio/text/key/model settings. Wrong proposed arithmetic results are test-harness counterexamples, never model-owned application grades.

A packet is a concrete functional test design. During implementation it must be materialized into the already specified operation schemas, storage and prompt/context inputs by the real named owner. No new production runner, service, account, queue, mandatory corpus, human approval or ordinary-use benchmark is added.

## Observed specification checks

- 2,810 finite integrity assertions: set/edge/packet relationships, independent exact text-edit replay, scenario/requirement fingerprints and preservation.
- Positive collection-order invariance and six negative sensitivity checks: missing DAG edge, changed polarity, fabricated set execution, false decoy error credit, unbound property and duplicate packet disguised by scenario renaming.
- All 151 existing schemas compile with registered references; format validation is disabled and no cross-field runtime semantics are claimed. All 249 version-vector file digests match the current active specification.
- Strict OpenSpec validation, evidence graph validation and discovery validation pass; their receipts are retained here.
- Original taxonomy, mutation recipes, metric/provider/source registries are byte-identical to starting commit b0cbe97. All 122 categories/recipes, 42 original formulas, 11 full-source scopes and accepted product features remain.

New application behavior runs: zero. The graph retains 64 implemented historical bounded case scopes, 16 planned and 2,052 blocked cases. Those historical receipts neither execute the new collection nor prove full product operation. No schema/graph/index result establishes linguistic validity, audio realization, account entitlement, native source completeness or implemented runtime acceptance.

## Commit and IDE/index handoff

The unrelated audit/spec-fullness-20261008/GAPS.md edit remains excluded from this commit. IDEA metadata is ignored. User-authorized IDEA opening, native indexing and exact committed Context indexing follow the specification commit. Their actual machine receipts are saved separately under ignored data/logs/property-test-sets-20261010; project/index status is reported only after the relevant operations return. Index readiness is developer tooling evidence, not application acceptance.
