## ADDED Requirements

### Requirement: SPEC-036 Prosody feature/unit/method and valid missingness table

Each of the eleven prosody features MUST use its permitted unit, measurement or human annotation method, and explicit missingness rule.

The normative artifacts are:

- `domain/audio-methods.yaml`.
- `docs/audio-methods.md`.
- `contracts/audio-measurement.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-036`.
- **THEN** A voiced F0 measurement has sufficient valid frames and the specified reference. The report stores the actual semitone result.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-036`.
- **THEN** Unvoiced frames, provider naturalness, or requested settings are used as measured prosody. The observation is rejected or unavailable.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
