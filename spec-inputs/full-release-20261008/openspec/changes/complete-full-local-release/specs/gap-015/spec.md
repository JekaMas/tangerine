## ADDED Requirements

### Requirement: SPEC-015 Severity assignment and fixed weight binding

Severity MUST bind to the fixed 1-to-4 weight rubric before answer entry. False assertions retain weight one.

The normative artifacts are:

- `domain/judgment-policy.yaml`.
- `docs/review-and-gold.md`.
- `docs/scoring-v1.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-015`.
- **THEN** Reviewers justify the context-specific severity under the fixed rubric. The immutable case records the corresponding weight.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-015`.
- **THEN** An evaluator changes weight after it sees an answer. The score input fails the fixed-policy guard.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
