## ADDED Requirements

### Requirement: SPEC-054 Complete deployment/configuration and release manifest schema

The release publisher MUST supply actual compatible images and a launcher that creates persistent internal secrets. The operator supplies only declared external configuration.

The normative artifacts are:

- `docs/local-delivery.md`.
- `contracts/release-manifest.schema.json`.
- `domain/configuration-registry.yaml`.
- `deploy/local/compose.reference.yaml`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-054`.
- **THEN** A qualified release starts the real stack on loopback with persistent data and no account setup.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-054`.
- **THEN** Images are missing, a secret is exposed, or an architecture lacks qualification. The launcher cannot claim a completed first release.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
