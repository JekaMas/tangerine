## ADDED Requirements

### Requirement: SPEC-025 Auxiliary and provisional result response contracts

All 42 named measurements MUST have an output location and explicit availability, unit, method, and reason. Unresolved scores MUST remain provisional.

The normative artifacts are:

- `contracts/auxiliary-results.schema.json`.
- `contracts/result-envelope.schema.json`.
- `domain/metrics.v1.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-025`.
- **THEN** An observable auxiliary measure has a genuine method and source intervals. The response includes the measure with its actual evidence.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-025`.
- **THEN** Teacher speech is unobserved or a semantic decision is pending. The corresponding field stays unavailable and no final aggregate or invented zero appears.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
