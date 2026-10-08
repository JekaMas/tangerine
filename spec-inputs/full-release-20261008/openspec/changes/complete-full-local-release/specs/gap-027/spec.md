## ADDED Requirements

### Requirement: SPEC-027 Feedback-only failure versus evaluation-failure outcome

A feedback-only failure MUST preserve a valid semantic score and show approved stored rationale or an explicit unavailable commentary state.

The normative artifacts are:

- `docs/lifecycle.md`.
- `contracts/result-envelope.schema.json`.
- `contracts/retry-request.schema.json`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-027`.
- **THEN** The final feedback call times out after a valid score commit. An explicit feedback retry uses the same score and cannot re-map claims.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-027`.
- **THEN** The mapper fails. The feedback exception cannot promote that attempt to a completed score.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
