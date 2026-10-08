## ADDED Requirements

### Requirement: SPEC-001 Complete product and internal API operation contracts

The application MUST implement the complete operation inventory through its declared closed request and response contracts.

The normative artifacts are:

- `contracts/openapi.yaml`.
- `domain/operations.yaml`.
- `docs/interface-contract.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-001`.
- **THEN** The local operator uses a listed preparation or teacher action. The response uses its named schema, status, and atomic effect.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-001`.
- **THEN** An operation has an unknown field, stale revision, or unknown action. The API returns the declared error without a partial successful result.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
