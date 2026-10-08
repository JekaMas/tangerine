## ADDED Requirements

### Requirement: SPEC-038 Full synthetic target capability and canary specification

Every taxonomy target and requested acoustic combination MUST have requested-versus-observed qualification evidence and a version-bound drift check.

The normative artifacts are:

- `domain/target-capabilities.yaml`.
- `contracts/capability-record.schema.json`.
- `docs/audio-methods.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-038`.
- **THEN** An actual synthesis and two human observations satisfy the target-specific criteria for a fixed profile. That profile can use the qualification.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-038`.
- **THEN** A target fails after the bounded render attempts. It remains a full-release blocker and cannot be omitted or replaced silently.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
