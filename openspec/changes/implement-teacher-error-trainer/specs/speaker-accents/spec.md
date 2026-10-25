## ADDED Requirements

### Requirement: ACC-01 Per-speaker accent and voice selection
The application SHALL offer Automatic plus registered American, British,
Australian and Indian English speaker voices with preview playback. Keep choices
when speaker count changes, submit only active speakers, preserve explicit
advanced overrides and explain failed catalogue/preview access without erasing
other input. Automatic preserves the configured speech defaults.

#### Scenario: ACC-01 Independent choices and override
- **GIVEN** two speaker roles and the local voice catalogue
- **WHEN** Australian and Indian voices are selected and the request is saved
- **THEN** each ordered role retains its exact selected voice and accent
- **AND** changing the count does not silently swap a retained speaker's voice
- **AND** explicit advanced speaker fields take precedence
- **AND** metadata/playback failures retain selections and do not dispatch an LLM

### Requirement: ACC-02 Explicit local rendering and persistence
The service SHALL route chosen local voices to their actual registered models,
freeze their bindings with the preparation and reuse them on resume. Missing
assets or unknown voices fail clearly without a fallback or paid call. Keep
speaker accent distinct from text variety and from intentionally injected errors.

#### Scenario: ACC-02 Mixed accents and interruption
- **GIVEN** a saved Australian/Indian dialogue request
- **WHEN** it is rendered or resumed
- **THEN** each turn uses its saved local voice/model/locale
- **AND** an unavailable model leaves completed work retained without a substitution
- **AND** the answer key never declares an accent itself a mistake

### Requirement: ACC-03 Local model and pronunciation evidence
Australian and Indian English SHALL have actual local model-generated audio and
fixed voice previews. Supported acoustic edits retain the actual phoneme inputs,
model-derived intervals and waveform operations. Preview replay reads saved audio
without new synthesis. Requested accent metadata does not fabricate auditory
verification or universal linguistic correctness.

#### Scenario: ACC-03 Actual voice and controlled mistake
- **GIVEN** pinned installed English model assets and literal independent targets
- **WHEN** Australian/Indian speech and a controlled phone substitution are produced
- **THEN** the actual inputs, speaker binding, output and timing remain inspectable
- **AND** missing assets and unsupported phones do not silently use another voice
- **AND** repeated preview playback consumes no model/provider calls

### Requirement: ACC-04 Real whole-flow demonstration
The delivered demonstration SHALL record actual UI selection, generation, stored
audio playback, submitted answer, native scoring and LLM feedback using admitted
included/local resources. Preserve original user work. Label time compression or
separately synchronized audio, and retain the original recording and artifacts.

#### Scenario: ACC-04 Real generation through feedback
- **GIVEN** admitted existing included text access and installed local speech
- **WHEN** the demonstration runs through the ordinary browser
- **THEN** recorded screens and saved artifacts correspond to the actual exercise
- **AND** no model response, score, playback or success is simulated
- **AND** failures remain visible in retained evidence and paid fallback is forbidden
