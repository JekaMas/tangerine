## ADDED Requirements

### Requirement: SPEC-004 Database and object-store commit protocol

The application MUST reserve an asset, store complete bytes, verify their read-back digest, and commit the owning reference in that order.

The normative artifacts are:

- `contracts/asset.schema.json`.
- `docs/runtime-and-storage.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-004`.
- **THEN** Upload and read-back agree. The final owning transaction links the private immutable asset.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-004`.
- **THEN** The process stops between upload and link. Recovery reports an orphan or pending reservation and never publishes missing bytes.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
