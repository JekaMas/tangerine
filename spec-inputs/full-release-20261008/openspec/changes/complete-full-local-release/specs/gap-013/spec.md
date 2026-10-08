## ADDED Requirements

### Requirement: SPEC-013 Detection-event boundaries and overlapping category resolution

The reviewed unitization MUST count one independent repair obligation as one event and preserve secondary categories without extra denominator credit.

The normative artifacts are:

- `docs/math-and-judgments.md`.
- `domain/error-taxonomy.v1.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-013`.
- **THEN** Two repairs share a span but either repair leaves the other defect. The reviewed key retains two independent units with the rationale.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-013`.
- **THEN** Two labels describe the same repair or equally supported primary domains remain unresolved. The application cannot inflate opportunities or choose a primary domain arbitrarily.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
