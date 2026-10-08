## ADDED Requirements

### Requirement: SPEC-046 Leakage grouping, split allocation and duplicate protocol

Split allocation MUST preserve connected speaker, learner, script, task, and derivative groups under the fixed policy and retain upstream splits separately.

The normative artifacts are:

- `docs/splits-and-validation.md`.
- `contracts/split-manifest.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-046`.
- **THEN** Independent connected components admit the chosen allocation. The frozen manifest records every member and seed.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-046`.
- **THEN** Shared prompts create one giant connected component. The procedure reports insufficient independent groups rather than weakening leakage boundaries.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
