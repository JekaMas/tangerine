## ADDED Requirements

### Requirement: SPEC-024 Exact score transport, composite rational and numeric bounds

Exact metric and composite fractions MUST use bounded decimal-string numerators and positive denominators. Display rounding MUST NOT feed another calculation.

The normative artifacts are:

- `contracts/exact-rational.schema.json`.
- `contracts/score-result.schema.json`.
- `docs/math-and-judgments.md`.
- `reference/scorer.py`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-024`.
- **THEN** A result crosses Python, JSON, Go, and browser boundaries. Its reduced rational stays identical.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-024`.
- **THEN** A number overflows, a denominator is zero, or a rounded display is submitted as the exact value. The numeric contract rejects it or uses the declared unavailable state.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
