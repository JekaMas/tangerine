## ADDED Requirements

### Requirement: SPEC-031 Retry, deadline and input/output capacity protocol

One request-wide retry and deadline protocol MUST govern provider calls, cancellation, token capacity, and late writes.

The normative artifacts are:

- `docs/runtime-and-storage.md`.
- `domain/configuration-registry.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-031`.
- **THEN** A retryable transport failure occurs with sufficient reserve and retry budget. One accounted retry can proceed.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-031`.
- **THEN** The output is incomplete or the prompt exceeds capacity. The application preserves source input and fails without truncation or semantic retries.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
