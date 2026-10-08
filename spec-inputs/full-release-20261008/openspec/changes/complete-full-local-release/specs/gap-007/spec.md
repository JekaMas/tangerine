## ADDED Requirements

### Requirement: SPEC-007 Case lifecycle transition and guard table

Case transitions MUST obey the exhaustive guard table. Quarantine MUST prevent new attempts and final score commits until resolved review.

The normative artifacts are:

- `docs/lifecycle.md`.
- `contracts/case-head.schema.json`.
- `contracts/transition-request.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-007`.
- **THEN** A verified case has matching final approvals and valid grants. Publication commits the same content and audio digests.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-007`.
- **THEN** A quarantined case is retired. The unresolved quarantine flag remains and final evaluation stays blocked.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
