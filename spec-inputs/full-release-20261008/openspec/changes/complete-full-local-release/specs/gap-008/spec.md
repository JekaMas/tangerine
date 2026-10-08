## ADDED Requirements

### Requirement: SPEC-008 Attempt and evaluation recovery transition table

Submission MUST preserve the answer before provider work. Only the current lease epoch can commit a result against frozen inputs.

The normative artifacts are:

- `contracts/attempt.schema.json`.
- `docs/lifecycle.md`.
- `docs/runtime-and-storage.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-008`.
- **THEN** An expired evaluation receives explicit recovery. The epoch increases and the exact answer, case, and policy stay fixed.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-008`.
- **THEN** A delayed provider response arrives under a stale epoch or after the deadline. The result is retained as failed evidence and cannot become final.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
