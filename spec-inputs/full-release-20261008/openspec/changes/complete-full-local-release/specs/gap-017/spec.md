## ADDED Requirements

### Requirement: SPEC-017 Variety, register and judgment consistency table

Context-dependent judgments MUST use a visible variety, register, and assessment basis compatible with the judgment table.

The normative artifacts are:

- `domain/judgment-policy.yaml`.
- `docs/review-and-gold.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-017`.
- **THEN** The public task establishes the relevant constraint and reviewers support the target judgment. The unit can enter the declared error population.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-017`.
- **THEN** The only basis is a hidden accent preference or an incompatible context label. The case cannot publish that unit as a true error.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
