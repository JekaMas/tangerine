## ADDED Requirements

### Requirement: SPEC-049 Elapsed attempt start and validated playback event contracts

Attempt elapsed time MUST use the database start and submission clocks. Play counts MUST use deduplicated validated events bound to the heard asset.

The normative artifacts are:

- `contracts/attempt.schema.json`.
- `contracts/playback-event.schema.json`.
- `docs/interface-contract.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-049`.
- **THEN** A repeated event ID arrives with the same payload. It is accepted idempotently and does not add another play.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-049`.
- **THEN** A client supplies another asset, an impossible time, or a changed payload under the same event ID. It cannot affect telemetry or ability scores.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
