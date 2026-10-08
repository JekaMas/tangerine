## ADDED Requirements

### Requirement: SPEC-041 Complete L2-ARCTIC v5 read and suitcase parser profile

L2-ARCTIC v5 ingestion MUST preserve all read and suitcase components, clocks, original tiers, and manual-versus-automatic provenance.

The normative artifacts are:

- `docs/sources/l2-arctic-v5.md`.
- `contracts/raw-record.schema.json`.
- `domain/phone-symbols.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-041`.
- **THEN** The read and suitcase inventories match the actual source release and retain CPL/PPL/edit labels.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-041`.
- **THEN** Automatic alignments or uncertain err markers are converted into manual narrow-label gold. The conversion cannot be accepted.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
