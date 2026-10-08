## ADDED Requirements

### Requirement: SPEC-053 Backup/restore consistency and compatibility protocol

Backup and restore MUST use a consistent database/media/evidence boundary, exact hashes, compatibility checks, and non-destructive target activation.

The normative artifacts are:

- `contracts/backup-manifest.schema.json`.
- `docs/maintenance-and-limits.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-053`.
- **THEN** A complete verified backup restores into an inactive target and passes reference checks before activation.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-053`.
- **THEN** A component is missing, a digest fails, or a schema is incompatible. The original workspace remains active and no partial restore reports success.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
