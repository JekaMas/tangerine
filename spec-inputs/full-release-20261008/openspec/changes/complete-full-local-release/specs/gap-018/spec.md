## ADDED Requirements

### Requirement: SPEC-018 Claim identity, extraction partition and completeness

Claim IDs MUST derive from the exact saved answer and Unicode spans. A disjoint coverage partition MUST preserve every substantive segment or mark it unresolved.

The normative artifacts are:

- `contracts/claim-extraction.schema.json`.
- `docs/math-and-judgments.md`.
- `reference/validators_v2.py`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-018`.
- **THEN** All exact spans and coverage cells agree with the frozen answer. The server assigns reproducible persistent identities.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-018`.
- **THEN** A source quote is fabricated, an assertion is omitted, or identical spans carry conflicting interpretations. The extraction cannot enter completed scoring.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
