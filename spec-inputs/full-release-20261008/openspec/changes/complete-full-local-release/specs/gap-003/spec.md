## ADDED Requirements

### Requirement: SPEC-003 Complete persistent entity and constraint model

Every persistent field MUST belong to a named closed schema and a typed immutable document. References MUST bind the exact kind, scope, and digest.

The normative artifacts are:

- `db/schema.sql`.
- `domain/persistence-map.json`.
- `docs/persistence.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-003`.
- **THEN** A new domain document and its reference nodes commit. Its head, references, and audit event share one database transaction.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-003`.
- **THEN** A reference points to another case or missing document. The operation cannot commit a healthy record.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
