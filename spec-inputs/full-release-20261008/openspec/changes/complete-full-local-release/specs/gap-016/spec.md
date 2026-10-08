## ADDED Requirements

### Requirement: SPEC-016 Rated difficulty evidence protocol

Difficulty labels MUST use the specified target population, actual first-exposure outcomes, sample floor, and Wilson interval bands. Otherwise the label is unrated.

The normative artifacts are:

- `contracts/difficulty-study.schema.json`.
- `docs/review-and-gold.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-016`.
- **THEN** The complete study evidence meets the frozen band rule. The display cites that study and its population.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-016`.
- **THEN** The interval crosses bands or the sample is insufficient. The application keeps unrated and does not substitute author intuition or learner CEFR.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
