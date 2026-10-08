## ADDED Requirements

### Requirement: SPEC-022 Semantic decisions to deterministic rubric and scorer input

Code MUST derive rubric fractions from fixed required and forbidden propositions. Models MUST NOT provide authoritative grades.

The normative artifacts are:

- `docs/math-and-judgments.md`.
- `contracts/scoring-input.schema.json`.
- `reference/validators_v2.py`.
- `reference/scorer.py`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-022`.
- **THEN** Required proposition findings resolve without forbidden assertions. Code calculates the exact satisfied-count fraction.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-022`.
- **THEN** A supplied response includes a forbidden assertion or a plausible novel alternative. The first receives zero under the fixed rubric; the second requires review.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
