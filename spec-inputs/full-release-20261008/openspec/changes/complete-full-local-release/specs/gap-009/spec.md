## ADDED Requirements

### Requirement: SPEC-009 Dispute and adjudicated result revision records

An adjudication MUST append a traceable result revision. It MUST NOT overwrite the original answer, audio, key, or result.

The normative artifacts are:

- `contracts/dispute.schema.json`.
- `contracts/adjudication.schema.json`.
- `contracts/unit-correspondence.schema.json`.
- `contracts/result-revision.schema.json`.
- `docs/lifecycle.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-009`.
- **THEN** The operator selects affected historical attempts after a reviewed key correction. New revisions use an explicit old-to-new unit map.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-009`.
- **THEN** A replacement recording differs from the heard asset. The application cannot rescore the old listening attempt as though that recording was heard.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
