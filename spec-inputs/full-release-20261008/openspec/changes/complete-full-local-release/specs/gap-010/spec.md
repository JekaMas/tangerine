## ADDED Requirements

### Requirement: SPEC-010 Independent blind-listening annotation contract

A blind review MUST save independently observed intervals, labels, uncertainty, and notes before the planned-key disclosure event.

The normative artifacts are:

- `contracts/blind-annotation.schema.json`.
- `contracts/review-context.schema.json`.
- `contracts/disclosure-record.schema.json`.
- `docs/review-and-gold.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-010`.
- **THEN** A genuine reviewer submits observations. Their hash and time freeze before key correspondence becomes available.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-010`.
- **THEN** The reviewer already saw the key or changes a submitted observation. The evidence cannot count as an original independent blind annotation.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
