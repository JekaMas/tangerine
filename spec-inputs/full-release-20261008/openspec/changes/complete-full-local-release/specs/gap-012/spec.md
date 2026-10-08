## ADDED Requirements

### Requirement: SPEC-012 Teacher-answer gold annotation data contract

Teacher gold MUST retain actual original answers, independent pre-model annotations, disagreement, and adjudicated expected mappings.

The normative artifacts are:

- `contracts/teacher-gold.schema.json`.
- `docs/review-and-gold.md`.
- `docs/splits-and-validation.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-012`.
- **THEN** Annotators label a real frozen answer before model output. Their original labels and final correspondence remain separate.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-012`.
- **THEN** A generated answer or model-derived label is presented as independent human gold. It cannot satisfy heldout evidence.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
