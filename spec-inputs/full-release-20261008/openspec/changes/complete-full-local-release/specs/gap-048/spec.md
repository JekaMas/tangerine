## ADDED Requirements

### Requirement: SPEC-048 Agreement and semantic evaluation denominator protocols

Agreement and semantic metrics MUST use the declared fixed event populations and retain missing labels, abstentions, and pre-adjudication disagreement.

The normative artifacts are:

- `docs/math-and-judgments.md`.
- `docs/splits-and-validation.md`.
- `contracts/holdout-report.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-048`.
- **THEN** The same independent rater pair labels aligned events. Raw marginals define agreement and kappa.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-048`.
- **THEN** Adjudicated unanimity replaces the original labels or abstentions disappear from coverage. The reported statistic cannot pass.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
