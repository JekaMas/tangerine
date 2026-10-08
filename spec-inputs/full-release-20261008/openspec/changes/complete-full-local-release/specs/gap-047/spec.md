## ADDED Requirements

### Requirement: SPEC-047 Gold stimulus, asset and negative-control counting

Gold coverage MUST count assets, stimuli, target observations, pair families, and controls separately and retain the 732 distinct-stimulus floor.

The normative artifacts are:

- `docs/review-and-gold.md`.
- `domain/validation-policy.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-047`.
- **THEN** Each leaf has three independent contrast-pair families, one per split, with actual final-audio review.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-047`.
- **THEN** One multi-target file is counted as many independent stimuli or an acceptable variant is labeled erroneous to meet the count. Coverage fails.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
