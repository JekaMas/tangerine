## ADDED Requirements

### Requirement: SPEC-051 Retention, deletion and permission revocation lifecycle

Retention and erasure MUST respect actual source and person restrictions and apply revocation before future display, transfer, restoration, or reuse.

The normative artifacts are:

- `docs/maintenance-and-limits.md`.
- `contracts/deletion-request.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-051`.
- **THEN** A confirmed erasure plan removes restricted bytes and preserves only expressly permitted tombstones.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-051`.
- **THEN** A backup would restore revoked active content. Restore must reapply the revocation/deletion ledger before serving it.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
