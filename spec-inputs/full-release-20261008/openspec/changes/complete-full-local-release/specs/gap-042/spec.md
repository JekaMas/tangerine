## ADDED Requirements

### Requirement: SPEC-042 Complete W&I+LOCNESS and FCE v2.1 M2 parser profiles

Each BEA v2.1 source MUST preserve token-to-codepoint positions, annotator alternatives, insertions, noop and detection-only labels, and unavailable test annotations.

The normative artifacts are:

- `docs/sources/bea-v21.md`.
- `domain/source-label-map.yaml`.
- `contracts/raw-record.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-042`.
- **THEN** One original annotator layer is normalized without merging alternative edits. Raw tokens and labels remain recoverable.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-042`.
- **THEN** The importer invents learner IDs, missing test labels, or an unsupported exact leaf mapping. The record remains unbound rather than invented gold.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
