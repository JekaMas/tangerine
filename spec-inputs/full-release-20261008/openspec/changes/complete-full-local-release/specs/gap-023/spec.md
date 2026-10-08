## ADDED Requirements

### Requirement: SPEC-023 Mapper/auditor comparison equality contract

Mapper and auditor comparison MUST use the same frozen extraction and key, an exact compared projection, and explicit set normalization.

The normative artifacts are:

- `docs/math-and-judgments.md`.
- `contracts/mapping-input.schema.json`.
- `prompts/audit-map-v1.txt`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-023`.
- **THEN** Record order differs but all score-relevant fields and evidence meanings agree. The difference does not change the score.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-023`.
- **THEN** The target, option, proposition credit, stance source, or exclusion differs. The result requires review and both outputs remain stored.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
