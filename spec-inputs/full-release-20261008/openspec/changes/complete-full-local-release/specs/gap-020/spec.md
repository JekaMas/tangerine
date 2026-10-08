## ADDED Requirements

### Requirement: SPEC-020 Evaluator and cross-schema conditional truth tables

Structural validity MUST be followed by the declared cross-field, scope, null, and eligibility rules. An impossible tuple is rejected.

The normative artifacts are:

- `docs/cross-field-invariants.md`.
- `domain/semantic-invariants.yaml`.
- `reference/validators_v2.py`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-020`.
- **THEN** A supplied correction, selected option, proposition sets, and verdict agree with the same source and unit. The tuple enters normalization.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-020`.
- **THEN** A model reports accepted credit without supplied text, a foreign proposition, or an unresolved component in a resolved decision. The application rejects the tuple.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
