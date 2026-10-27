## ADDED Requirements

### Requirement: I32 Simultaneous speech and word masking
The application SHALL implement ENG-01 through the production sample-domain composer and the additive contracts in specification/v2/docs/overlap-composition.md. It SHALL retain both real source recordings, correct independent source/final clocks and answer-key passages, durable resume and cooperative controls. No hosted service, paid credit, review ceremony or stored-data audit is required.

#### Scenario: I32 Typed intent and sequential compatibility
- **WHEN** a new mutation requests a bound obstructive or cooperative overlap
- **THEN** the single output admission preserves that contextual unit and explicit gains in the frozen manifest/render plan, rejects mismatched units/turns/scopes, and absent intent preserves sequential playback

#### Scenario: I32 Actual weighted sample composition
- **WHEN** two24000-sample recordings start at0 and12000samples at24kHz
- **THEN** the output has36000samples before explicit gaps, shared samples equal the independent weighted sum, unselected sources remain unchanged and clipping or cancellation cannot become a successful recording

#### Scenario: I32 Concurrent clocks and persisted recovery
- **WHEN** composition resolves selected words against actual accepted source timing
- **THEN** both source mappings and concurrent key intervals survive; split pieces and subsequent turns retain their clocks, and interruption/restart reuses the saved composition/sources without guessed timing or repeated synthesis

#### Scenario: I32 Actual obstructive and cooperative recordings
- **WHEN** actual local recordings realize an explicitly protected safety instruction or an invited brief acknowledgment
- **THEN** stored production playback contains two simultaneous streams, obstruction has the expected scored opportunity, cooperation has none, and independent finite recognition/context observations retain their limited origin

#### Scenario: I32 Evidence and preservation
- **WHEN** the selected iteration is accepted
- **THEN** literal positive/negative tests, exact unchanged native observations, actual WAVs, source/model/context and local Lab readback are reconciled; unrelated application data,122categories,42formulas and11source scopes are preserved without claiming universal perceptual qualification
