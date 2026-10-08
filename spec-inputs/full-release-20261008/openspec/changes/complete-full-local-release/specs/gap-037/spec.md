## ADDED Requirements

### Requirement: SPEC-037 ASR and pronunciation advisory normalization

ASR and pronunciation scores MUST retain raw responses and exact chunk-to-final-audio clocks. They remain advisory, not inferred observed IPA.

The normative artifacts are:

- `docs/audio-methods.md`.
- `docs/provider-contracts.md`.
- `contracts/evidence.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-037`.
- **THEN** A pronunciation chunk has its actual source interval, reference slice, offsets, and provider scales. Its evidence stays linked to final bytes.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-037`.
- **THEN** A missing or NoMatch field is converted to a perfect score, or a low score becomes a phone substitution. The conversion fails.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
