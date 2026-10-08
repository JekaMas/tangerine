## ADDED Requirements

### Requirement: SPEC-021 Approved rationale registry and explanation-null binding

Explanation option_id MUST remain null. Feedback rationale identities MUST resolve to the same case, unit, language, approved text, and evidence.

The normative artifacts are:

- `contracts/rationale.schema.json`.
- `contracts/evaluator-output.schema.json`.
- `docs/math-and-judgments.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-021`.
- **THEN** A rationale ID resolves to the reviewed language-specific unit record. Feedback can cite its exact text.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-021`.
- **THEN** A correction option is used as an explanation option or the rationale belongs to another language/version. The reference is rejected.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
