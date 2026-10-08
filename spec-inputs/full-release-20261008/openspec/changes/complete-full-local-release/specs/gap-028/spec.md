## ADDED Requirements

### Requirement: SPEC-028 Linguistic audit role prompt, schema and decisions

The advisory linguistic audit MUST use its exact prompt and closed input/output contract with source-bound findings. It cannot issue human or publication approval.

The normative artifacts are:

- `contracts/linguistic-audit-input.schema.json`.
- `contracts/linguistic-audit.schema.json`.
- `prompts/linguistic-audit-v1.txt`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-028`.
- **THEN** The candidate contains an apparent untracked textual issue. The audit references its exact subject and span for human review.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-028`.
- **THEN** The audit claims a heard phone from planned SSML or reports missing input as no_findings. The output fails its authority and status rules.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
