## ADDED Requirements

### Requirement: SPEC-026 Grounded bilingual feedback and missed-unit references

Feedback MUST distinguish detected, missed, false-positive, acceptable, and pending items and use their valid reference types in the requested language.

The normative artifacts are:

- `contracts/feedback.schema.json`.
- `contracts/feedback-output.schema.json`.
- `prompts/feedback-v1.txt`.
- `docs/interface-contract.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-026`.
- **THEN** A missed unit has no teacher claim. Its feedback references the real key unit and approved rationale without inventing a claim ID.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-026`.
- **THEN** A generated explanation introduces a new correction, score, or unsupported observation. It cannot appear as confirmed feedback.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
