## ADDED Requirements

### Requirement: SPEC-039 Full source manifest, legal scope and transformation contracts

Full-source ingestion MUST reconcile actual components, accepted and rejected records, transformations, permissions, and counts with one exact release manifest.

The normative artifacts are:

- `contracts/source-release.schema.json`.
- `contracts/permission-grant.schema.json`.
- `contracts/import-report.schema.json`.
- `contracts/transformation.schema.json`.
- `docs/sources/acquisition-and-rights.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-039`.
- **THEN** The imported release matches every required component and permitted use. Its raw and normalized identities remain traceable.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-039`.
- **THEN** Only a sample is acquired or an external transfer lacks permission. The source cannot satisfy full acquisition or the proposed transfer.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
