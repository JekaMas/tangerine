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

### Requirement: TTS-02 Requested and actual sound
The application MUST store requested and actual speech characteristics separately. A provider instruction MUST NOT establish observed pronunciation, pace, or accent strength. Each required target MUST pass its applicable review.

#### Scenario: TTS-02 Permitted behavior
- **GIVEN** The generated file includes a measured duration and reviewed target intervals.
- **WHEN** The application stores the evidence.
- **THEN** The observations refer to that file hash.

#### Scenario: TTS-02 Boundary behavior
- **GIVEN** The provider ignores a requested pronunciation.
- **WHEN** A reviewer hears the correct form instead.
- **THEN** The case fails target realization.

### Requirement: TTS-03 Speaker and audio origin
Each audio turn MUST retain its speaker, utterance, and provider origin. Final audio MUST retain the turn offsets and hashes. Human recordings or substitute voices MUST require separate explicit owner approval.

#### Scenario: TTS-03 Permitted behavior
- **GIVEN** A plan contains two supported speaker voices.
- **WHEN** The adapter makes the dialogue audio.
- **THEN** The manifest preserves both speakers and all turn offsets.

#### Scenario: TTS-03 Boundary behavior
- **GIVEN** The requested synthetic voice cannot make a target.
- **WHEN** No owner approval permits substitution.
- **THEN** The operation stops without a human-recorded or different-voice replacement.
