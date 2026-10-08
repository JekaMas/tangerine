## ADDED Requirements

### Requirement: SPEC-019 Fragment consolidation, duplicate and retraction normalization

Normalization MUST preserve all source clauses, combine only compatible fragments, and apply only explicit backward retractions.

The normative artifacts are:

- `contracts/normalization.schema.json`.
- `docs/math-and-judgments.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-019`.
- **THEN** A later explicit retraction withdraws an earlier assertion. The final endorsed group retains both clauses and the retraction evidence.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-019`.
- **THEN** Two unretracted repairs conflict or a relation forms a cycle. The group requires review rather than best-of or last-write credit.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
