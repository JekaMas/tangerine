## ADDED Requirements

### Requirement: SPEC-052 Request quotas, concurrency, costs and import resource bounds

One local resource policy MUST bound expensive concurrency, request capacity, cost reservations, and safe archive expansion without disabling stored playback.

The normative artifacts are:

- `domain/configuration-registry.yaml`.
- `contracts/configuration.schema.json`.
- `docs/maintenance-and-limits.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-052`.
- **THEN** A request fits the exact limits and has a known accounted price bound. One expensive foreground operation is admitted.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-052`.
- **THEN** Unknown charge exposure, excessive decompression, or an exhausted budget violates admission. The operation fails rather than truncating required content.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
