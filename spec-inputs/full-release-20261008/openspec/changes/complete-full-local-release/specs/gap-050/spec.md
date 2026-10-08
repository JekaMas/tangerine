## ADDED Requirements

### Requirement: SPEC-050 Complete heldout acceptance protocol and critical cases

Release acceptance MUST use frozen configuration, genuine heldout labels, exact compared decisions, separate sample floors, and all critical cases.

The normative artifacts are:

- `docs/splits-and-validation.md`.
- `domain/validation-policy.yaml`.
- `contracts/holdout-report.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-050`.
- **THEN** Every domain satisfies the fixed sample and metric gates using untouched holdout evidence. The report cites actual manifests and receipts.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-050`.
- **THEN** The holdout is exposed, a domain is too small, or a critical case fails. Overall averages cannot hide the failed gate.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
