## ADDED Requirements

### Requirement: SPEC-030 Provider-specific strict-schema projection and response parsing

Provider adapters MUST preserve full local constraints and accept only one completed visible output object under their documented transport.

The normative artifacts are:

- `domain/schema-projection.yaml`.
- `docs/provider-contracts.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-030`.
- **THEN** The documented wire projection returns a completed object. Full local schema and semantic checks still run.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-030`.
- **THEN** Reasoning text, a refusal, incomplete output, ignored instruction placement, or JSON repair produces plausible text. The adapter cannot treat it as a successful stage.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
