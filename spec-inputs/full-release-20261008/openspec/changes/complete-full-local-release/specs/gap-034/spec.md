## ADDED Requirements

### Requirement: SPEC-034 Audio quality measurement method and boundary rules

Every quality threshold MUST use the declared decoding, loudness, peak, RMS, window, and interval method on final delivery bytes.

The normative artifacts are:

- `docs/audio-methods.md`.
- `domain/audio-methods.yaml`.
- `contracts/audio-measurement.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-034`.
- **THEN** The report includes actual finite measurements with their method version and boundary classification.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-034`.
- **THEN** The recording is silent, too short, non-finite, or measured on an upstream file. The report cannot approve final audio.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
