## ADDED Requirements

### Requirement: SPEC-011 Reviewer independence and qualification records

Counted reviews MUST reference distinct genuine people, applicable competence, declared conflicts, and the exact final artifact.

The normative artifacts are:

- `contracts/person.schema.json`.
- `contracts/qualification.schema.json`.
- `contracts/review-decision.schema.json`.
- `docs/review-and-gold.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-011`.
- **THEN** Two eligible people independently review final audio and resolve findings. Their actual final approvals can satisfy the human gate.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-011`.
- **THEN** Two names describe one person, competence is unsupported, or the author reviews their own case. Publication cannot count those records as independent approvals.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
