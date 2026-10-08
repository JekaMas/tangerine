## ADDED Requirements

### Requirement: SPEC-043 EFCAMDAT full release and derivative ingest scope

The required EFCAMDAT scope MUST include R2, Shatz2020, and Oksuz2025 as separate releases. Each needs actual source-format and permitted-use bindings.

The normative artifacts are:

- `docs/sources/efcamdat.md`.
- `domain/corpus-sources.v1.yaml`.
- `contracts/source-format-binding.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-043`.
- **THEN** The operator supplies authorized source files, real documentation, and matching mappings for each release. Full ingestion reconciles them separately.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-043`.
- **THEN** Workbook headers, labels, or rights remain unavailable. A generic schema or a cleaned subset cannot falsely satisfy the missing native release contract.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
