## ADDED Requirements

### Requirement: SPEC-035 Speech tokenizer, reviewed intervals and disfluency event rules

Speech rates and disfluency density MUST use the fixed tokenizer and reviewed interval/event rules, not estimated text length or an unversioned VAD.

The normative artifacts are:

- `docs/audio-methods.md`.
- `domain/audio-methods.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-035`.
- **THEN** Reviewed token events and interval unions are available. Each numerator and denominator can be recomputed.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-035`.
- **THEN** A filler is automatically called an error or overlapping intervals count twice. The measurement is invalid.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
