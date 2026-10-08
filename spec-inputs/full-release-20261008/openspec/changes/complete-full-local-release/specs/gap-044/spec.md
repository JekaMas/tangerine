## ADDED Requirements

### Requirement: SPEC-044 Doubao underlying study-record release contract

Study-record ingestion MUST require an actual author-authorized Doubao release and participant-use scope. Paper metadata cannot create recordings.

The normative artifacts are:

- `docs/sources/private-vendors-and-study.md`.
- `contracts/source-release.schema.json`.
- `domain/corpus-sources.v1.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-044`.
- **THEN** An authorized complete release identifies its files, participant groups, annotation format, and permitted uses. It can enter the normal import protocol.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-044`.
- **THEN** Only the paper and sample counts exist. Record access remains unavailable and the full-source obligation is not reported complete.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
