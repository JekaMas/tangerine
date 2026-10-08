## ADDED Requirements

### Requirement: SPEC-033 SSML compilation and final-audio assembly specification

SSML compilation and final assembly MUST preserve turn order and target scope and bind reviews to the actual delivered mono PCM16 24-kHz WAV.

The normative artifacts are:

- `docs/audio-methods.md`.
- `contracts/render-plan.schema.json`.
- `contracts/transformation.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-033`.
- **THEN** The compiler escapes literal text and assembles turns with recorded offsets. The delivery hash identifies the reviewed bytes.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-033`.
- **THEN** Encoding, normalization, trimming, or a turn order changes after review. Existing approval cannot transfer to that file.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
