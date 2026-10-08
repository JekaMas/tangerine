## ADDED Requirements

### Requirement: SPEC-045 Moodrick and NIR vendor-data scope and contracts

Moodrick and NIR MUST have separate licensed or authorized private-source bindings. Account references cannot substitute for data rights or a documented interface.

The normative artifacts are:

- `docs/sources/private-vendors-and-study.md`.
- `contracts/connector-configuration.schema.json`.
- `contracts/source-format-binding.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-045`.
- **THEN** A real authorized export or documented API contract is supplied with the appropriate credential reference. The source uses only its permitted operations.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-045`.
- **THEN** Only public descriptions or a key exist without an authorized interface and release. No private answer bank, endpoint, or source asset is invented.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
