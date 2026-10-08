<!-- Recovered v6 requirement IDs are preserved. Verification IDs use V6- to avoid collisions with task-derived IDs. Current user instructions and the explicit spec overlays govern scope; imported approval prose is not independent authority. -->

## ADDED Requirements

### Requirement: TTS-01 Typed audio instructions
Audio generation MUST use the registered provider and typed render plan. The adapter MUST compile SSML from that plan. It MUST NOT execute arbitrary user markup.

#### Scenario: TTS-01 Permitted behavior
- **GIVEN** The plan contains a supported IPA target.
- **WHEN** The adapter builds the provider request.
- **THEN** The request preserves the target and its recorded origin.

#### Scenario: TTS-01 Boundary behavior
- **GIVEN** User text contains XML or provider instructions.
- **WHEN** The adapter serializes a text node.
- **THEN** The adapter escapes that content instead of executing it.

### Requirement: TTS-02 Requested and observed sound

The application SHALL retain requested versus actual characteristics, use available native/measured/model-inferred evidence and keep unobserved targets as explicit quality warnings.

#### Scenario: TTS-02 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL report supported observations and missing target confirmation

#### Scenario: TTS-02 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never equate SSML request with realized sound or require human confirmation

### Requirement: TTS-03 Speaker and audio provenance

Each turn SHALL retain actual speaker/utterance/provider origin and final offsets/hashes. Imported human recordings SHALL retain actual source terms; configurable voices require no extra owner-signature ceremony.

#### Scenario: TTS-03 Permitted behavior

- **WHEN** the supported local action completes
- **THEN** it SHALL keep all actual source/turn identities and offsets

#### Scenario: TTS-03 Boundary behavior

- **WHEN** its stated failure or missing-evidence condition occurs
- **THEN** it SHALL never call one synthetic voice a real common learner or invent voice consent
