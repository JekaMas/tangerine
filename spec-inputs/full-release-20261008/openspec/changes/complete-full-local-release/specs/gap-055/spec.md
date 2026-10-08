## ADDED Requirements

### Requirement: SPEC-055 Specification authority, version compatibility and drift closure

Each domain MUST resolve to one active artifact and exact compatible versions. Unavailable repository bytes MUST NOT be claimed integrated.

The normative artifacts are:

- `docs/authority.md`.
- `audit/input-lock.json`.
- `domain/version-compatibility.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-055`.
- **THEN** An implementer compares the supplied package against the real current checkout and records every accepted migration or conflict.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-055`.
- **THEN** Historical account requirements reappear or a structural count substitutes for semantic integration evidence. The integration gate remains blocked.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
