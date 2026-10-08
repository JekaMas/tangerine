## ADDED Requirements

### Requirement: SPEC-040 Complete SpeechOcean762 parser and source scale profile

SpeechOcean762 ingestion MUST retain all selected partitions, metadata, aggregate/detail scores, five raters, source scales, and uncertain phone markers.

The normative artifacts are:

- `docs/sources/speechocean762.md`.
- `contracts/raw-record.schema.json`.
- `domain/phone-symbols.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-040`.
- **THEN** All supplied components reconcile and original score layers remain independent.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-040`.
- **THEN** An importer drops child metadata, mixes scales, or guesses a phone from low accuracy. It cannot pass faithful full import.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
