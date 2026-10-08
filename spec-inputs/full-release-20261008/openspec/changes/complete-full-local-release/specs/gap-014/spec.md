## ADDED Requirements

### Requirement: SPEC-014 Frozen English/Russian aliases and taxonomy ancestors

Explicit category interpretation MUST use the frozen English/Russian registry. An unknown or ambiguous alias cannot receive a guessed narrow category.

The normative artifacts are:

- `domain/category-aliases.v1.yaml`.
- `docs/math-and-judgments.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-014`.
- **THEN** The teacher supplies one registered unambiguous term. The mapper uses that exact ancestor or leaf identity.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-014`.
- **THEN** A term maps to multiple entries or a different registry version. The affected category decision remains unresolved.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
