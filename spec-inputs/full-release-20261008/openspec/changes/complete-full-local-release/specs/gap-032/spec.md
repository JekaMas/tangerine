## ADDED Requirements

### Requirement: SPEC-032 Typed render operator and hard-capability catalog

The renderer MUST use only closed text, phoneme, pause, and prosody operations compatible with the selected voice and every hard constraint.

The normative artifacts are:

- `contracts/render-constraint.schema.json`.
- `contracts/render-plan.schema.json`.
- `domain/audio-methods.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-032`.
- **THEN** The typed plan satisfies parameter ranges, scope, and known capability requirements. The compiler can issue the real synthesis call.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-032`.
- **THEN** A voice/locale conflicts with a target or a constraint is unknown. The application fails before synthesis instead of dropping the requirement.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
